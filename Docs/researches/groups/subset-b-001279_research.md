# subset-b-001279 research

This grouped report covers the FireWire OHCI host driver, IP-over-1394 net driver, PCILynx nosy sniffer, packet field helpers, PHY packet helpers, and their KUnit serialization tests. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/init_ohci1394_dma.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/init_ohci1394_dma.c

Purpose: provides an early-boot helper that scans PCI bus 0..31 for OHCI-1394 controllers and enables physical DMA before the normal FireWire stack claims the hardware. It exists for early remote debugging over IEEE 1394, not for normal runtime host-controller operation.

Important APIs and control flow: `setup_ohci1394_dma()` is wired through `early_param("ohci1394_dma", ...)` and sets the `__initdata` flag when the kernel command line passes `ohci1394_dma=early`. `init_ohci1394_dma_on_all_controllers()` checks `early_pci_allowed()`, performs direct PCI config-space discovery, filters for `PCI_CLASS_SERIAL_FIREWIRE_OHCI`, and invokes `init_ohci1394_controller()` once per device. `init_ohci1394_controller()` reads BAR0, maps it through `FIX_OHCI1394_BASE`, and calls `init_ohci1394_reset_and_init_dma()`. The initialization sequence soft-resets the controller, enables LPS, clears interrupts, initializes bus/link/PHY defaults, waits for bus resets to settle, then programs `PhyReqFilterHi/Lo` and `PhyUpperBound` to allow physical requests.

State and persistence behavior: all functions and the tiny `struct ohci` wrapper are `__init` or used only by `__init` code, so no long-lived runtime state remains after boot. Hardware state persists in controller registers after this helper exits, especially link enablement, asynchronous request filtering, retry limits, and the physical DMA window covering the low 4 GB. Later bus resets can disable physical DMA, so the normal FireWire stack must re-enable it if early DMA is still required after stack initialization.

Dependencies and integration points: depends on direct x86-style PCI config access, fixmap MMIO mapping, early boot timing through `mdelay()`, and the OHCI register definitions in `ohci.h`. It is intentionally separate from `ohci.c` because it runs before driver-model PCI probing, interrupts, DMA API ownership, or the FireWire core are available.

Risks and test signals: the feature deliberately opens unfiltered physical DMA from all FireWire nodes to low memory and is therefore a major security risk outside controlled debugging. It assumes BAR0 MMIO is valid and only scans the first 32 buses. Poll loops can silently continue after timeouts, and bus-reset timing is heuristic. Test signals include boot logs for each initialized controller, successful early remote DMA/debug access before driver probe, no boot hang on systems with OHCI cards, and later `fw-ohci` probe still succeeding after the early reset and register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/init_ohci1394_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/net.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/net.c

Purpose: implements IPv4 over IEEE 1394 per RFC 2734 and IPv6 over IEEE 1394 per RFC 3146 as a Linux `net_device`. It exposes FireWire peers as an ARPHRD_IEEE1394 network link, receives datagrams from async write requests and broadcast GASP stream packets, fragments/reassembles RFC 2734 datagrams, and advertises local unit directories through the FireWire core.

Important APIs and control flow: `fwnet_init()` registers RFC 2734 and optional RFC 3146 descriptors, creates the `fwnet_packet_task` slab cache, and registers an `fw_driver`. `fwnet_probe()` creates one `firewire%d` netdev per card, registers a high-memory address handler through `fwnet_fifo_start()`, fills the 1394 hardware address from card GUID, max receive, speed, and FIFO address, registers the netdev, then adds a `fwnet_peer` for the probed unit. `fwnet_open()` starts broadcast isochronous receive with `fwnet_broadcast_start()`; `fwnet_stop()` stops it. `fwnet_receive_packet()` handles unicast async write requests to the local FIFO; `fwnet_receive_broadcast()` handles GASP stream packets on channel 31 and requeues receive iso buffers.

Transmit flow starts in `fwnet_tx()`. It validates ARP, IPv4, or IPv6, chooses broadcast stream versus peer FIFO based on the pseudo Ethernet destination address, computes max payload from peer speed and `max_rec`, builds either an unfragmented RFC 2734 header or a first-fragment header, throttles at `FWNET_MAX_QUEUED_DATAGRAMS`, and calls `fwnet_send_packet()`. `fwnet_send_packet()` prepends RFC/GASP headers and uses `fw_send_request()` for `TCODE_STREAM_DATA` broadcasts or `TCODE_WRITE_BLOCK_REQUEST` unicasts. Completion callbacks drive `fwnet_transmit_packet_done()` or `fwnet_transmit_packet_failed()`, which chain remaining fragments, update stats, and wake the net queue when queued datagrams fall back to `FWNET_MIN_QUEUED_DATAGRAMS`.

Receive reassembly is centered on `fwnet_incoming_packet()`, `fwnet_pd_new()`, `fwnet_pd_update()`, and `fwnet_pd_is_complete()`. Unfragmented datagrams are copied directly into an skb and passed to `fwnet_finish_incoming_packet()`. Fragmented datagrams are keyed by source peer and datagram label, stored as a partial datagram with a fragment-info list, rejected on overlap or size mismatch, capped by `FWNET_MAX_FRAGMENTS`, then completed into the network stack when the fragment list spans the whole datagram. `fwnet_update()` refreshes peer node ID and generation after bus reset; `fwnet_remove()` removes peers and tears down the shared netdev when the last peer disappears.

State and persistence behavior: global state is `fwnet_device_list` guarded by `fwnet_device_mutex` and the packet-task cache. Each `fwnet_device` persists card-level netdev state, peer list, local FIFO address handler, broadcast iso receive context and buffer pointers, queued TX count, datagram label for broadcast, and carrier state. Each `fwnet_peer` persists GUID, current node ID, generation, speed, max payload, outgoing datagram label, and partial receive datagrams. `dev->lock` serializes peer lists, partial datagrams, queued-datagram accounting, and broadcast receive buffer cursors.

Dependencies and integration points: depends on the FireWire core transaction, address-handler, iso-context, descriptor, and device-id APIs; on Linux netdev/header_ops/ethtool interfaces; and on `net/firewire.h` hardware-address layout. It integrates with ARP/neighbour header caching through `fwnet_header_ops`, with FireWire config ROM publication through `fw_core_add_descriptor()`, and with FireWire bus reset notifications through `fw_driver.update`.

Risks and test signals: risks include fragile fragment-overlap/list ordering logic, unbounded wait up to five seconds for outstanding queued datagrams during remove, `BUG()` if TX fragment state becomes impossible, partial datagrams surviving peer generation changes until peer removal, broadcast receive queue requeue failures, and concurrency between TX completion and netdev teardown. The driver only supports ARP, IPv4, and optional IPv6; other EtherTypes are dropped. Test signals include module load creating RFC descriptors, `firewire%d` netdev registration, ARP over broadcast GASP, unicast IP via peer FIFO, fragmented datagrams reassembling across out-of-order packets without overlaps, queue stop/wake behavior under 20 queued datagrams, carrier toggling as peers appear/disappear, and clean removal with no leaked partial datagrams or packet tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy-user.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/nosy-user.h

Purpose: defines the small userspace ABI for the `nosy` FireWire snoop-mode character device. It gives user programs the ioctl numbers, statistics structure, and packet layout expected from `nosy.c`.

Important APIs and control flow: `NOSY_IOC_GET_STATS` copies out `struct nosy_stats`; `NOSY_IOC_START` adds the client to the active capture list; `NOSY_IOC_STOP` removes it; and `NOSY_IOC_FILTER` writes a 32-bit tcode mask. `struct nosy_stats` reports total packets offered to a client buffer and packets dropped because that buffer was full. The comment documents read records as a CPU-endian microsecond timestamp quadlet, little-endian quadlet-padded packet data, and a little-endian ack quadlet.

State and persistence behavior: this header contains no mutable state. Its definitions are persistent ABI: ioctl numbers and record layout must remain compatible with existing `nosy-dump` style tools.

Dependencies and integration points: depends on Linux ioctl encoding and fixed-width UAPI types. It is included by `nosy.c` and by userspace tools built against this kernel header.

Risks and test signals: `NOSY_IOC_STOP` and `NOSY_IOC_FILTER` both use command number 2 with different direction bits, so tooling should use the macros rather than raw numbers. The packet layout mixes CPU-endian timestamp with little-endian packet words, requiring explicit userspace parsing. Test signals include successful ioctl decoding from userspace, stats increasing during capture, filter masks suppressing unwanted tcodes, and readers correctly handling bus-reset timestamp-only records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy-user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/nosy.c

Purpose: implements a misc character-device packet sniffer for TI PCILynx IEEE 1394 controllers in snoop mode. Unlike `fw-ohci`, this driver is diagnostic capture infrastructure: it configures the PCILynx DMA engine to receive bus packets, timestamps them, filters by tcode per client, and exposes packet streams through `/dev/nosy`.

Important APIs and control flow: `add_card()` is the PCI probe path. It sets a 32-bit DMA mask, enables bus mastering, maps PCILynx registers, allocates two PCL programs plus a 16 KiB receive buffer, builds a receive PCL with 2048-byte chunks, resets the chip, enables DMA/link interrupts, clears the PHY link-active bit for self-ID packets, enables `LINK_CONTROL_SNOOP_ENABLE`, starts DMA channel 0 with `run_pcl()`, requests a shared IRQ, and registers a dynamic misc device named `nosy`. `remove_card()` deregisters the misc device, removes the card from `card_list`, disables interrupts, wakes blocked clients, frees coherent buffers, unmaps registers, disables PCI, and drops the kref.

Userspace flow is implemented by `nosy_open()`, `nosy_release()`, `nosy_read()`, `nosy_poll()`, and `nosy_ioctl()`. Open locates the PCILynx by misc minor, takes a kref, allocates a `client`, and initializes a 128 KiB circular packet buffer. `NOSY_IOC_START` links the client into `lynx->client_list`; `NOSY_IOC_STOP` unlinks it; `NOSY_IOC_FILTER` sets a tcode bitmask; `NOSY_IOC_GET_STATS` snapshots per-client counters. Reads block until buffer data is available or the card is removed, then copy one variable-length record out of the circular buffer.

Interrupt flow starts in `irq_handler()`. It rejects non-owned interrupts, clears link status before PCI status, emits a bus-reset timestamp record on `LINK_INT_PHY_BUSRESET`, and on `PCI_INT_DMA0_HLT` calls `packet_irq_handler()` before restarting the receive PCL. `packet_irq_handler()` reads packet length from PCL status, derives tcode from the receive buffer or maps a 12-byte PHY packet to synthetic `TCODE_PHY_PACKET`, writes a real-time microsecond timestamp into the first quadlet, then copies `length + 4` bytes to each active client whose filter mask matches.

State and persistence behavior: global `card_list` is protected by `card_mutex`; each `pcilynx` has a kref, PCI/MMIO/coherent DMA resources, misc device identity, and a spinlocked client list. Each `client` persists its filter mask and circular packet buffer until release. Buffer occupancy is an atomic byte count; head/tail pointers and counters are otherwise protected by the client-list lock while IRQ writers run. Captured packet state is volatile and per-client; no persistent storage is used.

Dependencies and integration points: depends on PCILynx register/PCL definitions from `nosy.h`, the `nosy-user.h` UAPI, PCI core, miscdevice, DMA coherent allocation, wait queues, poll, and copy_to_user. It binds only TI vendor ID plus PCILynx device ID `0x8000`.

Risks and test signals: risks include legacy hardware assumptions, no explicit bounds check that the PCL buffer index count stays within 13 entries if `RCV_BUFFER_SIZE` changes, circular buffer records returning 0 when user buffers are too small, real-time timestamp only using microseconds within the current second, lock coupling between IRQ packet writes and ioctl stats/filter changes, and clients observing `EPOLLHUP` after removal through `list_empty(&lynx->link)`. Test signals include `/dev/nosy` registration, `NOSY_IOC_START` beginning capture, bus reset records arriving as 4-byte timestamps, packet filters selecting async/PHY traffic, lost-packet stats increasing under slow readers, DMA channel restarting after each halt, and clean card removal waking blocked reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/nosy.h

Purpose: provides PCILynx register, DMA PCL, FIFO, link, PHY, and interrupt bit definitions used by the `nosy` snoop-mode driver. It is a hardware binding header rather than a behavioral module.

Important APIs and control flow: defines register offsets such as `MISC_CONTROL`, `PCI_INT_STATUS`, `PCI_INT_ENABLE`, DMA channel windows, `FIFO_SIZES`, `LINK_ID`, `LINK_CONTROL`, `LINK_PHY`, `LINK_INT_STATUS`, and `LINK_INT_ENABLE`. Macro families such as `DMA_BREG()`, `DMA_SREG()`, `DMA_CHAN_CTRL(chan)`, and `DMA_WORD*_CMP_*()` encode repeated channel windows. PCL command bits identify receive/transmit/PCI-to-local-bus commands, branch conditions, endian control, interrupt generation, and buffer termination. Interrupt bits describe both PCI-level DMA/link interrupts and link-level bus-reset, PHY, FIFO, cycle, and error conditions.

State and persistence behavior: there is no software state in this file. The values are the persistent hardware ABI between `nosy.c` and TI PCILynx silicon.

Dependencies and integration points: included only by the nosy driver in this work item. It mirrors naming from the PCILynx specification and older Linux 1394 headers so that `nosy.c` can build PCL receive programs and configure link snoop mode without duplicating magic numbers.

Risks and test signals: incorrect bit definitions can corrupt MMIO programming or leave interrupts uncleared. The header lacks include guards, so it relies on current include patterns. Several macros assume five DMA channels and fixed register strides. Test signals include successful compile of `nosy.c`, correct interrupt ownership and clearing, DMA0 receive PCL execution, snoop mode activation through `LINK_CONTROL_SNOOP_ENABLE`, and no unexpected FIFO or DMA error interrupts during capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci-serdes-test.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/ohci-serdes-test.c

Purpose: provides KUnit coverage for serialization and deserialization helpers in `ohci.h`, specifically OHCI self-ID count fields, self-ID receive-buffer header fields, asynchronous transmit data quadlets, and isochronous transmit data quadlets.

Important APIs and control flow: `test_self_id_count_register_deserialization()` verifies `ohci1394_self_id_count_is_error()`, generation extraction, and size extraction against a sample `SelfIDCount` value. `test_self_id_receive_buffer_deserialization()` verifies generation and timestamp extraction from the first self-ID receive-buffer quadlet. `test_at_data_serdes()` decodes a three-quadlet OHCI AT DMA header with speed, tlabel, retry, tcode, destination ID, and destination offset, then reserializes it with setter helpers. `test_it_data_serdes()` performs the same round trip for IT DMA speed, tag, channel, tcode, sync, and data length. The suite is registered as `firewire-ohci-serdes`.

State and persistence behavior: no runtime state persists beyond KUnit execution. Test vectors are static constants and local stack buffers.

Dependencies and integration points: depends on KUnit and `ohci.h`. It indirectly validates field helpers used by `ohci.c` while building async transmit descriptors and stream-data descriptors and while parsing self-ID completion state.

Risks and test signals: this test is intentionally narrow and does not exercise MMIO, descriptor DMA, bus resets, or endian quirks beyond little-endian helper use. It can catch mask/shift regressions in `ohci.h`, swapped setter fields, and accidental changes to the expected OHCI DMA header layout. Test signal is a passing KUnit suite named `firewire-ohci-serdes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci-serdes-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/ohci.c

Purpose: implements the primary PCI OHCI IEEE 1394 host-controller driver for the Linux FireWire core. It probes OHCI-class PCI devices, manages controller quirks, async request/response DMA, isochronous transmit/receive contexts, self-ID and bus-reset handling, config ROM updates, CSR access, physical DMA filtering, interrupts, and suspend/resume.

Important APIs and control flow: module lifecycle is `fw_ohci_init()` registering `fw_ohci_pci_driver`, `pci_probe()` allocating and initializing `struct fw_ohci`, and `pci_remove()` removing the FireWire card, resetting hardware, freeing IRQs, and freeing PCI vectors. `pci_probe()` maps BAR0, applies quirk tables or module override, allocates a shared coherent page for AR descriptors and self-ID DMA, initializes AR request/response contexts, AT request/response contexts, discovers IR/IT context support through interrupt-mask registers, reads card GUID and bus options, allocates MSI or INTx unless quirked, requests a threaded IRQ, and calls `fw_card_add()`.

Controller enablement is via `ohci_enable()`, the `fw_card_driver.enable` callback. It performs software reset, enables LPS and posted writes, configures byte swapping, self-ID buffer, cycle timer/master, AT retries, 1394a enhancements, PHY link-active and contender bits, config ROM DMA mapping, async request filters, interrupt masks, link enable, receive self-ID/PHY packet bits, AR DMA context startup, and finally schedules a bus reset. `ohci_disable()` masks interrupts, synchronizes IRQ/work, and flushes AT contexts.

Async receive uses `struct ar_context`. `ar_context_init()` maps noncontiguous pages into a contiguous virtual ring with wraparound pages, maps each page for device writes, and builds input descriptors. IRQ bits `RQPkt` and `RSPkt` queue `ohci_ar_context_work()`, which finds the last active buffer from descriptor residual counts, syncs DMA to CPU, parses packets with `handle_ar_packet()`, passes requests or responses to the FireWire core, and recycles buffers back to the controller. Async transmit uses generic `struct context` descriptor programs inside `struct at_context`. `at_context_queue_packet()` converts FireWire packet headers into OHCI AT/IT DMA data formats, maps payloads or inlines short payloads, checks generation under lock, appends descriptors, and wakes or starts the context. `handle_at_packet()` retires completed descriptors, unmaps payloads, translates OHCI event codes into ACK/RCODE values, handles a known invalid pending-code device quirk, and invokes packet callbacks.

Bus reset and self-ID handling is centered on hard IRQ `irq_handler()` and threaded `handle_selfid_complete_event()`. The hard IRQ acknowledges most events, queues AR/AT/isoc work, logs posted-write and cycle errors, handles 64-second bus time rollover, masks `busReset` until self-ID completion, and wakes the thread on `selfIDComplete`. The threaded handler validates `NodeID`, root state, `SelfIDCount`, self-ID inverse quadlets, generation consistency, optional TI SLLZ059 local self-ID reconstruction, stops/flushed AT contexts across the reset, installs pending config ROM updates, optionally enables unfiltered physical DMA, and calls `fw_core_handle_bus_reset()`.

Isochronous support is through `ohci_allocate_iso_context()`, `ohci_queue_iso()`, `ohci_start_iso()`, `ohci_stop_iso()`, `ohci_free_iso_context()`, and `ohci_flush_iso_completions()`. Transmit contexts build OUTPUT descriptors in `queue_iso_transmit()`. Receive packet-per-buffer contexts build INPUT descriptor blocks with separate packet headers in `queue_iso_packet_per_buffer()`. Multichannel receive uses buffer-fill descriptors and `set_multichannel_mask()`. Completion callbacks gather headers or byte counts, synchronize DMA ranges, and call the FireWire core iso callbacks.

State and persistence behavior: `struct fw_ohci` persists the embedded `fw_card`, MMIO base, node ID, generation, request generation, quirk flags, cycle/bus time state, root status, locks, coherent misc buffer, four async contexts, IR/IT context bitmasks and arrays, config ROM buffers, self-ID DMA buffer, and decoded self-ID buffer. Context state persists in coherent descriptor buffers and hardware context registers. `ohci->lock` serializes generation changes, descriptor queues, context masks, config ROM pointer swaps, bus time, and physical DMA filter updates. `phy_reg_mutex` serializes PHY register paging and access.

Dependencies and integration points: depends on PCI, DMA mapping, workqueues, IRQ threading, FireWire core card/packet/iso/CSR APIs, tracepoints, `ohci.h`, packet header helpers, and PHY packet helpers. It is the provider behind higher-level FireWire services such as SBP-2, fwnet, userspace FireWire devices, and iso consumers. Platform integration includes PowerMac cable-power hooks and x86 detection for a VIA/ASM108x/Ryzen cycle-timer read reboot quirk.

Risks and test signals: risks include subtle DMA descriptor ordering requirements, generation races around bus reset and AT queueing, physical DMA exposure through `remote_dma`, hardware-specific quirk drift, cycle timer read instability, error paths that stop contexts without restart, KUnit-covered field helpers not covering full descriptor programs, and large blast radius because this is the FireWire core host driver. Test signals include PCI probe logs with correct IR/IT counts and quirks, successful `fw_card_add()` and bus reset self-ID processing, async request/response traffic with correct callbacks, config ROM updates taking effect after bus reset, isochronous transmit/receive context allocation and callbacks, suspend/resume restoring GUID and contexts, no posted-write or unrecoverable context errors under load, and KUnit serdes tests passing for packet field helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/ohci.h

Purpose: defines the OHCI 1394 register map, event/status bits, asynchronous transmit DMA data-field helpers, isochronous transmit DMA data-field helpers, and self-ID DMA field helpers shared by the early DMA initializer, the main OHCI driver, and KUnit tests.

Important APIs and control flow: register macros cover global controller state (`Version`, `BusOptions`, `GUIDHi/Lo`, `HCControlSet/Clear`, `IntEvent/Mask`, `LinkControl`, `NodeID`, `PhyControl`, physical request filters), async context bases, and iso transmit/receive context windows. Event macros encode interrupt bits and descriptor event codes used by `ohci.c`. `OHCI1394_PhyControl_Read/Write` helpers package PHY register access commands. AT data helpers operate on little-endian OHCI DMA data quadlets: source bus ID, speed, tlabel, retry, tcode, destination ID, destination offset, and response rcode. IT data helpers similarly encode speed, tag, channel, tcode, sync, and data length for stream packets. Self-ID helpers decode `SelfIDCount` error/generation/size and self-ID receive-buffer generation/timestamp.

State and persistence behavior: no mutable state exists in the header. Its constants and inline helpers define the hardware ABI consumed by register reads/writes and coherent descriptor data in `ohci.c` and `init_ohci1394_dma.c`.

Dependencies and integration points: used by the main OHCI driver, the early physical DMA boot helper, and `ohci-serdes-test.c`. It complements `packet-header-definitions.h` by handling OHCI-specific DMA descriptor data formats, which differ from on-bus IEEE 1394 packet headers.

Risks and test signals: risks include endian mistakes in `__le32` setters/getters, duplicated or stale register masks, wrong event-code translations, and helper bugs corrupting transmitted packets. Some helper expressions rely on callers passing in-range values. Test signals include KUnit `firewire-ohci-serdes` passing, correct async transmit headers on the bus, correct stream-data headers, self-ID completion decoding expected sizes/generations, and no MMIO access regressions in `fw-ohci` probe or interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/packet-header-definitions.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/packet-header-definitions.h

Purpose: provides inline field accessors for standard IEEE 1394 asynchronous packet headers and isochronous packet headers. It centralizes masks and shifts for on-bus big-picture packet fields so driver code and tests avoid open-coded bit manipulation.

Important APIs and control flow: asynchronous helpers operate on a four-quadlet `u32 header[ASYNC_HEADER_QUADLET_COUNT]`. Getters and setters cover destination, tlabel, retry, tcode, priority, source, response code, 48-bit offset split across header quadlets 1 and 2, quadlet data, data length, and extended tcode. Isochronous helpers operate on one `u32` and cover data length, tag, channel, tcode, and sy. Setters clear the target mask then OR the shifted field value back into the header.

State and persistence behavior: there is no mutable state. The header defines a stable internal interface for packet construction/parsing in FireWire code.

Dependencies and integration points: included by `ohci.c` for parsing received async packets and building local request handling, and by `packet-serdes-test.c` for round-trip validation. The tcode and rcode values come from FireWire constants supplied by callers.

Risks and test signals: the file has a duplicated `ASYNC_HEADER_Q1_RCODE_*` definition pair, which is harmless but a maintenance smell. Helpers do not validate field ranges, so high bits are silently masked. Endian expectations are caller-owned: these helpers operate on CPU-order `u32` packet header words, not `__be32` buffers. Test signals include KUnit async header cases for write/read/lock requests and responses, isochronous header round trips, and correct `ohci.c` behavior when parsing packet tcode, length, offsets, and response codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/packet-header-definitions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/packet-serdes-test.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/packet-serdes-test.c

Purpose: provides KUnit round-trip tests for standard IEEE 1394 packet header helpers in `packet-header-definitions.h` and PHY packet helpers in `phy-packet-definitions.h`. It protects the mask/shift helpers used by `ohci.c` for packet parsing, self-ID processing, and synthetic self-ID construction.

Important APIs and control flow: helper functions serialize and deserialize common async header fields, request offsets, response rcodes, block lengths, extended tcodes, isochronous headers, self-ID zero packets, self-ID extended packets, and PHY config packets. Test cases cover async write quadlet/block request, write response, read quadlet/block request and response, lock request and response, one isochronous header vector, three self-ID layouts with port status extraction/insertion, and two PHY config packet forms. The suite is registered as `firewire-packet-serdes`.

State and persistence behavior: no state persists beyond each KUnit case. Tests use constant expected packet words and local zeroed output buffers.

Dependencies and integration points: depends on KUnit, FireWire constants, `packet-header-definitions.h`, and `phy-packet-definitions.h`. It is a direct test signal for the inline helpers consumed by the OHCI host controller driver.

Risks and test signals: the suite validates representative values but not every boundary or invalid input path. It does not currently exercise `self_id_sequence_enumerator_next()` error cases or every possible port index. It will catch common regressions such as wrong masks, shifts, setter clearing mistakes, data-length/extended-tcode swaps, and self-ID port-status packing errors. Test signal is a passing KUnit suite named `firewire-packet-serdes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/packet-serdes-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/phy-packet-definitions.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/phy-packet-definitions.h

Purpose: defines packet-field helpers for IEEE 1394 PHY packets, especially PHY config packets and self-ID packets. It is used by the OHCI driver to decode self-ID streams and to synthesize a missing local self-ID for a TI erratum, and by KUnit tests to validate serialization.

Important APIs and control flow: common helpers get/set the two-bit packet identifier. PHY config helpers get/set root ID, force-root-node, gap-count optimization, and gap count. Self-ID helpers get/set PHY ID, extended flag, more-packets flag, link-active, gap count, speed code, contender, power class, initiated-reset, and extended-packet sequence. `struct self_id_sequence_enumerator` plus `self_id_sequence_enumerator_next()` walks a buffer of self-ID quadlets one node sequence at a time, validating maximum quadlet count, extended packet markers, and sequence numbers. Port helpers compute capacity as `quadlet_count * 8 - 5` and get/set two-bit port statuses across base and extended self-ID quadlets.

State and persistence behavior: no global state exists. The enumerator mutates only its cursor and remaining quadlet count, allowing callers to incrementally consume a self-ID stream.

Dependencies and integration points: consumed by `ohci.c` for self-ID decoding, ordering by PHY ID, port-status synthesis in `find_and_insert_self_id()`, and bus-reset handoff to the FireWire core. Consumed by `packet-serdes-test.c` for round-trip coverage. It depends on Linux error-pointer conventions and errno values for enumerator failures.

Risks and test signals: `phy_packet_self_id_extended_set_sequence()` shifts by `SELF_ID_EXTENDED_SHIFT` instead of `SELF_ID_EXTENDED_SEQUENCE_SHIFT`, which is masked afterward and is suspicious even if current test vectors may not expose every sequence value. Helpers do not range-check inputs. `self_id_sequence_get_port_capacity()` underflows if called with zero quadlets. Enumerators return `ERR_PTR(-ENODATA)` and `ERR_PTR(-EPROTO)`, so callers must use error-pointer checks. Test signals include KUnit self-ID and PHY config round trips, OHCI bus reset handling with multi-quadlet self-ID sequences, correct port topology reported to the FireWire core, and explicit tests for enumerator malformed-sequence paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/phy-packet-definitions.h -->

# subset-b-004672 Research

Grouped research for DEC FDDI driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/defxx.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/defxx.c

## Purpose
Implements the Linux FDDI network driver for DEC PDQ-based adapters: DEFTA on TURBOchannel, DEFEA on EISA, and DEFPA on PCI. It binds bus devices, maps PDQ/PFI/ESIC register resources, allocates DMA-visible descriptor/consumer/command memory, initializes firmware-visible rings, exposes a `net_device`, and handles FDDI RX, TX, multicast filtering, MAC override, statistics, interrupts, reset, and teardown.

## Important APIs, Types, And Functions
The driver registers `pci_driver`, `eisa_driver`, and `tc_driver` instances from `dfx_init()` and unregisters them in `dfx_cleanup()`. `dfx_register()` is the common probe path and `dfx_unregister()` is the common remove path. The `net_device_ops` table wires `dfx_open()`, `dfx_close()`, `dfx_xmt_queue_pkt()`, `dfx_ctl_get_stats()`, `dfx_ctl_set_multicast_list()`, and `dfx_ctl_set_mac_address()` into the networking core.

Low-level hardware access is funneled through `dfx_port_read_long()` and `dfx_port_write_long()`, which choose MMIO or port I/O dynamically. Bus-specific setup is in `dfx_get_bars()`, `dfx_bus_init()`, `dfx_bus_uninit()`, and `dfx_bus_config_check()`. Adapter commands are issued by `dfx_hw_port_ctrl_req()` for port-control CSR commands and `dfx_hw_dma_cmd_req()` for firmware DMA commands. Receive and transmit ring routines are `dfx_rcv_init()`, `dfx_rcv_queue_process()`, `dfx_rcv_flush()`, `dfx_xmt_queue_pkt()`, `dfx_xmt_done()`, and `dfx_xmt_flush()`.

The key private state is `DFX_board_t` from `defxx.h`, especially `descr_block_virt/phys`, `cmd_req_virt`, `cmd_rsp_virt`, `cons_block_virt`, producer register shadows, CAM/filter tables, link state, receive skb pointers, transmit skb descriptors, bus base, and statistics counters.

## Control Flow
Probe allocates an FDDI netdev, enables PCI when needed, chooses MMIO first with fallback to I/O for PCI/EISA, reserves resources, maps MMIO or records port base, initializes bus logic, resets the adapter into DMA-unavailable state, reads the factory MAC address via `PI_PCTRL_M_MLA`, allocates one coherent block for descriptors, command buffers, receive storage metadata, and the consumer block, then registers the netdev.

Open requests the shared IRQ, restores the factory MAC, clears local CAM/filter state, initializes the spinlock, and calls `dfx_adap_init()`. `dfx_adap_init()` disables PDQ interrupts, resets/uninitializes DMA, clears false Type 0 interrupts and ring shadows, programs burst size, consumer block address, descriptor block address and byte-swap mode, sends `CHARS_SET`, `SNMP_SET`, CAM, filter, receive-buffer, and `START` commands, then reenables default interrupts.

Interrupt handling is split by bus. PCI checks `PFI_STATUS_M_PDQ_INT`, masks PFI interrupts, calls `dfx_int_common()`, clears PFI status, and reenables PFI. EISA checks ESIC pending status and masks/unmasks the ESIC. TURBOchannel checks PDQ pending bits directly. `dfx_int_common()` completes TX, processes RX, writes the Type 2 producer/completion shadow once, then handles Type 0 interrupts. Type 0 processing handles fatal errors, transmit flush requests, state changes, link availability, halted states, and reset/reinitialization.

Transmit validates FDDI LLC length, drops stale packets while link is unavailable, prepends the three-byte Motorola MAC packet request header, DMA-maps the skb, fills one transmit descriptor, records the skb for completion, advances the transmit producer, and writes the Type 2 producer register. Completion uses the consumer block to unmap and consume skbs. Receive walks the firmware consumer index, reads the FMC descriptor, accounts CRC/status/length errors, either copies small packets or swaps in a new skb for larger packets, strips driver padding/CRC, calls `fddi_type_trans()`, passes packets through `netif_rx()`, updates counters, then recycles descriptors.

## State And Persistence Behavior
Persistent in-kernel state lives in `DFX_board_t` for the lifetime of the netdev. Hardware state is rebuilt at each open or adapter reset from driver-maintained defaults: factory MAC, optional MAC override, CAM entries, multicast counts, promiscuous bits, burst size, full-duplex flag, requested TTRT, and receive buffer count. DMA-visible descriptor and command memory is allocated once during probe and freed during remove. RX skbs are dynamically allocated under `DYNAMIC_BUFFERS` and flushed on close/reset failure paths. TX skbs are held until adapter completion or flush.

The adapter itself persists firmware state across commands until reset; the driver intentionally resets it on initialization, close, fatal Type 0 errors, and halted-state recovery. There is no disk persistence or userspace configuration file handling.

## Dependencies And Integration Points
The file integrates with Linux PCI, EISA, TURBOchannel, DMA mapping, netdevice, FDDI helpers, shared IRQ handling, MMIO/PIO APIs, and module infrastructure. It depends heavily on constants and packed hardware ABI definitions from `defxx.h`, plus Linux FDDI constants such as `FDDI_K_ALEN`, `FDDI_K_LLC_ZLEN`, and `FDDI_K_LLC_LEN`. Bus IDs cover DEC PCI FDDI, EISA `DEC300[1-4]`, and TC `PMAF-F*` modules.

## Risks
The driver assumes 32-bit DMA addresses when writing descriptors and truncates DMA addresses to `u32`; this is historically mitigated by platform/device DMA constraints but is a key portability risk. TX error handling after a full ring returns `NETDEV_TX_BUSY` after DMA mapping and descriptor writes without unmapping in that path, so ring-full behavior is a sensitive area. The command path busy-waits with long `udelay()` loops and can consume CPU during firmware stalls. Receive processing in interrupt context can process multiple buffers and allocate skbs, so memory pressure leads to drops. MMIO/PIO fallback and EISA decoder programming are hardware-specific and hard to validate without real devices. Reset recovery reenters adapter initialization from interrupt context for serious errors, so locking and interrupt masking assumptions matter.

## Test Signals
Useful build signals are `CONFIG_DEFXX` across PCI, EISA, TC, `CONFIG_HAS_IOPORT`, and big-endian builds because producer/consumer layouts differ. Runtime smoke signals are probe resource reservation, factory MAC read, `register_netdev()`, successful `ifconfig/ip link set up`, IRQ request, link-available messages, packet RX/TX counters, multicast filter changes, MAC override, close/reopen, and module unload. Fault-oriented signals include forced link transitions, TX flush interrupt handling, adapter halt reset, DMA mapping failure paths, RX memory pressure drops, and no IRQ storms on shared lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/defxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/defxx.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/defxx.h

## Purpose
Defines the PDQ/DEC FDDIcontroller hardware and firmware interface consumed by `defxx.c`. It provides fixed-width aliases, port-interface command IDs, response layouts, SMT/FDDI MIB layouts, descriptor and consumer block formats, producer register views for little- and big-endian hosts, bus register offsets for TC/EISA/PCI variants, packet request header constants, driver return codes, and the driver's private board structure.

## Important APIs, Types, And Definitions
Core wire types include `PI_UINT8`, `PI_UINT16`, `PI_UINT32`, `PI_CNTR`, `PI_LAN_ADDR`, and `PI_STATION_ID`. Firmware command ABI is represented by per-command request/response structures such as `PI_CMD_FILTERS_SET_REQ`, `PI_CMD_CHARS_SET_REQ`, `PI_CMD_SMT_MIB_GET_RSP`, `PI_CMD_ADDR_FILTER_SET_REQ`, `PI_CMD_STATUS_CHARS_GET_RSP`, `PI_CMD_FDDI_MIB_GET_RSP`, `PI_CMD_DEC_EXT_MIB_GET_RSP`, and counter/error-log structures. `PI_DMA_CMD_REQ`, `PI_DMA_CMD_RSP`, and `PI_DMA_CMD_BUFFER` unify 512-byte command buffers.

DMA ring ABI definitions include `PI_CONSUMER_BLOCK`, `PI_RCV_DESCR`, `PI_XMT_DESCR`, and `PI_DESCR_BLOCK`, with fixed queue sizes for receive, transmit, SMT host, unsolicited, command response, and command request rings. `PI_TYPE_1_PROD_REG`, `PI_TYPE_2_PROD_REG`, `PI_TYPE_1_CONSUMER`, and `PI_TYPE_2_CONSUMER` are endian-sensitive views of producer/consumer longwords.

Hardware constants cover PDQ port registers, port-control commands, adapter states, halt IDs, host interrupt masks, Type 0 interrupt bits, TC CSR placement, EISA ESIC register layout, DEC EISA product IDs, PCI PFI register layout, DMA burst sizes, byte-swap initialization flags, and FDDI PRH bytes. `DFX_board_t` is the main software state container used by `defxx.c`.

## Control Flow Semantics
This header is declarative, but it encodes the state machine that `defxx.c` follows: reset and DMA unavailable states are reached through port reset/control commands; consumer and descriptor block addresses are provided through port-control commands; firmware DMA commands are posted via command request/response rings; RX/TX progress is synchronized through producer register shadows and the consumer block; Type 0 status bits trigger reset, flush, or link-state handling.

The endian-specific producer/consumer unions determine how byte-sized indices are read from and written to a 32-bit hardware register. The descriptor bit fields define how the driver marks SOP/EOP, segment sizes, physical buffer high bits, frame status, and packet lengths.

## State And Persistence Behavior
The file defines only in-memory and hardware-visible state; no persistent storage is involved. Structures in `DFX_board_t` persist for the netdev lifetime, while descriptor blocks, command buffers, consumer blocks, CAM tables, filter flags, receive skb pointers, transmit skb pointers, and statistics counters are reset or rebuilt by `defxx.c` at probe, open, close, or adapter reset boundaries.

## Dependencies And Integration Points
The header assumes Linux kernel definitions from files included by `defxx.c`, including `u8/u16/u32`, `dma_addr_t`, `struct sk_buff`, `spinlock_t`, `struct net_device`, `struct device`, `struct fddi_statistics`, and FDDI constants. It is tightly coupled to the DEC PDQ port specification, DEC EISA ESIC, DEC PCI PFI, and TURBOchannel CSR layout. Because the structures mirror firmware-visible buffers, field order and sizes are integration contracts.

## Risks
ABI drift is the primary risk: changing structure layout, field width, queue size, alignment, or endian mapping can break DMA with firmware. Several descriptor physical address fields are `PI_UINT32`, so users must ensure DMA addresses fit hardware expectations. Constants such as receive buffer alignment, descriptor block 8 KiB alignment, and command buffer 512-byte size are not optional. Some command response structures are very large and mirror SMT/FDDI specifications; incorrect copying or casting can corrupt statistics. The header also encodes legacy bus assumptions that may not hold on newer architectures.

## Test Signals
Compile coverage on little-endian and big-endian configurations is important because the producer/consumer unions differ. Runtime validation comes from successful adapter initialization, firmware command completion, stable RX/TX ring advancement, correct FDDI statistics, multicast CAM updates, and clean reset/close. Static checks should watch structure sizes, descriptor block alignment, and absence of unintended padding changes in firmware-visible structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/defxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/defza.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/defza.c

## Purpose
Implements the Linux TURBOchannel driver for DEC FDDIcontroller 700/700-C DEFZA devices. Unlike `defxx.c`, this driver talks to the FZA shared packet memory and FZA command/ring protocol defined by the DEC FDDIcontroller 700 port specification. It probes TC devices, maps the full MMIO resource, resets and initializes firmware, publishes a `net_device`, handles RX/TX and SMT rings, maintains link/reset state, and supports module-configured loopback mode.

## Important APIs, Types, And Functions
The module registers one `tc_driver` from `fza_init()` and unregisters it in `fza_exit()`. `fza_probe()` and `fza_remove()` are the lifecycle entry points. `net_device_ops` connects `fza_open()`, `fza_close()`, `fza_start_xmit()`, `fza_set_rx_mode()`, `fza_set_mac_address()`, and `fza_get_stats()`.

MMIO helpers `fza_reads()`, `fza_writes()`, `fza_moves()`, and `fza_zeros()` perform packet-memory transfers using 32- or 64-bit relaxed accesses while respecting the board's word-access constraints. Reset and command helpers include `fza_do_shutdown()`, `fza_do_reset()`, `fza_reset()`, `fza_cmd_send()`, and `fza_init_send()`. Ring processing is handled by `fza_rx_init()`, `fza_do_xmit()`, `fza_do_recv_smt()`, `fza_tx()`, `fza_rx_err()`, `fza_rx()`, `fza_tx_smt()`, `fza_uns()`, and `fza_tx_flush()`. `fza_interrupt()` dispatches command, TX, RX, SMT, flush, link, unsolicited, and state-change events.

The module parameter `loopback` is sanitized in probe and sent through the PARAM command. The static purger and beacon multicast addresses are always inserted into the CAM before user multicast entries.

## Control Flow
Probe allocates an FDDI netdev, reserves and maps the TC memory resource, initializes private pointers to registers and rings, sets wait queues/spinlock/timer, shuts the board down, requests the shared IRQ, enters driver mode, resets the board, sends INIT, reads hardware address, revision strings, ring addresses/sizes, default link parameters, SMT version, and PMD type, then closes the interface back to the uninitialized state before registering the netdev.

Open allocates and 512-byte-aligns all host receive skbs, DMA-maps them, sends INIT again, programs CAM/promiscuous mode, sends PARAM, and waits for command completion. Subsequent state-change interrupts move the device from initialized to running/maintenance, call `fza_rx_init()`, mark the queue active, and wake TX. Close stops the queue, deletes the reset timer, issues SHUT, waits for uninitialized state, then unmaps/frees RX skbs.

TX prepends a three-byte packet request header based on the FDDI frame-control byte, temporarily masks SMT TX poll interrupts to serialize access to the RMC transmit ring, copies skb data into board packet memory through `fza_do_xmit()`, frees the skb immediately after queuing, and returns the queuing result. `fza_do_xmit()` fragments into 512-byte board buffers, writes all non-first descriptors before finally handing the first descriptor to the RMC, and stops the netdev queue when remaining ring space falls below one MTU plus header.

RX walks the host receive ring until ownership returns to FZA, reads the RMC status, validates errors and length in `fza_rx_err()`, allocates a replacement aligned skb, unmaps the completed buffer, optionally feeds non-promiscuous async management frames into the SMT RX ring, trims preamble/starting delimiter/FCS, calls `fddi_type_trans()`, submits via `netif_rx()`, updates counters, and returns the descriptor to FZA. SMT TX frames from firmware can be mirrored to packet taps with `dev_queue_xmit_nit()` and then queued into the RMC TX ring. Unsolicited events currently account RX-overrun events.

## State And Persistence Behavior
All state is in `struct fza_private` for the netdev lifetime: MMIO pointers, ring indices, RX skb/DMA arrays, command/state wait flags, reset timer state, queue-active flag, interrupt mask, counters, and firmware-provided link parameters. Hardware command buffers and rings live in adapter memory and are addressed via offsets returned by INIT. RX buffers are allocated per open and freed on close/remove. The reset timer persists while recovery is in progress; if a reset times out it asserts reset harder for one second, then clears reset and waits again. There is no disk persistence.

## Dependencies And Integration Points
The file depends on Linux TURBOchannel, FDDI netdev setup, DMA mapping, wait queues, timers, interrupt APIs, MMIO APIs including non-atomic lo-hi 64-bit I/O, and constants/types from `defza.h`. It integrates with the net stack through `alloc_fddidev()`, `register_netdev()`, `netif_rx()`, carrier state, queue wake/stop, packet taps, and `fddi_type_trans()`. It is matched only to TC module `PMAF-AA`.

## Risks
Hardware access ordering and access width are critical; packet memory comments state only word writes/reads are permitted. `fza_start_xmit()` frees the skb even when `fza_do_xmit()` reports busy, so return semantics are sensitive and should be audited against current netdev expectations. Open error paths after RX allocation or command failure do not obviously free every allocated RX skb before returning in all cases. State transitions rely on interrupts and wait queues; missed `STATE_CHG` or `CMD_DONE` events cause multi-second timeouts. Reset recovery manipulates timers from interrupt and timer contexts, so synchronization around `reset_timer` and `fp->lock` matters. `fza_set_mac_address()` returns `-EOPNOTSUPP`, so address changes are intentionally unsupported despite CAM programming for multicast.

## Test Signals
Build with `CONFIG_DEFZA` and TURBOchannel support. Runtime smoke tests should show probe, reset completion, INIT success, revision/MAC logging, close-to-uninitialized during probe, successful `register_netdev()`, open PARAM completion, link carrier changes, RX/TX counters, queue stop/wake behavior, multicast/promiscuous updates, SMT traffic handling, close SHUT completion, and remove cleanup. Fault signals include reset timeout recovery, HALTED-state reset, command timeout logs, RX overrun unsolicited events, memory-pressure drops, and no divide-by-zero or ring-index corruption during early interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/defza.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/defza.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/defza.h

## Purpose
Defines the register map, ring descriptors, command buffers, status bits, packet request header constants, and private state structure for the DEC FDDIcontroller 700/700-C DEFZA driver. It is the hardware ABI layer used by `defza.c`.

## Important APIs, Types, And Definitions
Register constants describe FZA reset, interrupt event, status, interrupt mask, and control registers under `FZA_REG_BASE`, with bit definitions for reset sequencing, interrupt sources, adapter states, link status, halt reasons, self-test failures, and control actions. `struct fza_regs` overlays the sparse MMIO register layout.

Ring structures include `struct fza_ring_cmd`, `struct fza_ring_uns`, `struct fza_ring_rmc_tx`, `struct fza_ring_hst_rx`, and `struct fza_ring_smt`. Ownership constants define host/FZA/RMC ownership conventions, noting that RMC TX ownership is reversed. Buffer and ring constants define command/unsolicited ring sizes, host RX size, TX buffer addressing, 512-byte TX packet-memory slots, and 4096+512-byte RX buffers.

Command data structures include `struct fza_cmd_init`, `struct fza_cmd_cam`, `struct fza_cmd_param`, `struct fza_cmd_modprom`, `struct fza_cmd_setchar`, `struct fza_cmd_rdcntr`, `struct fza_cmd_status`, and `union fza_cmd_buf`. `struct fza_counters` maps firmware counters. Packet request header constants define PRH bytes for LLC and SMT transmission. `struct fza_private` is the driver-private netdev state. `struct fza_fddihdr` models the on-wire preamble/starting delimiter plus Linux `struct fddihdr`.

## Control Flow Semantics
The header encodes the control protocol followed by `defza.c`: reset moves the adapter through `RESET` and `UNINITIALIZED`; INIT command returns ring locations, default link parameters, revisions, and the link address; MODCAM/MODPROM update receive filtering; PARAM applies link parameters and loopback; TX/RX/SMT rings exchange ownership by setting or clearing `FZA_RING_OWN_MASK`; interrupt event bits wake the corresponding command, RX, TX, SMT, unsolicited, flush, link, or state-change handlers.

## State And Persistence Behavior
The definitions describe volatile MMIO and adapter-memory state. `struct fza_private` persists while the netdev exists and records software shadows for ring indices, interrupt mask, command/state wait flags, reset timer, queue state, stats, and link parameters copied from INIT. RX skb/DMA arrays are populated on open and cleared on close. Firmware rings live in mapped adapter memory and are reinitialized by reset/INIT. No persistent storage is defined.

## Dependencies And Integration Points
The header includes Linux compiler, FDDI, spinlock, timer, and type definitions. It assumes TURBOchannel little-endian behavior in the implementation, but the structures themselves are expressed as native integer fields accessed through MMIO helpers. It integrates with the Linux netdev and DMA APIs through `struct fza_private`, and with FDDI frame definitions through `struct fddihdr` and FDDI frame-control constants used by `defza.c`.

## Risks
Incorrect structure offsets or ring ownership constants can deadlock command, RX, or TX processing. Access-width requirements are implicit in how `defza.c` copies these buffers; future changes must preserve word-aligned packet-memory operations. Ring size macros have compile-time validation for RX size and TX mode, but firmware-returned ring sizes still need sane runtime handling. The command buffer structures mirror a hardware specification and must not be reordered or widened casually.

## Test Signals
Compile coverage should validate the `#error` guards for ring sizing and all users of `struct fza_private`. Runtime validation comes from successful INIT parsing, sensible ring sizes and addresses, correct MAC/revision reads, ownership transitions on all rings, carrier changes, RX/TX/SMT movement, and reset/SHUT state transitions without timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/defza.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/Makefile

## Purpose
Builds the SysKonnect FDDI PCI adapter driver object within the Linux kernel Kbuild system. It declares the `skfp.o` composite object when `CONFIG_SKFP` is enabled and lists the driver, hardware module, SMT, queue, timer, resource-management, and optional ESS object files that form the final module/built-in object.

## Important APIs, Types, And Functions
The public build interface is Kbuild syntax. `obj-$(CONFIG_SKFP) += skfp.o` gates compilation on the kernel configuration symbol. `skfp-objs := ...` declares the object aggregation list: `skfddi.o`, `hwmtm.o`, `fplustm.o`, `smt.o`, `cfm.o`, `ecm.o`, `pcmplc.o`, `pmf.o`, `queue.o`, `rmt.o`, `smtdef.o`, `smtinit.o`, `smttimer.o`, `srf.o`, `hwt.o`, `drvfbi.o`, and `ess.o`. `ccflags-y` adds `-DPCI`, `-DMEM_MAPPED_IO`, and suppresses strict-prototype warnings.

## Control Flow
There is no runtime control flow. During kernel builds, Kbuild evaluates `CONFIG_SKFP`, compiles each listed source into an object, then links them into `skfp.o`. The preprocessor flags select PCI and memory-mapped I/O code paths inside the SysKonnect sources.

## State And Persistence Behavior
The file has no runtime state. Its state effect is build-system state: enabling or disabling the composite driver and changing preprocessor symbols for all sources in this directory. Build outputs persist only as normal generated kernel objects outside the source file.

## Dependencies And Integration Points
This integrates with Linux Kbuild and the kernel configuration symbol `CONFIG_SKFP`. It assumes all listed `.c` files are present in the same directory and are compatible with `-DPCI -DMEM_MAPPED_IO`. The comment documents an intentional integration constraint: the hardware module source is shared with other projects, so warning cleanup is avoided to preserve common code.

## Risks
Object-list drift can silently omit driver subsystems or fail the build if a file is renamed. The global `ccflags-y` affects all listed objects, so changing it can alter hardware access mode or platform assumptions throughout the driver. Suppressing `-Wstrict-prototypes` can hide prototype quality issues, but the comment indicates this is a deliberate tradeoff for shared vendor code.

## Test Signals
Build with `CONFIG_SKFP=m` and `CONFIG_SKFP=y` to confirm both module and built-in paths link. Inspect the compile command for `-DPCI -DMEM_MAPPED_IO`. A clean build should produce `skfp.o` from all listed objects without missing-symbol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/Makefile -->

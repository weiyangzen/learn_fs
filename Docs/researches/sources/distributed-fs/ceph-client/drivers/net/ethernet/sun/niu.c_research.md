# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/niu.c

## Purpose

`niu.c` is the Linux network driver for Sun/Oracle Neptune NIU Ethernet hardware. It supports PCIe Neptune cards and, on SPARC64, Open Firmware platform NIU devices. The driver registers a `net_device`, discovers board/port invariants, configures PHY/SERDES/MAC blocks, allocates RX/TX DMA rings, handles interrupts through logical device groups, exposes ethtool configuration/statistics/filtering hooks, and performs runtime reset, suspend, resume, and removal cleanup.

This file is hardware-centric. Most of its logic is register programming around blocks defined in `niu.h`: MAC (`XMAC`/`BMAC`), PCS/XPCS, IPP, ZCP, FFLP/TCAM classifier, TXC/TXDMA/RXDMA, MIF/MDIO, EEPROM/SPROM, interrupt LDG/LDN, and port/channel partitioning.

## Important APIs, Types, and Functions

Primary external API surfaces:

- Module registration: `module_init(niu_init)` registers PCI and optional OF platform drivers; `module_exit(niu_exit)` unregisters them.
- PCI driver: `niu_pci_driver` probes Sun vendor device `0xabcd` through `niu_pci_init_one()` and removes it through `niu_pci_remove_one()`.
- OF platform driver: `niu_of_driver` matches `SUNW,niusl` and uses `niu_of_probe()`/`niu_of_remove()` under `CONFIG_SPARC64`.
- netdev ops: `niu_netdev_ops` implements open/close, transmit, stats, RX mode, MAC address, MTU change, ioctl stub, and TX timeout.
- ethtool ops: `niu_ethtool_ops` provides driver info, EEPROM reads, message level, link settings, stats, LED identify, RX NFC TCAM rules, and RX hash field configuration.
- power management: `niu_suspend()` and `niu_resume()` stop/reinitialize active devices.

Key state types are defined in `niu.h` and consumed here:

- `struct niu`: per-port private driver state, including MMIO bases, parent pointer, feature flags, RX/TX rings, LDGs, MAC stats, timer, reset work, port number, PHY ops, link config, classifier state, VPD/SPROM data, and optional OF resources.
- `struct niu_parent`: shared multi-port hardware state keyed by PCI domain/bus/device or OF parent. It stores port topology, channel division, RDC tables, LDG map, TCAM entries, classifier keys, PHY probe information, platform type, refcount, sysfs parent device, and a lock for shared hardware programming.
- `struct rx_ring_info`: RX channel state, RBR/RCR coherent DMA tables, mailbox, page hash, refill cursors, counters, WRED thresholds, and interrupt mitigation parameters.
- `struct tx_ring_info`: TX channel state, coherent descriptor ring and mailbox, SKB/DMA mapping metadata, producer/consumer cursors, wrap bit, mark accounting, counters, and max burst.
- `struct niu_link_config`: desired and active speed/duplex/autoneg/advertising/loopback state.
- `struct niu_phy_ops`: per-transport hooks for SERDES init, external transceiver init, and link status.
- `struct niu_tcam_entry` and `struct niu_classifier`: software mirrors for classifier/TCAM rules and VLAN/alternate-MAC RDC mappings.
- `struct niu_ops`: DMA abstraction, using normal DMA APIs for PCI and physical-address helpers for SPARC platform devices.

Major function families:

- Register waits and MMIO wrappers: `nr64*`, `nw64*`, `__niu_wait_bits_clear*()`, `niu_set_and_wait_clear*()`.
- MDIO/MII/PHY: `mdio_read()`, `mdio_write()`, `mii_read()`, `mii_write()`, BCM8704/8706 and Marvell 88x2011 init/status helpers.
- SERDES/link: `serdes_init_*()`, `niu_determine_phy_disposition()`, `niu_init_link()`, `niu_timer()`, `niu_link_status_common()`.
- Classifier: `fflp_early_init()`, `tcam_*()`, `hash_write()`, `vlan_tbl_write()`, `niu_init_classifier_hw()`, ethtool RX NFC rule add/delete/get helpers.
- DMA data path: `niu_alloc_channels()`, `niu_init_one_rx_channel()`, `niu_init_one_tx_channel()`, `niu_process_rx_pkt()`, `niu_rx_work()`, `niu_start_xmit()`, `release_tx_packet()`, `niu_tx_work()`.
- Interrupts: `niu_ldg_init()`, `niu_request_irq()`, `niu_interrupt()`, `niu_slowpath_interrupt()`, `niu_schedule_napi()`, `niu_poll()`.
- Lifecycle: `niu_open()`, `niu_close()`, `niu_init_hw()`, `niu_stop_hw()`, `niu_reset_task()`, `niu_change_mtu()`, probe/remove paths.

## Control Flow

Probe begins in either `niu_pci_init_one()` or `niu_of_probe()`. Both allocate an Ethernet device with `niu_alloc_and_init()`, create or attach to a shared `niu_parent`, map register resources, assign netdev/ethtool ops, and call `niu_get_invariants()`.

`niu_get_invariants()` derives static port configuration. On OF-capable systems it prefers device-tree properties such as `phy-type`, `local-mac-address`, `model`, and `hot-swappable-phy`. Otherwise PCI devices enable EEPROM PIO, try VPD parsing, validate VPD, and fall back to SPROM. It then validates the port, probes PHY layout, divides RX/TX channels and RDC groups across ports, initializes LDG interrupt mappings, initializes classifier software state, initializes link configuration, selects `niu_phy_ops`, and performs initial link/PHY setup.

Open flow in `niu_open()`:

1. Carrier is forced down.
2. RX/TX ring state and coherent DMA memory are allocated by `niu_alloc_channels()`.
3. Interrupts are masked, IRQs are requested, and NAPI contexts are enabled.
4. Under `np->lock`, `niu_init_hw()` programs TXC, TXDMA, RXDMA, classifier, ZCP, IPP, PCS/MAC, and enables MAC TX/RX.
5. Interrupts are enabled, TX queues are started, loopback may force carrier on, and the link timer starts.

RX fast path:

1. Hardware raises an LDG interrupt and `niu_interrupt()` reads `LDSV0/1/2`.
2. Fast RX/TX bits cause `niu_schedule_napi()` to mask involved LDNs and schedule NAPI.
3. `niu_poll()` calls `niu_poll_core()`, which runs `niu_rx_work()` for RX channels and `niu_tx_work()` for TX completions.
4. `niu_rx_work()` reads queue length, processes RCR entries with `niu_process_rx_pkt()`, refills RBR pages, acknowledges consumed packet/pointer counts, and syncs hardware discard counters under load.
5. `niu_process_rx_pkt()` maps RCR entries back to DMA pages through the `rxhash`, builds an SKB using page frags, handles multi-fragment packets, records RX hash/checksum status, updates counters, and submits to GRO.

TX fast path:

1. `niu_start_xmit()` selects the TX ring from `skb_get_queue_mapping()`, verifies descriptor availability, pads and headroom-adjusts the SKB, pushes a Neptune TX packet header, computes checksum/length/VLAN/IP metadata, DMA maps the linear data and frags, writes TX descriptors, and kicks hardware.
2. Completion status is captured in interrupt handling and consumed by `niu_tx_work()`.
3. `release_tx_packet()` unmaps descriptors, updates counters, clears SKB ownership, and frees the SKB.
4. Queues are stopped when descriptor space is low and woken when completions restore enough room.

Slow/error interrupts are handled in `niu_slowpath_interrupt()`. RX fatal/status bits invoke `niu_rx_error()`, TX fatal bits invoke `niu_tx_error()`, MIF invokes `niu_mif_interrupt()`, MAC status updates software MAC counters, and core device errors log subsystem bits. Fatal errors disable interrupts; TX timeouts separately schedule `niu_reset_task()`.

Close/reset flow:

- `niu_close()` calls `niu_full_shutdown()`, frees IRQs/channels, and turns LED state off.
- `niu_full_shutdown()` cancels reset work, disables NAPI and TX queues, deletes the timer, and stops hardware under the device lock.
- `niu_reset_task()` stops the netif and timer, stops hardware, rebuilds ring buffers, reinitializes hardware, restarts the timer, NAPI, queues, and interrupts if successful.
- `niu_change_mtu()` updates MTU, and if jumbo/non-jumbo class changes while running, performs a shutdown/free/reallocate/reinitialize sequence because RX buffer sizing changes.

## State and Persistence Behavior

The driver has no user-space persistent storage. Runtime state lives in memory, MMIO registers, DMA rings, and device EEPROM/VPD/SPROM reads.

Per-port mutable state includes `np->flags`, link configuration, MAC stats, ring pointers/counters, timer state, reset work, VPD cache, MMIO offsets, and `net_device` feature state. Per-parent mutable state includes discovered port topology, channel assignments, RDC tables, LDG mappings, software TCAM entries, classifier keys, user-programmed L3 classes, and a refcount. Parent lifetime spans all ports sharing the same physical device or OF parent and is represented by a synthetic `niu-board` platform device with sysfs attributes.

Hardware state is extensively mirrored but not fully reconstructible from hardware. Classifier TCAM entries are mirrored in `parent->tcam`; flow keys and user class reference counts are kept in `parent`. RX page ownership is tracked in `rx_ring_info->rxhash`, with the driver intentionally aliasing `struct page.mapping` via `union niu_page` to link pages in hash buckets. TX SKB/DMA mappings are tracked in `tx_buffs`.

Link status is polled by `niu_timer()`: one-second polling while carrier is down and five-second polling while up. The timer updates carrier, LED state, and XIF programming through `niu_link_status_common()`.

## Dependencies and Integration Points

Kernel subsystems used:

- PCI core, PCIe capability handling, MSI-X, resource mapping, and driver data.
- SPARC/Open Firmware platform device support when `CONFIG_SPARC64` is enabled.
- netdevice core, NAPI, multi-queue TX/RX, carrier state, GRO, VLAN-aware frame parsing, multicast/unicast filtering, and watchdog timeout.
- DMA mapping APIs for PCI and physical address helpers for SPARC platform NIU.
- ethtool for link settings, EEPROM, stats, LED identify, RX NFC, and RX hash fields.
- MII/MDIO constants and helpers for PHY negotiation/status translation.
- timers, workqueues, spinlocks, mutexes, sysfs device attributes, and module parameters.

Hardware integration points:

- Register definitions and descriptor formats come from `niu.h`.
- EEPROM/VPD/SPROM are read through ESPC registers to determine board model, MAC addresses, number of ports, firmware version, and PHY type.
- External PHYs are accessed through MIF/MDIO or MII; supported families include Broadcom BCM8704/8706/5464R-style devices and Marvell 88x2011.
- FFLP/TCAM and FCRAM classifier hardware route traffic to RX DMA channels and expose programmable ethtool rules.
- Parent-shared resources such as classifier initialization, LDG/LDN mappings, TXC controls, and channel division are protected with `parent->lock`.

## Risks and Edge Cases

- The RX page hash uses a deliberate `struct page.mapping` alias (`union niu_page`) as a linked-list pointer. `niu_init()` has a `BUILD_BUG_ON()` for the expected offset, but this remains a fragile low-level coupling to `struct page` layout.
- `niu_find_rxpage()` calls `BUG()` if hardware returns an RX DMA address not present in the hash. A corrupted ring, DMA programming bug, or stale descriptor can panic the kernel.
- Several hardware wait loops return `-ENODEV` on timeout; many reset/init paths abort cleanly, but some stop/reset helpers ignore errors during teardown.
- `niu_txc_set_imask()` reads and modifies `TXC_INT_MASK` but does not write the modified value back before unlocking, which looks suspicious and should be verified against upstream history or hardware behavior.
- `show_txchan_per_port()` calls `__show_chan_per_port(..., 1)`, the same as RX, so the sysfs TX channel attribute appears to print RX channel counts instead of TX counts.
- `niu_add_ethtool_tcam_entry()` has an `out:` label that always unlocks the parent lock. In the `IP_USER_FLOW` branch it may jump to `out` before unlocking or after unlocking depending on path; the successful branch unlocks before proceeding, then later relocks. This deserves careful audit for balanced locking on all error paths.
- Error recovery is coarse. Fatal interrupt paths disable interrupts, while TX timeout schedules full hardware reset. There is limited per-channel recovery.
- IPv6 ethtool RX classification retrieval/programming is explicitly not implemented for TCAM rules, even though flow class constants exist.
- DMA ring alignment and address-mask checks are strict. Probe/open can fail on platforms that cannot provide expected coherent alignment or DMA mask support.
- Link/PHY handling contains many board-specific assumptions and long delays. Hotplug PHY state is debounced only through init/read behavior and link polling.
- `niu_change_mtu()` writes the new MTU before reallocation. If channel allocation or hardware init fails, the interface can retain the new MTU while not fully restarted.

## Test Signals

Useful validation signals for this driver are mostly integration or hardware-in-loop:

- Probe/register: `niu` module loads, `register_netdev()` succeeds, parent sysfs attributes show expected `port_phy`, `plat_type`, `rxchan_per_port`, `txchan_per_port`, and `num_ports`.
- Firmware data: VPD/SPROM parsing produces a valid MAC address, expected model/board model, correct port count, and no checksum/property-length errors.
- Link: carrier transitions are logged with expected speed/duplex; `ethtool` link settings match active PHY/SERDES state; hotplug PHY removal/insertion logs expected state changes.
- Open/close: repeated `ip link set up/down` allocates/frees rings and IRQs without leaks, warnings, or stale carrier.
- RX/TX data path: traffic passes at expected rates, TX queues do not wedge, RX GRO packets are delivered, checksums are accepted, and per-ring counters advance.
- MTU: switching between standard and jumbo MTU causes clean shutdown/reallocate/reinit and jumbo frames pass up to `NIU_MAX_MTU`.
- Interrupts/NAPI: MSI-X or OF interrupts are assigned as expected; RX/TX LDG/LDN mappings match parent topology; NAPI completion rearms LDGs; no interrupt storms.
- Classifier/ethtool: RX hash field changes update `FLOW_KEY`; IPv4 RX NFC rule insert/get/delete updates TCAM state and routes packets to requested RX rings or discard; unsupported IPv6 rules return `-EINVAL`.
- Error paths: simulated or observed RX/TX/core/MIF errors log specific hardware bits, disable/recover as expected, and TX watchdog reset returns interface to service.
- Suspend/resume: active interfaces detach, stop hardware, then reinitialize and restart timers/queues on resume.

# Research group subset-b-004667

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/tsi108_eth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/tsi108_eth.h

## Purpose
This header is the hardware contract for the Tundra Tsi108 Gigabit Ethernet controller driver. It defines big-endian MMIO access helpers, register offsets, interrupt/status bits, DMA queue controls, and the on-device TX/RX descriptor layouts used by the companion Tsi108 Ethernet implementation.

## Important APIs, types, and constants
The `TSI_READ`, `TSI_WRITE`, `TSI_READ_PHY`, and `TSI_WRITE_PHY` macros assume the caller has a `data` object with `regs` and `phyregs` MMIO bases and perform big-endian `in_be32`/`out_be32` accesses. Register groups cover MAC configuration (`TSI108_MAC_CFG1`, `TSI108_MAC_CFG2`, MII management, station address), statistics counters and carry masks, Ethernet controller port control, interrupt status/mask bits, TX/RX queue configuration, queue pointer registers, hash filters, and DMA thresholds.

The public data types are `tx_desc` and `rx_desc`, each aligned to 32 bytes. `tx_desc` holds split buffer and next-descriptor addresses, VLAN metadata, length, and a 32-bit `misc` field using `TSI108_TX_*` ownership/status/control bits. `rx_desc` mirrors the split address and next fields, then exposes VLAN, received length, buffer length, and a 16-bit `misc` field using `TSI108_RX_*` bits. `TSI108_RX_SKB_SIZE` fixes normal RX buffer size at 1536 bytes.

## Control flow and integration
This file has no executable control flow. Runtime code includes it to program the MAC, configure DMA queue endianness and burst behavior, set descriptor ring base pointers with valid bits, arm RX/TX engines, process interrupts from `TSI108_EC_INTSTAT`, and interpret descriptor ownership. The descriptor comments explicitly state the layout assumes big-endian byte order, which ties the header to the Tsi108 platform's register and DMA representation.

## State and persistence behavior
State is entirely hardware-facing. MAC enable bits, link mode, RX filter bits, interrupt masks, statistics counters, queue pointers, and descriptor ownership persist in device registers and DMA memory until reset or reprogramming. The header also exposes statistic carry bits so driver code can account for counter overflow in software.

## Dependencies and integration points
The header depends on Linux integer types plus architecture/platform support for `in_be32` and `out_be32`. It integrates with Linux netdev DMA paths through descriptor memory that must remain 32-byte aligned and visible to the device. PHY management is through Tsi108 MAC MII registers and separate `phyregs` accessors.

## Risks and edge cases
The access macros rely on an implicit variable named `data`, making misuse easy outside the original driver style. Descriptor fields are split into high/low address words, so DMA address width and endian conversion must be handled exactly by callers. Incorrect ownership bit ordering can let the NIC consume partially initialized descriptors. RX buffer sizing is limited to normal Ethernet plus alignment slack, so jumbo support would require coordinated changes. Register bit definitions include several status carry and queue error bits that must be acknowledged correctly to avoid stuck interrupts.

## Test signals
Useful validation is build coverage of the Tsi108 driver on the target architecture, smoke tests for MMIO read/write byte order, TX/RX descriptor ownership transitions under traffic, PHY read/write operations, interrupt masking/acknowledgement behavior, and statistic overflow accounting with high packet rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/tsi108_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/Kconfig

## Purpose
This Kconfig file introduces the Vertexcom Ethernet vendor menu and the `MSE102X` SPI-attached Ethernet driver option.

## Important APIs, types, and functions
There are no C APIs. `NET_VENDOR_VERTEXCOM` is a boolean vendor gate defaulting to `y`, and `MSE102X` is a tristate driver symbol named "Vertexcom MSE102x SPI". `MSE102X` depends on `SPI`, so the driver is only offered when SPI support is available.

## Control flow and integration
The build configuration flow is standard vendor gating: enabling the vendor symbol reveals the specific device option, and selecting `MSE102X` later drives `obj-$(CONFIG_MSE102X)` in the local Makefile. As a tristate, the driver can be built in or as a module.

## State and persistence behavior
Kconfig selections persist in the kernel `.config` and determine whether `mse102x.c` participates in compilation. No runtime state is created by this file.

## Dependencies and integration points
The primary dependency is `SPI`, matching the driver's `spi_driver` registration and SPI transfer protocol. The file is expected to be included from the broader Ethernet vendor Kconfig tree.

## Risks and edge cases
There is no dependency on `OF`, even though the driver supports Device Tree matching and uses `of_get_ethdev_address`; non-DT SPI IDs remain available, so that is likely intentional. Missing dependencies would show up as compile errors only when the symbol is enabled.

## Test signals
Run Kconfig coverage for `CONFIG_SPI=y/m` with `CONFIG_MSE102X=y/m`, confirm the prompt appears under Ethernet vendor drivers, and build `mse102x.o` both built-in and modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/Makefile

## Purpose
This Makefile connects the Vertexcom Kconfig symbol to the actual MSE102x driver object.

## Important APIs, types, and functions
The only build rule is `obj-$(CONFIG_MSE102X) += mse102x.o`. There are no source-level APIs.

## Control flow and integration
When `CONFIG_MSE102X` is `y`, `mse102x.o` is linked into the built-in object set for this directory. When it is `m`, it is built as the `mse102x` module. When unset, no Vertexcom object is produced.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the mapping from `.config` selection to generated object/module outputs.

## Dependencies and integration points
It depends on the surrounding kernel kbuild infrastructure and the local `mse102x.c` implementation.

## Risks and edge cases
The rule is simple; the main risk is symbol/file drift if the source file or Kconfig symbol is renamed.

## Test signals
`make drivers/net/ethernet/vertexcom/` or a kernel build with `CONFIG_MSE102X=m` should produce `mse102x.ko`; `CONFIG_MSE102X=y` should include it in built-in linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/mse102x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/mse102x.c

## Purpose
This is the Linux netdev driver for Vertexcom MSE1021/MSE1022 Ethernet chips attached over SPI. It wraps Ethernet frames in the chip's SPI framing protocol, services an interrupt-per-received-packet model, queues TX work through a workqueue, exposes ethtool/debugfs diagnostics, and registers as a `spi_driver`.

## Important APIs, types, and functions
The main private state is split between `struct mse102x_net`, embedded in netdev private storage, and `struct mse102x_net_spi`, which adds SPI-specific synchronization and transfer state. `mse102x_net` tracks `ndev`, small fixed command RX/TX buffers, `msg_enable`, `txq`, and counters in `struct mse102x_stats`. `mse102x_net_spi` owns the SPI device, a mutex protecting frame transfer, one `spi_message`/`spi_transfer`, TX work, a `valid_cmd_received` diagnostic bit, and optional debugfs dentry.

The SPI protocol helpers are `mse102x_tx_cmd_spi`, `mse102x_rx_cmd_spi`, `mse102x_tx_frame_spi`, and `mse102x_rx_frame_spi`. They use `DET_CMD`, `DET_SOF`, `DET_DFT`, `CMD_RTS`, and `CMD_CTR` to negotiate receive/transmit readiness and frame boundaries. Netdev operations are `mse102x_net_open`, `mse102x_net_stop`, `mse102x_start_xmit_spi`, `eth_mac_addr`, and `eth_validate_addr`. Ettool hooks provide driver info, link reporting, message level control, and private statistics strings. PM hooks call stop/open around suspend and resume. Probe/remove are `mse102x_probe_spi` and `mse102x_remove_spi`.

## Control flow
Probe configures SPI mode 3, 8 bits per word, and a strict 6.0 MHz to 7.142857 MHz max-speed range. It allocates an Ethernet netdev, reserves headroom/tailroom for the SPI SOF/DFT markers, disables TX skb sharing, initializes the mutex, work item, SPI message, TX queue, netdev/ethtool ops, MAC address, and registers the netdev.

Open requests a threaded IRQ with `IRQF_ONESHOT`, starts the queue, forces carrier on, then polls one or two receive attempts to clear a potentially stuck pending SPI interrupt. IRQ handling locks the SPI mutex and calls `mse102x_rx_pkt_spi`. RX sends `CMD_CTR`, expects `CMD_RTS | len`, validates frame length, allocates an aligned skb, consumes invalid frames with maximum length when needed, verifies SOF/DFT unless dropping, then passes valid frames to `netif_rx`.

TX starts in `ndo_start_xmit`: the skb is appended to `txq`, the netdev queue is stopped if `TX_QUEUE_MAX` is reached, and `tx_work` is scheduled. The worker dequeues skbs, locks the SPI mutex, calls `mse102x_tx_pkt_spi`, updates stats, frees skbs, records timeout counters, and wakes the queue. `mse102x_tx_pkt_spi` repeatedly sends `CMD_RTS | len` until the device replies `CMD_CTR`, with a one-second work timeout and staged sleep/backoff, then sends the SOF + padded Ethernet frame + DFT.

Stop turns carrier off, flushes outstanding TX work, stops the queue, purges queued skbs, and frees the IRQ. Remove unregisters the netdev and removes debugfs.

## State and persistence behavior
Runtime state is in the netdev private struct and is not persistent across probe/remove. The driver does not program permanent device configuration other than using the configured SPI mode/speed and runtime MAC address. Statistics persist while the netdev instance lives. `valid_cmd_received` and debugfs `info` expose transient SPI protocol health. Suspend tears down the open netdev path; resume reopens it when it was running.

## Dependencies and integration points
The driver depends on the SPI core, netdev core, ethtool, optional debugfs, Device Tree MAC address helpers, IRQ infrastructure, workqueues, and skb queues. Device matching supports OF compatibles `vertexcom,mse1021` and `vertexcom,mse1022`, plus SPI IDs `mse1021` and `mse1022`. The Kconfig dependency on SPI is essential.

## Risks and edge cases
The SPI transfer object is reused, so the mutex is critical; any future path touching SPI must hold it. RX invalid command handling deliberately consumes a maximum-size frame, which avoids protocol desynchronization but can cost latency. TX timeout is internal to the work item rather than netdev watchdog, so external timeout observability is limited to private ethtool stats and an error-once log. The driver forces carrier on during open and does not manage PHY link state. Probe mutates `spi->controller->min_speed_hz`, which can affect controller-level behavior beyond this device. `velocity`-style DMA risks do not apply, but skb headroom/tailroom and padding are correctness-sensitive for the framing protocol.

## Test signals
Compile with `CONFIG_MSE102X=m/y`, bind via OF and SPI ID, verify SPI setup rejects speeds outside range, exercise ping/iperf traffic in both directions, test short-frame padding, unplug or stall device to trigger `xfer_err`, `invalid_*`, and `tx_timeout`, inspect `ethtool -S`, and verify debugfs `info` reports IRQ, effective SPI speed, mode, queue length, and valid command state. Suspend/resume should preserve functionality when the netdev is up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/mse102x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/Kconfig

## Purpose
This Kconfig file exposes VIA Ethernet support and the driver options for VIA Rhine Fast Ethernet and VIA Velocity Gigabit Ethernet hardware.

## Important APIs, types, and functions
There are no C APIs. `NET_VENDOR_VIA` gates the submenu. `VIA_RHINE` is a tristate that supports PCI and selected OF/platform configurations, depends on I/O ports and DMA, and selects `CRC32` and `MII`. `VIA_RHINE_MMIO` is a boolean tuning option under `VIA_RHINE` that switches Rhine PCI access toward MMIO. `VIA_VELOCITY` is a tristate depending on PCI or OF address/IRQ plus DMA, and selects `CRC32`, `CRC_CCITT`, and `MII`.

## Control flow and integration
Configuration choices drive the local Makefile: `CONFIG_VIA_RHINE` builds `via-rhine.o`, and `CONFIG_VIA_VELOCITY` builds `via-velocity.o`. `VIA_RHINE_MMIO` affects conditional code in `via-rhine.c` that sets `rqNeedEnMMIO` for PCI devices.

## State and persistence behavior
Selections persist in `.config` and determine build inclusion and module availability. No runtime state is created here.

## Dependencies and integration points
Dependencies mirror the source files: Rhine needs PCI or platform IRQ/iomap support, port I/O for PCI-era devices, DMA, CRC hashing for multicast filters, and MII helpers. Velocity needs PCI or OF-mapped platform resources, DMA, CRC helpers for multicast/WOL, and MII helpers.

## Risks and edge cases
`VIA_RHINE_MMIO` changes low-level access mode and can expose hardware/firmware issues on older revisions. The Rhine dependencies are more restrictive than pure platform operation because `HAS_IOPORT` is required. Build coverage should include both PCI and platform paths where possible.

## Test signals
Kconfig tests should confirm expected prompts and dependencies. Build matrices should cover Rhine with and without `VIA_RHINE_MMIO`, Velocity as module and built-in, and `COMPILE_TEST` platform coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/Makefile

## Purpose
This Makefile maps VIA Ethernet Kconfig symbols to their driver objects.

## Important APIs, types, and functions
The build rules are `obj-$(CONFIG_VIA_RHINE) += via-rhine.o` and `obj-$(CONFIG_VIA_VELOCITY) += via-velocity.o`. There are no runtime APIs.

## Control flow and integration
Kbuild includes each object when its Kconfig symbol is built-in or modular. Module names are `via-rhine` and `via-velocity`, matching the Kconfig help text and module metadata in the source files.

## State and persistence behavior
No runtime state exists. The file contributes build graph state only.

## Dependencies and integration points
It depends on the neighboring source files and the parent Ethernet Makefile including this directory.

## Risks and edge cases
The file is intentionally simple. Rename drift between Kconfig symbols, object names, and source files is the primary risk.

## Test signals
Build with `CONFIG_VIA_RHINE=m` and `CONFIG_VIA_VELOCITY=m` and confirm both `.ko` files are produced; repeat with built-in selections for link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-rhine.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-rhine.c

## Purpose
This is the Linux Ethernet driver for VIA Rhine Fast Ethernet controllers, including VT86C100A/Rhine-I, Rhine-II, Rhine-III, integrated southbridge variants, a management adapter path, and a platform/OF VT8500-compatible path. It implements PCI/platform probe, MII link management, DMA descriptor rings, NAPI interrupt handling, VLAN/multicast filtering, Wake-on-LAN, suspend/resume, and legacy hardware workarounds.

## Important APIs, types, and functions
`struct rhine_private` is the core state object. It stores active VLANs, coherent RX/TX descriptor rings, skb arrays and DMA addresses, Rhine-I TX bounce buffers, IRQ and MMIO/PIO addresses, NAPI, locks, work items, quirk flags, ring indexes, RX/TX u64 stats, WOL options, thresholds, MII state, and register base.

Important entry points are `rhine_init`/`rhine_cleanup`, `rhine_init_one_pci`, `rhine_init_one_platform`, `rhine_init_one_common`, `rhine_open`, `rhine_close`, `rhine_start_tx`, `rhine_interrupt`, `rhine_napipoll`, `rhine_rx`, `rhine_tx`, `rhine_tx_timeout`, `rhine_reset_task`, `rhine_slow_event_task`, `rhine_suspend`, `rhine_resume`, and `rhine_shutdown_pci`. Netdev ops include open/stop/start_xmit/stats/set_rx_mode/MII ioctl/VLAN add-kill/tx_timeout. Ettool ops expose driver info, MII link settings, link state, message level, and WOL.

The hardware model is described by register offset enums, interrupt bit enums, descriptor structures, and quirk bits such as `rqWOL`, `rqForceReset`, `rqStatusWBRace`, `rqRhineI`, `rqIntPHY`, `rqMgmt`, and `rqNeedEnMMIO`.

## Control flow
Module init checks a DMI table for BIOSes that need `avoid_D3`, then registers both PCI and platform drivers. PCI probe enables the device, derives quirks from revision, requests regions, maps PIO or MMIO depending on `CONFIG_VIA_RHINE_MMIO`, enables/verifies MMIO when needed, then calls common initialization. Platform probe maps the memory resource, parses IRQ, reads OF match quirks, and enters the same common path.

Common initialization sets a 32-bit DMA mask, allocates netdev state, initializes locks/work/NAPI/MII callbacks, resets and powers the chip, reads or randomizes the MAC, registers the netdev, discovers the PHY, and seeds carrier state. Open requests the shared IRQ, allocates coherent descriptor rings and buffers, re-enables MMIO/power, resets the chip, enables work tasks, initializes registers under netdev lock, then starts the queue. Register initialization writes station address, FIFO thresholds, ring base addresses, RX mode, optional CAM filters, enables NAPI, unmasks interrupts, starts TX/RX, and checks media.

Interrupt handling reads combined status including `IntrStatus2` for writeback-race chips. Fast RX/TX/stat work is moved into NAPI after masking interrupts. NAPI acknowledges non-slow events, calls `rhine_rx` up to budget, reaps TX completions with `rhine_tx`, handles TX errors via threshold bumps and `rhine_restart_tx`, updates hardware error counters, schedules slow work for link/PCI events, and re-enables interrupts when complete. Slow work acknowledges link/PCI events and updates media.

TX maps or bounce-copies the skb, writes descriptor address and length, handles hardware VLAN tagging for management adapters, uses memory barriers before setting `DescOwn`, advances `cur_tx`, wakes the TX engine, and applies queue stop/wake backpressure. TX completion scans from `dirty_tx` to `cur_tx`, handles error bits, unmaps DMA, consumes skbs, updates u64 stats and BQL, and wakes the queue when space returns. RX scans descriptors until owned by hardware or budget is reached, copies small packets when `rx_copybreak` applies, otherwise swaps in a newly allocated DMA buffer, extracts VLAN tags, submits skbs with `netif_receive_skb`, updates u64 stats, and returns descriptors to hardware.

Close disables tasks, NAPI, queue, interrupts, and the chip, then frees IRQ, RX/TX buffers, and coherent rings. Suspend disables tasks/interrupts/NAPI and may program WOL through the PCI shutdown path. Resume restores MMIO/power, resets rings, re-enables tasks, and reinitializes registers.

## State and persistence behavior
Most state is per-netdev and recreated on open. Descriptor rings and RX/TX buffers are allocated when the interface opens and freed on close. MAC address is read from hardware/EEPROM at probe and can be changed through `eth_mac_addr`. WOL options persist in `rp->wolopts` for the device lifetime and are programmed during shutdown/suspend. Hardware MIB-style CRC/missed counters are read and cleared into software stats. D3 avoidance can persist as a module parameter or DMI-derived runtime setting.

## Dependencies and integration points
The driver integrates with PCI, platform/OF, DMA mapping, netdev/NAPI/BQL, MII helpers, ethtool, VLAN acceleration, CRC32 multicast hashing, DMI, PM sleep, and optional netpoll. It relies on Kconfig-selected `MII`, `CRC32`, `HAS_DMA`, `HAS_IOPORT`, and optional MMIO behavior. Hardware integration includes EEPROM reload, PHY MDIO, CAM/VCAM filters, WOL registers, and chip-specific reset paths.

## Risks and edge cases
The driver carries many revision-specific workarounds: Rhine-I alignment/bounce buffers, MMIO enable differences, Tx status writeback race, forced reset, integrated PHY handling, and management adapter VLAN CAM behavior. Correct memory ordering around descriptor ownership and `cur_tx`/`dirty_tx` is critical. RX error counter clearing uses both write and read because chips differ. `rhine_disable_linkmon` can delay in contexts near interrupt handling. Platform remove manually `iounmap`s a devm-mapped resource, which is a point to inspect if ownership changes. WOL and D3 behavior is BIOS-sensitive.

## Test signals
Build with PCI, platform, and `VIA_RHINE_MMIO` variants. Runtime testing should cover open/close, sustained RX/TX, small packet copy path, VLAN filter add/remove on management adapters, multicast/promiscuous/allmulti changes, MII ethtool speed/duplex changes, TX timeout reset recovery, NAPI budget behavior, WOL shutdown/suspend, DMI `avoid_D3`, and netpoll when configured. Counters to watch include tx/rx packets and bytes, CRC/missed errors, TX FIFO/collision errors, and carrier transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-rhine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-velocity.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-velocity.c

## Purpose
This is the VIA Velocity Gigabit Ethernet driver for VT6110/Velocity-family adapters on PCI and OF/platform buses. It implements option parsing, PCI/platform probe, MAC/PHY setup, CAM and VLAN filters, DMA ring allocation, NAPI RX/TX service, checksum/VLAN offloads, interrupt coalescing, WOL, suspend/resume, and ethtool operations.

## Important APIs, types, and functions
The driver depends heavily on `via-velocity.h` for descriptors, registers, options, and `struct velocity_info`. Main lifecycle functions are `velocity_init_module`, `velocity_cleanup_module`, `velocity_pci_probe`, `velocity_platform_probe`, shared `velocity_probe`, `velocity_open`, `velocity_close`, `velocity_remove`, `velocity_suspend`, and `velocity_resume`.

Traffic functions include `velocity_xmit`, `velocity_intr`, `velocity_poll`, `velocity_rx_srv`, `velocity_receive_frame`, `velocity_tx_srv`, `velocity_error`, and ring helpers such as `velocity_init_rings`, `velocity_init_dma_rings`, `velocity_init_rd_ring`, `velocity_init_td_ring`, `velocity_rx_refill`, `velocity_give_many_rx_descs`, and `velocity_free_rings`. MAC/PHY helpers include CAM accessors, `velocity_init_registers`, `velocity_soft_reset`, `velocity_set_media_mode`, `mii_init`, `velocity_mii_read`, `velocity_mii_write`, `enable_mii_autopoll`, and flow-control setup.

Netdev ops expose open/stop/start_xmit/stats/set_rx_mode/change_mtu/ioctl/VLAN add-kill and optional netpoll. Ettool ops expose link settings, WOL, stats, coalescing, link state, driver info, and begin/complete hooks that power the device up for register access while closed.

## Control flow
Module init registers an IPv4 address notifier for ARP WOL support, then registers PCI and platform drivers. PCI probe enables the device, requests regions, and calls shared probe. Platform probe resolves OF match data and IRQ, then calls shared probe. Shared probe allocates netdev/private state, initializes chip metadata, validates bus resources, maps the MAC register window, resets WOL state, reads the hardware MAC address, parses per-adapter module options, captures PHY ID, installs netdev/ethtool/NAPI hooks, enables checksum/scatter-gather/VLAN features, registers the netdev, sets carrier state, stores drvdata, and powers the chip down to D3hot until opened.

Open allocates coherent RX/TX descriptor pools and skb metadata, powers the chip to D0, performs cold register initialization, requests IRQ, gives prepared RX descriptors to the NIC in multiples of four, enables interrupts, starts queueing, enables NAPI, and marks the interface opened. Cold register initialization resets the chip, optionally reloads EEPROM, restores the MAC address, configures DMA and RX thresholds, initializes CAM/VCAM filters, sets multicast mode, enables MII autopolling, programs interrupt suppression, writes RX/TX ring bases and sizes, starts queues, configures flow control, initializes PHY media, writes the interrupt mask, and clears ISR.

TX maps the skb linear data and up to six fragments, linearizing if the hardware segment limit would be exceeded. It programs one TX descriptor, sets VLAN and checksum request bits when applicable, marks ownership, advances ring indexes, stops the queue if no descriptors remain, sets `TD_QUEUE` on the previous descriptor, and wakes the TX queue. TX service runs from NAPI, scans completed descriptors, updates stats or error counters, unmaps DMA, frees skbs, advances tail pointers, and wakes the netdev queue when descriptors are available.

RX service scans descriptors until budget, ownership, or missing skb stops it. For valid frames it synchronizes DMA, validates error bits, applies RX checksum status, copies small packets below `rx_copybreak` or consumes the DMA skb directly, optionally realigns the IP header, removes CRC length, restores hardware VLAN tags, passes the skb to the stack, updates stats, refills buffers, and returns descriptors to the NIC in hardware-required groups of four.

Interrupt handling locks, reads and acknowledges ISR, disables interrupts and schedules NAPI for packet events, and processes non-packet error/link/MIB events through `velocity_error`. MTU changes allocate a temporary complete ring set before swapping under lock, minimizing downtime and preserving old rings until the new setup succeeds.

## State and persistence behavior
Per-device state lives in `struct velocity_info`. RX/TX rings and buffers are allocated on open and freed on close. Module options are copied into `vptr->options` during probe and then used for register programming. Hardware MIB counters are read-and-accumulated into `mib_counter`. WOL settings, password, and cached IPv4 address are retained in memory and programmed during suspend. Suspend saves selected MAC register context, shuts the device down, optionally programs WOL, and enters D3hot; resume restores context and reinitializes the MAC in WOL-resume mode.

## Dependencies and integration points
The driver integrates with PCI, platform/OF address and IRQ parsing, DMA mapping, netdev/NAPI, ethtool, MII, VLAN acceleration, CRC32 and CRC-CCITT, IPv4 address notifications, PM sleep, and optional netpoll. It uses the header's register structure and macros for all hardware access. Platform devices can set `no-eeprom` to skip EEPROM reload.

## Risks and edge cases
The code is register- and revision-sensitive. RX descriptors must be returned in multiples of four, RX buffers require 64-byte alignment, and TX supports at most seven segments. There are limited DMA mapping error checks in the TX fragment path compared with modern patterns. WOL ARP setup uses a static local buffer and single cached IPv4 address, so multi-IP and concurrency scenarios deserve care. Ettool begin/complete use a nesting counter to power-manage closed devices; imbalance would leave the device in the wrong power state. Suspend only acts when netdev is running, while probe powers the chip down when closed. Register context save/restore is partial by design.

## Test signals
Build both PCI and platform variants. Runtime tests should cover open/close, high-throughput RX/TX, scatter-gather with more than six frags, checksum offload, VLAN TX/RX/filtering, jumbo MTU up to 9000, MTU changes while up, multicast/promiscuous modes, link setting changes, interrupt coalescing get/set, MIB overflow/stat reporting, WOL magic/unicast/ARP suspend-resume, ethtool access while down, and platform `no-eeprom` probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-velocity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-velocity.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-velocity.h

## Purpose
This header is the private hardware and state definition layer for `via-velocity.c`. It defines descriptor formats, register offsets and bit masks, MAC register layout, PHY constants, module option structures, WOL packet structures, private adapter state, and inline helper routines for EEPROM reload, IP capture, MIB updates, and flow-control initialization.

## Important APIs, types, and constants
Descriptor types are `struct rx_desc`, `struct tx_desc`, `struct velocity_rd_info`, and `struct velocity_td_info`. RX descriptors expose receive status, length/ownership, VLAN tag/checksum metadata, DMA address, and buffer size/interrupt-enable fields. TX descriptors expose transmit status, length/ownership, VLAN/TCR command fields, and up to seven DMA buffer segments.

`struct mac_regs` maps the 256-byte register window used by the C file, including station address, command set/clear registers, CAM/MAR, interrupt status/mask, RX/TX queue control, ring base registers, MII registers, EEPROM registers, MIB registers, WOL registers, pattern CRCs, and byte masks.

`struct velocity_info` is the main private state: device and PCI pointers, netdev, `no_eeprom`, VLAN bitmap, cached IP, chip ID, mapped registers, resource addresses, TX/RX ring substructures, MIB counters, options, interrupt mask, flags, MII/PHY status, CAM masks, spinlock, WOL settings, saved context, ethtool nesting, revision ID, and NAPI object.

Important enums and constants include descriptor ownership bits, RSR/TSR/TCR checksum/VLAN/error bits, interrupt mask/status bits, command bits, CAM bits, MII control bits, WOL bits, MTU limits, descriptor count limits, PHY IDs, speed/duplex modes, init types, and flow-control modes.

Inline APIs used by the C file include `mac_eeprom_reload`, `velocity_get_ip`, `velocity_update_hw_mibs`, and `init_flow_control_register`. Many register helpers are macros such as `mac_read_isr`, `mac_write_isr`, `mac_disable_int`, `mac_enable_int`, `mac_rx_queue_run`, and `mac_tx_queue_wake`.

## Control flow and integration
This file has only inline/macro control flow. The C file uses it to allocate and program descriptor rings, interpret hardware completion status, configure interrupts and queue wakeups, operate the MII/PHY interface through `velocity_mii_read/write`, set WOL patterns, and synchronize software netdev state with hardware MIB counters.

## State and persistence behavior
The header defines the in-memory state that persists for each probed netdev and the hardware register state saved in `struct velocity_context` across suspend/resume. `velocity_get_ip` caches the first IPv4 address for ARP WOL. `velocity_update_hw_mibs` accumulates read-and-clear hardware counters into software counters. WOL options and MAC context persist in `struct velocity_info` while the netdev exists.

## Dependencies and integration points
It depends on kernel networking types (`sk_buff`, `net_device`, VLAN bitmap sizing, NAPI), PCI/device types, MII constants, endian annotations, and I/O accessors. It is tightly coupled to `via-velocity.c`; the macros call functions such as `velocity_mii_read` and `velocity_mii_write` that are implemented there.

## Risks and edge cases
The register macros perform read-modify-write without internal locking, so callers must serialize access. Many descriptor and status constants are endian-wrapped values; mixing host-endian and little-endian fields incorrectly would break ownership and status checks. The `MII_GET_PHY_ID` macro reads into a `u32` through `u16 *` casts, which is compact but sensitive to endian/layout assumptions. `struct mac_regs` is a hardware overlay and must remain aligned with the documented 256-byte register map. Inline loops that wait for hardware bits have no scheduling points.

## Test signals
Compile coverage should catch structure and macro drift with `via-velocity.c`. Runtime signals include correct descriptor ownership transitions, MIB counter accumulation, interrupt mask behavior, EEPROM reload completion, WOL ARP IP capture, MII reads/writes against supported PHYs, and suspend/resume context restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-velocity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/Kconfig

## Purpose
This Kconfig file defines the Wangxun Ethernet vendor menu and the build symbols for the shared Wangxun library plus physical-function and virtual-function drivers for GbE and 10/25/40GbE PCIe adapters.

## Important APIs, types, and functions
There are no C APIs. `NET_VENDOR_WANGXUN` gates the submenu. `LIBWX` is a hidden tristate common library symbol depending on `PTP_1588_CLOCK_OPTIONAL` and selecting `PAGE_POOL`, `DIMLIB`, and `PHYLINK`. Device options are `NGBE`, `TXGBE`, `TXGBEVF`, and `NGBEVF`. PF drivers depend on PCI and select `LIBWX`; VF drivers depend on PCI MSI and select `LIBWX`. `TXGBE` also selects support libraries for clocks, I2C DesignWare platform, Marvell 10G PHY, regmap, SFP, GPIO, IRQ chips, XPCS, and optional hwmon when built-in.

## Control flow and integration
Selecting a device driver causes the top-level Makefile to descend into the matching subdirectory and, through `select LIBWX`, build the shared `libwx` library. Help text points users to driver documentation under `Documentation/networking/device_drivers/ethernet/wangxun/`.

## State and persistence behavior
Kconfig choices persist in `.config` and determine which Wangxun modules or built-in objects are produced. No runtime state exists here.

## Dependencies and integration points
The file integrates Wangxun drivers with kernel PCI, MSI, PTP, page-pool, DIM, PHYLINK, SFP, XPCS, GPIO, regmap, hwmon, and documentation systems. The hidden `LIBWX` symbol centralizes common dependencies.

## Risks and edge cases
Because `LIBWX` is selected by multiple drivers, dependency mistakes can break broad Wangxun builds. `TXGBE` has many transitive dependencies; configuration combinations around built-in vs module and `HWMON if TXGBE=y` need coverage. VF drivers require MSI-X functionality per help text, represented by `PCI_MSI`.

## Test signals
Build each driver as module and, where supported, built-in. Verify `LIBWX` is selected automatically, `txgbe` pulls the required PHY/SFP/XPCS/GPIO dependencies, and docs referenced by help text remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/Makefile

## Purpose
This Makefile maps Wangxun Ethernet Kconfig symbols to subdirectories for the common library, physical-function drivers, and virtual-function drivers.

## Important APIs, types, and functions
The build rules are `obj-$(CONFIG_LIBWX) += libwx/`, `obj-$(CONFIG_TXGBE) += txgbe/`, `obj-$(CONFIG_TXGBEVF) += txgbevf/`, `obj-$(CONFIG_NGBE) += ngbe/`, and `obj-$(CONFIG_NGBEVF) += ngbevf/`.

## Control flow and integration
Kbuild descends into a subdirectory only when the corresponding symbol is enabled. Because device Kconfig entries select `LIBWX`, the common library directory should be built whenever any dependent Wangxun driver is enabled.

## State and persistence behavior
No runtime state exists. The file contributes build graph state only.

## Dependencies and integration points
It integrates with subdirectory Makefiles and the Kconfig symbols defined in `wangxun/Kconfig`.

## Risks and edge cases
The main risk is missing the `libwx/` descent for a driver that uses common objects, or stale directory names if drivers are renamed.

## Test signals
Build each Wangxun config symbol independently and confirm the expected directory is visited. For selected device drivers, confirm `libwx/` is also included through `CONFIG_LIBWX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/Makefile

## Purpose
This Makefile builds the Wangxun common support library object used by the Wangxun Ethernet drivers.

## Important APIs, types, and functions
The rule `obj-$(CONFIG_LIBWX) += libwx.o` creates the composite library object. `libwx-objs` is composed from `wx_hw.o`, `wx_lib.o`, `wx_ethtool.o`, `wx_ptp.o`, `wx_mbx.o`, `wx_sriov.o`, `wx_vf.o`, `wx_vf_lib.o`, and `wx_vf_common.o`.

## Control flow and integration
When `CONFIG_LIBWX` is enabled directly or selected by a Wangxun driver, kbuild compiles the listed objects and links them into `libwx.o`. Higher-level PF/VF drivers link against or depend on this common code through the directory-level build.

## State and persistence behavior
No runtime state is declared in the Makefile. The listed object files likely provide shared hardware, ethtool, PTP, mailbox, SR-IOV, and VF support state at runtime, but this file only controls composition.

## Dependencies and integration points
The file depends on the `LIBWX` Kconfig symbol and the presence of all listed source files in the `libwx` directory. Kconfig ensures supporting facilities such as PTP, page-pool, DIM, and PHYLINK are available.

## Risks and edge cases
Adding or removing common library source files requires updating `libwx-objs`; otherwise code may be omitted or stale object names may break builds. Because multiple drivers share this library, build failures here affect all Wangxun PF/VF drivers.

## Test signals
Build any driver that selects `LIBWX`, verify `libwx.o` is composed from all listed objects, and run module dependency checks for PF and VF drivers that consume common Wangxun functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/Makefile -->

# Research: subset-b-004617

This grouped report covers Realtek RTASE and Renesas Ethernet AVB, R-Car Gen4 PTP, and R-Switch L2-support files. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/rtase/rtase_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/rtase/rtase_main.c

## Purpose
This file is the complete PCI and netdev implementation for the Realtek RTASE automotive Ethernet switch endpoint driver. It binds PCI device `10ec:906a`, maps the BAR2 MMIO register space, allocates DMA descriptor rings, exposes a multiqueue Ethernet netdev, drives Tx/Rx through NAPI, handles MSI-X or MSI interrupts, reports software and hardware tally statistics, supports VLAN/checksum/TSO/RXFCS/RXALL features, exposes ethtool link/pause/MAC stats, implements CBS traffic-control offload, and handles reset, shutdown, suspend, and resume.

## Important APIs, Types, And Functions
- PCI/module surface: `rtase_pci_tbl`, `rtase_pci_driver`, `rtase_init_one()`, `rtase_remove_one()`, `rtase_shutdown()`, `rtase_suspend()`, and `rtase_resume()`.
- Netdev surface: `rtase_netdev_ops` wires `rtase_open()`, `rtase_close()`, `rtase_start_xmit()`, `rtase_set_rx_mode()`, `rtase_set_mac_address()`, `rtase_change_mtu()`, `rtase_tx_timeout()`, `rtase_get_stats64()`, `rtase_setup_tc()`, `rtase_fix_features()`, and `rtase_set_features()`.
- Queue/ring lifecycle: `rtase_alloc_desc()`, `rtase_free_desc()`, `rtase_init_ring()`, `rtase_tx_desc_init()`, `rtase_rx_desc_init()`, `rtase_tx_clear()`, `rtase_rx_clear()`, and `rtase_rx_ring_fill()` allocate coherent descriptor memory and page-pool Rx buffers.
- Data path: `rtase_start_xmit()` maps skb linear and fragment data into Tx descriptors; `tx_handler()` retires completed Tx descriptors; `rx_handler()` builds recycled skbs from page-pool buffers, handles checksum/VLAN metadata, and feeds GRO.
- Hardware programming: `rtase_hw_config()`, `rtase_nic_enable()`, `rtase_hw_start()`, `rtase_hw_reset()`, `rtase_desc_addr_fill()`, `rtase_interrupt_mitigation()`, and `rtase_hw_set_features()` program DMA, queue, filter, offload, interrupt, and tally-counter registers.
- Interrupt setup: `rtase_alloc_interrupt()`, `rtase_alloc_msix()`, `rtase_init_int_vector()`, `rtase_init_napi()`, `rtase_interrupt()`, `rtase_q_interrupt()`, and `rtase_poll()` connect hardware vectors to per-vector NAPI ring lists.

## Control Flow
Probe rejects virtual functions, allocates an `alloc_etherdev_mq()` netdev, enables PCI, validates BAR2, requests regions, sets a 64-bit DMA mask, maps MMIO, identifies the MAC version from `RTASE_TX_CONFIG_0`, initializes queue counts and interrupt-vector metadata, clears VLAN filter entries, allocates MSI-X with MSI fallback, registers NAPI and netdev/ethtool ops, enables offload feature flags, reads or randomizes the MAC address, allocates a coherent tally counter block, clears hardware counters, and registers the netdev.

Open allocates coherent Tx/Rx descriptors, creates a DMA-mapped page pool, formats Tx and Rx rings, fills all Rx descriptors, configures hardware in reset/config order, requests one IRQ per MSI-X vector or a shared MSI-style IRQ, enables hardware, enables NAPI, marks carrier on, and wakes the netdev queue. Interrupt handlers mask their vector, acknowledge status, and schedule NAPI. `rtase_poll()` runs every ring attached to the vector, retires Tx completions, receives packets up to budget, then re-enables the vector mask after `napi_complete_done()`.

Transmit chooses the queue from `skb_get_queue_mapping()`, prepares VLAN and checksum/TSO bits, maps fragments first, maps the linear head, writes descriptors with DMA barriers, sets `RTASE_DESC_OWN`, records skb ownership on the final descriptor, advances `cur_idx`, stops the subqueue if low on descriptors, and rings `RTASE_TPPOLL` when needed. Receive waits for hardware ownership to clear, checks error bits, rejects fragmented frames as oversized/unsupported, syncs the page-pool buffer for CPU access, builds an skb, applies checksum and VLAN metadata, hands it to GRO, clears the consumed buffer slot, and refills descriptors back to ASIC ownership.

Close disables NAPI, detaches ring list entries from vectors, stops Tx queues and carrier, resets the NIC, clears Tx/Rx software state and page-pool buffers, frees IRQs, and frees coherent descriptors. Tx timeout dumps descriptor, PCI, MMIO, and tally state, then performs a software reset that quiesces IRQ/NAPI, reinitializes rings, restarts hardware, and restores carrier. Suspend detaches and resets a running interface without freeing all PCI resources; resume restores the MAC address, reinitializes rings and hardware if running, and reattaches the netdev.

## State And Persistence
Driver state lives in `struct rtase_private`, the per-vector `struct rtase_int_vector` array, `struct rtase_ring` arrays, page-pool buffers, coherent descriptor memory, a coherent `struct rtase_counters` tally block, MMIO registers, and PCI MSI/MSI-X state. Ring cursors are `cur_idx` and `dirty_idx`; Tx ownership is tracked through `ring->skbuff[]` and `ring->mis.len[]`; Rx ownership is tracked through `ring->data_buf[]` and `ring->mis.data_phy_addr[]`. No disk persistence exists. Hardware-visible state includes descriptor base registers, interrupt masks/status, MAC address registers, queue mode, DMA burst settings, flow-control bits, packet filters, CBS idleslope registers, tally counter DMA address, and feature offload bits.

## Dependencies And Integration Points
The file depends on Linux PCI, netdevice multiqueue APIs, NAPI, DMA mapping, page pool, ethtool, traffic-control CBS offload, VLAN helpers, checksum/TSO helpers, runtime/system PM, and register/descriptor definitions from `rtase.h`. It integrates with the network stack through netdev ops, ethtool ops, per-CPU `tstats`, NAPI GRO, `netif_queue_set_napi()`, `netif_subqueue_completed_wake()`, `netdev_tx_sent_queue()`, and PM callbacks registered through the PCI driver.

## Risks And Edge Cases
- Several descriptor pointer calculations cast `ring->desc` to typed pointers and then add byte-sized products; because `ring->desc` is not visible here, this relies on the header's pointer type matching the intended arithmetic.
- `rtase_rx_ring_clear()` calls `virt_to_head_page(ring->data_buf[i])` before checking whether `data_buf[i]` is non-NULL, which is sensitive to `virt_to_head_page(NULL)` behavior if cleanup runs on partially filled rings.
- `rtase_open()` enables NAPI after `rtase_hw_start()` and IRQ request; an early interrupt before NAPI is enabled would rely on normal IRQ scheduling assumptions and masking.
- DMA mapping failures in transmit drop the skb and return `NETDEV_TX_OK`, so upper layers will not retry.
- Hardware reset, software reset, close, suspend, and resume share ring/page-pool teardown paths; ordering is critical to avoid DMA into freed pages or NAPI touching removed ring list entries.
- The driver reports carrier on unconditionally after open because the PCI endpoint is treated as always linked to the switch GMAC, which differs from PHY-backed drivers.

## Test Signals
Useful validation signals include successful probe and `register_netdev()`, MSI-X allocation with fallback to MSI, queue count and NAPI mapping sanity, Tx/Rx traffic across all queues, VLAN tag insertion/extraction, RXCSUM/IP checksum/TSO/TSO6 toggles, jumbo MTU disabling TSO through `ndo_fix_features`, CBS qdisc offload writes, ethtool pause get/set and MAC stats, rx-all/rxfcs behavior, Tx timeout reset recovery, suspend/resume with a running interface, remove/unload without DMA or NAPI lifetime warnings, and hardware tally counters matching software packet counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/rtase/rtase_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/Kconfig

## Purpose
This Kconfig file defines the Renesas Ethernet driver menu and the build-time feature gates for SuperH Ethernet, Ethernet AVB, Renesas Ethernet Switch, R-Car Gen4 PTP, and Renesas Ethernet-TSN support. It controls which objects from the Renesas Ethernet directory can be built and which common networking subsystems are selected for each driver.

## Important APIs, Types, And Functions
- `config NET_VENDOR_RENESAS` gates the whole Renesas Ethernet submenu and defaults to enabled.
- `config SH_ETH` enables the SuperH Ethernet driver and selects `CRC32`, `MII`, `MDIO_BITBANG`, and `PHYLIB`.
- `config RAVB` enables the Renesas Ethernet AVB driver, depends on `PTP_1588_CLOCK_OPTIONAL`, and selects `PAGE_POOL`, `PHYLIB`, `RESET_CONTROLLER`, and MDIO/MII support.
- `config RENESAS_ETHER_SWITCH` enables the R-Switch driver, depends on required PTP clock support, selects `PHYLINK`, and selects `RENESAS_GEN4_PTP`.
- `config RENESAS_GEN4_PTP` builds the shared R-Car Gen4 gPTP provider, visible as a tristate prompt only under `COMPILE_TEST`.
- `config RTSN` enables the Ethernet-TSN driver and also selects `RENESAS_GEN4_PTP`.

## Control Flow
Kconfig evaluation first asks whether the Renesas vendor menu is visible. Inside the menu, each driver symbol becomes available when its architecture or `COMPILE_TEST` dependency is met. Selecting `RENESAS_ETHER_SWITCH` or `RTSN` automatically selects the shared Gen4 PTP module, while `RAVB` can compile with optional PTP support through `PTP_1588_CLOCK_OPTIONAL`.

## State And Persistence
The file persists only build configuration in the generated kernel `.config`. There is no runtime state. The selected symbols determine which object files are compiled, whether drivers are built-in or modules, and whether required network, PHY, PTP, reset, page-pool, and checksum dependencies are available to source files.

## Dependencies And Integration Points
This file integrates with `drivers/net/ethernet/renesas/Makefile`, which consumes the symbols to build `sh_eth.o`, `ravb.o`, `rswitch.o`, `rcar_gen4_ptp.o`, and `rtsn.o`. It depends on architecture symbols such as `ARCH_RENESAS` and `SUPERH`, generic `COMPILE_TEST`, and network infrastructure symbols such as `PTP_1588_CLOCK`, `PHYLIB`, `PHYLINK`, `MDIO_BITBANG`, `PAGE_POOL`, and `RESET_CONTROLLER`.

## Risks And Edge Cases
- `RENESAS_GEN4_PTP` is only user-visible for `COMPILE_TEST`, but it is selected by real drivers; dependency changes must keep selected builds valid.
- `RENESAS_ETHER_SWITCH` selects `PHYLINK`, while the visible header/source interactions also use classic PHY and switchdev APIs; missing dependency selects elsewhere would show up as build failures.
- `RAVB` depends on optional PTP support, so source paths must compile with PTP disabled or module-optional semantics respected.
- Overly broad `COMPILE_TEST` exposure can find missing include or dependency assumptions on non-Renesas architectures.

## Test Signals
Run `allmodconfig`/`allyesconfig` and targeted `ARCH_RENESAS` builds with `RAVB`, `RENESAS_ETHER_SWITCH`, `RENESAS_GEN4_PTP`, and `RTSN` as built-in and modules. Confirm the Makefile links the expected composite objects and that dependency-selected headers and symbols are available without manual user selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/Makefile

## Purpose
This Makefile maps Renesas Ethernet Kconfig symbols to kernel objects and declares the composite object membership for the AVB and R-Switch drivers.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_SH_ETH) += sh_eth.o` builds the SuperH Ethernet driver.
- `ravb-objs := ravb_main.o ravb_ptp.o` composes the `ravb.o` module/built-in object from the main AVB implementation and its PTP support file.
- `obj-$(CONFIG_RAVB) += ravb.o` links the composite AVB driver.
- `rswitch-objs := rswitch_main.o rswitch_l2.o` composes the R-Switch driver from its main implementation and switchdev L2 offload support.
- `obj-$(CONFIG_RENESAS_ETHER_SWITCH) += rswitch.o`, `obj-$(CONFIG_RENESAS_GEN4_PTP) += rcar_gen4_ptp.o`, and `obj-$(CONFIG_RTSN) += rtsn.o` map the remaining symbols to objects.

## Control Flow
Kbuild includes this file after Kconfig resolves symbols. For composite modules, Kbuild compiles each listed `*-objs` member and links them into the named object. `ravb_ptp.o` is always part of `ravb.o` when `CONFIG_RAVB` is enabled, while `rcar_gen4_ptp.o` is a separate shared object selected by R-Switch and RTSN.

## State And Persistence
The file has no runtime state. Its persistent effect is build graph structure: which translation units are linked together and which symbols are exported or local within each module/built-in object.

## Dependencies And Integration Points
It consumes symbols from `Kconfig` and integrates with the kernel top-level kbuild system. Source-level integrations include `ravb_main.c` calling functions from `ravb_ptp.c`, `rswitch_main.c` calling functions from `rswitch_l2.c`, and R-Switch/RTSN using exported symbols from `rcar_gen4_ptp.c`.

## Risks And Edge Cases
- Composite object membership means `ravb_ptp.c` must compile whenever `RAVB` compiles, even when PTP clock support is optional.
- `rswitch_l2.o` is always linked with `rswitch.o`; missing switchdev dependencies must be handled through Kconfig or includes.
- `rcar_gen4_ptp.o` is not automatically linked into `rswitch.o`; callers rely on Kconfig selecting a separate object/module and on exported GPL symbols.

## Test Signals
Build each symbol as `y` and `m`, inspect generated modules for `ravb`, `rswitch`, `rcar_gen4_ptp`, and `rtsn`, and confirm link errors do not occur for cross-file calls such as `ravb_ptp_init()`, `rswitch_register_notifiers()`, and `rcar_gen4_ptp_register()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb.h

## Purpose
This header defines the Renesas Ethernet AVB driver's register map, descriptor ABI, queue constants, PTP state, hardware-variant capability table, private netdev state, MMIO helpers, and cross-file prototypes shared by `ravb_main.c` and `ravb_ptp.c`.

## Important APIs, Types, And Functions
- Register ABI: `enum ravb_reg` names AVB-DMAC, E-MAC, gPTP, interrupt, MDIO, GbEth checksum, and counter registers.
- Bit definitions: enums such as `CCC_BIT`, `CSR_BIT`, `GCCR_BIT`, `ECMR_BIT`, `RIS*_BIT`, `TIS_BIT`, `ECSR_BIT`, `CSR0/1/2_BIT`, and many queue/interrupt masks encode hardware operations.
- Descriptor types: `struct ravb_desc`, `struct ravb_rx_desc`, `struct ravb_ex_rx_desc`, and `struct ravb_tx_desc` model base, normal Rx, timestamped Rx, and Tx descriptors.
- Queue and timestamp state: `enum RAVB_QUEUE`, `struct ravb_tstamp_skb`, `struct ravb_ptp_perout`, and `struct ravb_ptp` track BE/NC queues, pending Tx timestamp skbs, and PHC state.
- Variant table: `struct ravb_hw_info` carries function pointers and feature flags for receive path, rate setting, feature programming, DMAC/EMAC init, stats strings, descriptor sizes, maximum frame sizes, queue support, gPTP support, interrupt layout, WoL, internal delay, and GbEth checksum behavior.
- Main state: `struct ravb_private` stores platform/netdev pointers, clocks, MDIO bitbang control, descriptor base table, Tx/Rx rings, page pools, stats, timestamp controls, NAPI structs, work item, PHY state, feature flags, reset control, and computed GTI increment.
- Inline helpers and prototypes: `ravb_read()`, `ravb_write()`, `ravb_modify()`, `ravb_wait()`, `ravb_ptp_interrupt()`, `ravb_ptp_init()`, and `ravb_ptp_stop()`.

## Control Flow
The header itself is declarative, but it sets the contracts that drive AVB control flow. `ravb_main.c` selects a `ravb_hw_info` entry from the device-tree compatible string, then calls through its function pointers for variant-specific DMAC, EMAC, receive, rate, and feature operations. Descriptor definitions and `NUM_RX_QUEUE`/`NUM_TX_QUEUE` guide ring allocation, while PTP structures are initialized and consumed by `ravb_ptp.c`.

## State And Persistence
All state is runtime state. `ravb_private` persists for the lifetime of the registered netdev and carries hardware state mirrors such as ring indices, timestamp mode, speed/duplex/link, WoL enablement, delay-mode booleans, and computed `gti_tiv`. Hardware register writes persist only until reset or reconfiguration. No file-backed persistence is present.

## Dependencies And Integration Points
The header depends on Linux netdevice, interrupt, IO, MDIO bitbang, PHY, platform device, PTP clock, and page-pool types. It is the internal integration point between `ravb_main.c` and `ravb_ptp.c`, and between AVB netdev operations and Renesas hardware variants such as R-Car Gen2/Gen3/Gen4, RZ/V2M, and RZ/G2L GbEth.

## Risks And Edge Cases
- Register and bit definitions are hardware ABI; incorrect offsets or reserved-bit masks can break multiple SoC generations.
- `struct ravb_hw_info` flags must match descriptor format and interrupt layout; mixing GbEth normal descriptors with R-Car extended timestamp descriptors would corrupt DMA handling.
- Descriptor DMA addresses are stored in 32-bit descriptor fields, so DMA mask/platform assumptions must remain aligned with hardware capability.
- PTP and timestamp controls share `priv->lock` and descriptor state with data path code; changes must preserve locking and memory barriers.
- The `rx_1st_skb` field is global in `ravb_private`, so multi-fragment receive assumptions are sensitive to queue concurrency and currently used only by the GbEth receive path.

## Test Signals
Compile all compatible variants, verify `sizeof()` descriptor expectations, exercise BE-only and BE+NC queue paths, validate gPTP and non-gPTP builds, confirm register writes through `ravb_read()`/`ravb_write()`, test internal delay DT parsing on Gen3/Gen4, and run traffic with timestamp, checksum, ring-size, WoL, and PM operations enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb_main.c

## Purpose
This is the primary platform and netdev implementation for the Renesas Ethernet AVB/GbEth driver. It probes device-tree AVB-compatible devices, selects the correct hardware variant table, initializes clocks/reset/MMIO/MDIO/descriptors, manages BE and optional NC queues, drives Tx/Rx through DMA descriptors and NAPI, handles PHY link changes, PTP timestamp routing, ethtool operations, wake-on-LAN, runtime/system PM, and removal.

## Important APIs, Types, And Functions
- Platform/module surface: `ravb_match_table`, `ravb_driver`, `ravb_probe()`, `ravb_remove()`, `ravb_suspend()`, `ravb_resume()`, `ravb_runtime_suspend()`, and `ravb_runtime_resume()`.
- Netdev surface: `ravb_netdev_ops` wires open/stop, transmit, queue select, stats, rx mode, timeout, PHY ioctl, MTU, MAC validation, feature changes, and hwtstamp get/set.
- Hardware variant tables: `ravb_gen2_hw_info`, `ravb_gen3_hw_info`, `ravb_gen4_hw_info`, `ravb_rzv2m_hw_info`, and `gbeth_hw_info` select descriptor sizes, queue counts, checksum support, interrupt layout, gPTP mode, frame limits, WoL, and init callbacks.
- Ring/data path: `ravb_ring_init()`, `ravb_ring_format()`, `ravb_ring_free()`, `ravb_rx_ring_refill()`, `ravb_rx_rcar()`, `ravb_rx_gbeth()`, `ravb_tx_free()`, and `ravb_start_xmit()`.
- Hardware init/stop: `ravb_set_opmode()`, `ravb_set_config_mode()`, `ravb_dmac_init()`, `ravb_dmac_init_rcar()`, `ravb_dmac_init_gbeth()`, `ravb_emac_init_*()`, `ravb_stop_dma()`, `ravb_set_gti()`, and `ravb_compute_gti()`.
- Interrupt/NAPI: `ravb_interrupt()`, `ravb_multi_interrupt()`, `ravb_emac_interrupt()`, `ravb_be_interrupt()`, `ravb_nc_interrupt()`, `ravb_queue_interrupt()`, `ravb_timestamp_interrupt()`, `ravb_error_interrupt()`, and `ravb_poll()`.
- PHY/MDIO/ethtool: `ravb_mdio_init()`, `ravb_phy_init()`, `ravb_adjust_link()`, `ravb_get_ethtool_stats()`, `ravb_set_ringparam()`, `ravb_get_ts_info()`, and WoL helpers.

## Control Flow
Probe requires a device-tree node, obtains reset control and match data, allocates a multiqueue netdev sized for BE-only or BE+NC operation, deasserts reset, requests IRQs according to the selected interrupt topology, gets clocks, enables runtime PM, maps MMIO, parses PHY mode and link properties, computes maximum MTU and descriptor count, computes the gPTP increment when needed, parses internal-delay DT properties, allocates the descriptor base address table, switches hardware to config mode, reads or randomizes the MAC address, registers the MDIO bus, returns hardware to reset mode, adds NAPI contexts, optionally enables software IRQ coalescing for GbEth, registers the netdev, and marks wakeup capable.

Open enables NAPI, resumes runtime PM, enters config mode, applies internal delays, writes the descriptor base table DMA address, initializes DMAC rings, initializes EMAC registers, programs GTI, registers PTP when supported, connects and starts the PHY, and starts all Tx queues. Close stops Tx, masks interrupts, stops/disconnects PHY, unregisters PTP, stops DMA into config mode, drains pending Tx timestamp skbs, cancels timeout work, disables NAPI, frees BE/NC rings and page pools, updates stats, switches to reset mode, and drops runtime PM usage.

Receive processing is variant-specific. R-Car uses extended Rx descriptors with hardware timestamps and a two-queue model; GbEth uses normal descriptors and can assemble multi-descriptor packets into a page-backed skb. Both paths check descriptor ownership/type before reading fields, account MAC errors, sync DMA buffers for CPU, build or extend skbs from page-pool pages, apply checksum status if enabled, feed GRO, mark consumed page slots NULL, and refill descriptors with `DT_FEMPTY`. Transmit maps one or two descriptors per packet depending on alignment requirements, optionally sets a Tx timestamp tag for NC queue packets, uses DMA barriers before descriptor type changes and doorbell writes, advances `cur_tx`, frees completed descriptors, and stops a subqueue if the ring remains full.

Interrupt handling supports both shared summary IRQs and multi-IRQ devices. Summary handlers read `ISS`, dispatch timestamp FIFO processing, queue RX/TX scheduling, E-MAC link/magic-packet events, error accounting, and gPTP interrupts under `priv->lock`. Per-queue handlers schedule only their queue. NAPI clears RX/TX status, receives packets, retires Tx descriptors, wakes subqueues, mirrors overrun/fifo stats, and unmasks interrupts after completion.

## State And Persistence
Runtime state is held in `struct ravb_private`, DMA rings, page pools, descriptor base table, per-queue `net_device_stats`, pending timestamp skb list, PHY state, MDIO bus, clocks, reset control, and hardware registers. Persistent platform configuration comes from device tree properties such as compatible string, MAC address, PHY mode, `renesas,no-ether-link`, link polarity, internal delay properties, MDIO child node, and PHY handle. No runtime settings are stored to disk; ethtool ring size, timestamp mode, WoL flag, and feature flags are in-memory netdev state.

## Dependencies And Integration Points
The driver depends on Linux platform device, OF/MDIO/PHY, PM runtime, reset controller, clocks, DMA mapping, page pool, NAPI, ethtool, hwtstamp, PTP, netdev queueing, and `ravb_ptp.c`. Device-tree compatible entries map hardware generations to the `ravb_hw_info` table. It integrates with phylib for link negotiation, MDIO bitbang for bus access, ethtool for stats/ring/ts/WoL controls, PTP for timestamping, and kernel PM for autosuspend and system suspend/resume.

## Risks And Edge Cases
- `ravb_start_xmit()` calls `skb_checksum_help()` but does not check its return value before continuing, which is worth scrutiny if software checksum completion can fail.
- Descriptor programming relies on strict `dma_wmb()` ordering, especially two-descriptor aligned Tx; reordering can leave DMA seeing a start descriptor without an end descriptor.
- `ravb_stop_dma()` may fail; timeout and close paths intentionally avoid some reinitialization when hardware is still operating.
- `ravb_set_ringparam()` stops and frees rings on a running device; failure during reinit can leave the interface detached or partially stopped.
- PTP init/stop conditions vary between `gptp` and `ccc_gac`; timeout work checks only `info->gptp`, unlike open/close, so Gen3/Gen4 `ccc_gac` behavior deserves regression coverage.
- Runtime PM guards interrupt handlers and stats/feature operations; missed get/put ordering could produce MMIO while clocks are off.
- `ravb_remove()` returns early if runtime resume fails, which can leave device-managed teardown incomplete.

## Test Signals
Test probe on each compatible family, MDIO registration and PHY/fixed-link connection, BE-only GbEth and BE+NC R-Car traffic, Rx/Tx checksum toggles, hardware timestamp Tx on NC queue and Rx filters, PTP clock registration and interrupts, ethtool ring resize while running, MTU changes, WoL suspend/resume, runtime autosuspend clock gating, multi-IRQ and shared-IRQ paths, Tx timeout recovery, descriptor empty/fifo error accounting, and unload after active traffic with no DMA/page-pool leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb_ptp.c

## Purpose
This file implements the PTP Hardware Clock support for the Renesas Ethernet AVB driver. It registers the AVB gPTP clock, adjusts frequency and time, reads/writes the hardware timer, supports one external timestamp input, supports one periodic output, and services gPTP interrupt events for external timestamp and compare-match periodic output.

## Important APIs, Types, And Functions
- Clock operations: `ravb_ptp_info` provides `adjfine`, `adjtime`, `gettime64`, `settime64`, and `enable` callbacks to the PTP core.
- Timer register helpers: `ravb_ptp_tcr_request()`, `ravb_ptp_time_read()`, `ravb_ptp_time_write()`, and `ravb_ptp_update_compare()` serialize GCCR requests and access `GCT*`, `GTO*`, `GTI`, and `GPTC`.
- Feature controls: `ravb_ptp_extts()` toggles external timestamp interrupt masks, and `ravb_ptp_perout()` configures compare target/period and enables or disables compare interrupts.
- Driver integration: `ravb_ptp_interrupt()`, `ravb_ptp_init()`, and `ravb_ptp_stop()` are called by `ravb_main.c`.

## Control Flow
Initialization copies `ravb_ptp_info` into `priv->ptp.info`, records the default/current addend from `GTI`, waits for no outstanding timer request, selects adjusted gPTP time in `GCCR_TCSS`, and registers a PTP clock. Frequency adjustment computes a new addend with `adjust_by_scaled_ppm()`, updates `priv->ptp.current_addend`, writes `GTI`, and requests hardware load through `GCCR_LTI`. Time adjustment reads the current time under `priv->lock`, converts to nanoseconds, adds the delta, and writes the new time through the timer reset/load sequence.

External timestamp enablement accepts only index 0 and toggles either legacy `GIC_PTCE` or separate enable/disable registers (`GIE_PTCS`/`GID_PTCD`) depending on hardware. Periodic output accepts only index 0, validates that start and period fit in 32-bit nanosecond compare registers, writes the next compare value, stores target/period in `priv->ptp.perout[0]`, and enables compare interrupts. The interrupt handler reads enabled `GIS` bits, emits `PTP_CLOCK_EXTTS` events with `GCPT`, advances periodic targets by period on compare matches, rewrites `GPTC`, and clears handled status bits.

## State And Persistence
PTP state is stored inside `struct ravb_private` as `priv->ptp.clock`, copied `ptp_clock_info`, `default_addend`, `current_addend`, one `extts[]` enable flag, and one `perout[]` target/period. Hardware timer state resides in AVB gPTP registers and survives only until hardware reset or reinitialization. There is no disk persistence.

## Dependencies And Integration Points
The file depends on `ravb.h`, Linux PTP clock APIs, `timespec64`/ktime helpers, spin locking supplied by `priv->lock`, and `ravb_read()`/`ravb_write()`/`ravb_modify()`/`ravb_wait()` from `ravb_main.c`. It is linked into the composite `ravb.o` object and is initialized/stopped by open/close, ring resize, timeout recovery, suspend/WoL, and resume paths in `ravb_main.c`.

## Risks And Edge Cases
- All multi-register timer reads/writes require `priv->lock`; callers and interrupt paths must preserve that contract.
- `ravb_ptp_update_compare()` clamps compare values away from timer increment wrap hazards, but `perout->target += period` can still wrap naturally in 32 bits.
- `ravb_ptp_init()` does not check `ptp_clock_register()` for errors before later users call `ptp_clock_index()` in `ravb_main.c`; failures could propagate as invalid PHC state.
- `ravb_ptp_stop()` unconditionally unregisters `priv->ptp.clock`; repeated stop or failed init paths need matching lifecycle.
- Hardware paths differ for `irq_en_dis`, so Gen2-style mask writes and Gen3+ enable/disable registers need separate testing.

## Test Signals
Check `ethtool -T` PHC index, `phc2sys`/`testptp` get/set/adjfine/adjtime behavior, external timestamp event delivery, periodic output programming and repeated compare interrupts, interrupt-mask behavior on both old and `irq_en_dis` hardware, PTP lifecycle across open/close/ring resize/suspend/resume, and error handling when timer request bits remain busy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rcar_gen4_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rcar_gen4_ptp.c

## Purpose
This file implements the shared Renesas R-Car Gen4 gPTP Hardware Clock provider used by newer Renesas Ethernet drivers such as R-Switch and RTSN. It allocates a private PTP context around an MMIO timer block, registers a PTP clock, provides time/frequency adjustment operations, and exports helper functions for users to query the PHC index and read time.

## Important APIs, Types, And Functions
- State type: `struct rcar_gen4_ptp_private` stores the MMIO base, PTP clock pointer, clock info, spinlock, default addend, and initialization flag.
- PTP callbacks: `rcar_gen4_ptp_adjfine()`, `rcar_gen4_ptp_adjtime()`, `rcar_gen4_ptp_gettime()`, `rcar_gen4_ptp_settime()`, and `rcar_gen4_ptp_enable()`.
- Internal locked helpers: `_rcar_gen4_ptp_gettime()` and `_rcar_gen4_ptp_settime()` access the multi-register seconds/nanoseconds timer.
- Exported integration API: `rcar_gen4_ptp_alloc()`, `rcar_gen4_ptp_register()`, `rcar_gen4_ptp_unregister()`, `rcar_gen4_ptp_clock_index()`, and `rcar_gen4_ptp_gettime64()`.
- Register constants: `PTPTMEC_REG`, `PTPTMDC_REG`, `PTPTIVC0_REG`, `PTPTOVC*`, and `PTPGPTPTM*` define timer enable/disable, increment, offset, and current-time registers.

## Control Flow
A client calls `rcar_gen4_ptp_alloc()` with a platform device and MMIO address; this devm-allocates the private state, copies the static `ptp_clock_info`, and stores the base address. Registration is idempotent if `initialized` is already true. On first register, the driver initializes the spinlock, computes a timer increment addend from the supplied clock rate, writes `PTPTIVC0_REG`, registers the PTP clock, enables the timer, and marks the context initialized.

PTP operations use the private lock for multi-register time access. `adjfine()` scales the default addend by scaled-ppm to write a new increment. `adjtime()` reads current time, adds a nanosecond delta, and rewrites the offset registers. `settime()` disables/resets offset state, writes seconds high/low and nanoseconds offset registers, then enables loading. `enable()` returns `-EOPNOTSUPP`, so no external timestamp or periodic output support is exposed.

## State And Persistence
All state is runtime-only. `default_addend` records the nominal increment derived from the client-supplied rate, `initialized` gates helper behavior, and hardware registers store current timer/addend/offset values until reset or unregister. No nonvolatile persistence is used.

## Dependencies And Integration Points
The file depends on Linux platform device, PTP clock core, spinlocks, `timespec64` conversion helpers, MMIO accessors, and `rcar_gen4_ptp.h`. It exports GPL symbols for other Renesas Ethernet modules. `rswitch_main.c` allocates the PTP provider at its gPTP MMIO offset, registers it during hardware init, uses `rcar_gen4_ptp_clock_index()` for ethtool timestamp info, and can call `rcar_gen4_ptp_gettime64()` for timestamp conversion.

## Risks And Edge Cases
- `rcar_gen4_ptp_unregister()` does not clear `initialized` or `clock`, so callers must not unregister and then rely on idempotent re-register semantics without reinitialization review.
- `adjfine()` writes a signed 64-bit `addend` through `iowrite32()`, truncating to hardware width by design but requiring range assumptions.
- `rcar_gen4_ptp_gettime64()` silently returns without writing `ts` if not initialized, so callers need initialized checks or a known zeroed output.
- Time set writes several registers; lock coverage is required to avoid torn get/set operations.
- `ptp_clock_register()` uses a NULL parent device, unlike some drivers that pass `&pdev->dev`; sysfs/device lifetime expectations should be verified.

## Test Signals
Build with R-Switch and RTSN as modules and built-ins, verify exported symbol resolution, check PHC registration and `ethtool -T` PHC index, run `testptp` get/set/adjfine/adjtime, validate timer rate calculation for expected clock rates, exercise unregister during driver remove, and ensure no unsupported PTP request type is advertised beyond basic clock adjustment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rcar_gen4_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rcar_gen4_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rcar_gen4_ptp.h

## Purpose
This header declares the public internal API for the shared Renesas R-Car Gen4 gPTP provider. It lets Ethernet drivers allocate/register/unregister a PHC context and query or read the clock without exposing the provider's private structure layout.

## Important APIs, Types, And Functions
- Forward declaration: `struct rcar_gen4_ptp_private` keeps provider state opaque to clients.
- Lifecycle: `rcar_gen4_ptp_alloc()`, `rcar_gen4_ptp_register()`, and `rcar_gen4_ptp_unregister()`.
- Query helpers: `rcar_gen4_ptp_clock_index()` returns the PHC index or `-1` when uninitialized, and `rcar_gen4_ptp_gettime64()` reads current time into a `timespec64`.

## Control Flow
Clients include this header, allocate a provider with a platform device and MMIO timer address, register it with the timer rate once hardware is ready, expose `rcar_gen4_ptp_clock_index()` through ethtool timestamp info, optionally read time for timestamp conversion, and unregister during hardware teardown.

## State And Persistence
The header defines no storage and no persistence. It intentionally hides provider state behind an opaque pointer. Runtime state is owned by `rcar_gen4_ptp.c` and client drivers store only the returned pointer.

## Dependencies And Integration Points
The declarations depend on kernel types from including translation units: `struct platform_device`, `void __iomem`, `u32`, and `struct timespec64`. It is included by `rcar_gen4_ptp.c`, `rswitch.h`, and client drivers that use the shared Gen4 PTP block. Kconfig/Makefile ensure `rcar_gen4_ptp.o` is available for R-Switch and RTSN.

## Risks And Edge Cases
- Because the header does not include type headers itself, includers must already have the needed kernel type declarations.
- Opaque-state design prevents clients from validating `initialized` directly; they must use return values such as `clock_index == -1`.
- Register/unregister ordering is left to clients, so incorrect lifecycle handling can still call helpers after teardown.

## Test Signals
Compile all includers, verify no missing type declarations under `COMPILE_TEST`, confirm modules link to exported functions, and test client remove paths call unregister after successful register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rcar_gen4_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch.h

## Purpose
This header defines the Renesas Ethernet Switch driver's register map, descriptor formats, queue constants, per-port and global state structures, forwarding/L2 offload register bits, MMIO helpers, and cross-file prototypes shared by `rswitch_main.c` and `rswitch_l2.c`.

## Important APIs, Types, And Functions
- Global constants and iteration helpers: `RSWITCH_NUM_PORTS`, `RSWITCH_NUM_AGENTS`, `RSWITCH_MAX_NUM_QUEUES`, ring sizes, MTU/buffer sizing, `rswitch_for_all_ports()`, and enabled-port iteration macros.
- Register ABI: `enum rswitch_reg` covers forwarding engine, TOP, COMA, ETHA/RMAC, and GWCA register offsets.
- Register field macros: ETHA modes, GWCA modes, MDIO fields, interrupt register calculators, forwarding fields (`FWPC0/1/2`, `FWPBFC`, `FWMACAG*`), descriptor info fields, and timestamp descriptor extractors.
- Descriptor types: `struct rswitch_desc`, `struct rswitch_ts_desc`, `struct rswitch_ext_desc`, and `struct rswitch_ext_ts_desc`.
- Hardware state: `struct rswitch_etha`, `struct rswitch_gwca_queue`, `struct rswitch_gwca`, `struct rswitch_device`, `struct rswitch_mfwd`, and `struct rswitch_private`.
- Cross-file APIs: `is_rdev()` identifies R-Switch netdevs, and `rswitch_modify()` updates MMIO registers with clear/set masks.

## Control Flow
The header is declarative, but it shapes the R-Switch driver flow. `rswitch_main.c` allocates `rswitch_private`, initializes `rswitch_etha` ports and `rswitch_gwca` queues, registers one netdev per enabled port, uses descriptor types for Tx/Rx/timestamp rings, and exports `is_rdev()`/`rswitch_modify()` for `rswitch_l2.c`. `rswitch_l2.c` uses the port list, bridge/offload fields in `rswitch_device`, and forwarding register macros to turn bridge STP state into hardware learning and forwarding configuration.

## State And Persistence
All structures are runtime state. `rswitch_private` stores the platform device, MMIO base, shared Gen4 PTP provider, per-port pointers, opened-port bitmap, GWCA/ETHA state, forwarding table metadata, port list, interrupt lock, clock, halt/runtime-change flags, selected offload bridge, and hwtstamp settings. `rswitch_device` stores one netdev's queue pointers, NAPI, timestamp skb slots, port number, PHY/serdes state, bridge master, and L2 learning/forwarding requested/offloaded flags. Hardware register state persists only until reset/reconfiguration.

## Dependencies And Integration Points
The header depends on platform device, PHY, netdevice/NAPI types through includers, and `rcar_gen4_ptp.h`. It is the primary coupling point between main R-Switch data-path code, shared PTP support, and switchdev L2 offload code. Kbuild links `rswitch_main.o` and `rswitch_l2.o` into one `rswitch.o` object, so prototypes here define the internal boundary.

## Risks And Edge Cases
- The register enum is a large hardware ABI; typos or wrong offsets can program unrelated forwarding, interrupt, or MAC registers.
- Iteration macros depend on `priv->rdev[i]` being valid before checking `disabled`; initialization order must guarantee that.
- `struct rswitch_mfwd` refers to `struct rswitch_mac_table_entry *`, while this header defines `struct rswitch_mfwd_mac_table_entry`; that naming mismatch deserves build/context verification.
- Bridge offload fields are bitfields updated by notifier/open/stop paths without obvious locking in `rswitch_l2.c`; concurrency assumptions rely on netdevice/switchdev notifier serialization.
- Descriptor pointer fields split high and low DMA address bits, so DMA mask and descriptor packing must match hardware expectations.

## Test Signals
Compile R-Switch under `COMPILE_TEST`, validate register offsets against hardware documentation, bring up all enabled ports, exercise Tx/Rx and timestamp rings, verify PTP registration through `rcar_gen4_ptp`, test bridge join/leave and STP transitions, inspect L2 forwarding register writes, run suspend/resume/remove, and check that disabled-port iteration avoids null or uninitialized `rdev` access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_l2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_l2.c

## Purpose
This file implements switchdev and netdevice notifier support for R-Switch bridge offload. It tracks which R-Switch ports belong to a Linux bridge, decides whether a bridge has enough open R-Switch ports for hardware L2 offload, programs forwarding-engine registers for MAC learning and L2 forwarding, handles bridge STP state changes, applies bridge ageing time, and registers/unregisters notifier blocks for the module.

## Important APIs, Types, And Functions
- Offload eligibility: `rdev_for_l2_offload()` requires a selected `priv->offload_brdev`, matching `rdev->brdev`, and an opened port bit.
- Hardware programming: `rswitch_change_l2_hw_offloading()`, `rswitch_update_l2_hw_learning()`, `rswitch_update_l2_hw_forwarding()`, and exported `rswitch_update_l2_offload()`.
- Bridge tracking: `rswitch_update_offload_brdev()`, `rswitch_port_update_brdev()`, and `rswitch_netdevice_event()` handle `NETDEV_CHANGEUPPER` bridge link/unlink notifications.
- Switchdev attributes: `rswitch_port_update_stp_state()`, `rswitch_update_ageing_time()`, `rswitch_port_attr_set()`, `rswitch_switchdev_event()`, and `rswitch_switchdev_blocking_event()`.
- Notifier lifecycle: `rswitch_register_notifiers()` and `rswitch_unregister_notifiers()` register netdevice, switchdev atomic, and switchdev blocking notifier blocks.

## Control Flow
When a netdevice upper changes, the netdevice notifier filters for R-Switch netdevs using `is_rdev()` and for bridge masters using `netif_is_bridge_master()`. It updates the port's `brdev`, scans all R-Switch ports for the first bridge with at least two member ports, stores that bridge as `priv->offload_brdev`, and recalculates L2 offload. Open and stop in `rswitch_main.c` also call `rswitch_update_l2_offload()` when a port has a bridge master so offload follows port runtime state.

STP changes arrive through switchdev `SWITCHDEV_ATTR_ID_PORT_STP_STATE`. The driver marks learning requested for LEARNING or FORWARDING states, forwarding requested only for FORWARDING, and updates hardware. Learning offload toggles `FWPC0_MACSSA`, `FWPC0_MACHLA`, and `FWPC0_MACHMA`; forwarding offload toggles `FWPC0_MACDSA`. Forwarding also computes a destination mask where participating hardware-forwarded ports are cleared, writes `FWPC2(port)` with a mask that prevents self-forwarding, and starts/stops hardware forwarding per port. Bridge ageing time writes `FWMACAGC` after validating the value fits the hardware field.

## State And Persistence
State is runtime-only in `struct rswitch_device` and `struct rswitch_private`: each port tracks `brdev`, `learning_requested`, `learning_offloaded`, `forwarding_requested`, and `forwarding_offloaded`; the private structure tracks the currently selected `offload_brdev` and opened-port bitmap. Hardware forwarding state persists in MFWD registers until changed or reset. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux netdevice notifier APIs, bridge helpers, switchdev notifier APIs, FIELD_PREP/FIELD_FIT bitfield helpers, `rswitch.h` register/state definitions, and `rswitch_l2.h` prototypes. It integrates with `rswitch_main.c` through `is_rdev()`, `rswitch_modify()`, port list state, open/stop notifications, module probe notifier registration, and remove notifier unregistration.

## Risks And Edge Cases
- Only one bridge is selected for offload (`priv->offload_brdev`), chosen as the first bridge found with two R-Switch ports; additional bridges or later ordering changes are not offloaded.
- The debug message in `rswitch_update_offload_brdev()` appears inverted: it logs "changing" when the new bridge equals the old bridge, and "starting" otherwise.
- Notifier callbacks update shared port/offload state without an explicit private lock; this relies on notifier and RTNL/switchdev serialization.
- Ageing time is a `clock_t` written directly into the hardware field, so unit conversion expectations must match switchdev's ageing-time units and the hardware's configured ageing clock.
- Unsupported switchdev port object add/delete operations return `-EOPNOTSUPP`; bridge features beyond STP state and ageing time are not offloaded.

## Test Signals
Create Linux bridges with two or more R-Switch ports, join and leave ports, open/close bridge member interfaces, change STP states through bridge operation, verify `FWPC0` learning/forwarding bits and `FWPC2` destination masks, set bridge ageing time and validate field limits, test unsupported FDB/VLAN/MDB operations fail gracefully, and remove the driver while notifiers are registered without callbacks touching freed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_l2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_l2.h

## Purpose
This header declares the R-Switch L2 offload interface used by the main R-Switch driver. It exposes bridge offload recalculation and notifier lifecycle functions while hiding switchdev implementation details in `rswitch_l2.c`.

## Important APIs, Types, And Functions
- `rswitch_update_l2_offload(struct rswitch_private *priv)` recalculates and applies hardware learning/forwarding state for all ports.
- `rswitch_register_notifiers()` registers netdevice and switchdev notifier blocks.
- `rswitch_unregister_notifiers()` unregisters those notifier blocks.

## Control Flow
`rswitch_main.c` includes this header, registers notifiers during probe after hardware/ports initialize, calls `rswitch_update_l2_offload()` from port open/stop when a bridge master is present, and unregisters notifiers during remove before deinitializing driver state.

## State And Persistence
The header defines no storage. It operates on `struct rswitch_private` state declared in `rswitch.h` and maintained by `rswitch_main.c`/`rswitch_l2.c`. There is no persistent state.

## Dependencies And Integration Points
It depends on `struct rswitch_private` being declared before use by including `rswitch.h` in source files. It forms the internal build boundary between `rswitch_main.o` and `rswitch_l2.o`, both linked into `rswitch.o`.

## Risks And Edge Cases
- The header itself does not forward-declare `struct rswitch_private`; include order must provide it.
- Notifier registration is global, so probe/remove ordering must avoid double registration or unregistering while callbacks can still reference freed driver state.
- Main driver callers must call `rswitch_update_l2_offload()` when port open state changes, otherwise hardware offload can remain stale.

## Test Signals
Compile `rswitch_main.c` and `rswitch_l2.c` together, verify probe registers notifiers exactly once, remove unregisters them before state teardown, and bridge membership/open/stop events cause visible forwarding-engine register updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_l2.h -->

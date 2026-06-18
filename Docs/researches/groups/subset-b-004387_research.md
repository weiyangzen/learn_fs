# Research: subset-b-004387

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/Kconfig

## Purpose
This Kconfig file exposes the Cadence Ethernet driver family to the Linux networking configuration menu. It defines the vendor gate `NET_VENDOR_CADENCE`, the main Cadence MACB/GEM platform driver option `MACB`, optional GEM IEEE 1588 hardware timestamping through `MACB_USE_HWSTAMP`, and the `MACB_PCI` wrapper that instantiates the platform driver from a Cadence PCI function.

## Important symbols and dependencies
- `NET_VENDOR_CADENCE` is a boolean vendor menu guarded by `HAS_IOMEM` and defaults to enabled so Cadence devices remain discoverable in normal network driver configuration.
- `MACB` is tristate, depends on `HAS_DMA`, `COMMON_CLK`, and `PTP_1588_CLOCK_OPTIONAL`, and selects `PHYLINK` and `CRC32`. Those selections match the implementation in `macb_main.c`, which uses DMA rings, common clock APIs, phylink link management, and CRC32 for software FCS generation.
- `MACB_USE_HWSTAMP` is a boolean dependent on `MACB` and `PTP_1588_CLOCK`; when enabled it causes `macb_ptp.o` to be linked into the `macb` module.
- `MACB_PCI` is a tristate dependent on both `MACB` and `PCI`; it builds the PCI wrapper module `macb_pci`.

## Control flow and integration
This file does not execute runtime control flow, but it controls object inclusion. `MACB` enables the platform module built from `macb_main.o`; `MACB_USE_HWSTAMP` conditionally adds PTP support and activates the `CONFIG_MACB_USE_HWSTAMP` declarations in `macb.h`; `MACB_PCI` builds a separate PCI driver that registers a synthetic platform device named `macb`.

## State, persistence, and risks
The configuration state is compile-time only. A mismatch between enabled Kconfig options and hardware expectations mainly appears as missing timestamp support, missing PCI wrapper support, or unavailable phylink/clock dependencies. Because timestamping is a bool rather than tristate, a `macb` module built with hardware timestamping always includes the PTP code path.

## Test signals
Build coverage should include `MACB=y`, `MACB=m`, `MACB_USE_HWSTAMP=y`, and `MACB_PCI=m/y` combinations. Runtime signals are whether the `macb` module exports normal netdevs, whether `ethtool -T` reports PHC support only when `MACB_USE_HWSTAMP` and hardware capabilities allow it, and whether `macb_pci` can load only when PCI support is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/Makefile

## Purpose
This Makefile maps the Cadence Kconfig choices to kernel objects. It builds the main `macb` object from `macb_main.o`, conditionally links `macb_ptp.o` into that same object when hardware timestamping is enabled, and builds `macb_pci.o` as the PCI wrapper module.

## Important build rules
- `macb-y := macb_main.o` makes `macb_main.c` the always-present implementation of `CONFIG_MACB`.
- `ifeq ($(CONFIG_MACB_USE_HWSTAMP),y) macb-y += macb_ptp.o endif` keeps PTP code in the main driver only when the bool is enabled.
- `obj-$(CONFIG_MACB) += macb.o` emits the platform driver as built-in or module according to the tristate.
- `obj-$(CONFIG_MACB_PCI) += macb_pci.o` emits the PCI wrapper separately.

## Control flow and integration
There is no runtime logic. The key integration point is object composition: `macb_ptp.c` relies on symbols and structures from `macb.h`/`macb_main.c`, and it is compiled into `macb.o` rather than a standalone module. The PCI wrapper remains separate and depends on the platform driver name `macb`.

## State, persistence, risks, and test signals
State is build-system state only. The main risk is build/link drift if PTP declarations in `macb.h` stop matching the conditional inclusion of `macb_ptp.o`. Useful tests are kernel build matrix checks around `CONFIG_MACB_USE_HWSTAMP`, module load checks for `macb.ko` and `macb_pci.ko`, and symbol/link verification that PTP functions are present only in hardware timestamp builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb.h

## Purpose
`macb.h` is the shared hardware and driver contract for the Cadence MACB/GEM Ethernet implementation. It defines register offsets, bitfield helpers, descriptor layouts, capability flags, statistics descriptors, driver state structures, PTP interfaces, queue metadata, platform data, and ENST/TAPRIO timing helpers used by `macb_main.c`, `macb_ptp.c`, and `macb_pci.c`.

## Important APIs, types, and constants
- Register definitions cover legacy MACB registers, GEM registers, per-queue register windows, PTP timer registers, PCS/USXGMII registers, screener/filter registers, and ENST scheduled-traffic registers.
- `MACB_BIT`, `MACB_BF`, `MACB_BFEXT`, `MACB_BFINS` and GEM equivalents centralize bitfield generation/extraction.
- `macb_readl`, `macb_writel`, `gem_readl`, `gem_writel`, `queue_readl`, and `queue_writel` dispatch through the `struct macb` MMIO accessor callbacks, allowing native raw or relaxed I/O depending on detected endianness.
- `struct macb_dma_desc`, `struct macb_dma_desc_64`, and `struct macb_dma_desc_ptp` describe the variable descriptor formats used for 32-bit DMA, 64-bit DMA, and hardware timestamp extension words.
- `struct macb_tx_skb` tracks the skb, DMA mapping, size, and page/single mapping mode for each TX descriptor slot.
- `struct macb_stats`, `struct gem_stats`, `struct gem_statistic`, and `queue_statistics` define hardware and per-queue statistic accumulation and ethtool string mapping.
- `struct macb_or_gem_ops` abstracts MACB versus GEM RX allocation, free, ring initialization, and RX polling behavior.
- `struct macb_ptp_info` provides the optional PTP hook table used by `macb_main.c` without hard-coding `macb_ptp.c`.
- `struct macb_queue` stores per-queue IRQ number, register offsets, TX/RX descriptor rings, DMA addresses, NAPI structures, work item, counters, and ENST register offsets.
- `struct macb` is the central device state: MMIO base, accessors, clocks, queues, netdev, phylink/PCS objects, capabilities, DMA/ring sizing, stats, Wake-on-LAN state, PTP clock state, RX flow-filter list, work items, EEE state, prefetch fields, interrupt masks, saved PM state, and USRIO config.
- `struct macb_config` and `struct macb_usrio_config` are platform match-data contracts for capabilities, clock/init callbacks, DMA burst size, MTU limits, and USRIO bit encodings.
- `struct macb_platform_data` carries fixed `pclk`/`hclk` pointers for the PCI wrapper-created platform device.
- `struct macb_queue_enst_config`, `enst_ns_to_hw_units()`, and `enst_max_hw_interval()` support Enhanced Scheduled Traffic configuration in the TAPRIO offload path.

## Control flow and integration
The header is heavily integrated with the main driver. `macb_main.c` uses register constants and bitfield macros for probe, phylink configuration, DMA setup, interrupts, TX/RX rings, ethtool, flow filters, TAPRIO, and PM. `macb_ptp.c` uses the descriptor and TSU register definitions to expose PHC operations and timestamp skb completion. `macb_pci.c` uses `struct macb_platform_data` to pass clocks into the platform probe. Conditional `CONFIG_MACB_USE_HWSTAMP` blocks export real PTP functions when built and inline no-ops when omitted.

## State and persistence behavior
The header declares volatile runtime state rather than persistence. Durable state lives in hardware registers while the device is powered and in `struct macb` while the netdev exists. `struct macb_pm_data` captures small register state (`scrt2`, `usrio`) across suspend/resume. Descriptor ownership bits (`RX_USED`, `TX_USED`, wrap bits, PTP valid bits) form the critical hardware/software synchronization state.

## Dependencies and risks
The header depends on Linux networking, DMA, phylink, PTP, ethtool, clk, platform, PHY, and list/spinlock infrastructure through included translation units. Risks are concentrated in bitfield correctness, descriptor-size calculations, capability flags matching actual hardware, and conditional PTP declarations staying consistent with the Makefile. Because per-queue register offsets are stored in `struct macb_queue`, bad queue probing or wrong queue-hole handling can corrupt unrelated hardware registers.

## Test signals
Compile-time tests should exercise builds with and without `CONFIG_MACB_USE_HWSTAMP`, 64-bit DMA, multiple queues, and platforms with different `macb_config` capabilities. Runtime signals include correct ethtool stats naming, stable TX/RX under ring wrap, valid PHC behavior only with DMA PTP capability, correct TAPRIO register programming units, and no sparse/build warnings around `__nonstring`, DMA address casting, or bitfield width changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_main.c

## Purpose
`macb_main.c` is the primary Cadence MACB/GEM Ethernet platform driver. It supports legacy MACB, GEM gigabit controllers, old AT91 EMAC compatibility mode, multiple queues, DMA descriptor rings, NAPI RX/TX completion, phylink/PCS link management, ethtool operations, Wake-on-LAN, RX flow filters, checksum/segmentation offloads, optional PTP integration, TAPRIO/ENST traffic-control offload, platform-specific initialization, runtime PM, system suspend/resume, and OF/platform driver registration.

## Important APIs, functions, and structures
- DMA and ring helpers: `macb_dma_desc_get_size()`, `macb_adj_dma_desc_idx()`, `macb_tx_desc()`, `macb_rx_desc()`, `macb_tx_skb()`, `macb_set_addr()`, `macb_get_addr()`, and ring wrap helpers encode descriptor layout differences for 64-bit DMA and PTP descriptors.
- MMIO and detection: `hw_readl_native()`, `hw_writel_native()`, `hw_readl()`, `hw_writel()`, `hw_is_native_io()`, and `hw_is_gem()` choose accessors and identify GEM hardware.
- MDIO/phylink: `macb_mdio_read_c22()`, `macb_mdio_write_c22()`, Clause 45 variants, `macb_mii_init()`, `macb_mii_probe()`, `macb_phylink_connect()`, `macb_mac_config()`, `macb_mac_link_up()`, `macb_mac_link_down()`, and PCS ops integrate the MAC with PHY or fixed-link configurations.
- Data path: `macb_start_xmit()`, `macb_tx_map()`, `macb_tx_complete()`, `macb_rx_poll()`, `gem_rx()`, `gem_rx_refill()`, `macb_rx()`, `macb_rx_frame()`, `macb_interrupt()`, and `macb_interrupt_misc()` implement TX submission, RX delivery, NAPI polling, and error handling.
- Resource lifecycle: `macb_open()`, `macb_close()`, `macb_alloc_consistent()`, `macb_free_consistent()`, `gem_alloc_rx_buffers()`, `macb_alloc_rx_buffers()`, `gem_init_rings()`, `macb_init_rings()`, `macb_init_hw()`, and `macb_reset_hw()` own runtime hardware resources.
- Ettool and netdev ops: `macb_get_stats()`, `gem_update_stats()`, string/stat callbacks, ring parameter callbacks, WoL callbacks, link settings callbacks, timestamp callbacks, feature toggles, and `macb_netdev_ops` expose the netdev contract.
- PTP hooks: when `CONFIG_MACB_USE_HWSTAMP` is enabled, `gem_ptp_info` connects `macb_main.c` to `macb_ptp.c`; TX/RX completion calls `gem_ptp_do_txstamp()` and `gem_ptp_do_rxstamp()`.
- RX flow filters: `gem_prog_cmp_regs()`, `gem_add_flow_filter()`, `gem_del_flow_filter()`, `gem_get_rxnfc()`, and `gem_set_rxnfc()` program GEM screener type 2 compare registers for IPv4 TCP/UDP n-tuple steering.
- Traffic control: `macb_setup_tc()`, `macb_setup_taprio()`, `macb_taprio_setup_replace()`, and `macb_taprio_destroy()` offload TAPRIO schedules to GEM ENST queue timing registers.
- Platform glue: `macb_configure_caps()`, `macb_probe_queues()`, clock init functions, platform-specific `macb_config` tables, `macb_dt_ids`, `macb_probe()`, `macb_remove()`, `macb_suspend()`, `macb_resume()`, runtime PM callbacks, and `module_platform_driver()`.

## Control flow
Probe maps MMIO, selects OF match data or default GEM config, initializes clocks, enables runtime PM, detects native I/O, probes queue count, allocates an MQ netdev, initializes `struct macb`, detects caps, configures DMA masks and MTU limits, resolves MAC address and PHY interface, runs platform-specific init, creates MDIO/phylink, registers the netdev, initializes deferred work, and drops the runtime PM reference.

Open resumes the device, sizes RX buffers from MTU, allocates descriptor rings and RX buffers, initializes rings and hardware registers, powers the PHY, connects and starts phylink, starts TX queues, and registers PTP if available. Close stops TX, disables NAPI, cancels LPI work, stops phylink, powers off the PHY, resets hardware, frees coherent DMA memory, removes PTP, and releases runtime PM.

TX submission validates checksum/FCS behavior, marks hardware timestamp requests, calculates needed descriptors, maps skb head/frags to DMA, fills descriptors in reverse order to avoid hardware races, wakes EEE LPI if necessary, and writes `TSTART`. TX NAPI reclaims descriptors after hardware sets `TX_USED`, timestamps skb completions when needed, updates stats, unmaps DMA, wakes stopped subqueues, and reschedules around missed completion interrupts.

GEM RX uses one skb per RX descriptor. `gem_rx_refill()` allocates/maps skbs and clears `RX_USED`; `gem_rx()` consumes descriptors with both SOF and EOF, unmaps DMA, applies checksum state, attaches hardware RX timestamps, updates stats, and passes packets to GRO. Legacy MACB RX uses coherent RX buffers and copies frame fragments into a new skb via `macb_rx_frame()`.

Interrupt handling reads per-queue ISR, disables RX/TX completion interrupts before scheduling NAPI, handles TX used-buffer restart, queues error work for TX and HRESP failures, records RX overruns, and handles MACB/GEM WoL interrupts. Error work halts/reinitializes TX or the whole DMA engine as appropriate.

Suspend detaches the netdev, optionally configures MAC WoL, disables NAPI, stops phylink or leaves wake receive enabled, saves USRIO and screener state, removes PTP, and forces runtime suspend when wake is not needed. Resume reverses this: restores clocks, disables WoL, rebuilds RX rings, restores USRIO/screener/features, restarts phylink, reattaches the netdev, and reinitializes PTP.

## State and persistence behavior
The central persistent-in-memory state is `struct macb` stored as netdev private data. Hardware state lives in MMIO registers, DMA rings, descriptor ownership bits, IRQ masks, phylink state, and clock rates. There is no filesystem persistence. Across suspend/resume, only selected register state is saved in `bp->pm_data`; other hardware state is reconstructed from `struct macb`, netdev feature flags, RX flow-filter lists, and phylink. Descriptor rings and RX buffers are allocated on open and freed on close, while the netdev and phylink objects live from probe to remove.

## Dependencies and integration points
The driver depends on Linux netdev, NAPI, DMA mapping, phylink, MDIO, ethtool, PTP, runtime PM, common clock, OF, PHY, reset, Xilinx firmware calls for some SGMII modes, and platform device infrastructure. It is integrated with `macb.h` for hardware definitions, `macb_ptp.c` through `struct macb_ptp_info`, and `macb_pci.c` through platform data clocks. Device tree match data drives capabilities for Atmel/Microchip, Xilinx, SiFive, Mobileye, Raspberry Pi RP1, and other Cadence integrations.

## Risks and edge cases
High-risk areas include DMA descriptor ordering and memory barriers, TX error recovery, missed interrupt rescheduling, runtime PM during MDIO accesses, 64-bit DMA descriptor high-address constraints, queue mask holes, PTP descriptor layout, EEE LPI wake timing, RX partial store-and-forward watermarks, feature restore after resume, and TAPRIO time conversion/validation. The old AT91 EMAC path has a separate non-NAPI transmit/interrupt model and must not regress while changing common helpers. Flow filters rely on exact GEM screener register availability and only support unmasked IPv4 TCP/UDP fields in specific combinations.

## Test signals
Useful signals include successful kernel builds across `CONFIG_MACB_USE_HWSTAMP`, `CONFIG_ARCH_DMA_ADDR_T_64BIT`, OF and COMPILE_TEST matrices; probe/remove on representative compatibles; `ip link set up/down`; sustained TX/RX with small packets, jumbo frames, fragmented skbs, SG, TSO/UFO, checksum on/off, promisc/allmulti; multi-queue IRQ and NAPI behavior; `ethtool -S`, ring parameter changes, RX n-tuple add/delete/list, `ethtool -T`, hardware timestamp send/receive, WoL magic/ARP suspend wake, runtime PM MDIO access, TAPRIO replace/destroy, and suspend/resume with netdev running and stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_pci.c

## Purpose
`macb_pci.c` is a thin PCI wrapper for the Cadence MACB/GEM platform driver. It binds Cadence PCI device ID `0xe007`, enables the PCI function, constructs platform resources and fixed clocks, and registers a child platform device named `macb` so the main platform driver in `macb_main.c` can handle the hardware.

## Important APIs and functions
- `macb_probe(struct pci_dev *pdev, const struct pci_device_id *id)` enables the PCI device with managed PCI helpers, sets bus mastering, translates BAR0 and IRQ vector 0 into platform resources, creates fixed-rate `pclk` and `hclk` clocks at 50 MHz, fills `struct macb_platform_data`, and calls `platform_device_register_full()`.
- `macb_remove(struct pci_dev *pdev)` unregisters the child platform device and unregisters the fixed clocks.
- `dev_id_table` matches `PCI_VDEVICE(CDNS, PCI_DEVICE_ID_CDNS_MACB)`.
- `macb_pci_driver` registers through `module_pci_driver()`.

## Control flow
On PCI probe, BAR and IRQ resources are copied into a temporary `resource[2]`, platform data carries clock handles, and `platform_device_info` points at the PCI device as parent and forwards the PCI fwnode. Once the platform device is registered, normal `macb_probe()` takes over. On remove, the platform device is removed first so the main driver releases resources before the fixed clocks are unregistered.

## State, persistence, and dependencies
Runtime state is the child `platform_device` stored with `pci_set_drvdata()`, plus two fixed-rate clocks stored in the copied platform data. There is no persistent storage. The file depends on PCI, platform-device registration, common clock fixed-rate providers, and `macb.h` for `struct macb_platform_data`.

## Risks and test signals
The wrapper assumes BAR0 and IRQ vector 0 are valid and that 50 MHz fixed pclk/hclk values are correct for the PCI integration. It uses stack-allocated platform data/resources only through `platform_device_register_full()`, which copies the data; changing to a non-copying path would be unsafe. Test signals include `macb_pci` module load/unload, child `macb` platform probe success, correct BAR/IRQ display, no clock leaks on probe failure paths, and successful network traffic through the PCI-instantiated device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_ptp.c

## Purpose
`macb_ptp.c` implements IEEE 1588 Precision Time Protocol hardware timestamp support for Cadence GEM devices with DMA PTP descriptor extensions. It registers a PHC, initializes the GEM timestamp unit, adjusts and reads TSU time, converts descriptor timestamp words into skb hardware timestamps, and handles ethtool hardware timestamp configuration.

## Important APIs and functions
- `macb_ptp_desc()` locates PTP timestamp extension words after the base descriptor and optional 64-bit address descriptor.
- `gem_tsu_get_time()` reads nanoseconds and split seconds registers with rollover handling and optional system timestamp sampling.
- `gem_tsu_set_time()` writes TSU time, clearing nanoseconds before writing high/low seconds to avoid overflow/atomicity issues.
- `gem_tsu_incr_set()` writes sub-nanosecond and nanosecond increment registers in the required order.
- `gem_ptp_adjfine()` adjusts the TSU increment from scaled ppm using the base increment stored in `bp->tsu_incr`.
- `gem_ptp_adjtime()` uses hardware time adjust for small deltas and full read/add/set for larger deltas.
- `gem_ptp_init()` fills `ptp_clock_info`, derives TSU rate and max adjustment from `struct macb_ptp_info`, registers the PHC, initializes locking and TSU time.
- `gem_ptp_remove()` unregisters the PHC and clears TSU increment/adjust registers.
- `gem_ptp_rxstamp()` and `gem_ptp_txstamp()` attach RX/TX hardware timestamps to skbs when descriptor valid bits are set.
- `gem_get_hwtst()` and `gem_set_hwtst()` implement netdev hardware timestamp get/set for ethtool/netlink.

## Control flow
The main driver calls `gem_ptp_init()` during `macb_open()` when GEM caps and Kconfig allow PTP, and `gem_ptp_remove()` during close/suspend. TX completion calls `gem_ptp_txstamp()` for timestamp-requested skbs except one-step sync frames. RX delivery calls `gem_ptp_rxstamp()` before GRO. Userspace timestamp configuration reaches `gem_set_hwtst()` through netdev hwtstamp ops in `macb_main.c`.

## State and persistence behavior
PTP state lives in `struct macb`: `ptp_clock`, `ptp_clock_info`, `tsu_rate`, `tsu_incr`, `tsu_clk_lock`, and `tstamp_config`. Hardware state lives in TSU registers (`TSH`, `TSL`, `TN`, `TISUBN`, `TI`, `TA`), descriptor timestamp extension words, `TXBDCTRL`, `RXBDCTRL`, and NCR bits such as `OSSMODE` and `SRTSM`. There is no disk persistence; suspend/remove clears and later reinitializes TSU state.

## Dependencies and integration points
The file depends on the PTP clock subsystem, skb timestamp APIs, `ptp_classify` support, kernel time helpers, spinlocks, and descriptor/register definitions from `macb.h`. It is linked only when `CONFIG_MACB_USE_HWSTAMP=y` and is invoked through `struct macb_ptp_info` set by `macb_main.c` when hardware design config reports TSU support.

## Risks and test signals
Risks include TSU read/write races, descriptor layout mismatch when 64-bit DMA and PTP are combined, seconds rollover reconstruction from truncated descriptor seconds, unsupported timestamp filters returning the right errors, one-step sync mode leaving `OSSMODE` in the intended state, and PHC registration failures falling back cleanly. Test signals include `ethtool -T`, `hwstamp_ctl`/netlink hwtstamp configuration, PHC index presence, `ptp4l` operation, RX/TX timestamp delivery, adjfine/adjtime behavior, suspend/resume PTP reinitialization, and warning-free operation when descriptor valid bits are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/Kconfig

## Purpose
This Kconfig file exposes the Calxeda Highbank XGMAC Ethernet driver. It defines `NET_CALXEDA_XGMAC`, a tristate option for the 1G/10G XGMAC IP block used on Calxeda Highbank platforms.

## Important symbols and dependencies
- `NET_CALXEDA_XGMAC` depends on `HAS_IOMEM`, because the driver accesses memory-mapped hardware registers.
- It depends on `ARCH_HIGHBANK || COMPILE_TEST`, limiting normal selection to Highbank while still allowing broader build coverage.
- It selects `CRC32`, indicating the implementation requires CRC helpers, likely for Ethernet filtering or frame operations.

## Control flow, state, and integration
There is no runtime control flow in this file. It controls whether `xgmac.o` from the same directory is built by the Makefile. The option integrates into the Ethernet vendor tree as a standalone Calxeda driver, separate from the Cadence MACB/GEM implementation.

## Risks and test signals
The main risk is build coverage erosion for older Highbank-specific hardware. Test signals are successful builds with `ARCH_HIGHBANK`, successful `COMPILE_TEST` builds on other architectures with `HAS_IOMEM`, and correct inclusion/exclusion of `xgmac.o` through the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/Makefile

## Purpose
This Makefile maps `CONFIG_NET_CALXEDA_XGMAC` to the Calxeda XGMAC object file.

## Important build rule
- `obj-$(CONFIG_NET_CALXEDA_XGMAC) += xgmac.o` builds the XGMAC driver as built-in, module, or not at all according to the Kconfig tristate.

## Control flow, state, dependencies, and integration
There is no runtime control flow or persisted state. The file integrates with the kernel kbuild object model and relies on `Kconfig` to define when `CONFIG_NET_CALXEDA_XGMAC` is available.

## Risks and test signals
The risk surface is small: the object name must continue to match the implementation file and Kconfig symbol. Test signals are compile checks for `NET_CALXEDA_XGMAC=y` and `NET_CALXEDA_XGMAC=m`, plus module packaging that emits the expected XGMAC module when configured as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/Makefile -->

# subset-b-004652 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pci.c

## Purpose
This file is the PCI bus binding for the STMMAC Ethernet core. It turns a matched PCI device into generic `stmmac_dvr_probe()` input by allocating `plat_stmmacenet_data`, mapping a BAR, filling default MAC/DMA/MDIO settings, and wiring PCI PM callbacks through `stmmac_simple_pm_ops`.

## Important APIs, Types, and Functions
`struct stmmac_pci_info` is a small per-ID descriptor whose `setup()` callback initializes platform data. `common_default_data()` provides legacy GMAC defaults: CSR clock range, GMAC core type, store-and-forward DMA, and MDIO reset. `stmmac_default_data()` sets bus/PHY defaults for the synthetic/STMicro IDs. `snps_gmac5_default_data()` configures GMAC5/GMAC4-style capabilities: TSO, PMT, four RX/TX queues, WRR TX scheduling, SP RX scheduling, TBS on nonzero TX queues, GMII, PBL settings, and AXI outstanding/burst limits. `stmmac_pci_probe()` is the main probe path; `stmmac_pci_remove()` delegates to the common remove path. The PCI ID table covers synthetic STMMAC, STMicro MAC, and Synopsys GMAC5 IDs.

## Control Flow
Probe allocates platform data, MDIO bus data, and safety feature config; enables the PCI device with devres-managed `pcim_enable_device()`; scans BARs until it maps the first nonempty BAR through `pcim_iomap_region()`; enables bus mastering; runs the ID-specific setup; copies `pdev->irq` into both normal and WoL IRQs; enables safety feature bits; installs PCI suspend/resume callbacks into platform data; then calls `stmmac_dvr_probe()`. Removal is intentionally thin and calls `stmmac_dvr_remove()`.

## State and Persistence
The file owns no persistent state beyond devres allocations attached to the PCI device and platform data passed to the common driver. Queue configuration, AXI settings, safety flags, MDIO reset needs, and PM callback pointers persist in `plat_stmmacenet_data` for the lifetime of the probed netdev.

## Dependencies and Integration Points
It depends on PCI core APIs, `stmmac_plat_dat_alloc()`, common STMMAC probe/remove, PCI-specific platform PM helpers from `stmmac_libpci.h`, and register/feature constants from the STMMAC core. It integrates with module autoloading through `MODULE_DEVICE_TABLE(pci, ...)`.

## Risks and Test Signals
BAR selection maps the first nonempty BAR, so devices with multiple BARs require correct resource ordering. The default PHY interface is GMII and may be too rigid for boards needing custom PHY data. Safety features are enabled unconditionally after setup, so new PCI IDs must confirm compatible error interrupt behavior. Test signals are PCI probe/remove, suspend/resume, MDIO discovery, multi-queue bring-up on GMAC5, TSO/TBS operation, and successful common STMMAC selftests after PCI probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pcs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pcs.c

## Purpose
This file implements the integrated PCS adapter used by GMAC/DWMAC cores to expose SGMII and BASE-X link state to phylink. It translates MAC PCS registers into `phylink_pcs_ops`, handles PCS link/auto-negotiation interrupts, and records which PHY interface selections are supported.

## Important APIs, Types, and Functions
The core object is `struct stmmac_pcs`, embedded with a `struct phylink_pcs` and initialized by `stmmac_integrated_pcs_init()`. `dwmac_integrated_pcs_inband_caps()` advertises in-band negotiation only for 802.3z modes when TBI/RTBI support is detected. `dwmac_integrated_pcs_enable()` and `dwmac_integrated_pcs_disable()` toggle MAC interrupt mask bits through `stmmac_mac_irq_modify()`. `dwmac_integrated_pcs_get_state()` decodes either BASE-X state with `phylink_mii_c22_pcs_decode_state()` or RGMII/SGMII status bits from the RGSMII register. `dwmac_integrated_pcs_config()` writes advertisement and auto-negotiation control. `stmmac_integrated_pcs_irq()` updates extra stats and notifies phylink with `phylink_pcs_change()`.

## Control Flow
Initialization devm-allocates PCS state, computes register bases from offsets in `stmmac_pcs_info`, installs the ops table, probes `BMSR_ESTATEN` to infer TBI/RTBI capability, marks SGMII and 1000BASE-X as supported, optionally marks 2500BASE-X when the platform flag says the SerDes supports it, and stores the object in `priv->integrated_pcs`. Runtime phylink calls flow through the ops table. IRQ handling reads AN status, accounts for ANE/link interrupts, and reports link changes to phylink.

## State and Persistence
PCS state persists under devres for the device lifetime. Register pointers, masks, interrupt mask, and `support_tbi_rtbi` are immutable after init. Link state is hardware-owned and read on demand. Interrupt counters are accumulated in `struct stmmac_extra_stats`.

## Dependencies and Integration Points
The file depends on phylink, MII register definitions, STMMAC MAC interrupt helpers, `priv->hw->reverse_sgmii_enable`, and PCS register offsets supplied by core-specific files such as `dwmac4_core.c` and `dwmac1000_core.c`. `stmmac_main.c` asks for this PCS when the selected interface is in `supported_interfaces`.

## Risks and Test Signals
BASE-X AN capability is inferred from extended status, so unusual hardware can be misclassified. Non-802.3z state depends on correct RGSMII status mask and offset from the core description. `dwmac_integrated_pcs_config()` enables AN by default outside the BASE-X/TBI case, making reverse SGMII behavior sensitive to MAC flags. Test signals include phylink resolution for SGMII/1000BASE-X/2500BASE-X, PCS link interrupt delivery, AN restart, and link speed/duplex decode under in-band mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pcs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pcs.h

## Purpose
This header defines the integrated PCS register offsets, control bits, PCS state structures, and exported helpers used by DWMAC core files and the common STMMAC phylink path.

## Important APIs, Types, and Functions
Register definitions cover `GMAC_AN_CTRL()` and auto-negotiation control bits such as restart, enable, external loopback, comma detect, lock-to-reference, and SGMII RAL. `struct stmmac_pcs_info` is the per-core static description: PCS offset, RGSMII offset, RGSMII mask, and interrupt mask. `struct stmmac_pcs` stores the resolved register pointers, owning `stmmac_priv`, interrupt mask, embedded `phylink_pcs`, and TBI/RTBI support flag. `phylink_pcs_to_stmmac_pcs()` performs container conversion. `dwmac_ctrl_ane()` is an inline register helper that enables/restarts or disables AN and optionally sets SGMII RAL.

## Control Flow
Core implementations pass `stmmac_pcs_info` into `stmmac_integrated_pcs_init()`. Phylink later receives the embedded `phylink_pcs`; callbacks in `stmmac_pcs.c` use the inline conversion and register helpers from this header. Interrupt handlers call `stmmac_integrated_pcs_irq()`, and MAC configuration code may call `stmmac_integrated_pcs_get_phy_intf_sel()`.

## State and Persistence
The header itself stores no state. It defines the shape of PCS state that is devm-allocated by `stmmac_pcs.c` and retained via `priv->integrated_pcs`.

## Dependencies and Integration Points
It includes phylink, slab, IO helpers, and `common.h`. It is consumed by PCS implementation files and DWMAC core files that need register constants and initialization entry points.

## Risks and Test Signals
The inline `dwmac_ctrl_ane()` leaves `GMAC_AN_CTRL_RAN` set when enabling AN and only clears `ANE` when disabling, so hardware semantics around sticky restart bits matter. `srgmi_ral` is misspelled in the parameter name but functionally maps to SGMII RAL. Test signals are compile coverage across core variants, correct PCS init for each offset set, and phylink AN behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.c

## Purpose
This file is the platform/OF glue for STMMAC. It parses device-tree configuration into `plat_stmmacenet_data`, gathers MMIO and IRQ resources, exposes devres-managed probe helpers for wrapper drivers, and implements platform PM clock handling.

## Important APIs, Types, and Functions
`stmmac_probe_config_dt()` is the main DT parser. It reads MAC address, PHY mode, optional legacy `mac-mode`, `phy-handle`, max speed, bus alias, CSR clock, deprecated `snps,phy-addr`, FIFO sizes, DMA PBL/burst options, core-compatible capabilities, AXI config, MTL queues, clocks, PTP ref clock, and resets. `stmmac_mtl_setup()` parses per-RX/TX queue scheduling, DCB/AVB modes, priorities, route selectors, DMA channels, weights, and CBS parameters. `stmmac_mdio_setup()` decides whether an MDIO bus is described, required by legacy assumptions, or absent. `stmmac_get_platform_resources()` gathers named IRQs, optional per-queue IRQ arrays, and MMIO. `stmmac_pltfr_probe()`, `devm_stmmac_pltfr_probe()`, and `stmmac_pltfr_remove()` bridge wrapper drivers into common probe/remove. `stmmac_pltfr_pm_ops` provides system/runtime/noirq PM operations.

## Control Flow
Wrapper drivers usually call `devm_stmmac_probe_config_dt()` and `stmmac_get_platform_resources()`, then pass both to `stmmac_pltfr_probe()` or the devm variant. DT parsing starts with allocation and address/interface discovery, then fills MDIO, core capabilities, DMA, AXI, and MTL fields before enabling clocks and acquiring resets. Error paths release OF nodes and disable prepared clocks. Runtime suspend/resume toggles bus clocks. Noirq system suspend/resume disables the PTP ref clock and forces runtime PM only when the interface is running without WoL.

## State and Persistence
Parsed platform state persists in `plat_stmmacenet_data` and drives common driver behavior for queues, DMA mode, filter limits, PTP clock rate, MDIO, resets, and wrapper callbacks. Static `bus_id` allocates fallback Ethernet IDs for nodes without aliases. Devres actions clean clocks and OF node references. PM state depends on `priv->wolopts`, netdev running state, and prepared clocks.

## Dependencies and Integration Points
The file depends on Linux OF, platform, reset, clock, PM runtime, MDIO, and net address APIs. It exports symbols for wrapper drivers and integrates with common `stmmac_dvr_probe()`, `stmmac_suspend()`, `stmmac_resume()`, and wrapper `plat->init/exit/clks_config` hooks.

## Risks and Test Signals
DT parsing is broad and backward-compatible, so regressions often come from property precedence or missing cleanup. `stmmac_mtl_setup()` requires the number of child queue nodes to match `*-queues-to-use`; bad DT fails probe. Clock handling differs for `snps,dwc-qos-ethernet-4.10`, which skips the main clock fetch. Noirq PM only restores the PTP ref clock when WoL is off. Test signals include probe deferral on IRQ/clock/reset, MDIO discovery modes, multi-queue DT validation, suspend/resume with and without WoL, PTP clock rate selection, and wrapper-driver devres removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.h

## Purpose
This header exposes the platform glue API used by board/wrapper drivers that embed STMMAC through Linux platform devices.

## Important APIs, Types, and Functions
It declares `devm_stmmac_probe_config_dt()` for devres-managed DT parsing, `stmmac_pltfr_find_clk()` for looking up clocks by ID in `plat_stmmacenet_data`, `stmmac_get_platform_resources()` for MMIO/IRQ discovery, `stmmac_pltfr_probe()` and `devm_stmmac_pltfr_probe()` for common driver attach, `stmmac_pltfr_remove()` for detach, and `stmmac_pltfr_pm_ops` for wrapper driver PM tables. `get_stmmac_bsp_priv()` retrieves `priv->plat->bsp_priv` from a `struct device`.

## Control Flow
Wrapper drivers include this header, prepare or obtain platform data, collect resources, then call the probe helper. PM-capable wrappers can reference `stmmac_pltfr_pm_ops` directly. Wrapper-specific callbacks store their private pointer in `plat->bsp_priv`, which `get_stmmac_bsp_priv()` recovers from the netdev stored as driver data.

## State and Persistence
The header owns no state. It codifies that platform device driver data is a `struct net_device *`, and that BSP private state is reachable through the common `stmmac_priv` and platform data.

## Dependencies and Integration Points
It includes `stmmac.h`, so consumers inherit the common driver types. The functions are implemented and exported by `stmmac_platform.c`.

## Risks and Test Signals
`get_stmmac_bsp_priv()` assumes driver data has already been set to a netdev by common probe; using it before probe completion or after removal would dereference invalid state. Test signals are wrapper driver build coverage and successful probe/remove/PM callback use through this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ptp.c

## Purpose
This file implements PTP hardware clock operations for STMMAC MAC variants. It exposes Linux `ptp_clock_info` operations for frequency adjustment, time adjustment, get/set time, PPS/perout, external timestamping, cross timestamping, and clock registration.

## Important APIs, Types, and Functions
`stmmac_adjust_freq()` computes a new addend with `adjust_by_scaled_ppm()` and writes it under `ptp_lock`. `stmmac_adjust_time()` shifts system time and, if EST/TAS is enabled, temporarily disables EST, adjusts time, recalculates TAS base time via `stmmac_calc_tas_basetime()`, and reconfigures EST. `stmmac_get_time()` and `stmmac_set_time()` wrap hardware system time reads/writes. `stmmac_enable()` handles `PTP_CLK_REQ_PEROUT` through flexible PPS and `PTP_CLK_REQ_EXTTS` through auxiliary snapshot registers. `stmmac_getcrosststamp()` delegates synchronized device/system reads to a platform callback. `stmmac_ptp_register()` finalizes `priv->ptp_clock_ops` from hardware capabilities and calls `ptp_clock_register()`. `stmmac_ptp_unregister()` unregisters and destroys the aux timestamp mutex.

## Control Flow
The common hardware interface copies one of the constant ops templates into `priv->ptp_clock_ops`. During netdev setup, `stmmac_ptp_register()` adjusts per-out/ext-ts counts, max adjustment, CDC error, and cross-timestamp support, initializes locks, and registers with the PTP core. User PTP ioctls call the ops methods. Unregister tears down only if a clock was successfully registered.

## State and Persistence
Persistent state lives in `stmmac_priv`: `ptp_clock_ops`, `ptp_clock`, `ptp_lock`, `aux_ts_lock`, PPS configuration array, default addend, sub-second increment, systime flags, platform PTP rate, and EST state. External timestamp enablement also toggles `STMMAC_FLAG_EXT_SNAPSHOT_EN` in platform flags.

## Dependencies and Integration Points
This file integrates with the Linux PTP clock subsystem, STMMAC hardware callbacks (`stmmac_config_addend`, `stmmac_adjust_systime`, `stmmac_flex_pps_config`, `stmmac_get_systime`, `stmmac_init_systime`), EST/TAS support, and optional platform cross timestamp callbacks. GMAC1000 uses a different `.enable` implementation declared elsewhere but shares the common get/set/adjust methods.

## Risks and Test Signals
PTP time adjustment has a cross-feature dependency on EST; failures while reconfiguring EST are logged but `adjtime` still returns success. Perout start times in the past are treated as offsets with a 500 us safety margin, which affects user expectations. External timestamp code permits only one auxiliary snapshot channel at a time. Test signals include `ptp4l` frequency/time adjustments, PPS output, external timestamp enable/disable, EST continuity across time adjustment, crosststamp accuracy, and unregister/re-register cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ptp.h

## Purpose
This header defines STMMAC PTP register offsets, bit fields, auxiliary snapshot constants, and exported PTP clock operation templates.

## Important APIs, Types, and Functions
It defines per-core PTP register offsets for XGMAC, GMAC4, and GMAC3.x, IEEE 1588 register offsets such as timestamp control, system time, addend, auxiliary control/timestamps, correction, and latency registers, plus control bits for timestamp enable, fine/coarse update, initialization, update, addend update, rollover, protocol selection, event filtering, and MAC address filtering. It also defines SSIR limits, auxiliary snapshot enable bits, ART register selectors, `enum aux_snapshot`, prototypes for GMAC1000 PTP enable/time/interrupt helpers, and externs for `stmmac_ptp_clock_ops` and `dwmac1000_ptp_clock_ops`.

## Control Flow
Core-specific hardware setup uses these constants to locate PTP registers and configure timestamp behavior. `hwif.c` selects one of the exported `ptp_clock_info` templates for each MAC family, then the common driver copies and registers it through `stmmac_ptp_register()`.

## State and Persistence
The header stores no state. It defines the register ABI and exported operation templates used to populate persistent `priv->ptp_clock_ops`.

## Dependencies and Integration Points
It forward-declares PTP and STMMAC types to avoid heavier includes. It is consumed by `stmmac_ptp.c`, GMAC1000 core timestamp helpers, and common hardware abstraction code.

## Risks and Test Signals
Register bit definitions are hardware ABI; incorrect values cause silent timestamping failures. Several comments distinguish GMAC4 behavior for snapshot selection, so cross-core reuse needs care. Test signals are compile coverage for all PTP-capable cores, hardware timestamp enablement, auxiliary snapshot interrupts, and PPS/perout operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_selftests.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_selftests.c

## Purpose
This file implements ethtool offline selftests for STMMAC hardware. It generates loopback packets, validates received frames through packet handlers, toggles MAC/PHY loopback, and tests filtering, VLAN, TC offload, ARP offload, jumbo, split-header, and time-based scheduling features.

## Important APIs, Types, and Functions
`struct stmmac_packet_attrs` describes generated test packets, including VLAN tags, addresses, IP/ports, queue, expected RSS hash, source-address replacement mode, and launch timestamp. `stmmac_test_get_udp_skb()` and `stmmac_test_get_arp_skb()` synthesize packets. `__stmmac_test_loopback()` registers a packet handler, transmits with `dev_direct_xmit()`, and waits for completion. Individual tests include MAC/PHY loopback, MMC counters, EEE, hash/perfect/unicast/multicast filters, flow control pause frames, RSS, VLAN and double-VLAN filtering, flexible RX parser, SA insertion/replacement, VLAN TX insertion, L3/L4 flower filters, ARP offload, jumbo and multichannel jumbo, split header, and TBS/ETF. `stmmac_selftest_run()`, `stmmac_selftest_get_strings()`, and `stmmac_selftest_get_count()` are the ethtool-facing exports.

## Control Flow
`stmmac_selftest_run()` requires offline mode and carrier. It drains queues briefly, then iterates the static `stmmac_selftests[]` table. For each test it enables PHY loopback when possible or MAC loopback as requested, runs the test function, stores the return code in the ethtool buffer, marks failure for errors other than `-EOPNOTSUPP`, and disables loopback. Tests generally configure a feature, send one or more loopback frames, validate packet headers/magic IDs/counters, and restore configuration.

## State and Persistence
Most state is temporary and heap-allocated per test. The file mutates device state while testing: multicast/unicast lists, promiscuity, VLAN IDs, PHY/MAC loopback, RSS enablement, TC filters, ARP offload, SAR config, ETF/TBS state, RX queue stop/start, and `stmmac_test_next_id`. Cleanup paths usually restore state before returning.

## Dependencies and Integration Points
It depends on ethtool selftest hooks in `stmmac_ethtool.c`, PHY APIs, packet receive hooks, netdev address/VLAN APIs, TC action/offload structures when `CONFIG_NET_CLS_ACT` is enabled, STMMAC hardware operations, and PTP time for TBS testing.

## Risks and Test Signals
These are invasive offline tests and require valid link; they can alter filters, queues, and PHY loopback while running. Several tests skip with `-EOPNOTSUPP` based on hardware capability, promisc mode, RSS, or missing TC action support. Packet validation relies on generated magic IDs and timeouts, so slow hardware can appear flaky. The test file itself is the strongest signal: ethtool offline selftest output shows which STMMAC features are working on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_selftests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_tc.c

## Purpose
This file implements hardware traffic-control offloads for STMMAC: flexible RX parser `cls_u32`, flower L3/L4 and routing filters, CBS, TAPRIO/EST, ETF/TBS, capability queries, and MQPRIO/FPE mapping for newer MACs.

## Important APIs, Types, and Functions
`tc_init()` allocates L3/L4 flow entries, RFS routing entries, and flexible RX parser entries based on DMA capabilities. `tc_setup_cls_u32()` adds/replaces/deletes u32 parser rules by filling `struct stmmac_tc_entry` and programming `stmmac_rxp_config()`. `tc_setup_cls()` handles flower replace/destroy, trying L3/L4 filters, EthType routing for LLDP/PTP, and VLAN priority routing. `tc_setup_cbs()` maps CBS qdisc parameters into DWMAC credit registers and switches queues between DCB and AVB. `stmmac_calc_tas_basetime()` computes a future base time. `tc_setup_taprio()` and `tc_taprio_configure()` translate taprio gate lists into EST state and optionally configure FPE preemptible classes. `tc_setup_etf()` toggles TBS per TX queue. `tc_setup_dwmac510_mqprio()` maps Linux traffic classes to real TX queues and FPE classes.

## Control Flow
Initialization discovers capacity from `priv->dma_cap`. Runtime entry points are reached from the netdev TC setup path through HWIF macros. Classifier setup first validates offload availability and RSS conflicts, then stores cookies in driver-private entry arrays so deletes can locate hardware state. Qdisc setup validates queue/capability limits, writes hardware mode/state, and updates `plat->tx_queues_cfg`, `priv->est`, or `priv->dma_conf` as needed.

## State and Persistence
Persistent state includes `priv->tc_entries`, `flow_entries`, `rfs_entries`, per-type RFS counters, queue mode/CBS parameters in platform data, EST gate/base/cycle state under `est_lock`, per-queue TBS flags, netdev TC mapping, and FPE preemption class map. Filter cookies provide delete identity.

## Dependencies and Integration Points
It depends on Linux TC classifier/qdisc APIs, flow dissector/action APIs, STMMAC hardware callbacks for RX parser, L3/L4 filters, queue routing, CBS, EST, FPE, DMA queue modes, and RSS state. `stmmac_ptp.c` calls `stmmac_calc_tas_basetime()` when PTP time changes under EST.

## Risks and Test Signals
RSS bypasses filtering, so flower offloads return busy when RSS is enabled. Mask support is limited: VLAN priority and EthType require full masks, and L3/L4 support is capability-bound. TAPRIO must respect hardware width/depth limits and depends on a valid PTP clock; EST state is shared with PTP time adjustment. CBS rejects queue 0 and unsupported port rates. Test signals include `tc` offload acceptance/errors, ethtool selftests for RX parser/L3/L4/TBS, taprio stats, queue drops, and successful FPE/mqprio mapping on DWMAC510.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_vlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_vlan.c

## Purpose
This file implements VLAN filtering, hash/perfect VLAN match programming, VLAN insertion mode, RX VLAN acceleration, and VLAN operation tables for DWMAC/XGMAC variants.

## Important APIs, Types, and Functions
`vlan_add_hw_rx_fltr()` and `vlan_del_hw_rx_fltr()` maintain `hw->vlan_filter[]` and program either single-filter hardware or extended VLAN filter entries. `vlan_write_single()` writes the simple VLAN tag register. `vlan_write_filter()` writes extended filter data and polls the operation-busy bit. `vlan_restore_hw_rx_fltr()` replays filters after hardware reset. `vlan_update_hash()` programs DWMAC VLAN hash/perfect matching. `dwxgmac2_update_vlan_hash()` does the same for XGMAC plus packet-filter VTFE toggling. `vlan_enable()` configures TX VLAN insertion mode. `vlan_rx_hw()` transfers descriptor VLAN TCI into skb hardware-accelerated tag metadata. `vlan_set_hw_mode()` controls RX stripping and descriptor reporting. `stmmac_get_num_vlan()` decodes hardware filter-entry count from feature register bits.

## Control Flow
Netdev VLAN callbacks call the add/delete ops selected from `dwmac_vlan_ops`, `dwxgmac210_vlan_ops`, or `dwxlgmac2_vlan_ops`. Add validates VID, handles single-filter limitations, finds an empty extended slot, writes hardware if the netdev is running, then updates software shadow state. Delete clears matching slots and hardware. Restore reprograms all shadow entries after reset/open. Hash/perfect update writes either hash table mode, exact VID mode, or disables VLAN filtering.

## State and Persistence
The software shadow `hw->vlan_filter[]`, `hw->num_vlan`, and `hw->hw_vlan_en` persist in `mac_device_info`. Hardware registers hold the active filter table, hash, tag control, insertion, and strip mode. After device reset, restore uses the shadow state to rebuild hardware.

## Dependencies and Integration Points
It depends on STMMAC MAC device info, descriptor callbacks, XGMAC packet filter definitions, `readl_poll_timeout()`, and skb VLAN acceleration APIs. Operation tables are referenced by `hwif.c` for each MAC family.

## Risks and Test Signals
Single-filter hardware cannot add VID 0 and only supports one active VID. Extended filter writes can time out after 500 ms and leave shadow/hardware state unchanged. `proto` parameters are currently unused in add/delete, so C-VLAN/S-VLAN distinctions rely on surrounding mode/hash configuration. Test signals include ethtool VLAN filtering/selftests, VLAN add/delete while interface is down and after reopen, double-VLAN behavior, descriptor RX tag delivery, and feature-count decoding on GMAC/XGMAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_vlan.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_vlan.h

## Purpose
This header defines VLAN register offsets, bit fields, operation-table externs, and the feature decode helper prototype for STMMAC VLAN support.

## Important APIs, Types, and Functions
It defines MAC VLAN registers (`VLAN_TAG`, `VLAN_TAG_DATA`, `VLAN_HASH_TABLE`, `VLAN_INCL`, `HW_FEATURE3`) and masks/bits for double VLAN processing, hash mode, inverse matching, S-VLAN selection, exact tag matching, filter data validity, VLAN insertion control, strip modes, descriptor reporting, and hardware filter count encoding. It declares `dwmac_vlan_ops`, `dwxgmac210_vlan_ops`, `dwxlgmac2_vlan_ops`, and `stmmac_get_num_vlan()`.

## Control Flow
Core hardware initialization includes this header to select VLAN ops and decode filter count. The implementation uses the constants to program RX filtering, TX insertion, and RX stripping.

## State and Persistence
The header owns no state. It defines the hardware ABI and exported symbols that drive persistent VLAN state in `mac_device_info`.

## Dependencies and Integration Points
It includes `linux/bitfield.h` and `dwxgmac2.h` because XGMAC VLAN programming also touches the XGMAC packet filter. It is consumed by `stmmac_vlan.c` and core files that initialize `mac_device_info`.

## Risks and Test Signals
Bit definitions must match hardware revisions; mismatches break VLAN filtering silently. The filter-count map exposes only encoded values 0 through 5 and falls back to one filter otherwise. Test signals are compile coverage across DWMAC/XGMAC variants and runtime VLAN filtering/stripping/insertion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_xdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_xdp.c

## Purpose
This file implements STMMAC XDP program attachment and AF_XDP zero-copy pool setup/teardown. It coordinates queue shutdown/restart, DMA mapping, XDP feature flags, and split-header disabling when XDP is active.

## Important APIs, Types, and Functions
`stmmac_xdp_enable_pool()` validates queue bounds, requires XSK frame size large enough for Q-in-Q Ethernet frames, DMA maps the XSK pool with `STMMAC_RX_DMA_ATTR`, optionally disables the live RX/TX queue and NAPI, marks the queue in `priv->af_xdp_zc_qps`, reenables the queue, and wakes XSK RX. `stmmac_xdp_disable_pool()` performs the inverse: disable NAPI/queues, `synchronize_rcu()`, unmap DMA, clear the queue bit, and restore normal NAPI/queues. `stmmac_xdp_setup_pool()` selects enable vs disable based on pool presence. `stmmac_xdp_set_prog()` rejects XDP with jumbo MTU, swaps `priv->xdp_prog`, opens/releases XDP resources when the enabled state changes, and updates XDP redirect-target features.

## Control Flow
The netdev BPF setup path in `stmmac_main.c` calls these functions. Program attach/detach may trigger full XDP open/release only when the netdev is running and the boolean enabled state changes. AF_XDP pool setup can be done per queue; when the interface is live and XDP is enabled, the affected queue is temporarily stopped around the pool state transition.

## State and Persistence
Persistent state includes `priv->xdp_prog`, `priv->af_xdp_zc_qps`, per-queue XSK pool DMA mappings, NAPI mode selection, and `priv->sph_active`. Old BPF programs are released with `bpf_prog_put()`. XDP disables split header by setting `sph_active` false while any XDP program is attached.

## Dependencies and Integration Points
It depends on AF_XDP driver helpers, BPF program lifetime rules, STMMAC queue control and XDP open/release routines in `stmmac_main.c`, NAPI, netdev feature helpers, and DMA attribute definitions from `stmmac_xdp.h`.

## Risks and Test Signals
The enable path disables `rx_napi` and `tx_napi` but re-enables `rxtx_napi`; the disable path reverses from `rxtx_napi` to split NAPI, so queue/NAPI mode assumptions must match the main driver. Jumbo frames are unsupported with XDP. Pool frame-size checks require Q-in-Q capacity. Test signals include XDP attach/detach while up/down, AF_XDP bind/unbind per queue, redirect target feature visibility, XSK wakeup, and no traffic after NAPI mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_xdp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_xdp.h

## Purpose
This header exposes STMMAC XDP setup entry points and DMA attributes used for AF_XDP zero-copy RX buffers.

## Important APIs, Types, and Functions
`STMMAC_RX_DMA_ATTR` combines `DMA_ATTR_SKIP_CPU_SYNC` and `DMA_ATTR_WEAK_ORDERING` for XSK pool DMA mapping. `stmmac_xdp_setup_pool()` attaches or detaches a `struct xsk_buff_pool` to a queue. `stmmac_xdp_set_prog()` attaches or detaches a BPF/XDP program and reports errors via `netlink_ext_ack`.

## Control Flow
`stmmac_main.c` includes this header and calls the functions from its BPF/XDP netdev operations. The implementation updates queue and program state in `stmmac_xdp.c`.

## State and Persistence
The header owns no state. The declared functions mutate `stmmac_priv` XDP program, AF_XDP queue bitmap, pool DMA mappings, and split-header state.

## Dependencies and Integration Points
Types are supplied by includes already present in callers or `stmmac.h`. The DMA attribute constant must match the RX buffer ownership model used by the main driver.

## Risks and Test Signals
Changing DMA attributes affects cache synchronization and ordering for zero-copy buffers. Test signals are AF_XDP data integrity, XDP attach/detach, and builds with XDP-enabled STMMAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/Kconfig

## Purpose
This Kconfig file defines the Sun Ethernet driver menu and feature symbols under `NET_VENDOR_SUN`.

## Important APIs, Types, and Functions
`NET_VENDOR_SUN` is a vendor-gating bool enabled by default when SUN3, SBUS, PCI, or SUN_LDOMS is available. Under it, tristate driver symbols select or depend on bus/platform capabilities: `HAPPYMEAL`, `SUNBMAC`, `SUNQE`, `SUNGEM`, `CASSINI`, `SUNVNET_COMMON`, `SUNVNET`, `LDMVSW`, and `NIU`. CRC32 is selected for several physical NICs. Virtual networking depends on `SUN_LDOMS` and `INET`, with `SUNVNET` and `LDMVSW` depending on `SUNVNET_COMMON`.

## Control Flow
Kconfig first exposes the vendor menu only on relevant architectures/buses. If enabled, users can choose individual physical or virtual Sun network drivers. The selected symbols drive object inclusion in the sibling Makefile.

## State and Persistence
The persistent output is kernel configuration state in `.config`; no runtime state is defined here. Defaults mark the vendor menu and logical-domain virtual networking as enabled/module-capable when dependencies allow.

## Dependencies and Integration Points
It integrates with the Linux networking driver Kconfig tree and the local Sun Makefile. Help text maps symbols to module names such as `sunhme`, `sunbmac`, and `sunqe`.

## Risks and Test Signals
Dependency mistakes can hide drivers on valid platforms or expose unbuildable options. The vendor bool does not build code directly; disabling it skips all child prompts. Test signals are `olddefconfig` visibility on SBUS/PCI/SUN_LDOMS builds and module/object inclusion for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/Makefile

## Purpose
This Makefile maps Sun Ethernet Kconfig symbols to the driver objects built by kbuild.

## Important APIs, Types, and Functions
It uses standard `obj-$(CONFIG_...) += ...` assignments for `sunhme.o`, `sunqe.o`, `sunbmac.o`, `sungem.o`, `cassini.o`, `sunvnet_common.o`, `sunvnet.o`, `ldmvsw.o`, and `niu.o`.

## Control Flow
During kbuild, each object is included when the corresponding config symbol is `y` or built as a module when `m`. Symbols are defined in the sibling Kconfig file.

## State and Persistence
No runtime state exists. Build output depends entirely on `.config`.

## Dependencies and Integration Points
The file integrates the `drivers/net/ethernet/sun/` directory into the kernel build. `SUNVNET` and `LDMVSW` can depend on common support via Kconfig, but this Makefile only maps each symbol to its object.

## Risks and Test Signals
Object-name mismatches or missing Kconfig mappings would produce build failures or skipped drivers. Test signals are allmodconfig/allnoconfig build coverage and expected module names for selected Sun drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/Makefile -->

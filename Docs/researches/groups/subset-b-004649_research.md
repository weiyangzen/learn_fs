# subset-b-004649 research

This grouped report covers the requested STMMAC/DWMAC platform glue, MAC core, DMA, descriptor, and DWMAC5 support files. Each section is bounded with reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun8i.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun8i.c

## Purpose
Allwinner sun8i/sun50i glue for a non-standard EMAC block that is integrated with the STMMAC core but has its own register layout and DMA/MAC operation tables. It supports multiple SoC variants, syscon/CCU clock selection, internal PHY muxing, and platform-specific delays.

## Important APIs, Types, And Functions
`struct emac_variant` records syscon field, supported PHY interfaces, internal PHY presence, and delay limits. `struct sunxi_priv_data` persists clocks, regulator, reset, regmap field, PHY state, and MDIO mux handle. `sun8i_dwmac_dma_ops` and `sun8i_dwmac_ops` are the integration contracts passed through `sun8i_dwmac_setup`. Key functions include `sun8i_dwmac_probe`, `sun8i_dwmac_set_syscon`, `sun8i_dwmac_reset`, `sun8i_dwmac_power_internal_phy`, `mdio_mux_syscon_switch_fn`, and custom DMA interrupt/start/stop/init handlers.

## Control Flow
Probe gets platform resources, allocates variant private data, resolves optional PHY regulator, locates the syscon regmap, parses STMMAC DT config, installs custom ops/capabilities, programs syscon interface/delays, calls `stmmac_pltfr_probe`, resumes the runtime-suspended MAC for reset/mux work, and either registers the MDIO mux/internal PHY path or performs a plain reset. Runtime init enables the regulator and powers the internal PHY if selected. Exit/remove unwind mux, clock, reset, regulator, STMMAC platform state, and syscon bits.

## State And Persistence
Persistent state is all kernel-managed device state: syscon register fields, EMAC register bits, regulator enable count, internal PHY clock/reset state, `internal_phy_powered`, `use_internal_phy`, and mux handle. No disk persistence exists. The syscon value carries PHY mode, clock delays, EPHY address, LED polarity, and internal/external PHY selection.

## Dependencies And Integration Points
Depends on STMMAC core/platform APIs, Linux regmap/syscon, MDIO mux, runtime PM, reset, regulator, OF/MDIO parsing, and netdev multicast/unicast list handling. It deliberately bypasses generic DWMAC1000/4 ops and supplies Allwinner-specific DMA/MAC callbacks.

## Risks
Syscon writes are sensitive to DT properties and SoC variant limits; invalid delay units or unsupported PHY modes fail probe. Internal PHY muxing requires correct `mdio-mux` child nodes, reset, and clock handles. Interrupt status maps RX timeout to `tx_hard_error`, which deserves care in debugging. Reset timing was expanded to 100 ms for boards with no cable, so regressions may be board-specific.

## Test Signals
Probe/remove on each compatible, link at MII/RMII/RGMII speeds, MDIO mux switching, internal/external PHY selection, regulator and reset unwind on failures, ethtool register dumps, multicast/unicast filter programming, RX/TX IRQ counters, checksum enable, flow control, and suspend/runtime-PM interactions are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun8i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sunxi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sunxi.c

## Purpose
Legacy Allwinner sun7i A20 GMAC glue for the standard DWMAC GMAC core. It mainly programs the external TX clock and optional PHY regulator around generic STMMAC platform probing.

## Important APIs, Types, And Functions
`struct sunxi_priv_data` stores the PHY interface, TX clock enable state, TX clock handle, and optional regulator. `sun7i_gmac_init` and `sun7i_gmac_exit` are platform callbacks. `sun7i_set_clk_tx_rate` is the STMMAC speed-change callback for GMII. `sun7i_gmac_probe` wires these into `plat_stmmacenet_data`.

## Control Flow
Probe obtains STMMAC resources and DT platform config, allocates private data, gets `allwinner_gmac_tx`, handles optional `phy` regulator, sets DWMAC GMAC core type and FIFO sizes, and delegates to `devm_stmmac_pltfr_probe`. Init enables the regulator, sets clock rate to 125 MHz for RGMII/GMII or 25 MHz for MII, and prepares/enables as required. Speed changes in GMII disable/unprepare before selecting 125 MHz for 1000 Mbps or 25 MHz otherwise.

## State And Persistence
The only persistent state is the device lifetime clock/regulator state and `clk_enabled` guard. No hardware state survives beyond registers programmed by the clock framework and STMMAC core.

## Dependencies And Integration Points
Integrates with STMMAC platform callbacks, CCF clocks, regulator framework, OF match `allwinner,sun7i-a20-gmac`, and generic DWMAC GMAC support via `DWMAC_CORE_GMAC`.

## Risks
Clock prepare/enable bookkeeping is manual; mismatched `clk_enabled` paths can leak an enabled clock or unprepare incorrectly. `clk_set_rate` return values are ignored. Missing regulator is allowed except `-EPROBE_DEFER`, so board power descriptions must be correct.

## Test Signals
Probe with and without PHY regulator, link speed transitions in GMII, RGMII init rate, MII prepare-only behavior, module remove/devm cleanup, and clock rate checks are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sunxi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-tegra.c

## Purpose
NVIDIA Tegra234 MGBE glue for the XGMAC/STMMAC driver. It manages wrapper register mappings, clock/reset sequencing, IOMMU stream ID programming, XPCS/UPHY SERDES bring-up, and suspend/resume.

## Important APIs, Types, And Functions
`struct tegra_mgbe` persists device, bulk clocks, MAC/PCS resets, IOMMU SID, mapped hypervisor/MAC/XPCS register bases, and MDIO bus pointer. `tegra_mgbe_probe` is the main setup path. `mgbe_uphy_lane_bringup_serdes_up/down` are STMMAC SERDES callbacks. `tegra_mgbe_suspend` and `tegra_mgbe_resume` wrap core suspend/resume with clocks, reset, interrupt, SID, and TX lane handling.

## Control Flow
Probe maps named resources (`hypervisor`, `mac`, `xpcs`), reads the interrupt and IOMMU SID, obtains and enables all clocks, asserts/deasserts MAC and PCS resets, parses STMMAC DT config, sets `DWMAC_CORE_XGMAC`, TSO and PMT flags, ensures MDIO bus data, enables the TX UPHY lane if not powered, waits for hardware clear, installs SERDES callbacks, programs FIFO sizes, enables wrapper interrupts, writes SID, and calls `stmmac_dvr_probe`. SERDES up sequences RX override, IDDQ/sleep/calibration/data/CDR/PCS-ready bits and polls link status; down reverses RX data/sleep/IDDQ.

## State And Persistence
State lives in mapped wrapper registers, clock/reset state, `iommu_sid`, and STMMAC platform data. No disk persistence exists. Resume must reconstruct wrapper interrupt/SID and TX lane state after clock/reset cycling.

## Dependencies And Integration Points
Uses STMMAC direct DVR probe, Tegra IOMMU stream-ID helper, bulk clocks, reset framework, OF clock-name compatibility for `ptp-ref`, and XPCS/UPHY wrapper registers. It signals SERDES should power up after PHY link-up through `STMMAC_FLAG_SERDES_UP_AFTER_PHY_LINKUP`.

## Risks
The clock name table contains `mac` twice, making DT clock order/name correctness critical. Poll timeouts during TX lane or RX calibration/link can fail probe or resume. Error unwinding mostly disables clocks, so partial reset states rely on devm cleanup. Incorrect SID programming can break DMA behind IOMMU.

## Test Signals
Probe on Tegra234 DT, legacy `ptp-ref` clock fallback warning, suspend/resume with link recovery, SERDES up/down cycles, IOMMU SID write validation, XPCS timeout paths, and high-throughput XGMAC/TSO traffic are key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-thead.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-thead.c

## Purpose
T-HEAD TH1520 DWMAC platform glue that controls APB-side GMAC interface, clock direction, PLL divider, and delay registers around generic STMMAC platform probing.

## Important APIs, Types, And Functions
`struct thead_dwmac` stores the STMMAC platform data, APB register mapping, and device pointer. `thead_dwmac_set_phy_if`, `thead_dwmac_set_txclk_dir`, `thead_dwmac_enable_clk`, and `thead_set_clk_tx_rate` program glue registers. `thead_dwmac_init` is the platform init callback and `thead_dwmac_probe` wires resources.

## Control Flow
Probe gets STMMAC resources/config, optionally enables the APB clock with a warning for old DTs, maps APB register resource 1, sets `bsp_priv`, `set_clk_tx_rate`, and `init`, then calls `devm_stmmac_pltfr_probe`. Init validates MII/RGMII modes, sets interface and TX clock direction, clears RX/TX delay fields to zero, and enables clocks. RGMII speed changes compute divider from `stmmac_clk` and `rgmii_clock(speed)`.

## State And Persistence
Persistent device state is APB register programming and devm-managed clock/map lifetime. The PLL divider and clock enables persist until reset or driver removal. There is no persistent storage.

## Dependencies And Integration Points
Uses STMMAC platform config, `rgmii_clock`, OF/platform resources, CCF, and APB glue registers. It supports MII and RGMII-family modes only.

## Risks
Divider programming assumes `stmmac_clk` is an exact multiple of target RGMII clock; non-divisible rates fail link speed changes. APB clock may be absent for old DTs, leaving speed changes potentially fragile. RX/TX delay fields are hard-coded to zero, so board timing relies on PHY/interface delays.

## Test Signals
TH1520 probe with new and old DTs, MII vs RGMII register values, 10/100/1000 RGMII rate changes, invalid clock-rate rejection, and link stability after speed renegotiation are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-thead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-visconti.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-visconti.c

## Purpose
Toshiba Visconti DWMAC glue that initializes Visconti-specific Ethernet control/clock registers and supplies a speed-dependent TX clock-rate callback.

## Important APIs, Types, And Functions
`struct visconti_eth` stores the MAC register base, `phy_ref_clk`, and device. `visconti_eth_set_clk_tx_rate` programs clock mux/enable/direction for RGMII, RMII, and other modes. `visconti_eth_init_hw` sets PHY interface and releases reset. `visconti_eth_clock_probe/remove` manage clocks. Probe calls `stmmac_dvr_probe` after platform setup.

## Control Flow
Probe obtains STMMAC resources/config, allocates private data, uses the MAC resource as the glue register base, enables `phy_ref_clk`, initializes hardware interface and clocks, forces `dma_cfg->aal = 1`, then calls STMMAC. Clock-rate changes stop internal clocks, program mux selection for speed/interface, enable RX/TX/RMII clocks, and set TX output direction.

## State And Persistence
State is held in Visconti clock/control registers and clock framework state. The driver also disables both `phy_ref_clk` and `priv->plat->stmmac_clk` in its remove helper. No persistent storage exists.

## Dependencies And Integration Points
Depends on STMMAC platform parsing, `stmmac_get_phy_intf_sel`, DWMAC4 definitions, CCF clocks, and OF match `toshiba,visconti-dwmac`.

## Risks
`visconti_eth_init_hw` return value is ignored in probe, so unsupported PHY mode may not abort setup as intended. Clock remove disables `stmmac_clk` in addition to the PHY ref clock, which must align with STMMAC ownership. Speed/interface programming is register-sequence sensitive.

## Test Signals
Probe with GMII/MII/RGMII/RMII modes, unsupported PHY mode handling, 10/100/1000 speed changes, clock enable/disable balance on probe failure and remove, and DMA alignment-sensitive traffic should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-visconti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100.h

## Purpose
Register and bit definitions for the older DWMAC100 10/100 MAC and DMA block. It is consumed by DWMAC100 core and DMA implementation files.

## Important APIs, Types, And Functions
Defines MAC CSR offsets (`MAC_CONTROL`, address/hash/MII/flow/VLAN registers), control bits for duplex, port select, loopback, filtering, and flow-control pause time. Defines DMA bus-mode PBL mask, transmit threshold enum values, stop-on-empty/operate-on-second-frame bits, missed-frame counter masks, and declares `dwmac100_dma_ops`.

## Control Flow
The header has no runtime control flow; it controls how the C files interpret memory-mapped registers and construct values for init, filtering, flow control, and diagnostics.

## State And Persistence
No state is stored in the header. Its macros describe persistent hardware state written into MAC/DMA registers during device operation.

## Dependencies And Integration Points
Includes `linux/phy.h` and `common.h`; used by `dwmac100_core.c` and `dwmac100_dma.c`. It bridges generic STMMAC ops to the DWMAC100 register layout.

## Risks
Bit definitions directly encode hardware ABI. Mistakes affect register programming globally. The missed-frame counter masks and comments contain legacy naming/typos, so diagnostics should be verified against the databook.

## Test Signals
Compile coverage of DWMAC100, ethtool register dumps, flow-control register values, multicast filter modes, TX threshold selection, and missed-frame counter increments validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000.h

## Purpose
Register map and bit definitions for the DWMAC1000 GMAC generation, including MAC, PCS, EEE, PMT, filtering, DMA bus/control, flow-control thresholds, debug, extended hash, and PTP auxiliary timestamp registers.

## Important APIs, Types, And Functions
Defines `GMAC_*` offsets, PMT `enum power_event`, inter-frame gap, DMA bus mode and operation-mode bits, threshold enums (`ttc_control`, `rtc_control`, `rfa`, `rfd`), hash/address helpers, PTP auxiliary snapshot bits, and declares `dwmac1000_dma_ops`.

## Control Flow
No executable flow exists. The constants drive `dwmac1000_core.c` and `dwmac1000_dma.c` register operations for init, filters, EEE, PMT, PCS, DMA operation mode, feature discovery, and PTP.

## State And Persistence
The header stores no state. It defines hardware state layout for memory-mapped registers that persist until reset or reprogramming.

## Dependencies And Integration Points
Includes `linux/phy.h` and `common.h`; integrates with generic STMMAC core, PCS, PTP, DMA, and ethtool diagnostics by providing exact register encodings.

## Risks
Threshold encodings and FIFO flow-control masks are hardware-specific and easy to misuse. Address helper behavior changes after register 15. PTP auxiliary snapshot bits are tied to GMAC3 timestamp layout and should not be applied to incompatible cores.

## Test Signals
Build coverage, DWMAC1000 register dump sanity, PCS interrupt behavior, EEE timers, PMT wake, RX/TX flow-control threshold behavior, feature-register decode, and PTP external timestamp tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_core.c

## Purpose
Implements MAC-core operations for DWMAC1000/GMAC 3.x hardware: initialization, interrupts, filtering, flow control, PMT/WOL, EEE, PCS integration, debug counters, loopback, setup, and auxiliary PTP timestamp support.

## Important APIs, Types, And Functions
Exports `dwmac1000_ops`, `dwmac1000_setup`, `dwmac1000_get_ptptime`, `dwmac1000_timestamp_interrupt`, and `dwmac1000_ptp_enable`. Key internals include `dwmac1000_core_init`, `dwmac1000_set_filter`, `dwmac1000_irq_status`, EEE helpers, `dwmac1000_debug`, and PCS init/control functions.

## Control Flow
Setup fills `mac_device_info` with register base, filter counts, link bit masks, MII register layout, and capabilities. Core init applies jumbo/2K frame bits from MTU, writes `GMAC_CORE_INIT`, masks interrupts, and optionally configures VLAN tag detection. Runtime STMMAC callbacks then program MAC enable, checksum offload, filters, flow control, PMT, EEE, PCS, and loopback. PTP enable toggles auxiliary snapshot bits under `aux_ts_lock`, polls FIFO clear, and enables/disables timestamp interrupts.

## State And Persistence
State resides in GMAC registers, `mac_device_info`, `priv->dma_cap`, stats counters, `priv->plat->flags` for external snapshots, and PTP locks/clock event delivery. No disk state is used.

## Dependencies And Integration Points
Uses STMMAC core structures, `stmmac_pcs`, `stmmac_ptp`, ethtool stats, netdev address lists, CRC32 multicast hashing, and Linux PTP clock events.

## Risks
`dwmac1000_irq_status` uses GMAC interrupt mask semantics where disabled bits are discarded; incorrect mask writes can hide events. Multicast hash width depends on hardware configuration. External timestamp handling assumes valid PTP clock and can emit multiple events from snapshot count. Jumbo enable depends only on MTU thresholds.

## Test Signals
MAC setup, MTU >1500/>2000 behavior, unicast overflow to promiscuous, multicast hash bins 64/128/256, PMT wake, EEE LPI IRQ counters, PCS link/ANE IRQ, debug stat increments, loopback, and PTP external timestamp enable/interrupt are core tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_dma.c

## Purpose
Implements DMA operations for DWMAC1000, including AXI bus programming, channel initialization, RX/TX descriptor base setup, operation modes, register dumps, hardware feature decode, and RX watchdog.

## Important APIs, Types, And Functions
Exports `dwmac1000_dma_ops`. Key functions are `dwmac1000_dma_axi`, `dwmac1000_dma_init_channel`, `dwmac1000_dma_init_rx/tx`, `dwmac1000_dma_operation_mode_rx/tx`, `dwmac1000_configure_fc`, `dwmac1000_get_hw_feature`, and `dwmac1000_rx_watchdog`.

## Control Flow
STMMAC calls reset via common `dwmac_dma_reset`, initializes bus/channel bits, writes descriptor base addresses, configures AXI limits/burst settings, selects store-and-forward or threshold modes, and enables common DMA helpers for IRQ/start/stop. RX mode also enables embedded flow control when RX FIFO is at least 4 KiB. Feature discovery reads `DMA_HW_FEATURE` and populates `dma_features`, returning `-EOPNOTSUPP` for old zero-valued registers.

## State And Persistence
State is DMA channel registers, AXI bus mode, descriptor base addresses, interrupt masks, RX watchdog, and decoded `dma_features`. No persistent storage exists.

## Dependencies And Integration Points
Depends on `dwmac1000.h`, common `dwmac_dma.h` helpers, STMMAC DMA config, AXI config, and the common interrupt/start/stop paths in `dwmac_lib.c`.

## Risks
AXI UNDEF semantics are inverted/read-only, so platform AXI values must be valid. Flow-control thresholds are simplified to full-minus-1K/full-minus-2K. Feature decode assumes databook bit positions. Only low 32 bits of descriptor base are written, so DMA addressing support is limited here.

## Test Signals
DMA init register values for PBL/RPBL/ATDS/AAL, AXI burst/OSR settings, RX/TX SF vs threshold modes, FIFO-size flow-control behavior, hardware feature decode on old/new IP, RX watchdog writes, and normal/abnormal IRQ handling through common code are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_core.c

## Purpose
Implements MAC-core operations for the older 10/100 DWMAC100 controller used by ST SoCs.

## Important APIs, Types, And Functions
Exports `dwmac100_ops` and `dwmac100_setup`. Important callbacks include `dwmac100_core_init`, `dwmac100_set_filter`, `dwmac100_flow_ctrl`, `dwmac100_set_umac_addr/get_umac_addr`, `dwmac100_dump_mac_regs`, and `dwmac100_set_mac_loopback`.

## Control Flow
Setup fills MAC register base, 10/100 link capabilities, MII register layout, and link bit masks. Core init sets `MAC_CORE_INIT` and optional VLAN tag register. Runtime callbacks program MAC enable through common `stmmac_set_mac`, configure multicast/promiscuous filtering, set pause time, and read/write the single MAC address registers.

## State And Persistence
State is limited to MAC registers and `mac_device_info`. No PMT state is meaningful because this core reports no PMT support in the callback. No disk persistence exists.

## Dependencies And Integration Points
Uses STMMAC core, DWMAC100 header definitions, common MAC address helpers, netdev multicast lists, and CRC hashing.

## Risks
DWMAC100 has only one primary address slot; `reg_n` is ignored for address operations. RX checksum offload and host IRQ status are stubs returning zero. Flow control always writes enable bit and only conditions pause time on duplex, so `fc` parameter is not honored like newer cores.

## Test Signals
10/100 link setup, MII access, multicast hash programming, promiscuous/allmulti/no-multicast transitions, loopback bit, flow-control register contents, and register dump output provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_dma.c

## Purpose
Implements DMA operations for the DWMAC100 controller: bus/PBL setup, descriptor base programming, TX threshold selection, register dump, and missed-frame diagnostics.

## Important APIs, Types, And Functions
Exports `dwmac100_dma_ops`. Key functions are `dwmac100_dma_init`, `dwmac100_dma_init_rx/tx`, `dwmac100_dma_operation_mode_tx`, `dwmac100_dump_dma_regs`, and `dwmac100_dma_diagnostic_fr`.

## Control Flow
STMMAC resets through common `dwmac_dma_reset`, calls init to write bus mode and default interrupt mask, writes RX/TX descriptor base registers, configures TX threshold based on requested mode, and uses common helpers for DMA start/stop/IRQ/poll demand. Diagnostics reads the missed-frame counter and accumulates overflow and missed counters.

## State And Persistence
State is DMA registers and `stmmac_extra_stats` counters. Descriptor bases are written as low 32-bit DMA addresses. No durable persistence exists.

## Dependencies And Integration Points
Depends on `dwmac100.h`, `dwmac_dma.h`, common DMA helper functions, and STMMAC DMA op dispatch.

## Risks
No RX operation mode callback is supplied. TX threshold configuration ORs bits without clearing previous threshold bits, so repeated mode changes may preserve stale threshold bits. Descriptor addressing is 32-bit. Missed-frame counter interpretation must match hardware.

## Test Signals
PBL programming, descriptor base writes, TX threshold changes from ethtool/module settings, missed-frame counter increments, common DMA interrupt handling, and register dump layout are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4.h

## Purpose
Defines the DWMAC4/5 MAC and MTL register map, bit fields, helper address calculators, interrupt bits, feature bits, queue routing, filtering, EEE, CBS, debug, and L3/L4 filter constants.

## Important APIs, Types, And Functions
Important macros include `GMAC_CONFIG`, queue control registers, address/hash helpers, `GMAC_HW_FEATURE*` fields, `MTL_CHAN_*` helpers, ETS/CBS register helpers, interrupt masks, `GMAC_CORE_INIT`, and PCS status masks. It declares `dwmac4_dma_ops` and `dwmac410_dma_ops`.

## Control Flow
No runtime flow exists in the header, but inline helpers choose default or platform-provided register strides from `struct dwmac4_addrs`, affecting all DWMAC4 core/DMA register accesses.

## State And Persistence
No state is stored. The constants describe persistent hardware registers and allow platform-specific address remapping via `dwmac4_addrs`.

## Dependencies And Integration Points
Includes `common.h`; used by DWMAC4 core, DMA, lib, descriptors, DWMAC5, and platform glue such as Visconti. It is central to queue, MTL, feature, and offload support.

## Risks
Address helper changes can affect every queue/channel register access. `DMA_CHANNEL_NB_MAX` in the DMA header is separate, so register dump coverage may not reflect all hardware channels. Feature-bit interpretation must stay synchronized with Synopsys databooks.

## Test Signals
Builds across DWMAC4/5 users, feature decode, multi-queue routing, CBS, VLAN fail queueing, L3/L4 filters, EEE, PCS status, and ethtool register dumps indirectly validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_core.c

## Purpose
Implements DWMAC4/4.10/5.10 MAC operations: core init, IRQ control, queue routing/priority, MTL algorithms, CBS, filtering, flow control, WOL, EEE, PCS, debug stats, loopback, source address insertion, ARP offload, and L3/L4 filters.

## Important APIs, Types, And Functions
Exports `dwmac4_ops`, `dwmac410_ops`, `dwmac510_ops`, and `dwmac4_setup`. Key functions include `dwmac4_core_init`, `dwmac4_irq_modify`, `dwmac4_update_caps`, queue config helpers, `dwmac4_set_filter`, `dwmac4_flow_ctrl`, `dwmac4_irq_status`, `dwmac4_irq_mtl_status`, `dwmac4_config_cbs`, `dwmac4_config_l3_filter`, and `dwmac4_config_l4_filter`.

## Control Flow
Setup populates MAC register base, link capabilities including 2.5G, MII/MDIO bit masks, VLAN count, filter capacities, and multicast hash log2. Core init writes `GMAC_CORE_INIT`, programs 1-us LPI tick from `stmmac_clk`, enables default interrupts, and initializes timestamp wait queue when timestamp IRQs are enabled. STMMAC later calls ops for queues, filters, flow control, EEE, PCS, and offloads. DWMAC410/510 ops reuse DWMAC4 logic but add DWMAC5 PPS/FPE/safety/RXP callbacks.

## State And Persistence
State resides in MAC/MTL registers, `mac_device_info`, STMMAC private stats, wait queues, and platform feature/capability structures. No disk persistence exists.

## Dependencies And Integration Points
Depends on STMMAC core, FPE, PCS, VLAN helpers, DWMAC5 extension APIs, netdev lists, CRC32 multicast hashing, and platform `dwmac4_addrs` register-layout overrides.

## Risks
Multi-queue mode disables half-duplex caps. Queue priority code relies on software not mapping a priority to multiple queues. VLAN fail queueing uses DWMAC5-defined registers in DWMAC4 filter logic. LPI tick divides clock rate by 1 MHz and assumes a valid nonzero clock. L3/L4 filter programming enables global IP filtering and must avoid stale filter registers.

## Test Signals
Core init, link caps with one vs multiple queues, RX/TX priority mapping, packet routing classes, WRR/WFQ/DWRR/SP, CBS registers, unicast overflow, multicast hash table size, VLAN filtering/fail queue, WOL, EEE timer/interrupt, PCS link, MTL overflow IRQ, ARP offload, L3/L4 ethtool filters, FPE/PPS/safety op presence on 4.10/5.10 are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.c

## Purpose
Implements DWMAC4 descriptor operations for normal, extended, and enhanced descriptors, including TX/RX status parsing, ownership, timestamps, TSO, VLAN contexts, source address insertion, secondary buffers, and time-based scheduling fields.

## Important APIs, Types, And Functions
Exports `dwmac4_desc_ops` and `dwmac4_ring_mode_ops`. Key functions include `dwmac4_wrback_get_tx_status`, `dwmac4_wrback_get_rx_status`, owner setters, timestamp helpers, TX/TSO prepare, ring display, MSS context, address setters, VLAN tag context, `set_16kib_bfsize`, and `dwmac4_set_tbs`.

## Control Flow
STMMAC uses init callbacks to clear TX descriptors and assign RX descriptors to DMA. TX prepare fills buffer sizes, packet length, FS/LS, checksum insertion, TSO fields, and sets OWN after a barrier for first descriptors. RX status returns DMA-own/not-last/discard/good plus checksum flags while updating detailed stats. Timestamp status checks write-back and following context descriptors. Context descriptors are generated for MSS and VLAN insertion.

## State And Persistence
State is descriptor ring memory shared with DMA and extra stats counters. Ownership bits synchronize CPU/DMA access. No persistent storage exists.

## Dependencies And Integration Points
Depends on STMMAC descriptor structures, common status enums, DWMAC4 descriptor bit definitions, DMA memory ordering, VLAN/TSO/PTP/TBS paths in the STMMAC core.

## Risks
Descriptor ownership ordering is critical; missing barriers would cause DMA races. RX timestamp polling checks at most 10 times and may report busy. Status parsing assumes valid write-back descriptors and can discard context descriptors. TBS fields use extended descriptors and must match ring descriptor size.

## Test Signals
TX completion/error stats, RX checksum/PTP/filter stats, VLAN extraction, hardware timestamp TX/RX, TSO segmentation descriptors, MSS context updates, descriptor dump formats, 16 KiB buffer selection for large MTUs, secondary buffer addresses, and TBS launch-time programming validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.h

## Purpose
Defines DWMAC4 descriptor bit fields for transmit and receive read/write-back formats, context descriptors, VLAN, TSO, timestamps, ownership, and extended launch-time fields.

## Important APIs, Types, And Functions
Macros cover `TDES2/TDES3` buffer sizes, checksum insertion, TSO payload/header fields, context type, timestamp status, ownership, VLAN insertion, `TDES4/TDES5` launch time, and `RDES0..RDES3` RX status/filter/timestamp/error fields. It declares `dwmac4_ring_mode_ops` and `dwmac4_desc_ops`.

## Control Flow
The header has no executable flow. The descriptor ops use these masks to fill descriptors before DMA ownership and parse write-back descriptors after DMA completion.

## State And Persistence
No state is stored. It defines the memory ABI of descriptor rings shared between CPU and DMA, which persists until descriptors are recycled.

## Dependencies And Integration Points
Includes Linux bitops and is consumed by `dwmac4_descs.c` and STMMAC descriptor handling. It underpins checksum, VLAN, PTP, TSO, split-header, secondary buffer, and time-based scheduling features.

## Risks
Read and write-back formats reuse descriptor words with different meanings; using the wrong mask in the wrong phase corrupts behavior. Context descriptor bits overlap normal descriptor bits. Endianness conversion must be done by users.

## Test Signals
Descriptor ring unit/traffic tests for TSO, checksum offload, VLAN insertion/extraction, timestamping, RX filter stats, error stats, and TBS indirectly verify these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.c

## Purpose
Implements DWMAC4 DMA operations: system bus/AXI setup, per-channel init, descriptor base programming including 64-bit high halves, MTL RX/TX operation modes, feature discovery, TSO, queue mode, buffer size, split-header, and time-based scheduling enable.

## Important APIs, Types, And Functions
Exports `dwmac4_dma_ops` and `dwmac410_dma_ops`. Key functions include `dwmac4_dma_init`, `dwmac4_dma_init_channel`, `dwmac410_dma_init_channel`, `dwmac4_dma_init_rx_chan/tx_chan`, `dwmac4_dma_rx_chan_op_mode`, `dwmac4_dma_tx_chan_op_mode`, `dwmac4_get_hw_feature`, `dwmac4_enable_tso`, `dwmac4_enable_sph`, and `dwmac4_enable_tbs`.

## Control Flow
STMMAC calls common reset, global DMA init, per-channel init, RX/TX descriptor-base setup, then MTL operation mode setup. RX mode selects store-and-forward or thresholds, sets queue FIFO size, disables TCP error forwarding, and enables flow control if FIFO and queue type allow. TX mode selects SF/threshold, queue enable mode, and FIFO size. Feature discovery reads four GMAC hardware feature registers and populates capabilities for checksum, timestamps, queues, FIFO sizes, TSO, SPH, FPE, EST, FRP, TBS, and address width.

## State And Persistence
State is DMA and MTL channel registers, descriptor base high/low registers, FIFO/threshold config, capability fields, and offload enable bits. No disk state exists.

## Dependencies And Integration Points
Depends on DWMAC4 headers/lib helpers, STMMAC DMA config, AXI config, platform `dwmac4_addrs`, and DWMAC4/5 feature consumers in the core.

## Risks
Flow-control threshold constants are tuned by FIFO size and may overflow at 4 KiB. Feature decode converts encoded FIFO/address widths and must match hardware. `DMA_CHANNEL_NB_MAX` register dumps only one channel despite hardware supporting more. Enabling TBS verifies EDSE but only DWMAC410 ops expose it.

## Test Signals
DMA init for fixed/mixed/AAL/EAME/DCHE/MSI modes, 64-bit descriptor base writes, RX/TX SF and threshold modes, AVB vs DCB queue enable, feature register decode, TSO toggling, SPH enable and buffer size, TBS enable failure path, and multi-queue traffic are primary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.h

## Purpose
Defines DWMAC4 DMA register offsets, channel address helpers, interrupt masks, control bits, TBS control, ring-length/tail-pointer/current-pointer registers, status masks, and prototypes for lib helpers.

## Important APIs, Types, And Functions
The `dma_chanx_base_addr` helper supports default and platform-specific `dwmac4_addrs`. Macros define global bus mode, system bus mode, AXI LPI/OSR, channel TX/RX control, descriptor base high/low, ring length, interrupt enable/status masks, RX watchdog, and current descriptors/buffers. It declares `dwmac4_dma_reset`, IRQ enable/disable, start/stop, interrupt, ring length, and tail pointer helpers.

## Control Flow
No runtime flow except address calculation. The macros drive all DWMAC4 DMA/lib register access.

## State And Persistence
No stored state. It describes DMA channel register state that persists in hardware.

## Dependencies And Integration Points
Used by `dwmac4_dma.c` and `dwmac4_lib.c`; depends on `struct dwmac4_addrs` from common STMMAC definitions.

## Risks
Interrupt summary bit definitions differ between 4.00 and 4.10; the header carries separate masks that must be paired with the correct ops table. Channel address remapping must be consistent across DMA and MTL users. `DMA_CHANNEL_NB_MAX` is set to 1 for dumps, not actual max capability.

## Test Signals
Compile coverage, register dump offsets, interrupt handling on 4.00 vs 4.10, ring length/tail pointer writes, 64-bit base address registers, and TBS register writes validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c

## Purpose
Provides common DWMAC4 DMA/MAC helper functions used by the DWMAC4/4.10 DMA ops: reset, tail pointers, ring lengths, DMA start/stop, IRQ enable/disable, interrupt decoding, DWMAC4 MAC address programming, and MAC RX/TX enable.

## Important APIs, Types, And Functions
Exports helper functions declared in `dwmac4_dma.h`: `dwmac4_dma_reset`, `dwmac4_set_rx_tail_ptr`, `dwmac4_set_tx_tail_ptr`, `dwmac4_dma_start_tx/rx`, `dwmac4_dma_stop_tx/rx`, ring length setters, IRQ enable/disable, `dwmac4_dma_interrupt`, `stmmac_dwmac4_set_mac_addr`, and `stmmac_dwmac4_set_mac`.

## Control Flow
Reset sets software reset and polls up to 1 s. Start TX/RX sets DMA channel bits and also enables MAC TE/RE in `GMAC_CONFIG`; stop only clears DMA channel bits. Interrupt handling reads channel status/enables, masks by RX or TX direction, updates abnormal/normal stats, returns STMMAC action flags, and clears enabled pending bits.

## State And Persistence
State is hardware register bits, per-CPU IRQ stats, and `stmmac_extra_stats`. MAC address writes set the AE bit and default DMA channel selection for address filters. No durable persistence exists.

## Dependencies And Integration Points
Depends on DWMAC4 DMA and MAC headers, common status enums, STMMAC stats, and platform address overrides. Used by DWMAC4 DMA ops tables.

## Risks
Start enables MAC RX/TX globally but stop only stops DMA, so caller sequencing matters. Interrupt clear writes `intr_status & intr_en`, unlike older common DMA code. MAC address helper assumes non-null address and channel 0 destination selection. Reset timeout is longer than older DMA.

## Test Signals
Reset timeout behavior, start/stop register bits, IRQ counters/action returns for RX/TX/fatal/RBU/RPS/RWT/TBU/ERI, tail/ring writes, MAC address filter programming, and MAC enable/disable transitions are key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.c

## Purpose
Adds DWMAC5/EQoS 5.x features used by DWMAC510 ops: automotive safety/ECC/parity handling, RX parser table programming, and flexible PPS output configuration.

## Important APIs, Types, And Functions
Exports `dwmac5_safety_feat_config`, `dwmac5_safety_feat_irq_status`, `dwmac5_safety_feat_dump`, `dwmac5_rxp_config`, and `dwmac5_flex_pps_config`. Internal error descriptor tables map MAC/MTL/DMA safety bits to stat offsets and log strings. RX parser helpers disable/enable parser and update internal RAM entries.

## Control Flow
Safety config enables ECC/address override and interrupt bits based on ASP level and optional config, then enables FSM parity/timeout and data parity protection for higher ASP levels. Safety IRQ status reads MTL/DMA summary bits, dispatches MAC/MTL/DMA handlers, clears detailed status registers, logs each set bit, updates stats, and returns nonzero on uncorrectable errors. RX parser config disables MAC RX, disables parser, clears `in_hw`, programs entries by priority plus fragments, appends last/pass entry, writes NPE/NVE, enables parser, and restores RX. PPS config validates busy/sub-second inputs, disables or sets target time, interval, width, and activate command.

## State And Persistence
State lives in safety control/status registers, `stmmac_safety_stats`, RX parser table RAM, `stmmac_tc_entry` metadata (`in_hw`, `table_pos`), PPS registers, and MAC RX enable state. No disk persistence exists.

## Dependencies And Integration Points
Depends on DWMAC4/5 registers, STMMAC TC entries, PTP time flags, netdev logging, and DWMAC510 ops table in `dwmac4_core.c`.

## Risks
Safety log uses bit positions as stat array offsets; layout coupling with `stmmac_safety_stats` is strict. RX parser temporarily disables RX and must restore prior MAC config on all paths. `min_prio_idx` is only valid if `found`. PPS period math divides by `sub_second_inc` and rejects too-small periods after programming some state.

## Test Signals
Safety config for ASP 0/1/2/3, correctable vs uncorrectable IRQ handling and stats, invalid dump indexes, RX parser entry ordering/fragments/last entry, no-entry path, RX restore after update failure, PPS enable/disable, busy target rejection, binary vs digital rollover nanosecond conversion, and FPE users of DWMAC510 ops are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.h

## Purpose
Defines DWMAC5/EQoS 5.x registers and bit fields for safety, RX parser, PPS, VLAN fail queueing, and FPE interrupt enable, plus prototypes for DWMAC5 extension functions.

## Important APIs, Types, And Functions
Key macros include safety status/control registers (`MAC_DPP_FSM_INT_STATUS`, `MTL_ECC_CONTROL`, `DMA_SAFETY_INT_STATUS`), RX parser control/internal-access fields, PPS control/target/interval/width helpers, VLAN fail queue register fields, and `GMAC_INT_FPE_EN`. Function prototypes expose safety config/status/dump, RX parser config, and flexible PPS config.

## Control Flow
No runtime flow exists. The C implementation uses these macros to program and decode DWMAC5 hardware blocks.

## State And Persistence
No state is stored in the header. The defined registers represent hardware state for safety, parser table control, and PPS outputs.

## Dependencies And Integration Points
Used by `dwmac5.c` and `dwmac4_core.c`; depends on STMMAC types for safety cfg/stats, TC entries, and PPS cfg.

## Risks
PPS bit helper macros construct per-index fields inside a shared register; index range must be validated by callers/capabilities. Safety bits are tightly coupled to hardware ASP levels. RX parser internal-access fields require strict busy polling in users.

## Test Signals
DWMAC510 build coverage, safety feature tests, RX parser filter programming, VLAN fail queue behavior, PPS output configuration, and FPE interrupt enable paths validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_dma.h

## Purpose
Defines common pre-DWMAC4 DMA register offsets, channel address helpers, status/control/interrupt masks, AXI mode fields, register dump sizes, and common helper prototypes.

## Important APIs, Types, And Functions
Macros cover `DMA_BUS_MODE`, poll-demand registers, descriptor base registers, `DMA_STATUS` event bits, RX/TX/common masks, `DMA_CONTROL` start/stop/flush bits, interrupt enable masks, missed-frame counter, channel offset helpers, RX watchdog, AXI LPI/OSR/UNDEF fields, current buffer registers, and hardware feature register. Prototypes expose common DMA start/stop/IRQ/reset and poll helpers.

## Control Flow
No runtime control flow except `dma_chan_base_addr`, which maps common register offsets to per-channel offsets.

## State And Persistence
No state is stored. It describes hardware DMA register state used by DWMAC100 and DWMAC1000 code.

## Dependencies And Integration Points
Used by `dwmac_lib.c`, `dwmac100_dma.c`, and `dwmac1000_dma.c`. It integrates older DMA engines with STMMAC's `stmmac_dma_ops`.

## Risks
Interrupt mask definitions are shared across older cores and must be paired with correct channel offsets. Common helper prototypes assume this older register layout, not DWMAC4. Debug state masks are only used when `DWMAC_DMA_DEBUG` is enabled.

## Test Signals
Compile coverage for DWMAC100/1000, DMA reset/poll demand/start/stop, RX/TX IRQ masks, AXI config, RX watchdog, and register dump sizes validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_lib.c

## Purpose
Common helper implementation for older DWMAC DMA/MAC blocks: DMA reset, poll demand, IRQ masks, start/stop, interrupt decoding, TX FIFO flush, and generic MAC address and MAC enable helpers.

## Important APIs, Types, And Functions
Exports `dwmac_dma_reset`, DMA poll/start/stop/IRQ helpers, `dwmac_dma_interrupt`, `dwmac_dma_flush_tx_fifo`, `stmmac_set_mac_addr`, `stmmac_set_mac`, and `stmmac_get_mac_addr`. Optional debug helpers decode TX/RX process state when compiled with `DWMAC_DMA_DEBUG`.

## Control Flow
Reset sets software reset and polls until clear. Poll helpers write demand registers. Start/stop toggle `DMA_CONTROL_ST/SR`. Interrupt handling reads channel status, optionally logs debug state, masks by RX/TX direction, updates abnormal and normal stats, returns STMMAC action flags, warns on unexpected PMT/MMC/line-interface bits, and clears low status bits. MAC address helper writes high/low words with AE; enable helper toggles generic RX/TX bits.

## State And Persistence
State is hardware DMA/MAC registers and stats counters. Exported MAC address registers retain programmed values until reconfigured/reset. No disk persistence exists.

## Dependencies And Integration Points
Depends on `common.h`, `dwmac_dma.h`, STMMAC stats/action enums, Linux iopoll, and is reused by DWMAC100 and DWMAC1000 DMA ops.

## Risks
Interrupt handling checks the global `DMA_INTR_ENA` register for RX enable rather than channel-specific enable in one path, which is legacy-layout sensitive. TX FIFO flush busy-waits without timeout. MAC address helper assumes `addr` is valid and sets AE even for high register 0.

## Test Signals
DMA reset timeout, poll demand, start/stop bits, abnormal IRQ cases, per-CPU normal IRQ counters, unexpected optional interrupt warnings, FIFO flush completion, MAC address round-trip, and MAC enable/disable register transitions are the key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_lib.c -->

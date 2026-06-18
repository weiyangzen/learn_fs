# subset-b-001152 Research

Grouped research for the listed Qualcomm clock-controller source files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-sdm660.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-sdm660.c

## Purpose
`mmcc-sdm660.c` implements the Qualcomm multimedia clock controller for SDM660 and the closely related SDM630. It registers multimedia PLLs, root clock generators, branch gates, reset lines, and GDSC power domains for camera, display, video, memory/interconnect, SMMU, and miscellaneous MMSS blocks. Its exported clock IDs come from `dt-bindings/clock/qcom,mmcc-sdm660.h`, so consumers in device tree can request stable identifiers such as CAMSS, MDSS, DP, DSI byte/pixel, VFE, JPEG, and Venus clocks.

## Important APIs, Types, And Functions
The file is almost entirely static clock-provider data consumed by the Qualcomm common clock framework. Important types include `struct clk_alpha_pll`, `struct alpha_pll_config`, `struct pll_vco`, `struct parent_map`, `struct clk_parent_data`, `struct freq_tbl`, `struct clk_rcg2`, `struct clk_branch`, `struct clk_regmap_div`, `struct gdsc`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`.

The top-level entry point is `mmcc_660_probe()`. It maps the MMIO register block with `qcom_cc_map()`, applies SDM630-specific clock removal through `sdm630_clock_override()` when `device_get_match_data()` returns the match-table data flag, configures APSS-controlled multimedia alpha PLLs with `clk_alpha_pll_configure()`, and finally registers the provider through `qcom_cc_really_probe()`. `module_platform_driver(mmcc_660_driver)` binds this probe path to `qcom,mmcc-sdm660` and `qcom,mmcc-sdm630`.

## Clock Model And Control Flow
The driver builds a hierarchy from fixed external parents (`xo`, sleep clock, DSI PLL byte/pixel clocks, DP PHY link/VCO clocks, GPLL0 outputs) through local MMPLL sources and RCGs into branch clocks. Voteable PLLs `mmpll0` and `mmpll6` use shared enable registers at `0x1f0`; APSS-controlled PLLs `mmpll3`, `mmpll4`, `mmpll5`, `mmpll7`, `mmpll8`, and `mmpll10` have explicit alpha PLL configurations and VCO tables. Parent maps encode the hardware source selector values for the many RCGs.

Frequency tables describe supported rates for AHB, CAMSS general-purpose clocks, CCI, CPP, CSI PHY/timers, DisplayPort auxiliary/crypto/GTC/link paths, JPEG, MCLK, MDP, rotation, VFE, video core, AXI, and other roots. Branch gates then expose block-local enables and halt checks. Many branches use `CLK_SET_RATE_PARENT`, allowing display/camera/video consumers to change the upstream RCG rate through the branch clock. DSI byte, DSI pixel, DisplayPort link/pixel, and video subcore clocks use `CLK_GET_RATE_NOCACHE` where rate must be read live because the real source may be a PHY or external hardware path.

## State And Persistence Behavior
The persistent state is hardware register state in the MMCC register range, plus GDSC power-domain state in the GDSCR/CXC registers. The `regmap_config` is 32-bit, 4-byte-stride, fast I/O, and allows accesses up to `0x40000`. The driver has no remove callback; registered clocks, resets, and power domains are owned by the platform device and common clock framework for the lifetime of the device.

SDM630 handling mutates the static `mmcc_660_desc.clks` array by setting second-DSI clock entries to `NULL`, because SDM630 has only one DSI interface. That mutation is process-global state in the module. It is safe for normal single-compatible probing, but it means the descriptor is not immutable after an SDM630 probe.

## Dependencies And Integration Points
This code depends on Linux CCF, platform-device matching, regmap MMIO, Qualcomm clock helpers (`common.h`, `clk-regmap.h`, `clk-alpha-pll.h`, `clk-rcg.h`, `clk-branch.h`, `clk-regmap-divider.h`), Qualcomm reset helpers, and Qualcomm GDSC support. Device-tree integration is through `qcom,mmcc-sdm660` or `qcom,mmcc-sdm630` compatible strings, one MMIO resource, and parent clock names or phandles for `xo`, DSI PLLs, sleep clock, GPLL0, and DP PHY clocks.

Downstream consumers include DRM/MSM display drivers, camera/VFE/CSI/JPEG drivers, Venus video drivers, SMMU/interconnect users, and reset consumers for `MDSS_BCR` and `CAMSS_MICRO_BCR`. GDSC entries expose power domains for Venus, MDSS, CAMSS top/VFE/CPP, and Venus core0, with parent-child relationships where hardware requires top domains before subdomains.

## Risks And Edge Cases
The largest correctness risk is table drift: RCG register offsets, parent selector values, reset offsets, and DT binding indexes must all match the SoC clock plan. Incorrect values can produce silent bad rates, failed clock enables, or hangs in camera/display/video blocks. The commented-out `bimc_smmu_gdsc` notes that this domain can hang the multimedia subsystem, which is a strong signal that GDSC additions need board-level validation rather than mechanical table extension.

SDM630 override mutability is another risk if mixed compatibles could ever share a loaded module instance. Several PHY-fed clocks intentionally bypass cached rates; removing `CLK_GET_RATE_NOCACHE` would make link and pixel programming stale. PLL programming in probe is also sensitive: changing alpha PLL configs may disrupt firmware/APSS assumptions or bootloader-initialized rates.

## Test Signals
Useful smoke signals are successful probe, no deferred parent-clock failures, a populated `/sys/kernel/debug/clk/clk_summary`, and visible registration of GDSC power domains. Functional tests should exercise display bring-up over DSI/DP, camera CSI/VFE/JPEG pipelines, Venus video decode/encode, and reset assertions for MDSS/CAMSS microcontroller blocks. Rate tests should verify key tables via `clk_summary` or tracepoints while changing display modes, camera resolutions, and video workloads. SDM630-specific testing should confirm the second DSI clocks are absent and that single-DSI display paths still work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-sdm660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/negcc-nord.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/negcc-nord.c

## Purpose
`negcc-nord.c` implements the Qualcomm NORD NE_GCC clock controller. It provides clocks, resets, DFS metadata, and GDSC power domains for a peripheral-oriented clock block covering UFS PHY, primary and secondary USB/USB3 paths, QUPv3 wrapper 2 serial engines, SDCC4, a secondary GPU-related clock group, and general-purpose clocks. Clock and reset IDs are sourced from `dt-bindings/clock/qcom,nord-negcc.h`.

## Important APIs, Types, And Functions
The driver uses the Qualcomm common clock framework data structures: `clk_alpha_pll` and `clk_alpha_pll_postdiv` for Lucid OLE PLLs, `clk_rcg2` for root clock generators, `clk_branch` for gates and halt checks, `clk_regmap_div` for post-dividers, `clk_regmap_mux` and `clk_regmap_phy_mux` for PHY pipe/symbol source selection, `gdsc` for power domains, `qcom_reset_map` for block resets, `clk_rcg_dfs_data` for dynamic frequency scaling RCGs, `qcom_cc_driver_data` for probe-time extras, and `qcom_cc_desc` for final registration.

The functional entry points are small. `clk_nord_regs_configure()` sets `FORCE_MEM_CORE_ON` for the UFS ICE core and UFS AXI branches with `qcom_branch_set_force_mem_core()`. `ne_gcc_nord_probe()` calls `qcom_cc_probe()` with `ne_gcc_nord_desc`. The match table binds `qcom,nord-negcc`, and `module_platform_driver()` installs the platform driver.

## Clock Model And Control Flow
The provider starts with Lucid OLE PLLs `ne_gcc_gpll0`, its even post-divider `ne_gcc_gpll0_out_even`, and `ne_gcc_gpll2`, all ultimately sourced from DT parent index `DT_BI_TCXO`. Parent maps combine TCXO, GPLL0 main/even, GPLL2, sleep clock, UFS RX/TX symbol parents, and USB3 PHY pipe clocks. PHY symbol and pipe inputs are represented through dedicated regmap mux helpers so UFS and USB PHY wrappers can provide recovered or pipe clocks to the controller.

RCGs define programmable rates for `gp1`, `gp2`, QUPv3 wrapper 2 serial engines `s0` through `s6`, SDCC4 applications, UFS PHY AXI/ICE/aux/unipro, USB20 master/mock UTMI, USB31 primary and secondary master/mock UTMI, and USB3 primary/secondary PHY aux clocks. Branch gates expose the usable clocks for aggregate NoC paths, CNOC USB paths, GPU secondary paths, QUP wrapper core and serial lines, SDCC4, UFS PHY subclocks, USB sleep/master/mock/pipe/aux/com-aux paths, and frequency measurement.

Probe-time control flow is declarative: `qcom_cc_probe()` maps registers, registers clocks/resets/GDSCs, applies driver data, and installs DFS support for the listed QUP RCGs. The custom register callback is part of `qcom_cc_driver_data`, so UFS force-memory settings are applied during common registration rather than in a hand-written probe sequence.

## State And Persistence Behavior
Persistent state lives in the NE_GCC hardware registers up to `0xf41f0`, with 32-bit values and 4-byte stride. PLL enable bits use shared registers, RCGs persist their command/source/divider fields, branch clocks persist enable bits and memory-core override settings, reset lines persist only while asserted, and GDSCs persist power-domain state for UFS and USB islands. The driver has no local dynamic allocation or remove path; the common framework owns provider state after probe.

DFS metadata for QUPv3 serial clocks is static state used by the clock framework to coordinate runtime rate transitions. `clk_nord_regs_configure()` intentionally changes branch memory-retention behavior for UFS ICE/AXI, so storage stability depends on this setup being applied before UFS consumers aggressively gate or power-manage those clocks.

## Dependencies And Integration Points
The driver depends on DT parent ordering, `qcom,nord-negcc` bindings, Linux CCF, regmap, Qualcomm PLL/RCG/branch/divider/mux/PHY-mux helpers, reset support, and GDSC power domains. External parent clocks include TCXO, sleep, UFS PHY symbol clocks, and primary/secondary USB3 pipe clocks. Consumers include UFS host/PHY and ICE, USB2/USB3 controllers and PHYs, QUPv3 serial controllers, SDCC4/eMMC or SD card paths, GPU-related NoC/SMMU voting clocks, and reset-controller users for USB/UFS/QUP/SDCC blocks.

GDSC integration exposes seven domains: UFS memory PHY, UFS PHY, USB20 primary, USB31 primary, USB31 secondary, USB3 PHY, and USB3 secondary PHY. Reset integration covers GPU secondary, QUP wrapper 2, SDCC4, UFS PHY, USB20/USB31 blocks, USB3 DP PHY blocks, USB3 PHY blocks, and USB3PHY PHY sub-blocks.

## Risks And Edge Cases
The highest risk is mismatched DT parent order because many parent references use `.index` rather than names. A binding/order mismatch would route serial, UFS, or USB clocks to the wrong source. PHY muxes for UFS symbol and USB pipe clocks are also sensitive to hardware readiness; consumers may see bad rates or enable failures if PHY drivers are not registered or if parent clock flags are wrong.

UFS has a targeted force-memory-core workaround. Removing or moving it could introduce data-path instability during low-power transitions. QUP DFS tables must stay aligned with serial-engine expectations; incomplete DFS coverage can cause rate switches to fail for some UART/SPI/I2C instances. Because the driver is mostly generated-style tables, small offset or bit mistakes in branch/reset/GDSC data can have broad runtime effects.

## Test Signals
Probe should register the `qcom,nord-negcc` provider without missing parent errors and show PLLs, RCGs, branches, and GDSCs in debugfs. UFS tests should cover link startup, high-speed modes, ICE activity, suspend/resume, and runtime PM. USB tests should cover primary and secondary USB3 pipe clocks, USB2 UTMI mock clocks, connect/disconnect, and suspend/resume. QUP tests should change rates on all seven wrapper 2 serial engines. Reset signals can be validated through peripheral reinitialization after reset-controller assertions, and GDSC signals through power-domain on/off transitions while clocks are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/negcc-nord.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-ipq5424.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-ipq5424.c

## Purpose
`nsscc-ipq5424.c` implements the Qualcomm NSS clock controller for IPQ5424 networking SoCs. It registers NSS/PPE/packet-engine clocks, Ethernet port RX/TX and MAC clocks, UNIPHY clocks, XGMAC PTP reference clocks, reset lines, and hardware-backed interconnect nodes for NSS NoC paths. Clock IDs, reset IDs, and interconnect node IDs come from `dt-bindings/clock/qcom,ipq5424-nsscc.h`, `dt-bindings/reset/qcom,ipq5424-nsscc.h`, and `dt-bindings/interconnect/qcom,ipq5424.h`.

## Important APIs, Types, And Functions
The core data types are `struct parent_map`, `struct clk_parent_data`, `struct freq_tbl`, `struct freq_conf`, `struct freq_multi_tbl`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct qcom_reset_map`, `struct qcom_icc_hws_data`, `struct regmap_config`, and `struct qcom_cc_desc`. The networking port RCGs use `freq_multi_tbl` and `clk_rcg2_floor_ops`, allowing discrete multi-output frequency programming for 25 MHz and 125 MHz Ethernet-style rates.

`nss_cc_ipq5424_probe()` is the only custom runtime function. It enables runtime PM, creates a PM clock container, adds a `"bus"` PM clock, resumes the device so the NSSCC register block is accessible, calls `qcom_cc_probe()`, and then drops the runtime PM reference. Runtime PM callbacks are `pm_clk_suspend` and `pm_clk_resume` through `SET_RUNTIME_PM_OPS()`. The platform driver also sets `.sync_state = icc_sync_state` so interconnect aggregation can synchronize after consumers are ready.

## Clock Model And Control Flow
The parent model is built from external DT-supplied parents: common PLL XO, common PLL NSS 300 MHz, common PLL NSS 375 MHz, GCC GPLL0 auxiliary, and three UNIPHY RX/TX parent pairs. Parent maps select combinations appropriate for generic NSS roots and for each port's RX/TX path.

The RCG set covers CE, NSS configuration, EIP BFDCD, PPE, and port1/port2/port3 RX and TX sources. Port RX/TX source clocks use two supported rate configurations, 25 MHz and 125 MHz, with separate RX/TX parent selections. Divider clocks sit after the port RCGs, and XGMAC PTP reference divider clocks provide per-MAC PTP timing sources.

Branch clocks expose CE APB/AXI, debug, EIP, NSS CSR, NSSNOC CE/EIP/NSS CSR/PPE/PPE CFG, three MAC clocks, three port RX/TX clocks, PPE eDMA and switch clocks, UNIPHY port RX/TX clocks, and XGMAC0-2 PTP reference clocks. Most branches set `CLK_SET_RATE_PARENT`, which lets Ethernet, PPE, and NSS consumers vote rates through branches to their RCGs or dividers.

## State And Persistence Behavior
The register map is 32-bit, 4-byte-stride, fast I/O, with a maximum register offset of `0x800`. Runtime PM and the `"bus"` PM clock gate access to that register space during probe and suspend/resume. After registration, clock enable bits, RCG source/divider settings, divider settings, reset bits, and interconnect hardware clock votes persist in hardware registers.

The descriptor registers six hardware-backed interconnect links with an `icc_first_node_id` derived from `5424 * 2`. These entries connect NSSNOC masters and slaves to concrete branch clock IDs, so bandwidth votes can enable or scale the backing NSSNOC clocks rather than relying only on direct clock consumers.

## Dependencies And Integration Points
The driver depends on Linux CCF, runtime PM, PM clock support, interconnect provider support, regmap, Qualcomm common clock/reset helpers, and a device tree that supplies the NSSCC MMIO resource, `"bus"` clock, and all listed parent clocks in binding order. It integrates with networking drivers for NSS, PPE switch/eDMA, crypto/EIP, Ethernet MAC/UNIPHY/XGMAC PTP paths, reset-controller consumers, and interconnect consumers that vote NSSNOC bandwidth.

The platform match compatible is `qcom,ipq5424-nsscc`. The driver name is also set to `qcom,ipq5424-nsscc`, and the PM ops must remain wired so register access is only attempted while the bus clock is active.

## Risks And Edge Cases
The main risk is hardware table accuracy. Parent selector values, multi-frequency port configurations, divider widths, branch offsets, halt registers, and reset bits must match IPQ5424 NSSCC. A bad port parent or divider can produce link-speed-specific failures that only appear at 10/100/1000 mode transitions or PTP validation. Interconnect node IDs also need to remain unique and aligned with the bindings; collisions would misroute bandwidth votes.

Probe ordering depends on the `"bus"` PM clock. If DT omits or misnames it, `pm_clk_add()` fails and no NSS clocks are registered. If runtime PM usage changes, `qcom_cc_probe()` may touch registers while the bus is off. The `pm_runtime_put()` call after probe means later accesses rely on clock-framework and PM-clock integration rather than a permanently active bus.

## Test Signals
Probe should complete without `"Fail to enable runtime PM"`, `"Fail to create PM clock"`, `"Fail to add bus clock"`, or `"Fail to resume"` errors. Debugfs should show CE, PPE, NSSNOC, port, UNIPHY, and XGMAC clocks with expected parents and rates. Functional tests should cover Ethernet links on all three ports at supported speeds, PTP timestamp stability on XGMAC0-2, PPE/eDMA traffic, EIP/crypto traffic if available, runtime suspend/resume, and interconnect bandwidth votes that enable the mapped NSSNOC clocks. Reset tests should assert/deassert PPE, port, UNIPHY, CE, EIP, and XGMAC resets and verify the owning drivers recover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-ipq5424.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-ipq9574.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-ipq9574.c

## Purpose
`nsscc-ipq9574.c` implements the Qualcomm NSS clock controller for IPQ9574. It is a larger networking clock provider than the IPQ5424 variant, covering CE, CLC, crypto/EIP, HAQ, IMEM, NSS CSR, NSSNOC, PPE, six Ethernet ports, six UNIPHY RX/TX paths, six XGMAC PTP reference paths, and four UBI32 core complexes. It also exposes a local UBI32 Huayra alpha PLL and hardware-backed interconnect clock nodes. IDs come from the IPQ9574 clock, reset, and interconnect DT binding headers.

## Important APIs, Types, And Functions
Key types include `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `alpha_pll_config`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `freq_tbl`, `freq_conf`, `freq_multi_tbl`, `qcom_reset_map`, `qcom_icc_hws_data`, `regmap_config`, and `qcom_cc_desc`. The local `ubi32_pll_main` uses `CLK_ALPHA_PLL_TYPE_NSS_HUAYRA`, `SUPPORTS_DYNAMIC_UPDATE`, and `clk_alpha_pll_huayra_ops`; `ubi32_pll` is a read-only postdivider exported as the usable PLL output.

`nss_cc_ipq9574_probe()` performs runtime PM setup, adds the `"bus"` PM clock, resumes the hardware, maps the controller with `qcom_cc_map()`, programs the UBI32 PLL using `clk_alpha_pll_configure()`, registers clocks/resets/interconnect nodes through `qcom_cc_really_probe()`, and releases the runtime PM reference. Runtime suspend/resume is delegated to `pm_clk_suspend` and `pm_clk_resume`, and driver sync state is `icc_sync_state`.

## Clock Model And Control Flow
The root parent model includes XO, bias PLL CC, bias PLL UBI NC, GCC GPLL0 auxiliary, the local UBI32 PLL output, and three UNIPHY RX/TX parent pairs. Parent maps are specialized for generic NSS roots, port roots, PPE/UBI roots, and PTP references.

RCGs define CE, configuration, CLC, crypto, HAQ, IMEM, internal configuration, PPE, UBI0-UBI3, UBI AXI, UBI NC AXI BFDCD, and port1-port6 RX/TX source clocks. Port 1 and 6 support 25/125 MHz style configurations; ports 5 adds a 312.5 MHz configuration for higher-speed operation; the source structures for ports 2-4 reuse the same base patterns with different offsets and parent maps. UBI RCGs select from the local UBI32 PLL and other NSS parents, with divider clocks for each UBI core.

Branch clocks expose the full hierarchy: CE, CLC, crypto/PPE, HAQ, IMEM, NSS CSR, NSSNOC mirrors, six MAC and port RX/TX branches, PPE switch/eDMA branches, many UBI32 AHB/AXI/core/intr/NC/UTCM branches, six UNIPHY port RX/TX branches, and XGMAC0-5 PTP reference branches. Most branches propagate rate changes upward with `CLK_SET_RATE_PARENT`, reflecting that consumers often control the backing RCG through the leaf clock they request.

## State And Persistence Behavior
The regmap is 32-bit, 4-byte-stride, fast I/O, with a maximum offset of `0x28a34`. Persistent state includes UBI32 PLL programming at `0x28000`, RCG command/source/divider registers, branch enable and halt state, divider registers, reset bits, aggregate bitmask resets, and interconnect hardware votes. Runtime PM gates access through the `"bus"` PM clock, so probe explicitly resumes before mapping and configuring the PLL.

The reset table is unusually rich. It includes block resets for CE/CLC/EIP/HAQ/IMEM/MAC/PPE/UBI/UNIPHY, individual ARES bits across grouped reset registers, UBI clamp enables, and aggregate bitmask resets such as `PPE_FULL_RESET`, `UNIPHY*_SOFT_RESET`, `UNIPHY_PORT*_ARES`, `NSSPORT*_RESET`, and `EDMA_HW_RESET`. These aggregate entries rely on `bitmask` rather than a single bit, giving reset consumers coarse-grained hardware sequences where needed.

## Dependencies And Integration Points
The driver depends on Linux CCF, runtime PM, PM clocks, interconnect provider support, regmap, Qualcomm alpha PLL, RCG, branch, divider, mux, reset, and common clock helpers. The device tree must provide compatible `qcom,ipq9574-nsscc`, a register resource, the `"bus"` clock, and parent clocks in binding order. Consumers are NSS/PPE networking drivers, Ethernet MAC and UNIPHY drivers, XGMAC PTP users, crypto/EIP and HAQ users, UBI32 firmware/core drivers, reset consumers, and interconnect clients voting NSSNOC bandwidth.

Interconnect integration exposes five NSSNOC hardware clock links: PPE, PPE CFG, NSS CSR, IMEM QSB, and IMEM AHB. The `icc_first_node_id` value is derived from `9574 * 2` to provide a unique base for the provider.

## Risks And Edge Cases
The highest risk areas are PLL configuration, reset aggregation, and port-rate tables. Incorrect UBI32 Huayra PLL parameters can break all UBI core clocks. Incorrect aggregate reset bitmasks can reset neighboring hardware unexpectedly or fail to reset all required lanes. Port 5 high-speed 312.5 MHz handling, six-port parent mapping, and XGMAC PTP dividers need per-port validation because failures can be speed-specific or only visible under timestamping tests.

Runtime PM ordering is also important. Mapping and PLL configuration are done while the device is resumed; removing that ordering can cause bus faults or ignored writes. Binding order matters for `.index` parent references. The interconnect node base must remain unique across providers, and the clock IDs referenced by `qcom_icc_hws_data` must stay synchronized with the clock table.

## Test Signals
Probe should show successful runtime PM setup, bus-clock acquisition, register mapping, UBI PLL programming, and common clock registration. Debugfs should show `ubi32_pll_main`, `ubi32_pll`, six port RX/TX trees, six XGMAC PTP references, and UBI32 branch clocks. Functional validation should cover all Ethernet ports at supported rates, PTP timestamping on XGMAC0-5, PPE/eDMA forwarding, crypto/HAQ/IMEM traffic, UBI firmware/core operation, runtime suspend/resume, and interconnect bandwidth votes. Reset validation should separately cover block resets, aggregate PPE/UNIPHY/NSSPORT resets, UBI clamp/reset controls, and EDMA reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-ipq9574.c -->

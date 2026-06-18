# Research: subset-b-001147

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-x1e80100.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-x1e80100.c

## Purpose
This file is the Qualcomm Global Clock Controller provider for the X1E80100 platform. It describes the SoC-level GCC clock, reset, and GDSC power-domain register layout for the common clock framework, covering general-purpose clocks, PCIe and tunnel/PHY clocks, UFS, SDCC, QUPv3 serial engines, USB2/USB3/USB4, video, camera, display, GPU interconnect support, and always-on infrastructure clocks.

The file is almost entirely descriptor data plus one probe routine. Its static tables bind hardware register offsets, parent mux encodings, frequency tables, branch gate behavior, reset bits, and power domains to the numeric IDs from `dt-bindings/clock/qcom,x1e80100-gcc.h`.

## Important APIs, Types, And Functions
The driver uses Qualcomm CCF helper types: `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_rcg2`, `struct clk_branch`, `struct clk_regmap_mux`, `struct clk_regmap_phy_mux`, `struct gdsc`, `struct qcom_reset_map`, `struct clk_rcg_dfs_data`, `struct regmap_config`, and `struct qcom_cc_desc`.

`gcc_gpll0`, `gcc_gpll4`, `gcc_gpll7`, `gcc_gpll8`, and `gcc_gpll9` are fixed Lucid OLE alpha PLL sources, with `gcc_gpll0_out_even` providing a post-divided parent. Parent maps combine DT-provided external clocks such as `bi_tcxo`, `sleep_clk`, PCIe pipe clocks, USB3 pipe clocks, USB4/DP/PCIe pipe GMUX clocks, QUSB4 RX clocks, and UFS symbol clocks with internal GPLL outputs.

The RCGs publish programmable clock roots for GP clocks, PCIe aux and rate-change clocks, PDM, QUPv3 wrapper serial engines, SDCC2/SDCC4, UFS AXI/ICE/PHY AUX/UNIPRO, USB2/USB3 master and mock UTMI clocks, USB3 PHY AUX, and USB4 master/PCIe pipe/sideband/TMU roots. `gcc_dfs_clocks[]` registers dynamic frequency switching metadata for every QUPv3 wrapper S0-S7 source across wrappers 0, 1, and 2. Branch descriptors expose leaf gates, many with parent links and `CLK_SET_RATE_PARENT`, and use halt modes such as normal halt, delay halt, skip halt, and voted halt depending on shared hardware behavior.

`gcc_x1e80100_gdscs[]` exports 27 power domains for PCIe tunnel/controller/PHY blocks, UFS PHY blocks, USB2/USB3/USB4 controllers, USB3 multiport PHYs, and individual USB PHY islands. `gcc_x1e80100_resets[]` exports reset controls for AV1E, camera, display, GPU, PCIe, PDM, QUPv3, QUSB2PHY, SDCC, UFS, USB2/USB3/USB4, and video blocks, including several bit-addressed USB4 miscellaneous reset lines. `gcc_x1e80100_probe()` maps the register block, registers QUP DFS RCGs, forces selected branch clocks on, clears the GDSC sleep vote auto-removal register, sets UFS force-memory-core bits, and then calls `qcom_cc_really_probe()`.

## Control Flow
The platform driver is registered at `subsys_initcall()` and matches `qcom,x1e80100-gcc`. Probe first calls `qcom_cc_map()` with `gcc_x1e80100_desc`; failure returns the mapped error before any registration. It then registers the QUPv3 DFS-capable RCG list with `qcom_cc_register_rcg_dfs()`. If DFS registration fails, the driver aborts before publishing the clock provider.

After the DFS setup, probe performs required hardware initialization: it enables camera AHB/XO, display AHB/XO, video AHB/XO, GPU CFG AHB, and a HLOS USB MMU vote branch; writes `0x0` to register `0x52224` so GDSC sleep votes are not automatically removed; and sets `FORCE_MEM_CORE_ON` for `gcc_ufs_phy_ice_core_clk` and `gcc_ufs_phy_axi_clk`. Only after these boot-time register tweaks does `qcom_cc_really_probe()` register all clocks, resets, and GDSCs with the common qcom clock framework.

Runtime control is delegated to generic qcom ops. Consumers request rates through CCF, RCG ops select parent encodings and M/N/D or HID divisors from the frequency tables, branch ops gate or ungate CBCR bits and poll halt status where appropriate, phy mux ops follow external pipe or symbol clocks, reset framework users assert/deassert BCR offsets, and genpd consumers toggle the GDSCs through the shared GDSC implementation.

## State And Persistence
The driver keeps no private dynamic state beyond registrations created by the qcom common clock core. The durable state is in GCC MMIO registers: PLL vote and status registers, RCG command/config/M/N/D registers, mux registers, branch enable and halt bits, BCR reset bits, DFS state, and GDSCR power-domain registers. Static descriptor arrays are module-lifetime state and are indexed by DT binding IDs, so sparse array indexes are part of the ABI contract.

Probe intentionally changes persistent hardware state. The always-on branch enables keep selected camera, display, video, GPU, and USB MMU paths available even before normal consumers vote for them. The sleep-vote write affects GDSC behavior across system sleep. Force-memory-core bits for UFS reduce the chance of losing UFS PHY/ICE register state while the related branches are disabled. There is no local suspend/resume save and restore; persistence relies on hardware retention, firmware expectations, GDSC retain-FF flags, and the common clock and genpd frameworks.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/qcom,x1e80100-gcc.h`, the `qcom,x1e80100-gcc` device-tree node, a GCC MMIO resource large enough for `max_register = 0x1f41f0`, external parent clocks supplied by DT indexes, and local qcom helpers for alpha PLLs, branches, RCGs, regmap muxes, phy muxes, resets, GDSCs, and DFS.

Integration points are broad: PCIe controllers and PHYs, USB2/USB3/USB4 controllers and PHY wrappers, UFS, SDCC, QUPv3 UART/I2C/SPI/QSPI engines, PDM, AV1E/video, camera, display, GPU interconnect support, NoC fabrics, RSCC, and boot ROM/QMIP support all consume IDs from this provider. The `qcom_cc_desc` is the single handoff object that exposes clocks, resets, and power domains through OF/CCF/reset/genpd registration.

## Risks And Test Signals
The main risks are descriptor drift and register-side effects. Wrong sparse indexes can expose the wrong clock, reset, or GDSC under a binding ID. Wrong parent maps can select the wrong external pipe/DP/RX/UFS symbol source. Wrong frequency-table entries can program unsupported QUP, SDCC, USB, or UFS rates. Wrong halt semantics can hang enable or disable calls, especially for voted PCIe/USB/NoC branches. The probe writes are high impact because they alter always-on clocks, sleep-vote behavior, and UFS memory retention before normal consumers run.

Useful test signals include clean probe with no missing parent clock warnings, `clk_summary` showing the expected X1E80100 GCC IDs, working QUPv3 serial engines across all three wrappers and DFS rate changes, SDCC2/SDCC4 operation, UFS link training and runtime suspend/resume, PCIe link up across the described controller lanes, USB2/USB3/USB4 enumeration including DP/pipe mux parents, video/camera/display/GPU dependent clocks staying available, reset-controller users successfully toggling BCRs, and power-domain debugfs traces showing GDSC transitions without timeout warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-x1e80100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gdsc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gdsc.c

## Purpose
This file implements Qualcomm Globally Distributed Switch Controller support as Linux generic power domains. It provides the shared runtime logic used by qcom clock-controller drivers to register GDSC descriptors, sequence power on/off, coordinate optional regulators and resets, configure retention behavior, expose genpd hardware-trigger mode, and publish onecell power-domain providers for device tree consumers.

## Important APIs, Types, And Functions
The central object is `struct gdsc` from `gdsc.h`, embedded around `struct generic_pm_domain`. `gdsc_register()` is the provider entry point called by qcom clock drivers; it allocates `genpd_onecell_data`, fetches optional supplies, initializes every GDSC, wires subdomain relationships, and calls `of_genpd_add_provider_onecell()`. `gdsc_unregister()` removes subdomains and unregisters the OF provider. `gdsc_gx_do_nothing_enable()` is exported for GPU GX domains where the CPU should enable only the parent supply and leave actual GX power-up to GMU firmware.

The low-level helpers are focused on register sequencing. `gdsc_check_status()` reads either the GDSCR, a separate hardware-control status register, or CFG_GDSCR and checks `PWR_ON_MASK`, `GDSC_POWER_UP_COMPLETE`, or `GDSC_POWER_DOWN_COMPLETE`. `gdsc_poll_status()` polls for up to `STATUS_POLL_TIMEOUT_US`. `gdsc_update_collapse_bit()` writes either an APCS collapse-vote register/mask or the GDSCR `SW_COLLAPSE_MASK`. `gdsc_toggle_logic()` performs regulator enable/disable, collapse bit writes, special votable disable delay, hardware-controller delay, and status polling.

Other helpers manage related state: reset assertion/deassertion through `reset_controller_dev`, memory/peripheral retention bits in CXC branch registers, GMEM IO clamps and AON reset, retain-FF setup, hardware-control mode, and subdomain list add/remove rollback.

## Control Flow
Registration starts in `gdsc_register()`. It allocates the onecell domain table, gets optional regulators named by each `gdsc.supply`, stores the shared `regmap` and reset controller in each descriptor, and calls `gdsc_init()` for every non-null entry. Once each domain is initialized, it adds subdomain relationships either to an explicit `gdsc.parent`, to the provider device's own PM domain, or to each parent in `desc->pd_list`. On success, it publishes the domain array to OF consumers.

`gdsc_init()` programs default transition waits, disables hardware trigger and software override, optionally forces always-on domains on, reads current hardware status, synchronizes regulator state if the domain is already on, casts a vote for already-on votable domains, enables retain-FF and hardware-control mode when requested, forces or clears memory retention bits based on current state and allowed power states, sets genpd flags and callbacks, and calls `pm_genpd_init()`.

At runtime, `gdsc_enable()` handles ON-only domains by deasserting resets. For normal domains it optionally toggles software resets, releases clamp IO, powers on through `gdsc_toggle_logic()`, forces memory retention if OFF is supported, waits for clock and memory timing, sets retain-FF, and enables hardware trigger mode when supported. `gdsc_disable()` reverses the path: it disables hardware trigger mode and waits for the domain to be on again, clears memory retention for OFF-capable domains, leaves RET+ON-only domains on because retention is entered only by parent hardware state, collapses the domain if OFF is allowed, and asserts clamp IO. `gdsc_set_hwmode()` and `gdsc_get_hwmode()` implement the genpd device hardware-mode hooks for domains flagged `HW_CTRL_TRIGGER`.

## State And Persistence
The persistent hardware state includes GDSCR bits, CFG_GDSCR power complete bits, optional separate hardware-control status, collapse-vote registers, CXC `RETAIN_MEM` and `RETAIN_PERIPH` bits, clamp and reset bits, regulator enable state, and reset-controller state. Software state is mostly static descriptor state plus devm-managed onecell arrays and optional regulator handles.

The implementation deliberately synchronizes with pre-existing hardware state during init. If firmware or another master left a domain on, the driver enables the regulator handle, votes on votable GDSCs, sets retain-FF if requested, and initializes genpd as powered. Memory retention bits are forced for domains currently on or capable of retention and cleared for fully off domains. There is no independent save/restore layer; system persistence depends on the hardware retention model and parent-domain transitions.

## Dependencies And Integration Points
This file depends on regmap MMIO access, Linux generic PM domains, OF genpd providers, reset-controller callbacks, optional regulator consumers, jiffies/ktime delay helpers, and descriptor data supplied by individual qcom clock controller drivers. It integrates with clock drivers through `gdsc_register()` and `gdsc_unregister()`, with device drivers through genpd attach APIs, with reset providers through `rcdev`, and with regulators through optional named supplies.

Subdomain support allows a GDSC to be nested under another GDSC, under the provider device's PM domain, or under a list of PM domains. That makes this code a shared integration layer between qcom clock-controller nodes and larger RPMh/genpd topology.

## Risks And Test Signals
The highest risks are sequencing and status interpretation. Polling the wrong register or bit can produce false on/off state or timeouts. Missing the 1 microsecond hardware-controller delay can read stale status. Incorrect votable handling can remove another master's vote or fail to cast a required local vote. Regulator error paths must leave supplies balanced, and subdomain rollback must remove only relationships added during the failed registration attempt. Retention and clamp flags are SoC-specific; a wrong descriptor flag can lose register context or leave IO clamped.

Useful test signals include qcom clock-controller probes successfully registering GDSCs, `/sys/kernel/debug/pm_genpd/` showing expected domains and hierarchy, domain on/off transitions without `status stuck` warnings, balanced regulator enable counts across runtime PM cycles, reset-controlled domains leaving reset on enable and entering reset on ON-only disable paths, successful hardware-mode set/get for flagged domains, and GPU recovery paths using `gdsc_gx_do_nothing_enable()` without CPU-side GX power-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gdsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gdsc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gdsc.h

## Purpose
This header defines the public descriptor contract for Qualcomm GDSC power domains. Clock-controller drivers include it to describe GDSC register offsets, allowed power states, sequencing flags, reset associations, optional supplies, and parent-domain relationships, then pass those descriptors to the implementation in `gdsc.c`.

## Important APIs, Types, And Functions
`struct gdsc` is the key type. It embeds `struct generic_pm_domain pd`, stores an optional parent domain, a regmap pointer, GDSCR and collapse-vote register offsets, optional hardware-control and clamp-IO registers, CXC register lists for retention bits, transition wait values, allowed power states, flags, reset-controller data, reset IDs, and optional regulator supply names and handles.

The power-state bitfields are `PWRSTS_OFF`, `PWRSTS_RET`, `PWRSTS_ON`, plus combined `PWRSTS_OFF_ON` and `PWRSTS_RET_ON`. The header documents that software cannot directly enter `PWRSTS_RET`; retention is reached by hardware when the parent domain enters a low-power state. Flags include `VOTABLE`, `CLAMP_IO`, `HW_CTRL`, `SW_RESET`, `AON_RESET`, `POLL_CFG_GDSCR`, `ALWAYS_ON`, `RETAIN_FF_ENABLE`, `NO_RET_PERIPH`, and `HW_CTRL_TRIGGER`.

`struct gdsc_desc` bundles a provider device, a sparse array of GDSC pointers, its size, and an optional parent PM-domain list. Public functions are `gdsc_register()`, `gdsc_unregister()`, and `gdsc_gx_do_nothing_enable()` when `CONFIG_QCOM_GDSC` is enabled. Stub inline definitions return `-ENOSYS` or no-op unregister when the config is disabled.

## Control Flow
The header itself has no runtime control flow, but it defines how callers drive the implementation. A clock controller declares static `struct gdsc` instances, places pointers in an ID-indexed array, fills a `struct gdsc_desc`, and lets qcom common clock code call `gdsc_register()`. The implementation then fills runtime-only fields such as `regmap`, `rcdev`, and `rsupply`, initializes each `generic_pm_domain`, and publishes the onecell provider.

## State And Persistence
Descriptor fields are static configuration. Runtime state is attached by `gdsc.c`: `regmap`, `rcdev`, optional regulator handles, genpd state, and subdomain registration. The important persistence semantics are encoded in `pwrsts` and flags. `PWRSTS_RET_ON`, `RETAIN_FF_ENABLE`, `NO_RET_PERIPH`, and CXC lists determine whether hardware state is expected to survive low-power transitions or be fully collapsed.

## Dependencies And Integration Points
The header depends on Linux PM domain types and forward declarations for regmap, regulator, and reset controllers. It is consumed by many qcom clock-controller drivers and by the qcom common clock registration path. Device-tree integration is indirect: sparse GDSC arrays indexed by dt-binding IDs become OF genpd onecell domains.

## Risks And Test Signals
The main risk is descriptor misuse. Wrong `pwrsts` can make genpd leave a domain on when software expects off, or collapse hardware that only supports retention. Wrong flags can poll the wrong register, skip needed reset/clamp sequencing, or enable hardware-control mode at the wrong time. Wrong `reset_count`, `resets`, or CXC lists can corrupt unrelated registers. Build coverage should include both `CONFIG_QCOM_GDSC=y/m` and disabled stub paths. Runtime signals are successful qcom clock-controller probe, correct genpd domain names and indexes, and expected power/retention behavior under runtime PM and system sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gdsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-glymur.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-glymur.c

## Purpose
This file is the Qualcomm GPU Clock Controller provider for the Glymur platform. It publishes GPU-specific PLL, RCG, divider, branch, reset, and CX GDSC resources used by the GPU, GMU, hub, SMMU vote path, RSCC, and fast-frequency support.

## Important APIs, Types, And Functions
The driver uses `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct qcom_cc_driver_data`, and `struct qcom_cc_desc`. `gpu_cc_pll0` is a Taycan EKO T alpha PLL configured for 1150 MHz from `bi_tcxo`; `gpu_cc_pll0_out_even` exposes a divide-by-2 postdiv path. Parent maps cover DT-provided `bi_tcxo`, `gpll0_out_main`, `gpll0_out_main_div`, and internal PLL0 main/even/odd references.

The RCGs are `gpu_cc_ff_clk_src` fixed at 200 MHz from GPLL0, `gpu_cc_gmu_clk_src` with XO and high GPU PLL-derived rates from 575 to 750 MHz, and `gpu_cc_hub_clk_src` at 200/300/400 MHz. `gpu_cc_hub_div_clk_src` is a read-only divider below the hub root. Branches publish AHB, CX/GX accu-shift, CX fast-frequency, CX/GX GMU, CXO, DEMET, DPM, frequency measurement, GPU SMMU vote, GX ACD/AHB/RCG fast-frequency, hub AON, hub CX internal, MEMNOC GFX, RSCC hub AON, and sleep clocks.

`gpu_cc_cx_gdsc` describes the GPU CX power domain at GDSCR `0x9080`, with separate hardware-control status at `0x9094`, OFF/ON support, `POLL_CFG_GDSCR`, and `RETAIN_FF_ENABLE`. `gpu_cc_glymur_resets[]` provides CB, CX, fast hub, FF, GMU, GX, and XO resets. `gpu_cc_glymur_driver_data` asks common qcom code to configure the alpha PLL and mark critical CBCRs at `0x93a4`, `0x9008`, and `0x9004`.

## Control Flow
The module registers a normal platform driver matching `qcom,glymur-gpucc`. Probe is a thin wrapper around `qcom_cc_probe(pdev, &gpu_cc_glymur_desc)`. The common qcom path maps the GPUCC MMIO range, configures PLLs and critical CBCRs from driver data, registers CCF clocks, exposes resets, and registers the CX GDSC.

Runtime control is table-driven. GPU/GMU consumers set rates on the GMU and hub RCGs; branch ops gate leaves and poll or delay according to each halt mode; the read-only divider reflects hardware hub division; reset users toggle the GPUCC BCR offsets; and the GDSC framework controls the CX power domain with retain-FF handling.

## State And Persistence
Persistent state lives in GPUCC registers up to `max_register = 0x95e8`: PLL configuration/status, RCG command/config registers, divider state, branch enable/halt bits, reset bits, critical CBCR bits, and GDSC power/retention bits. The driver holds static descriptors only. `use_rpm = true` indicates the qcom common registration must integrate RPM-aware behavior for this controller.

Critical CBCRs and AON branch ops are persistence-sensitive because they keep low-level XO/RSCC/hub paths available while other GPU clocks are gated. The CX GDSC uses retain-FF to preserve flip-flop state across domain transitions. There is no explicit suspend/resume code in the file; runtime PM and sleep behavior depend on CCF, RPM integration, the GDSC core, GMU firmware, and hardware retention.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/qcom,glymur-gpucc.h`, the `qcom,glymur-gpucc` device-tree node, DT parent clock indexes for XO and GPLL0 inputs, and qcom helpers for alpha PLLs, branches, RCGs, regmap dividers, GDSCs, resets, and common provider registration.

Consumers include the Adreno GPU and GMU, GPU SMMU, MEMNOC/DDR fabric paths, RSCC, DPM/frequency measurement logic, and recovery/reset paths for CX/GX/GMU/fast-hub blocks. The descriptor exposes both clock IDs and reset IDs to those drivers.

## Risks And Test Signals
Risks center on GPU timing and shared ownership. A bad PLL0 configuration or GMU frequency table can destabilize the GMU. A wrong critical CBCR can break low-power entry or wake. A wrong voted halt mode can disable a path still needed by RPM, GMU, SMMU, or firmware. The CX GDSC flags and status register must match hardware or genpd can time out or lose retained state.

Useful test signals include clean probe with configured PLL0 rate, `clk_summary` entries for GMU/hub/FF branches, successful GPU driver attach and GMU boot, GPU frequency changes across listed GMU rates, SMMU vote clock behavior during GPU activity, reset controls working during GPU recovery, CX GDSC transitions without timeout warnings, and suspend/resume retaining critical GPUCC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-glymur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-kaanapali.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-kaanapali.c

## Purpose
This file is the Qualcomm GPU Clock Controller provider for the Kaanapali platform. It publishes the GPUCC PLL, GMU and hub RCGs, branch clocks, reset controls, and CX GDSC needed by the platform GPU and GMU stack.

## Important APIs, Types, And Functions
The driver uses the same qcom CCF primitives as the Glymur GPUCC driver: `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. `gpu_cc_pll0` is a Taycan EKO T alpha PLL configured for 950 MHz from `bi_tcxo`, with `cal_l = 0x48`; `gpu_cc_pll0_out_even` provides the divide-by-2 postdiv.

One parent map combines DT-provided XO/GPLL0 parents and internal PLL0 main/even/odd outputs. `gpu_cc_gmu_clk_src` supports XO plus 475, 575, 700, 725, and 750 MHz PLL-derived rates and has `hw_clk_ctrl = true`. `gpu_cc_hub_clk_src` supports 150, 200, 300, and 400 MHz and also has `hw_clk_ctrl = true`. `gpu_cc_hub_div_clk_src` is a read-only divider.

The branch set is smaller than Glymur: AHB, CX accu-shift, CX GMU, CXO, DEMET, DPM, frequency measurement, GPU SMMU vote, GX accu-shift, GX GMU, hub AON, hub CX internal, and MEMNOC GFX. `gpu_cc_cx_gdsc` uses GDSCR `0x9080`, hardware-control/status `0x9094`, OFF/ON states, `POLL_CFG_GDSCR`, and `RETAIN_FF_ENABLE`, with a shorter `clk_dis_wait_val` of `0x8`. The reset map covers CB, CX, fast hub, FF, GMU, GX, and XO BCRs. Critical CBCRs are `GPU_CC_CXO_AON_CLK`, `GPU_CC_RSCC_HUB_AON_CLK`, and `GPU_CC_RSCC_XO_AON_CLK`.

## Control Flow
The module platform driver matches `qcom,kaanapali-gpucc`, and probe simply calls `qcom_cc_probe()` with `gpu_cc_kaanapali_desc`. The common qcom path maps the register range, configures PLL0 using the driver-data alpha PLL list, enables/marks the critical CBCRs, registers the clock array by dt-binding IDs, exposes the reset controller entries, and registers the single CX GDSC.

At runtime, GPU and GMU drivers request rate changes on the GMU and hub roots, branch ops gate and ungate leaves according to halt semantics, the read-only divider reflects existing hub division, reset consumers toggle BCRs, and genpd controls the CX GDSC. The two RCGs with `hw_clk_ctrl = true` are prepared for hardware-assisted clock control while still exposing software rate selection through the common RCG ops.

## State And Persistence
Hardware state is stored in GPUCC registers up to `max_register = 0x95e8`: PLL0 configuration and status, postdivider state, RCG command/config registers, branch enable and halt bits, reset bits, critical CBCR state, and CX GDSC retain/power bits. Software state is static descriptor data plus qcom common clock registration state.

Critical AON/RSCC clocks and retain-FF on the CX GDSC are the main persistence mechanisms in this file. There is no file-local suspend/resume path, so GPU low-power behavior is coordinated by CCF, RPM-aware qcom common code (`use_rpm = true`), the GDSC core, and GPU/GMU firmware.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/qcom,kaanapali-gpucc.h`, a `qcom,kaanapali-gpucc` DT node, DT parent clock indexes for `bi_tcxo`, `gpll0_out_main`, and `gpll0_out_main_div`, and local qcom clock, reset, GDSC, and common registration helpers.

Consumers are the Kaanapali GPU/GMU driver stack, GPU SMMU, MEMNOC graphics path, DPM/frequency measurement logic, RSCC/AON infrastructure, and GPU reset/recovery paths. The descriptor bridges those consumers to CCF clock IDs, reset IDs, and a genpd CX power-domain ID.

## Risks And Test Signals
The key risks are SoC-specific table differences. Kaanapali uses a lower PLL0 configuration than Glymur, includes a 475 MHz GMU rate, omits Glymur's fast-frequency branches, uses `hw_clk_ctrl` on GMU and hub RCGs, and has a different CX GDSC clock-disable wait value. Copying Glymur values into this file would expose unsupported clocks or incorrect rates. Wrong critical CBCRs can break AON/RSCC behavior, and wrong GDSC flags can cause power-domain timeouts or context loss.

Useful test signals include clean probe, PLL0 configured near 950 MHz, `clk_summary` showing only Kaanapali binding IDs, GPU/GMU boot, successful GMU rate changes including 475 MHz, stable hub rates at 150/200/300/400 MHz, SMMU vote activity during GPU use, reset controls working during recovery, CX GDSC on/off transitions without warnings, and system suspend/resume with AON GPUCC clocks intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-kaanapali.c -->

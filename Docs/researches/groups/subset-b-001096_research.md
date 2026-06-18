# Research: subset-b-001096

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx7d.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx7d.c

## Purpose
This file is the early boot clock provider for the i.MX7D CCM. It describes the SoC clock tree from external inputs through anatop PLLs, PFDs, root muxes, pre/post dividers, and CCGR-style gates, then publishes the clocks through a `clk_hw_onecell_data` provider for device tree consumers.

## Important APIs, Types, And Functions
The only function is `imx7d_clocks_init()`, registered with `CLK_OF_DECLARE(imx7d, "fsl,imx7d-ccm", ...)`. It allocates the onecell hardware array with `kzalloc_flex()`, resolves input clocks with `imx_get_clk_hw_by_name()`, maps anatop and CCM registers with `of_iomap()`, and registers clocks with i.MX helpers from `clk.h`: `imx_clk_hw_pllv3()`, `imx_clk_hw_pfd()`, `imx_clk_hw_mux2[_flags]()`, `imx_clk_hw_gate[2/3/4]()`, `imx_clk_hw_divider2()`, `imx_clk_hw_cpu()`, and shared/exclusive gate helpers. Static parent-name arrays define every root source selector. `test_div_table` and `post_div_table` model non-linear PLL divider encodings.

## Control Flow
Initialization first publishes dummy, oscillator, and CKIL entries, then maps `fsl,imx7d-anatop` and builds PLL bypass sources, PLL cores, bypass muxes, output gates, audio/video/DRAM post dividers, system PFDs, fixed-factor system/DRAM/ENET derived outputs, and the LVDS output selector. It then maps the CCM node and builds root source muxes, root gates, pre-dividers, post-dividers, and leaf gates for CPU, bus, DRAM, display, MIPI, PCIe, ENET, SAI/SPDIF, storage, I2C, UART, SPI, PWM, timers, watchdogs, USB, and ADC. After `imx_check_clk_hws()`, it registers the provider, forces PLL bypass parents to their PLLs, selects specific MIPI CSI and GPT parents, registers fixed USB PLL factors late, and calls `imx_register_uart_clocks()`.

## State And Persistence
The persistent state is the global `clk_hw_data`, `hws`, and shared gate counters for SAI1-3, NAND, and ENET1/2. Hardware register state lives in CCM/anatop MMIO and is not saved/restored here; this is an early init provider, not a removable platform driver. Several clocks are marked `CLK_IS_CRITICAL`, notably core system, IPG, AXI, and DRAM paths, so common clock framework disable paths should not shut them off.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/imx7d-clock.h` IDs matching the `hws[]` indexes, device tree nodes `fsl,imx7d-ccm` and `fsl,imx7d-anatop`, external input names such as `osc`, `ckil`, and `ext_clk_*`, and the i.MX clock helper library. Consumers bind through the OF clock provider and numeric DT clock specifiers. CPU frequency integration uses `imx_clk_hw_cpu()` with ARM root, ARM PLL, and system PLL clocks.

## Risks And Test Signals
Risks are mostly register-map drift and parent/index mismatch: a wrong offset or selector string can silently feed devices from the wrong PLL, while missing critical flags can stop DRAM, AXI, or IPG. Shared gates for SAI, NAND, and ENET must keep shared CCGR bits enabled until all users release them. Late USB fixed factors mean USB PHY consumers depend on correct naming. Test signals include boot on i.MX7D with no `imx_check_clk_hws()` warnings, populated `/sys/kernel/debug/clk/clk_summary`, working CPU frequency changes, UART console, USDHC/NAND/QSPI, ENET PTP/reference clocks, audio SAI clocks, display/MIPI paths, suspend/resume smoke tests, and absence of unexpected critical clock disables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx7d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx7ulp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx7ulp.c

## Purpose
This file registers the i.MX7ULP clock domains exposed by separate SCG1, PCC2, PCC3, and SMC1 device tree nodes. It covers system PLL/PFD generation, system/core/NIC/DDR roots, peripheral clock controller gates and composites, and the SMC ARM core selector.

## Important APIs, Types, And Functions
Four early init functions are declared with `CLK_OF_DECLARE()`: `imx7ulp_clk_scg1_init()`, `imx7ulp_clk_pcc2_init()`, `imx7ulp_clk_pcc3_init()`, and `imx7ulp_clk_smc1_init()`. Each allocates `struct clk_hw_onecell_data` with `kzalloc_flex()`, maps its node with `of_iomap()`, fills `hws[]`, validates with `imx_check_clk_hws()`, and registers `of_clk_hw_onecell_get`. The SCG path uses `imx_clk_hw_pllv4()`, `imx_clk_hw_pfdv2()`, mux, divider, divider-gate, and `imx_clk_hw_cpu()` helpers. PCC paths use `imx7ulp_clk_hw_composite()` plus simple gates. `ulp_div_table` defines the 1/2/4/8/16/32/64 divider encoding used by SCG bus dividers.

## Control Flow
SCG1 initialization resolves root inputs `rosc`, `sosc`, `sirc`, `firc`, and `upll`; configures APLL/SPLL pre-selectors and pre-dividers; registers APLL/SPLL and their PFDs; registers PLL/PFD selectors; creates SPLL, system, high-speed-run system, DDR, NIC, GPU, SOSC bus, and FIRC bus clocks. PCC2 then publishes DMA, GPIO, CAAM, timers, LPSPI, LPI2C, LPUART, FlexIO, USB, USDHC, watchdog, and USB PHY clocks. PCC3 publishes additional timers, MMDC, LPI2C/LPUART, DSI/LCDIF, VIU, pin controllers, and GPU2D/3D clocks. SMC1 only exposes the ARM mux selecting normal or HSRUN core parents.

## State And Persistence
There is no remove path or explicit suspend state. Each node owns a separate onecell provider allocated for boot lifetime. Hardware programming is persistent in SCG/PCC/SMC MMIO. Critical flags protect DDR and NIC clocks, and MMDC is registered as a critical gate because memory controller access must remain clocked.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx7ulp-clock.h`, node compatibles `fsl,imx7ulp-scg1`, `fsl,imx7ulp-pcc2`, `fsl,imx7ulp-pcc3`, and `fsl,imx7ulp-smc1`, and firmware/device-tree supplied clock names. PCC composites depend on the i.MX7ULP-specific composite helper's interpretation of PCC register fields. UART aliases are registered after PCC2/PCC3 setup through `imx_register_uart_clocks()`.

## Risks And Test Signals
Risk centers on split-provider ordering: PCC consumers depend on SCG roots such as `nic1_clk`, `nic1_bus_clk`, and PLL/PFD outputs already being registered. PLL configuration is marked as not safely changeable while enabled, so reparent/rate operations must respect gate flags. Test signals include successful boot with all four providers, stable DDR/NIC operation, UART console on LPUART4-7, USB/USDHC/CAAM/timer devices probing, GPU/display clocks when present, no missing-clock warnings, and clk-summary rates matching SCG/PCC register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx7ulp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8-acm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8-acm.c

## Purpose
This platform driver exposes the i.MX8 Audio Clock Mux (ACM) registers as common-clock muxes for i.MX8QM, i.MX8QXP, and i.MX8DXL. It routes audio recovery clocks, external MCLKs, SAI/ESAI/SPDIF bit clocks, PLL dividers, ASRC muxes, and MCLK outputs for ADMA audio peripherals.

## Important APIs, Types, And Functions
`struct clk_imx8_acm_sel` describes one ACM mux: clock name, DT ID, parent table, register offset, shift, and width. `struct imx8_acm_soc_data` selects the SoC-specific mux list and mutable MCLK parent table. `struct imx8_acm_priv` stores power-domain attachments, SoC data, base address, and saved registers. `imx8_acm_clk_probe()` maps registers, attaches multiple PM domains, enables runtime PM, registers muxes with `devm_clk_hw_register_mux_parent_data_table()`, patches MCLK parent entries to point at the earlier `acm_aud_clk0_sel` and `acm_aud_clk1_sel` clocks, and registers the onecell provider. `clk_imx_acm_attach_pm_domains()` and `_detach_pm_domains()` manage additional power domains and stateless runtime-PM device links.

## Control Flow
Probe obtains the OF match data, maps the ACM resource, allocates private and onecell state, attaches all listed power domains when more than one exists, powers the block with runtime PM, and iterates over the SoC mux table. The first two audio selector muxes are registered before downstream MCLK muxes; once registered, their `clk_hw` pointers are inserted into the SoC MCLK parent data so child muxes can use them as parents. On success, `devm_of_clk_add_hw_provider()` publishes all ACM clocks, then runtime PM releases the device. Error paths drop runtime PM and detach domains.

## State And Persistence
Clock state is stored in hardware ACM mux registers. Runtime suspend saves every mux register listed by `soc_data->sels` into `priv->regs[]`; runtime resume writes them back. Power-domain device links persist for driver lifetime and are explicitly removed in remove/error paths. The parent tables for MCLK selectors are static mutable data patched at probe time, so each SoC data instance assumes one driver instance per compatible.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx8-clock.h`, OF compatibles `fsl,imx8qm-acm`, `fsl,imx8qxp-acm`, and `fsl,imx8dxl-acm`, named firmware clocks in `clk_parent_data.fw_name`, optional dummy or unavailable `.index = -1` parent slots, genpd power domains, runtime PM, and the common clock framework. Audio drivers consume the exported `IMX_ADMA_ACM_*` clock IDs to select SAI/ESAI/SPDIF/MQS master clocks.

## Risks And Test Signals
The main risks are parent-table order mismatches with hardware selectors, static MCLK parent mutation in multi-instance scenarios, missing power-domain links causing register access while unpowered, and suspend/resume restoring stale mux values after firmware changes. Test signals include successful ACM probe on each compatible, no `devm_clk_hw_register_mux_parent_data_table()` errors, audio playback/capture across SAI/ESAI/SPDIF/MQS, MCLK parent switching through clk APIs, runtime PM suspend/resume preserving selected parents, and genpd traces showing all ACM domains active during register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8-acm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8dxl-rsrc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8dxl-rsrc.c

## Purpose
This file provides the i.MX8DXL SCU clock resource allowlist used by the SCU-backed i.MX clock driver. It enumerates the SCFW resource IDs for peripherals whose clocks may be exposed through the SCU clock framework on i.MX8DXL.

## Important APIs, Types, And Functions
The only exported object is `const struct imx_clk_scu_rsrc_table imx_clk_scu_rsrc_imx8dxl`, which points to `imx8dxl_clk_scu_rsrc_table` and its `ARRAY_SIZE()`. The resource IDs come from `dt-bindings/firmware/imx/rsrc.h`, while `struct imx_clk_scu_rsrc_table` is declared by `clk-scu.h`.

## Control Flow
There is no executable control flow in this file. At link/runtime, the SCU clock driver selects this table for i.MX8DXL and uses it to decide which SCU resources to register or query. The comment requires the table to stay sorted in ascending order, which matters if consumers perform ordered lookups.

## State And Persistence
The table is static read-only data after initialization. It does not cache SCU responses or own any hardware state. Persistent clock state remains in the system controller firmware and the broader SCU clock framework.

## Dependencies And Integration Points
This table integrates with the SCFW resource namespace and the i.MX SCU clock provider. It lists SPI, UART, I2C, ADC, FTM, CAN, LCD/PWM, GPT, FSPI, SDHC, ENET, USB, NAND, M4, display PLL, audio PLL, audio clock, and A35 resources available for i.MX8DXL clock handling.

## Risks And Test Signals
Risks are omission, stale resource IDs, or losing sorted order. Missing resources prevent downstream clocks from appearing; extra resources can cause SCU calls to unavailable hardware. Test signals include SCU clock probe on i.MX8DXL without invalid-resource errors, expected peripherals receiving clocks, and any table-search self-checks or debug logs confirming resource lookup coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8dxl-rsrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mm.c

## Purpose
This platform driver registers the i.MX8M Mini CCM clock tree. It publishes external inputs, anatop PLLs, fixed PLL outputs, root composites for CPU/bus/peripheral domains, CCGR leaf gates, shared gates, DRAM firmware-managed roots, and an ARM CPU clock provider.

## Important APIs, Types, And Functions
`imx8mm_clocks_probe()` is the only probe function and is bound by the `fsl,imx8mm-ccm` match table. It uses global `clk_hw_data` and `hws`, allocates a onecell provider with `kzalloc_flex()`, maps the anatop node with `of_find_compatible_node()`/`of_iomap()`, maps the CCM resource with `devm_platform_ioremap_resource()`, and registers clocks with `imx_clk_hw_pll14xx()`, `imx8m_clk_hw_composite*()`, `imx_clk_hw_gate4()`, shared gate helpers, and `imx_clk_hw_cpu()`. Parent-name arrays define all mux choices for A53, M4, VPU, GPU, AXI/AHB/NOC, display, PCIe, CSI, SAI, SPDIF, ENET, storage, serial, USB, GIC, and PDM domains.

## Control Flow
Probe first registers dummy/external clocks and anatop PLL roots: audio/video/DRAM/GPU/VPU/ARM/sys_pll3, bypass muxes, output gates, fixed SYS PLL1 and SYS PLL2 derived rates, and CLKOUT mux/div/gates. It then switches to the CCM base and builds core composites, backwards-compatible aliases for old source/gate/div IDs, the A53 core mux, bus composites, IPG dividers, firmware-managed DRAM clocks, all peripheral root composites, CCGR gates, shared NAND/SAI/PDM/display gates, fixed GPT 3 MHz and DRAM alternate roots, DRAM core mux, and the CPU clock. It validates with `imx_check_clk_hws()`, registers the provider, then registers UART lookup clocks.

## State And Persistence
The driver has no remove path for clocks and suppresses bind attributes to prevent unbind/rebind crashes. Clock state is in hardware registers, with global `hws` used by helper and debug paths. Shared counters protect CCGR bits shared by SAI root/IPG pairs, PDM root/IPG, NAND root/bus, and display subclocks. DRAM alternate/APB clocks are marked firmware-managed because TF-A changes DRAM clocks outside the Linux clock framework.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx8mm-clock.h`, `fsl,imx8mm-anatop`, `fsl,imx8mm-ccm`, input clock names (`osc_24m`, `osc_32k`, `clk_ext1-4`), i.MX8M composite helpers, PLL14xx data, and the common clock framework. Consumers use DT clock IDs. `mcore_booted` is exposed as a module parameter shared by i.MX code paths.

## Risks And Test Signals
Risks include incorrect PLL parent/bypass setup, mismatched old alias IDs, missing critical flags for NOC/AHB/GIC/DRAM, unsafe Linux control of firmware-managed DRAM clocks, and shared-gate underflow disabling a block still in use. Test signals include successful i.MX8MM boot, no missing clocks in `imx_check_clk_hws()`, clk-summary coverage of all IMX8MM IDs, CPUfreq changes, DRAM stability with TF-A, display/CSI/VPU/GPU/PCIe/USB/ENET/USDHC/audio peripheral probes, and failed provider-registration paths unregistering already created hardware clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mn.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mn.c

## Purpose
This platform driver registers the i.MX8M Nano CCM clock tree. It is structurally similar to the i.MX8MM provider but adjusted for Nano hardware: M7 instead of M4 naming, GPU core/shader clocks, a reduced/changed multimedia set, SAI2/3/5/6/7, six GPTs, camera/display pixel roots, and Nano-specific PLL names.

## Important APIs, Types, And Functions
`imx8mn_clocks_probe()` is bound to `fsl,imx8mn-ccm`. It allocates `struct clk_hw_onecell_data` with `devm_kzalloc()`, fills global `hws`, maps `fsl,imx8mn-anatop` with `devm_of_iomap()`, maps the CCM resource, and registers PLL14xx, fixed-factor, composite, gate, shared gate, and CPU clocks. It uses `imx8m_clk_hw_fw_managed_composite()` for DRAM paths, `imx8m_clk_hw_composite_bus_critical()` for key buses, and `imx_clk_hw_cpu()` for the ARM clock.

## Control Flow
Probe creates dummy/external clocks, registers audio/video/DRAM/GPU/M7_ALT/ARM/SYS_PLL3 PLLs and bypass/output gates, derives fixed SYS_PLL1/2 rates, and creates CLKOUT1/2. It then registers core composites for A53, M7, GPU core, and GPU shader, aliases GPU source/gate/div IDs to the composite hardware, creates the A53 core selector, bus and AHB/audio roots, IPG dividers, critical DRAM core mux, firmware-managed DRAM alt/APB clocks, peripheral composites, CCGR gates, shared NAND/SAI/PDM/display gates, fixed GPT 3 MHz and DRAM alternate roots, and the CPU clock. It validates, publishes the provider, and registers UART clocks.

## State And Persistence
Clock state persists in anatop/CCM registers. Global `clk_hw_data`/`hws` live for the module lifetime, and bind attributes are suppressed to avoid unbinding a provider whose clocks are in use. Shared counters guard SAI root/IPG pairs, SAI7, PDM, display/camera pixel group, and NAND. DRAM alt/APB clocks are firmware-managed because TF-A may alter them outside Linux.

## Dependencies And Integration Points
Dependencies are `dt-bindings/clock/imx8mn-clock.h`, compatibles `fsl,imx8mn-anatop` and `fsl,imx8mn-ccm`, external clock names, PLL14xx definitions, and the i.MX8M composite helper API. Device drivers consume the exported onecell clock IDs for display, camera, GPU, USB, ENET, USDHC, serial, timers, PDM, SAI, and watchdog clocks.

## Risks And Test Signals
Risks include accidental carryover from i.MX8MM where Nano lacks a block, wrong shared display gate semantics because camera and display pixel roots share one CCGR bit, missing critical handling for NOC/AHB/GIC/DRAM, and firmware-managed DRAM rate caching errors. Test signals include i.MX8MN boot with clean clock warnings, working CPUfreq, GPU/display/camera/USB/ENET/USDHC/audio probing, six GPT roots visible, shared SAI/PDM gates surviving simultaneous audio users, suspend/resume smoke tests, and clk-summary rates matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mp-audiomix.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mp-audiomix.c

## Purpose
This platform driver exposes the i.MX8MP Audio BLK_CTRL clock and reset-facing registers. It registers audio block gates, SAI MCLK selectors, PDM selector, an audio SAI PLL, its bypass/output/div2 clocks, optional auxiliary reset controller, and runtime PM save/restore for the audio block registers.

## Important APIs, Types, And Functions
`struct clk_imx8mp_audiomix_sel` models either a gate with one parent or a mux with parent data. `struct clk_imx8mp_audiomix_priv` stores the MMIO base, saved register values, and trailing onecell clock data. Macros `CLK_GATE`, `CLK_GATE_PARENT`, `CLK_PDM`, and `CLK_SAIn()` generate the table entries for gates and SAI MCLK mux/gate groups. `clk_imx8mp_audiomix_probe()` allocates `priv`, maps registers, enables runtime PM before registering clocks, iterates `sels[]`, registers the SAI PLL path, publishes the provider, and creates an auxiliary reset device if `#reset-cells` is present. Runtime suspend/resume call `clk_imx8mp_audiomix_save_restore()`.

## Control Flow
Probe makes the block active with `pm_runtime_get_noresume()`, `pm_runtime_set_active()`, and `pm_runtime_enable()` so clock registration can safely access runtime-PM-aware parents. It registers each table entry as either `devm_clk_hw_register_gate_parent_data()` or `devm_clk_hw_register_mux_parent_data_table()`. It then registers `sai_pll_ref_sel`, the PLL14xx `sai_pll`, `sai_pll_bypass`, `sai_pll_out`, and fixed-factor `sai_pll_out_div2`, publishes `of_clk_hw_onecell_get`, optionally registers reset support, and drops the runtime PM reference. Error paths disable runtime PM.

## State And Persistence
The driver saves `CLKEN0/1`, EARC, SAI MCLK selectors, PDM selector, SAI PLL registers, and `IPG_LP_CTRL` into `regs_save[]` during runtime suspend and restores them on resume. The onecell data is embedded in the private allocation for driver lifetime. Gate state is hardware-backed in Audio BLK_CTRL registers. Reset support is delegated to an auxiliary device.

## Dependencies And Integration Points
Dependencies include `dt-bindings/clock/imx8mp-clock.h`, compatible `fsl,imx8mp-audio-blk-ctrl`, parent clocks from the main CCM and audio sources (`ahb`, `axi`, `sai*`, `sai*_mclk`, `pdm`, `spdif_extclk`, `osc_24m`), PLL14xx support, runtime PM, optional reset-controller support through the auxiliary bus, and OF clock provider registration. Audio, DSP, SDMA/eDMA, EARC, PDM, SAI, and MQS users consume these clocks.

## Risks And Test Signals
Risks include registering clocks before runtime PM is active, wrong table-generated register bit positions, incomplete save/restore across low-power audio suspend, optional reset-controller mismatch, and parent-name mismatches between main CCM and audiomix. Test signals include probe on `fsl,imx8mp-audio-blk-ctrl`, clock summary entries for SAI/PDM/PLL gates, audio playback/capture across SAI1/2/3/5/6/7, PDM and EARC operation, runtime suspend/resume preserving muxes and PLL settings, and reset auxiliary device creation when `#reset-cells` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mp-audiomix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mp.c

## Purpose
This platform driver registers the main i.MX8M Plus CCM clock provider. It defines the full PLL, bus, peripheral, media, HDMI, GPU/NPU/VPU, audio, storage, network, USB, and CPU clock tree and applies datasheet-derived maximum rate constraints based on common and operating-mode-specific limits.

## Important APIs, Types, And Functions
`imx8mp_clocks_probe()` is the main entry point for `fsl,imx8mp-ccm`. It maps anatop and CCM resources, allocates a onecell provider, registers PLL14xx clocks, bypass muxes, fixed-factor outputs, i.MX8M composites, gates, shared gates, DRAM firmware-managed clocks, and the CPU clock. `struct imx8mp_clock_constraints` plus `imx8mp_clock_common_constraints`, `imx8mp_clock_nominal_constraints`, and `imx8mp_clock_overdrive_constraints` define maximum rates; `imx8mp_clocks_apply_constraints()` applies them with `clk_hw_set_rate_range()`. The driver publishes clocks with `of_clk_add_hw_provider()` and suppresses unbind through the platform driver.

## Control Flow
Probe maps `fsl,imx8mp-anatop` and the CCM resource, creates dummy/external clocks, registers audio/video/DRAM/GPU/VPU/ARM/SYS_PLL1/2/3 PLLs, bypass selectors, output gates, SYS PLL fixed-factor rates, and CLKOUT clocks. It then creates A53, M7, ML, GPU, audio, HSIO, media, bus, NOC, AHB, MIPI, DRAM, VPU, CAN, PCIe, I2C, SAI, ENET, NAND/QSPI/USDHC, UART, USB, GIC, ECSPI, PWM, GPT, watchdog, HDMI, camera, display, LDB, memrepair, PDM, and SAI7 composites and gates. Shared gate counters cover NAND, USB, media, and audio root groups. After validation, it applies common constraints, optionally applies `fsl,operating-mode = "nominal"` or `"overdrive"` constraints, registers the provider, and registers UART clocks.

## State And Persistence
Hardware state persists in anatop and CCM registers. Global `clk_hw_data` and `hws` are retained for the module lifetime. No suspend save/restore is implemented here; the clock framework and hardware retain state, while DRAM alt/APB roots are firmware-managed because TF-A can change DRAM clocks. Rate-range constraints persist in the common clock framework once applied. Critical clocks protect DRAM, NOC, AHB, GIC, memrepair, and related roots from disable/rate misuse.

## Dependencies And Integration Points
Dependencies include `dt-bindings/clock/imx8mp-clock.h`, `linux/units.h` for `HZ_PER_MHZ`, `fsl,imx8mp-anatop`, `fsl,imx8mp-ccm`, external input names, PLL14xx data, i.MX8M composite helpers, and the common clock framework. Consumers include CPUfreq, GPU/NPU/VPU/media/HDMI/display, audio/audiomix, ENET/ENET_QOS, PCIe, USB, USDHC, QSPI/NAND, CAN, I2C, UART, PWM, GPT, watchdog, and thermal/sensor blocks. The audio block driver depends on many parent clocks exported here.

## Risks And Test Signals
Risks are higher than the other table drivers because rate constraints affect runtime `clk_set_rate()` behavior. Wrong limits can cap performance or permit unsafe overclocking. Other risks include mismatched operating-mode property handling, missing critical flags, shared gate counters disabling grouped media/audio/USB clocks too early, firmware-managed DRAM conflicts, and parent-name mismatches with the audiomix driver. Test signals include clean boot with no missing clock IDs, correct provider registration, clk-summary coverage, CPUfreq and OPP operation in nominal/overdrive modes, `clk_hw_set_rate_range()` limiting affected clocks, stable DRAM under TF-A management, and functional HDMI/media/camera/GPU/NPU/VPU/audio/USB/PCIe/ENET/USDHC/QSPI/NAND/CAN/serial peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mp.c -->

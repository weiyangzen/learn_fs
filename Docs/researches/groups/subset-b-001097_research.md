# subset-b-001097 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mq.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mq.c

## Purpose
Registers the i.MX8MQ CCM clock tree. It exposes oscillator inputs, ANATOP PLLs, SSCG PLLs, fixed PLL derivatives, composite core/bus/IP roots, CCGR-style gates, monitor outputs, and the CPU clock to the common clock framework through the `fsl,imx8mq-ccm` provider.

## Important APIs, Types, And Functions
The main entry point is `imx8mq_clocks_probe()`. It allocates `struct clk_hw_onecell_data`, fills the global `hws` array indexed by `dt-bindings/clock/imx8mq-clock.h`, maps ANATOP and CCM register ranges, registers clocks through helpers from `clk.h`, calls `imx_check_clk_hws()`, and publishes `of_clk_hw_onecell_get`. The file is table-heavy: parent selector arrays describe mux inputs for PLLs, A53, M4, VPU, GPU, NOC, DRAM, display, PCIe, SAI, SPDIF, ENET, NAND, USDHC, I2C, UART, USB, CSI, DSI, CLKO, and PLL monitor outputs.

Key helpers used here include `imx_clk_hw_frac_pll()`, `imx_clk_hw_sscg_pll()`, `imx8m_clk_hw_composite*()`, `imx_clk_hw_mux*()`, `imx_clk_hw_gate*()`, `imx_clk_hw_fixed_factor()`, `imx8m_clk_hw_fw_managed_composite*()`, and `imx_clk_hw_cpu()`.

## Control Flow
Probe initializes dummy and external clocks from device tree names, maps `fsl,imx8mq-anatop`, builds PLL reference muxes/dividers/PLLs/bypass muxes/output gates, creates fixed SYS PLL outputs, and registers PLL monitor mux/dividers. It then maps the CCM resource, registers core, bus, AHB/IPG, DRAM, IP, peripheral, root-gate, and CPU clocks. On provider registration failure or mapping failure it jumps to `unregister_hws` and unregisters the array.

## State And Persistence Behavior
The persistent hardware state is CCM/ANATOP register content; kernel state is the allocated `clk_hw` graph and static shared-gate counters for SAI, display, and NAND gates sharing physical bits. DRAM clocks are flagged firmware-managed / no-cache because TF-A may alter their registers outside Linux.

## Dependencies And Integration Points
Depends on the common clock framework, OF platform probing, i.MX clock helpers, `imx8mq-clock.h`, ANATOP compatible lookup, CCM MMIO, and consumers that request clocks by DT index. It calls `imx_register_uart_clocks()` for serial clock integration.

## Risks
Risks are incorrect DT binding indexes, parent name drift, wrong register offsets or gate sharing, and critical-clock flag mistakes on NOC/AHB/GIC/DRAM paths. Reload is suppressed because clocks are not fully removable. Firmware-managed DRAM paths must remain uncached and must not assume Linux owns parent/divider state.

## Test Signals
Boot an i.MX8MQ DT and verify no missing-clock warnings, `clk_summary` topology/rates, UART console, CPU frequency clock, display/VPU/GPU/CSI/DSI/PCIe peripherals, suspend/resume with DRAM rates, and failure-path coverage for missing ANATOP/CCM resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qm-rsrc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qm-rsrc.c

## Purpose
Defines the SCU resource allowlist for i.MX8QM clocks. The SCU clock core uses this sorted table to avoid registering resource IDs that are not valid on the SoC.

## Important APIs, Types, And Functions
The file contains `imx8qm_clk_scu_rsrc_table[]` and exports `const struct imx_clk_scu_rsrc_table imx_clk_scu_rsrc_imx8qm`. The data type is declared in `clk-scu.h` and consumed by `imx_clk_scu_init()` / `imx_scu_clk_is_valid()`.

## Control Flow
There is no runtime control flow in this file. At match time, the i.MX8QXP/QM clock driver passes this table as match data for `fsl,imx8qm-clk`. Later SCU clock allocation performs a binary search over this list.

## State And Persistence Behavior
State is read-only kernel data. It must stay sorted in ascending order, as the SCU core uses `bsearch()`. It has no persistence beyond the compiled kernel image.

## Dependencies And Integration Points
Depends on firmware resource constants from `dt-bindings/firmware/imx/rsrc.h` and the SCU clock table contract from `clk-scu.h`. It integrates indirectly with device-tree compatible matching and SCFW resource ownership checks.

## Risks
The main risk is table drift. Missing a valid i.MX8QM resource prevents clocks from being registered; adding an invalid resource may cause useless allocation attempts. Reordering can break binary-search validation.

## Test Signals
Boot i.MX8QM with `fsl,imx8qm-clk`, verify expected SCU clocks appear, no valid owned resources are rejected with `-EINVAL`, and invalid i.MX8QXP-only resources remain filtered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qm-rsrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-lpcg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-lpcg.c

## Purpose
Registers i.MX8QXP LPCG gate clocks for subsystem clock-gate blocks. It supports legacy subsystem tables for ADMA, connectivity, and LSIO, and a newer generic DT binding where clock indices, parents, and output names are parsed from each LPCG node.

## Important APIs, Types, And Functions
`struct imx8qxp_lpcg_data` describes one gate: DT id, name, parent, flags, register offset, bit index, and hardware autogate support. `struct imx8qxp_ss_lpcg` groups a subsystem table and maximum clock count. `imx_lpcg_parse_clks_from_dt()` implements the new `fsl,imx8qxp-lpcg` binding. `imx8qxp_lpcg_clk_probe()` tries that path first, then falls back to static subsystem tables. `imx_lpcg_of_clk_src_get()` maps `clock-indices` bit offsets to onecell entries by dividing by four.

## Control Flow
Probe first attempts DT-driven registration. That path ioremaps the node resource, reads `clock-indices`, parent names, and output names, enables runtime PM with autosuspend, registers each LPCG through `imx_clk_lpcg_scu_dev()`, adds a devm clock provider, then autosuspends. On failure it unregisters created clocks and disables runtime PM.

If DT parsing is not applicable, the legacy path obtains match data, maps the subsystem range with `devm_ioremap()` rather than `devm_platform_ioremap_resource()` to allow overlapping peripheral mappings, allocates onecell data, registers static LPCG clocks with `imx_clk_lpcg_scu()`, warns about registration errors, and publishes the provider.

## State And Persistence Behavior
Kernel state is onecell clock arrays and allocated LPCG clock objects. Hardware state is the LPCG register gate bits. Runtime/system suspend state for individual gates is handled by the shared LPCG-SCU implementation and `imx_clk_lpcg_scu_pm_ops`.

## Dependencies And Integration Points
Depends on `clk-lpcg-scu.c`, `clk-imx8qxp-lpcg.h` register offsets, `dt-bindings/clock/imx8-clock.h`, runtime PM, OF clock providers, and SCU clock parents created by `clk-imx8qxp.c`.

## Risks
The old mapping path intentionally avoids reserving the memory region; changing it can break overlapping devices such as UARTs. DT-driven indexing assumes bit offsets are multiples of four and below eight outputs. Parent/output-name count mismatches and partial registration failures must keep cleanup correct.

## Test Signals
Test legacy ADMA/CONN/LSIO nodes and new generic LPCG nodes, verify clock lookup by phandle index, runtime PM autosuspend/resume, serial/network/storage peripherals behind LPCGs, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-lpcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-lpcg.h -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-lpcg.h

## Purpose
Provides subsystem-local LPCG register offsets for i.MX8QXP LSIO, connectivity, and ADMA clock-gate blocks.

## Important APIs, Types, And Functions
This header defines offset macros such as `LSIO_PWM_0_LPCG`, `CONN_USDHC_0_LPCG`, `CONN_ENET_0_LPCG`, `ADMA_LPUART_0_LPCG`, `ADMA_LPI2C_0_LPCG`, and many ADMA audio/peripheral LPCG offsets. There are no functions or types.

## Control Flow
No executable control flow. `clk-imx8qxp-lpcg.c` uses these constants in static LPCG tables to calculate MMIO addresses relative to a subsystem base.

## State And Persistence Behavior
All definitions are compile-time constants. The values encode hardware register layout and must match the SoC reference manual and DT binding expectations.

## Dependencies And Integration Points
The header is private to the i.MX clock driver implementation. It integrates static LPCG registration with dt-binding clock IDs and with the SCU LPCG gate helper.

## Risks
Wrong offsets gate the wrong peripheral clock or touch an unrelated register. Because subsystem ranges can overlap child devices, offset mistakes can be difficult to distinguish from power-domain or SCU ownership issues.

## Test Signals
Compile coverage plus peripheral smoke tests for PWM, UART, I2C, USDHC, ENET, NAND, ADMA audio, and DMA channels behind the listed LPCGs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-lpcg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-rsrc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-rsrc.c

## Purpose
Defines the sorted SCU resource allowlist for i.MX8QXP clocks.

## Important APIs, Types, And Functions
The file contains `imx8qxp_clk_scu_rsrc_table[]` and exported `imx_clk_scu_rsrc_imx8qxp`. The table is passed as match data for `fsl,imx8qxp-clk`.

## Control Flow
There is no executable logic. The SCU core validates requested resource IDs with `bsearch()` before allocating SCU clock devices.

## State And Persistence Behavior
State is immutable compiled data. It is not persisted or modified. The array order is part of the functional contract because search assumes ascending values.

## Dependencies And Integration Points
Depends on `rsrc.h` firmware constants and `clk-scu.h`. It gates registration for the higher-level i.MX8QXP clock tree in `clk-imx8qxp.c`.

## Risks
Incorrect entries cause false missing clocks or invalid SCFW requests. The table differs from i.MX8QM and i.MX8DXL, so using the wrong compatible data can hide or expose the wrong resources.

## Test Signals
Boot on i.MX8QXP, validate expected UART/I2C/SPI/PWM/USDHC/ENET/display/audio clocks register, and confirm invalid resources are skipped without SCFW errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-rsrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp.c

## Purpose
Registers SCU-managed clocks for i.MX8QXP-family SoCs, including i.MX8DXL and i.MX8QM variants. It describes resource/clock-type pairs and SCU GPR helper clocks for CPU, LSIO, DMA, audio, connectivity, display, MIPI/LVDS, CSI, parallel interface, GPU, M4, HDMI TX, and HDMI RX domains.

## Important APIs, Types, And Functions
`imx8qxp_clk_probe()` calls `imx_clk_scu_init()` with match-data resource tables, then creates clocks with `imx_clk_scu()`, `imx_clk_scu2()`, `imx_clk_divider_gpr_scu()`, `imx_clk_mux_gpr_scu()`, and `imx_clk_gate_gpr_scu()`. `clk_on_imx8dxl()` gates registration of ENET RX clocks unavailable on DXL. Module init registers the platform driver and the underlying `imx-scu-clk` driver through `imx_clk_scu_module_init()`.

## Control Flow
Probe initializes the SCU IPC-backed clock subsystem, then registers clock declarations in subsystem order. Each `imx_clk_scu*()` call allocates a platform device that later binds to the SCU clock driver. At the end, `of_clk_add_hw_provider()` publishes `imx_scu_of_clk_src_get` over `imx_scu_clks`. If provider registration fails, `imx_clk_scu_unregister()` cleans registered clocks.

## State And Persistence Behavior
Clock state mostly lives in SCFW, not Linux MMIO. Linux keeps lists of registered `clk_hw` objects by resource ID. The module registers two platform drivers and suppresses bind attributes to avoid unsafe clock removal.

## Dependencies And Integration Points
Depends on SCU firmware IPC, `clk-scu.c`, resource allowlists, `dt-bindings/firmware/imx/rsrc.h`, and DT compatibles `fsl,scu-clk`, `fsl,imx8dxl-clk`, `fsl,imx8qxp-clk`, and `fsl,imx8qm-clk`.

## Risks
Because registration is mostly a sequence of side-effecting SCU clock allocations, missing ownership or resource-table entries silently skip clocks. Parent selector arrays with dummy slots must match SCFW parent indexes. CPU clocks use ATF-mediated rate setting, while other SCU clocks use SCFW PM RPCs.

## Test Signals
Boot each compatible variant, inspect `clk_summary`, run CPU frequency changes, validate UART/I2C/SPI/CAN/USDHC/ENET/display/MIPI/LVDS/HDMI/GPU consumers, and test SCFW resource partitioning where unowned resources are absent rather than fatal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8ulp-sim-lpav.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8ulp-sim-lpav.c

## Purpose
Implements the i.MX8ULP LPAV System Integration Module clock provider for HiFi-related gates. It also creates shared regmap infrastructure used by child mux and auxiliary reset devices.

## Important APIs, Types, And Functions
`struct clk_imx8ulp_sim_lpav_data` embeds a spinlock and variable-size onecell clock data. `struct clk_imx8ulp_sim_lpav_gate` describes each HiFi gate. `clk_imx8ulp_sim_lpav_probe()` maps the SIM register block, initializes a regmap with custom lock/unlock callbacks, registers three gate clocks at `SYSCTRL0`, creates an auxiliary `reset` device, registers the clock provider, and populates child OF devices.

## Control Flow
Probe allocates data, stores it as driver data before regmap initialization so lock callbacks can find it, ioremaps the MMIO resource, initializes the regmap, registers the `hifi_core`, `hifi_pbclk`, and `hifi_plat` gates with parent firmware names `core`, `bus`, and `plat`, creates the reset aux device, adds the provider, and populates mux children.

## State And Persistence Behavior
State is volatile: gate bits in `SYSCTRL0`, the shared spinlock, regmap, auxiliary device, child devices, and onecell clock data. There is no persistent metadata.

## Dependencies And Integration Points
Depends on `imx8ulp-clock.h`, auxiliary bus helpers, regmap MMIO, OF platform population, and common-clock gate registration. It coordinates register access with reset/mux users through the same spinlock.

## Risks
The custom regmap lock uses `dev_get_drvdata()`; setting drvdata before regmap init is required. Clock gates access the register directly while reset/mux use regmap, so lock sharing is necessary to avoid RMW races. Child probing depends on successful provider and regmap setup.

## Test Signals
Probe `fsl,imx8ulp-sim-lpav`, verify the three HiFi gates, child mux/reset devices, concurrent reset and clock operations, and audio/HiFi consumers using the LPAV SIM clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8ulp-sim-lpav.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8ulp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8ulp.c

## Purpose
Registers clock providers and reset controllers for i.MX8ULP CGC1, CGC2, PCC3, PCC4, and PCC5 blocks. It covers PLLs, PFDs, oscillator dividers, bus/core roots, peripheral composite clocks, DMA gates, LPAV clocks, audio selectors, and PCC reset bits.

## Important APIs, Types, And Functions
The probe dispatcher `imx8ulp_clk_probe()` invokes match-data init functions: `imx8ulp_clk_cgc1_init()`, `imx8ulp_clk_cgc2_init()`, `imx8ulp_clk_pcc3_init()`, `imx8ulp_clk_pcc4_init()`, and `imx8ulp_clk_pcc5_init()`. Reset support uses `struct pcc_reset_dev`, `imx8ulp_pcc_assert()`, `imx8ulp_pcc_deassert()`, and `imx8ulp_pcc_reset_init()`. Clock creation uses i.MX helpers for PLLv4, PFDv2, disabled gates, muxes, dividers, composite PCC clocks, and fixed factors.

## Control Flow
Each init allocates onecell data sized for its binding, maps the platform resource, registers the block's clocks, calls `imx_check_clk_hws()`, and adds an OF provider. PCC blocks then register a reset controller using per-block offset arrays. PCC3 also registers UART clocks. The platform match table selects the init function by compatible string.

## State And Persistence Behavior
Hardware state is the CGC/PCC register set and PCC reset bits. Kernel state is devm-managed clock arrays plus reset-controller data. Reset RMW operations share `imx_ccm_lock` with clock control because reset bits live in the same PCC registers as clocks.

## Dependencies And Integration Points
Depends on `imx8ulp-clock.h`, reset-controller framework, OF clock providers, i.MX PLL/PFD/composite helpers, and platform compatibles for each block. Peripheral drivers consume clocks and resets from these providers.

## Risks
Clock and reset fields share registers, so missing locking can corrupt clock settings during reset toggles. Critical flags on A35/NIC/LPAV/DDR/MU/timer clocks affect boot and low-power reliability. PCC reset arrays must match binding reset IDs exactly.

## Test Signals
Boot all CGC/PCC nodes, inspect `clk_summary`, exercise UART, I2C, SPI, USDHC, USB, ENET, SAI, SPDIF, CSI/DSI, DMA, and GPU clocks, test reset controller users, and run suspend/resume with critical clocks retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8ulp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx93.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx93.c

## Purpose
Registers the i.MX93/i.MX91 CCM clock tree. It describes fixed system PLL PFD outputs, fractional GPPLLs, composite root clocks, CCGR gates, shared gates, and A55 CPU clock integration.

## Important APIs, Types, And Functions
`root_array[]` describes root composites with ID, name, offset, selector group, flags, and optional platform mask. `ccgr_array[]` describes gate clocks with parent, offset, flags, optional shared counter, and platform mask. `imx93_clocks_probe()` allocates onecell data, maps ANATOP and CCM, registers fixed/PFD/PLL clocks, iterates both arrays, creates the A55 selector and CPU clock, publishes the provider, and registers UART clocks.

## Control Flow
Probe selects platform mask from match data (`PLAT_IMX93` or `PLAT_IMX91`), initializes external clocks, registers fixed system PFD rates, maps `fsl,imx93-anatop`, creates ARM/audio/video PLLs, maps CCM, then conditionally registers root and CCGR entries whose masks match. Errors unregister the whole clock array.

## State And Persistence Behavior
State includes the `clk_hw` graph, hardware CCM/ANATOP registers, and shared gate counters for SAI, MU-B, PDM, and SPDIF gate pairs. The module parameter `mcore_booted` is declared for compatibility with broader i.MX clock code.

## Dependencies And Integration Points
Depends on `imx93-clock.h`, common clock framework, i.MX composite/gate/GPPLL helpers, OF platform probing, and platform compatibles `fsl,imx93-ccm` and `fsl,imx91-ccm`.

## Risks
Platform masks are important because i.MX91 and i.MX93 share offsets with different clock IDs. Shared CCGR gates must keep counts synchronized. Critical roots for A55/M33/NIC/HSIO/sys counter must not be disabled or low-power paths can fail.

## Test Signals
Boot i.MX93 and i.MX91 DTs, inspect platform-specific clocks, validate A55 CPU clock, UART/I2C/SPI/USDHC/SAI/PDM/SPDIF/media/USB/ENET consumers, and run suspend/resume/CPU idle tests that depend on critical gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx93.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx95-blk-ctl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx95-blk-ctl.c

## Purpose
Implements block-control clock providers for i.MX95 and i.MX94 subsystem CSR blocks, including VPU, camera, LVDS/display, NETC mix, and HSIO. It registers gate, divider, and mux clocks from per-compatible data tables and restores selected CSR state across runtime/system suspend.

## Important APIs, Types, And Functions
`struct imx95_blk_ctl` stores device state, APB clock, base address, spinlock, saved register, and matched data. `struct imx95_blk_ctl_clk_dev_data` describes each clock's name, parents, register, bit field, type, and flags. `struct imx95_blk_ctl_dev_data` groups clock data and PM behavior. `imx95_bc_probe()` registers clocks with `clk_hw_register_mux()`, `clk_hw_register_divider()`, or `clk_hw_register_gate()`. PM handlers are `imx95_bc_runtime_suspend()`, `imx95_bc_runtime_resume()`, `imx95_bc_suspend()`, and `imx95_bc_resume()`.

## Control Flow
Probe allocates state, maps MMIO, gets and enables the APB clock, obtains match data, optionally enables runtime PM, allocates onecell data, iterates clock table entries, registers the provider, populates child devices, and for runtime-PM-enabled blocks autosuspends by disabling APB. If no match data is present, the node is treated as a parent container and only child devices are populated.

## State And Persistence Behavior
Clock bits live in subsystem CSR registers. Linux stores one saved register value at `clk_reg_offset` for PM restore. Runtime-enabled blocks disable the APB clock after probe and restore CSR clock state on resume.

## Dependencies And Integration Points
Depends on i.MX94/i.MX95 clock binding IDs, common clock framework, runtime PM, OF platform population, APB clock provider, and subsystem consumers such as VPU, camera, display, LVDS, NETC, and HSIO drivers.

## Risks
Only one register is saved per block, so tables must keep `clk_reg_offset` aligned with all relevant state. Probe currently returns early on missing match data after enabling APB, which is acceptable for populated containers but worth reviewing for power behavior. Gate polarity flags such as `CLK_GATE_SET_TO_DISABLE` must match hardware.

## Test Signals
Probe each compatible, verify clock provider cells, toggle VPU/camera/LVDS/display/NETC/HSIO consumers, check runtime suspend/resume register restore, and test system sleep with blocks both active and runtime-suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx95-blk-ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imxrt1050.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imxrt1050.c

## Purpose
Registers the i.MX RT1050 CCM/ANATOP clock tree, including PLLs, PFD outputs, bypass muxes, system bus dividers, peripheral muxes, and a small set of peripheral gates.

## Important APIs, Types, And Functions
`imxrt1050_clocks_probe()` is the single platform probe. It fills a `clk_hw_onecell_data` indexed by `imxrt1050-clock.h`. It uses `imx_clk_hw_pllv3()`, `imx_clk_hw_pfd()`, mux/divider/gate helpers, fixed-factor helpers, and `of_clk_add_hw_provider()`.

## Control Flow
Probe allocates the clock array, obtains the oscillator, maps `fsl,imxrt-anatop`, registers PLL reference muxes, PLLv3 instances, bypass muxes, video dividers, PLL3 fixed 80 MHz, PLL2/PLL3 PFDs, then maps CCM and registers core/bus/peripheral selectors and gates. Failure unregisters all created clocks.

## State And Persistence Behavior
State is the ANATOP/CCM register contents and the provider's `clk_hw` array. There is no suspend state in this file. The driver is devm-backed except for clock unregister cleanup on probe errors.

## Dependencies And Integration Points
Depends on `imxrt1050-clock.h`, OF compatible `fsl,imxrt1050-ccm`, ANATOP compatible `fsl,imxrt-anatop`, and common i.MX PLL/PFD helpers. Consumers include USDHC, LPUART, LCDIF, DMA, DMAMUX, SEMC, AHB/IPG/peripheral bus users.

## Risks
Some parent entries are placeholders such as `"todo"` or dummy inputs, so DT/rate changes need caution. PLL/PFD register offsets must match RT1050 ANATOP, which differs from larger i.MX8 SoCs. Missing critical flags on SEMC/bus paths could destabilize memory access.

## Test Signals
Boot RT1050, verify clock provider registration, UART console, USDHC, LCDIF pixel path, DMA/DMAMUX, SEMC/bus rates, PFD rates in `clk_summary`, and assigned-clock rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imxrt1050.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-lpcg-scu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-lpcg-scu.c

## Purpose
Implements LPCG gate clocks used on SCU-based i.MX8 platforms. It controls LPCG software and hardware autogate bits and handles the e10858 write-synchronization erratum.

## Important APIs, Types, And Functions
`struct clk_lpcg_scu` stores `clk_hw`, register address, bit index, hardware-autogate flag, and saved state. `clk_lpcg_scu_enable()` and `clk_lpcg_scu_disable()` update the two-bit gate field under `imx_lpcg_scu_lock`. `lpcg_e10858_writel()` performs the write plus delay/readback required by the erratum. `__imx_clk_lpcg_scu()` registers a clock, and `imx_clk_lpcg_scu_unregister()` frees it. `imx_clk_lpcg_scu_pm_ops` saves/restores LPCG state in noirq suspend/resume.

## Control Flow
Enable clears the field and writes software-enable plus optional hardware-autogate selection. Disable clears the field. Both use the current clock rate to choose readback versus nanosecond delay. Registration allocates a clock object, sets `CLK_SET_RATE_PARENT`, registers it, and optionally stores it as device drvdata for PM.

## State And Persistence Behavior
Hardware state is the LPCG register. The driver saves one raw register value per device-backed LPCG for suspend and restores it on resume, skipping names beginning with `hdmi_lpcg`.

## Dependencies And Integration Points
Used by `clk-imx8qxp-lpcg.c` and declared in `clk-scu.h`. Depends on common clock framework, MMIO access, spinlocks, delay helpers, and system sleep PM callbacks.

## Risks
The erratum delay is rate-dependent; a wrong parent rate can under-delay low-frequency gates. Register fields are two bits wide and shifted by `bit_idx`; incorrect bit indexes affect adjacent gate fields. PM drvdata only tracks one clock per device, so multi-output DT paths must be reviewed with this limitation.

## Test Signals
Enable/disable LPCG-backed UART/I2C/USDHC/ENET clocks, verify e10858-safe writes on low-rate clocks, run suspend/resume, and check HDMI LPCG special-case behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-lpcg-scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pfd.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pfd.c

## Purpose
Implements legacy i.MX PFD clocks, where a PLL output is multiplied by 18 and divided by a six-bit fractional divider stored in a packed PFD register.

## Important APIs, Types, And Functions
`struct clk_pfd` stores `clk_hw`, register, and PFD index. Operations include `clk_pfd_enable()`, `clk_pfd_disable()`, `clk_pfd_recalc_rate()`, `clk_pfd_determine_rate()`, `clk_pfd_set_rate()`, and `clk_pfd_is_enabled()`. Public factory `imx_clk_hw_pfd()` is exported.

## Control Flow
Enable/disable write to hardware SET/CLR alias registers for the gate bit. Rate calculation reads the per-index fraction and computes `parent * 18 / frac`. Determine/set round the requested rate to a fraction clamped to 12..35, then update the packed field using CLR and SET aliases.

## State And Persistence Behavior
State is fully in the PFD hardware register. The allocated clock object is not devm-managed and is returned to callers for normal clock framework lifetime handling.

## Dependencies And Integration Points
Used by SoC clock drivers such as i.MXRT1050 and older i.MX6-style trees. Depends on common clock framework, MMIO alias semantics, and helper allocation macros from `clk.h`.

## Risks
No explicit locking protects shared packed PFD registers, so concurrent updates would rely on higher-level serialization. Fraction zero would divide by zero if hardware contains an invalid value. Valid range clamping can produce a different rate than requested.

## Test Signals
Verify PFD rates in `clk_summary`, assigned-clock rate rounding, gate enable/disable state, and peripherals sourced from PLL2/PLL3 PFD outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pfdv2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pfdv2.c

## Purpose
Implements second-generation i.MX PFD clocks with explicit gate and valid bits, used by newer platforms such as i.MX8ULP.

## Important APIs, Types, And Functions
`struct clk_pfdv2` stores register, gate bit, valid bit, and fraction offset. Main operations are `clk_pfdv2_enable()`, `clk_pfdv2_disable()`, `clk_pfdv2_recalc_rate()`, `clk_pfdv2_determine_rate()`, `clk_pfdv2_set_rate()`, and `clk_pfdv2_is_enabled()`. `imx_clk_hw_pfdv2()` exports the factory and sets flags based on `enum imx_pfdv2_type`.

## Control Flow
Enable clears the gate bit under `pfd_lock` and polls the valid bit. Disable sets the gate bit. Recalc reads the fraction and returns zero for invalid fraction zero. Determine searches candidate parent rates 480 MHz, 528 MHz, and the current best parent, clamps fraction to 12..35, and picks the closest result. Set-rate disables hardware-enabled PFDs first because the hardware cannot change rate while enabled, then writes the fraction.

## State And Persistence Behavior
State is in hardware gate/valid/fraction fields. There is no explicit suspend state. A global spinlock serializes RMW operations across PFDv2 clocks.

## Dependencies And Integration Points
Used by CGC/PFD code in i.MX8ULP. Depends on `readl_poll_timeout()`, common clock framework, and i.MX clock type definitions.

## Risks
Set-rate may disable a PFD that was enabled by hardware but has no software consumer count; consumers relying on boot defaults must be checked. Parent-rate search has hard-coded common rates. Valid-bit timeout is only 1 ms.

## Test Signals
Assigned-clock changes on i.MX8ULP SPLL/PLL4 PFDs, valid-bit timeout injection, consumers sourced by PFDv2 outputs, and concurrent rate changes across multiple PFDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pfdv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pll14xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pll14xx.c

## Purpose
Implements i.MX 1416x and 1443x PLL clock providers, including fixed table-based rates for integer PLLs and dynamic fractional settings for 1443x PLLs.

## Important APIs, Types, And Functions
`struct clk_pll14xx` stores base address, PLL type, and rate table. Exported PLL descriptors are `imx_1443x_pll`, `imx_1443x_dram_pll`, and `imx_1416x_pll`. Important functions include `imx_get_pll_settings()`, `pll14xx_calc_rate()`, `imx_pll14xx_calc_settings()`, determine-rate functions for 1416x/1443x, set-rate functions, `clk_pll14xx_prepare()`, `clk_pll14xx_unprepare()`, and exported factory `imx_dev_clk_hw_pll14xx()`.

## Control Flow
Registration selects ops by PLL type and clears bypass. Determine-rate for 1416x snaps to the descending static table. Determine-rate for 1443x first tries exact table settings, then tries kdiv-only adjustment for glitch-free retuning, then searches pdiv/sdiv/mdiv/kdiv for the closest rate. Set-rate either updates sdiv/kdiv in place or sequences bypass, reset, divider writes, delay, lock polling, and bypass exit.

## State And Persistence Behavior
State is hardware registers `GNRL_CTL`, `DIV_CTL0`, and `DIV_CTL1`, plus immutable rate tables. DRAM PLL descriptor uses `CLK_GET_RATE_NOCACHE` so framework reads hardware state.

## Dependencies And Integration Points
Used by i.MX8-family clock trees through `clk.h`. Depends on common clock framework, bitfield helpers, MMIO, lock polling, and PLL rate table macros.

## Risks
Bypass/reset sequencing is hardware-sensitive. 1443x dynamic search must keep kdiv in signed 16-bit range. Table ordering matters for 1416x rounding. Lock timeout failures must propagate to callers.

## Test Signals
Rate set/round/recalc tests for table and non-table 1443x rates, DRAM no-cache reads, lock timeout behavior, and boot validation of SoCs using 1416x/1443x PLLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pll14xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv1.c

## Purpose
Implements recalc-rate support for first-generation i.MX PLLs found on i.MX1/21/25/27/31/35.

## Important APIs, Types, And Functions
`struct clk_pllv1` stores base address and `enum imx_pllv1_type`. Helpers identify SoC variants and signed MFN behavior. `clk_pllv1_recalc_rate()` decodes MFI/MFN/MFD/PD fields and computes the PLL output. `imx_clk_hw_pllv1()` registers the clock.

## Control Flow
The only clock operation is recalc. It reads the PLL register, extracts fields, enforces minimum MFI of 5, handles SoC-specific MFN signedness, computes `2 * parent / (pd + 1) * (mfi +/- mfn/(mfd+1))`, and returns the result.

## State And Persistence Behavior
All PLL configuration lives in the hardware register. The driver does not support set-rate, prepare, or suspend state.

## Dependencies And Integration Points
Used by legacy i.MX clock drivers through `clk.h`. Depends on common clock framework and MMIO access.

## Risks
Variant-specific MFN interpretation is the main risk; i.MX1/i.MX21 differ from i.MX27 and later. This driver cannot change PLL settings, so platform code must not expect rate control.

## Test Signals
Compare recalc rates against bootloader-programmed PLL registers on legacy i.MX SoCs and validate signed MFN cases for i.MX27-like hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv2.c

## Purpose
Implements i.MX PLL version 2 clocks, including prepare/unprepare, recalc, determine-rate, and set-rate for the DP PLL register layout.

## Important APIs, Types, And Functions
`struct clk_pllv2` stores base address. `__clk_pllv2_recalc_rate()` computes the output from DP control/operator/MFD/MFN fields. `__clk_pllv2_set_rate()` derives DP fields for a target rate. Public ops include `clk_pllv2_prepare()`, `clk_pllv2_unprepare()`, `clk_pllv2_recalc_rate()`, `clk_pllv2_determine_rate()`, and `clk_pllv2_set_rate()`. Factory is `imx_clk_hw_pllv2()`.

## Control Flow
Prepare sets `UPEN` and polls `LRF` up to 1 ms. Set-rate computes MFI/PDF/MFN/MFD, enables `DPDCK0_2`, writes OP/MFD/MFN registers, and returns. Determine-rate simulates those fields and recalculates the achievable output.

## State And Persistence Behavior
Hardware state is the DP PLL register block. Kernel state is only the allocated `clk_hw`. There is no explicit suspend logic.

## Dependencies And Integration Points
Used by older i.MX clock trees. Depends on raw MMIO access, delay polling, common clock framework, and 64-bit division helpers.

## Risks
The rate solver is simple and may return `-EINVAL` for out-of-range MFI. `clk_pllv2_determine_rate()` stores an error code into `req->rate` on solver failure but returns success, which is legacy behavior to review before reuse. Lock polling is bounded at about 1 ms.

## Test Signals
Prepare lock success/failure, assigned-clock rate changes, recalc agreement with hardware fields, and out-of-range rate requests on i.MX5-era platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv3.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv3.c

## Purpose
Implements multiple i.MX PLLv3 variants: generic USB-style 20x/22x PLLs, SYS PLLs, audio/video fractional PLLs, VF610 fractional PLLs, ENET fixed-rate PLLs, and i.MX7-specific power/offset variants.

## Important APIs, Types, And Functions
`struct clk_pllv3` stores base address, power bit semantics, divider mask/shift, reference clock, and numerator/denominator offsets. The file provides variant-specific ops: `clk_pllv3_ops`, `clk_pllv3_sys_ops`, `clk_pllv3_av_ops`, `clk_pllv3_vf610_ops`, and `clk_pllv3_enet_ops`. Factory `imx_clk_hw_pllv3()` selects ops and offsets from `enum imx_pllv3_type`.

## Control Flow
Prepare toggles the configured power bit and waits for lock if powered. Generic set-rate selects 20x or 22x parent multiplier. SYS set-rate clamps to parent*54/2..parent*108/2. AV and DDR variants compute integer and fractional numerator/denominator fields. VF610 converts between 20/22 integer plus 30-bit fraction. ENET returns a fixed reference rate.

## State And Persistence Behavior
All clock settings are in PLL hardware registers. The driver stores no saved PM state. Variant data is encoded in each clock object at registration.

## Dependencies And Integration Points
Used by i.MX6/i.MX7/i.MXRT clock trees. Depends on common clock framework, MMIO, polling, delay helpers, and exported factory symbol.

## Risks
Power-bit polarity differs by variant (`powerup_set`). Fractional math must respect denominator limits. ENET PLL recalc ignores parent and returns fixed board-specific rates. Lock polling is required after set-rate and prepare.

## Test Signals
Variant-specific rate tests for SYS/USB/AV/VF610/ENET, lock timeout injection, i.MX7 ENET/DDR power-bit behavior, and consumers such as USB, video, audio, ENET, and system PLL roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv4.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv4.c

## Purpose
Implements i.MX PLLv4 clocks, including i.MX8ULP offset variants and the special 1 GHz range-based multiplier mode.

## Important APIs, Types, And Functions
`struct clk_pllv4` stores base address, register offsets, and whether multipliers are selected from a continuous range. Ops include `clk_pllv4_prepare()`, `clk_pllv4_unprepare()`, `clk_pllv4_is_prepared()`, `clk_pllv4_recalc_rate()`, `clk_pllv4_determine_rate()`, and `clk_pllv4_set_rate()`. Exported factory is `imx_clk_hw_pllv4()`.

## Control Flow
Determine-rate chooses either a valid multiplier from `{33,27,22,20,17,16}` or a multiplier in range 27..54, then computes optional fractional numerator/denominator. Set-rate validates the multiplier, writes multiplier, numerator, and denominator registers. Prepare sets `PLL_EN` and polls `PLL_VLD`; unprepare clears enable.

## State And Persistence Behavior
State is in PLL CSR/config/numerator/denominator registers. The driver stores offsets in the clock object so generic and i.MX8ULP layouts share ops. No suspend state is saved here.

## Dependencies And Integration Points
Used by i.MX8ULP CGC blocks. Depends on common clock framework, MMIO polling, type enum definitions, and exported factory use from platform clock drivers.

## Risks
Set-rate uses integer `rate / parent_rate`; requests that need a multiplier just outside valid table/range fail. Determine-rate returns zero on unsupported rates, so callers must treat that as failure. Fraction numerator must remain below denominator.

## Test Signals
PLL4/SPLL2/SPLL3 assigned-clock changes, valid multiplier edge cases, enable/valid-bit polling, and PFD consumers sourced from PLLv4 outputs on i.MX8ULP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-scu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-scu.c

## Purpose
Provides the SCU-backed clock implementation for i.MX8 SCFW platforms. It turns clock registrations into platform devices, attaches power domains, performs SCU PM/MISC RPCs for rate/parent/enable/GPR operations, and saves/restores clock state across system sleep.

## Important APIs, Types, And Functions
Key types are `struct imx_scu_clk_node`, `struct clk_scu`, and `struct clk_gpr_scu`. Public entry points include `imx_clk_scu_module_init()`, `imx_clk_scu_module_exit()`, `imx_clk_scu_init()`, `imx_scu_of_clk_src_get()`, `imx_clk_scu_alloc_dev()`, `__imx_clk_scu()`, `imx_clk_scu_unregister()`, and `__imx_clk_gpr_scu()`. Clock ops call SCFW RPCs through `clk_scu_recalc_rate()`, `clk_scu_set_rate()`, `clk_scu_get_parent()`, `clk_scu_set_parent()`, and `sc_pm_clock_enable()`. CPU rate changes use `clk_scu_atf_set_cpu_rate()` and ARM SMCCC.

## Control Flow
`imx_clk_scu_init()` gets the SCU IPC handle, initializes per-resource clock lists for two-cell providers, finds the SCU power-domain node, and stores an optional resource allowlist. Clock declarations call `imx_clk_scu_alloc_dev()`, which validates the resource, checks SCFW ownership, creates a platform device forced to bind `imx-scu-clk`, attaches a genpd unless it is an A-core resource, and adds the device. `imx_clk_scu_probe()` enables runtime PM for non-CPU clocks, registers the actual `clk_hw`, appends it to `imx_scu_clks[resource]`, and autosuspends.

## State And Persistence Behavior
Persistent clock authority is SCFW. Linux stores IPC handle, power-domain node, resource table, per-resource lists, and per-clock saved parent/rate/enabled state for noirq sleep. Resume restores parent, rate, and enabled state except CPU clocks and PI PLL enable.

## Dependencies And Integration Points
Depends on SCU IPC, SCFW RM ownership API, PM domain framework, runtime PM, ARM SMCCC for CPU frequency, Xen headers, OF clock providers, and resource constants. Higher-level i.MX8QXP/QM code uses the inline wrappers in `clk-scu.h`.

## Risks
Resource allowlists must be sorted. `imx_clk_scu_alloc_dev()` returns `NULL` for successful deferred platform-device creation and also for unowned resources, so callers intentionally ignore return values. Sleep restore order must respect power domains and SCFW ownership. CPU clocks are special because SCFW may report them unowned while Linux still controls cpufreq via ATF.

## Test Signals
Boot SCU platforms with two-cell clock providers, verify phandle lookups by resource/type, cpufreq changes via SMCCC, runtime PM autosuspend, suspend/resume restore for parent/rate/enabled clocks, and resource partition tests where unowned clocks are skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-scu.h -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-scu.h

## Purpose
Declares the SCU clock integration API used by i.MX8 SCFW clock drivers and LPCG helpers.

## Important APIs, Types, And Functions
Defines GPR clock flags `IMX_SCU_GPR_CLK_GATE`, `IMX_SCU_GPR_CLK_DIV`, and `IMX_SCU_GPR_CLK_MUX`; `struct imx_clk_scu_rsrc_table`; extern declarations for `imx_scu_clks`, LPCG PM ops, and SoC resource tables; and prototypes for SCU module init/exit, SCU provider init, phandle lookup, SCU clock allocation, direct SCU clock registration, unregister, LPCG registration, and GPR clock registration.

Inline helpers wrap the generic constructors: `imx_clk_scu()`, `imx_clk_scu2()`, `imx_clk_lpcg_scu_dev()`, `imx_clk_lpcg_scu()`, `imx_clk_gate_gpr_scu()`, `imx_clk_divider_gpr_scu()`, and `imx_clk_mux_gpr_scu()`.

## Control Flow
No executable control flow beyond inline wrappers that pass standard flag/parent/count arguments into implementation functions.

## State And Persistence Behavior
The header declares shared state but does not allocate it. Runtime state is implemented in `clk-scu.c` and `clk-lpcg-scu.c`.

## Dependencies And Integration Points
Depends on SCU firmware types from `linux/firmware/imx/sci.h` and OF declarations. It is included by SCU platform clock files, LPCG drivers, and resource-table files.

## Risks
Inline wrappers encode important flag combinations. Passing a stack parent pointer is safe only because registration consumes names immediately as expected by the clock framework. Changing return semantics or wrappers affects all SCU-based clock declarations.

## Test Signals
Compile all SCU clock users, verify wrappers create gate/divider/mux behavior, and run two-cell phandle lookup tests on i.MX8QXP/QM/DXL platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-scu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-sscg-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-sscg-pll.c

## Purpose
Implements spread-spectrum-capable SSCG PLL clocks used by i.MX8M SoCs. It supports normal two-stage PLL mode, stage-1 bypass, stage-2 bypass, parent switching, rate search, prepare/unprepare, and lock polling.

## Important APIs, Types, And Functions
`struct clk_sscg_pll_setup` stores computed dividers, VCOs, output, reference rates, bypass mode, and error. `struct clk_sscg_pll` stores clock object, base, setup, and parent indexes. Search helpers include `clk_sscg_pll_find_setup()`, `clk_sscg_pll1_find_setup()`, `clk_sscg_pll2_find_setup()`, and divider lookup helpers for divr/divf/divq. Clock ops include `clk_sscg_pll_prepare()`, `clk_sscg_pll_unprepare()`, `clk_sscg_pll_recalc_rate()`, `clk_sscg_pll_set_rate()`, `clk_sscg_pll_get_parent()`, `clk_sscg_pll_set_parent()`, and `clk_sscg_pll_determine_rate()`. Exported factory is `imx_clk_hw_sscg_pll()`.

## Control Flow
Determine-rate first tries full bypass if parent can supply the target directly, then stage-1 bypass, then normal mode. Each mode constrains parent/reference/VCO/output ranges and searches divider combinations for an exact or closest output. Set-rate writes bypass bits and divider fields from the previously computed setup, then waits for lock unless bypassed. Recalc decodes current divider fields and bypass bits.

## State And Persistence Behavior
Hardware state is in `PLL_CFG0` and `PLL_CFG2`. The last computed setup is stored in the clock object and consumed by set-rate/parent operations. No PM state is saved in this file.

## Dependencies And Integration Points
Used by i.MX8MQ clock registration for SYS3, DRAM, and VIDEO2 PLLs. Depends on common clock framework, bitfield helpers, MMIO, lock polling, and exported factory use from `clk.h`.

## Risks
`set_parent()` ignores the requested index and applies `setup.bypass`, so it must follow determine-rate/setup calculations. Divider search ranges are large but bounded; closest-rate fallback depends on `fout_error` initialization. Bypass and lock semantics must match hardware or boot-critical PLLs can hang.

## Test Signals
Rate round/set/recalc tests for bypass2, bypass1, and normal modes; DRAM/SYS3/VIDEO2 boot clocks on i.MX8M; lock timeout testing; and parent switching through assigned clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-sscg-pll.c -->

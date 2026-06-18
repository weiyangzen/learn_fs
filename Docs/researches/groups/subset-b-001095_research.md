# subset-b-001095 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx5.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx5.c

## Purpose
`clk-imx5.c` is the common clock framework provider for i.MX50, i.MX51, and i.MX53 CCM hardware. It builds a flat onecell clock table indexed by `dt-bindings/clock/imx5-clock.h`, maps DPLL and CCM register blocks, registers PLLs, muxes, dividers, fixed factors, gates, and CPU clocks, then exposes them to device tree consumers through `of_clk_add_provider()`. The file also applies boot-time parent/rate policy for SDHC, USB, CAN, TV/display, and low-power step clocks.

## Important APIs, Types, And Functions
The key state is `static struct clk *clk[IMX5_CLK_END]` and `static struct clk_onecell_data clk_data`. `mx5_clocks_common_init()` creates clocks shared by all supported i.MX5 variants: fixed inputs, bus roots, UART/ECSPI/USB/SSI/SPDIF roots, peripheral gates, critical AHB/AIPS/TMAX/SPBA/EMI/GPC clocks, and shared display/audio parent muxes. Variant entry points `mx50_clocks_init()`, `mx51_clocks_init()`, and `mx53_clocks_init()` map the correct PLL base addresses, call the common initializer, add SoC-specific muxes/gates, run `imx_check_clocks()`, register the provider, and tune initial parent/rate choices. Registration is via `CLK_OF_DECLARE()` compatible strings `fsl,imx50-ccm`, `fsl,imx51-ccm`, and `fsl,imx53-ccm`.

The implementation depends heavily on i.MX helper constructors from `drivers/clk/imx/clk.h`: `imx_clk_pllv2()`, `imx_clk_mux()`, `imx_clk_mux_flags()`, `imx_clk_divider()`, `imx_clk_gate2()`, `imx_clk_gate2_flags()`, `imx_clk_fixed_factor()`, and `imx_clk_cpu()`.

## Control Flow
Probe is early OF clock declaration driven. Each SoC init maps DPLL regions with fixed physical base addresses, maps the CCM node with `of_iomap()`, registers common clocks, registers SoC-only display/media/peripheral clocks, checks the table, publishes the onecell provider, then performs post-registration setup with normal clock framework calls. i.MX50 uses MX53-style DPLL addresses and a two-bit `main_bus` mux; i.MX51 applies MIPI power-saving register workarounds; i.MX53 adds PLL4, LDB, CAN, SATA, FIRI, CSI, IEEE1588, and an `imx_clk_cpu()` ARM clock model.

## State And Persistence
Persistent state is the global clock pointer table, `clk_data`, and hardware register state programmed through CCM/DPLL MMIO. No filesystem or NVRAM state is used. Parent/rate changes are persistent for the running kernel because they write live CCM register fields. Several gates are marked `CLK_IS_CRITICAL` to keep fabric, memory, and power-management clocks enabled regardless of consumer usage.

## Dependencies And Integration Points
The driver integrates with device tree clock consumers through numeric IDs from `imx5-clock.h`, with silicon revision helpers from `<soc/imx/revision.h>`, with Linux CCF APIs, and with downstream drivers through `clk_register_clkdev()` aliases for CPU and GPC DVFS plus `imx_register_uart_clocks()`. It also relies on board-provided fixed clocks named `ckil`, `osc`, `ckih1`, and `ckih2`.

## Risks
Risk is concentrated in register bit positions, parent arrays, and SoC differences. A wrong mux parent order breaks DT clock IDs silently. Failed `ioremap()`/`of_iomap()` only triggers `WARN_ON()` and execution continues, so a bad mapping can become a later NULL access. Clock names must remain stable because many in-file parents reference prior registrations by string. Critical-clock flags must be conservative: removing one from bus, memory, or power domains can hang boot.

## Test Signals
Useful signals are early boot without clock provider warnings, `imx_check_clocks()` absence of missing-clock diagnostics, working serial console after `imx_register_uart_clocks()`, correct SDHC enumeration at the configured 166.25 MHz or 200 MHz roots, USB PHY operation at 24 MHz/rounded 54 MHz OHCI/host roots, display/LDB paths on i.MX53, and debugfs `/sys/kernel/debug/clk/clk_summary` parent/rate/gate state matching the reference manual and board DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6q.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6q.c

## Purpose
`clk-imx6q.c` registers the i.MX6Q, i.MX6DL, and i.MX6QP CCM/ANATOP clock topology. It exposes `IMX6QDL_CLK_*` IDs as a hardware-clock onecell provider and models PLL bypasses, PFDs, audio/video post dividers, display/LDB paths, GPU/IPU/MMDC/AXI buses, ENET/PCIe/SATA references, and large peripheral gate banks. It also handles several hardware quirks that must be resolved before ordinary CCF consumers manipulate the clocks.

## Important APIs, Types, And Functions
State is held in `static struct clk_hw **hws` and `static struct clk_hw_onecell_data *clk_hw_data`. `clk_on_imx6q()`, `clk_on_imx6qp()`, and `clk_on_imx6dl()` branch registration for SoC variants. `ldb_di_sel_by_clock_id()` and `of_assigned_ldb_sels()` parse `assigned-clock-parents` so LDB DI muxes can be safely initialized before read-only registration. `pll6_bypassed()` detects static ENET PLL bypass configuration. `mmdc_ch1_disable()`, `mmdc_ch1_reenable()`, and `init_ldb_clks()` implement the special multi-step LDB mux transition. `disable_anatop_clocks()` gates unused PFDs and PLL5 after safe parents are known. `imx6q_obtain_fixed_clk_hw()` prefers OF-provided fixed clocks but falls back to local fixed-clock creation.

The main `imx6q_clocks_init()` allocates the flexible onecell array, maps ANATOP and CCM, registers PLL/PFD/fixed-factor/mux/divider/busy-divider/gate/shared-gate clocks, publishes the provider, and applies default parent/rate policy.

## Control Flow
Initialization starts from `CLK_OF_DECLARE(imx6q, "fsl,imx6q-ccm", imx6q_clocks_init)`. The driver obtains fixed inputs, maps `fsl,imx6q-anatop`, adjusts post-divider tables for i.MX6Q revision 1.0, builds PLL bypass sources and PLL gates, models ENET PLL outputs differently depending on bypass state, and creates LVDS exclusive in/out gates. After PFD and fixed-factor clocks are created, CCM muxes and dividers are registered. The code masks MMDC handshakes, initializes LDB DI muxes before registration on non-QP parts, gates large CCGR banks, checks all hardware clocks, and calls `of_clk_add_hw_provider()`. Post-registration setup assigns display, ENFC, USB PHY, CLKO, SPDIF, PCIe, GPU, and ENET parents/rates.

## State And Persistence
Runtime state includes the global `hws` array, shared-gate refcounts for ESAI/ASRC/SSI/MIPI/SPDIF/PRG, and hardware CCM/ANATOP/IOMUXC-GPR register contents. No persistent storage is used. Hardware state persists until reset and includes gate bits, mux choices, divider settings, PLL bypass bits, and GPR ENET reference mux selection.

## Dependencies And Integration Points
The file integrates with CCF `clk_hw` provider APIs, `dt-bindings/clock/imx6qdl-clock.h`, OF assigned-clock properties, SoC revision checks, `imx_mmdc_mask_handshake()`, `imx_clk_gpr_mux()` through `fsl,imx6q-iomuxc-gpr`, optional USB PHY and PCIe configurations, and `imx_register_uart_clocks()`. Consumers include IPU/LDB display, GPU, ENET, PCIe, SATA, SDHC, audio, UART, and memory-controller users.

## Risks
The LDB and MMDC code is high-risk because incorrect parent switching can glitch display clocks or disable a memory-derived clock. The PLL6 bypass model is intentionally static; changing assumptions later can misrepresent ENET/SATA/PCIe rates. Many branches reuse IDs differently across Q/DL/QP, so missing variant coverage can leave NULL `hws` entries. Register table mutations for i.MX6Q rev 1.0 affect global divider tables and must run before divider registration. `WARN_ON(!base)` does not stop execution after failed MMIO mapping.

## Test Signals
Boot should show no missing `imx_check_clk_hws()` entries and no LDB glitch/errors unless firmware already changed reset mux state. Check `clk_summary` for expected ENET/SATA/PCIe/LDB/IPU/GPU parents. Display panels using LDB/IPU, PCIe with LVDS1 reference, ENET reference selection via GPR, USB PHY refcounting, SDHC, SPDIF/audio clocks, and GPU rate ceilings are the primary integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sl.c

## Purpose
`clk-imx6sl.c` provides the i.MX6 SoloLite clock tree. It registers ANATOP PLLs, PFDs, CCM muxes/dividers/gates, and display/e-paper/audio/peripheral roots for the `fsl,imx6sl-ccm` compatible. In addition to normal CCF provider setup, it exports `imx6sl_set_wait_clk()` to implement the ERR005311 low-power WAIT-mode workaround by temporarily reducing the ARM/IPG ratio.

## Important APIs, Types, And Functions
The clock provider uses `static struct clk_hw **hws`, `static struct clk_hw_onecell_data *clk_hw_data`, plus global `ccm_base` and `anatop_base` used by the WAIT workaround. `imx6sl_get_arm_divider_for_wait()` inspects the current PLL1 switch and ARM PLL divider to choose a safe CACRR divider. `imx6sl_enable_pll_arm()` temporarily powers/enables PLL1 and restores the saved register value. `imx6sl_set_wait_clk(bool enter)` saves the current ARM divider, writes a low-frequency WAIT divider on entry, restores it on exit, and waits for `CDHIPR` busy clearance.

`imx6sl_clocks_init()` registers fixed inputs, ANATOP PLL bypasses and gates, PFDs, fixed factors, CCM muxes, busy muxes/dividers, peripheral dividers, shared gates for SSI/SPDIF, and CCGR gates for CSI, LCDIF, EPDC, PXP, GPU2D, SDMA, UART, USDHC, and related blocks.

## Control Flow
The OF clock declaration maps ANATOP first, creates PLL/bypass/PFD/video/audio/enet reference clocks, then maps the CCM node and stores `ccm_base`. It registers roots and peripheral selectors, then creates busy muxes and busy dividers for bus domains where hardware reports handshake status. CCGR gates are created last. The driver masks MMDC CH0 handshaking, validates all `IMX6SL_CLK_END` entries, publishes the onecell provider, sets AHB to 132 MHz, optionally enables USB PHY dummy gates, assigns SPDIF0 to PLL3 PFD3, chooses PLL5 video for LCDIF pixel, chooses PLL2 PFD2 for LCDIF AXI, and registers UART clocks.

## State And Persistence
Provider state is the allocated `clk_hw_data` and `hws` table. WAIT-mode state is static local saved values in `imx6sl_enable_pll_arm()` and `imx6sl_set_wait_clk()`, backed by live PLL_ARM/CACRR register writes. Clock configuration is maintained in hardware registers; there is no disk persistence. Shared gate refcounts coordinate logical SSI/SPDIF clock users that map to the same CCGR bits.

## Dependencies And Integration Points
The file depends on Linux CCF `clk_hw` constructors, `dt-bindings/clock/imx6sl-clock.h`, i.MX helper APIs including `imx_clk_hw_fixup_mux()`, `imx_clk_hw_busy_mux()`, `imx_clk_hw_busy_divider()`, and `imx_mmdc_mask_handshake()`, and optional `CONFIG_USB_MXS_PHY`. Consumers include LCDIF, EPDC, PXP, CSI, GPU2D, USDHC, ECSPI, UART, SSI/SPDIF, GPT/EPIT, I2C, and memory-controller clocks.

## Risks
The WAIT workaround runs in idle-sensitive context and uses raw polling instead of sleepable clock APIs, so register choices and saved-state handling must be exact. If `anatop_base` or `ccm_base` is unavailable, later WAIT calls would be unsafe. Busy divider/mux bit positions must match the reference manual to avoid changing active bus rates while hardware is busy. Fixup mux/divider use implies shared register fields where naive writes could disturb adjacent selectors.

## Test Signals
Boot should provide all `IMX6SL_CLK_*` IDs without `imx_check_clk_hws()` warnings. Runtime validation includes successful suspend/idle WAIT transitions without cache corruption symptoms, AHB at 132 MHz, LCDIF pixel output from PLL5 video, EPDC/LCDIF/PXP operation, USB PHY enablement when configured, and consistent SSI/SPDIF shared gate behavior under audio playback/recording.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sll.c

## Purpose
`clk-imx6sll.c` is the i.MX6SLL CCM/ANATOP provider. It describes a SoloLite-Lite style clock tree with PLL bypasses, PLL/PFD roots, AXI/AHB/MMDC bus clocks, display and e-paper pixel paths, SSI/SPDIF/external-audio shared gates, USB PHY dummy gates, and common low-speed peripheral gates. It registers the provider with `CLK_OF_DECLARE_DRIVER(imx6sll, "fsl,imx6sll-ccm", ...)`.

## Important APIs, Types, And Functions
The file is mostly declarative clock topology around `static struct clk_hw **hws` and `static struct clk_hw_onecell_data *clk_hw_data`. It uses parent-name arrays for PLL bypasses, bus roots, USDHC, SSI, SPDIF, LDB DI, LCDIF, EPDC, ECSPI, UART, and PERCLK selectors. `imx6sll_clocks_init()` is the only function: it allocates the onecell structure, obtains external fixed clocks (`ckil`, `osc`, `ipp_di0`, `ipp_di1`), maps `fsl,imx6sll-anatop`, clears PLL bypass bits via `xPLL_CLR()`, registers ANATOP clocks, maps CCM, registers CCM muxes/dividers/busy dividers/gates, masks MMDC handshake, publishes the provider, registers UART clocks, and adjusts bus rates.

## Control Flow
Initialization first disables PLL bypass by writing clear registers for PLL1/2/3/4/5/6/7. PLL constructors in this file use bypass-source parents for PLL inputs, then separate bypass muxes and post gates/fixed factors expose usable roots. Optional USB PHY gates are only created and marked critical when `CONFIG_USB_MXS_PHY` is enabled. After PFD and post-divider setup, CCM muxes define bus and peripheral parent choices, then dividers and busy dividers derive per-domain rates. CCGR sections create gates for AIPSTZ, DCP, UARTs, GPIOs, ECSPI, timers, I2C, OCOTP, CSI, LCDIF, PXP, EPDC, watchdogs, MMDC, OCRAM, ROM, SDMA, SPBA, audio, and USDHC. Final policy lowers AHB to 99 MHz, switches PERIPH through a safe intermediate path to PLL2 bus, then raises AHB to 132 MHz.

## State And Persistence
State lives in the allocated provider table, shared gate counters for audio/SSI groups, and live ANATOP/CCM registers. There is no external persistence. Critical gates for memory, OCRAM, ROM, AIPS, and MMDC IPG/fast paths prevent essential infrastructure from being disabled by unused-clock cleanup.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx6sll-clock.h`, standard CCF and i.MX-specific helpers, OF fixed-clock names, `imx_mmdc_mask_handshake()`, and UART clock registration. It feeds consumers for LCDIF, EPDC, LDB DI, PXP, CSI, USDHC, ECSPI, UART, I2C, GPIO, timers, watchdogs, SPBA, SSI/SPDIF/external audio, USB, and memory infrastructure.

## Risks
The PLL bypass clear sequence is hardware-sensitive and differs from drivers that use `clk_set_parent()` for bypass muxes. Several gates share one CCGR bit and depend on shared counters, so incorrect grouping can under- or over-gate audio clocks. `IMX6SLL_CLK_LDB_DI1_DIV_SEL` appears to use the same bit offset as DI0 in this source; if not intentional, display clock selection would be suspect. As with other i.MX drivers, `WARN_ON(!base)` does not abort after failed MMIO mapping.

## Test Signals
Expected test signals are clean provider registration, no missing-clock warnings, AHB settling at 132 MHz after the safe parent transition, working LCDIF and EPDC pixel clocks including LDB-derived alternatives, stable USDHC/UART/I2C/ECSPI operation, USB PHY clocks when enabled, and audio paths proving shared SSI/SPDIF/external-audio gates do not disable each other.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sx.c

## Purpose
`clk-imx6sx.c` registers the i.MX6 SoloX clock provider. It models a broad mixed application/MCU SoC topology: PLLs/PFDs, AXI/AHB/MMDC/OCRAM buses, display/LDB/LCDIF clocks, GPU clocks, M4 core clocking, PCIe, dual ENET references, QSPI, GPMI, audio, CAN/CANFD, and standard peripheral gates. It publishes `IMX6SX_CLK_*` IDs through a `clk_hw` onecell provider.

## Important APIs, Types, And Functions
The central function is `imx6sx_clocks_init()`, backed by `hws` and `clk_hw_data`. Static parent arrays encode mux input order for all major clock roots. Shared counter variables coordinate ASRC, ESAI, audio/SPDIF, SSI1/2/3, and SAI1/2 gates. The driver uses i.MX constructors for PLLv3, PFD, fixed-factor, mux, divider, busy mux/divider, gate2, shared gate2, and exclusive LVDS gates. It also uses `of_find_node_by_path()` to inspect whether LCDIF1 has assigned clock parents before applying a default display parent policy.

## Control Flow
The init path obtains fixed clocks and external display inputs, maps `fsl,imx6sx-anatop`, creates PLL bypass sources, PLLs, bypass muxes, PLL gates, USB PHY dummy gates, PCIe/ENET reference roots, LVDS exclusive gates, PFDs, fixed factors, and audio/video post dividers. It then maps CCM, registers a large set of muxes for bus, GPU, LDB, QSPI, ENET, M4, display, CSI, CLKO, and peripheral roots, followed by dividers and busy bus dividers. CCGR gate registration covers critical bus fabric, security, DMA, CAN, display, M4, ENET, QSPI, GPMI, ROM, audio, SAI, UART, USDHC, PWM, I2C, and USB blocks. Final policy masks MMDC handshakes, publishes the provider, enables USB PHY gates when configured, sets EIM, LCDIF1 defaults, PCIe LVDS parent, ENET rates, audio rates, VADC/CAN/GPU/QSPI parents, and UART aliases.

## State And Persistence
State is the `clk_hw` table, shared gate refcounts, OF node lookup result for LCDIF policy, and live hardware register contents. No disk persistence exists. Initial clock rates and parent choices persist as hardware state for the running system and are later mutable through normal CCF calls and assigned-clock processing.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/imx6sx-clock.h`, CCF, OF address lookup, `CONFIG_USB_MXS_PHY`, `imx_mmdc_mask_handshake()`, and board DT properties for external inputs and assigned display clocks. Consumers include Linux drivers for Cortex-M4 integration, PCIe, ENET/ENET2/PTP, LCDIF1/2, LDB, GPU, QSPI, GPMI NAND, ESAI/SSI/SAI/SPDIF, CANFD, USDHC, UART, ECSPI, I2C, PWM, and timers.

## Risks
This driver has many mux parent lists where ID order must exactly match hardware encoding. The LCDIF1 default policy depends on a hard-coded DT path, so alternative DT layouts may skip or misapply defaults. PCIe reference setup assumes LVDS1 and logs only on parent failure. Shared-gate groupings must match CCGR bit sharing. Rate changes for ENET, audio, GPU, and QSPI can affect board-specific constraints if assigned clocks are absent or incomplete.

## Test Signals
Good signals include no `imx_check_clk_hws()` warnings, ENET and ENET2 reference clocks at 125 MHz, ENET AHB at 200 MHz, EIM at 132 MHz, audio roots at 393.216 MHz/98.304 MHz/24.576 MHz where configured, working LCDIF1 fallback when DT lacks assigned parents, PCIe reference availability, M4 clock visibility, QSPI boot/storage operation, and GPU parent updates reflected in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6ul.c -->
# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6ul.c

## Purpose
`clk-imx6ul.c` registers the i.MX6UL and i.MX6ULL clock tree. It covers ANATOP PLL/PFD roots, CA7 step clocking, bus clocks, USDHC, NAND/GPMI/BCH/ENFC, LCDIF/SIM or EPDC, SAI/SPDIF/ESAI audio, dual ENET references selected through IOMUXC GPR, QSPI, CAN, UART, and low-speed peripheral gates. One `fsl,imx6ul-ccm` OF declaration serves both UL and ULL, with runtime compatibility checks for variant-only blocks.

## Important APIs, Types, And Functions
Provider state is `hws` plus `clk_hw_data`. `clk_on_imx6ul()` and `clk_on_imx6ull()` branch registration for SIM/CAAM versus EPDC/ESAI/DCP/AIPSTZ3 differences. Parent arrays define PLL bypasses, CA7 secondary/step, AXI, PERIPH/PERIPH2, USDHC, BCH/GPMI, EIM, SPDIF, SAI, LCDIF/SIM/EPDC, LDB, QSPI, ENFC, CAN, ECSPI, UART, PERCLK, CSI, and CLKO muxes. ENET reference selection is implemented with `imx_clk_gpr_mux()` using `IMX6UL_GPR1_ENET*_` bit tables and optional pad fixed clocks from OF.

## Control Flow
`imx6ul_clocks_init()` allocates the onecell table, obtains fixed and external display clocks, maps `fsl,imx6ul-anatop`, registers PLL bypass sources, PLLs, bypass muxes, roots, USB PHY dummy gates, PFDs, ENET reference dividers/gates, post dividers, and fixed factors. It maps CCM and registers variant-aware selectors: SIM muxes for i.MX6UL or EPDC/ESAI muxes for i.MX6ULL. It then registers dividers, busy bus dividers, and CCGR gates, with conditional CAAM versus DCP/ENET placement and EPDC versus ENET/SIM gates. After masking MMDC handshake, it registers ENET GPR muxes, validates the table, publishes the provider, performs a safe AHB/PERIPH parent transition to get AXI to 264 MHz while keeping AHB within 133 MHz, sets ENET/CSI rates, enables AIPSTZ3 on ULL and USB PHY gates when needed, assigns CAN/SIM or EPDC/ENFC parents, selects internal ENET references, and registers UART clocks.

## State And Persistence
State is limited to the allocated provider table, shared gate refcounts for ASRC/audio/SAI/ESAI groups, and live ANATOP/CCM/IOMUXC-GPR register state. No filesystem persistence exists. Critical clock flags keep AIPS, MMDC, AXI, and ROM infrastructure alive. Variant branches leave some IDs meaningful only on the compatible SoC.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx6ul-clock.h`, CCF, OF fixed clocks, `imx_mmdc_mask_handshake()`, `imx_clk_gpr_mux()`, IOMUXC GPR definitions from `imx6q-iomuxc-gpr.h`, optional USB PHY support, and UART registration. Primary consumers are ENET MACs/PTP, LCDIF, EPDC on ULL, SIM on UL, GPMI NAND, USDHC, SAI/SPDIF/ESAI audio, CAN, QSPI, UART, ECSPI, I2C, PWM, ADC, timers, watchdogs, and security/DMA blocks.

## Risks
Variant branching is a major risk: a clock ID registered only for UL or ULL must not be used by the other DT. ENET reference selection crosses CCM and IOMUXC GPR state, so wrong table masks can drive pads incorrectly. The safe AHB transition is required because AHB must stay at or below 133 MHz; reordering those parent/rate writes can overclock the bus. Some gates intentionally share register bits for serial/ipg pairs; incorrect use of non-shared gates would break refcounting.

## Test Signals
Expected signals are no missing-clock warnings for the active compatible, AXI at the intended 264 MHz path with AHB restored to 132 MHz, PERCLK sourced from OSC, ENET1/2 references at 50 MHz and selected through GPR muxes, CSI at 24 MHz, working CAN from PLL3 80 MHz, SIM clocks on UL or EPDC/ESAI clocks on ULL, NAND/GPMI operation, USB PHY dummy gate enablement when configured, and stable UART console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6ul.c -->

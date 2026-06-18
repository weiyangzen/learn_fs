# subset-b-001098 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-vf610.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-vf610.c

### Purpose
`clk-vf610.c` is the early OF clock provider for Freescale/NXP Vybrid VF610 CCM/ANATOP clocks. It builds the full onecell clock table matching `dt-bindings/clock/vf610-clock.h`, covering fixed oscillators, PLLs, PFDs, bus dividers, peripheral muxes, gates, and clock defaults needed by VF610 devices.

### Important APIs, Types, And Functions
The key entry point is `vf610_clocks_init()`, installed with `CLK_OF_DECLARE("fsl,vf610-ccm")`. It uses i.MX helper wrappers from `clk.h`, including PLLv3, PFD, mux, divider, gate, gate2, exclusive gate, and fixed-factor helpers. `vf610_get_fixed_clock()` obtains named DT clocks with backward-compatible fixed-clock fallback. `vf610_clk_suspend()` and `vf610_clk_resume()` implement `syscore_ops` state save/restore for CSCMR, CSCDR, and CCGR registers.

### Control Flow, State, And Persistence
Initialization first registers dummy and oscillator roots, maps ANATOP and CCM registers, then creates the PLL bypass source muxes, PLLs, PFDs, system bus hierarchy, and large peripheral set. It forces PLL bypass muxes back to PLL parents, programs QSPI parents/rates, selects audio_ext for SAI clocks, enables a small init-on list, registers syscore PM, and finally publishes `clk_data` via `of_clk_add_provider()`. Suspend persistence is manual: selected mux/divider/gate registers are cached in globals and restored on resume.

### Dependencies, Integration Points, Risks, And Test Signals
This file depends on DT clock IDs, `fsl,vf610-anatop`, common i.MX clock primitives, syscore PM, and downstream device clock lookups by onecell index. Risks include hard `BUG_ON()` on missing MMIO nodes, mismatch with dt-binding IDs, invalid parent/rate programming before provider registration, incomplete register save/restore, and critical clocks being disabled by unused-clock cleanup. Test signals include booting VF610 DTs, onecell clock lookup by every binding ID, suspend/resume with peripheral clocks retained, QSPI/SAI rate checks, and init-on clocks surviving late unused-clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-vf610.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk.c

### Purpose
`clk.c` provides shared support code for NXP i.MX clock drivers. It centralizes the CCM spinlock, fixed-clock lookup fallbacks, common diagnostics, minor SoC register fixups, MMDC handshake masking, and temporary UART clock retention for early console users.

### Important APIs, Types, And Functions
Exported state includes `imx_ccm_lock` and `mcore_booted`. Utility APIs include `imx_unregister_hw_clocks()`, `imx_mmdc_mask_handshake()`, `imx_check_clocks()`, `imx_check_clk_hws()`, `imx_obtain_fixed_clock()`, `imx_obtain_fixed_clock_hw()`, `imx_obtain_fixed_of_clock()`, `imx_get_clk_hw_by_name()`, and `imx_cscmr1_fixup()`. Non-module builds also define `imx_register_uart_clocks()` and the late init cleanup path.

### Control Flow, State, And Persistence
Fixed-clock helpers first try DT nodes under `/clocks/<name>` or a named clock on a given node, then synthesize a fixed-rate clock if no provider exists. Clock check helpers scan arrays and log registration failures without aborting. `imx_cscmr1_fixup()` applies the documented XOR mapping for odd CSCMR1 ACLK divider encoding. Early console retention is driven by `earlycon`/`earlyprintk` setup parameters: stdout clocks are acquired and enabled early, then disabled and released in a `late_initcall_sync()`.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates OF clock providers, clkdev/common clock APIs, i.MX CCM register locking, command-line setup parsing, and board-specific drivers through exported helpers. Risks include NULL/ERR handling around `of_stdout`, fallback fixed clocks masking DT omissions, leaked UART clocks if acquisition stops mid-loop, and the CSCMR1 fixup being used on the wrong register field. Test signals include earlycon boot logs after unused-clock cleanup, DT-less build tests, registration failure logs, MMDC handshake register writes, and fixed-clock fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk.h -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk.h

### Purpose
`clk.h` is the shared private interface for i.MX clock drivers. It defines common PLL metadata, helper prototypes, and macro wrappers that turn common clock framework registrations into compact i.MX-specific declarations with consistent locking and flags.

### Important APIs, Types, And Functions
The header declares PLL families (`imx_pllv1_type`, `imx_pllv3_type`, `imx_pllv4_type`, `imx_pll14xx_type`, `imx_fracn_gppll_clk`, `imx_pll14xx_clk`), PFD/composite helpers, gate/mux/divider constructors, `to_clk()`, fixed-clock helpers, and SoC-specific composite APIs for i.MX7ULP, i.MX8ULP, i.MX8M, and i.MX93. It also declares globals such as `imx_ccm_lock` and `mcore_booted`.

### Control Flow, State, And Persistence
Most wrappers are inline or macro-level policy: gates, muxes, and dividers are registered with `imx_ccm_lock`; many clocks default to `CLK_SET_RATE_PARENT` or `CLK_SET_RATE_NO_REPARENT`; gate2 helpers encode i.MX CGR fields; composite helpers layer i.MX8M bus/core/firmware-managed flags. The header itself has no persistent state, but it standardizes how stateful register-backed clocks in C files use common spinlock protection and clock flags.

### Dependencies, Integration Points, Risks, And Test Signals
This header depends on Linux common clock provider APIs, bit helpers, and the implementation files for each declared PLL/composite type. It is a high-impact integration point because many SoC clock tables rely on its flag defaults. Risks include macro argument side effects, flag policy changes affecting broad clock trees, incorrect parent-rate propagation, and prototype drift with implementation files. Test signals are all i.MX clock driver build coverage, lockdep around shared CCM registers, rate propagation tests, and boot checks for SoCs using each PLL/composite helper family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/Kconfig

### Purpose
This Kconfig file exposes Ingenic CGU and TCU clock driver options for MIPS platforms and compile testing. It groups SoC-specific CGU drivers plus the shared TCU clock driver under an Ingenic clock menu.

### Important APIs, Types, And Functions
Important symbols are `INGENIC_CGU_COMMON`, the SoC selections `INGENIC_CGU_JZ4725B`, `JZ4740`, `JZ4755`, `JZ4760`, `JZ4770`, `JZ4780`, `X1000`, `X1830`, and `INGENIC_TCU_CLK`. Each CGU symbol selects the common CGU support, and the TCU option selects `MFD_SYSCON`.

### Control Flow, State, And Persistence
The configuration flow is dependency-driven: the menu appears for `MIPS || COMPILE_TEST`; SoC CGU symbols default to their `MACH_*` platform symbols; enabling any CGU pulls in common `cgu.o` and `pm.o` through the Makefile. `INGENIC_TCU_CLK` defaults to `MACH_INGENIC`, reflecting that timer/counter clock support is platform-wide rather than tied to one CGU table.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates architecture platform symbols, compile-test coverage, the Ingenic Makefile, and MFD syscon support for TCU regmaps. Risks include missing `select` relationships causing link failures, default mismatches leaving required clocks unbuilt, and bool/tristate expectations diverging from Makefile object composition. Test signals include allmodconfig/allyesconfig on MIPS and COMPILE_TEST, per-SoC defconfigs, and verifying selected objects match enabled symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/Makefile

### Purpose
The Ingenic Makefile maps Kconfig symbols to the CGU common objects, SoC-specific CGU tables, and TCU clock driver.

### Important APIs, Types, And Functions
It builds `cgu.o pm.o` when `CONFIG_INGENIC_CGU_COMMON` is enabled, one `*-cgu.o` file per SoC symbol, and `tcu.o` for `CONFIG_INGENIC_TCU_CLK`.

### Control Flow, State, And Persistence
Build composition is direct: SoC CGU options depend on and select the common implementation, so table files link against `ingenic_cgu_new()`, `ingenic_cgu_register_clocks()`, and `ingenic_cgu_register_syscore()`. There is no runtime state in this file, but the object list determines which OF_DECLARE registrations are present at boot.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay aligned with Kconfig names, source filenames, and dt-binding compatible coverage. Risks are missing common objects for a selected SoC, stale object names after file renames, or absent TCU support in platform builds. Test signals are kernel build matrix coverage for each `CONFIG_INGENIC_*` symbol and successful link of each OF clock declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.c

### Purpose
`cgu.c` implements the generic Ingenic Clock Generation Unit framework used by multiple JZ/X SoC clock tables. It turns declarative `ingenic_cgu_clk_info` entries into common clock framework clocks for external roots, PLLs, muxes, dividers, fixed dividers, gates, and custom SoC callbacks.

### Important APIs, Types, And Functions
Major internal operations are `ingenic_pll_recalc_rate()`, `ingenic_pll_determine_rate()`, `ingenic_pll_set_rate()`, PLL enable/disable/is_enabled, non-PLL parent/rate/gate operations, and `ingenic_register_clock()`. Public entry points are `ingenic_cgu_new()` and `ingenic_cgu_register_clocks()`. Gate helpers interpret `clear_to_gate`; divider helpers handle tables, busy bits, change-enable bits, stop bits, and parent bypass masks.

### Control Flow, State, And Persistence
`ingenic_cgu_new()` allocates a CGU, maps the OF MMIO region, records clock metadata, and initializes the spinlock. `ingenic_cgu_register_clocks()` allocates the onecell array, registers clocks in table order so parent indexes are available, and publishes the provider. Registration special-cases external clocks by obtaining named DT clocks and registering clkdev aliases. Runtime operations read/modify/write CGU registers under the shared CGU spinlock and poll stable/busy bits when hardware requires it.

### Dependencies, Integration Points, Risks, And Test Signals
The implementation depends on OF MMIO mapping, common clock registration, clkdev aliases, `readl_poll_timeout()`, and SoC tables with correct parent order. Risks include `BUG_ON()` for invalid parent/table encodings, insufficient parent array size, inaccurate PLL OD encodings, set-rate rejection when exact divider rates cannot be produced, and incomplete cleanup after provider failure. Test signals include booting every Ingenic compatible, rate changes through PLL/divider clocks, muxes with skipped parent slots, gate polarity tests, suspend/resume through PM helpers, and failure injection for missing external clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.h -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.h

### Purpose
`cgu.h` defines the declarative data model and public API used by Ingenic CGU SoC drivers. It describes PLL register layouts, mux fields, divider fields, fixed dividers, gate bits, custom ops, CGU instances, and private clock wrappers.

### Important APIs, Types, And Functions
Key types are `struct ingenic_cgu_pll_info`, `ingenic_cgu_mux_info`, `ingenic_cgu_div_info`, `ingenic_cgu_fixdiv_info`, `ingenic_cgu_gate_info`, `ingenic_cgu_custom_info`, `ingenic_cgu_clk_info`, `ingenic_cgu`, and `ingenic_clk`. The `CGU_CLK_*` bit flags describe clock capabilities. Public functions are `ingenic_cgu_new()` and `ingenic_cgu_register_clocks()`, and `to_ingenic_clk()` maps `clk_hw` to driver state.

### Control Flow, State, And Persistence
The header has no runtime control flow, but it defines how runtime code interprets state: clock tables index parents through the same array, PLLs can have custom M/N/OD calculators and set-rate hooks, dividers may require change-enable or busy polling, and gates can use inverted polarity plus stabilization delays. SoC files persist their clock topology in static arrays of this structure.

### Dependencies, Integration Points, Risks, And Test Signals
The header integrates common clock callbacks with OF onecell providers and SoC-specific DT binding IDs. Risks include field-order mistakes in positional initializers, unsupported combinations of `CGU_CLK_*` bits, parent index drift from dt-bindings, and custom clock ops bypassing generic protections. Test signals are compile warnings for initializer mismatches, provider registration of all table entries, rate/parent operations across mux/div/gate combinations, and ABI consistency with DT binding clock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4725b-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4725b-cgu.c

### Purpose
`jz4725b-cgu.c` supplies the table-driven CGU description for the Ingenic JZ4725B SoC, including external roots, one PLL, core/bus dividers, multimedia/storage dividers, gate-only peripherals, RTC selection, and USB device PHY gating.

### Important APIs, Types, And Functions
The important artifacts are register offset definitions, `pll_od_encoding`, CPCCR divider tables, `jz4725b_cgu_clocks[]`, and `jz4725b_cgu_init()`. The clock table uses `ingenic_cgu_clk_info` entries indexed by `dt-bindings/clock/ingenic,jz4725b-cgu.h`. Initialization calls `ingenic_cgu_new()`, `ingenic_cgu_register_clocks()`, and `ingenic_cgu_register_syscore()`.

### Control Flow, State, And Persistence
At boot, `CLK_OF_DECLARE_DRIVER("ingenic,jz4725b-cgu")` invokes initialization, creating one CGU instance and registering all clocks in binding order. Runtime behavior is inherited from `cgu.c`; table metadata controls PLL calculations, divider writes, gate bits, and parent selection. Critical persistence is mostly through generic CGU register state plus the PM syscore low-power-mode hook.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on the JZ4725B dt-binding indices, external `ext` and `osc32k` clocks, and downstream peripherals consuming names like `mmc0`, `lcd`, `tcu`, and `udc_phy`. Risks include comments marking uncertain parents for BCH/TCU, the `ext/512` clock using /256 despite its name, and global `cgu` limiting multiple instances. Test signals include boot with JZ4725B DT, RTC parent selection, USB device PHY enable polarity, MMC/LCD rate programming, and suspend/resume low-power entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4725b-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4740-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4740-cgu.c

### Purpose
`jz4740-cgu.c` describes the CGU clocks for Ingenic JZ4740-compatible SoCs. It provides the external roots, PLL, PLL-half divider, CPU/HCLK/PCLK/MCLK clocks, LCD/I2S/SPI/MMC/UHC/UDC functional clocks, and gate-only peripheral clocks.

### Important APIs, Types, And Functions
Important definitions include CGU register offsets, PLL control bit constants, divider tables, `jz4740_cgu_clocks[]`, and `jz4740_cgu_init()`. The table uses `CLK_IS_CRITICAL` for CPU and memory clocks and expresses the UDC gate with clear-to-gate polarity through the SCR register.

### Control Flow, State, And Persistence
The OF declaration for `ingenic,jz4740-cgu` initializes the CGU early, registers table entries in order, and installs the generic Ingenic syscore PM hook. Clock control flow after boot is generic: the common CGU ops calculate PLL rate, apply divider table values, update mux parents, and gate peripherals based on table fields.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the JZ4740 clock binding, external `ext` and `rtc` clocks, common CGU code, and consumers such as LCD, MMC, USB, UART, DMA, ADC, I2C, AIC, and TCU drivers. Risks include critical-clock flag omissions, UDC gate polarity mistakes, unused register constants, and mismatches between CPCCR divider tables and hardware. Test signals include JZ4740 boot, clock summary rates, USB UDC operation, LCD pixel clock changes, MMC clocking, and unused-clock cleanup preserving critical roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4740-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4755-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4755-cgu.c

### Purpose
`jz4755-cgu.c` provides the Ingenic JZ4755 CGU clock topology, derived from the JZ4725B model but expanded for H0/H1 buses, extra UARTs, TV encoder, camera interface, auxiliary CPU/AHB blocks, and additional peripheral gates.

### Important APIs, Types, And Functions
Key contents are register offsets, PLL OD and divider tables, `jz4755_cgu_clocks[]`, and `jz4755_cgu_init()`. The table defines external `ext`/`osc32k` roots, PLL and half-rate derivations, `ext half`, core/bus clocks, multiplexed/divided functional clocks, RTC mux/gate, and many gate-only clocks.

### Control Flow, State, And Persistence
The driver is registered with `CLK_OF_DECLARE_DRIVER("ingenic,jz4755-cgu")`, allowing the CGU node to also be a `simple-mfd` parent for child devices. Initialization allocates/registers the common CGU and registers syscore PM. Runtime parent/rate/gate behavior is entirely table-driven by `cgu.c`.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on JZ4755 DT binding indices, external clocks, common CGU operations, and child devices that consume clocks for LCD, MMC, I2S, SPI, TVE, CIM, UART, DMA, BCH, TCU, and USB PHY. Risks include lack of explicit critical flags on CPU/memory compared with similar files, uncertain comments for TSSI/IPU parents, and positional initializer fragility. Test signals include SoC boot, CPU/memory clock stability under unused-clock cleanup, USB PHY polarity, LCD/TVE muxing, and MMC/I2S rate control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4755-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4760-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4760-cgu.c

### Purpose
`jz4760-cgu.c` describes the CGU for Ingenic JZ4760 and JZ4760B SoCs. It adds dual PLLs, multiple AHB-style bus clocks, PLL0/PLL1-selectable functional clocks, and a broader gate set than earlier JZ47xx parts.

### Important APIs, Types, And Functions
Important items are register offsets, `pll_od_encoding`, CPCCR and PLL-half divider tables, the custom `jz4760_cgu_calc_m_n_od()` PLL calculator, `jz4760_cgu_clocks[]`, and `jz4760_cgu_init()`. The file declares OF compatibles for both `ingenic,jz4760-cgu` and `ingenic,jz4760b-cgu`.

### Control Flow, State, And Persistence
The custom PLL calculator chooses N, M, and OD with hardware-specific constraints before the generic CGU set-rate path writes PLL registers. The clock table marks CPU and memory clocks critical, creates mux/div/gate combinations for UHC, GPU, LCD/TVE, GPS, PCM/I2S/USB/MMC/SSI/CIM, and then gate-only peripherals. Generic PM syscore registration toggles low-power mode around suspend.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on JZ4760 binding IDs, common CGU code, external `ext` and `osc32k`, and consumers for USB, graphics, MMC, audio, camera, UART/I2C, DMA, VPU, and RTC. Risks include the TODO that PLL1 can depend on PLL0 but is modeled only from EXT, JZ4760B differences not implemented, PLL calculator edge cases, and gate delay assumptions for VPU/USB PHY. Test signals include rate setting for PLL0/PLL1-derived clocks, muxes with skipped parents, VPU delay behavior, USB PHY enable, and JZ4760B DT boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4760-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4770-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4770-cgu.c

### Purpose
`jz4770-cgu.c` provides the CGU clock table for Ingenic JZ4770 SoCs. It models dual PLLs, split H0/H1/H2/C1 buses, per-MMC muxes, media/storage functional clocks, USB PHY controls, and a custom UHC PHY clock.

### Important APIs, Types, And Functions
The notable custom code is `jz4770_uhc_phy_enable()`, `jz4770_uhc_phy_disable()`, `jz4770_uhc_phy_is_enabled()`, and `jz4770_uhc_phy_ops`, which manipulate OPCR and USBPCR1 bits. The table `jz4770_cgu_clocks[]` defines PLLs, mux/div/gate clocks, gate-only clocks, fixed `ext/512`, and RTC mux.

### Control Flow, State, And Persistence
OF initialization registers the common CGU and PM syscore hook. Generic clocks use `cgu.c` operations, while the UHC PHY custom clock directly sequences suspend and power bits outside generic gate metadata. C1 clock uses inverted gate semantics to disable CPU clock stop on idle, and VPU/USB PHY gates include stabilization delays.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the JZ4770 binding header, common CGU implementation, external roots, USB host/OTG blocks, MMC, graphics, camera, audio, DMA, and bus consumers. Risks include global `cgu` use inside custom ops, the TODO that PLL1 may depend on PLL0, direct register writes without the CGU lock in UHC PHY ops, and incorrect parent modeling for GPU/muxed clocks. Test signals include UHC PHY power sequencing, OTG PHY gate delay, MMC0/1/2 independent rates, C1 idle-stop behavior, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4770-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4780-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4780-cgu.c

### Purpose
`jz4780-cgu.c` defines the clock topology for the Ingenic JZ4780, including APLL/MPLL/EPLL/VPLL, CPU and bus muxes/dividers, DDR and multimedia clocks, USB OTG PHY rate/control, and a custom clock for bringing up the second CPU core.

### Important APIs, Types, And Functions
Custom operations include `jz4780_otg_phy_recalc_rate()`, `determine_rate()`, `set_rate()`, OTG PHY enable/disable/is_enabled, and `jz4780_core1_enable()`. The table `jz4780_cgu_clocks[]` uses `DEF_PLL()` for PLLs and defines mux/div/gate clocks for DDR, VPU, I2S, LCD, MSC, UHC, SSI, CIM, PCM, GPU, HDMI, BCH, RTC, and many gate-only peripherals.

### Control Flow, State, And Persistence
Initialization maps and registers the common CGU, then registers PM syscore. The OTG PHY custom clock constrains refclk rates to 12/19.2/24/48 MHz and updates USBPCR1 under the CGU lock; enable/disable toggles OPCR and USBPCR bits. `jz4780_core1_enable()` clears secondary CPU power-down/gate bits under lock, then polls LCR for power-up completion with timeout.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on the JZ4780 DT binding, common CGU code, common clock framework, USB PHY programming rules, and SMP/CPU bring-up users of the `core1` clock. Risks include custom USB writes racing with other PHY users, timeout handling for secondary CPU power-up, critical DDR/L2/CPU flags being mandatory, and skipped parent slots requiring correct index translation. Test signals include USB PHY refclk rate changes, CPU1 enable during SMP boot, DDR clock stability, display/audio/storage rate changes, and unused-clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4780-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.c

### Purpose
`pm.c` provides a minimal syscore PM hook for Ingenic CGU drivers. It sets the CGU low-power mode bit during suspend and clears it during resume when sleep PM is enabled.

### Important APIs, Types, And Functions
The exported entry point is `ingenic_cgu_register_syscore()`. Internal pieces are `ingenic_cgu_pm_suspend()`, `ingenic_cgu_pm_resume()`, `ingenic_cgu_pm_ops`, and `ingenic_cgu_pm`. The hardware state touched is `CGU_REG_LCR` bit `LCR_LOW_POWER_MODE`.

### Control Flow, State, And Persistence
Each SoC CGU init calls `ingenic_cgu_register_syscore(cgu)`. If `CONFIG_PM_SLEEP` is enabled, the function stores the CGU base in a global pointer and registers syscore ops. Suspend reads LCR and ORs in low-power mode; resume reads LCR and clears the bit. No broad clock register save/restore is done here.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `struct ingenic_cgu`, MMIO accessors, syscore PM, and SoC files calling it after mapping the CGU. Risks include the single global base assuming only one CGU, concurrent or repeated registration, and low-power bit semantics being shared across SoCs. Test signals include suspend/resume on each supported Ingenic SoC, verifying LCR bit transitions, and ensuring clocks remain functional after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.h -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.h

### Purpose
`pm.h` is the small interface between Ingenic SoC CGU drivers and the shared syscore PM helper.

### Important APIs, Types, And Functions
It forward-declares `struct ingenic_cgu` and declares `ingenic_cgu_register_syscore(struct ingenic_cgu *cgu)`.

### Control Flow, State, And Persistence
The header carries no runtime state. It lets each SoC-specific `*-cgu.c` file register the shared suspend/resume low-power-mode hook after the common CGU object is created.

### Dependencies, Integration Points, Risks, And Test Signals
Its integration point is narrow but important: every Ingenic CGU driver includes it to opt into the PM hook. Risks are mostly declaration drift if the implementation changes. Test signals are compile coverage of all SoC CGU files and PM suspend/resume paths using the registered syscore ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/tcu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/tcu.c

### Purpose
`tcu.c` implements common clock framework support for Ingenic Timer/Counter Unit clocks. It exposes timer channels, watchdog, and optional OST clocks as onecell `clk_hw` providers with selectable parents, prescalers, and stop-bit gates.

### Important APIs, Types, And Functions
Important types are `ingenic_soc_info`, `ingenic_tcu_clk_info`, `ingenic_tcu_clk`, and `ingenic_tcu`. Clock ops include enable/disable/is_enabled, get/set parent, recalc/determine/set rate. Setup functions are `ingenic_tcu_register_clock()`, `ingenic_tcu_probe()`, and `ingenic_tcu_init()`, registered for several `ingenic,*-tcu` compatibles.

### Control Flow, State, And Persistence
Probe obtains a regmap from the TCU syscon node, optionally gets/enables the parent `tcu` clock, allocates a fixed-size onecell provider, resets each channel TCSR to a default parent, registers channel clocks, registers watchdog with RTC as default parent, optionally registers OST, and adds the OF provider. Register access is gated by temporarily clearing stop bits because TCSR registers are only accessible when a channel is running. Syscore suspend disables the TCU parent clock and resume re-enables it.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on MFD syscon/regmap, `linux/mfd/ingenic-tcu.h`, common clock framework, clockchips, DT bindings, and CGU-provided parent clocks named `pclk`, `rtc`, `ext`, and sometimes `tcu`. Risks include global singleton state, legacy X1000 DTs missing the TCU clock, WARN-only regmap errors still returning success, cleanup index mistakes on partial registration, and parent mask interpretation via `ffs()`. Test signals include timer/watchdog clock lookup, parent switching, prescale rate rounding, boot with old X1000 DT, suspend/resume, and clocksource/watchdog operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/tcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/x1000-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/x1000-cgu.c

### Purpose
`x1000-cgu.c` defines the Ingenic X1000 CGU clock tree. It covers APLL/MPLL, CPU and bus clocks, DDR, MAC, I2S fractional PLL behavior, LCD, MSC, USB OTG, SSI, RTC, and gate-only peripherals.

### Important APIs, Types, And Functions
Custom code includes OTG PHY recalc/determine/set-rate and enable/disable/is_enabled ops, `x1000_i2spll_calc_m_n_od()`, and `x1000_i2spll_set_rate_hook()`. The main data is `x1000_cgu_clocks[]`, indexed by the X1000 binding header. `x1000_cgu_init()` registers the common CGU and syscore PM.

### Control Flow, State, And Persistence
OTG PHY rate control maps requested rates to 12/24/48 MHz USBPCR1 divider bits under the CGU lock, while USB PHY enable/disable toggles OPCR and USBPCR bits directly. I2S PLL rate calculation uses rational approximation and a post-write hook that clears `I2SCDR1` so the hardware recalculates its dependent divider. The rest of the runtime behavior is generic table-driven CGU mux/div/gate control.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on common CGU logic, `linux/rational.h`, USB PHY registers, X1000 DT bindings, and consumers for audio, LCD, MMC, MAC, SSI/SFC, TCU/OST, and DMA. Risks include global `cgu` in custom callbacks, exact PLL/rational constraints for audio, direct USB register writes without full locking, critical CPU/DDR flags being required, and legacy simple-mfd child probing. Test signals include I2S audio sample rates, USB PHY 12/24/48 MHz selection, DDR/CPU stability, MAC clock rates, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/x1000-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/x1830-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/x1830-cgu.c

### Purpose
`x1830-cgu.c` provides the CGU clock description for the Ingenic X1830 SoC. It models four PLLs with large OD encoding, CPU/bus/DDR clocks, MAC/LCD/MSC/SSI clocks, RTC selection, USB PHY custom control, and peripheral gates.

### Important APIs, Types, And Functions
Notable custom functions are `x1830_usb_phy_enable()`, `x1830_usb_phy_disable()`, `x1830_usb_phy_is_enabled()`, and `x1830_otg_phy_ops`. The large `pll_od_encoding[64]` table maps supported output divider values. `x1830_cgu_clocks[]` defines APLL/MPLL/EPLL/VPLL, muxes/dividers, and gates; `x1830_cgu_init()` registers the CGU.

### Control Flow, State, And Persistence
Initialization is OF-driven for `ingenic,x1830-cgu`, then common CGU registration publishes all clocks and PM hooks. USB PHY enable clears `OPCR_GATE_USBPHYCLK`, asserts `SPENDN0`, and clears OTG disable/SIDDQ; disable reverses those bits. Generic CGU code handles PLL rates, mux parent translation with skipped entries, divider busy/change bits, and gates.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include X1830 clock bindings, common CGU infrastructure, USB PHY register semantics, and consumers for MAC, LCD, MMC, SSI/SFC, I2C/UART, TCU, OST, and random-number blocks. Risks include supported OD values being sparse, custom USB ops using the global CGU pointer, critical CPU/DDR gate modeling, and parent selection across multiple PLL roots. Test signals include USB PHY enable state, PLL rate calculation with high OD values, display/storage/network clock rates, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/x1830-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/Kconfig

### Purpose
This Kconfig file exposes TI Keystone/K3 clock drivers: legacy Keystone PLL/PSC clocks, TI System Control Interface clocks, optional firmware scanning, and syscon-backed gate clocks.

### Important APIs, Types, And Functions
Symbols are `COMMON_CLK_KEYSTONE`, `TI_SCI_CLK`, `TI_SCI_CLK_PROBE_FROM_FW`, and `TI_SYSCON_CLK`. `TI_SCI_CLK` depends on `TI_SCI_PROTOCOL`; `TI_SYSCON_CLK` defaults on Keystone or K3; legacy common Keystone clocks depend on OF and Keystone architecture or compile testing.

### Control Flow, State, And Persistence
The file controls which objects in `drivers/clk/keystone/Makefile` are built. `TI_SCI_CLK_PROBE_FROM_FW` changes sci-clk discovery behavior at compile time: firmware-wide probing instead of DT-demand discovery. There is no runtime state here, but build selections determine which OF compatibles and platform drivers are available.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include architecture symbols, OF, the TI SCI protocol driver, and COMPILE_TEST. Risks include enabling SCI clocks without protocol support, firmware probing increasing boot time, and default symbol choices not matching board DTs. Test signals are Keystone and K3 defconfigs, allmodconfig, boot with TI SCI firmware, and DT nodes matching selected drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/Makefile

### Purpose
The Keystone Makefile connects Keystone/K3 clock Kconfig symbols to their implementation objects.

### Important APIs, Types, And Functions
It builds `pll.o gate.o` for `CONFIG_COMMON_CLK_KEYSTONE`, `sci-clk.o` for `CONFIG_TI_SCI_CLK`, and `syscon-clk.o` for `CONFIG_TI_SYSCON_CLK`.

### Control Flow, State, And Persistence
Build flow is direct object selection. The legacy PLL and PSC gate implementations are bundled under the common Keystone symbol, while TI SCI and syscon gate drivers are independently selectable and can be modular.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must match Kconfig and module metadata in the C files. Risks are link failures from stale object selection or missing objects for a compatible used in DT. Test signals include modular and built-in builds for each symbol and boot-time probing of the selected OF/platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/gate.c -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/gate.c

### Purpose
`gate.c` implements legacy Keystone PSC-based clock gates. It drives the Power Sleep Controller module/domain state machine so peripheral clocks can be enabled or disabled through common clock framework gate operations.

### Important APIs, Types, And Functions
Important types are `clk_psc_data` and `clk_psc`. Key functions are `psc_config()`, `keystone_clk_enable()`, `keystone_clk_disable()`, `keystone_clk_is_enabled()`, `clk_register_psc()`, `of_psc_clk_init()`, and `of_keystone_psc_clk_init()`. The OF compatible is `ti,keystone,psc-clock`.

### Control Flow, State, And Persistence
DT init maps `control` and `domain` register resources, reads `domain-id`, records domain transition base from domain zero, resolves parent and output name, registers a PSC clock, and adds a simple OF provider. Enabling/disabling takes the shared spinlock, programs MDCTL next state, optionally asserts local reset on disable, starts domain transition with PTCMD, polls PTSTAT, then polls MDSTAT until the requested state is reached.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on DT `reg-names`, PSC register layout, parent clocks, and early OF clock declaration. Risks include no timeout error propagation from polling loops, global transition base depending on domain zero being initialized, missing parent causing failure, and register mapping leaks only handled on init failure. Test signals include enabling/disabling PSC modules, MDSTAT MCKOUT state, boot ordering with multiple domains, invalid DT resource tests, and peripheral functionality after clock transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/pll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/pll.c

### Purpose
`pll.c` implements legacy Keystone PLL, PLL divider, and PLL mux clocks from device tree. PLL clocks are read-only rate providers that calculate output frequency from hardware multiplier/divider fields.

### Important APIs, Types, And Functions
Important types are `clk_pll_data` and `clk_pll`. Core functions are `clk_pllclk_recalc()`, `clk_register_pll()`, `_of_pll_clk_init()`, `of_keystone_pll_clk_init()`, `of_keystone_main_pll_clk_init()`, `of_pll_div_clk_init()`, and `of_pll_mux_clk_init()`. OF compatibles are `ti,keystone,pll-clock`, `ti,keystone,main-pll-clock`, `ti,keystone,pll-divider-clock`, and `ti,keystone,pll-mux-clock`.

### Control Flow, State, And Persistence
PLL init maps the control register, optional post-divider register, and optional main-PLL multiplier register, fills masks/shifts according to legacy or main PLL layout, registers the clock, and publishes a simple provider. Recalc reads multiplier, predivider, and postdivider fields, then computes `parent / (prediv + 1) * (mult + 1) / postdiv`. Divider and mux helpers map a single register, parse bit shift/mask properties, register standard CCF divider/mux clocks, and add OF providers.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF clock parents, DT properties `reg-names`, `fixed-postdiv`, `bit-shift`, and `bit-mask`, plus common clock divider/mux helpers. Risks include returning NULL instead of ERR_PTR from `clk_register_pll()` failure, missing iounmap paths in some mux/div error cases, no set-rate support, and DT mask values needing to match CCF field-width expectations. Test signals include PLL rate accuracy, main PLL multiplier split handling, fixed vs register postdiv, divider/mux provider lookup, and malformed DT property handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/sci-clk.c -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/sci-clk.c

### Purpose
`sci-clk.c` implements TI System Control Interface clock support for Keystone/K3 systems. It exposes firmware-managed clocks to the common clock framework and translates CCF operations into TI SCI protocol calls.

### Important APIs, Types, And Functions
Important types are `sci_clk_provider` and `sci_clk`. Clock ops include `sci_clk_prepare()`, `unprepare()`, `is_prepared()`, `recalc_rate()`, `determine_rate()`, `set_rate()`, `get_parent()`, and `set_parent()`. Discovery and registration are handled by `_sci_clk_build()`, `sci_clk_get()`, `ti_sci_scan_clocks_from_dt()` or `ti_sci_scan_clocks_from_fw()`, `ti_sci_init_clocks()`, `ti_sci_clk_probe()`, and `ti_sci_clk_remove()`.

### Control Flow, State, And Persistence
Probe gets a TI SCI handle, selects firmware-wide or DT-driven clock discovery at compile time, registers each discovered clock with generated names like `clk:<dev>:<clk>`, and adds an OF hw provider using a two-cell specifier. CCF prepare/put calls acquire or release firmware clock usage; rate operations ask firmware for current, best-match, and set frequencies; parent ops use firmware clock ID arithmetic. `determine_rate()` caches the last requested and resolved rate until parent changes.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on `TI_SCI_PROTOCOL`, firmware ABI behavior, OF phandle parsing for `clocks` and assigned-clock properties, sorted clock arrays for `bsearch()`, devm-managed CCF registration, and platform driver binding to `ti,k2g-sci-clk`. Risks include firmware scan boot-time cost, DT scan missing unused-but-needed clocks, parent count cropping to 255, cache staleness across firmware-side changes, and SCI errors returning zero rates or failed prepares. Test signals include assigned-clock handling, mux parent changes, rate setting within +/-10 percent window, duplicate DT references being de-duplicated, firmware scan builds, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/sci-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/syscon-clk.c -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/syscon-clk.c

### Purpose
`syscon-clk.c` implements syscon-backed TI gate clocks, primarily ePWM time-base clocks and AM62 audio reference clock gates. It exposes bit-controlled gates in simple MMIO registers through common clock framework providers.

### Important APIs, Types, And Functions
Important types are `ti_syscon_gate_clk_priv` and `ti_syscon_gate_clk_data`. Core functions are `ti_syscon_gate_clk_enable()`, `disable()`, `is_enabled()`, `ti_syscon_gate_clk_register()`, and `ti_syscon_gate_clk_probe()`. Static data tables cover AM654 EHRPWM, AM64 ePWM, AM62 ePWM, and AM62 audio refclk compatibles.

### Control Flow, State, And Persistence
Probe matches a compatible to a data table, maps the single MMIO resource, creates a regmap, counts gate entries, validates that AM62 audio refclk has a parent, allocates onecell hw data, registers each gate clock using an optional parent, then installs either a simple or onecell provider. Runtime enable/disable writes the gate bit through regmap; `is_enabled()` reads the same bit.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on platform-device probing, OF match data, devm MMIO/regmap setup, common clock gate semantics, and child consumers using the provider. Risks include warnings but continued provider registration when individual gate registration fails, generated names changing when a parent is present, single-parent assumption, and regmap write errors being ignored on disable/is_enabled. Test signals include clock lookup for each compatible, ePWM time-base enable bits, AM62 audio parent requirement, multi-clock onecell index behavior, and module unload through devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/syscon-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/kunit_clk_assigned_rates.h -->
## sources/distributed-fs/ceph-client/drivers/clk/kunit_clk_assigned_rates.h

### Purpose
`kunit_clk_assigned_rates.h` is a tiny test header that centralizes expected assigned-clock rate constants for clock KUnit tests.

### Important APIs, Types, And Functions
It defines `ASSIGNED_RATES_0_RATE` as `1600000` and `ASSIGNED_RATES_1_RATE` as `9700000`, guarded by `_KUNIT_CLK_ASSIGNED_RATES_H`.

### Control Flow, State, And Persistence
There is no runtime control flow or persistent state. The header supplies compile-time constants consumed by KUnit test code or test DT fixtures so expected rates remain shared.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are limited to inclusion by clock KUnit tests. Risks are stale constants if assigned-clock fixture data changes, or include-guard/name drift. Test signals are KUnit assigned-rate tests compiling and passing with these expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/kunit_clk_assigned_rates.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/Kconfig

### Purpose
This Kconfig file is the central build-selection surface for MediaTek common clock drivers. It exposes the shared MediaTek clock core, optional FHCTL support, and many SoC/topology-specific clock driver symbols for application processors, routers, multimedia islands, camera/image/video blocks, audio, GPU/mfg, I2C wrappers, storage, and other subsystems.

### Important APIs, Types, And Functions
Primary shared symbols are `COMMON_CLK_MEDIATEK` and `COMMON_CLK_MEDIATEK_FHCTL`. SoC roots include MT2701, MT2712, MT6735, MT6765, MT6779, MT6795, MT6797, MT7622, MT7629, MT7981, MT7986, MT7988, MT8135, MT8167, MT8173, MT8183, MT8186, MT8188, MT8192, MT8195, MT8196, MT8365, and MT8516. Subsystem symbols select or depend on their SoC roots and cover MMSYS, IMGSYS, VDEC/VENC, CAMSYS, AUDSYS, MFGCFG, VPPSYS, VDOSYS, WPESYS, IPESYS, IMP_IIC_WRAP, and related blocks.

### Control Flow, State, And Persistence
The menu is visible for `ARCH_MEDIATEK || COMPILE_TEST`. Root SoC symbols select `COMMON_CLK_MEDIATEK`; some newer or FHCTL-capable SoCs also select `COMMON_CLK_MEDIATEK_FHCTL`. Subsystem symbols generally depend on their root SoC symbol and often default to that root so a platform build pulls in the expected clock islands. Several display/camera/video symbols depend on VPPSYS or IMGSYS roots, encoding subsystem hierarchy in Kconfig rather than C code.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates with the MediaTek clock Makefile, reset-controller selection through the common core, architecture defaults for ARM/ARM64, COMPILE_TEST coverage, and DT compatibles implemented by the corresponding C files. Risks include inconsistent bool/tristate choices, default `m` subsystem clocks when built-in consumers need them early, dependency chains that omit required multimedia parents, typo-level help text or indentation issues, and enabling FHCTL only on SoCs that need it. Test signals include allmodconfig/allyesconfig, per-SoC defconfigs, module vs built-in link tests, DT boot on each SoC family, and clock/reset provider availability for subsystem devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/Kconfig -->

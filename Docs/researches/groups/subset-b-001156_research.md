<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a06g032-clocks.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a06g032-clocks.c

## Purpose
Implements the R9A06G032 system controller clock provider. Unlike the newer table-only Renesas CPG files, this driver owns a custom clock tree, special module gate sequencing, UART source selection, a generic PM domain that attaches managed clocks to devices, a DMAMUX register helper, USB host/device mode setup, and a restart handler.

## Important APIs, Types, And Functions
- `struct regbit`, `struct r9a06g032_gate`, and `struct r9a06g032_clkdesc` compactly describe system-controller bit locations, gate/reset/ready/idle controls, and each clock node.
- Descriptor macros `D_ROOT`, `D_FFC`, `D_DIV`, `D_GATE`, `D_MODULE`, and `D_UGATE` build the static `r9a06g032_clocks[]` table.
- `r9a06g032_sysctrl_set_dmamux()` is exported with `EXPORT_SYMBOL_GPL` and safely read-modify-writes the DMAMUX register.
- Custom CCF operations cover gates (`r9a06g032_clk_gate_ops`), dividers (`r9a06g032_clk_div_ops`), bit-select muxes (`clk_bitselect_ops`), and UART dual gates (`r9a06g032_clk_dualgate_ops`).
- `r9a06g032_clocks_probe()` registers all clocks, adds the OF onecell provider, installs the PM domain, sets reset policy, registers restart handling, and populates child devices.

## Control Flow
`subsys_initcall()` registers a platform driver for `renesas,r9a06g032-sysctrl`, then `platform_driver_probe()` calls the init-only probe. Probe allocates `r9a06g032_priv` and onecell storage, gets the external `mclk`, maps sysctrl registers, selects USB H2 mode based on a `renesas,rzn1-usbf` child node, clears stale reset causes, enables software/watchdog reset paths, and registers a restart handler. It iterates through `r9a06g032_clocks[]` in dependency order, resolving each parent from a prior clock index or `mclk`, and dispatches to fixed-factor, gate, divider, bit-select, or dual-gate registration. After registration it publishes the provider with `of_clk_add_provider()`, adds cleanup action, creates a genpd provider, saves `sysctrl_priv`, and populates child nodes.

## State And Persistence
Runtime state is the memory-mapped sysctrl register block and the singleton `sysctrl_priv`. Clock gate and DMAMUX writes are protected by `spinlock_t lock`. Gate enable writes the gate bit, deasserts reset, delays 5 us, sets ready, and clears the master idle request; disable reverses ready/idle and gate. Divider programming writes the divider value with bit 31 set as a latch bit. Restart persists only as a write to `RSTCTRL`. No filesystem or nonvolatile state is used.

## Dependencies And Integration Points
The driver integrates with Linux CCF, OF clock provider APIs, platform bus probing, generic PM domains, `pm_clk`, `of_platform_populate()`, sys-off restart registration, and the R9A06G032 DT binding IDs. It exposes the sysctrl DMAMUX helper through `<linux/soc/renesas/r9a06g032-sysctrl.h>`. Peripheral device nodes consume clocks through `#clock-cells`, while PM-domain attach scans each device's `clocks` property and only attaches descriptors marked `managed`.

## Risks And Edge Cases
Descriptor order is critical because parent names are pulled from already-registered clocks. Register offsets in `regbit` are encoded in 32-bit words, so byte/word confusion would toggle the wrong sysctrl bit. Some fields in `I_GATE()` are intentionally ignored, making table data look richer than the implementation. `clk_rdesc_get()` has no null-bit guard, so callers must avoid using the all-zero sentinel except where meaningful. Divider rate selection contains a UART-specific escape hatch to avoid changing shared UART group dividers. Gate registration marks already-enabled clocks critical because firmware or the CM3 may own them. `sysctrl_priv` is global and can return `-EPROBE_DEFER` to early DMAMUX consumers.

## Test Signals
Useful signals are successful boot on R9A06G032/RZN1 hardware, complete `/sys/kernel/debug/clk/clk_summary` registration, correct peripheral probe with PM clock attach/detach, working UART source switching without disabling the inactive group incorrectly, successful DMAMUX clients after probe, USB host/device mode matching DT, and successful `reboot` through the sysctrl restart path. Build coverage should include the exported symbol user and DT binding IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a06g032-clocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a07g043-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a07g043-cpg.c

## Purpose
Describes the RZ/G2UL CPG clock, module-stop, and reset topology for the shared `rzg2l-cpg` backend. It supports both ARM64 and RISC-V build variants by conditionally describing CPU-local clocks, resets, and no-PM clocks.

## Important APIs, Types, And Functions
- Exports `const struct rzg2l_cpg_info r9a07g043_cpg_info`.
- `r9a07g043_core_clks[]` describes external `extal`, PLL/fixed/divider/mux clocks, SDHI muxes, and exported core clocks.
- `r9a07g043_mod_clks[]` maps module IDs to parent clocks, CPG gate registers, gate bits, and bus MSTOP bits.
- `r9a07g043_resets[]` maps reset IDs to reset register offsets and bit positions.
- Critical lists `r9a07g043_crit_mod_clks` and `r9a07g043_crit_resets` keep CPU/interrupt/DMA paths alive.

## Control Flow
There is no local probe. A compatible selected by another Renesas CPG driver passes `r9a07g043_cpg_info` into the `rzg2l-cpg` core, which registers core clocks first, then module clocks and reset controls. SDHI mux definitions use `DEF_SD_MUX()` with status bits in `CPG_CLKSTATUS` and the shared `rzg2l_cpg_sd_clk_mux_notifier`.

## State And Persistence
State is represented by hardware CPG registers selected by packed `SEL_PLL_PACK()` and `DDIV`/`DIVPL` values, module stop registers, and reset registers. The file stores no runtime state itself. Conditional ARM64/RISC-V arrays change which IDs are valid and how many hardware module clocks/resets the info struct advertises.

## Dependencies And Integration Points
It depends on `<dt-bindings/clock/r9a07g043-cpg.h>` and `rzg2l-cpg.h` macros such as `DEF_INPUT`, `DEF_FIXED`, `DEF_SAMPLL`, `DEF_DIV`, `DEF_MUX`, `DEF_SD_MUX`, `DEF_MOD`, `DEF_COUPLED`, and `DEF_RST`. Device tree consumers use the binding IDs exported in the info struct. SDHI, CRU, LCDC, USB, Ethernet, I2C, SPI, SCI/SCIF, CANFD, ADC, TSU, DMAC, and CPU interrupt blocks are represented.

## Risks And Edge Cases
The ARM64 and RISC-V branches have different CPU module names, critical clocks, reset counts, and last hardware IDs. A mismatch between `num_hw_mod_clks`, `num_resets`, and DT binding IDs can hide valid clocks or expose invalid holes. SDHI mux tables use register encodings `{1, 2, 3}`, so the backend must preserve the non-zero values. Coupled LCDC/Ethernet clocks share gate/MSTOP control and should not be managed as independent hardware gates.

## Test Signals
Build with both `CONFIG_ARM64` and `CONFIG_RISCV` variants where applicable. On hardware, confirm clock summary includes expected core outputs, SDHI parent changes complete through status bits, critical DMAC/CPU clocks are never gated, resets deassert for each described peripheral, and peripheral probes succeed for SDHI, Ethernet, USB, serial, I2C, SPI, CANFD, ADC, TSU, and video blocks enabled in DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a07g043-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a07g044-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a07g044-cpg.c

## Purpose
Provides shared RZ/G2L and RZ/V2L (`r9a07g044`/`r9a07g054`) CPG descriptors for the `rzg2l-cpg` backend. It defines common clocks/modules/resets and conditionally appends DRP/STPAI resources for the RZ/V2L configuration.

## Important APIs, Types, And Functions
- Exports `r9a07g044_cpg_info` under `CONFIG_CLK_R9A07G044` and `r9a07g054_cpg_info` under `CONFIG_CLK_R9A07G054`.
- `core_clks.common` contains 56 common core clock descriptors, while `core_clks.drp` adds DRP clocks for RZ/V2L.
- `mod_clks.common` contains common module gates; `mod_clks.drp` adds STPAI/DRP module clocks.
- `r9a07g044_resets[]` includes common reset controls and the optional `R9A07G054_STPAI_ARESETN`.
- No-PM and critical lists protect video clocks and essential GIC/IA55/DMAC paths.

## Control Flow
The backend consumes one of the exported `rzg2l_cpg_info` structs. The G2L variant passes only the common arrays and uses `R9A07G044_TSU_PCLK`/`R9A07G044_TSU_PRESETN` as terminal IDs. The V2L variant increases `num_core_clks`, `num_mod_clks`, `num_hw_mod_clks`, and `num_resets` to include DRP/STPAI resources. SDHI and PLL5/DSI/GPU muxes are registered through shared RZG2L clock-type macros.

## State And Persistence
The file is declarative; persistent state is CPG hardware register content. It packs SDHI select/status registers, PLL selection, divider tables, module stop metadata, and reset offsets into static const arrays. Runtime suspend/resume behavior is handled by the backend and by no-PM lists for clocks that should not be automatically power-managed.

## Dependencies And Integration Points
It includes both `r9a07g044-cpg.h` and `r9a07g054-cpg.h`, and relies on `rzg2l-cpg.h`. It integrates with consumers for GPU, CRU, MIPI DSI, LCDC, SSI, USB, Ethernet, I2C, SCIF/SCI, RSPI, CANFD, GPIO, ADC, TSU, GPT/POEG/WDT, and optional STPAI/DRP.

## Risks And Edge Cases
Because one C file supports two SoCs, array sizes and terminal IDs must stay aligned with conditional members. `last_dt_core_clk` is set to the RZ/V2L DRP terminal, which is valid only because the backend sees the specific exported info counts. DRP module arrays must be physically adjacent to the common arrays due to the struct layout passed as a flat pointer. Coupled gates for LCDC and Ethernet share hardware control. DSI/GPU PLL mux/divider changes can affect active display or graphics paths if no-PM handling is wrong.

## Test Signals
Build both config variants and check that each exported info symbol is present only when expected. Hardware tests should probe SDHI, GPU, CRU, DSI/LCDC, Ethernet, USB, serial, I2C, SPI, CANFD, ADC, TSU, and optional STPAI/DRP. Inspect `clk_summary` for common plus optional DRP clocks, and exercise reset controls for all described reset IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a07g044-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a08g045-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a08g045-cpg.c

## Purpose
Describes the RZ/G3S CPG topology for the RZG2L-style backend, including G3S-specific divider/status registers, SDHI mux/divider notifications, PLL1/4/6 configuration packing, module gates, resets, critical clocks, and no-PM clocks.

## Important APIs, Types, And Functions
- Exports `const struct rzg2l_cpg_info r9a08g045_cpg_info`.
- Defines G3S-specific packed divider/select/status constants such as `G3S_DIVPL2B`, `G3S_DIV_SDHI0`, `G3S_SEL_PLL4`, and status fields in `G3S_CLKDIVSTATUS`/`G3S_CLKSELSTATUS`.
- `DEF_G3S_MUX` wraps generic mux type construction with high-word mask behavior.
- `r9a08g045_core_clks[]` covers PLL1, PLL2/3/4/6, SDHI selectors/dividers, bus clocks, oscillator outputs, and HP/TSU clocks.
- `r9a08g045_mod_clks[]`, `r9a08g045_resets[]`, critical lists, and `r9a08g045_no_pm_mod_clks[]` describe module integration.

## Control Flow
The shared backend registers the core clocks, using `DEF_G3S_PLL`, `DEF_SD_MUX`, and `DEF_G3S_DIV` for G3S-specific behavior. SDHI output clocks are rate-changeable with `CLK_SET_RATE_PARENT` and `rzg3s_cpg_div_clk_notifier` to coordinate divider changes against status bits. The exported info struct then allows module clocks and resets to be registered and used by DT consumers.

## State And Persistence
All runtime state lives in CPG divider/select/status, module stop, and reset registers. The descriptor lists mark GIC, IA55, DMAC, and VBAT as critical, DMAC resets as critical, and PCI low-power clock as no-PM. The file itself keeps no mutable state.

## Dependencies And Integration Points
Depends on `<dt-bindings/clock/r9a08g045-cpg.h>` and `rzg2l-cpg.h`. Integration points include GIC, IA55, DMAC, watchdog, three SDHI instances, SSI, USB, Ethernet, I2C, SCIF, GPIO, ADC, TSU, PCI, I3C, and VBAT domains. It also includes `<linux/pm_domain.h>` for backend structures/macros used by no-PM handling.

## Risks And Edge Cases
G3S divider writes require matching status-bit definitions; wrong status packing can hang rate changes. SDHI dividers have min/max rate hints and parent propagation, so SD card timing regressions are likely if mux tables or notifier arguments drift. VBAT is critical and should not be accidentally gated. `num_hw_mod_clks` and `num_resets` use the last binding ID plus one; binding/header changes must update these terminals.

## Test Signals
Build with the RZ/G3S clock option enabled. On target hardware, check `clk_summary`, SDHI clock switching under card timing changes, PCI low-power behavior, VBAT retention paths, GIC/IA55/DMAC availability, and reset control for USB, SDHI, Ethernet, I2C, serial, PCI, I3C, and VBAT blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a08g045-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a08g046-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a08g046-cpg.c

## Purpose
Provides an initial RZ/G3L CPG descriptor set for the RZG2L-style backend. The file is small and currently describes external clock inputs, PLL2/PLL3-derived core clocks, a minimal module-clock set, reset controls, and critical DMAC/CPU infrastructure.

## Important APIs, Types, And Functions
- Exports `const struct rzg2l_cpg_info r9a08g046_cpg_info`.
- Defines G3L-specific divider registers `G3L_CPG_PL2_DDIV`, `G3L_CPG_PL3_DDIV`, and status register `G3L_CLKDIVSTATUS`.
- `r9a08g046_core_clks[]` registers `extal`, Ethernet TX/RX external inputs, PLL2/PLL3 fixed clocks, and P0/P1/P3 dividers.
- `r9a08g046_mod_clks[]` currently lists GIC, IA55, DMAC, and SCIF0 clocks.
- `r9a08g046_resets[]` provides matching reset lines for GIC, IA55, DMAC, and SCIF0.

## Control Flow
The backend consumes the exported info struct and registers clocks from `r9a08g046_core_clks[]` before module clocks and resets. Core divider clocks use `DEF_G3S_DIV()` with G3L-specific control/status fields but no notifier. Module and reset consumers access entries by the DT binding IDs from `renesas,r9a08g046-cpg.h`.

## State And Persistence
State is entirely in CPG divider/status, module-stop, and reset registers. Critical lists keep GIC, IA55, and DMAC clocks/resets active. The external Ethernet input clocks are registered as CCF inputs but are not consumed by the small module list in this file yet.

## Dependencies And Integration Points
Depends on `<dt-bindings/clock/renesas,r9a08g046-cpg.h>` and `rzg2l-cpg.h`. It integrates with GIC, IA55 CPU-side clocks, DMAC, SCIF0, and advertised but currently sparse binding ranges up to `R9A08G046_BSC_X_BCK_BSC` and `R9A08G046_BSC_X_PRESET_BSC`.

## Risks And Edge Cases
The advertised `num_hw_mod_clks` and `num_resets` extend to BSC IDs even though only a subset is described in local arrays; this is normal for sparse ID spaces but should be validated by the backend. The file has no no-PM list. If future modules use Ethernet external inputs, mux/module descriptors must be added consistently. Divider table values are coarse and status bits must match hardware.

## Test Signals
Build with the RZ/G3L clock driver enabled. On hardware, verify boot-critical clocks are present, SCIF0 works, DMAC probes, critical resets remain deasserted, and the backend handles sparse module/reset IDs without exposing bogus clocks. Check `clk_summary` for external Ethernet input registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a08g046-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g011-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g011-cpg.c

## Purpose
Describes the RZ/V2M Clock Pulse Generator, Module Standby, and Software Reset resources for the RZG2L backend. It covers fixed PLL-derived clocks, read-only and writable mux/divider selections, module gates, reset lines with optional monitor bits, and critical CPU/peripheral clocks.

## Important APIs, Types, And Functions
- Exports `const struct rzg2l_cpg_info r9a09g011_cpg_info`.
- Defines PLL4 packing through `PLL4_CONF`, divider fields `DIV_A/B/D/E/W`, and selectors `SEL_B`, `SEL_CSI0`, `SEL_CSI4`, `SEL_D`, `SEL_E`, `SEL_SDI`, `SEL_W0`.
- `r9a09g011_core_clks[]` contains `extal`, main divisions, PLL1/2/4, divider clocks, muxes, and `.selb_d2`.
- `r9a09g011_mod_clks[]` maps SDI/eMMC, Ethernet, USB, timers, PWM, IIC, UART, CSI, GIC, PFC, and CA53 clocks.
- `r9a09g011_resets[]` uses `DEF_RST` and `DEF_RST_MON` for reset controls and monitored reset completion.

## Control Flow
The backend registers core clocks first, including read-only dividers/muxes for hardware-selected paths and writable muxes for SDI/CSI/UART selections. Module clocks are then registered by CPG register offset and bit; coupled Ethernet clocks share gate control. The reset provider uses monitor metadata for reset lines that need acknowledgement.

## State And Persistence
Runtime state is CPG register content only. The info struct sets `.has_clk_mon_regs = false`, so reset monitor behavior is explicitly per-reset where `DEF_RST_MON` is used rather than through common clock monitor registers. Critical clocks include CA53, multiple CPERI group pclks, GIC, SYC counter, and UART pclk.

## Dependencies And Integration Points
Depends on `<dt-bindings/clock/r9a09g011-cpg.h>` and `rzg2l-cpg.h`. Integrates with SDI/eMMC storage, Ethernet, USB, timer/PWM groups, IIC, watchdog, UART, CSI, PFC, GIC, and CA53 CPU clocking.

## Risks And Edge Cases
`LAST_DT_CORE_CLK` is zero because no core clocks are exported to DT through a contiguous range; backend handling of internal-only core IDs must stay correct. The file mixes read-only and writable muxes, so accidental writability changes can alter boot strap behavior. `num_resets = ARRAY_SIZE()` rather than last ID plus one, so reset IDs must be suitable for backend lookup semantics. Critical CPERI group clocks are shared by many timers/peripherals and should not be disabled.

## Test Signals
Boot RZ/V2M with storage, Ethernet, USB, timers, UART, CSI, and IIC enabled. Check CA53 and GIC stability, reset monitor completion for SDI/eMMC/Ethernet/SYC/PWM/CSI/watchdog lines, correct module gating through runtime PM, and correct clock rates for SDI and CSI mux selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g011-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g047-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g047-cpg.c

## Purpose
Defines the Renesas RZ/G3E CPG resources for the `rzv2h-cpg` backend. It describes PLL-derived core clocks, programmable dividers/muxes, Ethernet and XSPI external-clock selection, a large banked module-clock table, reset banks, and total MSTOP capacity.

## Important APIs, Types, And Functions
- Exports `const struct rzv2h_cpg_info r9a09g047_cpg_info __initconst`.
- `r9a09g047_core_clks[]` uses RZ/V2H-family macros such as `DEF_PLL`, `DEF_DDIV`, `DEF_CSDIV`, `DEF_SMUX`, and fixed-factor descriptors.
- `r9a09g047_mod_clks[]` uses bank/bit arguments plus `BUS_MSTOP()` metadata; it includes `DEF_MOD_CRITICAL`, `DEF_MOD_NO_PM`, and `DEF_MOD_MUX_EXTERNAL` variants.
- `r9a09g047_resets[]` maps resets with four numeric fields that encode reset and monitor bank/bit locations.
- `num_hw_mod_clks = 28 * 16` and `num_mstop_bits = 208` declare sparse hardware capacity.

## Control Flow
No local functions run. The `rzv2h-cpg` core receives the info struct, registers external inputs (`audio_extal`, `rtxin`, `qextal`), PLLs, derived clocks, then banked module clocks and resets. Module gates refer to parent core-clock IDs and bus MSTOP masks. Ethernet TX/RX module clocks can select external pins through `DEF_MOD_MUX_EXTERNAL`.

## State And Persistence
State is stored in RZ/V2H-family CPG PLL, divider, selector, module stop, and reset registers. This file is declarative and immutable after init. Critical module entries keep ICU and GIC clocks active; no-PM entries protect active video/XSPI-related clocks from automatic gating.

## Dependencies And Integration Points
Depends on `<dt-bindings/clock/renesas,r9a09g047-cpg.h>` and `rzv2h-cpg.h`. It integrates with DMAC, ICU, GIC, GPT, WDT, RSPI, RSCI/SCIF, I3C, RIIC, CANFD, SPI/XSPI, SDHI, USB2/USB3, Ethernet, PCIe, CRU, GPU, and TSU blocks.

## Risks And Edge Cases
Banked numeric descriptors are dense and easy to misalign; one wrong bank/bit can gate or reset an unrelated device. `DEF_MOD_MUX_EXTERNAL` for Ethernet depends on external clock parent names matching board DT. Sparse module capacity means array length is not the same as hardware ID space. No-PM clocks must match peripherals that continue driving video or SPI timing. Reset comments are the main human-readable mapping for the numeric `DEF_RST()` arguments.

## Test Signals
Build with the RZ/G3E clock option and boot with representative peripherals. Confirm `clk_summary` includes CA55, XSPI, Ethernet, USB, CRU, GPU, and serial clocks; verify Ethernet external clock selection, SDHI timing, USB3/PCIe/video probe, and reset control across banked reset lines. Runtime PM should not gate critical or no-PM clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g047-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g056-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g056-cpg.c

## Purpose
Describes Renesas RZ/V2N CPG resources for the `rzv2h-cpg` backend. Compared with the smaller G3E file, it adds PLLDSI, PLLGPU, CRU1, ISP, DSI, LCDC, GPU, RTC, and TSU resources while preserving the common RZ/V2H-style banked module/reset model.

## Important APIs, Types, And Functions
- Exports `const struct rzv2h_cpg_info r9a09g056_cpg_info __initconst`.
- Uses `RZV2H_CPG_PLL_DSI_LIMITS()` and `PLL_PACK_LIMITS()` to define constrained DSI PLL programming.
- `r9a09g056_core_clks[]` contains PLLCM33/CLN/DTY/CA55/VDO/ETH/DSI/GPU clocks, gear dividers, muxes, Ethernet fixed clocks, XSPI status-aware fixed clock, and USB/core outputs.
- `r9a09g056_mod_clks[]` maps DMAC, ICU/GIC, GTM, WDT, RTC, RSPI, RSCI, SCIF, I3C, RIIC, CANFD, SPI/XSPI, SDHI, USB, Ethernet, PCIe, CRU, ISP, DSI, LCDC, GPU, and TSU.
- `r9a09g056_resets[]` provides a large banked reset table for the same domains.

## Control Flow
The backend registers core clocks from the exported info struct, including constrained PLLDSI and PLLGPU gear paths. It then registers module clocks using the bank/bit/reset metadata and bus MSTOP masks. Reset controls are exported from the reset table. No code in this file executes outside backend-driven registration.

## State And Persistence
Hardware CPG registers hold all state. The descriptor arrays mark ICU/GIC clocks critical and use no-PM for CRU video clocks. `num_hw_mod_clks = 25 * 16` and `num_mstop_bits = 192` describe the sparse module and MSTOP spaces.

## Dependencies And Integration Points
Depends on `<linux/clk/renesas.h>`, `<dt-bindings/clock/renesas,r9a09g056-cpg.h>`, and `rzv2h-cpg.h`. It integrates with display/camera pipelines, GPU, Ethernet with optional external TX/RX clocks, USB2/USB3, PCIe, SDHI, serial/I2C/SPI/CAN, DMAC, and CPU/interrupt infrastructure.

## Risks And Edge Cases
DSI and GPU PLL limits must match silicon constraints or display/GPU rate requests can be rejected or misprogrammed. `DEF_FIXED_MOD_STATUS` for `spi_clk_spi` implies module status coordination; changing it to a plain fixed clock would lose status awareness. RZ/V2N omits some USB2 host and WDT resources present on related parts, so copying entries between sibling files can create invalid IDs. Banked reset ordering must match the binding comments.

## Test Signals
Test boot with display, camera, GPU, Ethernet, USB, PCIe, SDHI, serial, and timer blocks enabled. Check DSI PLL rate requests, GPU gear rates, CRU no-PM behavior, Ethernet external clock muxing, reset deassertion, MSTOP bit accounting, and sparse clock ID lookup. Build-time validation should catch binding symbol drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g056-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g057-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g057-cpg.c

## Purpose
Describes Renesas RZ/V2H(P) CPG resources for the `rzv2h-cpg` backend. It is the fuller sibling of RZ/V2N, adding CRU2/CRU3 and USB3_1 core/ref clocks while retaining PLLDSI, PLLGPU, ISP, display, GPU, Ethernet, PCIe, SDHI, and serial resources.

## Important APIs, Types, And Functions
- Exports `const struct rzv2h_cpg_info r9a09g057_cpg_info __initconst`.
- Defines DSI PLL limits with `RZV2H_CPG_PLL_DSI_LIMITS()` and `PLL_PACK_LIMITS()`.
- `r9a09g057_core_clks[]` registers RZ/V2H PLLs, gear dividers, SMUX/CSDIV paths, four CRU VDO dividers, DSI/GPU gears, and USB2/USB3 core outputs.
- `r9a09g057_mod_clks[]` includes dense banked module descriptors for DMAC, ICU/GIC, GTM, RTC/WDT, RSPI/RSCI/SCIF, I3C/RIIC/CAN, SPI/XSPI, SDHI, USB2/USB3, Ethernet, PCIe, four CRUs, ISP, DSI/LCDC, GPU, and TSU.
- `r9a09g057_resets[]` maps the corresponding banked reset lines, including USB3_1 and CRU2/CRU3 resets.

## Control Flow
The shared RZ/V2H backend consumes this info struct. It registers clocks, gates, MSTOP bits, and resets based solely on the descriptors. External Ethernet module mux entries are resolved by the backend to allow internal or board-provided TX/RX clocks.

## State And Persistence
All mutable state is in hardware registers. The descriptor arrays are init const data. `num_hw_mod_clks = 25 * 16` and `num_mstop_bits = 192` describe the clock/MSTOP spaces. Critical ICU/GIC and no-PM video entries shape runtime PM behavior.

## Dependencies And Integration Points
Depends on `<linux/clk/renesas.h>`, `<dt-bindings/clock/renesas,r9a09g057-cpg.h>`, and `rzv2h-cpg.h`. The table integrates with CPU/interrupt controllers, DMA, timers, RTC/WDT, serial/I2C/SPI/CAN, storage, USB, Ethernet, PCIe, camera/display, DSI/LCDC, GPU, and thermal sensor peripheral clocks.

## Risks And Edge Cases
The file is highly similar to RZ/V2N but not identical; copying fixes between them can accidentally remove USB3_1 or CRU2/3 resources. PLLDSI/PLLGPU and VDO divider tables must match silicon rate constraints. Banked clock/reset descriptors are numeric and error-prone. Ethernet external mux entries depend on DT-provided external clock names. No-PM video clocks are required to keep active scanout/capture paths stable.

## Test Signals
Build and boot on RZ/V2H/P hardware. Confirm USB3_0 and USB3_1 clocks/resets, all four CRU video clocks, DSI/LCDC, GPU, Ethernet external clock selection, PCIe, SDHI, and serial/I2C/SPI/CAN functionality. Use runtime PM and `clk_summary` to verify no critical or no-PM clocks are gated unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g057-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g077-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g077-cpg.c

## Purpose
Implements the RZ/T2H and RZ/N2H-style CPG/MSSR description and custom clock registration for `renesas-cpg-mssr`. It provides fixed/mux/divider core clocks, module clocks, a two-block register layout, and special XSPI divider rate selection that respects FSELXSPI hardware limits.

## Important APIs, Types, And Functions
- Exports `const struct cpg_mssr_info r9a09g077_cpg_mssr_info`.
- Register packing helpers `RZT2H_REG_CONF`, `CONF_PACK`, `GET_REG_OFFSET`, `GET_SHIFT`, and `GET_WIDTH` encode block, offset, shift, and width into `core->conf`.
- Custom clock types `CLK_TYPE_RZT2H_DIV`, `CLK_TYPE_RZT2H_MUX`, and `CLK_TYPE_RZT2H_FSELXSPI` extend `CLK_TYPE_CUSTOM`.
- `r9a09g077_core_clks[]` defines LOCO, PLL0/1/2/4 selections, SCI/SPI async dividers, XSPI parent selection, CPU clocks, bus clocks, SDHI/USB/Ethernet/CAN/XSPI clocks.
- `r9a09g077_cpg_clk_register()` dispatches to divider, mux, or FSELXSPI registration and chooses `pub->base0` or `pub->base1` from the packed offset.

## Control Flow
The `renesas-cpg-mssr` core invokes the custom `cpg_clk_register` callback for each custom core clock. Divider and mux clocks use devm CCF helper registration with the backend RMW lock. FSELXSPI registration allocates a modified copy of `clk_divider_ops` with `determine_rate` overridden by `r9a09g077_cpg_fselxspi_determine_rate()`. That determine-rate path scans legal divider-table entries, asks the parent mux which DIVSELXSPI parent rate can be provided, rejects illegal 600 MHz/divider combinations, and selects the closest legal output.

## State And Persistence
State is in SCKCR/SCKCR2/SCKCR3 registers across two register blocks, plus MSSR module-stop registers managed by the backend. `xspi_div_ops` is a static pointer initialized once during FSELXSPI registration but allocated devm against the current device. No reset table is provided in this file. `reg_layout = CLK_REG_LAYOUT_RZ_T2H` tells the backend how module IDs map to hardware registers.

## Dependencies And Integration Points
Depends on `<dt-bindings/clock/renesas,r9a09g077-cpg-mssr.h>`, `<dt-bindings/clock/renesas,r9a09g087-cpg-mssr.h>`, and `renesas-cpg-mssr.h`. Module clocks cover XSPI, SCI, IIC, SPI, ADC, TSU, CANFD, GMAC/Ethernet switch/subsystem, USB, and SDHI. The same info shape can serve related binding sets.

## Risks And Edge Cases
The fixed-factor definitions use multipliers/dividers in the CCF sense, so PLL constants must be verified against hardware naming. FSELXSPI uses `to_clk_fixed_factor()` on parent hardware, which assumes the selected parents are fixed-factor clocks; changing parent types could break this logic. The static `xspi_div_ops` is devm-allocated and reused, so it assumes a single device lifetime. Packed register block/offset bits must remain within the field masks. Incorrect `num_hw_mod_clks = 14 * 32` can hide or overexpose module IDs.

## Test Signals
Build the RZ/T2H/N2H CPG-MSSR path and boot with XSPI, SCI, SPI, I2C, Ethernet, USB, SDHI, ADC, TSU, and CANFD enabled. Exercise `clk_round_rate()`/`clk_set_rate()` for XSPI at 800 MHz and 600 MHz parent modes, verify illegal divider combinations are skipped, and inspect module-stop behavior through runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a09g077-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.c

## Purpose
Provides shared helper code for R-Car CPG drivers, especially synchronized register modification, simple suspend/resume register save/restore, SD/SDH divider clocks, and RPC/RPCD2 composite clocks.

## Important APIs, Types, And Functions
- Defines global `DEFINE_SPINLOCK(cpg_lock)` exported via the header.
- `cpg_reg_modify()` performs locked read-modify-write on one MMIO register.
- `cpg_simple_notifier_call()` and `cpg_simple_notifier_register()` save a register on suspend and restore it on resume.
- `cpg_sdh_clk_register()` registers an SDH divider-table clock and registers a notifier for the SDnCKCR register.
- `cpg_sd_clk_register()` registers the lower SD divider.
- `cpg_rpc_clk_register()` registers a composite divider/gate RPC clock and a notifier for RPCCKCR.
- `cpg_rpcd2_clk_register()` registers a fixed divide-by-2 plus gate clock sharing RPCCKCR.

## Control Flow
Generation-specific drivers call these helpers from their `*_cpg_clk_register()` switch cases. Registration allocates small CCF wrapper structures, initializes divider/gate/fixed-factor members, and calls `clk_register_*` or `clk_register_composite()`. Suspend/resume notifiers are registered on the backend raw notifier chain; on suspend they read the saved register and on resume they restore it.

## State And Persistence
State includes the global spinlock, allocated wrapper objects, CCF clock hardware, and `struct cpg_simple_notifier.saved` snapshots across suspend/resume. Hardware state is SDnCKCR and RPCCKCR content. The helper supports reading legacy/firmware SDH divider encodings but Linux will sanitize by using recommended table entries.

## Dependencies And Integration Points
Used by R-Car Gen3 and Gen4 CPG code, and conceptually by shared CPG-MSSR registration. Depends on Linux CCF divider/gate/fixed-factor/composite operations, raw notifier chains, PM events, and MMIO helpers. The header declares its public surface.

## Risks And Edge Cases
All users share `cpg_lock`; mixing it with generation-local locks must avoid deadlock. The notifier only saves one 32-bit register per object and blindly restores it, so register fields controlled elsewhere during suspend must be considered. RPC and RPCD2 share RPCCKCR but only RPC owns the notifier. SDH divider tables include non-recommended encodings to tolerate firmware state, so initialization must normalize if needed.

## Test Signals
Build Gen3/Gen4 CPG drivers that call these helpers. On hardware, verify SDHI and RPC clocks register, gate, divide, and survive suspend/resume. Use clock debugfs to check rates and gates before and after PM cycles, and test concurrent clock rate/gate operations for lock coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.h

## Purpose
Declares shared R-Car CPG helper APIs and data structures used by generation-specific CPG drivers.

## Important APIs, Types, And Functions
- Declares `extern spinlock_t cpg_lock`.
- Defines `struct cpg_simple_notifier` with a notifier block, MMIO register pointer, and saved 32-bit value.
- Declares `cpg_simple_notifier_register()` and `cpg_reg_modify()`.
- Declares clock registration helpers for SDH, SD, RPC, and RPCD2 clocks.

## Control Flow
This header has no executable flow. R-Car generation drivers include it and call the declared helpers while processing SoC-specific `cpg_core_clk` descriptors. The notifier structure is embedded in helper-allocated clock wrappers or allocated directly by generation drivers when a register must be restored after resume.

## State And Persistence
The header defines the shape of per-register suspend/resume state through `saved`. It also exposes the shared spinlock used by helper and generation code to serialize MMIO read-modify-write operations.

## Dependencies And Integration Points
Depends on CCF `struct clk`, Linux `__init`, `void __iomem`, and raw notifier infrastructure through included users. It is paired with `rcar-cpg-lib.c` and used by R-Car Gen3/Gen4 CPG implementations.

## Risks And Edge Cases
The shared lock is global, so users must avoid taking it recursively. Callers must pass valid CPG register addresses and notifier heads whose lifetime outlives registered notifiers. The helper declarations assume parent names are stable CCF names.

## Test Signals
Compile all users of the header. Runtime signals are indirect: successful registration of SDH/SD/RPC/RPCD2 clocks, correct rates/gates, and suspend/resume restoration for registers registered through `cpg_simple_notifier`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.c

## Purpose
Implements R-Car Gen2 custom CPG clock registration for `renesas-cpg-mssr`. It handles mode-pin-derived fixed factors, PLL configuration, an adjustable CPU Z clock, ADSP/RCAN composite clocks, and SDHI divider quirks.

## Important APIs, Types, And Functions
- `rcar_gen2_cpg_init()` stores the SoC PLL config, PLL0 divider, mode pins, and SoC quirks.
- `rcar_gen2_cpg_clk_register()` is the backend callback that maps `enum rcar_gen2_clk_types` to CCF clocks.
- `struct cpg_z_clk` plus `cpg_z_clk_ops` implements adjustable Z rate with FRQCRC fields and FRQCRB KICK polling.
- `cpg_rcan_clk_register()` creates a divide-by-6 plus gate composite clock.
- `cpg_adsp_clk_register()` creates a divider-table plus gate composite clock.
- SDH/SD divider tables model Gen2 SDHI register encodings, with an `SD_SKIP_FIRST` quirk for `r8a77470`.

## Control Flow
SoC-specific Gen2 code calls `rcar_gen2_cpg_init()` before the CPG-MSSR core registers clocks. For each custom core clock, the backend calls `rcar_gen2_cpg_clk_register()`, which resolves the parent from `pub->clks`, checks the clock type, and either returns a fixed-factor clock, a custom Z clock, a composite ADSP/RCAN clock, or an SD divider-table clock. Z rate changes write FRQCRC, set FRQCRB KICK, and spin until hardware clears KICK or times out.

## State And Persistence
Static initdata stores PLL config, PLL0 divider, mode pins, and quirk bits. Hardware state is in FRQCRB, FRQCRC, SDCKCR, PLL0CR, ADSPCKCR, and RCANCKCR. `cpg_lock` serializes composite gate/divider and SD divider accesses. No persistent software state survives beyond registered CCF objects.

## Dependencies And Integration Points
Depends on `renesas-cpg-mssr.h` for core descriptor types and `rcar-gen2-cpg.h` for enum/config definitions. It integrates with SoC files that define `cpg_core_clk` descriptors and call `rcar_gen2_cpg_init()`. It uses `soc_device_match()` for quirks and Linux CCF fixed-factor, divider, gate, composite, and custom `clk_hw` APIs.

## Risks And Edge Cases
The code assumes `rcar_gen2_cpg_init()` ran before registration; otherwise config pointers are invalid. PLL0 may be fixed from config or read from PLL0CR, so wrong `pll0_mult` use can misclock CPUs. Z clock KICK polling can return `-EBUSY` or `-ETIMEDOUT`. SD divider quirks are SoC revision specific. `cpg_z_clk_set_rate()` uses integer truncation and clamps multipliers to 1..32.

## Test Signals
Compile Gen2 SoC CPG drivers and boot representative Gen2 boards. Check CPU Z clock cpufreq/rate changes, SDHI rates especially on `r8a77470`, ADSP and RCAN gates, PLL-derived fixed rates from mode pins, and timeout-free KICK completion under rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.h

## Purpose
Defines the public Gen2 CPG interface used by R-Car Gen2 SoC descriptor files and the CPG-MSSR core callback.

## Important APIs, Types, And Functions
- `enum rcar_gen2_clk_types` assigns custom clock type IDs for main, PLL0/1/3, Z, LB, ADSP, SDH, SD0, SD1, QSPI, and RCAN clocks.
- `struct rcar_gen2_cpg_pll_config` carries extal divider and PLL multipliers, with `pll0_mult` allowed to be zero when PLL0CR should be read.
- Declares `rcar_gen2_cpg_clk_register()` and `rcar_gen2_cpg_init()`.

## Control Flow
SoC-specific code uses the enum values in `DEF_BASE()`/core clock descriptors, calls `rcar_gen2_cpg_init()` with mode and PLL data, and points CPG-MSSR at `rcar_gen2_cpg_clk_register()` for custom type registration.

## State And Persistence
The header itself stores no state. It defines the configuration structure whose values are cached by `rcar-gen2-cpg.c` during init.

## Dependencies And Integration Points
Depends on `CLK_TYPE_CUSTOM`, `struct cpg_core_clk`, `struct cpg_mssr_info`, and `struct cpg_mssr_pub` from the CPG-MSSR infrastructure. It is included by Gen2 SoC clock descriptor files.

## Risks And Edge Cases
Enum ordering starts at `CLK_TYPE_CUSTOM`; changing it can break descriptor interpretation. `pll0_mult == 0` is a meaningful sentinel. SoC files must pass a valid mode word and PLL config before registration.

## Test Signals
Build all Gen2 SoC users. Runtime validation comes from correct rate registration for every enum type and successful boot on boards using PLL0CR-derived and fixed PLL0 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.c

## Purpose
Implements R-Car Gen3 custom CPG clock registration for CPG-MSSR. It covers configurable PLL0/PLL2 clocks for CPU boost modes, adjustable Z/ZG clocks, SD/SDH and RPC helper integration, mode-pin and RCKCR-selected clocks, RCLK quirks, and fixed-factor PLL/core clocks.

## Important APIs, Types, And Functions
- `rcar_gen3_cpg_init()` stores PLL config, EXTALR clock index, mode pins, and SoC quirks.
- `rcar_gen3_cpg_clk_register()` maps `enum rcar_gen3_clk_types` to custom or fixed-factor CCF clocks.
- `struct cpg_pll_clk` and `cpg_pll_clk_ops` read/write PLL control registers and wait for PLLECR status.
- `struct cpg_z_clk` and `cpg_z_clk_ops` implement Z/Z2/ZG rate control through FRQCRC/FRQCRB fields and KICK polling.
- Uses shared helpers `cpg_sdh_clk_register()`, `cpg_sd_clk_register()`, `cpg_rpc_clk_register()`, `cpg_rpcd2_clk_register()`, and `cpg_reg_modify()`.

## Control Flow
SoC-specific Gen3 code calls `rcar_gen3_cpg_init()`. During CPG registration, each custom descriptor enters `rcar_gen3_cpg_clk_register()`, which resolves a parent, checks clock type, and returns a PLL, Z/ZG, helper-registered SD/RPC, or fixed-factor clock. RCLK may choose EXTALR based on mode pin MD28 or an R8A7796 ES1.0 quirk that writes RCKCR manually and registers a suspend/resume notifier. Mode-select clocks decode two parent/divider pairs packed into descriptor fields.

## State And Persistence
Static initdata holds PLL config, EXTALR index, mode pins, and quirks. Hardware state includes PLLECR/PLLxCR, FRQCRB/FRQCRC, RPCCKCR, RCKCR, and SDnCKCR registers. Z clocks cache `max_rate` at registration. Shared simple notifiers save RCKCR/SD/RPC registers across suspend/resume.

## Dependencies And Integration Points
Depends on `renesas-cpg-mssr.h`, `rcar-cpg-lib.h`, and `rcar-gen3-cpg.h`. Integrates with Linux CCF, PM notifier chains, SoC revision detection through `soc_device_match()`, cpufreq-style PLL/Z rate changes, SDHI, RPC, and RCLK external oscillator handling.

## Risks And Edge Cases
Config must be initialized before registration. PLL set-rate waits for status but does not explicitly set a kick bit, matching Gen3 hardware semantics. Z clock rate logic changes parent rate for boost modes and can return `-EBUSY`/`-ETIMEDOUT`. Packed high bits in `core->parent` and `core->div` are type-specific; wrong macros corrupt parent selection. R8A7796 ES1.0 RCKCR quirk writes hardware based on whether EXTALR has a nonzero rate.

## Test Signals
Build Gen3 SoC users and boot boards across normal and quirked revisions. Exercise cpufreq/boost transitions for PLL0/PLL2 and Z clocks, SDHI and RPC clocks, suspend/resume with RCKCR/SD/RPC state restoration, RCLK parent selection with and without EXTALR, and mode-pin-derived clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.h

## Purpose
Declares R-Car Gen3 custom clock types, descriptor-construction macros, PLL configuration, key register offsets, and the Gen3 CPG registration/init functions.

## Important APIs, Types, And Functions
- `enum rcar_gen3_clk_types` defines main, PLL0-4, SDH/SD, R, MDSEL, Z/ZG, OSC, RCKSEL, RPCSRC variants, RPC, RPCD2, and a SoC-specific base.
- Macros such as `DEF_GEN3_SDH`, `DEF_GEN3_SD`, `DEF_GEN3_MDSEL`, `DEF_GEN3_PE`, `DEF_GEN3_OSC`, `DEF_GEN3_RCKSEL`, `DEF_GEN3_Z`, `DEF_FIXED_RPCSRC_E3`, and `DEF_FIXED_RPCSRC_D3` pack descriptor fields for `rcar_gen3_cpg_clk_register()`.
- `struct rcar_gen3_cpg_pll_config` carries extal, PLL1, PLL3, and oscillator predivider data.
- Declares `rcar_gen3_cpg_clk_register()` and `rcar_gen3_cpg_init()`.

## Control Flow
Gen3 SoC descriptor files use the macros to populate `struct cpg_core_clk` arrays. The CPG-MSSR core calls the declared registration callback after `rcar_gen3_cpg_init()` caches SoC-specific mode/config values.

## State And Persistence
The header stores no runtime state. It defines packed fields that later become parent indices, divider values, mode-bit offsets, or register offsets consumed by the C implementation.

## Dependencies And Integration Points
Depends on the CPG-MSSR descriptor format and CCF-facing registration callback signature. It exposes `CPG_RPCCKCR` and `CPG_RCKCR` offsets to SoC files that need them.

## Risks And Edge Cases
Several macros pack two parent IDs or dividers into one integer; parent IDs must fit 16-bit fields. Enum order must stay compatible with existing descriptors. `DEF_GEN3_PE` hardcodes mode bit 12 semantics. Wrong `osc_prediv` or mode-bit packing causes silent rate errors.

## Test Signals
Compile all Gen3 SoC descriptor files and verify each custom type reaches the expected case in `rcar_gen3_cpg_clk_register()`. Runtime signals include correct SD/RPC/R/Z/PLL rates and mode-dependent parent selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.c

## Purpose
Implements R-Car Gen4 custom CPG clock registration for CPG-MSSR. It extends Gen3 patterns with Gen4 register offsets, fractional 8.25 and 9.24 PLL handling, Gen4 Z clock register selection, SD/RPC helper integration, SDSRC decoding, and mode-pin/oscillator fixed-factor clocks.

## Important APIs, Types, And Functions
- `rcar_gen4_cpg_init()` stores Gen4 PLL config, EXTALR index, and mode pins.
- `rcar_gen4_cpg_clk_register()` dispatches `enum rcar_gen4_clk_types` to fixed-factor, PLL, Z, SD/RPC, SDSRC, MDSEL, or OSC registration.
- `struct cpg_pll_clk` plus `cpg_pll_f8_25_clk_ops`, `cpg_pll_v8_25_clk_ops`, and `cpg_pll_f9_24_clk_ops` implement fractional PLL rate calculation and selected variable set-rate support.
- `struct cpg_z_clk` and `cpg_z_clk_ops` implement Z0/Z1/ZG rate control across FRQCRC0, FRQCRC1, and FRQCRB fields.
- Uses shared helpers `cpg_reg_modify()`, `cpg_sdh_clk_register()`, `cpg_sd_clk_register()`, `cpg_rpc_clk_register()`, and `cpg_rpcd2_clk_register()`.

## Control Flow
Gen4 SoC code calls `rcar_gen4_cpg_init()` and CPG-MSSR invokes `rcar_gen4_cpg_clk_register()` for custom clocks. Fixed PLL types use config multipliers/dividers or read `CPG_PLLxCR_STC`. Fractional PLLs register custom CCF clocks with recalc-only or recalc/determine/set ops. Variable 8.25 set-rate writes NI/NF fields, sets `CPG_PLLxCR0_KICK`, and polls PLLECR status. Z clocks select the correct FRQCR register based on packed offset and poll FRQCRB KICK after changes.

## State And Persistence
Static initdata stores the Gen4 config/mode. Hardware state is in PLLECR, PLLxCR0/CR1, FRQCRB/FRQCRC0/FRQCRC1, SD0CKCR1, RPCCKCR, SD registers, and mode-pin-dependent state. Z clocks cache `max_rate`. Shared notifiers from `rcar-cpg-lib` persist selected SD/RPC registers across suspend/resume.

## Dependencies And Integration Points
Depends on `renesas-cpg-mssr.h`, `rcar-gen4-cpg.h`, and `rcar-cpg-lib.h`. Integrates with Gen4 SoC descriptor files, cpufreq/boost paths, SDHI, RPC, CANFD/MSIOF/CSI/DSI external-clock register offsets exposed by the header, and Linux CCF fractional-rate APIs.

## Risks And Edge Cases
Variable fractional 9.24 PLL is explicitly not supported and falls through to fixed 9.24 behavior. Fractional rate math must avoid overflow and must match hardware NI/NF interpretation. `readl_poll_timeout()` waits on PLLECR status after KICK; wrong PLL index mapping in `CPG_PLLECR_PLLST()` will cause false timeouts. Z offsets outside 0..95 return `-EINVAL`. The `cpg_clk_extalr` init value is stored but not currently used in this implementation.

## Test Signals
Build Gen4 SoC users. On target boards, test PLL recalc against measured rates, variable 8.25 rate changes, Z clock rate changes and KICK timeout handling, SDHI/RPC clocks and suspend/resume, SDSRC-derived rates, and mode-pin-selected clocks. Confirm unsupported variable 9.24 users do not expect set-rate support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.h

## Purpose
Declares R-Car Gen4 custom clock types, descriptor macros, PLL configuration, selected CPG register offsets, and the Gen4 CPG registration/init functions.

## Important APIs, Types, And Functions
- `enum rcar_gen4_clk_types` defines main, PLL fixed/variable fractional types, SDSRC, SDH/SD, MDSEL, Z, OSC, RPCSRC, RPC, RPCD2, and SoC-specific base.
- Macros `DEF_GEN4_SDH`, `DEF_GEN4_SD`, `DEF_GEN4_MDSEL`, `DEF_GEN4_OSC`, `DEF_GEN4_PLL_F8_25`, `DEF_GEN4_PLL_V8_25`, `DEF_GEN4_PLL_F9_24`, `DEF_GEN4_PLL_V9_24`, and `DEF_GEN4_Z` build `cpg_core_clk` descriptors.
- `struct rcar_gen4_cpg_pll_config` carries extal, PLL1, PLL5, and oscillator predivider config.
- Exposes register offsets for SD0, CANFD, MSIOF, CSI, and DSI external clock controls.
- Declares `rcar_gen4_cpg_clk_register()` and `rcar_gen4_cpg_init()`.

## Control Flow
Gen4 SoC-specific descriptor files include this header to assign custom types and packed fields. The CPG-MSSR core calls the declared registration callback after SoC init provides PLL/mode data.

## State And Persistence
The header itself has no runtime state. It defines the compact descriptor encoding consumed by `rcar-gen4-cpg.c`, including PLL indexes in `.offset`, mode pins in `.offset`, and parent/divider pairs packed into 16-bit halves.

## Dependencies And Integration Points
Depends on CPG-MSSR descriptor macros and Linux CCF types. It is the interface between Gen4 SoC clock tables and the shared Gen4 implementation.

## Risks And Edge Cases
Enum stability is required for existing descriptors. Packed parent and divider fields must fit their bit widths. The variable 9.24 macro exists even though the implementation currently treats it as fixed. Register offsets exposed here must match the generation's CPG map.

## Test Signals
Compile all Gen4 SoC descriptor users. Runtime validation is indirect through successful registration and correct rates for PLL, Z, SD, RPC, MDSEL, OSC, and external-clock control descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.h -->

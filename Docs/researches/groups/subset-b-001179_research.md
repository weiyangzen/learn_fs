# Research: subset-b-001179

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a64.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a64.c

Purpose: Allwinner A64 main CCU driver. It describes the SoC clock tree, exported `clk_hw` IDs, bus/module gates, reset lines, and probe-time register normalization for the common clock and reset frameworks.

Important APIs, types, and functions: uses Sunxi CCU primitives such as `ccu_nk`, `ccu_nm`, `ccu_nkm`, `ccu_mp`, `ccu_div`, `ccu_mux`, and `ccu_gate`. The central tables are `sun50i_a64_ccu_clks`, `sun50i_a64_hw_clks`, `sun50i_a64_ccu_resets`, and `sun50i_a64_ccu_desc`. `sun50i_a64_ccu_probe()` maps MMIO, adjusts PLL defaults, calls `devm_sunxi_ccu_probe()`, and registers CPU PLL/mux notifiers.

Control flow: platform probe maps resource 0, forces the audio 1x divider to 1, seeds the MIPI PLL register, registers the descriptor, then wires notifiers so CPU rate changes gate/ungate PLL CPUX and temporarily reparent CPUX to the 24 MHz oscillator.

State and persistence: persistent state is hardware CCU register content. Software state is static descriptor tables plus devm-registered clocks/resets; no disk state exists. Reset mappings are bit offsets in bus reset registers.

Dependencies and integration points: binds `allwinner,sun50i-a64-ccu`, imports `SUNXI_CCU`, includes DT clock/reset bindings through `ccu-sun50i-a64.h`, and supplies clocks/resets consumed by CPUfreq, MMC, USB, display, GPU, CSI, audio, DRAM, and PRCM users.

Risks and test signals: register bit positions are high-risk because most behavior is table-driven. The MIPI PLL magic value and audio divider fixup are hardware assumptions. CPU notifier behavior should be tested with cpufreq transitions. Good signals are boot probe success, complete DT clock lookup coverage, reset deassert for peripherals, `/sys/kernel/debug/clk/clk_summary` rates, MMC/USB/display/audio operation, and suspend/resume sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a64.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a64.h

Purpose: private clock-ID header for the A64 CCU driver. It combines public DT binding IDs with internal IDs for non-exported or derived clocks used only inside the provider.

Important APIs, types, and functions: includes `<dt-bindings/clock/sun50i-a64-ccu.h>` and `<dt-bindings/reset/sun50i-a64-ccu.h>`, then defines internal IDs such as `CLK_OSC_12M`, `CLK_PLL_CPUX`, fixed-factor audio/peripheral/video clocks, bus roots, `CLK_USB_OHCI*_12M`, and `CLK_NUMBER`.

Control flow: no executable control flow; the macros are consumed by `ccu-sun50i-a64.c` when filling `struct clk_hw_onecell_data`.

State and persistence: no runtime state. The numeric values are ABI-adjacent because they index provider arrays and must not collide with DT binding IDs.

Dependencies and integration points: tightly coupled to the A64 binding headers and the `.hws` array in the C file. Comments document which clock ranges are exported by the public binding and which are local.

Risks and test signals: off-by-one `CLK_NUMBER` or ID overlap can make DT lookups return the wrong clock or `NULL`. Test by building the driver, checking all referenced IDs compile, and verifying clock consumers resolve expected providers at boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6-r.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6-r.c

Purpose: PRCM/R_CCU clock and reset driver for Allwinner H6 and H616 always-on domain clocks. It exposes AR100/R-AHB/R-APB roots, low-speed peripheral gates, IR/1-wire module clocks, and reset lines.

Important APIs, types, and functions: defines `ar100_clk`, `r_apb1_clk`, `r_apb2_clk`, fixed `r_ahb_clk`, APB gate clocks, `ir_clk`, and `w1_clk`. SoC-specific export tables are `sun50i_h6_r_hw_clks` and `sun50i_h616_r_hw_clks`; reset sets are `sun50i_h6_r_ccu_resets` and `sun50i_h616_r_ccu_resets`. `sun50i_h6_r_ccu_probe()` uses OF match data to select a descriptor.

Control flow: platform probe reads `.data` from the matching compatible, maps the MMIO resource, and passes the selected `sunxi_ccu_desc` to `devm_sunxi_ccu_probe()`. No additional register fixups are performed.

State and persistence: state lives in R_CCU MMIO gate/divider/mux/reset bits. The H6 and H616 variants share the same `ccu_common` objects but publish different onecell IDs and reset maps.

Dependencies and integration points: binds `allwinner,sun50i-h6-r-ccu` and `allwinner,sun50i-h616-r-ccu`, integrates with the Sunxi CCU framework, and supplies clocks for RTC/PIO-adjacent always-on peripherals, IR, RSB/I2C/UART, PWM/TWD/timer, and low-power firmware blocks.

Risks and test signals: several parent and divider definitions are derived from BSP/manual interpretation, so mis-modeling affects low-speed peripherals. Sharing common clock objects across variants requires the exported ID tables to hide unsupported clocks correctly. Test with DT lookup on both SoCs, IR receive rate checks, RSB/I2C function, RTC clock retention, and reset control assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6-r.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6-r.h

Purpose: private ID bridge for the H6/H616 PRCM CCU driver. It imports public DT clock/reset IDs and defines local bus-root indexes that are not all exported in bindings.

Important APIs, types, and functions: includes `sun50i-h6-r-ccu` clock/reset bindings, defines `CLK_R_AHB`, `CLK_R_APB2`, and `CLK_NUMBER` as `CLK_R_APB1_RTC + 1`.

Control flow: none; macros drive array indexes in `ccu-sun50i-h6-r.c`.

State and persistence: no runtime state. The numeric definitions must remain stable relative to the binding header values used by DT consumers.

Dependencies and integration points: used only by the H6/H616 R_CCU implementation to size and populate `clk_hw_onecell_data`.

Risks and test signals: wrong `CLK_NUMBER` truncates provider arrays; wrong private indexes can alias exported IDs. Build coverage and boot-time onecell lookup for `CLK_R_APB1_RTC`, `CLK_R_AHB`, and R peripheral clocks are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6-r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6.c

Purpose: main CCU driver for Allwinner H6. It models PLLs, CPU/bus roots, MBUS, module clocks, bus gates, fixed factors, reset lines, and H6-specific safe register defaults.

Important APIs, types, and functions: major objects include `pll_cpux_clk`, DDR/peripheral/GPU/video/VE/DE/HSIC/audio PLLs, CPU/AXI/PSI/AHB/APB divisors, module clocks for MMC/USB/display/HDMI/CEC/CSI/audio, `sun50i_h6_ccu_clks`, `sun50i_h6_hw_clks`, `sun50i_h6_ccu_resets`, `sun50i_h6_ccu_desc`, and `sun50i_h6_ccu_probe()`.

Control flow: probe maps CCU registers, fixes GPU PLL and GPU clock divider defaults, enables lock bits for all PLLs, clears video PLL output-divider bits, forces OHCI 12 MHz source muxes to a known parent, programs PLL audio post/output dividers for exact audio rates, selects the usable HDMI CEC parent, registers clocks/resets, then installs a CPU mux notifier for PLL CPUX rate changes.

State and persistence: all durable behavior is hardware register state. Static descriptor arrays persist for module lifetime. No runtime allocation beyond devm registration and no filesystem persistence.

Dependencies and integration points: binds `allwinner,sun50i-h6-ccu`, depends on common Sunxi CCU helpers, DT binding IDs, and common clock reset consumers. It is central to CPUfreq, DRAM/MBUS, MMC, USB2/USB3, HDMI/CEC, display engine/TCON, GPU, CSI, VE, and audio blocks.

Risks and test signals: H6 has several explicit hardware quirks: unmodeled PLL test dividers, mysterious OHCI muxes, exact audio SDM rates, and CEC parent selection. Regressions appear as clock rate miscalculation, PLL lock failures, or peripherals hanging. Test signals include clk summary rates, cpufreq stress, HDMI/CEC, USB OHCI/EHCI, MMC, display pipeline, audio 22.5792/24.576 MHz families, reset-controller use, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6.h

Purpose: internal clock-ID header for the H6 main CCU provider. It fills gaps around public DT binding IDs for PLL derivatives and non-exported root clocks.

Important APIs, types, and functions: includes H6 clock/reset binding headers and defines IDs for `CLK_OSC12M`, PLL CPUX/DDR/peripheral/GPU/video/VE/DE/HSIC/audio clocks, CPU and bus roots, `CLK_MBUS`, private DRAM IDs, and `CLK_NUMBER`.

Control flow: no code executes; the C driver uses these macros as indexes in onecell clock storage.

State and persistence: no state. The IDs determine provider array layout and must match references in `ccu-sun50i-h6.c`.

Dependencies and integration points: coupled to `dt-bindings/clock/sun50i-h6-ccu.h` and reset bindings. Comments identify clocks exported for PRCM, DVFS, PIO, and module consumers.

Risks and test signals: ID drift causes consumers to acquire the wrong clock or fail probing. Compile-time use catches missing names; runtime test signals are successful DT lookups for CPUX, APB1, MBUS, module clocks, and reset consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h616.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h616.c

Purpose: main CCU driver for Allwinner H616-family SoCs. It is derived from H6 but adapts PLL layout, audio PLL modeling, GPU clock handling, module gates, and reset coverage for H616.

Important APIs, types, and functions: defines CPUX, DDR0/DDR1, peripheral, GPU, video0/1/2, VE, DE, and audio PLLs; fixed-factor audio and video outputs; CPU/AXI/PSI/AHB/APB/MBUS roots; module clocks and gates; `sun50i_h616_ccu_clks`, `sun50i_h616_hw_clks`, `sun50i_h616_ccu_resets`, `sun50i_h616_ccu_desc`, PLL/mux notifiers for CPU and GPU, and `sun50i_h616_ccu_probe()`.

Control flow: probe maps registers, enables lock and output-enable bits on all PLLs, clears video PLL test dividers, normalizes OHCI 12 MHz muxes, configures audio PLL M0/M1 for SDM use, programs GPU1 input divider for a safe 400 MHz default, selects HDMI CEC’s usable parent, registers the CCU descriptor, then installs CPU and GPU mux/PLL notifiers for safe rate changes and relocking.

State and persistence: state is MMIO register bits for PLL factors, gates, muxes, resets, and lock enables. Software state is static tables plus devm-managed framework registrations.

Dependencies and integration points: binds `allwinner,sun50i-h616-ccu`, uses Sunxi CCU primitives and DT binding IDs, and feeds CPUfreq, GPU, DRAM/MBUS, MMC, USB, display/TCON, HDMI/CEC, CSI, VE, audio, bus gates, and reset consumers.

Risks and test signals: risks cluster around variant differences from H6: extra DDR/video PLLs, PLL output-enable bit handling, GPU notifier correctness, audio SDM dividers, and reset ID alignment. Test with clk summary, cpufreq and GPU DVFS/rate changes, HDMI CEC, USB OHCI/EHCI, MMC, display/audio bring-up, reset-controller consumers, and boot logs for PLL lock failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h616.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h616.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h616.h

Purpose: internal ID header for the H616 CCU provider. It augments public H616 binding IDs with private PLL/root IDs used in the driver’s onecell array.

Important APIs, types, and functions: includes `dt-bindings/clock/sun50i-h616-ccu.h` and reset bindings, defines IDs for oscillator, CPUX, DDR0/DDR1, peripheral, GPU, video, VE, DE, audio-HS/audio fixed factors, CPU/bus roots, MBUS, DRAM, bus DRAM, and `CLK_NUMBER`.

Control flow: no runtime execution; macros are consumed by `ccu-sun50i-h616.c`.

State and persistence: no state. Values are array indexes and are therefore correctness-sensitive.

Dependencies and integration points: coordinates the C driver with DT-exposed clock/reset IDs. Comments document which clocks are exported for PRCM, DVFS, PIO, and module use.

Risks and test signals: incorrect numbering can silently wire consumers to wrong clocks. Test via build, boot-time DT clock lookup, `clk_summary` name/rate inspection, and driver probes for CPU, MMC, USB, display, GPU, and audio consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h616.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-mcu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-mcu.c

Purpose: MCU-domain CCU driver for Allwinner A523. It covers the auxiliary audio PLL, DSP/audio clocks, MCU timers, MCU DMA/RISC-V/debug/message-box gates, NPU bus gates, SRAM/MBUS links, and corresponding reset lines.

Important APIs, types, and functions: uses `clk_parent_data` firmware parents (`hosc`, `r-ahb`, `r-apb0`, audio parents), `ccu_nm` with sigma-delta table for `pll_audio1_clk`, fixed-factor `pll_audio1_div2/div5`, dual-divider mux gates for I2S/SPDIF/DMIC/codec clocks, timer `P` mux gates, bus gate macros, `sun55i_a523_mcu_ccu_clks`, `sun55i_a523_mcu_hw_clks`, `sun55i_a523_mcu_ccu_resets`, and `sun55i_a523_mcu_ccu_probe()`.

Control flow: probe maps resource 0, reads `SUN55I_A523_PLL_AUDIO1_REG`, sets PLL enable/LDO/lock-enable bits that the generic PLL model does not represent separately, enforces BSP-style p1/p0 audio divider defaults, writes the register, then registers clocks and resets through `devm_sunxi_ccu_probe()`.

State and persistence: state is MCU CCU MMIO. Static descriptors define all clock topology; runtime software state is devm-managed. No persistent storage is used.

Dependencies and integration points: binds `allwinner,sun55i-a523-mcu-ccu`, imports A523 MCU DT binding IDs directly, depends on parent clocks supplied by main and R CCUs, and serves DSP/audio, MCU timer/DMA, RISC-V MCU, NPU, SRAM, PWM, and message-box consumers.

Risks and test signals: comments identify uncertain DSP parent order, BSP-only `tzma` gates, guessed SRAM parentage, and generic PLL limitations. Test signals include audio sample-rate families through PLL audio1 SDM, DSP clock selection, MCU timer ticks, reset deassert for RISC-V/DMA/PWM, NPU bus clock enablement, and correct probe ordering against main/R CCUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-r.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-r.c

Purpose: PRCM/R-domain CCU driver for Allwinner A523. It models always-on bus roots, timers, PWM, SPI, spinlock/message-box, UART/I2C, PPU, IR, DMA, RTC, CPU configuration gates, and resets.

Important APIs, types, and functions: defines parent-data arrays for `hosc`, `losc`, `iosc`, `pll-periph`, `pll-audio`, and named 300 MHz PLL derivatives. Core clocks are `r_ahb_clk`, `r_apb0_clk`, `r_apb1_clk`, timer clocks, `r_pwmctrl_clk`, `r_spi_clk`, `r_ir_rx_clk`, many `SUNXI_CCU_GATE_HW` bus gates, `sun55i_a523_r_hw_clks`, `sun55i_a523_r_ccu_resets`, `sun55i_a523_r_ccu_desc`, and `sun55i_a523_r_ccu_probe()`.

Control flow: probe maps the R_CCU MMIO resource and registers the static descriptor with `devm_sunxi_ccu_probe()`. There are no probe-time register fixups.

State and persistence: state is hardware mux/divider/gate/reset bits. Critical gates for R DMA and CPUCFG are marked `CLK_IS_CRITICAL` to keep always-on infrastructure available. Software state is static plus devm registration.

Dependencies and integration points: binds `allwinner,sun55i-a523-r-ccu`, depends on main PLL providers by firmware/name parent references, and provides low-power clocks/resets to R-domain peripherals and MCU-domain parents (`r-ahb`, `r-apb0`).

Risks and test signals: parent-name spelling is sensitive (`pll-periph0-300M`/`pll-periph1-300M` names must match providers). Critical flag choices affect power management. Reset array ordering includes PPU0 after CPUCFG but indexed by binding IDs, so ID validation matters. Test with R UART/I2C/SPI/IR operation, RTC, wake-capable peripherals, MCU CCU probe, reset-controller consumers, and clk summary parent resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-r.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-r.h

Purpose: minimal private header for the A523 R_CCU provider. It imports public A523 R-domain clock/reset IDs and defines provider array size.

Important APIs, types, and functions: includes `dt-bindings/clock/sun55i-a523-r-ccu.h` and `dt-bindings/reset/sun55i-a523-r-ccu.h`; defines `CLK_NUMBER` as `CLK_BUS_R_CPUCFG + 1`.

Control flow: none; used by the A523 R_CCU C file at compile time.

State and persistence: no state. The macro determines the number of `clk_hw` slots exposed by the provider.

Dependencies and integration points: tightly coupled to `ccu-sun55i-a523-r.c` and the binding header’s highest exported clock ID.

Risks and test signals: if new binding IDs are added without updating `CLK_NUMBER`, later clocks become inaccessible. Test by build coverage and boot-time lookups for the highest R-domain clock ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523.c

Purpose: main CCU driver for Allwinner A523. It describes a large modern Sunxi clock tree including PLL output families, CPU/AXI/bus roots, DMA/MBUS, storage, network, USB, display, video, camera, audio, sensor, and reset domains.

Important APIs, types, and functions: uses parent-data based CCU definitions and fixed factors for PLL-periph, video, audio, and other derived outputs. Central artifacts are `sun55i_a523_ccu_clks`, `sun55i_a523_hw_clks`, `sun55i_a523_ccu_resets`, `sun55i_a523_ccu_desc`, `pll_regs`, and `sun55i_a523_ccu_probe()`. It also includes `<dt-bindings/clock/sun55i-a523-ccu.h>` and reset bindings directly.

Control flow: probe maps the CCU resource, iterates over all modeled PLL registers to set PLL enable, LDO enable, and lock-enable bits that are not represented independently by generic PLL structs, forces PLL_AUDIO0 `m1/m0` output-divider defaults, and registers the descriptor with `devm_sunxi_ccu_probe()`.

State and persistence: all persistent state is MMIO clock/reset state. Software descriptors are static. Some clocks are marked critical, including DDR, to prevent framework disablement of essential infrastructure.

Dependencies and integration points: binds `allwinner,sun55i-a523-ccu`, provides parent PLLs used by R/MCU CCUs, and clocks/resets for CPU, memory, DMA, VE, NPU, GPU, display, HDMI, MIPI DSI, TCON, LVDS/eDP, CSI/ISP, USB, PCIe/USB3, EMAC, SPI, I2C, UART, CAN, thermal, GPADC, LRADC, LEDC, and audio blocks.

Risks and test signals: this is mostly data-table code, so risks are wrong parent order, register offsets, reset bits, fixed-factor modeling, and PLL enable semantics. Comments flag BSP/register-derived resets. Test signals include full boot without missing parent warnings, clk summary review for PLL families, peripheral probe coverage across storage/network/display/camera/audio/USB, reset-controller exercise, and power-management tests verifying critical clocks stay enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun5i.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun5i.c

Purpose: early CCU driver for Allwinner sun5i A10s/A13/GR8 SoCs. It models legacy PLLs, CPU/AXI/AHB/APB roots, AHB/APB/module gates, display/media/audio/USB/GPS/DRAM clocks, reset lines, and variant-specific exported clock sets.

Important APIs, types, and functions: defines PLLs using `ccu_nkmp`, `ccu_nm`, `ccu_mult`, `ccu_nk`, and fixed factors; many gates and module clocks via Sunxi macros; `sun5i_a10s_ccu_clks`, `sun5i_a10s_hw_clks`, `sun5i_a13_hw_clks`, `sun5i_gr8_hw_clks`, `sun5i_a10s_ccu_resets`, three `sunxi_ccu_desc` structures, `sun5i_ccu_init()`, and three `CLK_OF_DECLARE` setup functions.

Control flow: early OF init maps CCU registers with `of_io_request_and_map()`, forces PLL-Audio-1x divider to 1, reparents AHB to PLL-periph instead of CPU/AXI to avoid cpufreq-induced timer instability, and calls `of_sunxi_ccu_probe()`. A10s, A13, and GR8 share clock objects but expose different `clk_hw_onecell_data` subsets.

State and persistence: state is early-mapped CCU MMIO and static clock descriptors. No devm cleanup exists because registration happens during early boot. Reset state is exposed through mapped reset bits.

Dependencies and integration points: binds through `CLK_OF_DECLARE` for `allwinner,sun5i-a10s-ccu`, `allwinner,sun5i-a13-ccu`, and `nextthing,gr8-ccu`. It integrates with DT binding IDs, common clock/reset frameworks, and consumers for CPU, timers, MMC, NAND, USB, EMAC, display, camera, audio, GPU, VE, and DRAM gates.

Risks and test signals: early mapping failures only log and return, leaving many consumers without clocks. Variant tables intentionally omit unsupported TS/GPS/HDMI/I2S/keypad/SPDIF combinations, so table accuracy matters. AHB reparenting protects timers but changes expected bus parents. Test signals include early boot clock provider availability, cpufreq plus high-speed timer stability, A10s/A13/GR8 peripheral probes, display/audio/USB behavior, reset consumers, and clk summary comparison per variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun5i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun5i.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun5i.h

Purpose: private ID header for the sun5i CCU provider. It imports public sun5i binding IDs and adds internal PLL/root IDs used by the early CCU driver.

Important APIs, types, and functions: includes `dt-bindings/clock/sun5i-ccu.h` and reset bindings, defines IDs for PLL core/audio/video/VE/DDR/peripheral, CPU-derived roots, DRAM AXI, `CLK_TCON_CH1_SCLK`, and `CLK_NUMBER`.

Control flow: none. The macros are compile-time indexes for the A10s/A13/GR8 `clk_hw_onecell_data` arrays.

State and persistence: no runtime state. The numeric constants are correctness-sensitive because they align public and private clock IDs in shared provider arrays.

Dependencies and integration points: consumed by `ccu-sun5i.c`; comments mark exported binding ranges for HOSC, video HDMI factors, CPU, bus gates, module clocks, USB, GPS, DRAM, and display clocks.

Risks and test signals: wrong values can alias or hide clocks across all three variants. Test with build coverage, boot clock lookup for each supported compatible, and checking that variant-specific omitted clocks are absent while common IDs resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun5i.h -->

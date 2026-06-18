<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/s4-peripherals.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/s4-peripherals.c

Purpose: This file describes and registers the Amlogic S4 peripheral clock controller. It is mostly a static clock topology table for the Linux common clock framework, covering RTC and CEC 32 kHz generation, protected system clock readout, video and HDMI clocks, GPU/VPU/video decoder clocks, storage and SPI clocks, PWM/SARADC/general-purpose clocks, demod/CVBS clocks, and many simple peripheral bus gates.

Important APIs, types, and functions: The file builds `struct clk_regmap`, `struct clk_fixed_factor`, `struct meson_clk_dualdiv_data`, `struct meson_vid_pll_div_data`, and `struct clk_hw *s4_peripherals_hw_clks[]`. Helper macros `S4_COMP_SEL`, `S4_COMP_DIV`, `S4_COMP_GATE`, and `S4_PCLK` wrap Meson common helpers. The only executable driver entry is the `platform_driver` using `meson_clkc_mmio_probe` with compatible `amlogic,s4-peripherals-clkc`.

Control flow: Probe is delegated to the Meson clock-controller utility. The utility maps the MMIO region, assigns the regmap to every `clk_regmap`, registers the hardware clocks indexed by dt-binding clock IDs, and exposes them through the OF clock provider. Runtime control is then handled by common clock ops such as regmap mux/divider/gate ops, dualdiv ops, and the read-only video PLL divider op.

State and persistence behavior: The driver keeps no private mutable state beyond CCF registration objects and MMIO-backed hardware registers. Several ROM-programmed or security-sensitive clocks, especially `sys_clk` A/B, are represented with read-only ops because writes are documented as crash-prone. Many peripheral gates carry `CLK_IGNORE_UNUSED` for historic compatibility, so unused-clock pruning intentionally leaves them enabled.

Dependencies and integration points: It depends on Meson helpers (`clk-regmap`, `clk-dualdiv`, `vid-pll-div`, `meson-clkc-utils`), dt-binding IDs from `amlogic,s4-peripherals-clkc.h`, and parent clocks supplied by the S4 PLL controller or firmware names such as `xtal`, `fclk_div*`, `gp0_pll`, `hifi_pll`, `hdmi_pll`, and `mpll*`. Consumers are display, video, GPU, storage, bus, PWM, ADC, CEC, and serial device-tree nodes.

Risks and edge cases: The file is register-table heavy, so ID-to-clock ordering and parent table values are the main correctness risks. Video clock paths have many muxed dividers and sparse parent value tables where invalid hardware indices are skipped. Read-only system clocks must remain read-only. `CLK_IGNORE_UNUSED` can hide missing consumer clock references. Test signals include boot probe, `/sys/kernel/debug/clk/clk_summary`, display/video mode changes, GPU and VPU rate changes, SD/eMMC and SPI transfer tests, PWM/SARADC tests, and compile-time validation of dt-binding indexes against `s4_peripherals_hw_clks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/s4-peripherals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/s4-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/s4-pll.c

Purpose: This file registers the Amlogic S4 PLL clock controller. It exposes fixed PLL derived clocks, GP0 PLL, HIFI PLL, HDMI PLL, a 50 MHz MPLL selector, and MPLL0 through MPLL3 outputs for downstream S4 peripheral clocks.

Important APIs, types, and functions: Important objects are `s4_fixed_pll_dco`, `s4_fixed_pll`, fixed-factor `fclk_div*` clocks, `s4_gp0_pll_dco`, `s4_hifi_pll_dco`, `s4_hdmi_pll_dco`, MPLL divider/gate pairs, `s4_pll_hw_clks[]`, `s4_pll_init_regs[]`, and `s4_pll_clkc_data`. It uses `meson_clk_pll_ops`, `meson_clk_pll_ro_ops`, `meson_clk_mpll_ops`, regmap divider/gate ops, and `meson_clkc_mmio_probe`.

Control flow: On platform probe for `amlogic,s4-pll-clkc`, the generic Meson MMIO probe applies controller-level init registers, registers each clock hardware object, and publishes the OF clock provider. Runtime rate operations are delegated to generic Meson PLL/MPLL and divider/gate implementations. GP0 and HIFI PLLs include init register sequences. Fixed PLL and fclk outputs are read-only because firmware/ROM owns them.

State and persistence behavior: Runtime state is almost entirely hardware register state plus CCF registrations. The file explicitly documents that fixed PLL registers are not writable in the kernel phase and writing them may crash the system, so fixed PLL DCO/dividers/gates use read-only ops and have no runtime persistence outside hardware.

Dependencies and integration points: It depends on Meson PLL/MPLL/regmap helpers, `meson-clkc-utils`, and dt-binding IDs from `amlogic,s4-pll-clkc.h`. Parent input is `xtal`; exported PLL and fclk names are consumed by S4 peripheral clock definitions, especially system, video, audio, storage, GPU, and demod clocks.

Risks and edge cases: PLL programming risks include wrong multiplier ranges, missing init sequences, lock-bit handling, and accidental writes to protected fixed PLL registers. MPLL outputs share a common control block and require correct SDM/N2/enable fields. Test signals include successful boot without PLL write faults, expected fixed PLL and fclk rates in clk summary, GP0/HIFI/HDMI rate changes with lock, MPLL audio-rate tests, and dt-binding index validation for all exported `CLKID_*` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/s4-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/sclk-div.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/sclk-div.c

Purpose: This is the Meson sample-clock divider implementation. It models hardware where divider register value zero gates the clock, nonzero values encode `divider = value + 1`, and some LR-clock variants have a programmable high-time field for duty cycle.

Important APIs, types, and functions: The exported API is `meson_sclk_div_ops`. Internal helpers include `sclk_div_maxval`, `sclk_div_maxdiv`, `sclk_div_getdiv`, `sclk_div_bestdiv`, `sclk_div_determine_rate`, `sclk_apply_ratio`, `sclk_div_set_duty_cycle`, `sclk_div_get_duty_cycle`, `sclk_apply_divider`, `sclk_div_set_rate`, `sclk_div_recalc_rate`, `sclk_div_enable`, `sclk_div_disable`, `sclk_div_is_enabled`, and `sclk_div_init`.

Control flow: CCF rate requests enter `determine_rate`, which finds the closest divider and may ask the parent to round to a better rate when `CLK_SET_RATE_PARENT` is set. `set_rate` caches the chosen divider and only writes hardware immediately if the clock is enabled. `enable` writes the cached divider and duty ratio; `disable` writes zero to the divider field. Init calls `clk_regmap_init`, reads the current hardware divider, chooses max divider if disabled, and caches the duty cycle.

State and persistence behavior: `struct meson_sclk_div_data` stores `cached_div` and `cached_duty` in memory. Hardware persistence is limited to the divider and optional high-time fields. Disabled clocks preserve desired rate in memory so enable can restore it rather than writing while gated.

Dependencies and integration points: It depends on `clk-regmap`, `parm`, common divider helpers, and CCF duty-cycle callbacks. Meson audio/sample clock definitions use this ops table through `clk_regmap` data.

Risks and edge cases: Divider zero means disabled, so rate recalculation uses cached state instead of raw hardware when disabled. Duty-cycle math depends on `cached_div`; unset or invalid duty denominators can produce unexpected high-time values. Parent-rate search clamps divider to at least 2. Test signals include rate round/set with and without parent propagation, enable-after-set behavior, disabled-state recalc, duty-cycle get/set on variants with and without `hi`, and register traces confirming zero gates the clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/sclk-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/sclk-div.h -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/sclk-div.h

Purpose: This header declares the data contract for Meson sample-clock dividers implemented by `sclk-div.c`.

Important APIs, types, and functions: `struct meson_sclk_div_data` contains a divider `struct parm`, optional high-time `struct parm`, cached divider value, and cached `struct clk_duty`. It declares the exported `meson_sclk_div_ops` clock operations table.

Control flow: The header has no executable control flow. Clock definition files embed this data structure in `struct clk_regmap.data`; the ops implementation casts it back and uses the `parm` descriptors to access regmap fields.

State and persistence behavior: The cached fields are per-clock runtime state used by the implementation to preserve desired divider and duty cycle across hardware gating. The `parm` members are static register metadata and do not change.

Dependencies and integration points: It includes `linux/clk-provider.h` for duty-cycle and ops types and `parm.h` for Meson register-field descriptors. It is consumed by Meson SoC clock files that need sample/LR clock dividers.

Risks and edge cases: Callers must initialize `div.width` correctly because max divider calculation depends on it. `hi` may be non-applicable, so users must rely on `MESON_PARM_APPLICABLE` behavior in the C file. Test signals are primarily compile-time integration plus runtime duty-cycle/rate tests for clock definitions using this struct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/sclk-div.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/t7-peripherals.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/t7-peripherals.c

Purpose: This file describes the Amlogic T7 peripheral clock controller. It registers RTC/CEC dualdiv clocks, smartcard, DSP, fixed 12/24/25 MHz outputs, Anakin, MIPI CSI/ISP, transport stream, Mali, Ethernet RMII/125 MHz, SD/eMMC, six SPICC clocks, SARADC, normal and AO PWM clocks, and a large set of system peripheral bus gates.

Important APIs, types, and functions: The core table is `t7_peripherals_hw_clks[]` indexed by `amlogic,t7-peripherals-clkc.h` IDs. `T7_COMP_SEL`, `T7_COMP_DIV`, `T7_COMP_GATE`, and `T7_SYS_PCLK` generate repeated mux/divider/gate and pclk objects. The driver exposes `t7_peripherals_data` through `meson_clkc_mmio_probe` for compatible `amlogic,t7-peripherals-clkc`.

Control flow: Probe maps the controller and registers every `clk_hw`. After registration, CCF operations modify register fields through generic Meson regmap mux/divider/gate and dualdiv helpers. Glitch-sensitive dual input paths for DSP, Anakin, MIPI CSI PHY, and Mali use two sibling mux/divider/gate chains and a final selector so CCF can switch between prepared paths.

State and persistence behavior: The driver has no private dynamic state beyond CCF objects. Hardware state is the MMIO clock register block. Most system gates are normal gates, while `sys_gic` is marked `CLK_IS_CRITICAL` because disabling the GIC clock would break interrupt handling. Some muxes use `CLK_SET_RATE_NO_REPARENT` where external pins or fixed routing should not be automatically changed.

Dependencies and integration points: It depends on `clk-dualdiv`, `clk-regmap`, `meson-clkc-utils`, and parent names exported by T7 PLL/fixed controllers such as `xtal`, `sys`, `fix`, `fdiv*`, `gp0`, `gp1`, `hifi`, `mpll*`, and `vid_pll0`. Downstream consumers include GPU, DSP, camera, ISP, Ethernet, storage, SPI, PWM, ADC, CEC, and bus devices.

Risks and edge cases: The main risks are dt-binding index mismatches, wrong parent value tables for sparse hardware muxes, and accidental gating of infrastructure clocks. Dualdiv tables assume exact 32 kHz style ratios. Test signals include boot probe, clk summary coverage for every ID, GIC clock remaining enabled, Ethernet RMII parent/rate tests, storage/SPI/PWM functional tests, and rate switching on Mali/DSP/MIPI dual-path clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/t7-peripherals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/t7-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/t7-pll.c

Purpose: This file registers Amlogic T7 PLL blocks. Unlike S4's single PLL controller node, it provides separate compatible entries for GP0, GP1, HIFI, PCIe, MPLL, HDMI, and MCLK PLL register regions.

Important APIs, types, and functions: It defines PLL DCO/divider chains for `t7_gp0_pll`, `t7_gp1_pll`, `t7_hifi_pll`, `t7_pcie_pll`, `t7_mpll0-3`, `t7_hdmi_pll`, and `t7_mclk_*`. It uses `meson_clk_pll_ops`, `meson_clk_pcie_pll_ops`, `meson_clk_mpll_ops`, regmap divider/gate ops, fixed-factor ops, `struct reg_sequence` init arrays, and multiple `struct meson_clkc_data` instances selected by OF match data.

Control flow: Platform probe is handled by `meson_clkc_mmio_probe`. The selected compatible determines which `hw_clks` array and init registers are registered for that MMIO region. GP/HIFI/HDMI/MCLK PLLs use standard Meson PLL ops with multiplier ranges and optional fractional or lock-detect fields. PCIe uses a strict init sequence with delays and the PCIe-specific PLL ops before exposing fixed/divided 100 MHz style outputs.

State and persistence behavior: Clock state is held in hardware PLL control/status registers and CCF registrations. MPLL has a controller init register. MCLK has muxes that can select the local MCLK PLL or firmware-provided `in1`/`in2`, then divides and gates two MCLK outputs.

Dependencies and integration points: It depends on Meson PLL/MPLL/regmap helpers, `meson-clkc-utils`, and dt-binding IDs from `amlogic,t7-pll-clkc.h`. Parent firmware names are `in0`, `in1`, and `in2`; consumers are T7 peripheral clocks and device-tree clock references.

Risks and edge cases: The T7 file is especially sensitive to per-compatible array sizing and ID offsets because each node exports only a subset of binding IDs. PLL lock/status register selection differs across PLL families. PCIe requires exact sequencing and delays for a precise reference clock. Test signals include probing each compatible node, checking expected PLL rates and locks, PCIe link bring-up, HDMI/display clocks, audio MPLL rates, and dt-binding index checks for sparse per-node providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/t7-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/vclk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/vclk.c

Purpose: This file implements reusable Meson video-clock gate and divider ops for hardware that has extra reset bits in addition to normal enable/divider fields.

Important APIs, types, and functions: It exports `meson_vclk_gate_ops` and `meson_vclk_div_ops`. Gate helpers are `meson_vclk_gate_enable`, `meson_vclk_gate_disable`, and `meson_vclk_gate_is_enabled`. Divider helpers are `meson_vclk_div_recalc_rate`, `meson_vclk_div_determine_rate`, `meson_vclk_div_set_rate`, `meson_vclk_div_enable`, `meson_vclk_div_disable`, and `meson_vclk_div_is_enabled`.

Control flow: Gate enable writes the enable bit, then pulses reset high and low. Gate disable clears enable. Divider rate calculation delegates to common divider helpers using the current regmap field, table, flags, and width. Divider set-rate calculates an encoded divider value and writes it. Divider enable deasserts reset before setting enable; disable clears enable and asserts reset.

State and persistence behavior: There is no private cached state. The hardware register fields described by `meson_vclk_gate_data` or `meson_vclk_div_data` are the authoritative state. Reset sequencing is transient but affects downstream video logic.

Dependencies and integration points: It depends on `vclk.h`, Meson `clk-regmap`/`parm` helpers, Linux divider helpers, and CCF. Newer Meson display clock descriptions can use these ops instead of open-coding reset-aware video gates/dividers.

Risks and edge cases: Reset polarity and ordering are critical; incorrect sequencing can leave video dividers held in reset or glitch output clocks. The gate-data `flags` field is currently not used by the implementation, despite being documented like clk-gate flags. Divider flags and optional tables must match hardware encoding. Test signals include enable/disable register traces, display pipeline bring-up after gating, rate set/recalc comparisons, and suspend/resume cycles that exercise reset state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/vclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/vclk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/vclk.h

Purpose: This header declares the data structures and ops symbols for Meson reset-aware video-clock gates and dividers.

Important APIs, types, and functions: `struct meson_vclk_gate_data` carries enable and reset `parm` fields plus a flags byte. `struct meson_vclk_div_data` carries divider, enable, reset, optional divider table, and flags. It declares `meson_vclk_gate_ops` and `meson_vclk_div_ops`.

Control flow: The header itself has no executable logic. Clock controller descriptions instantiate these structures as `clk_regmap.data`; `vclk.c` casts them back and uses the register-field metadata in CCF callbacks.

State and persistence behavior: The structures are static per-clock descriptors. They point the implementation at persistent MMIO fields for divider, enable, and reset state. There is no runtime allocation or cache in the header contract.

Dependencies and integration points: It includes `clk-regmap.h` and `parm.h`. It is intended for Meson display/video clock tree definitions that need reset-aware gate or divider behavior but still integrate through common `clk_regmap` registration.

Risks and edge cases: Users must describe reset bits accurately and set divider tables/flags consistently with CCF divider encoding. The documented `flags` semantics mention clk-gate and clk-divider flags, but unsupported flags such as HIWORD masks are ignored by the implementation. Test signals are compile-time users plus runtime register traces for gate/divider enable and disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/vclk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/vid-pll-div.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/vid-pll-div.c

Purpose: This file implements a read-only Meson video PLL fractional divider. It decodes hardware `shift_val` and `shift_sel` fields into a small set of known Amlogic fractional divide ratios used by video clocking.

Important APIs, types, and functions: The exported ops table is `meson_vid_pll_div_ro_ops`. Internal data includes `struct vid_pll_div`, the `vid_pll_div_table[]` of supported ratios from `/2` through `/15`, `_get_table_val`, and `meson_vid_pll_div_recalc_rate`.

Control flow: CCF calls `recalc_rate`; the driver reads the `val` and `sel` fields from the `meson_vid_pll_div_data`, looks for a matching entry in `vid_pll_div_table`, and computes `parent_rate * multiplier / divider` rounded up. Unsupported register encodings log a debug message and return zero. Init is the standard `clk_regmap_init`.

State and persistence behavior: There is no writable or cached state. The hardware register fields hold the current divider encoding, but this implementation only reports the resulting rate. The TODO in S4 users notes a future writable ops variant could be added.

Dependencies and integration points: It depends on `clk-regmap`, `parm`, CCF, and `vid-pll-div.h`. S4 peripheral video PLL definitions use it to model the divided HDMI PLL input before the rest of the VCLK tree.

Risks and edge cases: Unknown hardware encodings produce a zero rate, which can propagate into display clock calculations. The table only covers common vendor-provided ratios, so new SoCs or firmware settings may need additional entries. Test signals include reading known display modes from clk summary, forcing firmware-supported divider values, and confirming unsupported values fail visibly without crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/vid-pll-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/vid-pll-div.h -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/vid-pll-div.h

Purpose: This header declares the descriptor for Meson video PLL fractional divider clocks and the read-only ops table implemented in `vid-pll-div.c`.

Important APIs, types, and functions: `struct meson_vid_pll_div_data` contains two `struct parm` fields: `val` for the fractional shift value and `sel` for the shift selector. It declares `meson_vid_pll_div_ro_ops`.

Control flow: There is no executable logic in the header. SoC clock descriptions provide register field metadata, and the C file uses it during CCF recalc-rate callbacks.

State and persistence behavior: The structure is static clock metadata. Runtime state is the hardware register contents addressed by `val` and `sel`.

Dependencies and integration points: It includes `linux/clk-provider.h` and Meson `parm.h`. It is used by Meson peripheral clock controller files that include video PLL divider stages.

Risks and edge cases: Consumers only get read-only behavior; attempts to use it where software must program the video PLL divider will not be sufficient. Incorrect field widths or offsets will decode to the wrong ratio or zero. Test signals include compile-time inclusion and display clock recalc checks on users such as S4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/vid-pll-div.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/microchip/Kconfig

Purpose: This Kconfig fragment controls Microchip clock driver build options for legacy PIC32 and PolarFire SoC MPFS support.

Important APIs, types, and functions: It defines `COMMON_CLK_PIC32` as a default boolean when `COMMON_CLK && MACH_PIC32`, and `MCHP_CLK_MPFS` as the user-visible PolarFire SoC clock option. `MCHP_CLK_MPFS` depends on `ARCH_MICROCHIP || COMPILE_TEST`, defaults to `y`, requires `MFD_SYSCON`, and selects `AUXILIARY_BUS` and `REGMAP_MMIO`.

Control flow: Kconfig selection determines which objects in the Microchip clock Makefile are compiled. There is no runtime behavior in this file.

State and persistence behavior: The state is build configuration only. It affects the resulting kernel image or module set, not runtime persistence.

Dependencies and integration points: `COMMON_CLK_PIC32` enables shared PIC32 clock core compilation for PIC32 SoCs. `MCHP_CLK_MPFS` enables both MPFS MSS clock configuration and MPFS CCC drivers and ensures their syscon/regmap infrastructure is present.

Risks and edge cases: The default-yes MPFS option can build in COMPILE_TEST contexts but depends on required headers and dt-bindings being available. `COMMON_CLK_PIC32` is not user-prompted here, so PIC32 platform symbols drive it. Test signals include `allmodconfig`, `allyesconfig`, PIC32 builds, MPFS builds with `MFD_SYSCON`, and COMPILE_TEST builds on non-Microchip architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/microchip/Makefile

Purpose: This Makefile maps Microchip clock Kconfig symbols to build objects.

Important APIs, types, and functions: `clk-core.o` is built for `CONFIG_COMMON_CLK_PIC32`, `clk-pic32mzda.o` for `CONFIG_PIC32MZDA`, and both `clk-mpfs.o` and `clk-mpfs-ccc.o` for `CONFIG_MCHP_CLK_MPFS`.

Control flow: Kbuild includes these objects in the driver build according to configuration. There is no runtime control flow.

State and persistence behavior: The file has build-system state only. It determines object inclusion and link order within the Microchip clock directory.

Dependencies and integration points: It aligns with the Kconfig fragment and separates shared PIC32 operations from the PIC32MZDA SoC instantiation. MPFS core clock and CCC fabric clock drivers are both compiled when MPFS support is enabled.

Risks and edge cases: `clk-pic32mzda.o` depends on the shared `clk-core.o` APIs, so configuration must ensure both are available in PIC32MZDA builds. Enabling MPFS builds two platform drivers with different compatibles. Test signals are build coverage for each config combination and link checks for exported/internal symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-core.c -->
# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-core.c

Purpose: This file implements reusable PIC32 clock operations for peripheral bus clocks, reference oscillators, system PLL, system clock mux/slew divider, and secondary oscillator.

Important APIs, types, and functions: Exported ops and constructors include `pic32_pbclk_ops` with `pic32_periph_clk_register`, `pic32_roclk_ops` with `pic32_refo_clk_register`, `pic32_spll_ops` with `pic32_spll_clk_register`, `pic32_sclk_ops`/`pic32_sclk_no_div_ops` with `pic32_sys_clk_register`, and `pic32_sosc_ops` with `pic32_sosc_clk_register`. Key helpers include `calc_best_divided_rate`, `roclk_calc_rate`, `roclk_calc_div_trim`, `spll_calc_mult_div`, `sclk_set_parent`, and `sclk_init`.

Control flow: SoC-specific code registers clock descriptors through the constructors. CCF callbacks then read/write PIC32 registers directly. Protected writes call `pic32_syskey_unlock`, use `reg_lock`, and poll ready, active, lock, or busy bits. SPLL rate changes are refused while SPLL is the active system-clock parent. System clock parent changes program `NOSC`, set `OSC_SWEN`, wait for switch completion, and verify `COSC`.

State and persistence behavior: Runtime state lives in MMIO clock registers and small allocated clock wrapper structs. `pic32_sclk_hw` caches the system clock hardware so SPLL changes can detect active use. There is no disk persistence. Hardware settings persist until firmware reset or later clock operations.

Dependencies and integration points: It depends on CCF, MMIO accessors, polling helpers, PIC32 platform syskey APIs, and descriptor structs from `clk-core.h`. `clk-pic32mzda.c` is the main in-tree user.

Risks and edge cases: Clock switching is CPU-sensitive and uses NOP delays to avoid hangs during transitions. Poll timeouts, failed oscillator switching, reference oscillator active state, and SPLL in-use checks are critical. Several routines must preserve lock ordering around syskey-protected writes. Test signals include rate round/set for PBCLK/REFO/SPLL/SCLK, oscillator parent switching, timeout injection, critical-clock enable, and NMI/failsafe scenarios on PIC32 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-core.h -->
# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-core.h

Purpose: This header defines the shared descriptor contract for PIC32 clock implementations and SoC-specific PIC32 clock drivers.

Important APIs, types, and functions: It defines `struct pic32_clk_common`, `pic32_sys_pll_data`, `pic32_sys_clk_data`, `pic32_ref_osc_data`, `pic32_periph_clk_data`, and `pic32_sec_osc_data`. It declares ops tables for PBCLK, SCLK, SPLL, reference oscillator, and secondary oscillator, plus registration helpers for each clock type.

Control flow: The header is declarative. SoC files fill these descriptor structures with init data, register offsets, parent maps, masks, and rates, then call the registration functions in `clk-core.c`.

State and persistence behavior: Descriptor fields are static SoC metadata. `pic32_clk_common` carries shared runtime state: device pointer, MMIO base, and spinlock for protected register updates.

Dependencies and integration points: It includes `linux/clk-provider.h` and is shared by `clk-core.c` and `clk-pic32mzda.c`. It abstracts common PIC32 clock behavior away from SoC-specific clock lists.

Risks and edge cases: Offsets are added to the common MMIO base, so descriptors must use the correct register map. Parent maps must match hardware mux values, not just CCF parent order. Test signals include compile coverage of all constructors and runtime verification that PIC32MZDA descriptors register and expose expected parents/rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-mpfs-ccc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-mpfs-ccc.c

Purpose: This file implements the PolarFire SoC Clock Conditioning Circuitry driver. It exposes two fabric CCC PLLs and four divided outputs from each PLL.

Important APIs, types, and functions: Key types are `mpfs_ccc_data`, `mpfs_ccc_pll_hw_clock`, and `mpfs_ccc_out_hw_clock`. Important functions are `mpfs_ccc_pll_recalc_rate`, `mpfs_ccc_pll_get_parent`, `mpfs_ccc_register_outputs`, `mpfs_ccc_register_plls`, and `mpfs_ccc_probe`. It registers a platform driver for compatible `microchip,mpfs-ccc` at `core_initcall`.

Control flow: Probe maps two PLL resources, allocates a onecell clock data block, registers PLL0 and PLL1 using parent firmware names `pll*_ref0` and `pll*_ref1`, then registers four divider outputs for each PLL. The provider is published with `devm_of_clk_add_hw_provider`. PLL recalc reads feedback and reference dividers; parent selection reads `MPFS_CCC_REFCLK_SEL`.

State and persistence behavior: There is no private mutable state after registration except clock wrapper fields. PLL and output divider state is in the CCC MMIO resources. A global spinlock protects output divider writes because outputs share post-divider registers and the hardware has software-locked write behavior.

Dependencies and integration points: It depends on CCF, platform resource mapping, OF clock provider APIs, dt-binding IDs from `microchip,mpfs-clock.h`, and firmware-provided reference clocks. Fabric and peripheral consumers reference CCC output IDs through device tree.

Risks and edge cases: The `hw_data.hws[out_hw->id - 2]` packing assumes only PLL IDs and output IDs are present; the source comment warns DLL additions would need rework. Shared post-divider registers make locking important. Test signals include provider registration with two resources, expected PLL rates for both reference inputs, all eight output IDs resolving, concurrent divider changes, and fabric devices consuming CCC outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-mpfs-ccc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-mpfs.c -->
# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-mpfs.c

Purpose: This file implements the PolarFire SoC MSS/core complex clock controller. It registers the MSS PLL internal clock, four MSS PLL outputs, CPU/AXI/AHB/RTC reference dividers, and peripheral gate clocks.

Important APIs, types, and functions: Key types are `mpfs_clock_data`, `mpfs_msspll_hw_clock`, `mpfs_msspll_out_hw_clock`, `mpfs_cfg_hw_clock`, and `mpfs_periph_hw_clock`. Important functions include `mpfs_clk_msspll_recalc_rate`, `mpfs_clk_register_mssplls`, `mpfs_clk_register_msspll_outs`, `mpfs_cfg_clk_recalc_rate`, `mpfs_cfg_clk_determine_rate`, `mpfs_cfg_clk_set_rate`, peripheral gate callbacks, `mpfs_clk_syscon_probe`, `mpfs_clk_old_format_probe`, and `mpfs_clk_probe`.

Control flow: Probe first tries the modern syscon layout using `microchip,mpfs-mss-top-sysreg` plus an MSS PLL resource. If that fails, it falls back to an older device-tree format with two mapped resources, creates an MMIO regmap, and registers the MPFS reset controller. It then registers PLLs, outputs, config dividers, peripheral gates, and an OF onecell provider.

State and persistence behavior: Hardware registers hold PLL, divider, gate, and reset state. The driver stores a regmap, MMIO bases, and onecell clock array. Several peripheral gates are marked `CLK_IS_CRITICAL`, including ENVM, MMUART0, RTC, DDRC, FIC clocks, and Athena, because firmware, memory, RTC, or fabric interconnects depend on them.

Dependencies and integration points: It depends on CCF, regmap, syscon, platform resources, MPFS reset-controller helpers, dt-binding IDs, and `soc/microchip/mpfs.h`. Peripheral consumers are Microchip MPFS device-tree nodes for MAC, MMC, UART, SPI, I2C, CAN, USB, RTC, QSPI, GPIO, DDR, FIC, and CFM.

Risks and edge cases: `regmap_update_bits` in `mpfs_cfg_clk_set_rate` appears to pass value and mask in reversed order, so rate programming deserves careful review. PLL reference divider values must not be zero. Old/new DT fallback changes reset-controller behavior. Test signals include modern and old DT probing, critical clocks staying enabled, CPU/AXI/AHB divider rate changes, peripheral gate enable/disable, reset controller registration in old format, and dt-binding ID coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-mpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-pic32mzda.c -->
# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-pic32mzda.c

Purpose: This file instantiates the PIC32MZDA clock tree using the shared PIC32 clock core. It registers fixed oscillators, FRC divider, system PLL mux and PLL, system clock, PBCLKs, reference oscillators, critical clocks, and a failsafe clock monitor NMI notifier.

Important APIs, types, and functions: Descriptor macros `DECLARE_PERIPHERAL_CLOCK` and `DECLARE_REFO_CLOCK` build `pic32_periph_clk_data` and `pic32_ref_osc_data`. Static descriptors include `ref_clks`, `periph_clocks`, `sys_mux_clk`, `sys_pll`, and `sosc_clk`. Runtime functions are `pic32_fscm_nmi`, `pic32mzda_clk_probe`, and `microchip_pic32mzda_clk_init`.

Control flow: Probe maps the clock register block, initializes the shared lock, registers fixed-rate clocks (`posc`, `frc`, `bfrc`, `lprc`, `usbphy`), optionally registers SOSC from a DT property, registers `frcdiv_clk`, SPLL input mux, SPLL, system clock, PB1-PB7 clocks, REF1-REF5 clocks, clkdev aliases, and the OF onecell provider. It then force-enables critical clocks and registers an NMI notifier for failsafe clock monitor alerts.

State and persistence behavior: Driver state is stored in `pic32mzda_clk_data`, including the clock array, common MMIO base/lock, onecell data, and notifier. Hardware clock configuration persists in PIC32 registers. Critical clocks PB2 and PB7 are enabled during probe and intentionally kept active.

Dependencies and integration points: It depends on PIC32 dt-bindings, CCF, clkdev, OF MMIO mapping, MIPS trap/NMI notifier support, and the shared `clk-core` registration helpers.

Risks and edge cases: Error unwinding is limited after partial clock registration. Optional SOSC changes parent availability. Critical clock indexes must match binding IDs. The NMI notifier only reports failsafe clock failure and does not recover. Test signals include DT probe, fixed-rate clock visibility, system clock parent/rate changes, PB and REFO rates, optional SOSC property behavior, critical clock enablement, and simulated FSCM NMI logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-pic32mzda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/Kconfig

Purpose: This Kconfig fragment declares the Marvell MMP/PXA1908 common clock driver option.

Important APIs, types, and functions: It defines `COMMON_CLK_PXA1908`, a boolean "Clock driver for Marvell PXA1908" that depends on `ARCH_MMP || COMPILE_TEST`, depends on OF, defaults to `y` for `ARCH_MMP && ARM64`, and selects `AUXILIARY_BUS`.

Control flow: There is no runtime flow. The symbol controls whether PXA1908-specific clock objects are included by the MMP clock Makefile.

State and persistence behavior: This is build configuration state only.

Dependencies and integration points: It integrates with architecture selection, OF availability, and the MMP Makefile entries for PXA1908 APBC/APBCP/MPMU/APMU clocks.

Risks and edge cases: COMPILE_TEST builds require all auxiliary bus and OF dependencies to be available outside native platforms. Default-y behavior only applies to ARM64 MMP builds. Test signals include PXA1908 defconfig, COMPILE_TEST builds, and ensuring the selected object set links with common MMP clock helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/Makefile

Purpose: This Makefile defines the object composition for Marvell MMP clock support.

Important APIs, types, and functions: Core objects `clk-apbc.o`, `clk-apmu.o`, `clk-frac.o`, `clk-mix.o`, `clk-gate.o`, and `clk.o` are always built for the directory. Optional entries include `reset.o` for `CONFIG_RESET_CONTROLLER`, PXA168/PXA910 OF clock files for `CONFIG_MACH_MMP_DT`, MMP2 PLL/power/audio files for `CONFIG_COMMON_CLK_MMP2*`, PXA1908 APBC/APBCP/MPMU/APMU files for `CONFIG_COMMON_CLK_PXA1908`, and PXA1928 OF clocks for `CONFIG_ARCH_MMP`.

Control flow: Kbuild uses these assignments to compile and link platform-specific MMP clock providers. There is no runtime logic in this file.

State and persistence behavior: Build output composition is the only state.

Dependencies and integration points: The always-built helpers provide registration APIs used by multiple MMP SoC clock files. Optional SoC files layer device-tree providers and reset/power support on top.

Risks and edge cases: Always building helper objects assumes the parent Kbuild only enters this directory when MMP clock support is needed. Optional SoC objects depend on helper declarations in `clk.h`. Test signals include build coverage for reset-controller, legacy MMP DT, MMP2 audio, PXA1908, and ARCH_MMP configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-apbc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-apbc.c

Purpose: This file implements APB clock gate/reset preparation for Marvell MMP peripheral clocks controlled by APBC registers.

Important APIs, types, and functions: The public constructor is `mmp_clk_register_apbc`. Internal state is `struct clk_apbc` with `clk_hw`, MMIO base, delay, APBC flags, and optional spinlock. The ops table `clk_apbc_ops` provides `prepare` and `unprepare` through `clk_apbc_prepare` and `clk_apbc_unprepare`.

Control flow: Registration allocates a `clk_apbc`, fills `clk_init_data` with `CLK_SET_RATE_PARENT`, records register metadata, and calls `clk_register`. Prepare optionally locks, sets power and functional clock bits, waits the configured delay, sets APB bus clock, waits again, then deasserts reset unless `APBC_NO_BUS_CTRL` is set. Unprepare clears optional power and functional clock bits, delays, then clears APB bus clock.

State and persistence behavior: There is no managed lifetime beyond freeing on registration failure; successful clocks are unmanaged legacy CCF registrations. Runtime state is the APBC hardware register. Optional spinlock protects registers shared with mux clocks or other bitfields.

Dependencies and integration points: It depends on `clk.h` for APBC flag definitions and declarations, MMIO accessors, delays, CCF, and slab allocation. MMP SoC clock provider files call this helper for APB peripherals.

Risks and edge cases: Reset, functional clock, bus clock, and power sequencing must match hardware requirements. Shared registers require callers to pass the right lock. Delay values must be sufficient for hardware stabilization. Test signals include prepare/unprepare register traces, APBC_POWER_CTRL and APBC_NO_BUS_CTRL variants, shared-register lock coverage, and peripheral probe/remove using APBC clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-apbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-apmu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-apmu.c

Purpose: This file implements simple AXI/APMU peripheral clock gates for Marvell MMP clocks controlled by enable bits in APMU registers.

Important APIs, types, and functions: The public constructor is `mmp_clk_register_apmu`. Internal state is `struct clk_apmu`, which stores `clk_hw`, MMIO base, reset mask, enable mask, and optional lock. `clk_apmu_ops` supplies `enable` and `disable` through `clk_apmu_enable` and `clk_apmu_disable`.

Control flow: Registration allocates the wrapper, fills a single-parent `clk_init_data` with `CLK_SET_RATE_PARENT`, records base and enable mask, and registers the clock. Enable reads the register, ORs `enable_mask`, and writes it back under the optional lock. Disable reads, clears `enable_mask`, and writes it back.

State and persistence behavior: Hardware register bits hold the persistent enable state. The allocated clock object stores only register metadata. The `rst_mask` field exists in the struct but is not used by this implementation.

Dependencies and integration points: It depends on MMP `clk.h`, CCF, MMIO accessors, and optional external spinlocks. SoC-specific MMP clock files use it for APMU-controlled clocks where no reset or sequencing is needed.

Risks and edge cases: Read-modify-write races are possible without a shared lock for registers containing multiple controls. Unused `rst_mask` can confuse future users expecting reset behavior. Test signals include enable/disable register traces, shared-register locking tests, and device functional tests for APMU-gated peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-apmu.c -->

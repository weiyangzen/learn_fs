# Research: subset-b-005115 Sunplus and sunxi pinctrl files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl_sp7021.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl_sp7021.c

## Purpose

This file is the SP7021 SoC data table for the Sunplus pin controller. It describes the GPIO-visible pins, the subset that can participate in pinmuxing, fixed-function mux selectors, and grouped mux choices for buses and debug interfaces. The executable driver logic lives in the shared Sunplus pinctrl code included through `sppctl.h`; this file supplies the SP7021-specific names, IDs, groups, register fields, and function table consumed by that core.

## Important APIs, Types, And Functions

The exported data includes `sppctl_gpio_list_s`, `sppctl_gpio_list_sz`, `sppctl_pins_gpio`, `sppctl_pins_all`, `sppctl_pins_all_sz`, `sppctl_pmux_list_s`, `sppctl_pmux_list_sz`, `sppctl_list_funcs`, and `sppctl_list_funcs_sz`. Local helper macros `D_PIS()`, `D()`, and `P()` turn bank/pin coordinates into Linux pin names, numeric pin IDs, and `PINCTRL_PIN()` descriptors. The function/group tables are built with Sunplus-specific macros such as `EGRP()`, `FNCN()`, and `FNCE()` around `struct sppctl_grp` and `struct sppctl_func`.

## Control Flow

There is no local probe or runtime callback. At driver registration, the common Sunplus controller code imports these arrays, registers the 99 listed GPIO pins, exposes the muxable subset, and builds mux functions from `sppctl_list_funcs`. Pinmux requests select either fixed per-function mux fields (`pinmux_type_fpmx`) or grouped function choices (`pinmux_type_grp`) that reference the `sp7021grps_*` arrays. Those choices ultimately program Moon register fields identified by register offset, bit shift, and field width in each function entry.

## State And Persistence

All state in this file is static table data. Runtime state is held by the shared pinctrl driver and SP7021 hardware registers. Mux selections persist only as register contents until reset, power loss, or a later pinctrl request changes the same field. The first two `sppctl_list_funcs` entries are intentionally dummy entries for compatibility, so the table index is also part of the ABI expected by the common driver or bindings.

## Dependencies And Integration Points

The file depends on Linux GPIO and pinctrl descriptors plus `sppctl.h` for the Sunplus table schema. It integrates SP7021 pins with peripherals including SPI flash, SPI NAND, eMMC, SD card, UART, debug, FPGA, HDMI, audio interfaces, LCD, DVD debug, I2C, wakeup, USB/UPHY, probe ports, L2 switch RMII, PWM, capture, timers, GPIO interrupts, SPI master/slave, and I2C master functions.

## Risks

The main risk is table integrity: pin numeric IDs, muxable pin names, group pin lists, register offsets, shifts, and widths must match the SP7021 manual. `pins_spi42` contains `D(9, 8)`, which is outside the normal 0-7 pin range and numerically aliases `D(10, 0)` under `D(x, y) = x * 8 + y`; that may be intentional notation or a latent table error. Empty groups such as `pins_emmc` are also easy to misread and should be checked against the shared driver behavior. Dummy function entries must not be removed or reordered.

## Test Signals

Useful validation includes SP7021 pinctrl probe, debugfs listing of 99 GPIO pins and the muxable subset, GPIO request/direction/value tests across banks 0-12, mux tests for SPI flash, SD/eMMC, UART, HDMI, USB, audio, and L2 switch functions, and register readback confirming that fixed and grouped mux fields land in the expected Moon registers without shifting adjacent fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl_sp7021.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/Kconfig

## Purpose

This Kconfig fragment defines build-time configuration for Allwinner/sunxi pinctrl drivers. It gates the common sunxi pinctrl core under `ARCH_SUNXI` and provides per-SoC symbols for main PIO and R-PIO controllers from older ARM SoCs through newer ARM64 and RISC-V families.

## Important APIs, Types, And Functions

The central internal symbol is `PINCTRL_SUNXI`, a hidden bool selecting `PINMUX`, `GENERIC_PINCONF`, and `GPIOLIB`. Public SoC symbols include `PINCTRL_SUNIV_F1C100S`, `PINCTRL_SUN4I_A10`, `PINCTRL_SUN5I`, `PINCTRL_SUN6I_A31`, `PINCTRL_SUN6I_A31_R`, `PINCTRL_SUN8I_*`, `PINCTRL_SUN9I_*`, `PINCTRL_SUN20I_D1`, `PINCTRL_SUN50I_*`, and `PINCTRL_SUN55I_A523*`.

## Control Flow

There is no runtime flow. During kernel configuration, enabled architecture or machine symbols set defaults for matching pinctrl drivers. Selecting any SoC-specific symbol selects `PINCTRL_SUNXI`, which makes the common pinctrl, pinmux, generic pinconf, and GPIO dependencies available. The Makefile then uses the selected symbols to include the matching object files.

## State And Persistence

The only state is Kconfig configuration state saved in `.config` or generated defconfigs. That state controls compilation and built-in/module availability but does not persist runtime pin state.

## Dependencies And Integration Points

This file integrates with the architecture selection layer through `ARCH_SUNXI`, `MACH_SUNIV`, `MACH_SUN4I`, `MACH_SUN5I`, `MACH_SUN6I`, `MACH_SUN8I`, `MACH_SUN9I`, `ARM64`, and `RISCV`. It integrates with `drivers/pinctrl/sunxi/Makefile` through one-to-one `CONFIG_PINCTRL_*` object mappings.

## Risks

Incorrect defaults can omit required pinctrl support from platform defconfigs, leading to early boot failures when GPIO, UART, MMC, or regulator pins cannot be configured. Symbols are mostly bools, while A100 files use module registration macros; changing bool/tristate semantics must be coordinated with Makefile and init macro choices. A missing `select PINCTRL_SUNXI` on a new symbol would compile an SoC file without the common core.

## Test Signals

Useful validation includes `olddefconfig` for each supported architecture family, checking that expected `CONFIG_PINCTRL_*` symbols appear in generated configs, compile tests for all entries, and boot smoke tests confirming that device-tree-compatible pinctrl nodes bind on selected SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/Makefile

## Purpose

This Makefile maps the sunxi pinctrl Kconfig symbols to the common core objects and the per-SoC controller object files. It is the build integration point that turns enabled `CONFIG_PINCTRL_*` symbols into compiled drivers.

## Important APIs, Types, And Functions

The always-built core entries are `pinctrl-sunxi.o` and `pinctrl-sunxi-dt.o`. Per-SoC `obj-$(CONFIG_...)` rules build files such as `pinctrl-sun4i-a10.o`, `pinctrl-sun20i-d1.o`, `pinctrl-sun50i-a100.o`, `pinctrl-sun50i-h616.o`, and `pinctrl-sun55i-a523-r.o`.

## Control Flow

There is no runtime flow. Kbuild evaluates each `obj-y` and `obj-$(CONFIG_...)` assignment. Because `PINCTRL_SUNXI` is selected by every SoC symbol, the directory always includes the common core when any sunxi pinctrl support is enabled. The matching SoC object is then linked into the kernel or module set according to its config value.

## State And Persistence

Build state is limited to generated Kbuild outputs and object files. This file does not own runtime state or hardware configuration.

## Dependencies And Integration Points

This file depends on the Kconfig symbols defined in the adjacent `Kconfig` file and on source files with matching basenames. It integrates SoC tables with the shared sunxi core and with the top-level kernel build system.

## Risks

The primary risk is drift between Kconfig symbols and object names. A new symbol without an `obj-*` line silently produces no driver, while an object rule referencing a missing file breaks builds. The common `obj-y` core assumes this directory is only entered when sunxi pinctrl is selected; build-system changes should preserve that relationship.

## Test Signals

Validation should include allmodconfig/allnoconfig-style compile coverage, targeted builds for each `CONFIG_PINCTRL_*` symbol, and a check that every Kconfig SoC symbol has exactly one intended object rule.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun20i-d1.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun20i-d1.c

## Purpose

This file provides the Allwinner D1 PIO pin description for the shared sunxi pinctrl driver. It lists pins on banks PB through PG and maps each pin to GPIO input/output, peripheral mux values, and external interrupt positions.

## Important APIs, Types, And Functions

The main table is `d1_pins[]`, an array of `struct sunxi_desc_pin` built with `SUNXI_PIN()`, `SUNXI_PINCTRL_PIN()`, `SUNXI_FUNCTION()`, and `SUNXI_FUNCTION_IRQ_BANK()`. The file defines `d1_irq_bank_map[]`, `d1_pinctrl_data`, `d1_pinctrl_probe()`, `d1_pinctrl_match[]`, and `d1_pinctrl_driver`.

## Control Flow

The built-in platform driver binds to `allwinner,sun20i-d1-pinctrl`. Probe calls `sunxi_pinctrl_init_with_flags()` with `SUNXI_PINCTRL_NEW_REG_LAYOUT`. The common sunxi core registers the listed pins, groups functions by name, exposes GPIO and pinconf operations, and uses the new register layout when programming mux, pull, drive, data, and IRQ registers.

## State And Persistence

Local state is immutable table data. Runtime state is held by the common sunxi driver and by hardware registers. `d1_irq_bank_map` maps logical IRQ banks to hardware banks PB-PG, and `io_bias_cfg_variant = BIAS_VOLTAGE_PIO_POW_MODE_CTL` tells the core how to persist or update IO voltage bias register selections.

## Dependencies And Integration Points

The file depends on `pinctrl-sunxi.h`, OF platform binding, and Linux pinctrl descriptors. It integrates D1 peripherals including LCD, LVDS, DSI, TCON, DMIC, I2S, I2C, SPI, UART, CAN, IR, SPDIF, PWM, LEDC, MMC, EMAC, NCSI, JTAG, clock fanout, and boot/pll signals.

## Risks

The mux table is dense and shares names across alternative pins. Any wrong mux value or IRQ bank index can route a peripheral or interrupt to the wrong pad. Because this file opts into the new register layout and PIO power-mode bias control, using the wrong init flags would corrupt register offsets. Banks start at PB, so off-by-one errors in bank maps are plausible.

## Test Signals

Useful tests include D1 boot with the compatible node, debugfs pin/function listing for PB-PG, GPIO direction/value tests per bank, external interrupt tests on each mapped bank, IO bias tests for voltage-sensitive pins, and functional mux tests for UART console, MMC, I2C, SPI, audio, display, and EMAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun20i-d1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun4i-a10.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun4i-a10.c

## Purpose

This source describes the shared PIO controller for Allwinner A10, A20, and R40-class SoCs. It contains a large pin/function database for banks PA through PI and uses variant flags to expose only the functions valid on each compatible SoC.

## Important APIs, Types, And Functions

Important definitions are `PINCTRL_SUN4I_A10`, `PINCTRL_SUN7I_A20`, `PINCTRL_SUN8I_R40`, `sun4i_a10_pins[]`, `sun4i_a10_pinctrl_data`, `sun4i_a10_pinctrl_probe()`, and `sun4i_a10_pinctrl_match[]`. The table uses `SUNXI_FUNCTION_VARIANT()` heavily alongside regular `SUNXI_FUNCTION()` and `SUNXI_FUNCTION_IRQ_BANK()`.

## Control Flow

The built-in platform driver matches `allwinner,sun4i-a10-pinctrl`, `allwinner,sun7i-a20-pinctrl`, or `allwinner,sun8i-r40-pinctrl`. Probe reads the match data variant bit and calls `sunxi_pinctrl_init_with_flags()`. The common core filters variant-scoped functions and then services pinctrl, GPIO, and IRQ requests using the static descriptor.

## State And Persistence

The file owns only constant data. Runtime pin state is hardware register state plus common-core bookkeeping. The descriptor sets one IRQ bank, `irq_read_needs_mux = true`, and `disable_strict_mode = true`, so the core allows less strict GPIO/mux overlap while still requiring mux-aware IRQ reads.

## Dependencies And Integration Points

The file depends on OF match data and the sunxi common core. It integrates legacy peripherals including EMAC/GMAC, SPI, UART, CAN, I2C, I2S, AC97, IR, HDMI, LCD, LVDS, CSI, TS, MMC, NAND, PATA, memory-stick, PS2, keypad, PWM, JTAG, timers, clock outputs, and debug/pll functions.

## Risks

This is a high-risk table because one source serves three related SoCs. Variant masks must be exact; exposing A20 or R40-only functions on A10 can create unusable device-tree configurations, while hiding shared functions breaks boards. The old interrupt behavior and `disable_strict_mode` are compatibility choices that should not be changed casually. Large bank tables make mux-value transposition errors hard to catch by inspection.

## Test Signals

Validation should include builds and boot probes for all three compatibles, debugfs confirmation of variant-specific functions, GPIO and IRQ tests on PA-PI, and board-level mux tests for UART, MMC, Ethernet, display, camera, NAND/PATA, I2C, SPI, and audio paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun4i-a10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a100-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a100-r.c

## Purpose

This file describes the A100 R-PIO controller, the reduced always-on pin controller for PL pins. It maps PL0-PL11 to sleep-domain GPIO, serial, I2C, PWM, CIR, and JTAG functions.

## Important APIs, Types, And Functions

The core data is `a100_r_pins[]`, `a100_r_pinctrl_data`, `a100_r_pinctrl_probe()`, `a100_r_pinctrl_match[]`, and `a100_r_pinctrl_driver`. The descriptor sets `.pin_base = PL_BASE`, `.irq_banks = 1`, and `.io_bias_cfg_variant = BIAS_VOLTAGE_PIO_POW_MODE_CTL`.

## Control Flow

The platform driver matches `allwinner,sun50i-a100-r-pinctrl`. Probe calls `sunxi_pinctrl_init()`, and the common sunxi driver registers the PL-range pins with R-PIO numbering. Unlike many older sunxi files, this one uses `MODULE_DEVICE_TABLE()` and `module_platform_driver()`.

## State And Persistence

The source owns only static descriptors. Runtime mux, GPIO, IRQ, and bias state live in R-PIO hardware registers and common driver data. R-PIO pin numbering is offset by `PL_BASE`, so persistence and lookup must remain aligned with Linux global pin IDs.

## Dependencies And Integration Points

It depends on the sunxi pinctrl core and OF platform matching. It integrates sleep-domain functions `s_uart0`, `s_i2c0`, `s_i2c1`, `s_jtag`, `s_pwm`, and `s_cir`, with IRQ mappings through mux value `0x6`.

## Risks

The main risks are incorrect `PL_BASE` handling and IO-bias variant selection. A wrong pin base makes all consumers request the wrong global pins, while a wrong bias mode can affect low-power domain voltage handling. Because this controller is small and sleep-domain oriented, missing it can break wake, PMIC, or low-power serial paths even when the main PIO works.

## Test Signals

Validate probe from the R-PIO compatible, debugfs names PL0-PL11, GPIO and IRQ operation on PL pins, wake-capable interrupt behavior, and mux tests for sleep UART, I2C, PWM, CIR, and JTAG.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a100-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a100.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a100.c

## Purpose

This file provides the main A100 PIO pin/function table for banks PB through PH. It enables GPIO, IRQ, and mux support for multimedia, storage, serial, audio, display, camera, and Ethernet functions on the main pin controller.

## Important APIs, Types, And Functions

Important objects are `a100_pins[]`, `a100_irq_bank_map[]`, `a100_pinctrl_data`, `a100_pinctrl_probe()`, `a100_pinctrl_match[]`, and `a100_pinctrl_driver`. The descriptor maps seven IRQ banks through `{ 1, 2, 3, 4, 5, 6, 7 }` and uses `BIAS_VOLTAGE_PIO_POW_MODE_CTL`.

## Control Flow

The platform driver binds to `allwinner,sun50i-a100-pinctrl`. Probe calls `sunxi_pinctrl_init()`, after which the shared core registers all pins, groups functions by string name, and services mux/GPIO/IRQ/pinconf operations using the table. This file is module-capable through `MODULE_DEVICE_TABLE()` and `module_platform_driver()`.

## State And Persistence

Local data is static. Runtime state lives in common sunxi structures and PIO registers. IRQ banks are logical bank indexes in the descriptor, while `a100_irq_bank_map` maps them to hardware banks PB-PH. IO bias configuration uses PIO power-mode control registers.

## Dependencies And Integration Points

The table integrates A100 functions such as UART, SPI, I2C, JTAG/JTAG GPU, SPDIF, I2S, DMIC, NAND, MMC, LCD, LVDS, DSI, CSI, TCON, PWM, LEDC, CIR, EMAC, PLL, and BIST. It depends on the generic sunxi pinctrl binding and common driver.

## Risks

Dense IRQ annotation across seven banks creates off-by-one and bank-map risks. Shared function names with per-lane suffixes such as `i2s*_din*` and `i2s*_dout*` must match device-tree expectations exactly. Since the driver can be modular while the config is currently bool, future build changes need to preserve init ordering for early console and storage pins.

## Test Signals

Useful signals are successful probe, debugfs listing for PB-PH, GPIO tests across all banks, external interrupt tests for every IRQ bank, IO bias readback, and peripheral tests for UART console, MMC, NAND, SPI, I2C, display, audio, camera, LEDC, CIR, and EMAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a64-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a64-r.c

## Purpose

This file describes the Allwinner A64 R-PIO controller, covering sleep-domain PL0-PL12 pins. It supplies the reduced R-bank pin table used for low-power serial, RSB/I2C, PWM, CIR, JTAG, GPIO, and wake interrupt use cases.

## Important APIs, Types, And Functions

The file defines `sun50i_a64_r_pins[]`, `sun50i_a64_r_pinctrl_data`, `sun50i_a64_r_pinctrl_probe()`, `sun50i_a64_r_pinctrl_match[]`, and `sun50i_a64_r_pinctrl_driver`. The descriptor sets `.pin_base = PL_BASE` and `.irq_banks = 1`.

## Control Flow

The built-in platform driver binds to `allwinner,sun50i-a64-r-pinctrl`. Probe calls `sunxi_pinctrl_init()` with the R-PIO descriptor. The shared core uses `PL_BASE` to expose the pins under the global PL numbering and handles mux, GPIO, and IRQ requests.

## State And Persistence

This source contains immutable data only. Runtime state is in common sunxi objects and R-PIO registers. The wake/sleep domain nature means register state may be relevant across low-power transitions, but no local suspend/resume logic is implemented here.

## Dependencies And Integration Points

The table integrates `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_pwm`, and `s_cir_rx` functions, plus PL external interrupts through mux value `0x6`. It depends on the shared sunxi core and OF platform matching.

## Risks

`PL_BASE` must match the core's global pin numbering or every consumer is shifted. R-PIO pins often back PMIC or wake functions, so missing IRQ entries or wrong mux values can produce power-management failures rather than obvious boot failures. A64 lacks the explicit IO-bias variant used by newer R-PIO files, so copying descriptors between SoCs would be unsafe.

## Test Signals

Validate binding, debugfs PL0-PL12 visibility, GPIO and PL_EINT tests, suspend/wake tests, and functional checks for RSB/I2C to PMIC, sleep UART, PWM, CIR receive, and JTAG pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a64-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a64.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a64.c

## Purpose

This file provides the main Allwinner A64 PIO table for banks PB through PH. It enumerates GPIO, mux, and external interrupt capabilities for storage, display, camera, audio, serial, and network-related pins.

## Important APIs, Types, And Functions

The main definitions are `a64_pins[]`, `a64_pinctrl_data`, `a64_pinctrl_probe()`, `a64_pinctrl_match[]`, and `a64_pinctrl_driver`. The descriptor sets `.irq_banks = 3` and relies on the common sunxi core for all runtime operations.

## Control Flow

The built-in driver matches `allwinner,sun50i-a64-pinctrl` and calls `sunxi_pinctrl_init()` from probe. The core then builds pin groups/functions from `a64_pins[]` and programs PIO mux, pull, drive, data, and IRQ registers on demand.

## State And Persistence

Only static table data is local. Hardware state persists in PIO registers until reset or reconfiguration. The three IRQ banks correspond to the banks with EINT annotations in the table and are interpreted by the common IRQ support.

## Dependencies And Integration Points

The file integrates functions including UART, JTAG, SIM, audio interfaces, NAND, MMC, SPI, LCD, LVDS, CSI/CCIR, TS, I2C, PWM, EMAC, SPDIF, and microphone pins. It depends on Linux OF platform binding and `pinctrl-sunxi.h`.

## Risks

The table mixes banks with and without IRQ support and has many overlapping storage/display/audio functions. Wrong function names or mux values break device-tree consumers silently. Since `.irq_banks = 3` is positional rather than an explicit map, changes to the table must preserve the core's expected bank ordering.

## Test Signals

Validation should include A64 probe, debugfs pin/function review, GPIO tests on PB-PH, EINT tests on all IRQ-capable banks, and board tests for UART, MMC, NAND/SPI, display, camera, I2C, audio, PWM, and Ethernet-related pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h5.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h5.c

## Purpose

This file describes the Allwinner H5 main PIO controller for banks PA, PC, PD, PE, PF, and PG. It supports GPIO, mux, and interrupt routing for common H5 board peripherals.

## Important APIs, Types, And Functions

Important objects are `sun50i_h5_pins[]`, `sun50i_h5_pinctrl_data_broken`, `sun50i_h5_pinctrl_data`, `sun50i_h5_pinctrl_probe()`, `sun50i_h5_pinctrl_match[]`, and `sun50i_h5_pinctrl_driver`. The probe path is unusual because it calls `platform_irq_count()` and selects between two descriptors.

## Control Flow

The built-in platform driver matches `allwinner,sun50i-h5-pinctrl`. Probe counts platform IRQ resources. With two IRQs it warns that the device tree lacks the PG bank IRQ and initializes a reduced descriptor; with three IRQs it initializes the full descriptor; any other count fails with `-EINVAL`. The common core then handles the pinctrl/GPIO/IRQ operations.

## State And Persistence

All local state is immutable. Runtime state is common-core data plus hardware registers. The descriptor sets `irq_read_needs_mux = true` and `disable_strict_mode = true`. The selected descriptor controls whether the PG interrupt bank is available for the lifetime of the device.

## Dependencies And Integration Points

The table integrates UART, JTAG, SIM, I2C, display interface, SPI, SPDIF, I2S, TS, MMC, NAND, EMAC, CSI, PWM, and GPIO interrupt functions. It depends on platform IRQ resources being described correctly in device tree.

## Risks

The probe compatibility path intentionally tolerates broken device trees, but systems with only two IRQs lose PG bank interrupt support. Device-tree resource counts are therefore part of functional behavior. `disable_strict_mode` keeps legacy mux/GPIO overlap permissive and should not be removed without board testing. Table risks are typical dense mux errors.

## Test Signals

Test with both two-IRQ and three-IRQ device trees, confirm warning behavior for the broken case, verify debugfs pin and IRQ bank exposure, exercise PG EINTs on corrected device trees, and run peripheral tests for UART, MMC, Ethernet, I2C, SPI, audio, display, and camera pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h6-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h6-r.c

## Purpose

This file supplies the H6 R-PIO descriptor for PL0-PL10 and PM0-PM4. It covers GPIO, wake interrupts, sleep-domain serial/I2C/RSB/PWM/CIR/JTAG, and one-wire style functions.

## Important APIs, Types, And Functions

The file defines `sun50i_h6_r_pins[]`, `sun50i_h6_r_pinctrl_data`, `sun50i_h6_r_pinctrl_probe()`, `sun50i_h6_r_pinctrl_match[]`, and `sun50i_h6_r_pinctrl_driver`. The descriptor uses `.pin_base = PL_BASE`, `.irq_banks = 2`, and `.io_bias_cfg_variant = BIAS_VOLTAGE_PIO_POW_MODE_SEL`.

## Control Flow

The built-in driver matches `allwinner,sun50i-h6-r-pinctrl`. Probe calls `sunxi_pinctrl_init()`, and the common core registers the R-PIO pins and handles GPIO, pinmux, pinconf, and IRQ operations.

## State And Persistence

The file is declarative. Runtime state is stored in R-PIO registers and common driver structures. IO bias selection uses the PIO power-mode select variant, which is different from several other SoCs in this subset.

## Dependencies And Integration Points

It depends on `pinctrl-sunxi.h` and OF platform matching. It integrates `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_pwm`, `s_cir_rx`, `s_w1`, and `1wire` functions with PL/PM external interrupts.

## Risks

The mixed PL/PM R-PIO layout makes `.irq_banks = 2` and `PL_BASE` important. Incorrect IO-bias variant selection could misprogram voltage-domain controls. The table contains both `s_w1` and `1wire` naming, so device-tree users must match the exact function names expected by this driver.

## Test Signals

Validate probe, PL and PM pin visibility, GPIO and EINT operation on both banks, IO-bias register behavior, suspend/wake flows, and functional tests for RSB/I2C, sleep UART, CIR, PWM, and one-wire pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h6-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h6.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h6.c

## Purpose

This file describes the main Allwinner H6 PIO controller for banks PA, PB, PC, PD, PF, PG, and PH. It supplies mux and interrupt data for Ethernet, camera/display, storage, audio, serial, SIM, HDMI, and related functions.

## Important APIs, Types, And Functions

Important definitions are `h6_pins[]`, `h6_irq_bank_map[]`, `h6_pinctrl_data`, `h6_pinctrl_probe()`, `h6_pinctrl_match[]`, and `h6_pinctrl_driver`. The descriptor sets `.irq_banks = 4`, maps IRQ banks through `{ 1, 5, 6, 7 }`, enables `irq_read_needs_mux`, and uses `BIAS_VOLTAGE_PIO_POW_MODE_SEL`.

## Control Flow

The built-in driver matches `allwinner,sun50i-h6-pinctrl`. Probe calls `sunxi_pinctrl_init()`. The common core uses the explicit IRQ bank map to translate logical IRQ bank positions to hardware banks PB, PF, PG, and PH while servicing mux, GPIO, pinconf, and IRQ operations.

## State And Persistence

Local data is static. Runtime state is common-core bookkeeping plus PIO register contents. IRQ readback depends on mux state, and IO bias uses the power-mode select register variant.

## Dependencies And Integration Points

The table integrates EMAC, CCIR/CSI, I2S and H-I2S variants, I2C, PWM, NAND, SPI, MMC, UART, SIM, SPDIF, TS, LCD, HDMI, JTAG, IR transmit, and DMIC functions. It depends on the common sunxi pinctrl and GPIO/IRQ infrastructure.

## Risks

The explicit IRQ bank map is a key correctness point because the hardware IRQ-capable banks are not contiguous. Several early PA pins list only peripheral functions and lack normal GPIO entries, so assumptions that every descriptor has gpio-in/out are unsafe. IO-bias variant and mux-aware IRQ reads are SoC-specific and should not be generalized without hardware tests.

## Test Signals

Test H6 probe, debugfs pin and IRQ map output, GPIO behavior on banks with GPIO entries, IRQ tests on PB/PF/PG/PH, IO-bias readback, and peripheral mux tests for Ethernet, camera, MMC, NAND/SPI, UART, I2C, audio, HDMI, and display pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h616-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h616-r.c

## Purpose

This small file describes the H616 R-PIO controller for PL0 and PL1. It exposes the sleep-domain pins used for `s_rsb` or `s_i2c` SCK/SDA plus GPIO input/output.

## Important APIs, Types, And Functions

The definitions are `sun50i_h616_r_pins[]`, `sun50i_h616_r_pinctrl_data`, `sun50i_h616_r_pinctrl_probe()`, `sun50i_h616_r_pinctrl_match[]`, and `sun50i_h616_r_pinctrl_driver`. The descriptor sets `.pin_base = PL_BASE` and does not declare IRQ banks.

## Control Flow

The built-in driver matches `allwinner,sun50i-h616-r-pinctrl`. Probe calls `sunxi_pinctrl_init()` and the common core registers two PL pins for GPIO and mux use.

## State And Persistence

All local data is static. Runtime state is the shared core's device data and R-PIO register contents. No local suspend, resume, or IRQ behavior is defined.

## Dependencies And Integration Points

This file depends on OF platform binding and the sunxi common core. It integrates the low-power serial bus pins used by PMIC/control paths through `s_rsb` and `s_i2c` function names.

## Risks

Because only two pins are described, wrong `PL_BASE` or function ordering would break the entire controller. Lack of IRQ bank data means consumers must not expect wake interrupts from this descriptor. Copying richer R-PIO descriptors from other SoCs would add unsupported behavior.

## Test Signals

Validation includes probe, debugfs visibility for PL0 and PL1, GPIO direction/value tests, and functional RSB/I2C communication on the sleep-domain bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h616-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h616.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h616.c

## Purpose

This file supplies the main Allwinner H616 PIO table for banks PA, PC, PD, PE, PF, PG, PH, and PI. It describes GPIO, mux, IO-bias, and external interrupt capabilities for storage, networking, display, audio, camera, serial, and transport-stream functions.

## Important APIs, Types, And Functions

Important definitions are `h616_pins[]`, `h616_irq_bank_map[]`, `h616_pinctrl_data`, `h616_pinctrl_probe()`, `h616_pinctrl_match[]`, and `h616_pinctrl_driver`. The descriptor uses `ARRAY_SIZE(h616_irq_bank_map)`, maps IRQ banks through `{ 0, 2, 3, 4, 5, 6, 7, 8 }`, enables `irq_read_needs_mux`, and selects `BIAS_VOLTAGE_PIO_POW_MODE_CTL`.

## Control Flow

The built-in driver binds to `allwinner,sun50i-h616-pinctrl` and calls `sunxi_pinctrl_init()` in probe. The common driver registers all pins and translates the non-contiguous IRQ bank map when handling external interrupts.

## State And Persistence

Local state is immutable descriptor data. Runtime state is common-core data plus hardware PIO register contents. IO bias is managed through the PIO power-mode control variant, and interrupt readback depends on mux state.

## Dependencies And Integration Points

The table integrates EMAC0/EMAC1, I2C, I2S, PWM, NAND, MMC, SPI, UART, SIM, SPDIF, DMIC, LCD, LVDS, HDMI, CSI, TCON, TS, clock fanout, IR receive, JTAG, and GPIO interrupt functions. It depends on the shared sunxi pinctrl core.

## Risks

The table is large and has non-contiguous banks, making IRQ bank map correctness critical. H616 has many similarly named functions such as `emac0` versus `emac1` and lane-specific I2S names; spelling or mux-value drift breaks device-tree consumers. IO bias variant differs from H6, so cross-SoC copy/paste can misprogram voltage-domain registers.

## Test Signals

Validate probe, debugfs pin/function output for all banks, GPIO tests on PA/PC-PI, IRQ tests for each mapped bank, IO-bias readback, and peripheral tests for Ethernet, MMC, NAND/SPI, UART, I2C, display, HDMI, audio, camera, TS, and clock fanout pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h616.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun55i-a523-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun55i-a523-r.c

## Purpose

This file provides the Allwinner A523 R-PIO controller descriptor using the newer device-tree-table helper rather than a hand-written pin array. It covers PL and PM sleep-domain banks with generated pin descriptors, IRQ bank mapping, IRQ mux values, and IO-bias settings.

## Important APIs, Types, And Functions

Important objects are `a523_r_nr_bank_pins[]`, `a523_r_irq_bank_map[]`, `a523_r_irq_bank_muxes[]`, `a523_r_pinctrl_data`, `a523_r_pinctrl_probe()`, `a523_r_pinctrl_match[]`, and `a523_r_pinctrl_driver`. Probe calls `sunxi_pinctrl_dt_table_init()` with `SUNXI_PINCTRL_NEW_REG_LAYOUT`.

## Control Flow

The built-in platform driver matches `allwinner,sun55i-a523-r-pinctrl`. Probe asks the common DT-table helper to synthesize the pin table from bank sizes `{ 14, 6 }`, IRQ mux values `{ 14, 14 }`, descriptor metadata, and the new register-layout flag. The common core then registers pins and services GPIO, pinmux, pinconf, and IRQ requests.

## State And Persistence

The static arrays describe bank shape and IRQ capabilities. The generated pin table and driver state are owned by the common sunxi core after initialization. Runtime state persists only in R-PIO hardware registers until reset or reconfiguration. IO bias uses `BIAS_VOLTAGE_PIO_POW_MODE_SEL`.

## Dependencies And Integration Points

The file depends on `pinctrl-sunxi-dt` support through `sunxi_pinctrl_dt_table_init()`, OF platform matching, and the common sunxi core. It integrates PL/PM R-PIO pins starting at `PL_BASE`, two IRQ banks, mux value 14 for IRQ mode, and the new register layout used by newer Allwinner controllers.

## Risks

Because pins are generated, the bank-size and IRQ-mux arrays are the source of truth; a wrong count shifts every generated pin after the error. `a523_r_pinctrl_data` is non-const because the helper populates descriptor fields, so accidental reuse across multiple instances would need review. The new register layout, `PL_BASE`, IO-bias variant, and IRQ mux value must all match A523 R-PIO hardware.

## Test Signals

Validate A523 R-PIO probe, generated debugfs pin names for PL0-PL13 and PM0-PM5, GPIO tests across both banks, IRQ tests using mux value 14, IO-bias readback, and suspend/wake paths that rely on R-PIO pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun55i-a523-r.c -->

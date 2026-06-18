# Research Report: subset-b-005116

This grouped report covers the requested Allwinner sunxi pinctrl source files under `sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/`. Each section is source-tree aligned and wrapped for reconciliation into the per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun55i-a523.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun55i-a523.c

Purpose: This is the built-in platform driver for the Allwinner SUN55I A523 pin controller. Unlike many older sunxi drivers in this set, it does not hard-code every pin/function table in C. It provides compact bank metadata to the generic DT-driven table builder in `pinctrl-sunxi-dt.c`, so the actual peripheral function groups come from child nodes in the device tree.

Important APIs, types, and data: The file defines `a523_nr_bank_pins`, listing implemented pin counts for banks PA through PK with PA absent and PB..PK present. `a523_irq_bank_map` maps ten interrupt-capable banks, and `a523_irq_bank_muxes` marks IRQ mux value 14 for PB..PK. `a523_pinctrl_data` is a `struct sunxi_pinctrl_desc` with `irq_banks`, `irq_bank_map`, `irq_read_needs_mux = true`, and `io_bias_cfg_variant = BIAS_VOLTAGE_PIO_POW_MODE_SEL`. The probe calls `sunxi_pinctrl_dt_table_init()` with `SUNXI_PINCTRL_NEW_REG_LAYOUT | SUNXI_PINCTRL_ELEVEN_BANKS`.

Control flow: Device-tree matching on `allwinner,sun55i-a523-pinctrl` binds `a523_pinctrl_driver`. `a523_pinctrl_probe()` passes the bank pin counts, per-bank IRQ mux values, descriptor, and register-layout flags to the DT table builder. The generated descriptor is then handed to the shared sunxi pinctrl core.

State and persistence: Runtime state is devm-allocated by the generic builder and platform core. This file contributes static descriptor metadata only; no persistent storage, firmware writes, or module-global mutable state beyond the descriptor object are used.

Dependencies and integration points: It depends on `pinctrl-sunxi.h`, Linux platform/OF matching, and the DT child binding using `pins`, `function`, and `allwinner,pinmux`. It integrates with GPIO, IRQ, pinmux, and pin configuration paths implemented by the shared sunxi pinctrl core.

Risks: The critical risks are bad bank counts, an incorrect IRQ bank map, or a wrong IRQ mux value, because those errors would create invalid pin numbers or misroute external interrupts. Because functions are DT-supplied, binding drift or missing DT pin groups can silently remove expected mux options. The new register-layout and eleven-bank flags must match the A523 register block exactly.

Test signals: Useful checks include boot probing on an A523 DT, validating all expected pin names PB0..PK23/PK24 boundaries, exercising GPIO input/output, testing external interrupts on each IRQ bank, and confirming voltage bias configuration through boards using multiple IO domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun55i-a523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun5i.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun5i.c

Purpose: This driver describes the pin controller for sun5i-family SoCs: Allwinner A10s, A13, and NextThing GR8. It is a classic static sunxi pin table, enumerating 119 pins across banks A through G and their mux alternatives for GPIO, storage, display, camera, audio, serial, network, and interrupt use.

Important APIs, types, and data: The variant bits `PINCTRL_SUN5I_A10S`, `PINCTRL_SUN5I_A13`, and `PINCTRL_SUN5I_GR8` gate pins and functions that exist only on specific chips. `sun5i_pins[]` is an array of `struct sunxi_desc_pin` built with `SUNXI_PIN`, `SUNXI_PIN_VARIANT`, `SUNXI_FUNCTION`, `SUNXI_FUNCTION_VARIANT`, and `SUNXI_FUNCTION_IRQ`. Banks include PA0-PA17, PB0-PB20, PC0-PC19, PD0-PD27, PE0-PE11, PF0-PF5, and PG0-PG13, with several documented holes. Major functions include `emac`, `ts0`, `keypad`, `uart0`..`uart3`, `i2c0`..`i2c2`, `spi0`/`spi1`, `nand`, `mmc0`/`mmc1`/`mmc2`, `lcd`, `csi`, `i2s`, `pwm`, `ir`, and `jtag`. The descriptor sets `.irq_banks = 1` and `.disable_strict_mode = true`.

Control flow: OF matching selects one of three compatible strings and stores the matching variant bit in `.data`. `sun5i_pinctrl_probe()` retrieves that with `of_device_get_match_data()` and calls `sunxi_pinctrl_init_with_flags()`, causing the common pinctrl code to filter variant-gated entries and register pinctrl/GPIO/IRQ resources.

State and persistence: The pin/function table is read-only static kernel data. Runtime state such as selected muxes, GPIO state, and IRQ handlers lives in the shared sunxi pinctrl core and hardware registers. There is no persistence across reboot.

Dependencies and integration points: This file depends on the common sunxi macros and core registration in `pinctrl-sunxi.h`. It integrates with board DT nodes using compatible strings `allwinner,sun5i-a10s-pinctrl`, `allwinner,sun5i-a13-pinctrl`, and `nextthing,gr8-pinctrl`; downstream peripheral drivers consume the named functions through pinctrl states.

Risks: The main risks are variant mistakes, especially exposing A10s/GR8-only pins to A13 or hiding shared pins from GR8. `.disable_strict_mode` permits mux sharing patterns that can be necessary on older SoCs, but it weakens conflict detection. The single IRQ bank and `SUNXI_FUNCTION_IRQ(0x6, n)` encoding must match the external interrupt hardware.

Test signals: Build coverage should catch macro/descriptor errors. Runtime validation should cover each compatible, probe variant filtering, GPIO toggling per bank, EINT handling, and representative peripheral states: MMC, NAND, LCD, CSI, EMAC, UART, I2C, SPI, I2S, PWM, and IR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun5i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun6i-a31-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun6i-a31-r.c

Purpose: This file describes the A31 "R" or special/low-power pin controller, separate from the main PIO controller. It covers PL and PM pins used by always-on or system-management peripherals.

Important APIs, types, and data: `sun6i_a31_r_pins[]` defines 17 pins: PL0-PL8 and PM0-PM7, with a hole between L and M. Functions include `gpio_in`, `gpio_out`, `s_i2c`, `s_p2wi`, `s_uart`, `s_ir`, `s_jtag`, `1wire`, and `rtc`. Interrupt-capable pins use `SUNXI_FUNCTION_IRQ_BANK(0x2, bank, irq)`, mapping PL to IRQ bank 0 and PM to IRQ bank 1. `sun6i_a31_r_pinctrl_data` sets `.pin_base = PL_BASE`, `.irq_banks = 2`, and `.disable_strict_mode = true`.

Control flow: The platform driver binds on `allwinner,sun6i-a31-r-pinctrl`. Probe directly calls `sunxi_pinctrl_init()` with the static descriptor, so no variant filtering or DT-built function table is involved.

State and persistence: All pin descriptions are static constants. Runtime mux and IRQ state is held by the shared pinctrl driver and hardware. The file itself stores no persistent configuration.

Dependencies and integration points: It depends on the common sunxi pinctrl core and the special `PL_BASE` numbering convention, which prevents collisions with main-controller pins. It integrates with DT pinctrl states for secure/standby I2C/P2WI, low-power UART, IR, JTAG, 1-wire, RTC clock output, GPIO, and EINT consumers.

Risks: `PL_BASE` and IRQ bank numbering are critical. An off-by-one would direct PM interrupts into the wrong irqchip bank. Low-power peripherals often remain active in suspend paths, so wrong muxing can break PMIC, RTC, or wakeup behavior. Strict mode is disabled, so pin conflicts may require board-level validation.

Test signals: Probe on A31 hardware, request GPIOs from PL/PM, exercise PL/PM EINT wake interrupts, validate `s_i2c` or `s_p2wi` for PMIC communication, and check suspend/resume with wake-capable pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun6i-a31-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun6i-a31.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun6i-a31.c

Purpose: This is the main pin controller driver for Allwinner A31 and A31s SoCs. It provides a large static mux table for 165 pins across banks PA through PH and handles SoC differences with variant bits.

Important APIs, types, and data: `PINCTRL_SUN6I_A31` and `PINCTRL_SUN6I_A31S` select chip-specific pins/functions. `sun6i_a31_pins[]` uses `SUNXI_PIN`, `SUNXI_PIN_VARIANT`, and `SUNXI_FUNCTION_VARIANT` for bank-wide and chip-specific entries. Major mux functions include `gmac`, `lcd0`, `lcd1`, `uart0`..`uart5`, `spi0`..`spi3`, `nand0`/`nand1`, `mmc0`..`mmc3`, `i2c0`..`i2c3`, `csi`, `ts`, `i2s0`/`i2s1`, `pwm`, `ir`, `jtag`, `clk`, and an undocumented `spdif` mapping. IRQ functions use mux value `0x6` across four IRQ banks, covering PA, PB, PE, and PG style interrupt groups. The descriptor sets `.irq_banks = 4` and `.disable_strict_mode = true`.

Control flow: OF match data selects either `allwinner,sun6i-a31-pinctrl` or `allwinner,sun6i-a31s-pinctrl`. `sun6i_a31_pinctrl_probe()` calls `sunxi_pinctrl_init_with_flags()` with the selected variant, allowing the shared core to publish only valid pins/functions.

State and persistence: Source state is static descriptor data. Runtime pin state is in hardware and in the common sunxi pinctrl objects created during probe. There is no durable state.

Dependencies and integration points: The file integrates with the Linux pinctrl, GPIO, and IRQ subsystems through the common sunxi core. Board DTS files select named functions in pinctrl states for Ethernet, display, camera, NAND/MMC, serial, audio, and miscellaneous clocks.

Risks: Variant handling is a major risk because A31-only pins include extra PC/PE/PH entries while A31s has holes and reduced functions. The undocumented SPDIF mux relies on vendor sources rather than the public manual. Large display, NAND, camera, and GMAC groups are sensitive to swapped mux values. Disabled strict mode can mask conflicting consumer states.

Test signals: Validate both A31 and A31s compatible strings, confirm variant-only pins are filtered, test EINTs in all four IRQ banks, and run board-level probes for GMAC, LCD, MMC/NAND, UART/I2C/SPI, CSI, I2S, PWM, IR, and SPDIF where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun6i-a31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a23-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a23-r.c

Purpose: This driver describes the A23 reduced/always-on pin controller, covering the special PL bank used for standby and low-power peripherals.

Important APIs, types, and data: `sun8i_a23_r_pins[]` defines PL0-PL11. Every pin supports GPIO in/out, most have interrupt function `SUNXI_FUNCTION_IRQ_BANK(0x4, 0, n)`, and peripheral functions include `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_twi`, and `s_pwm`. The descriptor sets `.pin_base = PL_BASE`, `.irq_banks = 1`, and `.disable_strict_mode = true`.

Control flow: The platform driver matches `allwinner,sun8i-a23-r-pinctrl`. Probe calls `sunxi_pinctrl_init()` with the static descriptor, registering the PL pins with the shared sunxi pinctrl implementation.

State and persistence: All source-level pin metadata is const. Runtime mux, GPIO direction/value, and IRQ setup are managed by the common driver and hardware registers, with no persistent storage in this file.

Dependencies and integration points: The `PL_BASE` numbering convention links this special controller to the wider sunxi pin numbering scheme. It integrates with DT pinctrl consumers for PMIC/control buses (`s_rsb`, `s_i2c`, `s_twi`), standby UART, standby JTAG, standby PWM, GPIO, and wake-capable EINT.

Risks: Low-power bus pins are board-critical; wrong mux values can prevent PMIC access or wake behavior. IRQ mux `0x4` and the PL interrupt numbering must match the hardware. Because strict mode is disabled, runtime conflicts rely on board definitions and testing.

Test signals: Probe the A23 R controller, verify PL0/PL1 RSB or I2C operation, test PL EINT lines including wake from suspend, and validate GPIO direction/value on non-bus pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a23-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a23.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a23.c

Purpose: This file is the main A23 pinctrl driver. It statically describes 106 pins across PA, PB, PC, PD, PE, PF, PG, and PH, including holes where banks or ranges are absent.

Important APIs, types, and data: `sun8i_a23_pins[]` maps pin muxes with `SUNXI_PIN` and `SUNXI_FUNCTION_IRQ_BANK`. Functions include `spi0`, `spi1`, `uart0`..`uart4`, `jtag`, `i2c0`..`i2c2`, `mmc0`..`mmc2`, `nand0`, `lcd`, `csi`, `i2s0`, `i2s1`, `pwm0`, and `pwm1`. IRQ mappings use mux `0x4` across three IRQ banks, mainly PA, PB, and PG. `sun8i_a23_pinctrl_data` sets `.irq_banks = 3` and `.disable_strict_mode = true`.

Control flow: Matching on `allwinner,sun8i-a23-pinctrl` calls `sun8i_a23_pinctrl_probe()`, which invokes `sunxi_pinctrl_init()` with the static descriptor.

State and persistence: The table is static read-only data. The kernel's common pinctrl code allocates runtime state during probe and drives hardware registers for active pin states. Nothing persists outside the SoC register state.

Dependencies and integration points: The driver integrates with board DT pinctrl states for serial buses, storage, display, camera, audio, PWM, GPIO, and EINT. It depends on the common sunxi descriptor parser and pinctrl/GPIO/IRQ registration paths.

Risks: A23 has holes and compact IRQ bank mapping, so count/order mistakes can produce invalid pin names or wrong IRQ banks. Display, camera, NAND, and MMC groups span many pins and are vulnerable to incomplete board state definitions. Disabled strict mode makes consumer conflicts a board validation concern.

Test signals: Confirm probe and pin range registration, exercise IRQs from PA/PB/PG, test GPIO on each bank, and validate representative peripheral states for MMC, NAND, LCD, CSI, UART, I2C, SPI, I2S, and PWM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a33.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a33.c

Purpose: This driver describes the Allwinner A33 main pin controller. It is based on the A23 table but starts at PB and reflects A33-specific muxing, especially alternate UART and multimedia functions.

Important APIs, types, and data: `sun8i_a33_pins[]` defines 96 pins across PB, PC, PD, PE, PF, PG, and PH, with PA absent. Functions include `uart0`..`uart4`, `i2c0`..`i2c2`, `spi0`/`spi1`, `mmc0`..`mmc2`, `nand0`, `lcd`, `csi`, `i2s0`, `i2s1`, `pwm0`, and `pwm1`. IRQ functions use mux `0x4` across two IRQ banks, PB and PG. The descriptor sets `.irq_banks = 2` and `.disable_strict_mode = true`.

Control flow: The platform driver matches `allwinner,sun8i-a33-pinctrl`. Probe calls `sunxi_pinctrl_init()` with `sun8i_a33_pinctrl_data`, after which the common core registers pinctrl, GPIO, and IRQ services.

State and persistence: Static pin descriptors are immutable. Runtime mux selection and GPIO/IRQ state live in shared sunxi structures and MMIO registers; no persistent state exists.

Dependencies and integration points: It depends on `pinctrl-sunxi.h` and Linux platform/OF infrastructure. Integration is through DT pinctrl states consumed by UART, I2C, SPI, MMC, NAND, display, camera, audio, PWM, and GPIO users.

Risks: Because the table is similar to A23 but not identical, copy-forward mistakes are plausible. PB carries both UART2 and UART0 alternatives on early pins, making board states easy to misconfigure. IRQ bank count and mux value must match PB/PG EINT layout. Disabled strict mode can conceal multi-consumer conflicts until runtime.

Test signals: Build and boot with `allwinner,sun8i-a33-pinctrl`, verify PB and PG external interrupts, test UART0 remap options, and exercise storage/display/camera/audio pin groups on a representative A33 board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a33.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a83t-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a83t-r.c

Purpose: This file describes the A83T special R pin controller, which provides PL pins for standby/low-power functions.

Important APIs, types, and data: `sun8i_a83t_r_pins[]` defines PL0-PL12. Functions include `gpio_in`, `gpio_out`, `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_twi`, `s_pwm`, and standby IR-style functions. IRQ entries use `SUNXI_FUNCTION_IRQ_BANK(0x6, 0, n)` for one PL IRQ bank. `sun8i_a83t_r_pinctrl_data` sets `.pin_base = PL_BASE`, `.irq_banks = 1`, and `.disable_strict_mode = true`.

Control flow: The platform driver matches `allwinner,sun8i-a83t-r-pinctrl`, and probe calls `sunxi_pinctrl_init()` with the static descriptor.

State and persistence: The file only contributes static pin/function data. Runtime configuration is held in the common pinctrl driver and hardware registers, without durable persistence.

Dependencies and integration points: It integrates with DT nodes for A83T standby buses and wake-capable GPIO/IRQ users. The `PL_BASE` dependency is important so PL pins are numbered in the expected special-bank range.

Risks: Standby controllers often participate in PMIC, wakeup, and suspend/resume paths, so wrong mux data can cause system power-management failures. IRQ mux `0x6` differs from A23 R's `0x4`, so copying between drivers is risky. Strict mode is disabled.

Test signals: Validate probe, PL GPIO, PL EINT and suspend wake, PMIC bus operation over `s_rsb` or `s_i2c`, and standby UART/JTAG states if the board exposes them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a83t-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a83t.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a83t.c

Purpose: This is the main pinctrl driver for the Allwinner A83T SoC. It defines the static mux table for 105 pins across PB, PC, PD, PE, PF, PG, and PH.

Important APIs, types, and data: `sun8i_a83t_pins[]` uses sunxi descriptor macros to expose GPIO, IRQ, and peripheral mux functions. Major functions include `uart0`..`uart4`, `i2c0`..`i2c3`, `spi0`/`spi1`, `mmc0`..`mmc2`, `nand0`, `lcd`, `csi`, `i2s`, `pwm`, and related multimedia/storage functions. IRQ functions use mux `0x6` across three IRQ banks, covering PB, PG, and PH groups. The descriptor sets `.irq_banks = 3` and `.disable_strict_mode = true`.

Control flow: OF match on `allwinner,sun8i-a83t-pinctrl` binds the platform driver. Probe calls `sunxi_pinctrl_init()` with the static descriptor, and the common core registers the pin groups, GPIO chips, and IRQ domains.

State and persistence: Pin data is static and read-only. Active mux selections, GPIO values, and IRQ state are runtime hardware/common-driver state only.

Dependencies and integration points: The file depends on the shared sunxi pinctrl macros and core. Integration points are DT pinctrl states for storage, display, camera, serial, audio, PWM, GPIO, and external interrupt consumers.

Risks: A83T has several high-pin-count peripheral groups; incomplete DTS states can leave buses partially muxed. IRQ bank mapping must match PB/PG/PH EINT layout. Since strict mode is disabled, duplicate pin ownership may be detected only by board behavior.

Test signals: Probe on A83T hardware, validate GPIO per bank, exercise all three IRQ banks, and run representative pinctrl states for MMC/NAND, LCD, CSI, UART/I2C/SPI, I2S, and PWM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a83t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-h3-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-h3-r.c

Purpose: This driver describes the H3 R pin controller, a small PL-bank controller used for low-power and system functions.

Important APIs, types, and data: `sun8i_h3_r_pins[]` defines PL0-PL11. Functions include `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_twi`, `s_pwm`, and `s_cir_rx`, plus GPIO and interrupt mappings. The descriptor sets `.pin_base = PL_BASE`, `.irq_banks = 1`, `.irq_read_needs_mux = true`, and `.disable_strict_mode = true`.

Control flow: The platform driver matches `allwinner,sun8i-h3-r-pinctrl`. Probe invokes `sunxi_pinctrl_init()` with `sun8i_h3_r_pinctrl_data`.

State and persistence: Source-level state is static pin metadata. Runtime pinctrl and IRQ state is in the common driver and SoC registers. There is no persistence.

Dependencies and integration points: The file integrates with standby bus, UART, JTAG, PWM, IR receiver, GPIO, and wake interrupt consumers. `irq_read_needs_mux` tells the common IRQ path it must handle mux state when reading IRQ-capable pins.

Risks: Wake and PMIC buses are sensitive to mux errors. The `irq_read_needs_mux` flag must be correct, otherwise IRQ/GPIO reads can be wrong when a pin is in IRQ mode. Disabled strict mode requires board-level care.

Test signals: Validate PL IRQ reads, wakeup events, RSB/I2C PMIC access, `s_cir_rx` if present, and suspend/resume behavior on an H3 board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-h3-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-h3.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-h3.c

Purpose: This is the main H3 pin controller driver. It defines 93 pins across PA, PC, PD, PE, PF, and PG, with banks B and some ranges absent.

Important APIs, types, and data: `sun8i_h3_pins[]` declares GPIO, IRQ, and peripheral mux functions. Major functions include `uart0`..`uart3`, `i2c0`..`i2c2`, `spi0`/`spi1`, `mmc0`..`mmc2`, `emac`, `lcd`, `csi`, `i2s0`, `i2s1`, `spdif`, `sim`, `pwm0`, `ir`, and `jtag`. IRQ functions use mux `0x6` and two IRQ banks, with `.irq_read_needs_mux = true`. The descriptor also sets `.disable_strict_mode = true`.

Control flow: The OF compatible `allwinner,sun8i-h3-pinctrl` selects this platform driver. Probe passes the static descriptor to `sunxi_pinctrl_init()`.

State and persistence: The pin table is static. The common core manages runtime muxing, GPIO values, and IRQ state. No persistent state is written by this file.

Dependencies and integration points: It depends on the shared sunxi pinctrl core and Linux OF/platform infrastructure. It is consumed by H3 board DTS pinctrl states for Ethernet, storage, display/camera/audio, serial buses, GPIOs, and external interrupts.

Risks: H3 pin multiplexing is dense on PA/PC/PD/PG, so DTS conflicts are easy. IRQ read behavior depends on `irq_read_needs_mux`. Multimedia and storage groups span many pins and require complete board states. Disabled strict mode can allow overlapping use.

Test signals: Boot on H3 hardware, exercise GPIO and IRQ on PA/PG, verify EMAC, MMC0/MMC1/MMC2, UART/I2C/SPI, LCD/CSI, I2S/SPDIF, PWM, IR, and SIM pinctrl states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-h3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-v3s.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-v3s.c

Purpose: This driver describes the V3 and V3s pin controller. It reuses one static table with variant flags to represent differences between the larger V3 and smaller V3s packages.

Important APIs, types, and data: `PINCTRL_SUN8I_V3` and `PINCTRL_SUN8I_V3S` select chip-specific pins. `sun8i_v3s_pins[]` covers 88 pins across PB, PC, PE, PF, and PG, with V3-only entries such as extra JTAG, CSI, and PG UART/I2S pins gated by `SUNXI_PIN_VARIANT` or `SUNXI_FUNCTION_VARIANT`. Functions include `uart0`..`uart2`, `i2c0`/`i2c1`, `pwm0`/`pwm1`, `jtag`, `csi`, `mmc0`/`mmc1`, `spi0`, `i2s`, and GPIO/IRQ. `sun8i_v3s_pinctrl_irq_bank_map[] = { 1, 2 }` maps the two IRQ banks, and the descriptor sets `.irq_read_needs_mux = true`.

Control flow: OF match data selects `allwinner,sun8i-v3-pinctrl` or `allwinner,sun8i-v3s-pinctrl`. Probe reads the variant and calls `sunxi_pinctrl_init_with_flags()`.

State and persistence: Static descriptors carry all source-level data. Runtime state is common-driver/hardware state only.

Dependencies and integration points: It depends on the shared sunxi pinctrl core and variant filtering. Board DTS files use the named functions for camera, MMC, serial buses, I2S, PWM, GPIO, and IRQ.

Risks: Variant gating is the highest-risk area: exposing V3-only PG pins on V3s would create unusable pinctrl states, while hiding them would break V3 boards. The custom IRQ bank map must line up with the physical banks. The descriptor lacks `disable_strict_mode`, unlike many older tables, so conflicts may be rejected more strictly.

Test signals: Boot both compatible variants, confirm variant-only pins appear only for V3, test IRQs through the mapped banks, and validate CSI, MMC, UART/I2C/SPI, I2S, PWM, and GPIO states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-v3s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun9i-a80-r.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun9i-a80-r.c

Purpose: This driver describes the A80 R pin controller, covering low-power/special banks PL, PM, and PN.

Important APIs, types, and data: `sun9i_a80_r_pins[]` defines 25 pins: PL0-PL9, selected PM0-PM15 pins with holes, and PN0-PN1. Functions include `s_uart`, `s_jtag`, `s_cir_rx`, `1wire`, `s_ps2`, `s_i2s0`, `s_i2s1`, `s_i2c0`, `s_i2c1`, and `s_rsb`, plus GPIO and IRQ. IRQ functions use mux `0x6` across two banks. The descriptor sets `.pin_base = PL_BASE`, `.irq_banks = 2`, `.disable_strict_mode = true`, and `.io_bias_cfg_variant = BIAS_VOLTAGE_GRP_CONFIG`.

Control flow: OF matching on `allwinner,sun9i-a80-r-pinctrl` invokes probe, which calls `sunxi_pinctrl_init()` with the static descriptor.

State and persistence: The file's state is static C data. Runtime mux, bias, GPIO, and IRQ settings live in hardware and common sunxi driver structures. No persistence is implemented.

Dependencies and integration points: It depends on `PL_BASE` for special-bank numbering and on the common bias-voltage handling selected by `BIAS_VOLTAGE_GRP_CONFIG`. It integrates with standby serial, JTAG, IR, 1-wire, PS/2, I2S, I2C/RSB, GPIO, and wake interrupt consumers.

Risks: A80 R includes holes in PM, so pin numbering and array order matter. Voltage group configuration affects board IO levels. Low-power bus and wake pins are boot/suspend critical. Disabled strict mode weakens conflict rejection.

Test signals: Validate PL/PM/PN pin naming, test EINTs across both IRQ banks, check IO bias behavior on board domains, and exercise standby I2C/RSB, UART, JTAG, IR, I2S, and wake scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun9i-a80-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun9i-a80.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun9i-a80.c

Purpose: This is the main Allwinner A80 pin controller driver. It statically describes 132 pins across banks PA, PB, PC, PD, PE, PF, PG, and PH, including several holes.

Important APIs, types, and data: `sun9i_a80_pins[]` maps GPIO, IRQ, and peripheral functions for high-bandwidth peripherals. Major functions include `gmac`, `uart0`..`uart5`, `eclk`, `clk_out_a`, `clk_out_b`, `pwm0`..`pwm3`, `spi0`..`spi3`, `nand0`, `nand0_b`, `mmc0`..`mmc2`, `lcd0`, `csi`, `ts`, `i2c0`..`i2c4`, and `hdmi`. IRQ functions use mux `0x6` across five IRQ banks. The descriptor sets `.irq_banks = 5`, `.disable_strict_mode = true`, and `.io_bias_cfg_variant = BIAS_VOLTAGE_GRP_CONFIG`.

Control flow: The platform driver matches `allwinner,sun9i-a80-pinctrl`, and probe calls `sunxi_pinctrl_init()` with the descriptor. The shared sunxi core performs pinctrl, GPIO, IRQ, and bias registration.

State and persistence: Static pin tables are immutable. Runtime mux and bias state is held by hardware and the common driver; there is no persistent configuration store.

Dependencies and integration points: This file integrates with board DT pinctrl states for Ethernet, display, camera/transport stream, HDMI DDC/CEC, NAND/MMC, UART/I2C/SPI, PWM, clocks, GPIO, and EINT. It depends on group voltage bias support through `BIAS_VOLTAGE_GRP_CONFIG`.

Risks: The table is broad and has holes, increasing the chance of pin-numbering mistakes. GMAC, LCD0, NAND, CSI/TS, and HDMI groups are multi-pin and highly sensitive to partial configuration. IO bias group selection is board-electrical critical. Strict mode is disabled, so invalid sharing may not be rejected early.

Test signals: Boot an A80 board, validate all five IRQ banks, exercise GPIO per represented bank, test voltage bias on configurable IO groups, and run representative pinctrl states for GMAC, HDMI, LCD, CSI/TS, NAND/MMC, UART/I2C/SPI, PWM, and clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun9i-a80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-suniv-f1c100s.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-suniv-f1c100s.c

Purpose: This driver describes the suniv F1C100s pin controller, a compact Allwinner F-series SoC with banks PA through PF and a mix of LCD/camera/storage/audio/touch functions.

Important APIs, types, and data: `suniv_f1c100s_pins[]` defines 53 pins: PA0-PA3, PB0-PB3, PC0-PC3, PD0-PD21, PE0-PE12, and PF0-PF5. Functions include `rtp`, `i2s`, `uart0`..`uart2`, `spi0`/`spi1`, `dram`, `i2c0`/`i2c1`, `lcd`, `csi`, `mmc0`, `jtag`, `ir0`, `ir`, `pwm0`, `pwm1`, `clk0`, and GPIO/IRQ. IRQ entries use mux `0x6` across three IRQ banks. `suniv_f1c100s_pinctrl_data` sets `.irq_banks = 3`.

Control flow: The platform driver matches `allwinner,suniv-f1c100s-pinctrl`. Probe calls `sunxi_pinctrl_init()` with the static descriptor.

State and persistence: The file contains only static pin descriptors. Runtime mux, GPIO, and IRQ settings are common-driver/hardware state and do not persist across reboot.

Dependencies and integration points: It integrates with DT pinctrl states for resistive touch, DRAM-related pins, LCD, CSI, MMC0, serial buses, audio, IR, PWM, clock output, JTAG, GPIO, and external interrupts. It uses the standard sunxi descriptor path without variant filtering.

Risks: Some mux names are unusual or typo-prone, including `dgb0` in the PF1 JTAG/debug entry, so binding/users must match existing names. DRAM-related alternate functions are board-critical. The absence of `.disable_strict_mode` means conflicts may be enforced more strictly than in many older sunxi files.

Test signals: Probe on F1C100s hardware, validate GPIO and IRQ across banks, test LCD/CSI/MMC0 and UART/I2C/SPI states, and check touch/audio/IR/PWM/clock outputs on boards that expose them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-suniv-f1c100s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi-dt.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi-dt.c

Purpose: This file implements the generic DT-driven table builder used by newer Allwinner pinctrl drivers such as the A523 driver. It constructs a `struct sunxi_desc_pin` array at probe time from simple per-driver bank counts plus pin group information in the device tree, then calls the traditional sunxi pinctrl initializer.

Important APIs, types, and functions: `INVALID_MUX` is `0xff`. `sunxi_pinctrl_dt_read_pinmux()` reads the indexed `allwinner,pinmux` u32 property and falls back to the last value when fewer mux values are provided than pins. `init_pins_table()` counts pins from `pins_per_bank`, allocates `struct sunxi_desc_pin` entries and a contiguous pin-name buffer, then fills names like `PB0` and numbers based on `desc->pin_base` and `PINS_PER_BANK`. `prepare_function_table()` counts required functions, allocates a contiguous `struct sunxi_desc_function` table, pre-populates `gpio_in`, `gpio_out`, optional `irq`, and uses the `variant` field temporarily as a per-pin function count. `fill_pin_function()` reads each child node's `function`, `pins`, and `allwinner,pinmux` data, validates pin names and mux values, skips identical duplicate definitions, and warns on conflicts. `sunxi_pinctrl_dt_table_init()` is the exported integration point for per-SoC drivers.

Control flow: A per-SoC driver calls `sunxi_pinctrl_dt_table_init(pdev, pins_per_bank, irq_bank_muxes, desc, flags)`. The function initializes all pins, prepares base GPIO/IRQ functions, iterates every child pin group of the controller DT node to add named peripheral functions, clears the temporary `variant` counters, assigns `desc->pins`, and calls `sunxi_pinctrl_init_with_flags()`.

State and persistence: All allocated tables use `devm_kcalloc()` or `devm_kmalloc()` and are lifetime-bound to the platform device. The function mutates the caller-provided `desc` by incrementing `desc->npins` and setting `desc->pins`; callers should provide a fresh/static descriptor for one probe. There is no persistent storage.

Dependencies and integration points: It depends on OF property helpers, platform devices, slab allocation, `pinctrl-sunxi.h`, and the traditional sunxi pinctrl core. The DT binding must provide child nodes with `pins`, `function`, and `allwinner,pinmux`. IRQ metadata is supplied by the calling driver through `irq_bank_muxes` and optional descriptor bank maps.

Risks: `desc->npins` is incremented, not reset, so unexpected reprobe of a reused descriptor would overcount unless the platform lifecycle prevents it. `prepare_function_table()` can over-allocate for duplicate function definitions, which is safe but relies on later duplicate filtering. Missing or malformed DT properties only warn and skip entries, potentially leaving a peripheral without mux options. IRQ bank numbering is inferred while iterating pins and changes when banks have holes, so caller-provided bank maps and mux arrays must be consistent. Pin names are generated from bank counts only, so DT pin names outside generated ranges are ignored with warnings.

Test signals: Unit-like DT overlays can cover single and repeated `allwinner,pinmux` values, missing `function`, invalid mux, unknown pin names, duplicate identical functions, and conflicting redefinitions. Runtime testing should verify generated pin names, GPIO in/out availability on all pins, IRQ function insertion per `irq_bank_muxes`, and successful peripheral pinctrl selection from DT child groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi-dt.c -->

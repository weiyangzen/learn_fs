# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-tmpv7700.c

## Purpose

This file provides TMPV7700/TMPV7708-specific data for the Visconti pinctrl common driver. It defines register offsets, pins, groups, functions, GPIO mux entries, the register unlock sequence, and platform-driver binding for `toshiba,tmpv7708-pinctrl`.

## Important APIs, Types, And Data

- Register offset constants describe key/unlock registers, five pinmux registers, IO select/voltage/drive registers, and pull-enable/pull-select registers.
- `pins_tmpv7700[]` describes 35 pins: GPIO0-GPIO31 plus SPI pins `spi_sck`, `spi_sdo`, and `spi_sdi`. Each pin includes DSEL and PUDE/PUDSEL offsets and shifts.
- Group pin arrays cover I2C0-I2C8, SPI0-SPI6 with chip selects, UART0-UART3, PWM alternatives on GPIO4-GPIO19, and PCMIF input/output.
- `groups_tmpv7700[]` maps each group to a register offset, mask, and mux value.
- `functions_tmpv7700[]` exposes pinmux functions for I2C, SPI, UART, PWM, and PCMIF.
- `gpio_mux_tmpv7700[]` provides one GPIO mux operation per GPIO-capable pin, mostly clearing four-bit fields in `REG_PINMUX2` through `REG_PINMUX5`.
- `tmpv7700_pinctrl_unlock()` writes `1` to `REG_KEY_CTRL` and `tmpv7700_MAGIC_NUM` to `REG_KEY_CMD`.
- `tmpv7700_pinctrl_data` packages data for `visconti_pinctrl_probe()`.

## Control Flow

The platform driver registers at `arch_initcall()` and matches `toshiba,tmpv7708-pinctrl`. `tmpv7700_pinctrl_probe()` delegates to the common Visconti probe with `tmpv7700_pinctrl_data`. The common probe maps registers, registers the pinctrl device, invokes `tmpv7700_pinctrl_unlock()`, and enables pinctrl.

At runtime, function selection uses `groups_tmpv7700[]` register masks and values. GPIO request enable uses `gpio_mux_tmpv7700[]` to clear a pin’s mux field to GPIO mode. Pinconf uses the per-pin DSEL and pull offsets from `pins_tmpv7700[]`.

## State And Persistence

This file contains only static descriptor data and an unlock write sequence. Hardware state persists in the TMPV7700 pinmux and IO registers. The common driver owns private state, locking, and MMIO access.

## Dependencies And Integration Points

It depends on `pinctrl-common.h`, Linux platform/OF APIs, and the common Visconti implementation. It integrates with device trees that use `toshiba,tmpv7708-pinctrl`. Build inclusion is controlled by `CONFIG_PINCTRL_TMPV7700`.

The data model assumes the common driver can represent each functional group with a single register offset/mask/value tuple, which is true for the listed TMPV7700 groups.

## Risks And Edge Cases

- Register unlock must occur before protected pinmux writes are needed; the common probe calls unlock after registration and before `pinctrl_enable()`.
- `gpio_mux_tmpv7700[]` has 32 entries while `pins_tmpv7700[]` has 35 pins. The common GPIO path indexes by pin, so GPIO requests for the SPI-only pins would be unsafe unless those pins are never requested as GPIO.
- Many functions share the same physical pins with different four-bit mux values, such as PWM and UART/SPI alternatives; board device-tree states must avoid conflicts.
- The common driver assumes dense pin numbering from zero; TMPV7700 satisfies this with pins 0 through 34.

## Test Signals

Verify probe and unlock on TMPV7708 hardware or emulation, pinctrl debugfs function/group listings, GPIO requests for GPIO0-GPIO31, and pinmux selection for I2C0-I2C8, SPI0-SPI6 including chip selects, UART0-UART3, PWM alternatives, and PCMIF. Pinconf tests should cover pull-up/down/disable and supported drive strengths on several DSEL registers.

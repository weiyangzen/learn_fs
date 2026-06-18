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

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

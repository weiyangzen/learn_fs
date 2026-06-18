# sources/distributed-fs/ceph-client/drivers/soc/renesas/pwc-rzv2m.c

## Purpose

`pwc-rzv2m.c` drives the Renesas RZ/V2M PWC block. It exposes two write-only PWC GPIO-like outputs and optionally registers a system power-off handler that requests PWC-managed shutdown.

## Important APIs, Types, and Functions

`struct rzv2m_pwc_priv` stores MMIO base, device, gpio chip, and a software bitmap tracking the two output states because the hardware register cannot be read. GPIO callbacks are `rzv2m_pwc_gpio_set()`, `rzv2m_pwc_gpio_get()`, and `rzv2m_pwc_gpio_direction_output()`. `rzv2m_pwc_poweroff()` writes reset, clock-enable, and power-off registers.

## Control Flow

Probe maps the register resource, clears both output bits using write-enable bits 16 and 17, initializes the cached bitmap, registers the gpiochip, and if `renesas,rzv2m-pwc-power` is present registers a devm power-off handler. Power-off writes reset/clock/power-off bits, delays 150 ms, and reports failure if execution continues.

## State and Persistence Behavior

GPIO output state is cached only in `ch_en_bits`; hardware is write-only from this driver's perspective. Power-off state is hardware-side and expected not to return. No persistent storage is used.

## Dependencies and Integration Points

It depends on platform MMIO, gpiolib, firmware node GPIO discovery, and sys-off registration. Board DT decides whether the power-off handler is active.

## Risks and Edge Cases

Software cache can diverge from hardware if firmware or another agent writes PWC GPIO. `direction_output()` validates `nr > 1`, while gpiolib normally bounds offsets. Parent assignment uses `pdev->dev.parent`, which may affect GPIO device hierarchy. The power-off path cannot verify success except by not returning.

## Test Signals

Test GPIO set/get/direction for both offsets, invalid offset rejection, reset default state on probe, optional power-off registration, and power-off MMIO write sequence on hardware or emulator.

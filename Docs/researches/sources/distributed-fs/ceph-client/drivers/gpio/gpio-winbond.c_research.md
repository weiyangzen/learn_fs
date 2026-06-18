# sources/distributed-fs/ceph-client/drivers/gpio/gpio-winbond.c

## Purpose
Provides GPIO support for Winbond/Nuvoton Super I/O chips, currently W83627UHG/NCT6627UD, using legacy Super I/O extended function mode. GPIO ports are enabled and exposed according to module parameters.

## Important APIs, Types, And Functions
- `struct winbond_gpio_params` stores module-selected base address, enabled ports, output driver modes, and overrides for firmware-owned pins.
- Super I/O helpers `winbond_sio_enter`, `winbond_sio_leave`, `winbond_sio_select_logical`, `winbond_sio_reg_read/write`, and bit helpers manage the index/data port protocol.
- `struct winbond_gpio_info` describes each GPIO port's logical device, enable bit, output mode bit, direction, inversion, data registers, and possible conflicts.
- `winbond_gpio_get_info` maps a flat gpiolib offset to an enabled eight-pin port and applies GPIO2 safety restrictions.
- `winbond_gpio_get`, `winbond_gpio_direction_in`, `winbond_gpio_direction_out`, and `winbond_gpio_set` implement GPIO operations.
- `winbond_gpio_configure`, `winbond_gpio_check_chip`, `winbond_gpio_imatch`, and `winbond_gpio_iprobe` handle ISA probing, chip detection, port configuration, and chip registration.

## Control Flow
The ISA match path validates module masks, probes the configured or default Super I/O base addresses, and checks the chip ID. Probe enters extended mode, configures selected ports, disables ports with fatal conflicts, chooses push-pull/open-drain mode when requested, computes the total exposed line count, and registers one sleepable gpiochip. Each GPIO operation enters Super I/O mode, selects the relevant logical device, reads or writes direction/data/inversion bits, then exits extended mode.

## State And Persistence
Module parameters are global state and determine which hardware ports become visible. Hardware Super I/O registers persist until firmware or another driver changes them. There is no per-line shadow state. The base address is passed to gpiolib as driver data.

## Dependencies And Integration Points
Uses the ISA bus helper, I/O port resource muxing, Super I/O index/data ports at 0x2e or 0x4e, gpiolib, and module parameters for policy. It intentionally protects firmware-owned functions such as Power LED, BEEP, I2C, UARTs, and FDC unless overridden or only warned.

## Risks And Edge Cases
Incorrect module masks can expose or alter pins owned by firmware or serial/FDC/I2C functions. `winbond_gpio_get_info` assumes at least one enabled bit and relies on prior mask cleanup. GPIO2 has special per-pin restrictions that can surprise users with `-EACCES`. Super I/O enter/leave happens on every operation, so balanced release of the muxed region is critical. The module parameter descriptions appear to omit closing parentheses, which is cosmetic but visible.

## Test Signals
Validate chip-ID probing at both default bases, invalid `gpios` bits cleanup, push-pull/open-drain mutual exclusion, conflict disabling for FDC, warn-only UART conflicts, GPIO2 protected pins with and without overrides, inversion-aware get/set, and correct line count when GPIO6 contributes only five pins.

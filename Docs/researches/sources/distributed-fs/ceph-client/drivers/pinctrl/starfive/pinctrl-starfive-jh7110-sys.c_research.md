# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110-sys.c

## Purpose
This file supplies the JH7110 system pinctrl instance. It provides the SYS pin table, function-select and VIN-group sideband programming tables, register layout, IRQ handlers, pad-config ranges, and platform-driver binding for the common JH7110 driver.

## Important APIs, types, and functions
`jh7110_sys_pins[]` lists 64 GPIO pins plus SD0, GMAC1, and QSPI pads. `struct jh7110_func_sel` and `jh7110_sys_func_sel[]` describe per-pin function select bitfields. `struct jh7110_vin_group_sel` and `jh7110_sys_vin_group_sel[]` map VIN-related GPIO groups. `jh7110_sys_set_one_pin_mux()` combines generic GPIO mux writes, function selection, and VIN group selection. `jh7110_sys_get_padcfg_base()` maps pins to one of two pad-config register regions. `jh7110_sys_irq_handler()` dispatches the two 32-bit masked IRQ status registers. `jh7110_sys_pinctrl_info` supplies masks, register bases, saved-register count, callbacks, and pin metadata to the common probe.

## Control flow
The platform driver matches `starfive,jh7110-sys-pinctrl` and delegates probe to `jh7110_pinctrl_probe()`. For each pinmux entry, the common driver decodes pin/din/dout/doen/function and calls `jh7110_sys_set_one_pin_mux()`. If the selected pin is a GPIO and function is 0, `jh7110_set_gpiomux()` updates DOUT/DOEN/GPI selectors. It then writes any defined function-select bitfield if the requested function is within that pin's max. For GPIO pins with function 2, it also writes VIN group selection. IRQ init masks both banks, clears both edge-clear registers, and enables the global GPIO interrupt.

## State and persistence behavior
All mutable state is in common driver allocations and SYS MMIO. The common PM ops save and restore 174 32-bit registers for this instance. Function-select and VIN-group sideband registers are included in that saved range, so suspend/resume should preserve mux state even beyond the common GPIO selector registers.

## Dependencies and integration points
The file depends on JH7110 DT binding pin IDs and mux encoding, the common JH7110 header, and the exported common helper symbols. It integrates with the common gpiochip as a 64-line GPIO controller and with the pinctrl core as a larger pin controller for GPIO, SD0, GMAC1, and QSPI pads.

## Risks
Function-select table entries use fixed offsets, shifts, and `max` values; bad entries silently skip writes or ignore over-range function values, which can make DT pinmux failures hard to diagnose. `jh7110_set_function()` uses a fixed `0x3U` mask even when some entries declare max 3 and shifts are not uniformly spaced; table correctness is critical. Pad configuration is intentionally unavailable for the GMAC1 range between `PAD_GMAC1_MDC` and `PAD_GMAC1_TXC`, so common pinconf may no-op for those pins. VIN group selection is tied to function value 2 and only for tabled GPIO pins.

## Test signals
Tests should cover GPIO mux function 0, alternate function selection for tabled GPIOs, over-range function requests, VIN group setup for function 2, SD0/QSPI padconf ranges, GMAC1 no-padconf behavior, interrupt dispatch across GPIO0-31 and GPIO32-63, and suspend/resume restoring the 174-register window.

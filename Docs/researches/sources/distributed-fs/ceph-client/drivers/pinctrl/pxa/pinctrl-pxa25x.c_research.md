# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa25x.c

## Purpose
Provides the PXA25x-specific pin descriptor table and platform probe wrapper for the common PXA2xx pinctrl implementation.

## Important APIs, Types, And Functions
The file defines `pxa25x_pins[]` using `PXA_GPIO_ONLY_PIN`, `PXA_GPIO_PIN`, `PXA_PINCTRL_PIN`, and `PXA_FUNCTION` macros from `pinctrl-pxa2xx.h`. Runtime code is `pxa25x_pinctrl_probe()`, the OF match table for `marvell,pxa25x-pinctrl`, and a `platform_driver`.

## Control Flow
Probe maps alternate-function, direction, and sleep-state register resources, derives per-bank pointers, then calls `pxa2xx_pinctrl_init()` with the PXA25x table. The common code builds one group per pin and unique function lists from the table.

## State And Persistence
Persistent hardware state is in PXA GPIO alternate-function, direction, and sleep registers. This file contributes static pin/function metadata; allocated pinctrl state is owned by the common driver.

## Dependencies And Integration Points
Depends on platform resources in the order expected by probe and on the common PXA2xx implementation exported from `pinctrl-pxa2xx.c`. It integrates with OF through `marvell,pxa25x-pinctrl`.

## Risks
The table is the source of truth for every PXA25x mux option, so duplicate or incorrect function names change generated function groups. Register pointer arithmetic uses `sizeof(base_af[0])`, the pointer size, as a stride, which assumes the mapped resources are laid out as expected by the original register bank model.

## Test Signals
Probe with a PXA25x DT node, function list/group generation, muxing representative UART/MMC/LCD/PCMCIA pins, GPIO direction changes, and sleep-state pinconf updates are useful signals.

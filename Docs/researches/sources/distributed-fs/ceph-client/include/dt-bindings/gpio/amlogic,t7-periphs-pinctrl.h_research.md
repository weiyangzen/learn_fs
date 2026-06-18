# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/amlogic,t7-periphs-pinctrl.h

## Purpose
Defines Amlogic T7 peripheral GPIO pin numbers for DT pinctrl/GPIO bindings.

## Important APIs, Types, and Constants
Exports banked pin macros such as `GPIOB_*`, `GPIOC_*`, `GPIOD_*`, `GPIOE_*`, `GPIOF_*`, `GPIOG_*`, `GPIOH_*`, and `GPIO_TEST_N`. Values are linear pin indexes from 0 through 156 across the peripheral pin controller.

## Control Flow and State
No runtime flow. GPIO direction, mux, pull, and value state are managed by the Amlogic pinctrl/GPIO driver.

## Dependencies and Integration Points
Self-contained binding included by T7 DTS pinctrl groups and GPIO consumers. It integrates with pin controller nodes that expect these numeric offsets.

## Risks and Test Signals
Bank ordering and pin numbers must match hardware and driver offset tables. Wrong constants can mux or toggle the wrong pin. Test signals include DTS compilation, pinctrl schema validation, and board-level tests for GPIO, pinmux, interrupts, and peripheral pins.

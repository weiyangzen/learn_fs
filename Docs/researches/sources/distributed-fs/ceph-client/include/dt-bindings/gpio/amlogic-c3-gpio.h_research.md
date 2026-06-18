# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/amlogic-c3-gpio.h

## Purpose
Defines Amlogic C3 GPIO pin numbers for DT pinctrl and GPIO consumers.

## Important APIs, Types, and Constants
Exports banked macros `GPIOE_*`, `GPIOB_*`, `GPIOX_*`, `GPIOD_*`, `GPIOA_*`, and `GPIO_TEST_N`, numbered from 0 through 54. The constants are linear offsets into the C3 GPIO controller.

## Control Flow and State
No executable logic. Runtime pin state is controlled by the Amlogic C3 pinctrl/GPIO driver and hardware registers.

## Dependencies and Integration Points
Self-contained header included by Amlogic C3 DTS files for GPIO specifiers, pin mux groups, and interrupt-capable pins.

## Risks and Test Signals
The primary risk is bank/offset mismatch, which can drive the wrong external signal. Test signals include DT schema validation, GPIO line naming/offset checks, and board-level tests for pinmux, GPIO input/output, and interrupts.

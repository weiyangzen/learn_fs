# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xtensa.c

## Purpose
Exposes the Xtensa LX4 GPIO32 optional TIE extension as two gpiolib chips: `impwire` for 32 input-only wires and `expstate` for 32 output-only state bits.

## Important APIs, Types, And Functions
- `enable_cp` and `disable_cp` save/restore interrupt state and CPENABLE access to the Xtensa GPIO32 coprocessor when needed.
- `xtensa_impwire_get_direction` and `xtensa_impwire_get_value` expose input direction and the `read_impwire` instruction.
- `xtensa_expstate_get_direction`, `xtensa_expstate_get_value`, and `xtensa_expstate_set_value` expose output direction, `rur.expstate`, and `wrmsk_expstate`.
- Static `impwire_chip` and `expstate_chip` define the two 32-line gpiochips.
- `xtensa_gpio_init` creates a simple platform device and registers the platform driver.

## Control Flow
At init, the driver registers a synthetic `xtensa-gpio` platform device and then the matching driver. Probe registers the input chip first, then the output chip. Each hardware access temporarily enables the required coprocessor bit, executes the TIE instruction, and restores CPENABLE and interrupts.

## State And Persistence
The driver has no heap-allocated private state and no software shadow. `IMPWIRE` and `EXPSTATE` are CPU/core architectural states. The static chips persist for the module/built-in lifetime.

## Dependencies And Integration Points
Depends on Xtensa architecture support, `asm/coprocessor.h`, compile-time `XCHAL_CP_ID_XTIOP`, platform-device helpers, and gpiolib. The source explicitly notes it is incompatible with SMP because GPIO32 availability and wires can be core-local.

## Risks And Edge Cases
If registering `expstate_chip` fails after `impwire_chip` succeeds, the first chip is not removed. The driver registers a platform device before registering the driver and has no cleanup path for failure after device creation. Static gpiochips and core-local coprocessor state make SMP unsafe. Access depends on correct CPENABLE save/restore under local IRQ disable.

## Test Signals
Build for Xtensa variants with and without `XCHAL_HAVE_CP`, read input bits via `read_impwire`, read/write output bits via `EXPSTATE`, verify direction reporting, inject second-chip registration failure, and confirm the driver is not enabled on SMP configurations.

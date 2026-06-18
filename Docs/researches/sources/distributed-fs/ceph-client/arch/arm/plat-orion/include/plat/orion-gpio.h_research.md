# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/orion-gpio.h

Purpose: Declares Orion-specific GPIO setup and extension APIs beyond standard gpiolib.

Important APIs/macros: `orion_gpio_set_unused()` drives an unused pin low as output, `orion_gpio_set_blink()` toggles hardware blink, `orion_gpio_led_blink_set()` adapts hardware blink to LED class GPIO blink callbacks, `orion_gpio_set_valid()` updates valid input/output masks, and `orion_gpio_init()` registers a GPIO bank and its interrupt wiring. `GPIO_INPUT_OK` and `GPIO_OUTPUT_OK` encode allowed directions.

Control flow/state: Platform code initializes banks first, then MPP setup updates validity. LED and board code can call blink helpers after registration. Hardware and static chip state are owned by `gpio.c`.

Dependencies/integration: Depends on Linux init/types/irqdomain and forward-declared `struct gpio_desc`. Integrates GPIO with MPP and LED subsystems.

Risks/tests: Calling validity or unused-pin helpers before bank registration is a no-op. Callers must pass correct `secondary_irq_base` and parent IRQ array. Tests should cover pin validity, blink state, and IRQ mapping across both supported chips.

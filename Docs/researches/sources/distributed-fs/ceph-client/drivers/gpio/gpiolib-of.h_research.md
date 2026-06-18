# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-of.h

## Purpose
`gpiolib-of.h` is the internal Device Tree GPIO interface. It declares descriptor lookup, gpiochip registration/removal, instance matching, GPIO counting, and lookup-flag translation for OF-backed GPIO controllers and consumers.

## Important APIs, Types, And Functions
With `CONFIG_OF_GPIO`, it declares `of_find_gpio()`, `of_gpiochip_add()`, `of_gpiochip_remove()`, `of_gpiochip_instance_match()`, `of_gpio_count()`, and `of_gpiochip_get_lflags()`. Without OF GPIO, inline stubs return no-op success or not-found values. It also declares `extern struct notifier_block gpio_of_notifier`.

## Control Flow
Generic gpiolib code can call OF hooks unconditionally. Build-time stubs keep non-OF configurations from linking OF implementation code while preserving generic control flow.

## State And Persistence
The header owns no runtime state. The external notifier declaration represents dynamic OF state handled in `gpiolib-of.c` when that support is built.

## Dependencies And Integration Points
It depends on `linux/err.h`, `linux/types.h`, and `linux/notifier.h`, and forward-declares OF, fwnode, GPIO chip, descriptor, and device types. It integrates generic gpiochip and consumer lookup paths with OF-specific implementation.

## Risks
Stub return choices influence fallback behavior in non-OF builds. The unconditional notifier declaration must remain consistent with implementation and build configuration.

## Test Signals
Build-test `CONFIG_OF_GPIO=y` and disabled configurations, and verify generic gpiolib registration and lookup call sites link and behave as expected.

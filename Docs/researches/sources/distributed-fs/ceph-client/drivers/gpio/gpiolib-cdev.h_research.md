# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-cdev.h

## Purpose
`gpiolib-cdev.h` is the internal declaration header for GPIO character device registration and unregistration.

## Important APIs, Types, And Functions
It forward-declares `struct gpio_device` and declares `gpiolib_cdev_register(struct gpio_chip *gc, dev_t devt)` and `gpiolib_cdev_unregister(struct gpio_device *gdev)`. The header includes `linux/types.h` for `dev_t`.

## Control Flow
Generic gpiochip registration code can include this header and call into the cdev implementation without exposing the cdev internals. Registration takes a `gpio_chip` because it initializes cdev state from `gc->gpiodev`; unregistration takes the `gpio_device` that owns the character device.

## State And Persistence
The header owns no state. It defines the boundary for state created in `gpiolib-cdev.c`, including cdev registration and workqueue lifetime.

## Dependencies And Integration Points
It integrates generic gpiolib chip lifecycle code with the userspace character device implementation.

## Risks
Because this header omits a forward declaration for `struct gpio_chip`, it relies on includers already having that type visible. Signature drift would break gpiochip lifecycle integration.

## Test Signals
Build-test gpiochip registration paths with cdev enabled, and verify `/dev/gpiochipN` devices appear and disappear with gpiochip add/remove.

# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib.h

## Purpose
`gpiolib.h` is the private GPIO core header shared by gpiolib implementation files. It defines internal state containers, descriptor flags, helper iteration macros, lookup suffix handling, guard-based SRCU access to chips, logging helpers, and cross-file prototypes for descriptor request/configuration, array I/O, hogging, and line notifications.

## Important APIs, types, and functions
The key types are `struct gpio_device`, `struct gpio_desc`, `struct gpio_array`, `struct gpio_desc_label`, and `struct gpio_chip_guard`. `gpio_device` wraps the driver-core device/cdev, chip pointer, descriptor array, validity masks, SRCU domains, pin ranges, notifier chains, line workqueue, and legacy base. `gpio_desc` carries per-line flags such as requested, output, active-low, open-drain/source, IRQ, hog, pull bias, event clock, and shared-proxy state. Prototypes cover `gpiod_request*()`, `gpiod_free*()`, `gpiod_find_and_request()`, `gpiod_configure_flags()`, `gpiochip_add_hog()`, `gpiochip_get_ngpios()`, and array get/set complex helpers.

## Control flow
The header has no standalone execution, but it shapes core control flow. `DEFINE_CLASS(gpio_chip_guard, ...)` opens the descriptor's GPIO-device SRCU read side and safely dereferences `gdev->chip`, allowing call sites in `gpiolib.c` to abort when a hot-unplugged chip has vanished. `for_each_gpio_property_name()` generates `con_id-gpios`/`con_id-gpio` firmware property names. Descriptor iteration macros let chip registration, debugfs, hog cleanup, and IRQ cleanup scan all lines or lines with a given flag.

## State and persistence behavior
All declared state is in-memory and tied to `struct gpio_device` lifetime. Descriptor labels are RCU/SRCU-freed through `struct gpio_desc_label`. `gpio_array` is co-allocated with `struct gpio_descs` by `gpiod_get_array()` and caches masks for fast same-chip bitmap I/O. There is no persistent storage beyond firmware data consumed by the implementation.

## Dependencies and integration points
The header depends on Linux device, cdev, module, notifier, spinlock, SRCU, workqueue, GPIO consumer/driver, and pinctrl-facing types. It is included by the GPIO cdev/sysfs/OF/ACPI/shared implementation files and provides their private contract with the central gpiolib core.

## Risks and edge cases
Flag bit meanings are ABI-like within the GPIO core; mismatches break cdev notifications, IRQ safety checks, and line configuration. `gpio_device_get_chip()` style access is explicitly unsafe without SRCU, so users should prefer the guard pattern. The property suffix macro uses a caller-provided buffer and depends on the buffer being large enough. `gpio_array` fast-path layout assumes it immediately follows the descriptor pointer array allocated by `gpiod_get_array()`.

## Test signals
Compile coverage across GPIO core variants is essential. Runtime signals include successful hot-unplug without use-after-free, cdev line info matching descriptor flags, array fast path use only for eligible descriptors, correct line-state notifications, hog cleanup, and pinctrl/IRQ helpers observing the same flags as gpiolib core.

# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-shared.c

## Purpose
`gpiolib-shared.c` implements infrastructure for GPIO lines intentionally shared by multiple firmware-described consumers. It scans firmware nodes, identifies shared OF GPIO references, claims the real descriptor, creates auxiliary proxy devices for each consumer, installs machine lookup tables for proxy access, and exposes managed shared descriptors with sleep-aware locking.

## Important APIs, Types, And Functions
Externally used functions are `gpiochip_setup_shared()`, `gpio_device_teardown_shared()`, `gpio_shared_add_proxy_lookup()`, and `devm_gpiod_shared_get()`. Core data structures are `struct gpio_shared_entry`, representing one physical GPIO pin, `struct gpio_shared_ref`, representing one consumer reference, and `struct gpio_shared_desc`, declared in the header for shared descriptor users.

Key internal helpers include `gpio_shared_of_scan()`, `gpio_shared_of_traverse()`, `gpio_shared_find_entry()`, `gpio_shared_make_ref()`, `gpio_shared_setup_reset_proxy()`, `gpio_shared_make_adev()`, `gpio_shared_dev_is_reset_gpio()`, `gpio_shared_remove_adev()`, `gpiod_shared_desc_create()`, `gpio_shared_release()`, `gpio_shared_free_exclusive()`, and teardown helpers.

## Control Flow
At `postcore_initcall`, the code scans the OF tree. It ignores disabled nodes, `__symbols__`, and gpio hogs, then inspects GPIO-like properties (`*-gpios`, `*-gpio`, `gpios`, `gpio`) with two-cell GPIO specifiers. References to the same controller fwnode and offset are grouped into one `gpio_shared_entry`. Entries that are not really shared are discarded.

When a gpiochip registers, `gpiochip_setup_shared()` first detects whether it is itself a proxy chip and marks its only descriptor as `GPIOD_FLAG_SHARED_PROXY`. Otherwise, if the chip matches a shared entry, it translates the OF offset if needed, marks the real descriptor `GPIOD_FLAG_SHARED`, requests it with label `shared` before normal consumers can take it, and creates one auxiliary proxy device per reference.

When a consumer requests a shared GPIO through a proxy path, `gpio_shared_add_proxy_lookup()` matches the consumer fwnode and connection ID, creates a `gpiod_lookup_table` keyed to the proxy device, and registers it. `devm_gpiod_shared_get()` retrieves the shared entry from auxiliary device platform data, creates or reuses a refcounted `gpio_shared_desc`, and installs a devres put action.

## State And Persistence
Global state is `gpio_shared_list` and `gpio_shared_ida`. Each shared entry holds a controller fwnode reference, offset, ref list, mutex, optional shared descriptor, and kref. Each ref owns an auxiliary device, optional lookup table, copied connection ID, optional fwnode ref, and lockdep key. Teardown removes lookup tables, auxiliary devices, descriptor reservations, fwnode refs, IDA IDs, and locks.

## Dependencies And Integration Points
The file depends on OF scanning, auxiliary bus, GPIO machine lookup tables, GPIO descriptor internals, device properties, fwnode refs, reset-gpio special handling, IDA, kref, lockdep, and devres. It integrates with gpiochip registration, auxiliary proxy drivers, reset-gpio, and consumers that need coordinated shared-line access.

## Risks
The scanner currently supports only OF and predominantly two-cell GPIO bindings. Incorrect sharing detection could either reserve a line unnecessarily or allow unsafe concurrent consumers. Lifetime is complex because auxiliary devices, lookup tables, fwnode references, and descriptor reservations must be torn down in the right order. The reset-gpio special case mutates a proxy ref's fwnode after matching, so tests need to cover that path.

## Test Signals
Test OF systems with one, two, and more than two consumers referencing the same GPIO, exclusive single-reference entries being discarded, reset-gpio proxy creation, gpiochip registration before and after scan, proxy lookup table creation, managed shared descriptor refcounting, sleep-capable and atomic locks, gpiochip teardown, and failure injection in auxiliary device or lookup allocation.

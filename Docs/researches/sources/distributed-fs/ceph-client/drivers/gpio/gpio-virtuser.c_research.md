# sources/distributed-fs/ceph-client/drivers/gpio/gpio-virtuser.c

## Purpose
Implements a configurable virtual GPIO consumer module for testing and exercising GPIO providers. It can bind to GPIO descriptors described by firmware or configfs-created software nodes, then exposes per-line and per-array controls through debugfs.

## Important APIs, Types, And Functions
- `struct gpio_virtuser_attr_data`, `gpio_virtuser_line_array_data`, and `gpio_virtuser_line_data` hold debugfs backing data for GPIO arrays and individual lines.
- `struct gpio_virtuser_irq_work_context` bridges debugfs "atomic" operations into hard IRQ work for non-sleeping GPIO APIs.
- Debugfs value/direction/consumer/debounce/interrupt functions expose descriptor operations such as `gpiod_get_array_value_cansleep`, `gpiod_set_value_cansleep`, `gpiod_direction_input`, `gpiod_set_consumer_name`, `gpiod_set_debounce`, `gpiod_to_irq`, and `request_threaded_irq`.
- `gpio_virtuser_probe` discovers GPIO IDs, requests descriptor arrays, and creates the debugfs tree.
- Configfs types `gpio_virtuser_device`, `gpio_virtuser_lookup`, and `gpio_virtuser_lookup_entry` model devices, consumer IDs, and lookup-table entries.
- `gpio_virtuser_device_activate` builds a software node and lookup table, registers a `gpio-virtuser` platform device, waits for probe, and marks it live.

## Control Flow
For firmware-described devices, probe counts IDs from `*-gpios` OF properties or the `gpio-virtuser,ids` property, requests each descriptor array, creates a debugfs directory for the platform device, adds array-level `values` files, and adds per-line files for direction, value, debounce, consumer name, and interrupt counting. For configfs, users create a device group, lookup groups, and lookup-entry groups; attributes configure key, offset, drive, pull, active-low, and transitory flags while the device is offline. Writing `live=1` locks dependent configfs entries, creates a gpiod lookup table and software node, registers a platform device, and relies on normal probe to create the debugfs controls. Writing `live=0` unregisters the platform device and tears down lookup/swnode state.

## State And Persistence
The module holds global ID allocation state in `gpio_virtuser_ida`, a global debugfs root, configfs hierarchy objects, dynamically allocated lookup tables, software nodes, platform device pointers, and per-line debugfs state. IRQ enablement is tracked by `atomic_t irq`; interrupt counts are `atomic_t irq_count`. Debounce and consumer strings are cached in per-line data. State persists only while the module/configfs objects are alive.

## Dependencies And Integration Points
Depends on GPIO consumer APIs, gpiod lookup tables, property/software-node APIs, platform driver binding, configfs, debugfs, IRQ work, threaded IRQs, IDA allocation, and OF property parsing. It is primarily a GPIO test and demonstration consumer rather than a hardware controller.

## Risks And Edge Cases
Debugfs write parsing expects exact lengths for array values and small string buffers. The interrupt disable path calls `free_irq` on the result of `atomic_xchg`; writing `0` before enabling can pass IRQ 0 to `free_irq`. Atomic debugfs paths queue hard IRQ work and wait synchronously, so failures in completion handling would deadlock readers/writers. Configfs live locking must stay balanced on activation failures and deactivation. Lookup-table memory ownership is manual around `dev_id`, table allocation, and `no_free_ptr`.

## Test Signals
Create configfs devices with multiple lookup groups, validate busy errors when editing live objects, activate/deactivate repeatedly, verify software-node IDs drive probe, read/write debugfs scalar and array values in sleepable and atomic modes, change consumer/debounce attributes, request/release IRQ counting, and remove configfs groups while live to confirm deactivation cleanup.

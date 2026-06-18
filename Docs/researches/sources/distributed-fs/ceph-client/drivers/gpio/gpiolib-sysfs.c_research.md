# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-sysfs.c

## Purpose
`gpiolib-sysfs.c` implements the GPIO sysfs interface. It supports chip-level sysfs devices, per-line export/unexport, per-line `direction` and `value` attributes, and, when legacy sysfs is enabled, `/sys/class/gpio/export`, `/sys/class/gpio/unexport`, per-line `edge` polling, `active_low`, and links to exported GPIO class devices.

## Important APIs, Types, And Functions
Exported functions are `gpiod_export()`, `gpiod_export_link()`, `gpiod_unexport()`, `gpiochip_sysfs_register()`, and `gpiochip_sysfs_unregister()`. Core state structures are `struct gpiod_data` for one exported line and `struct gpiodev_data` for one gpiochip sysfs device set.

Important helpers include `direction_show/store()`, `value_show/store()`, `gpio_sysfs_request_irq()`, `gpio_sysfs_free_irq()`, `edge_show/store()`, `gpio_sysfs_set_active_low()`, `active_low_show/store()`, `gpio_is_visible()`, `export_gpio_desc()`, `unexport_gpio_desc()`, `do_chip_export_store()`, `gdev_get_data()`, `gpiod_unexport_unlocked()`, `gpiofind_sysfs_register()`, and `gpiolib_sysfs_init()`.

## Control Flow
At `postcore_initcall`, `gpiolib_sysfs_init()` registers the `gpio` class and scans already-registered gpiochips to create sysfs devices. Later gpiochip registration calls `gpiochip_sysfs_register()` directly. Each chip gets a modern `chipN` class device with `label`, `ngpio`, `export`, and `unexport`; legacy builds also create `gpiochip<base>` and class-wide export/unexport files.

Exporting a descriptor requires the gpio class to exist, the descriptor to be valid and requested, and the `GPIOD_FLAG_EXPORT` bit to be acquired. `gpiod_export()` allocates per-line data, initializes attributes, optionally creates a legacy `gpioN` class device, adds a per-chip `gpio<offset>` attribute group, and records the exported line under `gpiodev_data`. `gpiod_unexport()` removes the same state under `sysfs_lock`.

Legacy edge support configures an IRQ for polling the `value` file. `edge_store()` maps string triggers to flags, frees old IRQ state, requests a new IRQ when needed, and emits line state notifications. `active_low_store()` flips descriptor polarity and reconfigures single-edge IRQs so poll semantics remain logical.

## State And Persistence
`sysfs_lock` serializes export/unexport and unregister. Per-line state stores the descriptor, device, attribute objects, parent kobject, direction permission, optional kernfs node, IRQ number, and IRQ flags. Per-chip state stores exported line list and sysfs devices. Descriptor flags track export, sysfs ownership, active-low, and edge bits. All state is removed when lines are unexported or gpiochips unregister.

## Dependencies And Integration Points
The file depends on sysfs/class device APIs, kernfs notification, GPIO descriptor and chip APIs, IRQ APIs, SRCU/chip guards, kstrtox, and UAPI GPIO naming. It integrates with cdev line-state notifications through `gpiod_line_state_notify()` and with legacy userspace that still relies on `/sys/class/gpio`.

## Risks
Sysfs GPIO is legacy and has broad compatibility constraints. Risks include races between edge reconfiguration and device deregistration, stale exported-line state during gpiochip unregister, active-low changes while an IRQ is active, and ensuring `GPIOD_FLAG_EXPORT`/`GPIOD_FLAG_SYSFS` are cleared in all error paths. Legacy global GPIO numbers depend on stable bases, while modern chip devices use gpio device IDs and offsets.

## Test Signals
Test early gpiochip registration before class init, chip add/remove after class init, per-chip export/unexport by offset, legacy global export/unexport by GPIO number, direction/value reads and writes, hidden direction when not changeable, edge polling and sysfs notifications, active_low IRQ reconfiguration, export error cleanup, `gpiod_export_link()`, and gpiochip unregister with exported sysfs-owned lines.

# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-core.h

Purpose: core data structures and helper macros for Samsung legacy gpiolib.

Important APIs/types/functions: defines `struct samsung_gpio_chip`, `struct samsung_gpio_cfg`, PM helper types, locking helpers, `to_samsung_gpio()`, and chip lookup/tracking interfaces.

Control flow: no standalone flow; implementation in `gpio-samsung.c` and PM GPIO code uses these structures.

State and persistence: chip structures hold MMIO base, gpio_chip, lock, config callbacks, IRQ base, PM hooks, and interrupt bitmap.

Dependencies and integration points: bridges Linux gpiolib, Samsung config/pull APIs, and platform-specific GPIO bank arrays.

Risks: lock and base offset semantics differ across bank styles; bad structure initialization breaks all GPIO access for a bank.

Test signals: gpiochip registration, get/set/direction, config/pull operations, PM save/restore, and chip lookup.

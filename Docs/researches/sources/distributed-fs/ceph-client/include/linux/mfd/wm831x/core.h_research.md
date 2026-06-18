# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/core.h

## Purpose
`wm831x/core.h` is the main WM831x/WM832x MFD core contract. It defines parent IDs, a large shared register map, selected bitfields, parent state, IRQ helper, device I/O APIs, initialization/suspend/shutdown hooks, regmap config, and OF matching.

## Important APIs, Types, and Functions
Register constants span reset/revision/security, system control, interrupts, GPIO levels, RTC, watchdog, OTP/security key, DC/DC and LDO regulators, charger/status LEDs/current sinks, clock/FLL, unique IDs, and OTP controls. Bitfields include chip/revision IDs, ON-pin control, clock output, XTAL/FLL, and FLL tuning. `enum wm831x_parent` identifies WM8310/11/12/20/21/25/26. `struct wm831x` stores I/O lock, device, regmap, platform data, type, IRQ domain/masks, revision flags, GPIO state caches, AUXADC queue/active state, security key lock, and locked state. APIs include register read/write/lock/unlock/set-bits/bulk-read, device init/suspend/shutdown, IRQ init/exit, AUXADC init, and `wm831x_irq()`.

## Control Flow
Bus frontends instantiate regmap and call `wm831x_device_init()`, which identifies the chip, configures IRQs, initializes children, and records revision flags. Register writes to protected areas are mediated by `wm831x_reg_unlock()`/`wm831x_reg_lock()`. IRQ code maps chip IRQs through an IRQ domain and caches mask values.

## State and Persistence Behavior
Hardware persists regulator, charger, RTC, watchdog, GPIO, clock/FLL, interrupt, OTP, and security state. Software tracks IRQ masks/cache, GPIO pending updates/levels, AUXADC pending/active conversions, soft-shutdown flag, revision capability flags, and security-key lock state.

## Dependencies and Integration Points
The header depends on regmap, IRQ domains, mutexes, regulator and platform data declarations, OF match tables, and AUXADC declarations. It integrates with regulator, RTC, watchdog, GPIO, charger, LED, clock/FLL, AUXADC, IRQ, poweroff/shutdown, and device-tree matching.

## Risks and Test Signals
Risks include protected-register writes without lock sequencing, stale IRQ mask caches, revision flag misuse (`has_gpio_ena`, `has_cs_sts`, charger wake), AUXADC queue races, and broad register-map constants drifting from volatile/readable tables. Test signals are regmap read/write and lock tests, IRQ mask cache synchronization tests, GPIO update flush tests, AUXADC queue tests, device init per parent ID, suspend/shutdown tests, and regulator/RTC/watchdog child probe smoke tests.

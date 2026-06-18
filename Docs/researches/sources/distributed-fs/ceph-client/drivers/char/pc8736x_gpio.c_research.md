# sources/distributed-fs/ceph-client/drivers/char/pc8736x_gpio.c

## Purpose
`pc8736x_gpio.c` implements a character-device GPIO interface for National Semiconductor/Winbond PC87365/PC87366 Super I/O GPIO pins. It provides 32 pin minors, uses the shared `nsc_gpio` read/write command parser, and implements Super I/O configuration and runtime port operations.

## Important APIs, Types, and Functions
- Super I/O helpers `superio_outb()`, `superio_inb()`, `pc8736x_superio_present()`, `device_select()`, and `select_pin()` access config registers at `0x2e` or `0x4e`.
- `pc8736x_gpio_configure_fn()` serializes pin config writes under `pc8736x_gpio_config_lock`.
- `pc8736x_gpio_get()`, `pc8736x_gpio_set()`, `pc8736x_gpio_current()`, and `pc8736x_gpio_change()` implement `struct nsc_gpio_ops`.
- `pc8736x_gpio_open()` validates minor `< PC8736X_GPIO_CT` and installs ops in `file->private_data`.
- `pc8736x_gpio_init()` creates a platform device, validates chip ID and enabled GPIO unit, reserves the runtime I/O range, allocates/registers the char region, initializes output shadow state, and adds one `cdev` for 32 minors.

## Control Flow
Init probes both Super I/O command bases for supported IDs, checks the global chip-enable bit and GPIO logical device activation, reads the GPIO runtime base from config space, reserves 16 I/O ports, and exposes all pin minors under a dynamic or configured major. Reads/writes enter `nsc_gpio_read()`/`nsc_gpio_write()`, which call this driver's pin operations.

## State and Persistence
Hardware configuration and GPIO levels can persist depending on the Super I/O and board. Software state includes `pc8736x_gpio_base`, `pc8736x_gpio_shadow[4]`, selected Super I/O command base/device, major number, cdev, and platform device. The shadow array tracks last readback/output state for `gpio_current()` toggling.

## Dependencies and Integration Points
The driver depends on x86-style I/O ports, Super I/O PC8736x register layout, shared `nsc_gpio` helpers, cdev registration, platform-device logging, and `request_region()` ownership.

## Risks
- Super I/O config access is global and only partially protected; `selected_device` is not itself a lock.
- Runtime GPIO set/read operations are not locked against each other, and shadow state may race.
- The user command interface can reconfigure pins without capability checks.
- Init trusts BIOS-enabled GPIO unit and takes minimal activation action.

## Test Signals
Tests should verify probe failure on absent/disabled chips, I/O region conflict handling, minor bounds, shared `nsc_gpio` command effects, shadow initialization from output ports, and cleanup releasing cdev, chrdev region, I/O region, and platform device.

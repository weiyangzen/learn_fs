
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-cgbc.c

Purpose: exposes 14 GPIO lines controlled through the Congatec Board Controller MFD command interface.

Important APIs/types/functions: `struct cgbc_gpio_data` contains the gpiochip, parent `struct cgbc_device_data`, and mutex. Important routines are `cgbc_gpio_cmd()`, `cgbc_gpio_get()`, `__cgbc_gpio_set()`, `cgbc_gpio_set()`, `cgbc_gpio_direction_set()`, `cgbc_gpio_direction_input()`, `cgbc_gpio_direction_output()`, `cgbc_gpio_get_direction()`, and `cgbc_gpio_probe()`.

Control flow: probe gets the MFD parent driver data, allocates state, initializes the mutex, fills gpiochip callbacks, and registers 14 sleeping GPIOs. Every operation sends a three-byte board-controller command and receives a one-byte result. Offsets 0-7 and 8-13 are addressed as separate command banks. Output direction first sets the desired output value, then changes direction.

State and persistence behavior: there is no value cache; state persists inside the board controller. The mutex serializes command sequences, especially read-modify-write set and direction operations. The driver marks no explicit suspend/resume state.

Dependencies and integration points: depends on the `linux/mfd/cgbc.h` command API, platform MFD child registration, gpiolib, and mutex cleanup through devm. It is a can-sleep controller because all operations cross the controller command transport.

Risks: command failure returns directly to GPIO callers. Read-modify-write behavior can race with other firmware/controller clients outside this driver. Direction bit semantics must remain aligned with board-controller firmware. There is no IRQ support.

Test signals: probe as `cgbc-gpio`, value get/set across both banks, direction transitions with set-before-output ordering, concurrent GPIO operations serialized by lock, and command-error propagation from mocked or real `cgbc_command()`.


# sources/distributed-fs/ceph-client/drivers/gpio/gpio-en7523.c

Purpose: implements the Airoha EN7523 GPIO controller using generic GPIO data access plus custom direction/output-enable registers.

Important APIs/types/functions: `struct airoha_gpio_ctrl` stores a generic chip, data register, two direction registers, and output-enable register. Key functions are `airoha_dir_set()`, `airoha_dir_out()`, `airoha_dir_in()`, `airoha_get_dir()`, and `airoha_gpio_probe()`.

Control flow: probe maps four resources, initializes a 32-line generic GPIO chip using the data register, then overrides direction callbacks. Direction uses one bit per pin in an output-enable register and one direction bit every two bits in two 16-pin direction registers. Output direction writes the direction register, writes the requested output value through generic-chip set, then updates output enable.

State and persistence behavior: hardware registers hold all state. There is no lock around direction/output register read-modify-write, no IRQ support, and no PM context. Generic-chip handles basic data reads/writes.

Dependencies and integration points: depends on platform MMIO resources, OF compatible `airoha,en7523-gpio`, gpiolib generic helpers, and device-managed registration.

Risks: direction read-modify-write is unlocked and could race with concurrent GPIO operations. Resource order is part of the ABI. The two-bit direction spacing is hardware-specific and easy to misconfigure if offsets change.

Test signals: probe resource ordering, 32-line exposure, direction transitions across lower and upper 16-pin banks, output-enable bit updates, generic value get/set, and concurrent direction stress testing.

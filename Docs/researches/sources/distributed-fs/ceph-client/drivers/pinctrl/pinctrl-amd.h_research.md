# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amd.h

Purpose: Supplies the AMD GPIO driver's register layout, bit definitions, runtime state structures, pin descriptors, group descriptors, and optional IOMUX function table. It is a data-heavy companion to `pinctrl-amd.c`.

Important APIs and types: Defines register offsets such as `WAKE_INT_MASTER_REG`, `WAKE_INT_STATUS_REG0/1`, debounce, interrupt, wake, pull, output, and drive-strength bit offsets/masks. `struct amd_gpio` stores the driver's lock, GPIO and IOMUX MMIO bases, pinctrl/gpio objects, group table, saved registers, platform device, and IRQ. `struct amd_function` describes IOMUX function names, four selectable groups, group count, and register index. Static tables include `kerncz_pins[]`, `kerncz_groups[]`, and `pmx_functions[]`.

Control flow: No executable logic is defined, but macros generate large sets of one-pin groups named `IMX_F{0..3}_GPIO<n>` and functions named `iomux_gpio_<n>`. Runtime code indexes these arrays in `amd_get_groups_count()`, `amd_set_mux()`, and pinctrl descriptor registration.

State and persistence: The header itself is immutable data. Its bit definitions determine which hardware register fields are read, saved, restored, or modified by the driver. `saved_regs` is declared in `struct amd_gpio` but allocated and maintained in the C file.

Dependencies and integration points: Depends on pinctrl generic descriptors and `struct pingroup`. It encodes the Kerncz-era AMD GPIO numbering where GPIO 63 is absent, GPIOs 0-62 and 64-183 are described, and extra groups exist for I2C and UART functions.

Risks: The table data is a contract with hardware. Incorrect bit offsets can break IRQ, wake, debounce, and GPIO output behavior across the whole driver. The group enum and generated group table must remain aligned; gaps such as missing GPIO63 must be reflected consistently in pins, groups, and functions. `NSELECTS` assumes exactly four IOMUX choices per GPIO.

Test signals: Compile-time array alignment, successful pinctrl registration with the expected pin and group counts, debugfs group enumeration, IOMUX selection readback for valid GPIOs, and suspend register save/restore across all described pin numbers validate this header.

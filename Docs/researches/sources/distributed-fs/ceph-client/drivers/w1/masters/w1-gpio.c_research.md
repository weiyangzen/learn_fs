# sources/distributed-fs/ceph-client/drivers/w1/masters/w1-gpio.c

## Purpose
GPIO-backed 1-Wire master driver. It adapts one data GPIO, plus an optional external pullup-enable GPIO, into the generic `struct w1_bus_master` callback interface used by the W1 core.

## Important APIs, Types, and Functions
`struct w1_gpio_ddata` stores the line GPIO, optional pullup GPIO, and pending pullup duration. `w1_gpio_probe()` allocates driver data and `struct w1_bus_master`, requests GPIO descriptors, installs `read_bit`, `write_bit`, and sometimes `set_pullup`, then calls `w1_add_master_device()`. `w1_gpio_remove()` disables the optional pullup GPIO and unregisters the master. `w1_gpio_set_pullup()` implements the W1 strong pullup contract for GPIO open-drain emulation.

## Control Flow
Probe defaults to `GPIOD_OUT_LOW_OPEN_DRAIN`; the `linux,open-drain` property means external hardware already provides open-drain behavior, so the descriptor is requested as normal output. After registration, the optional pullup GPIO is driven high. Bit reads and writes are direct descriptor operations. Strong pullup is staged by the W1 core: nonzero delay records duration; a zero call forces the data line high with `gpiod_set_raw_value()`, sleeps, then restores open-drain input/high behavior.

## State and Persistence
State is entirely runtime driver data and GPIO line state. There is no persistent storage. `pullup_duration` is a one-shot timing request consumed by the W1 core's post-write path.

## Dependencies and Integration Points
Depends on gpiolib, platform device probing, device properties, OF compatible `w1-gpio`, and the W1 core exported `w1_add_master_device()` and `w1_remove_master_device()`. It integrates below all W1 slave drivers as a bus provider.

## Risks and Test Signals
The `linux,open-drain` property must match board wiring; an incorrect setting can actively drive a shared bus. Strong pullup relies on raw GPIO override and `msleep()`, so timing and electrical behavior should be validated with parasite-powered devices. Test signals are successful master registration, slave discovery through the core, sysfs master presence, pullup GPIO level on probe/remove, and stable reads/writes under thermal or EEPROM conversion workloads.

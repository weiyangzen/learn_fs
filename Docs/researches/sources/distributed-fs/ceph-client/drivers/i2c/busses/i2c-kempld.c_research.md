# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-kempld.c

Purpose: implements the Kontron KEM PLD I2C bus driver. It is a polling state-machine adapter built on the parent KEMPLD MFD register access and mutex, with optional GPIO I2C muxing, configurable bus frequency, 10-bit address support, suspend/resume handling, and preservation of pre-existing controller enable state.

Important APIs, types, and functions: `struct kempld_i2c_data` stores device, parent PLD data, adapter, current message pointer, buffer position, remaining message count, state, and `was_active`. `kempld_i2c_process()` is the central state machine. `kempld_i2c_xfer()` repeatedly calls it under the parent mutex until done or timeout. `kempld_i2c_device_init()` programs prescaler, mux config, interrupt acknowledgement, and controller enable.

Control flow: probe captures whether the controller was already enabled, initializes hardware under the PLD mutex, registers a numbered adapter using module parameter `i2c_bus` if set, and reports the selected frequency. Transfers initialize state to `STATE_INIT` and poll until the bus is free, address bytes are sent, data bytes are written/read, repeated messages are handled, STOP is emitted, or errors occur. Suspend disables the controller; resume re-runs device init.

State and persistence: software transfer state is stored in `msg`, `pos`, `nmsgs`, and `state`. Persistent configuration comes from module parameters `bus_frequency`, `i2c_bus`, and `i2c_gpio_mux`. Remove disables the controller only if it was not active before probe. Hardware prescaler and GPIO mux bits persist in the PLD until changed.

Dependencies and integration points: depends on the KEMPLD MFD APIs `kempld_read8`, `kempld_write8`, `kempld_get_mutex`, and `kempld_release_mutex`, ACPI companion propagation, platform device registration, and I2C core functionality flags including 10-bit addressing and SMBus emulation.

Risks: all register accesses require the parent mutex; missing that contract can race other KEMPLD functions. `I2C_STAT_TIP` and busy states use polling with one-second timeout. NACK during address/data transitions sends STOP and returns `-ENXIO`; arbitration lost returns `-EAGAIN`. Prescaler formulas differ by PLD spec major and clamp negative values to zero. `I2C_M_NOSTART` message handling reuses the current state and must preserve `pos` correctly.

Test signals: standard and 10-bit addressing, read/write multi-message transfers with and without `I2C_M_NOSTART`, arbitration loss, NACK, stuck busy timeout, bus-frequency clamping and prescaler values for spec major 1 and later, GPIO mux module parameter, suspend/resume reinitialization, and remove behavior when hardware was pre-enabled.

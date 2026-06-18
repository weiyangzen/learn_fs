# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-gpio.c

Purpose: GPIO-controlled I2C multiplexer driver. It maps mux channel IDs to GPIO bit patterns and creates child adapters for each channel.

Important APIs/types: `struct gpiomux` embeds platform data, GPIO count, and descriptor array. Core callbacks are `i2c_mux_gpio_select()` and optional `i2c_mux_gpio_deselect()`. Firmware parsing fills `struct i2c_mux_gpio_platform_data`.

Control flow: probe obtains platform data or parses OF/ACPI firmware for parent adapter, child `reg` values, `idle-state`, and `settle-time-us`. It gets the parent adapter, allocates an I2C mux core, determines whether mux locking is needed by comparing GPIO-controller roots with the I2C root, requests mux GPIOs at the initial idle or first-channel state, and adds one adapter per value. Select writes all GPIOs with `gpiod_set_array_value_cansleep()` and optionally waits; deselect drives the idle state.

State and persistence: GPIO output state represents the selected or idle channel. Mux data stores channel values, parent adapter reference, settle time, and child adapters.

Dependencies and integration: depends on gpiolib, OF/ACPI firmware parsing, platform data compatibility, and I2C mux core.

Risks: incorrect initial state can select an unintended downstream bus during probe. Locking decision depends on root adapter detection for GPIO providers. Firmware child count and `reg` properties must match hardware. No-idle mode leaves last channel selected.

Test signals: GPIO bit patterns for each channel, idle disconnect behavior, settle delay, platform-data and firmware probe paths, mux-locked logging, and partial adapter-add cleanup.

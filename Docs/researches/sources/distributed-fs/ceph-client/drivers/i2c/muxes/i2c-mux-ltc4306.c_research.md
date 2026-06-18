# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-ltc4306.c

Purpose: I2C mux/switch driver for Analog Devices/Linear Technology LTC4305 and LTC4306 devices, including optional GPIO support on LTC4306.

Important APIs/types: `enum ltc_type`, `struct chip_desc`, and `struct ltc4306` describe channel count, GPIO count, regmap, and gpiochip. Registers include status, config, mode, and switch. Mux callbacks are `ltc4306_select_mux()` and `ltc4306_deselect_mux()`.

Control flow: probe selects chip data from OF or ID table, checks idle-disconnect property, allocates an `I2C_MUX_LOCKED` mux core, initializes regmap, toggles optional enable GPIO, writes the switch register to verify presence/disconnect channels, configures upstream/downstream accelerators, registers GPIOs if present, and creates adapters for every channel. Select sets the switch mask bit for the chosen channel; deselect clears it when idle disconnect is enabled.

State and persistence: regmap cache and hardware registers hold accelerator, GPIO mode/config, and selected switch state. Child adapters persist until remove. Optional GPIO directions/values are visible through gpiolib.

Dependencies and integration: depends on regmap-I2C, gpiolib, device properties, I2C mux core, and OF/ID matching.

Risks: register bit numbering maps channel to `BIT(7 - chan)`, so channel-count changes need care. Probe uses register writes as presence tests. GPIO mode register is reset to all-inputs during init. Idle disconnect controls whether downstream channels remain connected between transfers.

Test signals: LTC4305 two-channel and LTC4306 four-channel probes, enable GPIO sequencing, accelerator properties, GPIO get/set/direction/config, idle disconnect, and regmap error paths.

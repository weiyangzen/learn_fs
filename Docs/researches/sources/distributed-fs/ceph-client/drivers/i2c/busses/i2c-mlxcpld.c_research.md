# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mlxcpld.c

Purpose: Mellanox CPLD LPC-I2C bridge driver. It exposes a numbered I2C adapter backed by CPLD LPC registers, with optional extended transfer sizes, SMBus block support, and platform-data controlled bus frequency.

Important APIs/types: `struct mlxcpld_i2c_priv` stores adapter, LPC base address, mutex, current transfer descriptor, device, SMBus-block capability, and polling interval. `struct mlxcpld_i2c_curr_xfer` tracks command direction, address width, data length, message count, and message pointer. Main functions are `mlxcpld_i2c_xfer()`, `mlxcpld_i2c_wait_for_free()`, `mlxcpld_i2c_wait_for_tc()`, `mlxcpld_i2c_xfer_msg()`, `mlxcpld_i2c_set_frequency()`, and `mlxcpld_i2c_probe()`.

Control flow: probe initializes the private object, optionally reads platform regmap data to set 100/400/1000 kHz timing, reads the CPLD capability register, selects adapter quirks for normal or extended data windows, enables SMBus block mode if advertised, and adds a numbered adapter. A transfer validates message count, buffers, 7-bit address equality, and combined length, waits for the bridge to be free, soft-resets on stuck busy, records transfer layout, writes data/address counts and payload bytes into the LPC data window, starts by writing the command register, polls status until ACK/NACK/timeout, then copies read data back.

State and persistence: adapter state is per platform device. Transfer state is stored in `priv->xfer` under `priv->lock`. Hardware state persists in CPLD timing/capability/status registers. There is no suspend/resume handling; remove deletes the adapter and destroys the mutex.

Dependencies and integration: depends on LPC `inb/inw/inl` and `outb/outw/outl`, Linux I2C core quirks, platform data from `mlxreg_core_hotplug_platform_data`, and regmap for frequency configuration. It integrates with Mellanox platform code through completion notification after adapter registration.

Risks: LPC bulk helpers cast byte buffers to `u16`/`u32`, so alignment and endian assumptions matter. `comm_len` is an 8-bit sum and relies on adapter quirks to bound message lengths. Polling is the only completion mechanism despite comments mentioning interrupts. Reset only toggles a control bit and may not recover severe bridge faults. The adapter template is static and copied per instance, so probe must fully overwrite instance-specific fields.

Test signals: test normal and extended capability values, SMBus block reads with valid and invalid returned lengths, write-then-read combined messages with address widths up to 4 bytes, busy reset recovery, NACK mapping to `-ENXIO`, frequency platform data, and numbered adapter notification.

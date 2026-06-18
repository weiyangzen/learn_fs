# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-mlxcpld.c

Purpose: Mellanox CPLD-based I2C mux driver using platform data supplied by a parent I2C CPLD client.

Important APIs/types: `struct mlxcpld_mux` stores cached `last_val`, parent I2C client, and `struct mlxcpld_mux_plat_data`. Key callbacks are `mlxcpld_mux_select_chan()` and `mlxcpld_mux_deselect()`.

Control flow: probe requires platform data, chooses SMBus byte-data or raw I2C functionality based on 1-byte or 2-byte register addressing, allocates a mux core, copies platform data, initializes `last_val`, and adds adapters for each platform channel ID. Register writes use `__i2c_smbus_xfer()` for 1-byte register addresses or `__i2c_transfer()` for 2-byte addresses to avoid recursive adapter locking. Select writes the new channel only when it differs from `last_val`; deselect writes zero and clears the cache.

State and persistence: CPLD mux register holds selected channel. `last_val` caches software state to skip redundant writes. Platform data also carries completion notification state for board code.

Dependencies and integration: depends on parent being an I2C client, Mellanox platform data, I2C mux core, and adapter functionality bits.

Risks: platform-data-only design limits firmware self-description. Cached `last_val` can become stale if firmware or another agent changes the CPLD. Register size validation is strict. Completion callback receives adapter pointers after registration and must not outlive them.

Test signals: both register-size modes, functionality rejection, channel cache behavior, deselect writes, completion notification, and partial channel registration cleanup.

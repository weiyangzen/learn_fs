<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i3c.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i3c.c

Purpose: Adds basic regmap transport support for I3C devices using SDR transfers.

Important APIs/types/functions: `regmap_i3c_write()` issues one outbound `struct i3c_xfer`; `regmap_i3c_read()` issues a write register phase followed by a read phase; `regmap_i3c` is the bus definition. `__regmap_init_i3c()` and `__devm_regmap_init_i3c()` are exported wrappers.

Control flow: The write path wraps the whole formatted regmap buffer as one I3C write transfer. The read path builds two transfers: register bytes out, value bytes in. Both call `i3c_device_do_xfers(..., I3C_SDR)` and return its status directly. Initialization passes `&i3c->dev` as both device and bus context.

State and persistence behavior: The file owns no persistent state or allocations. Transfer state is stack-local per operation.

Dependencies and integration points: Depends on I3C device/master APIs and the regmap core. It integrates where I3C client drivers want the same register formatting, caching, and locking services as I2C/SPI regmap users.

Risks: Only SDR mode is used. The transport does not advertise endian defaults, async I/O, gather write, or raw size caps, leaving those to regmap defaults and controller behavior. Any device requiring dynamic address handling or private transfer modes needs logic outside this adapter.

Test signals: Confirm a formatted register write transfer is produced, a read produces exactly two SDR transfers, errors propagate, and managed/unmanaged initialization uses the correct device context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i3c.c -->

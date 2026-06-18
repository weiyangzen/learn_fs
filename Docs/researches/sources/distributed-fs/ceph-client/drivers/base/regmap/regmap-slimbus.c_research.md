<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-slimbus.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-slimbus.c

Purpose: Implements regmap transport for SLIMbus devices with 16-bit register addresses and 8-bit values.

Important APIs/types/functions: `regmap_slimbus_write()` and `regmap_slimbus_read()` call `slim_write()` and `slim_read()`. `regmap_get_slimbus()` selects the bus. `__regmap_init_slimbus()` and `__devm_regmap_init_slimbus()` export initialization.

Control flow: Bus selection accepts only `val_bits == 8` and `reg_bits == 16`. Write interprets the first two bytes of the formatted data as the address and writes the rest of the payload. Read interprets the two-byte register buffer and reads `val_size` bytes. Both use little-endian regmap defaults.

State and persistence behavior: No private state or allocations are owned. The SLIMbus device and hardware retain all external state.

Dependencies and integration points: Depends on SLIMbus APIs and regmap core. It allows SLIMbus client drivers to use standard regmap caching and formatting.

Risks: No explicit `reg_size` or `count` validation is performed in callbacks; the core must supply correctly formatted buffers. Only one address/value format is supported. Endianness relies on the host interpretation of `*(u16 *)`.

Test signals: Validate format rejection, address decode passed to `slim_read/write`, payload length as `count - 2`, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-slimbus.c -->

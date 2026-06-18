<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-fsi.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-fsi.c

Purpose: Provides regmap bus support for FSI slave devices, selecting byte, 16-bit, or 32-bit accessors and endian conversions from `regmap_config`.

Important APIs/types/functions: Defines `regmap_fsi8`, `regmap_fsi16`, `regmap_fsi16le`, `regmap_fsi32`, and `regmap_fsi32le` `struct regmap_bus` instances. `regmap_get_fsi_bus()` selects the bus. Exported wrappers `__regmap_init_fsi()` and `__devm_regmap_init_fsi()` call the regmap core with `fsi_dev->slave` as bus context.

Control flow: Bus selection accepts register widths of 8, 16, or 32 bits and value widths of 8, 16, or 32 bits. For 16/32-bit values it consults `regmap_get_val_endian()` and maps little/native or big/default/native to the matching accessor. Read callbacks issue `fsi_slave_read()`, convert if needed, and return an unsigned value. Write callbacks validate 8/16-bit value bounds where truncation is possible, convert if needed, then call `fsi_slave_write()`.

State and persistence behavior: The adapter owns no heap state and stores no persistent state beyond the regmap created by the core. FSI slave state remains in the underlying FSI subsystem and hardware.

Dependencies and integration points: Depends on `<linux/fsi.h>`, regmap core, endian helpers, and `struct fsi_device`. Integrates with FSI slave read/write APIs and the standard managed/unmanaged regmap initialization pattern.

Risks: Unsupported endian combinations return `-EOPNOTSUPP`; drivers must provide compatible `reg_bits`, `val_bits`, and endian settings. Native endian branches are compile-time dependent. 32-bit non-LE path uses host-order `u32`, while little-endian-selected path explicitly stores big-endian typed temporaries to match FSI byte ordering expectations.

Test signals: Useful tests would instantiate all supported value sizes and endianness settings, verify unsupported configurations fail, and check 8/16-bit writes reject out-of-range values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-fsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mdio.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mdio.c

Purpose: Provides regmap support for MDIO devices using Clause 22 and Clause 45 register access.

Important APIs/types/functions: `regmap_mdio_c22_read/write()` and `regmap_mdio_c45_read/write()` implement bus callbacks. `regmap_mdio_c22_bus` and `regmap_mdio_c45_bus` are selected by `__regmap_init_mdio()` and `__devm_regmap_init_mdio()`.

Control flow: Clause 22 is selected for `reg_bits == 5` and `val_bits == 16`; reads validate the register fits five bits, call `mdiodev_read()`, mask to 16 bits, and return. Clause 45 is selected for `reg_bits == 21`; the encoded register is split into device address and 16-bit register number, then `mdiodev_c45_read/write()` is used. Unsupported configurations return `-EOPNOTSUPP`.

State and persistence behavior: No internal state or allocation is owned by this adapter. It delegates persistence entirely to the MDIO device and regmap core.

Dependencies and integration points: Depends on MDIO helpers, bit masks, regmap core, and the `REGMAP_MDIO_C45_*` encoding contract exposed by regmap headers.

Risks: Out-of-range registers return `-ENXIO`. Clause 45 callers must encode device address and register number correctly. Value writes are not range-checked beyond the underlying MDIO API, so callers should use 16-bit regmap value widths.

Test signals: Validate Clause 22 and 45 selection, register mask rejection, value masking on reads, C45 devad/regnum split, and managed/unmanaged init failure on unsupported config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mdio.c -->

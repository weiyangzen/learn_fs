# sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9.h

Purpose: small shared header for KXSD9 transport drivers. It declares the common probe/remove entry points and exported runtime PM operations implemented by `kxsd9.c`.

Important APIs/types/functions: `kxsd9_common_probe(struct device *dev, struct regmap *map, const char *name)`, `kxsd9_common_remove(struct device *dev)`, and `extern const struct dev_pm_ops kxsd9_dev_pm_ops`. `KXSD9_STATE_RX_SIZE` and `KXSD9_STATE_TX_SIZE` are defined but unused by the listed SPI/common files.

Control flow: SPI and I2C wrappers include this header, initialize a bus-specific regmap, and delegate common IIO registration and teardown to these declarations.

State and persistence: no state is defined here; private state is intentionally hidden inside `kxsd9.c`.

Dependencies and integration points: includes Linux `device` and `kernel` headers but relies on an external declaration of `struct regmap`; the included source files already include regmap before this header.

Risks: because `struct regmap` is not forward-declared in this header, standalone include hygiene depends on prior includes. The unused RX/TX size macros may be legacy residue and should not be treated as current transport contract without checking users.

Test signals: all KXSD9 transport modules compile with namespace imports and PM ops linkage.

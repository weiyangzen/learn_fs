# sources/distributed-fs/ceph-client/drivers/base/regmap/Kconfig

## Purpose
This Kconfig file declares the build symbols for generic regmap support, regmap KUnit/build helpers, and transport-specific regmap backends.

## Important APIs, Types, And Functions
Key symbols are `REGMAP`, `REGMAP_KUNIT`, `REGMAP_BUILD`, `REGMAP_AC97`, `REGMAP_I2C`, `REGMAP_SLIMBUS`, `REGMAP_SPI`, `REGMAP_SPMI`, `REGMAP_W1`, `REGMAP_MDIO`, `REGMAP_MMIO`, `REGMAP_IRQ`, `REGMAP_RAM`, `REGMAP_SOUNDWIRE`, `REGMAP_SOUNDWIRE_MBQ`, `REGMAP_SCCB`, `REGMAP_I3C`, `REGMAP_SPI_AVMM`, and `REGMAP_FSI`.

## Control Flow And State
`REGMAP` is a hidden bool that defaults to enabled when any transport or IRQ regmap user is selected. Transport symbols are mostly tristates with dependency constraints on their bus subsystems. `REGMAP_IRQ` selects `IRQ_DOMAIN`; `REGMAP_KUNIT` depends on `KUNIT && REGMAP`, defaults with `KUNIT_ALL_TESTS`, and selects `REGMAP_RAM`. `REGMAP_BUILD` exists to force core regmap availability for tests without a concrete transport user.

## Dependencies And Integration Points
This file is consumed by the kernel Kconfig system and directly controls object inclusion in the regmap Makefile. It integrates with bus subsystems such as I2C, SPI, SPMI, W1, PHYLIB/MDIO, SoundWire, I3C, and FSI.

## Risks And Test Signals
Risks include missing dependency expressions that allow impossible builds, hidden `REGMAP` not enabling when a new backend is added, and KUnit tests not selecting a usable RAM backend. Test signals include allmodconfig/allyesconfig, minimal KUnit regmap builds, and checking that new `CONFIG_REGMAP_*` symbols are mirrored in the Makefile and `REGMAP` default expression.

# sources/distributed-fs/ceph-client/drivers/mfd/wm5110-tables.c

`wm5110-tables.c` is the WM5110/Arizona data-table companion. It supplies revision-specific regmap patches, AOD and main regmap IRQ-chip descriptors, reset defaults, readable/volatile register predicates, ADSP memory windows, and exported I2C/SPI `regmap_config` objects.

Important entry points are `wm5110_patch()`, exported `wm5110_aod`, `wm5110_irq`, `wm5110_revd_irq`, `wm5110_spi_regmap`, and `wm5110_i2c_regmap`. Patch selection is based on `arizona->rev`: Rev A, B, D, and a default Rev E path. The Rev D IRQ table expands the main interrupt controller to six status registers and uses V2 masks for changed interrupt layout. Regmap access policy is driven by `wm5110_readable_register()`, `wm5110_volatile_register()`, and revision-dependent ADSP memory range helpers.

Runtime control is mostly indirect: Arizona core code consumes the exported tables during probe, regmap consults the access predicates on each access/cache decision, and regmap-irq handles interrupt dispatch from the static descriptors. Persistent state is static table data plus hardware register/cache state produced by registered patches and defaults.

Dependencies include `linux/mfd/arizona/core.h`, `linux/mfd/arizona/registers.h`, local `arizona.h`, regmap, and regmap-irq. Integration points are the Arizona bus/core drivers, codec/DSP users, AOD wake handling, and IRQ consumers using `ARIZONA_IRQ_*` numbering.

Risks: revision fallback sends any unrecognized revision to the Rev E patch; manual readable/volatile lists are easy to desynchronize from hardware; ADSP memory windows depend on correct revision detection; repeated patch/IRQ initializer lines in this copied source should be checked as source-integrity risks. Test signals include build coverage, probe-time patch success, I2C and SPI regmap access to audio/DSP/IRQ registers, AOD wake IRQ exercise, and DSP memory reads across supported revisions.

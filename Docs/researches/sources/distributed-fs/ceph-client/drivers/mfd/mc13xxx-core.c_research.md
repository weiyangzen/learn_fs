# sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-core.c

Purpose: Bus-independent core for Freescale MC13xxx PMICs. It wraps regmap access, exports locking and IRQ helpers, performs revision detection, configures regmap-irq, provides ADC conversion support, and registers variant-named child devices.

Important APIs, types, and functions: exported `mc13xxx_lock()`, `mc13xxx_unlock()`, `mc13xxx_reg_read()`, `mc13xxx_reg_write()`, `mc13xxx_reg_rmw()`, `mc13xxx_irq_mask()`, `mc13xxx_irq_unmask()`, `mc13xxx_irq_status()`, `mc13xxx_irq_request()`, `mc13xxx_irq_free()`, `mc13xxx_get_flags()`, and `mc13xxx_adc_do_conversion()` form the shared API. Variant descriptors `mc13xxx_variant_mc13783`, `mc13xxx_variant_mc13892`, and `mc13xxx_variant_mc34708` format revision fields. `mc13xxx_common_init()` initializes watchdog-reset behavior, regmap IRQs, flags, and subdevices. `mc13xxx_common_exit()` removes devices and IRQ chip state.

Control flow: bus drivers initialize `regmap`, `irq`, and `variant`, then call `mc13xxx_common_init()`. The core reads the revision register, enables `WDIRESET`, configures 48 regmap IRQs over two 24-bit banks, chooses feature flags from DT or platform data, then adds children such as regulator, LED, power button, codec, touchscreen, ADC, and RTC. ADC conversions serialize with `mc13xxx_lock()`, request the ADCDONE IRQ, program ADC registers, wait for completion, read samples, and restore touchscreen mode when needed.

State and persistence: `struct mc13xxx` holds regmap, IRQ chip data, mutex, flags, variant pointer, and ADC busy flag. Hardware register state is not cached. ADC conversion temporarily changes ADC configuration and restores only selected fields.

Dependencies and integration points: depends on regmap, regmap-irq, MFD core, DT feature booleans (`fsl,mc13xxx-uses-*`), and transport-specific I2C/SPI files. Child names are constructed from the chip name, for example `mc13892-regulator`.

Risks: `BUG_ON(val & ~mask)` in `mc13xxx_reg_rmw()` can panic the kernel on bad callers. Many `mc13xxx_add_subdevice*()` return values are ignored, so partial child registration can go unnoticed. `snprintf()` length check uses `> sizeof(buf)` rather than `>=`, risking truncation acceptance. ADC conversion error paths require careful review because locks are manually released and reacquired. Test signals include revision parsing for all variants, DT flag selection, regmap IRQ domain child IRQs, ADC timeout and EBUSY handling, and partial MFD-add failure behavior.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/altera-a10sr.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/altera-a10sr.c

Purpose: provides SPI MFD access to the Altera Arria 10 development kit MAX5 system resource chip. It exposes GPIO and reset child devices backed by an 8-bit regmap with explicit readability, writability, and volatility rules.

Important APIs and functions: `altr_a10sr_spi_probe` allocates `struct altr_a10sr`, configures SPI mode 3 with 8-bit words, initializes a SPI regmap, and registers `"altr_a10sr_gpio"` and `"altr_a10sr_reset"` children. Register access policy is defined by `altr_a10sr_reg_readable`, `altr_a10sr_reg_writeable`, and `altr_a10sr_reg_volatile`.

Control flow: on probe, the driver sets SPI transport parameters, calls `spi_setup`, stores driver data, creates a regmap using single-byte read/write with read flag bit set, and then calls `devm_mfd_add_devices`. It is registered as a built-in SPI driver through `builtin_driver`.

State and persistence: software state is the devm-managed `struct altr_a10sr` with the SPI device and regmap. Hardware state is in the MAX5 resource chip registers; no regcache is used (`REGCACHE_NONE`).

Dependencies and integration points: depends on SPI core, `linux/mfd/altera-a10sr.h`, regmap SPI, OF matching for `"altr,a10sr"`, and child GPIO/reset drivers. The regmap access tables protect reserved or unsupported resource-chip registers from generic child access.

Risks: `spi_setup` return value is ignored, so transport configuration failures may surface later as regmap I/O errors. The `max_register` is `ALTR_A10SR_WR_KEY_REG`, which can exclude newer registers if the header grows without updating the core. No IRQ chip is provided for pushbutton/switch status despite volatile IRQ registers.

Test signals: probe on Arria10 DevKit hardware, SPI mode verification, regmap readable/writable filtering, GPIO and reset child creation, register access failure injection, and build coverage for built-in registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/altera-a10sr.c -->

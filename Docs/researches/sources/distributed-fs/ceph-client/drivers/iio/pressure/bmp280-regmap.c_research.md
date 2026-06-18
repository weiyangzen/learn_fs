<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-regmap.c

Purpose: regmap access policy definitions for BMP180, BMP280, BME280, BMP380, and BMP580 register maps.

Important APIs, types, and functions: per-family `*_is_writeable_reg()` and `*_is_volatile_reg()` callbacks classify writable control registers and volatile data/status registers. Exported `regmap_config` objects define 8-bit registers/values, max register, RBTREE cache, and access callbacks for each family.

Control flow: bus adapters choose the chip-info regmap config; regmap then uses these callbacks to cache stable calibration/config registers while bypassing volatile sensor data and status. Write restrictions prevent unintended writes to read-only calibration/data registers.

State and persistence: regmap cache state is maintained by regmap at runtime. This file itself stores only static policy. BMP580 writeable NVM access registers are exposed so the core nvmem operations can program rows.

Dependencies and integration points: depends on regmap and register constants from `bmp280.h`. Exports configs in namespace `IIO_BMP280` to both I2C and SPI adapters through chip-info structures.

Risks: incorrect volatile classification can return stale pressure/temperature/status values; incorrect writeable classification can block required setup or permit unsafe writes. `max_register` must include undocumented registers used by workarounds or NVM operations. BMP580 exposes many control registers, increasing review burden.

Test signals: regmap cache behavior tests around repeated sensor reads, writes to allowed and disallowed registers, variant-specific probe smoke tests, and static review when adding new registers in `bmp280.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-regmap.c -->

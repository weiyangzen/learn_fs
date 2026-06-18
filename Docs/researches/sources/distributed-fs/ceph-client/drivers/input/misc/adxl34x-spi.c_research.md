<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-spi.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-spi.c

Purpose: SPI transport wrapper for the ADXL345/ADXL346 accelerometer core.

Important APIs/types/functions: SPI command macros encode read/write and multi-byte accesses. `adxl34x_spi_read()`, `adxl34x_spi_write()`, and `adxl34x_spi_read_block()` implement `adxl34x_bus_ops`. `adxl34x_spi_probe()` enforces a 5 MHz maximum, sets the FIFO delay flag for SPI clocks above 1.5 MHz, and calls `adxl34x_probe()`.

Control flow and state: probe validates bus speed, delegates initialization to the common core, and stores the returned pointer with `spi_set_drvdata()`. The registered `spi_driver` attaches common sysfs groups and sleep PM ops.

State and persistence behavior: no independent persistence. The SPI speed-derived `fifo_delay_default` influences core FIFO-drain timing for multi-sample reads.

Dependencies and integration points: depends on Linux SPI helpers, the local `adxl34x.h` transport ABI, and the core's input/sysfs/PM exports.

Risks: invalid board SPI mode or IRQ wiring is only caught indirectly. High-speed FIFO correctness depends on the 3 us delay in the core plus controller chip-select behavior.

Test signals: probe at valid and excessive SPI clock rates, multi-byte axis reads, FIFO watermark operation above and below 1.5 MHz, suspend/resume, and module binding by SPI device name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-spi.c -->

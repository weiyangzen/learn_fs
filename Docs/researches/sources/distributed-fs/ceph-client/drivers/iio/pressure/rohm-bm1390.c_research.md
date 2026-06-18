<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/rohm-bm1390.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/rohm-bm1390.c

## Purpose
`rohm-bm1390.c` is an I2C/regmap IIO driver for the ROHM BM1390 pressure sensor. It supports direct raw reads, scale reporting, optional IRQ-driven data-ready triggers, hardware FIFO buffering with watermarks, and temperature sampling alongside pressure.

## Important APIs, types, and functions
Regmap access tables mark volatile, precious, read-only, and no-increment ranges. `struct bm1390_data` stores timestamps, trigger, regmap, IRQ, state, watermark, trigger flag, sample buffer, and a mutex protecting FIFO/read sequences. `bm1390_chip_init()` powers/reset/releases the sensor and configures IIR filtering. `bm1390_read_data()` performs direct continuous-mode measurement. `__bm1390_fifo_flush()` drains the four-sample pressure FIFO, derives timestamps, and appends temperature if selected. Trigger and IRQ handlers coordinate data-ready and FIFO watermark operation. Probe initializes regmap, regulator, chip, buffer, optional trigger, and IIO registration.

## Control flow
Probe enables `vdd`, reads the part ID, allocates IIO state, initializes the chip, sets up the triggered buffer, and, if an IRQ exists, registers trigger and FIFO-capable info operations. Direct raw reads claim direct mode, start continuous measurement, sleep for the maximum measurement time, read the requested channel, and stop measurement. Software-buffer mode without an external trigger enables the hardware FIFO and WMI interrupt. Triggered mode uses DRDY interrupts to push one sample at a timestamp captured in the hard IRQ.

## State and persistence behavior
Driver state tracks whether the device is in single-sample or FIFO mode, whether the trigger is enabled, the configured watermark, and timestamp interpolation state. Regmap cache is reinitialized after reset. Hardware register configuration for IIR/filtering, FIFO enable, WMI/DRDY IRQs, and measurement mode persists until disabled or reset.

## Dependencies and integration points
It depends on I2C regmap, regulators, IIO triggers, triggered buffers, hardware FIFO callbacks, IRQs, and firmware-provided optional IRQ. OF compatible is `rohm,bm1390glv-z`.

## Risks
`bm1390_read_data()` returns `0` instead of `ret` after attempting to stop measurement, which means channel read errors in the switch path should be reviewed carefully. FIFO sequencing is delicate: accessing other registers mid-FIFO can drop samples, hence the mutex and explicit FIFO_LVL close read. Temperature is one value applied to all flushed pressure samples. IRQ-less devices cannot use FIFO buffering.

## Test signals
Test part-ID read, regulator failure, direct pressure/temp reads and scale values, trigger enable/disable, FIFO watermark values 2 and 3, FIFO level corruption handling, timestamp interpolation, IRQ-less mode, and regmap error injection during FIFO close and sample reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/rohm-bm1390.c -->

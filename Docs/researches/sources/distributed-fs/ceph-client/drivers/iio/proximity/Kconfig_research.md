<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/Kconfig

## Purpose
`drivers/iio/proximity/Kconfig` defines configuration entries for IIO lightning, proximity, distance, PIR, SAR, time-of-flight, ultrasonic, and ChromeOS EC proximity drivers. It controls which source files are built and which framework dependencies are selected.

## Important APIs, types, and functions
The file contains Kconfig symbols such as `AS3935`, `CROS_EC_MKBP_PROXIMITY`, `D3323AA`, `HX9023S`, `IRSD200`, `ISL29501`, `LIDAR_LITE_V2`, `MB1232`, `PING`, `RFD77402`, `SRF04`, `SX_COMMON`, `SX9310`, `SX9324`, `SX9360`, `SX9500`, and `SRF08` in the read portion. Entries use `tristate`, `depends on`, `select`, and help text to express build and subsystem requirements.

## Control flow
Kconfig is declarative. The menu first groups the AS3935 lightning sensor under a lightning menu, then groups proximity/distance sensors. User or defconfig choices propagate dependencies to the build system and module list.

## State and persistence behavior
The selected symbols persist in the kernel `.config`, not at runtime. Hidden helper symbol `SX_COMMON` is selected by Semtech drivers.

## Dependencies and integration points
It integrates with the kernel Kconfig system, IIO buffer/trigger options, bus dependencies such as I2C/SPI/GPIOLIB, regmap selections, and ChromeOS EC dependencies. The corresponding `Makefile` uses these symbols to compile objects.

## Risks
Missing `select` lines cause link/build failures for drivers that use triggered buffers or regmap. Overly broad `select`s can force unwanted subsystems. Entries must stay synchronized with source files and Makefile object names.

## Test signals
Run Kconfig builds for each symbol as built-in and module, randconfig coverage for dependency edges, and verify every enabled symbol has a matching Makefile object and required helper selects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/Kconfig -->

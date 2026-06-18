# sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9-spi.c

Purpose: SPI transport wrapper for the Kionix KXSD9 accelerometer. It adapts a `spi_device` to the shared KXSD9 IIO core by building an 8-bit regmap and delegating all sensor behavior to `kxsd9_common_probe()` and `kxsd9_common_remove()`.

Important APIs/types/functions: `kxsd9_spi_probe()` sets `SPI_MODE_0`, initializes `devm_regmap_init_spi()` with 8-bit registers/values and max register `0x0e`, then passes the regmap and SPI id name to the common driver. `kxsd9_spi_remove()` calls the common remove helper. Device matching is through `kxsd9_spi_id`, `kxsd9_of_match`, and `module_spi_driver()`. The module imports namespace `IIO_KXSD9`.

Control flow: probe is transport-only: configure SPI mode, allocate regmap, return probe failure on regmap errors, then transfer lifecycle ownership to the common IIO code. Remove performs no transport cleanup beyond common core teardown because regmap and allocations are devm-managed.

State and persistence: no private transport state is stored here. Runtime state, scale cache, regulators, triggered buffers, and PM state live in `kxsd9.c` private data.

Dependencies and integration points: depends on Linux SPI, regmap-SPI, OF matching, and `kxsd9.h`. It integrates with the accelerometer core through exported common functions and PM ops.

Risks: `spi_get_device_id(spi)->name` assumes an SPI id is present; OF-only instantiation still normally receives modalias/id support, but this is a transport assumption. SPI mode is overwritten unconditionally before regmap initialization.

Test signals: module build with namespace import resolution, SPI probe against `kionix,kxsd9`, regmap read/write traces, direct raw IIO reads, buffer enable/disable, and suspend/resume through `kxsd9_dev_pm_ops`.

# sources/distributed-fs/ceph-client/drivers/iio/light/rohm-bu27034.c

## Purpose
`rohm-bu27034.c` is an I2C IIO driver for the ROHM BU27034ANUC ambient light sensor. It exposes a processed illuminance channel plus two raw visible-band intensity channels and supports direct reads and software-buffered sampling.

## Important APIs, types, and functions
- `struct bu27034_data` stores the regmap, device pointer, serialization mutex, `struct iio_gts` gain/time-scale helper, optional buffer kthread, raw sample storage, and naturally aligned scan payload.
- `bu27034_channels` defines one `IIO_LIGHT` channel, two indexed `IIO_INTENSITY` channels, and a timestamp. `bu27034_scan_masks` permits buffered raw-pair scans and raw-pair-plus-lux scans.
- The IIO GTS tables `bu27034_gains` and `bu27034_itimes` model hardware gain and integration-time multipliers. `bu27034_get_scale()`, `bu27034_set_scale()`, and `bu27034_try_set_int_time()` keep scale, gain, and integration time coherent across both raw channels.
- `bu27034_calc_mlux()` implements the vendor lux formula using fixed-point helpers that avoid overflow in mixed gain/time cases.
- `bu27034_read_raw()`, `bu27034_write_raw()`, and `bu27034_read_avail()` implement the IIO direct-mode ABI.
- `bu27034_buffer_enable()`, `bu27034_buffer_thread()`, and `bu27034_buffer_disable()` implement software-buffered polling because the device has no data-ready interrupt.
- `bu27034_probe()` creates the regmap, enables `vdd`, validates the part ID, initializes IIO GTS, resets the chip, sets up the kfifo buffer, and registers the IIO device.

## Control flow
Probe initializes an RBTREE-cached regmap with volatile data/status ranges and read-only data/manufacturer registers, enables the regulator, reads `SYSTEM_CONTROL`, warns on unexpected part IDs, initializes the gain/time-scale model, resets the sensor, and registers direct plus software-buffer modes.

Direct raw intensity reads claim direct mode, lock the driver mutex, enable measurement, sleep for the active integration time, poll the `VALID` bit, and read the requested 16-bit channel. Direct lux reads enable measurement, wait for a valid two-channel sample, compute milli-lux from both raw channels, and then disables measurement. Scale and integration-time writes are refused while buffering through `iio_device_claim_direct()`.

Buffered mode enables measurement under the same mutex and starts a kernel thread. The thread sleeps until slightly before the expected conversion completion, polls the `VALID` bit, bulk-reads both raw channels, computes lux when requested by the active scan mask, and pushes the scan with an IIO timestamp. Predisable stops the thread before disabling measurements.

## State and persistence
Persistent external state is the chip register map: gain selectors, integration-time selector, measurement enable, and data/status bits. The driver keeps no nonvolatile settings. The regmap caches configuration registers but treats status and data as volatile. The mutex protects measurement enable, scale/time changes, and buffered/direct read exclusion. Reading `MODE_CONTROL4` clears the `VALID` bit, so validity checks are state-changing.

## Dependencies and integration points
The driver integrates with the I2C core, device properties, regulator framework, regmap, IIO core, IIO GTS helper namespace, kfifo software buffers, and kernel kthreads. Device-tree matching uses `rohm,bu27034anuc`; the module imports `IIO_GTS_HELPER`.

## Risks
- Scale changes can require changing integration time and compensating the other channel's gain. Regressions here can silently alter reported units.
- `VALID` reads clear data readiness, so extra status reads or debug paths can consume samples.
- The buffer thread uses sleep-plus-poll timing and can miss samples under scheduler delay; the code accepts that tradeoff.
- `bu27034_get_mlux()` returns before disabling measurement if data acquisition or lux calculation fails, leaving measurement enabled on some error paths.
- Fixed-point lux math has several overflow-avoidance branches; boundary tests are needed for max raw values and high gain ratios.
- Probe only warns on unknown part ID, so compatible-but-incorrect devices may still bind.

## Test signals
- Build with `CONFIG_ROHM_BU27034` and `CONFIG_IIO_GTS_HELPER` coverage.
- Direct-read tests should cover raw channels, lux computation, invalid channel masks, `-EBUSY` while buffering, and scale/int-time writes.
- Conversion tests should exercise all supported gains, all four integration times, ratio branch at `D1/D0 == 1.5`, zero raw values, and saturation-adjacent values.
- Buffer tests should verify scan mask layout, timestamp alignment, kthread start/stop, measurement disable on buffer teardown, and no direct-mode access while active.
- Hardware tests should confirm regulator handling, reset/cache reinit, and `VALID` polling behavior.

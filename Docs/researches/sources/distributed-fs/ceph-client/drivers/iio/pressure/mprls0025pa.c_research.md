<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.c

## Purpose
`mprls0025pa.c` is the shared core for Honeywell MicroPressure MPR pressure sensors. It supports I2C and SPI bus wrappers, regulator and reset GPIO control, devicetree pressure-range/transfer-function configuration, direct raw reads, scale/offset reporting, optional end-of-conversion IRQs, and triggered buffers.

## Important APIs, types, and functions
Transfer-function tables map Honeywell functions A/B/C to raw output min/max counts, and triplet tables map part-number pressure ranges to pascals. `mpr_reset()` toggles the optional reset GPIO. `mpr_read_pressure()` issues a sync conversion command, waits by IRQ completion or fixed delay, reads a four-byte frame, validates status bits, and extracts a 24-bit pressure count. `mpr_trigger_handler()` pushes pressure plus timestamp. `mpr_read_raw()` exposes raw count, scale, and offset. `mpr_common_probe()` parses properties, calculates scale/offset, requests EOC IRQ if present, configures regulator/reset, installs a triggered buffer, and registers the IIO device.

## Control flow
Bus wrappers call `mpr_common_probe()` with transport callbacks and an IRQ. Probe enables `vdd`, reads `honeywell,transfer-function`, then either `honeywell,pressure-triplet` or explicit `honeywell,pmin-pascal`/`pmax-pascal`, validates limits, computes the userspace ABI scale and offset, sets up optional EOC completion, resets the sensor, and registers the direct/buffered IIO device. Direct reads and triggered-buffer reads both lock `data->lock` around the command/wait/read sequence.

## State and persistence behavior
Driver state includes parsed pressure range, transfer-function selection, calculated ABI scale/offset, optional IRQ/completion, reset GPIO, and TX/RX buffers. The sensor's pressure range and transfer function are physical part characteristics, not programmable runtime state. No sampled values are cached except the temporary buffered channel struct.

## Dependencies and integration points
The core exports `mpr_common_probe()` in namespace `IIO_HONEYWELL_MPRLS0025PA`. It depends on IIO triggered buffers, completions, IRQs, GPIO descriptors, regulators, property APIs, unaligned big-endian helpers, and bus-supplied read/write ops.

## Risks
Property validation is critical: wrong transfer function or range yields misleading pressure conversion without obvious bus failure. If an EOC IRQ is declared but never fires, direct reads block up to one second and return `-ETIMEDOUT`. Status handling accepts only `MPR_ST_POWER`; memory/math error bits become `-EIO`, which is conservative. The scale calculation uses integer division and split nanounits, so regression tests need exact ABI values.

## Test signals
Cover all transfer functions, triplet and explicit pressure-range parsing, invalid property combinations, reset GPIO behavior, regulator failure, IRQ and polling measurement paths, busy/status-error frames, triggered buffer pushes, and I2C/SPI transport short-transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.c -->

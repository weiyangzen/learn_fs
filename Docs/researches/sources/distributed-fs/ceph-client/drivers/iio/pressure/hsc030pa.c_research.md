<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.c

Purpose: common IIO core for Honeywell TruStability HSC/SSC pressure and temperature sensors. Bus-specific files provide the receive callback.

Important APIs, types, and functions: `hsc_triplet_variants[]` and `hsc_range_config[]` map pressure triplets to pascal ranges. `hsc_func_spec[]` defines output ranges for transfer functions A, B, C, and F. `hsc_get_measurement()` calls the bus receive callback and validates status. `hsc_read_raw()` extracts 14-bit pressure and 11-bit temperature from the 4-byte frame and exposes scale/offset. `hsc_common_probe()` parses firmware properties, enables `vdd`, computes pressure conversion fields, sets up triggered buffer, and registers the IIO device.

Control flow: direct and buffered reads receive a four-byte measurement, check that status bits are zero, and decode fields from big-endian frame layout. Probe requires `honeywell,transfer-function` and `honeywell,pressure-triplet`; if the triplet starts with `NA`, it falls back to explicit pmin/pmax properties.

State and persistence: runtime state includes function, pressure limits, output min/max, computed scale and offset, latest validity flag, raw buffer, and scan buffer. No persistent storage is modified.

Dependencies and integration points: depends on IIO buffers/triggers, regulator framework, firmware properties, unaligned/bitfield helpers, and bus receive callbacks declared in `hsc030pa.h`. Exports `hsc_common_probe` in namespace `IIO_HONEYWELL_HSC030PA`.

Risks: no mutex protects shared `buffer` and `is_valid` between direct reads and triggered buffers. Pressure offset uses `IIO_VAL_INT_PLUS_MICRO` while scale uses nano precision; rounding should be verified for small ranges. `str_has_prefix(triplet, "NA")` accepts any `NA...` value for explicit range mode. Stale-data status maps to `-EAGAIN`, which callers may retry aggressively.

Test signals: all transfer functions, representative triplet mappings, explicit pmin/pmax mode, invalid status codes, direct versus buffered concurrency, scale/offset vectors from datasheet, regulator failure, and namespace/modpost builds with bus modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.c -->

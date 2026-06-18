<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-core.c

Purpose: shared IIO core for PNI RM3100 3-axis geomagnetic sensors. Bus wrappers provide regmap transport; the core implements direct polling, optional IRQ/data-ready trigger, continuous buffered mode, sample-frequency control, cycle-count/scale management, and exported regmap access tables.

Important APIs/types/functions: exported symbols are `rm3100_readable_table`, `rm3100_writable_table`, `rm3100_volatile_table`, and `rm3100_common_probe()`. `struct rm3100_data` stores regmap, completion, interrupt flag, conversion time, scale, fixed scan buffer, optional data-ready trigger, and mutex. Key functions are `rm3100_wait_measurement()`, `rm3100_read_mag()`, `rm3100_get_samp_freq()`, `rm3100_set_cycle_count()`, `rm3100_set_samp_freq()`, raw read/write handlers, buffer preenable/postdisable, IRQ handlers, and `rm3100_trigger_handler()`.

Control flow: common probe allocates IIO state, sets up optional IRQ and trigger, installs a triggered buffer, reads `TMRC`, validates sample-rate index, initializes conversion timeout and cycle count/scale, and registers the IIO device. Direct reads claim direct mode, write the poll register for one axis, wait for DRDY via completion or status polling, bulk-read a 24-bit big-endian result, sign-extend, and return. Buffered mode writes CMM to enable active axes, IRQ or trigger handler bulk-reads packed result bytes, reshapes them to IIO 32-bit storage alignment, pushes timestamped buffers, and disables CMM after buffer shutdown.

State/persistence: sample rate is in `TMRC`, cycle count is in three CC registers, and `scale`/`conversion_time` are cached in memory. Frequency writes may change cycle count between 100 and 200 to keep 600 Hz valid and restart CMM if buffers are active. There is no PM implementation despite TODO.

Dependencies/integration: uses regmap supplied by I2C/SPI wrappers, IIO sysfs/buffer/trigger APIs, IRQ completions, unaligned big-endian helpers, and namespace `IIO_RM3100`.

Risks: no runtime/system PM. `rm3100_get_samp_freq()` indexes `rm3100_samp_rates[tmp - offset]` without range validation after probe, so corrupted registers can cause invalid indexing. Buffer handler has several scan-mask-specific byte reshaping paths that are easy to regress. IRQ thread clears interrupts by writing `POLL=0`, which may interact with concurrent measurements.

Test signals: test I2C and SPI wrappers, no-IRQ polling and IRQ completion paths, every sample-frequency value including cycle-count transitions, direct-mode exclusion during buffers, all supported scan masks, CMM restart when frequency changes while buffered, timeout paths, and modpost namespace exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-core.c -->

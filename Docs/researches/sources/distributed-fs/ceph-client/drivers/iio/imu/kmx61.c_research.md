<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/kmx61.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/kmx61.c

Purpose: complete I2C IIO driver for Kionix KMX61, exposing accelerometer and magnetometer as two IIO devices with raw reads, scale/ODR sysfs, data-ready triggers, buffered capture, and accelerometer any-motion threshold events.

Important APIs/types/functions: `struct kmx61_data` stores shared I2C client, mutex, standby/power flags, range/ODR/wake settings, two `iio_dev` instances, and three triggers. Core helpers are `kmx61_set_mode()`, `kmx61_set_odr()`, `kmx61_set_scale()`, `kmx61_chip_init()`, `kmx61_setup_new_data_interrupt()`, `kmx61_setup_any_motion_interrupt()`, `kmx61_set_power_state()`, `kmx61_read_raw()`, event callbacks, trigger callbacks, `kmx61_probe()`, remove, and PM hooks.

Control flow: probe allocates shared driver data, creates separate accel and magn IIO devices, validates WHO_AM_I, initializes range/ODR/wake defaults, optionally requests one IRQ and allocates accel data-ready, magnetometer data-ready, and motion triggers, then registers both IIO devices with runtime autosuspend. Raw reads power the selected sensor, read a 16-bit SMBus word, sign-extend according to channel shift/realbits, and autosuspend. ODR and scale changes put both sensors in standby before writing configuration. IRQ top-half polls enabled triggers, while the threaded handler reads motion status bits, pushes per-axis rising/falling threshold events, resets the interrupt latch, and reads `INL`.

State and persistence: `acc_stby`/`mag_stby` mirror hardware standby; `acc_ps`/`mag_ps` track runtime PM logical users; `range`, `odr_bits`, `wake_thresh`, and `wake_duration` mirror configuration. Suspend forces both sensors to standby without updating saved standby state; resume restores saved standby bits. Runtime suspend updates standby state and runtime resume reconstructs standby from power-state booleans.

Dependencies and integration: depends on I2C SMBus byte/word access, IIO sysfs/events/triggers/triggered buffers, runtime PM, and an optional client IRQ. The driver has an I2C ID table for `kmx611021`.

Risks: most configuration requires both sensors in standby, so failures after entering standby can leave hardware disabled or software mirrors stale. `kmx61_set_power_state()` updates power booleans before runtime PM calls. Motion event config refuses threshold changes while enabled but trigger/event interactions share `motion_trig_on` and `ev_enable_state`. Buffer pushes do not include the pollfunc timestamp despite using `iio_pollfunc_store_time`.

Test signals: probe WHO_AM_I, accel and magn raw reads, scale and sampling-frequency writes across supported tables, runtime autosuspend/resume, three trigger enable states, any-motion threshold events per axis/direction, IRQ latch clearing, and remove/suspend restoring standby.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/kmx61.c -->

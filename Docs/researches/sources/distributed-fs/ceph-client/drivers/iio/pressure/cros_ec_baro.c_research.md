<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/cros_ec_baro.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/cros_ec_baro.c

Purpose: IIO pressure driver for a barometer presented by the ChromeOS Embedded Controller sensor hub.

Important APIs, types, and functions: `struct cros_ec_baro_state` embeds `struct cros_ec_sensors_core_state` and owns a two-entry channel array for pressure plus timestamp. `cros_ec_baro_read()` handles raw pressure through `cros_ec_sensors_read_cmd()`, reads scale by sending `MOTIONSENSE_CMD_SENSOR_RANGE`, and delegates other attributes to `cros_ec_sensors_core_read()`. `cros_ec_baro_write()` updates the EC sensor range for scale writes and delegates other writes. `cros_ec_baro_probe()` initializes common EC sensor state, builds channel descriptors, and registers through `cros_ec_sensors_core_register()`.

Control flow: probe requires a parent `cros_ec_dev`, allocates IIO state, calls `cros_ec_sensors_core_init()`, configures a pressure channel when `state->core.type` is `MOTIONSENSE_TYPE_BARO`, appends a timestamp channel, sets `read_ec_sensors_data`, and registers callbacks. Runtime reads and writes hold `core.cmd_lock` while sending EC host commands.

State and persistence: state is EC-sensor runtime metadata, channel definitions, current range tracking, and IIO scan buffering in memory. Scale writes update EC sensor range and set `range_updated`/`curr_range`; persistence beyond runtime depends on EC firmware behavior.

Dependencies and integration points: depends on `IIO_CROS_EC_SENSORS_CORE`, ChromeOS EC command protocol, IIO kfifo/triggered buffer support, EC platform data, and platform-device ID `cros-ec-baro`. Integration is with the EC abstraction, not a specific pressure sensor datasheet.

Risks: behavior depends on EC firmware units and range semantics; scale is returned as `range / (10 << CROS_EC_SENSOR_BITS)` to produce kPa. Raw data is stored through a `u16` local cast to `s16 *`, so signedness and width must remain aligned with EC sensor format. Unknown motion sensor types abort probe. Range writes round up, which is intentional but can surprise exact-value tests.

Test signals: EC sensor enumeration with and without parent EC device, pressure raw/scale reads, scale writes and `curr_range` update, sample-frequency delegation, triggered buffer capture through `cros_ec_sensors_push_data`, suspend/resume through EC common PM ops, and comparison with EC firmware-reported units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/cros_ec_baro.c -->

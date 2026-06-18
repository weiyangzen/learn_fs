# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub.c

## Purpose
`cros_ec_sensorhub.c` discovers motion sensors exposed by a Chrome EC and creates platform devices for the corresponding IIO sensor drivers. It also wires FIFO/ring support when the EC supports motion-sense FIFO events.

## Important APIs, Types, and Functions
- `cros_ec_sensorhub_allocate_sensor()` registers a child platform device with `struct cros_ec_sensor_platform { sensor_num }` and devm cleanup.
- `cros_ec_sensorhub_register()` loops over EC sensors, sends `MOTIONSENSE_CMD_INFO`, maps motion-sense types to platform device names, and registers sensor children.
- `cros_ec_sensorhub_probe()` allocates shared command buffers and `struct cros_ec_sensorhub`, checks EC features, retrieves sensor count, prepares FIFO support, enumerates sensors, and adds/removes ring support.
- PM callbacks disable/enable FIFO interrupts across suspend/resume.

## Control Flow
Probe obtains the parent `cros_ec_dev`, allocates a command large enough for motion-sense parameters and max EC response, and checks `EC_FEATURE_MOTION_SENSE`. In normal sensorhub mode it calls `cros_ec_get_sensor_count()`, optionally allocates ring data if `EC_FEATURE_MOTION_SENSE_FIFO` exists, enumerates every sensor with up to 50 retries on `-EBUSY`, creates typed platform children, and finally registers the FIFO notifier/ring. In legacy mode, if the EC does not advertise motion sense but the platform device exists, it creates two `"cros-ec-accel-legacy"` children.

## State and Persistence
`struct cros_ec_sensorhub` stores the EC pointer, shared command buffer, params/response aliases, sensor count, command mutex, and ring-related state allocated by `cros_ec_sensorhub_ring_allocate()`. The parent `cros_ec_dev->has_kb_wake_angle` flag is set when at least two accelerometers are found. Platform children are registered for the lifetime of the sensorhub device and devm-unregistered on teardown.

## Dependencies and Integration Points
The driver depends on Chrome EC feature and command helpers from `cros_ec_proto.c`, motion-sense command structures, `cros_ec_sensorhub_ring_*()` helpers, platform device registration, and IIO child drivers named `cros-ec-accel`, `cros-ec-gyro`, `cros-ec-mag`, `cros-ec-baro`, `cros-ec-prox`, `cros-ec-light`, `cros-ec-activity`, and `cros-ec-lid-angle`.

## Risks and Edge Cases
Sensor info retrieval tolerates individual failures by logging and continuing, so a partially enumerated sensorhub can exist. `-EBUSY` retrying handles EC sensor initialization delays but caps at 50 attempts with 5-6 ms sleeps. A zero sensor count is treated as probe failure. FIFO support must be allocated before child registration because child drivers may register callbacks. Suspend/resume behavior assumes disabling FIFO interrupts is enough to avoid unwanted EC interrupts while preserving wake signaling.

## Test Signals
No direct tests are present in this subset. Indirect test coverage exists for `cros_ec_get_sensor_count()` in `cros_ec_proto_test.c`. Runtime signals include child platform devices appearing for the expected sensor types and FIFO samples reaching registered IIO callbacks when FIFO support is enabled.

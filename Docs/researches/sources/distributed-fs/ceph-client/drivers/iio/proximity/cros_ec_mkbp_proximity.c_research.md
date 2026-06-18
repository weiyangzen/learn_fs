<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/cros_ec_mkbp_proximity.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/cros_ec_mkbp_proximity.c

## Purpose
`cros_ec_mkbp_proximity.c` is a platform IIO driver exposing the ChromeOS EC MKBP front-proximity switch as a proximity channel with optional threshold events.

## Important APIs, types, and functions
`struct cros_ec_mkbp_proximity_data` stores the EC pointer, IIO device, mutex, notifier block, last state, and event-enable flag. `cros_ec_mkbp_proximity_query()` sends `EC_CMD_MKBP_INFO` version 1 to fetch current switch state. `cros_ec_mkbp_proximity_parse_state()` extracts `EC_MKBP_FRONT_PROXIMITY`. `cros_ec_mkbp_proximity_push_event()` compares state changes and emits IIO threshold events when enabled. Notifier, read_raw, event config, resume, probe, and remove functions wire the driver into ChromeOS EC event delivery.

## Control flow
Probe obtains the parent `cros_ec_device`, allocates an IIO device, initializes `last_proximity` to unknown, registers IIO, and registers a blocking notifier on the EC event chain. Raw reads query the EC synchronously. MKBP switch notifications parse the event payload and push events on state changes. Resume queries current state and pushes an event if the state changed while suspended.

## State and persistence behavior
Runtime state is `last_proximity` and `enabled`, protected by a mutex. No hardware configuration is persisted by this driver; event enable only controls whether IIO events are emitted locally.

## Dependencies and integration points
It depends on ChromeOS EC command/protocol headers, platform devices, blocking notifier chains, IIO events/sysfs, and unaligned little-endian parsing. OF compatible is `google,cros-ec-mkbp-proximity`.

## Risks
Notifier registration is manual rather than devm-managed, making remove cleanup essential. Event direction maps proximity present to falling and absent to rising, which tests must preserve. If the IIO clock is not boottime, EC event timestamps are replaced with local IIO timestamps. Query size mismatches return `-EPROTO`.

## Test signals
Test EC query success, transport failures and wrong response sizes, notifier switch events, enable/disable event config, duplicate-state suppression, resume state reconciliation, timestamp mode behavior, and remove unregistering the notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/cros_ec_mkbp_proximity.c -->

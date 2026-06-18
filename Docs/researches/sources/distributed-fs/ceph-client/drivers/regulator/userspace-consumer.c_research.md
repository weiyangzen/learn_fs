<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/userspace-consumer.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/userspace-consumer.c

Purpose: Exposes one or more regulator supplies to userspace through sysfs so board support or tests can enable and disable named outputs.

Important APIs and types: `struct userspace_consumer_data` stores optional display name, mutex, enabled flag, autoswitch policy, supply count, and bulk supply array. Sysfs attributes `name` and `state` expose read-only name and read/write enabled state. Probe uses `devm_regulator_bulk_get_exclusive()` and state writes use `regulator_bulk_enable()` or `_disable()`.

Control flow: Probe consumes platform data when provided. For devicetree `regulator-output` nodes, it creates a default single `"vout"` supply and disables automatic initial switching. After exclusive regulator acquisition, it creates the sysfs group, optionally enables supplies when `init_on && !no_autoswitch`, then initializes the cached enabled flag from the first supply. Remove deletes sysfs and optionally disables supplies.

State and persistence: Cached state is protected by a mutex and mirrors successful regulator operations. Persistent state is only the underlying regulator hardware. Sysfs permissions provide the operational interface.

Dependencies and integration points: Depends on regulator consumer APIs, optional platform data, OF compatible `regulator-output`, and sysfs attribute registration.

Risks: Invalid state strings log an error but return `count`, so userspace sees a successful write. Enabled state is inferred from only the first supply after probe. Exclusive regulator acquisition prevents concurrent kernel consumers by design. `no_autoswitch` leaves output state untouched on probe/remove.

Test signals: Platform-data and OF probe, missing supplies, exclusive-busy failures, sysfs `enabled`/`disabled` and `1`/`0` writes, invalid writes, multi-supply partial failure behavior, and remove with both autoswitch modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/userspace-consumer.c -->

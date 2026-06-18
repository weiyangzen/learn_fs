# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_phc.c

## Purpose
`ena_phc.c` integrates ENA device time with the Linux PTP Hardware Clock framework. The implementation is read-only from the host perspective: it registers a PHC when supported and enabled, provides timestamp reads with system timestamp bracketing, and rejects adjustment/set/feature operations.

## Important APIs, Types, And Functions
The PTP callbacks are `ena_phc_gettimex64()`, `ena_phc_adjtime()`, `ena_phc_adjfine()`, `ena_phc_settime64()`, and `ena_phc_feature_enable()`. Public driver APIs are `ena_phc_enable()`, `ena_phc_is_enabled()`, `ena_phc_is_active()`, `ena_phc_alloc()`, `ena_phc_free()`, `ena_phc_init()`, `ena_phc_destroy()`, and `ena_phc_get_index()`. `ena_phc_register()` and `ena_phc_unregister()` manage kernel registration.

## Control Flow, State, And Integration
Probe allocates `struct ena_phc_info`; device initialization calls `ena_phc_init()`. Initialization checks ENA PHC support and kernel/devlink enablement, initializes/configures ENA common PHC state, then registers `ptp_clock_info`. Timestamp reads lock `phc_info->lock`, bracket `ena_com_phc_get_timestamp()` with `ptp_read_system_prets()` and `ptp_read_system_postts()`, and convert nanoseconds to `timespec64`. Destroy unregisters unless a reset is in progress, preserving PHC index across reset, then destroys ENA common PHC state. On failures, PHC is disabled and the devlink PHC param is disabled.

## Dependencies
Dependencies include Linux PTP clock APIs, PCI slot naming, ENA common PHC operations, ENA adapter flags, and ENA devlink PHC parameter handling.

## Risks And Test Signals
Risks include lock ordering around timestamp reads, PHC lifetime across reset/remove, devlink enable state mismatch, and unsupported adjustment operations surprising callers. Test signals include `ethtool -T`, `/dev/ptp*` index stability across reset, timestamp reads under concurrent reset, devlink PHC toggling, and expected `-EOPNOTSUPP` for set/adjust requests.

# sources/distributed-fs/ceph-client/drivers/powercap/dtpm_devfreq.c

## Purpose
`dtpm_devfreq.c` implements a DTPM backend for devfreq devices with Energy Model data. It registers devfreq devices as DTPM leaves, estimates power from devfreq load/frequency, and limits power through device PM QoS maximum-frequency requests.

## Important APIs, Types, And Functions
`struct dtpm_devfreq` embeds `struct dtpm`, `dev_pm_qos_request`, and a `struct devfreq *`. Backend ops are `update_pd_power_uw()`, `set_pd_power_limit()`, `get_pd_power_uw()`, and `pd_release()`. `_normalize_load()` converts devfreq busy/total time to a 0..1024 scale. `__dtpm_devfreq_setup()` registers Energy Model data if missing, registers the DTPM node, and adds PM QoS.

## Control Flow
During DT setup, the backend finds a devfreq device by node; absent devices are ignored. If no EM exists, it tries `dev_pm_opp_of_register_em()`. It allocates state, initializes DTPM ops, registers a leaf named from the parent device, adds a `DEV_PM_QOS_MAX_FREQUENCY` request, then calls `dtpm_update_power()`. Limit setting chooses the highest EM frequency whose power is not greater than the request, writes QoS, and returns achieved power. Current power uses `devfreq->last_status`, normalizes load, finds the EM frequency at or above current frequency, and scales power by busy fraction.

## State, Persistence, And Dependencies
State is the DTPM node, devfreq pointer, and PM QoS request. Hardware/device state is affected only through PM QoS. Dependencies include devfreq, OPP/EM registration, PM QoS, OF node lookup, and DTPM core.

## Integration Points
`dtpm_devfreq_ops` is included under `CONFIG_DTPM_DEVFREQ`. It is invoked by `dtpm_setup_dt()` for any hierarchy DT node; nodes without devfreq devices are skipped quietly.

## Risks
Like CPU, `set_pd_power_limit()` uses `table[i - 1]` and can underflow if the requested limit is below the lowest EM state. `__dtpm_devfreq_setup()` registers an EM when missing but does not re-fetch `pd` afterward before later functions rely on it. `dtpm_update_power()` return value is ignored after QoS setup. There is no exit hook beyond node release, so backend lifetime depends on DTPM tree destruction.

## Test Signals
Test missing devfreq nodes, missing EM with successful/failed OPP EM registration, min-limit underflow behavior, PM QoS add/remove, load normalization for huge and zero total time, current-frequency unit conversion, and DTPM unregister cleanup.

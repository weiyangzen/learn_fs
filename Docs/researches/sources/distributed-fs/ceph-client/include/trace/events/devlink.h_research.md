<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/devlink.h -->
# sources/distributed-fs/ceph-client/include/trace/events/devlink.h

## Purpose
Defines the `devlink` tracepoint surface for network device-management diagnostics when `CONFIG_NET_DEVLINK` is enabled, plus small no-op stubs for selected trace calls when devlink support is compiled out. The header records hardware messages, hardware errors, health-reporter transitions, aborted recovery attempts, and packet trap reports.

## APIs, Control Flow, and State
The exported trace call sites are generated from `TRACE_EVENT()` declarations: `devlink_hwmsg`, `devlink_hwerr`, `devlink_health_report`, `devlink_health_recover_aborted`, `devlink_health_reporter_state_update`, and `devlink_trap_report`. Events capture stable device identity through `devlink_bus_name()`, `devlink_dev_name()`, and `devlink_dev_driver_name()`. `devlink_hwmsg` copies an arbitrary byte buffer into a dynamic trace array; health events copy reporter names, messages, state, and recovery timing; trap reports copy trap/group names and the optional input netdev name. The header itself persists no runtime state beyond trace buffers owned by ftrace/perf; disabled builds only define empty `trace_devlink_hwmsg()` and `trace_devlink_hwerr()` helpers.

## Dependencies, Integration, Risks, and Tests
Depends on `<net/devlink.h>`, device helpers, `sk_buff`, `devlink_trap_metadata`, and the tracepoint generator. Integration points are devlink driver hardware command paths, health reporters, and packet trap delivery. Risks include tracing large or sensitive hardware buffers, passing metadata whose string fields are not valid for the tracepoint lifetime, assuming health/trap stubs exist in !`CONFIG_NET_DEVLINK` builds, and copying buffers from paths where trace overhead matters. Test signals include enabling `/sys/kernel/tracing/events/devlink/*`, exercising devlink health report/recover flows, generating traps, and building both devlink-enabled and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/devlink.h -->

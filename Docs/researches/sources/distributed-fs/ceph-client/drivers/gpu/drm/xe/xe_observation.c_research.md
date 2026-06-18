
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_observation.c

## Purpose

`xe_observation.c` is the top-level observation ioctl dispatcher for Xe performance/diagnostic streams and owns the `dev/xe/observation_paranoid` sysctl controlling non-root access.

## Important APIs, Types, and Functions

- Global `u32 xe_observation_paranoid = true`.
- `xe_observation_ioctl()` dispatches by observation type.
- Internal dispatchers route OA operations to `xe_oa_*` and EU stall stream open to `xe_eu_stall_stream_open()`.
- `xe_observation_sysctl_register()` and `xe_observation_sysctl_unregister()` manage the sysctl table.

## Control Flow

The DRM ioctl receives `drm_xe_observation_param`, rejects top-level extensions, selects OA or EU stall by `observation_type`, then dispatches supported operations. OA supports stream open, add config, and remove config; EU stall currently supports stream open only.

## State and Persistence Behavior

The paranoid sysctl persists globally while the module is loaded. Its value is consulted by OA stream/config and OA mmap permission checks.

## Dependencies and Integration Points

It connects UAPI observation types to OA and EU stall backends and is registered/unregistered from module init/exit.

## Risks and Edge Cases

- Unsupported extensions or operation/type combinations return `-EINVAL`.
- Sysctl registration currently returns 0 unconditionally; a failed `register_sysctl()` would leave `sysctl_header` NULL for unregister.
- Relaxing `observation_paranoid` broadens access to sensitive performance data.

## Test Signals

Ioctl dispatch tests should cover all valid and invalid type/op combinations, extension rejection, sysctl registration/unregistration, and permission behavior when toggling `observation_paranoid`.

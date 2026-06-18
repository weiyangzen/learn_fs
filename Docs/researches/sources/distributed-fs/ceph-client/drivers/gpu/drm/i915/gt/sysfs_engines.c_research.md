# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.c

### Purpose
`sysfs_engines.c` creates `/sys/.../engine/<engine>/` nodes exposing i915 engine identity, uABI capabilities, scheduler/reset/heartbeat tunables, and default values.

### Important APIs, Types, And Functions
The public entry is `intel_engines_add_sysfs()`. It defines `struct kobj_engine`, show/store callbacks for `name`, `class`, `instance`, `mmio_base`, `capabilities`, `known_capabilities`, `max_busywait_duration_ns`, `timeslice_duration_ms`, `stop_timeout_ms`, `preempt_timeout_ms`, and optionally `heartbeat_interval_ms`. Helpers include `__caps_show()`, `repr_trim()`, `kobj_engine()`, and `add_defaults()`.

### Control Flow
Initialization creates an `engine` kobject under the DRM primary device, iterates uABI engines, creates one kobject per engine, installs base files, conditionally installs timeslice/preempt files, and creates a `.defaults` child with read-only default attributes. Store callbacks parse integers, clamp against engine-specific limits, reject unclamped values with `-EINVAL`, update `engine->props`, and adjust active timers or heartbeat state when needed.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is in the sysfs kobjects and mutable `engine->props`; defaults are read from `engine->defaults`. Dependencies include Linux kobject/sysfs APIs, i915 timer utilities, execlists scheduling state, heartbeat control, and engine uABI metadata. Integration is user/admin-facing sysfs tuning. Risks include partial sysfs creation on failures, capability string truncation, concurrent property reads/writes using `READ_ONCE`/`WRITE_ONCE`, and exposing invalid timings. Test signals are sysfs file presence by engine capability, rejected out-of-range writes, timer updates on active engines, and correct `.defaults` contents.

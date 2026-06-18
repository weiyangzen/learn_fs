## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log_debugfs.c

Purpose: exposes GuC logging controls and dumps through debugfs.

Important APIs, types, and functions:
- `obj_to_guc_log_dump_size()` estimates seq_file buffer size for a raw dword log dump.
- `guc_log_dump_size()` and `guc_load_err_dump_size()` size normal and load-error dumps.
- `guc_log_dump_show()` and `guc_load_err_log_dump_show()` call `intel_guc_log_dump()` with the appropriate source.
- `guc_log_level_get/set()` expose `intel_guc_log_get_level()` and `intel_guc_log_set_level()`.
- `guc_log_relay_open()`, `guc_log_relay_write()`, and `guc_log_relay_release()` implement a debugfs relay control file: open creates relay state, writing `1` starts relay, other writes force flush, release closes relay.
- `intel_guc_log_debugfs_register()` registers `guc_log_dump`, `guc_load_err_log_dump`, `guc_log_level`, and `guc_log_relay`.

Control flow:
- Registration is skipped when GuC is unsupported.
- Dump reads preallocate based on backing object size. DEBUG_GEM builds warn once if the seq_file overflows the estimate.
- Relay open requires `intel_guc_is_ready()`, stores the log pointer in `file->private_data`, then delegates lifecycle to `intel_guc_log.c`.

State and persistence:
- Debugfs writes mutate log verbosity and relay state. The relay file is session-scoped: open creates, writes start/flush, release closes.

Dependencies and integration points:
- Depends on GT debugfs helpers, GuC support/ready checks, log implementation, and UC load-error log storage.

Risks:
- Large log objects can produce large textual dumps; size estimation must keep seq_file usable.
- Relay open/close must be balanced; release always calls close.
- Userspace can force flushes while firmware/runtime PM state changes, so lower-level log code must handle readiness.

Test signals:
- Read both dump files with/without log objects and saved load-error logs.
- Set legal/illegal log levels through debugfs.
- Open relay, write `1`, write other values to flush, then close; verify no leaked relay channel.

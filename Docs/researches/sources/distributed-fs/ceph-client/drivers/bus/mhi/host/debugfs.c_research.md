# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/debugfs.c

Purpose: debugfs diagnostics and controls for MHI host controllers. It exposes controller state, event rings, channels, devices, selected register dumps, device wake votes, and timeout tuning under a per-controller debugfs directory.

Important APIs: `mhi_debugfs_init()` creates the root directory, `mhi_create_debugfs()` creates per-controller files, `mhi_destroy_debugfs()` removes them, and `mhi_debugfs_exit()` removes the root. File operations use `single_open()` and seq_file show helpers. Writable files are `device_wake` and `timeout_ms`.

Control flow: state/events/channels/devices show functions first validate active state when needed, then print controller PM/device/MHI/EE state, counters, event ring contexts, channel contexts, child MHI devices, or register values. `device_wake` accepts `get`/`put` to call `mhi_device_get_sync()` or `mhi_device_put()`. `timeout_ms` parses a u32 and updates controller timeout.

State and persistence: debugfs files expose live controller fields and can mutate `timeout_ms` and device wake votes. No state persists across unload/reboot. `debugfs_dentry` is tracked in the controller.

Dependencies and integration: depends on debugfs, seq_file, MHI host internals, register access helpers, PM-state validity macros, device model child traversal, and string helpers.

Risks: writable debug controls can affect runtime power state and timeout behavior, so this is gated by debugfs configuration rather than production ABI. Register dumps require valid PM/register-access state. Test signals include debugfs directory creation/removal, reads when active/inactive, wake get/put behavior, timeout writes including invalid input, event/channel ring formatting, register read failures, and controller removal while files exist.

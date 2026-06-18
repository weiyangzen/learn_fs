# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_debugfs.c

## Purpose
`fjes_debugfs.c` exposes a debugfs status view for FJES endpoint connectivity when `CONFIG_DEBUG_FS` is enabled. It creates a driver root directory and per-adapter status file that reports each endpoint's share state, zone relationship, and connection status.

## Important APIs and Functions
The file defines `fjes_dbg_init()`, `fjes_dbg_exit()`, `fjes_dbg_adapter_init()`, `fjes_dbg_adapter_exit()`, and the seq-file show function `fjes_dbg_status_show()`. `DEFINE_SHOW_ATTRIBUTE(fjes_dbg_status)` supplies file operations for the read-only `status` file. `ep_status_string[]` maps `enum ep_partner_status` values to display strings.

## Control Flow
Module init calls `fjes_dbg_init()` to create the root debugfs directory named after `fjes_driver_name`. Probe calls `fjes_dbg_adapter_init()`, which creates a child directory named after the platform device and a `status` file with the adapter as private data. Reads call `fjes_dbg_status_show()`, which iterates all EPIDs, prints placeholders for the local endpoint, and for remote endpoints queries `fjes_hw_get_partner_ep_status()`, `fjes_hw_epid_is_same_zone()`, and `fjes_hw_epid_is_shared()`.

## State, Dependencies, and Integration
Global state is `fjes_debug_root`; per-adapter state is `adapter->dbg_adapter`. The file depends on debugfs, seq_file, platform device names, and the hardware status helpers in `fjes_hw.c`. It is compiled into the driver object but entirely guarded by `CONFIG_DEBUG_FS`.

## Risks and Test Signals
Risks include indexing `ep_status_string[]` if partner status ever exceeds the enum range, stale debugfs dentries after probe/remove failures, and status reads racing with endpoint teardown. Test signals are clean builds with debugfs enabled and disabled, correct `/sys/kernel/debug/fjes/<device>/status` output for shared/unshared/waiting/complete endpoints, and safe removal while the file is open.

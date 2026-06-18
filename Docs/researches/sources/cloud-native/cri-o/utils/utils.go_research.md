<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils.go -->
# sources/cloud-native/cri-o/utils/utils.go

Purpose: broad CRI-O utility collection for process status, detachable IO, diagnostics, identity file handling, SELinux labels, sync helpers, terminal resize handling, and duration parsing.

Important APIs and flow: `CopyDetachable` copies from reader to writer while detecting detach key sequences, returning `DetachError`. `WriteGoroutineStacksToFile` and `WriteGoroutineStacksTo` dump goroutine stacks. `GenerateID` returns 32 random bytes hex encoded. `GetUserInfo`, `GetUser`, and `GetGroup` safely read container `/etc/passwd` and `/etc/group` using secure joins. `GeneratePasswd` and `GenerateGroup` create runtime-specific passwd/group files only when IDs are absent and permissions allow safe modification. `EnsureSaneLogPath` removes broken symlinks. `GetLabelOptions`, `SyncParent`, `Sync`, `HandleResizing`, and `ParseDuration` provide smaller shared behaviors.

State and persistence: reads container rootfs files, may create/chown passwd/group files in a run directory, remove broken log-path symlinks, sync file descriptors, and spawn a resize goroutine. Risks include subtle detach sequence buffering, secure file permission skip rules, chown requirements, unbounded resize goroutine lifetime until channel close, and negative durations being made positive. Test signal is broad `utils_test.go` coverage for IDs, copy/detach errors, user/group generation, and duration parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils.go -->

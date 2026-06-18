<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_linux.go -->
# sources/cloud-native/cri-o/utils/utils_linux.go

Purpose: Linux-specific utility implementations for systemd scope placement and filesystem sync.

Important APIs and flow: `RunUnderSystemdScope` validates a DBus manager, builds default transient unit properties (`PIDs`, `Delegate`, `DefaultDependencies`), optionally adds a slice, starts a systemd transient unit via `RetryOnDisconnect`, and waits up to six minutes for the job channel to report `done`. `Syncfs` opens a path and invokes the Linux `syncfs` syscall on its file descriptor.

State and integration: mutates systemd state by moving a PID into a scope; syncs filesystem state to disk. Dependencies include systemd DBus, CRI-O internal dbus manager, and Linux syscalls. Risks include long timeout, DBus job channel behavior, pid/slice validity, and `syncfs` requiring open path permissions. Test signal is mostly integration-level because systemd behavior is host-dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_linux.go -->

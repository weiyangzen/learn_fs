<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_freebsd.go -->
# sources/cloud-native/containerd/core/mount/mount_freebsd.go

Purpose: FreeBSD platform mount implementation using the system `mount(8)` command because Go syscall packages do not expose a FreeBSD `Mount` wrapper.

Important APIs/types/functions: platform `(*Mount).mount` builds `mount -o <opt> -t <type> <source> <target>` arguments; it uses `Lookup` and `unmount` for ECHILD retry cleanup.

Control flow: captures mount info before invoking `mount`; retries up to ten times on `unix.ECHILD`; when mount ID changes after an ECHILD, unmounts the new mount before retrying. Non-ECHILD failures include command output in the returned error.

State and persistence: creates a real FreeBSD mount at the target when successful; may perform cleanup unmounts during uncertain helper failures.

Dependencies and integration points: selected on FreeBSD; integrates with the same public `Mount.Mount` API as Linux. Depends on external `/sbin/mount` resolution through PATH and mountinfo lookup.

Risks: command-line escaping depends on `exec.Command` argument boundaries but option semantics are delegated to FreeBSD `mount(8)`. ECHILD retry logic may still leave ambiguous partial state if lookup/unmount fails.

Test signals: no FreeBSD-specific tests in this subset; Linux tests exercise analogous helper retry ideas for FUSE.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_freebsd.go -->

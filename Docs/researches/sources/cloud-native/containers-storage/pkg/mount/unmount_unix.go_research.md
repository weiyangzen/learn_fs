# sources/cloud-native/containers-storage/pkg/mount/unmount_unix.go

Purpose: implements Unix unmount with retry handling.

Important APIs, types, and functions: platform `unmount(target string, flags int) error`.

Control flow: tries `unix.Unmount` up to 50 times. On `EBUSY`, sleeps 50ms and retries. On `EINVAL` or nil, returns nil, treating not-mounted as success. Other errors break and are wrapped in `mountError`.

State and persistence: mutates the mount namespace by removing a mount. No package-level state.

Dependencies and integration points: depends on `time` and `golang.org/x/sys/unix`; called by `Unmount`, `ForceUnmount`, and recursive cleanup.

Risks and edge cases: `EINVAL` can also indicate invalid flags, but the code assumes flags are correct. Lazy detach semantics depend on the passed `mntDetach` constant. Worst-case retry takes about 2.5 seconds.

Test signals: exercised indirectly by Linux mount tests and shared-subtree tests during cleanup.

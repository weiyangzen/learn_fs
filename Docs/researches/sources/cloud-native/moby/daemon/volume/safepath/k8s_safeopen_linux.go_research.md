# sources/cloud-native/moby/daemon/volume/safepath/k8s_safeopen_linux.go

## Purpose
Fallback Linux safe-open implementation derived from Kubernetes subpath handling for kernels lacking `openat2`.

## Important APIs, Types, And Functions
`kubernetesSafeOpen(base, subpath string) (int, error)` opens a path component-by-component without following symlinks and returns an fd for the final target.

## Control Flow
The function opens the base with nofollow flags, splits the subpath, checks each current path remains local to base, triggers automounts with `fstatat` on a trailing slash, opens each child via `openat` with `O_NOFOLLOW|O_PATH`, stats it to reject symlinks, closes the previous parent fd, and returns the final fd without closing it.

## State And Persistence
No persistent state. It opens and closes fds; caller owns the returned fd.

## Dependencies And Integration Points
Used by `safeOpenFd` when `openat2` is unavailable. Depends on Unix no-EINTR wrappers and shared `isLocalTo`/typed errors.

## Risks
Correct fd cleanup on all error paths is subtle. It assumes resolved input from `evaluatePath` and disallows symlinks during traversal. Automount behavior may have host-specific effects.

## Test Signals
Covered indirectly by safepath join tests on systems where `openat2` is unavailable or by forcing fallback in lower-level tests outside this subset.

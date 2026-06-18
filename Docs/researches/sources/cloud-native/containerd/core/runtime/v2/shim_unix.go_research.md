# sources/cloud-native/containerd/core/runtime/v2/shim_unix.go

## Purpose
Provides non-Windows shim logging pipe behavior and default socket-directory selection.

## APIs, Flow, State, Dependencies, Risks, And Tests
`openShimLog` opens `bundle.Path/log` as a FIFO with read/write, create, and nonblocking flags. `checkCopyShimLogError` suppresses expected read-closed/closed errors only when the context has been canceled. `defaultSocketDir` chooses a short socket directory: root uses `/run/containerd/s`; non-root tries that, `$XDG_RUNTIME_DIR/containerd/s`, `/run/<uid>/containerd/s`, then `/tmp/containerd-s-<uid>`. `ensureSocketDir` creates a directory, verifies ownership, and normalizes mode to `0700`.

State changes are filesystem directory creation/chmod and FIFO creation. Dependencies include containerd defaults, fifo package, Unix syscalls, and user ownership checks.

Integration points are shim log copying and shim manager socket dir selection. Risks include failure to find a short owned directory, FIFO open semantics causing synchronization issues, and ignoring only the correct expected log-copy errors. Test signals include `TestCheckCopyShimLogError`, socket dir ownership/mode tests, and rootless startup integration.

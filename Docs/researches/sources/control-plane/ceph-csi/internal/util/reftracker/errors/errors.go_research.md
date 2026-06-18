<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/errors/errors.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/errors/errors.go

Purpose: centralizes reftracker error values and formatting helpers. The key exported sentinel is `ErrObjectOutOfDate`, used to represent failed RADOS `AssertVersion` optimistic-concurrency checks.

APIs and control flow: `UnexpectedReadSize`, `UnknownObjectVersion`, `FailedObjectRead`, and `FailedObjectWrite` wrap low-level errors with stable context. `TryRADOSAborted` inspects `rados.OperationError`, then an `ErrorCode()`-bearing operation error, mapping negative `EOVERFLOW` and `ERANGE` into `ErrObjectOutOfDate`; non-RADOS errors pass through, while unmatched RADOS operation errors return `nil`.

State and dependencies: no persistence. Depends on `github.com/ceph/go-ceph/rados` error shape and `golang.org/x/sys/unix` errno constants.

Integration points: called from v1 read/write paths to normalize stale-generation failures and from encoding parsers for length mismatch diagnostics.

Risks: `TryRADOSAborted` returning `nil` for unrecognized RADOS operation errno can suppress an underlying operation failure when wrapped through `FailedObjectRead/Write`. The comment above `FailedObjectWrite` incorrectly repeats `FailedObjectRead`.

Test signals: no direct test file in this subset, but v1 tests assert stale generation surfaces as `ErrObjectOutOfDate`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/errors/errors.go -->

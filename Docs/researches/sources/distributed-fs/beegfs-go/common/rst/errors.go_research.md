# sources/distributed-fs/beegfs-go/common/rst/errors.go

Purpose: defines RST sentinel errors and a timestamp-wrapping error used by job preparation and completion logic.

Important APIs are exported errors such as `ErrConfigRSTTypeNotSet`, `ErrReqAndRSTTypeMismatch`, `ErrUnsupportedOpForRST`, `ErrConfigUpdateNotAllowed`, `ErrJobAlreadyComplete`, `ErrJobAlreadyOffloaded`, precondition/open-file/stub-file errors, `IsErrJobTerminalSentinel`, `MtimeErr`, and `GetErrJobAlreadyCompleteWithMtime`.

Control flow is indirect. Provider implementations and builders wrap these sentinels to classify terminal no-op states, invalid configuration, unsupported request/provider combinations, lock/precondition failures, and remote unavailability. `MtimeErr` preserves the mtime associated with already-complete jobs while still unwrapping to the sentinel.

State is limited to package-level immutable errors and per-instance `MtimeErr` fields. Dependencies are `errors`, `fmt`, and `time`.

Integration points are BeeRemote job status mapping, CLI error reporting, file-state preparation, and tests that use `errors.Is`.

Risks: sentinel overload can hide context if wrappers are not descriptive. `IsErrJobTerminalSentinel` currently treats only already-complete/offloaded as terminal; adding new terminal states requires updating it. `MtimeErr.Error` uses `time.String`, not a stable RFC3339 format.

Test signals: S3 and store tests assert several sentinels; no dedicated tests for `MtimeErr`.

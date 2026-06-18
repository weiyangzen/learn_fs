<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/errdefs/exec.go -->
## sources/cloud-native/buildkit/solver/llbsolver/errdefs/exec.go

Purpose: wraps execution errors with references to input and mount results, ensuring borrowed refs can be released if the error is dropped.

Important APIs and types: `ExecError`, `WithExecError`, `WithExecErrorWithContext`, `EachRef`, and `Release`.

Control flow: constructor returns nil for nil errors, stores inputs/mounts, and installs a finalizer that warns and releases unreleased refs if ownership was not borrowed. `EachRef` deduplicates result pointers across inputs and mounts before invoking a callback. `Release` releases all refs once and marks `OwnerBorrowed`.

State and dependencies: holds in-memory result references and an ownership flag. It depends on solver `Result`, `context`, `runtime.SetFinalizer`, and BuildKit logging.

Integration points: exec op code can wrap errors so higher layers can include input/mount context and safely transfer result ownership.

Risks and test signals: finalizers are nondeterministic and should be a leak backstop, not normal control flow. Callers must call `Release` or intentionally borrow ownership. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/errdefs/exec.go -->

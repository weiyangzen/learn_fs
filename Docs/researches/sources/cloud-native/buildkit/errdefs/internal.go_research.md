# Research: sources/cloud-native/buildkit/errdefs/internal.go

Purpose: defines BuildKit's internal/system error marker and helpers for classifying syscall failures as internal or resource-exhaustion errors.

Important APIs and flow: `internalError` wraps an error and implements `System()`. `Internal` wraps non-nil errors. `IsInternal` returns true for errors implementing `System()` or syscall errno values known by `isInternalSyscall`. `IsResourceExhausted` returns true only for known syscall errors marked resource-exhaustion. `isInternalSyscall` delegates to platform-specific `syscallErrors`.

State and dependencies: no persistence. Depends on Go error wrapping/as semantics and syscall errno values supplied by OS-specific files.

Risks and test signals: classification affects retry/reporting semantics across BuildKit. Non-Linux builds return no syscall map, so only explicit internal wrappers match. There are no direct tests in this subset.

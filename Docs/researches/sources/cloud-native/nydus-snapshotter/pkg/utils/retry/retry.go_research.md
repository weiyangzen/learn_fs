<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/retry/retry.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/retry/retry.go

Purpose: implements configurable retry behavior with attempt count, delay strategy, jitter, max delay, retry predicates, callbacks, and optional last-error-only reporting.

Important APIs/types: `RetryableFunc`, `AbortFunc`, `OnRetryFunc`, `DelayTypeFunc`, `Config`, `Option`, option helpers (`Attempts`, `Delay`, `MaxDelay`, `MaxJitter`, `DelayType`, `OnRetry`, `OnlyRetryIf`, `LastErrorOnly`), delay strategies (`FixedDelay`, `RandomDelay`, `BackOffDelay`, `CombineDelay`), `Do`, aggregate `Error`, `Unrecoverable`, `IsRecoverable`, and `WrappedErrors`.

Control flow and state: `Do` builds defaults, applies options, repeatedly calls the function, stores unpacked errors, checks recoverability/predicate, invokes `onRetry`, sleeps unless on the last attempt, and returns either nil, the last error, or an aggregate `Error`. `Unrecoverable` wraps an error so default retry logic stops.

Dependencies/integration: pure standard-library utility used by mount wait logic and likely other transient operations.

Risks and test signals: no direct tests in this subset. `RandomDelay` panics if `maxJitter` is zero because `rand.Int63n(0)` is invalid. `BackOffDelay` can overflow for large attempt numbers. `Error.Error` allocates a slice sized by non-nil count but indexes by original position, which can panic if nil holes precede later errors; current `Do` usually fills sequentially but future callers of `Error` could trigger it.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/retry/retry.go -->

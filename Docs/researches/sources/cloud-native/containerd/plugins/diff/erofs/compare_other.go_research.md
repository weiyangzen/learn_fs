# sources/cloud-native/containerd/plugins/diff/erofs/compare_other.go

## Purpose
Provides the non-Linux implementation of EROFS `Compare`, returning not implemented.

## Important APIs, Types, And Functions
`erofsDiff.Compare` matches the Linux method signature but returns `emptyDesc` and `errdefs.ErrNotImplemented`.

## Control Flow
The method performs no inspection and immediately delegates fallback selection to callers that understand `ErrNotImplemented`.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
Compiled under `!linux`. It integrates with the diff service fallback chain, allowing other differs such as walking to handle comparisons on unsupported platforms.

## Risks
Callers must check `errdefs.IsNotImplemented`; treating the error as fatal can disable otherwise valid fallback differs.

## Test Signals
No direct tests. Platform build coverage ensures signature compatibility.

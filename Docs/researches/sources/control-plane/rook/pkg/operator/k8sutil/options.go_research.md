# sources/control-plane/rook/pkg/operator/k8sutil/options.go

## Purpose
`options.go` defines reusable wait/retry options for Kubernetes utility operations.

## Important APIs, Types, and Functions
`WaitOptions` carries `Wait`, `RetryCount`, `RetryInterval`, and `ErrorOnTimeout`. The unexported methods `retryCountOrDefault()` and `retryIntervalOrDefault()` select explicit values or caller-provided defaults.

## Control Flow, State, and Persistence
The struct is pure in-memory configuration. No function performs waiting itself; consumers decide how to apply these values.

## Dependencies and Integration Points
The only dependency is `time.Duration`. Delete/update helpers elsewhere in `k8sutil` can accept or compose these options to control polling behavior.

## Risks
The defaulting methods have pointer receivers and will panic if called on a nil `*WaitOptions`. Callers must guard nil options before defaulting. Because the type does not enforce valid combinations, `Wait=false` with retry fields set is possible.

## Test Signals
No direct test file is mapped for this source. Useful tests would cover defaulting, zero values, nil-option handling by callers, and timeout behavior in consumers.

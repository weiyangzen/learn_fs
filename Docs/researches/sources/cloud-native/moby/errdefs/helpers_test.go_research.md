# sources/cloud-native/moby/errdefs/helpers_test.go

## Purpose
Unit tests for all errdefs wrapper constructors.

## Important APIs and Types
Defines `errTest`, a local `wrapped` interface, and tests for each class constructor.

## Control Flow, State, and Persistence
Each test starts with a plain error that should not satisfy the containerd predicate, wraps it with the Moby helper, verifies the corresponding containerd `Is...` predicate, checks `Unwrap` returns the original error, checks `errors.Is`, then wraps again with `fmt.Errorf("%w")` to verify causal-chain classification.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on standard `errors`, `fmt`, `testing`, and containerd errdefs. It is strong compatibility coverage for cross-package error classification. It does not directly test nil passthrough, already-classified passthrough, or `FromContext`; those remain residual test gaps.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_test.go -->
# sources/cloud-native/containerd/pkg/shim/util_test.go

## Purpose
Tests ttrpc unary interceptor chaining helper.

## Important APIs, Types, And Functions
TestChainUnaryServerInterceptors constructs two interceptors and a method, validating context propagation, info propagation, and unmarshal wrapping order.

## Control Flow
The chained interceptor calls first, then second, then method; each layer checks expected context values and numeric transformations.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Exercises chainUnaryServerInterceptors in util.go and ttrpc function signatures.

## Risks And Edge Cases
A regression in order or unmarshal wrapping would change expected numeric results and fail the test.

## Test Signals
Direct high-signal unit test for interceptor composition.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_test.go -->

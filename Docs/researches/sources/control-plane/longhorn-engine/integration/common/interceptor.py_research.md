# sources/control-plane/longhorn-engine/integration/common/interceptor.py

## Purpose
Defines a Python gRPC unary-unary client interceptor that injects Longhorn identity metadata (`volume-name`, `instance-name`) into outgoing requests.

## Important APIs, Types, and Functions
- `_ClientCallDetails` namedtuple implementing `grpc.ClientCallDetails`.
- `IdentityValidationInterceptor` with `intercept_unary_unary`.

## Control Flow
For each unary request, existing metadata is copied, optional volume and instance metadata are appended, a new `_ClientCallDetails` is built, and continuation is invoked with the original request.

## State and Persistence Behavior
No persistence. It affects request metadata used by server-side identity validation.

## Dependencies and Integration Points
Used by generated or wrapper clients in integration tests to exercise identity validation. Mirrors Go-side identity validation used by CLI clients.

## Risks and Edge Cases
`next(iter((request,)))` is an unusual way to pass the request but returns the original object. Only unary-unary RPCs are intercepted; streaming calls would need other interceptors.

## Test Signals
`integration/core/test_identity.py` validates volume and instance mismatch failures across controller, replica, sync-agent, and CLI paths.

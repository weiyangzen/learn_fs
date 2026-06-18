# sources/control-plane/csi-driver-host-path/internal/proxy/proxy_test.go

## Purpose
This test file verifies the two-listener proxy can move bytes bidirectionally over Unix sockets and propagates connection closure.

## Important APIs, Types, And Functions
`TestProxy` creates a temp directory, starts `Run(ctx, a.sock, b.sock)`, and runs subtests `a-to-b` and `b-to-a`. `sendReceive` dials both endpoints, writes `ping` one way and `pong-pong` the other way, then closes one side and expects EOF on the other.

## Control Flow
Each subtest establishes a paired connection by dialing both endpoints. It performs request/response reads with fixed buffers, validates exact payload strings, closes the first connection, drains the second with `io.Copy`, and asserts no extra bytes arrived.

## State, Persistence, And Dependencies
The test uses temporary Unix socket files that are removed through proxy cleanup and `t.TempDir`. It depends on local Unix socket support and Go testing.

## Integration Points
It validates the behavior relied on by any test deployment or process that uses the proxy instead of socat to bridge CSI endpoints.

## Risks
The test covers only one connection pair at a time and only small payloads. It does not exercise TCP endpoints, cancellation while accepting, listener startup failures, or concurrent clients.

## Test Signals
Passing tests show basic pair establishment, bidirectional data movement, and EOF propagation. Failures usually indicate endpoint cleanup, accept ordering, or copy/close behavior regressions.

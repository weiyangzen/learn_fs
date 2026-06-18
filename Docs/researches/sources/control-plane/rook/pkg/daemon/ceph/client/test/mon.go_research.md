# sources/control-plane/rook/pkg/daemon/ceph/client/test/mon.go

This helper file generates JSON monitor-status responses for tests that need monitors in quorum. It keeps monitor fixtures near the client package while avoiding dependency cycles.

`MonInQuorumResponse()` returns a `client.MonStatusResponse` with one monitor named `a`, rank `0`, address `1.2.3.1`, and quorum `[0]`. `MonInQuorumResponseFromMons()` builds a response from a map of `MonInfo`, assigning incrementing ranks and quorum entries while deriving addresses from the loop index. `MonInQuorumResponseMany()` creates a response with monitors named `rook-ceph-monN`; it loops from zero through `count`, so it returns `count+1` monitor entries while quorum contains only rank `0`.

State is generated JSON only. Dependencies are `encoding/json`, `fmt`, and Ceph client monitor types. Integration points are monitor quorum tests and reconciliation code that parse `MonStatusResponse`.

Risks include nondeterministic map iteration order in `MonInQuorumResponseFromMons()` and the off-by-one-looking inclusive loop in `MonInQuorumResponseMany()`. Serialization errors are ignored because fixtures are built from marshalable structs. There are no direct tests here; value comes from consumers that parse the generated JSON.

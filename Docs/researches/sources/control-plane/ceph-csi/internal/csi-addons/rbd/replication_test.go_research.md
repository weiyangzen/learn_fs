# sources/control-plane/ceph-csi/internal/csi-addons/rbd/replication_test.go

Purpose: unit tests for helper logic that supports the RBD CSI-addons replication state machine.

Important APIs/types/functions: tests `validateSchedulingInterval()`, `validateSchedulingDetails()`, `getSchedulingDetails()`, `checkVolumeResyncStatus()`, `checkRemoteSiteStatus()`, `getGRPCError()`, `timestampFromString()`, `getFlattenMode()`, and `getCurrentReplicationStatus()`.

Control flow: schedule tests validate `m/h/d` suffixes, snapshot/journal mode behavior, optional start time rules, and default extraction. Resync status tests feed sample go-ceph status descriptions with present/zero/missing local snapshot timestamps. Remote readiness checks local/remote site states and `Up` flags. Error tests validate sentinel-to-gRPC code mapping. Timestamp tests validate round-trip and malformed strings. Status tests map local mirror state/up flags into CSI-addons `HEALTHY`, `DEGRADED`, `ERROR`, or `UNKNOWN` with messages.

State and persistence: pure in-memory fixtures, though time tests use current time values.

Dependencies and integration points: protects behavior that external replication operators depend on for retry/readiness/status decisions.

Risks: no tests exercise the actual RPC methods or RBD manager/mirror calls. Time round-trip compares `time.Time` values including monotonic behavior through `Equal`, which is normally fine but should remain watched if timestamp formatting changes. There is an expected `getGRPCError(nil)` oddity.

Test signals: strong helper coverage for parsing and mapping; missing integration coverage for real mirroring transitions.

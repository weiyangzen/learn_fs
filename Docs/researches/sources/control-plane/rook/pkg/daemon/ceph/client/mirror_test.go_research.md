# sources/control-plane/rook/pkg/daemon/ceph/client/mirror_test.go

Purpose: validates RBD mirroring command construction, status/info parsing, snapshot schedule operations, and peer lifecycle helpers.

Important test cases: tests cover bootstrap peer creation, enabling pool mirroring, reading pool mirroring status and verbose mirrored images, importing bootstrap peers with and without direction, reading mirror info, adding snapshot schedules with optional start time, listing schedules flat and recursively, removing schedules, resetting schedules, disabling mirroring, and removing peers. JSON fixtures such as `mirrorStatus`, `mirrorInfo`, schedule lists, and bootstrap token data drive parsing checks.

Control flow and dependencies: tests use mock executors and assert command-specific args before appended standard flags. They use `cephv1.NamedPoolSpec`/`PoolSpec` for mirror mode and snapshot schedule inputs. Import tests account for the generated temp token path by checking arg length and relative positions rather than exact path.

Risks and coverage gaps: this file gives strong coverage for the central pool mirroring paths, but does not cover Multus remote token copy/cleanup, temp-file write failures, `init-only` version gate, namespace mirroring enable/disable, cluster-wide bootstrap token creation/rotation, schedule reset behavior after list errors, malformed JSON, or status backward compatibility details beyond basic parsing.

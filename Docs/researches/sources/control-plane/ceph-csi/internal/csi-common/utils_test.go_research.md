# sources/control-plane/ceph-csi/internal/csi-common/utils_test.go

Purpose: unit and lightweight integration tests for common CSI utility helpers.

Important APIs/types/functions: tests include `TestGetReqID()`, `TestFilesystemNodeGetVolumeStats()`, `TestRequirePositive()`, `TestIsBlockMultiNode()`, `TestIsFileRWO()`, `TestIsBlockMultiWriter()`, `TestIsReaderOnly()`, and slow-GRPC tests for `killOnSlowGRPCWithThreshold()`.

Control flow: request ID tests construct many CSI, replication, and replication-source protobuf requests and assert `getReqID()` returns the expected fake ID or empty string. Filesystem stats walks up from the package working directory until it finds a mountpoint, then validates byte/inode usage. Access-mode tests build block and mount capabilities for single/multi node, reader, writer, and multi-writer modes. Slow-GRPC tests override package `osExit`, exercise fast/error/stuck handlers, and verify `/reclaimspace.` prefixes do not trigger exit.

State and persistence: mostly in-memory. Filesystem stats reads the local mounted filesystem. Slow-GRPC tests mutate `osExit` and intentionally avoid parallel execution for those cases.

Dependencies and integration points: protects middleware request labeling, node stats, RBD reclaim capability gating, CephFS read-only helpers, and process-restart safeguards.

Risks: filesystem stat test depends on the test environment having a discoverable mountpoint. Access helper tests do not cover nil access modes for every helper. Slow-GRPC stuck-handler test uses timing and goroutines, so thresholds need enough slack to avoid flakiness.

Test signals: strong regression signal for common helpers with careful non-parallel tests around global state.

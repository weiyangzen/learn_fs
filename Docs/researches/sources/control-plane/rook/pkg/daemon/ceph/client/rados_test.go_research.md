# sources/control-plane/rook/pkg/daemon/ceph/client/rados_test.go

This file tests `RadosRemoveObject()` using the mock executor and a minimal cluster context. It verifies the intended idempotent object deletion contract without requiring a real RADOS cluster.

`TestRadosRemoveObject` defines a helper that creates a `clusterd.Context` and `ClusterInfo`, then runs four subtests. The timeout case returns a fake timeout from the initial `stat` and asserts the wrapped error is still detectable by `exec.IsTimeout`. The stat-error case asserts that any non-timeout stat failure is treated as "already gone" and returns nil. The remove-error case makes `stat` succeed and `rm` fail, proving delete failures are returned. The success case verifies both `stat` and `rm` commands run with `--pool`, `--namespace`, and object name in the expected positions.

State is only mocked command state. The test integrates with Rook's executor test package and timeout classification helper. It does not cover object locking, namespace listing, shell piping, or JSON lock parsing. The main risk captured is preserving idempotency while still distinguishing timeout failures from absence-like stat failures.

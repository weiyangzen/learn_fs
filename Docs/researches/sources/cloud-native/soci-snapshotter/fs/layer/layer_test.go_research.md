# sources/cloud-native/soci-snapshotter/fs/layer/layer_test.go

Purpose: groups high-level layer node tests and includes a small condition-variable waiter regression test.

Important APIs and flow: `TestLayer` delegates to shared helpers `testNodeRead`, `testExistence`, and `testStatfs` using `metadata.NewTempDbStore`, thereby exercising file reads, whiteout/opaque/xattr handling, state files, modes, symlink sizes, and statfs behavior through layer node construction. `TestWaiter` defines a local `waiter`, starts a goroutine waiting on a condition, sleeps, calls `done`, and asserts the wait did not return early.

State and persistence: helper tests create temporary metadata DB stores and synthetic gzip/tar ztoc readers. The local waiter uses memory synchronization only.

Dependencies and integration: relies heavily on `util_test.go` helpers and the node implementation. It indirectly validates `reader.NewReader`, span manager reads, FUSE node operations, and metadata store behavior.

Risks and test signals: strong signal for node-facing layer behavior, but little direct coverage of `Resolver.Resolve`, blob/layer LRU caches, background fetch queueing, or prefetch artifacts. The local waiter test is self-contained and not connected to production code in this file.

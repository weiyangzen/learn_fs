## sources/cloud-native/stargz-snapshotter/fs/layer/layer_test.go

Purpose: entry point for the shared layer test suite and a direct test of the prefetch waiter primitive.

Important APIs and helpers: `TestLayer` wraps `testing.T` in the local `TestRunner` and runs `TestSuiteLayer` with `memorymetadata.NewReader`. `TestWaiter` constructs `newWaiter`, launches a goroutine waiting with a long timeout, sleeps one second, calls `done`, and verifies wait did not return too early.

Control flow: the layer suite itself is implemented in `testutil.go` and runs prefetch, node read, and node behavior tests across default and passthrough configurations. `TestWaiter` directly exercises channel closure and `sync.Once` behavior.

State and persistence: no persistent state. Test suite creates in-memory metadata/cache and temporary synthetic blobs through helper code.

Dependencies and integration points: depends on `metadata/memory` as the metadata store under test and package-local layer helpers. It indirectly integrates estargz test tar builders and compression variants through `testutil.go`.

Risks: `TestWaiter` only tests the success path where `done` fires before timeout; it does not test timeout behavior or idempotent repeated `done`. `TestLayer` coverage depends entirely on shared helper breadth.

Test signals: good smoke signal that the memory metadata backend satisfies layer expectations; direct waiter test catches premature wakeups but not timeout edge cases.

# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/fakeserver_test.go

Purpose: validates the lifecycle fake server used by component tests.

Important tests: default outcome is DONE; queued outcomes pop FIFO and then default applies; queues are isolated by bucket/object/version; delimiter-containing key components do not collide because map key is a struct; transport errors short-circuit before recording and can be cleared; recorded requests preserve order; recorded slices and requests are deep copies; nil requests use default; concurrent calls complete without errors and record all requests.

Control flow/state: tests mutate fake queues, default, error state, and recorded snapshots to confirm locking and copy boundaries. Concurrency test uses 64 goroutines.

Dependencies/integration: uses lifecycle protobuf outcomes and requests plus testify.

Risks/gaps: concurrent test checks completion and length, with race detector needed to prove absence of data races. It does not assert deterministic order under concurrency, which is appropriate.

Test signals: strong confidence that tests using this fake can model dispatcher outcomes, transport failures, blocked/retry paths, and request recording without cross-test contamination.

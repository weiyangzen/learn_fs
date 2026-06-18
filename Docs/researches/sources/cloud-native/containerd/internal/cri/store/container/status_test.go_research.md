# Research: sources/cloud-native/containerd/internal/cri/store/container/status_test.go

This test file validates container status state derivation, serialization, checkpoint persistence, transactional updates, deletion, and deep-copy behavior. `TestDeepCopyOfWindowsAffinityCpus` ensures Windows CPU affinity slices are copied without nil entries and mutations to the returned copy do not affect the original. `TestContainerState` verifies unknown, created, running, and exited state derivation from flags and timestamps.

`TestStatusEncodeDecode` confirms status JSON wrapping round-trips persistent fields while transient `Removing`, `Starting`, and `Unknown` are not encoded, and unsupported versions fail. `TestStatus` uses a temp directory to store the checkpoint, load it back, verify failed `Update` and `UpdateSync` roll back, verify memory-only `Update` does not change the on-disk checkpoint, verify `UpdateSync` does, confirm previously returned snapshots are immutable, and check idempotent deletion removes the status file.

The tests give strong signal for persistence correctness and transaction boundaries. They do not cover concurrent updates, every resource field, filesystem rename failure modes, or migration from old status versions. They guard the most important risk: divergence between in-memory status and checkpointed status must be intentional and predictable.

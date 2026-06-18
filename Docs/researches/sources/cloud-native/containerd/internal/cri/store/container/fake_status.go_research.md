# Research: sources/cloud-native/containerd/internal/cri/store/container/fake_status.go

This test helper supplies an in-memory `StatusStorage` implementation for container tests. `WithFakeStatus` is a `Container` option that installs `fakeStatusStorage` and closes the container stop channel when the fake status has `FinishedAt` set, simulating a task-exit event for exited containers.

`fakeStatusStorage` stores a `Status` protected by an RW mutex. `Get` returns the current status value. `UpdateSync` delegates to `Update` instead of writing any checkpoint. `Update` applies the supplied transactional `UpdateFunc`, leaves the old status unchanged on error, and stores the new status on success. `Delete` is a no-op returning nil.

There is no disk persistence, which is the point: tests can construct containers without temp checkpoint directories. The helper integrates with `NewContainer` options and any server/store tests that need status behavior without persistence. Risks are test fidelity gaps: `UpdateSync` does not exercise atomic file writes, `Get` does not deep-copy pointer fields like production status storage, and `Delete` never fails. It is used by container, sandbox stats, and service tests to model running/exited/failed containers.

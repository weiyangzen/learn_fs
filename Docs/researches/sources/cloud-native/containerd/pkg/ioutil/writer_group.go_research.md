# sources/cloud-native/containerd/pkg/ioutil/writer_group.go

Purpose: fan-out writer registry keyed by string. It lets callers add, retrieve, remove, write to all, and close all registered `io.WriteCloser`s safely under a mutex.

Important APIs/types/functions: `WriterGroup` stores `writers map[string]io.WriteCloser` and `closed bool`. `NewWriterGroup` initializes the map. `Add` replaces an existing writer and closes the replaced one, or immediately closes the new writer if the group is already closed. `Get` returns the current writer. `Remove` deletes and closes a writer. `Write` writes to every registered writer, accumulating the first error and returning the input length on success. `Close` closes all writers and marks the group closed.

Control flow: all public methods take the mutex. Writes are sequential across registered writers while holding the lock, so add/remove/close cannot race with fan-out writes.

State/persistence: in-memory registry; persistence is owned by underlying writers.

Dependencies/integration: generic I/O helper for broadcasting output streams.

Risks: holding the mutex during slow or blocking writes can block management operations. `Close` ignores close errors. `Write` returns after attempting all writers but only preserves the first error.

Test signals: `writer_group_test.go` covers empty, closed, add/get/remove, replacement, write fan-out, and close behavior.

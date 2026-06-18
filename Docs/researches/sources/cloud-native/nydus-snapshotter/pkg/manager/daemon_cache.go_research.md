# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_cache.go

This file implements the manager's in-memory daemon index. `DaemonCache` holds a mutex and a map from daemon ID to `*daemon.Daemon`. `Add` inserts or replaces and returns the previous pointer, `Remove` and `RemoveByDaemonID` delete entries, `Update` logs recovery and replaces the entry, `GetByDaemonID` optionally runs a callback while holding the lock, `List` returns a slice snapshot, and `Size` returns map length.

State is entirely in memory but mirrors the persistent store managed by `Manager`. The manager's comments require store updates before cache modifications, making this cache a performance and coordination layer rather than source of truth. It is used by daemon lookup, recovery, teardown, metrics server manager walks, and filesystem daemon selection.

Risks include callbacks running under the cache lock, `List` returning daemon pointers whose internals may still need their own locks, replacement behavior masking accidental duplicate daemon IDs if used outside `Manager.AddDaemon`, and no ordering guarantee from map iteration. Tests cover add/get/list/size/remove/update basics but not concurrent access or callback mutation.

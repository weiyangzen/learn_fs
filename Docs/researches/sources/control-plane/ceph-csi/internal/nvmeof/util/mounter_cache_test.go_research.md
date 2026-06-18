# sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_cache_test.go

Purpose: Unit tests for `MountCache` correctness and basic concurrency safety.

Important APIs/types/functions: Tests `NewMountCache`, `Add`, `GetDevice`, `RemoveByDevice`, `RemoveByMountPoint`, and duplicate-device overwrite prevention.

Control flow: Tests add mappings, retrieve them, remove by both directions, attempt removals from empty or missing entries, spawn concurrent add goroutines, and verify that adding a second staging path for the same device is ignored.

State and persistence behavior: All state is in-memory cache state. No external dependencies.

Dependencies and integration points: Uses `testify/require`. These tests support confidence in node server disconnect decisions that depend on cache consistency.

Risks: Concurrency test only covers concurrent adds with unique keys and does not run under explicit race detector here. It does not test concurrent add/remove/read interleavings.

Test signals: Strong signal for intended 1:1 semantics and basic locking behavior.

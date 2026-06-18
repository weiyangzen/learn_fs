<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/leasemanager.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/leasemanager.go

Purpose: wraps a containerd lease manager to tie BuildKit snapshot lease resources to the custom graphdriver snapshotter lifecycle.

Important APIs and control flow: `sLM` delegates create/list/resource operations to the underlying lease manager while tracking `snapshots/default` resources in `byLease` and `bySnapshot` maps. `Delete` removes all tracked refs for a lease after deleting the underlying lease. `AddResource`/`DeleteResource` update tracking. `addRef` optionally loads the snapshot layer and records chain metadata. `delRef` removes reverse refs and removes snapshots when no leases remain.

State and persistence: mutates underlying lease metadata, in-memory ref maps, snapshotter refs, and snapshot Bolt metadata.

Dependencies and integration: created by `NewSnapshotter` and wrapped with a namespace via BuildKit lease utilities. It controls when graphdriver snapshots can be cleaned up.

Risks: the map handling in `addRef`/`delRef` is delicate because lease and snapshot reverse maps must stay symmetric. Silent warnings on failed snapshot removal can leave graphdriver data. This code is central to preventing premature layer removal and storage leaks.

Test signals: no direct tests in this subset; lease lifecycle is covered indirectly through BuildKit cache prune and build cleanup tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/leasemanager.go -->

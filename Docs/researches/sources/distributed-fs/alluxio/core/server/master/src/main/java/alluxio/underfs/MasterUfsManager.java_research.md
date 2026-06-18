# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/underfs/MasterUfsManager.java

Purpose: master-side UFS manager that tracks mounted UFS roots and journaled physical UFS operation modes.

Important APIs/types/functions: extends `AbstractUfsManager` and implements `DelegatingJournaled`; `connectUfs`, `addMount`, `addMountWithRecorder`, `removeMount`, `hasMount`, `getPhysicalUfsState`, `setUfsMode`, `getDelegate`, `getJournalEntryIterator`, and nested `State`.

Control flow: mounting delegates to the abstract manager, then records the root URI and mount-id-to-root mapping. `setUfsMode` validates the root is managed, then applies and journals an `UpdateUfsModeEntry`. The nested state processes only `updateUfsMode` journal entries and emits one entry per stored mode during checkpoint iteration.

State and persistence: synchronized outer maps track managed roots and mount ids. Nested `State` persists `mUfsModes` through journal/checkpoint name `MASTER_UFS_MANAGER`. Default mode is `READ_WRITE` when no state exists for a root.

Dependencies/integration: used in `CoreMasterContext` and mount-table flows. `connectUfs` connects from the master RPC host using `NetworkAddressUtils`. Physical mode state informs file-system master behavior for reads/writes against UFS mounts.

Risks: removing a mount does not remove its root from `mUfsRoots`, so a removed physical root may remain accepted for mode updates if another mapping is absent. Journal state is separate from currently mounted IDs, so replayed modes can exist for roots not currently mounted.

Test signals: add/remove/hasMount, unknown-root rejection in `setUfsMode`, journal replay/checkpoint of modes, default read-write mode, and physical store state for multiple URIs sharing roots.

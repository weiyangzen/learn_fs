# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/UnifiedInodeProvider.cc

Purpose: Implements a facade that allocates file and container IDs either from separate counters or from one shared inode stream.
Important APIs/types/functions: `configure`, `reserveFileId`, `reserveContainerId`, blacklist methods, and first-free peeks for both ID classes.
Control flow: `configure()` reads `constants::sUseSharedInodes` from the metadata map. If `"yes"`, only the file provider is configured and both file/container operations route through it; otherwise, file and container providers use `sLastUsedFid` and `sLastUsedCid`.
State/persistence: holds a non-owning `QHash*`, `mSharedInodes`, and unique pointers to `NextInodeProvider`s. Persistent high-water marks remain in the QDB hash fields managed by those providers.
Dependencies/integration: wraps `NextInodeProvider`, `qclient::QHash`, and namespace constants; used by metadata services that create new files/containers.
Risks: no synchronization around `configure()` or shared flag; callers must configure before reservation; shared-inode mode changes the semantic coupling of file and container IDs and must match cluster metadata.
Test signals: `HierarchicalViewTest.CustomContainerId` and `CustomFileId` indirectly validate counter advancement after explicit IDs; `NextInodeProviderTest` covers the underlying allocator.

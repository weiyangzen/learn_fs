# sources/distributed-fs/coda/coda-src/vol/recovc.cc

Purpose: handles first-time RVM initialization, recoverable volume/vnode metadata checks, volume id allocation, vnode-list growth, and volume-disk-info extraction.

Important APIs: `coda_init`, `CheckVolData`, `ActiveVnodes`, `AllocatedVnodes`, `GetVolPartition`, `VAllocateVolumeId`, `VGetMaxVolumeId`, `VSetMaxVolumeId`, `GrowVnodes`, `ExtractVolDiskInfo`, and `AvailVnode`. `coda_init` initializes `MaxVolId` from `ThisServerId << 24`, old-compatible vnode free-list metadata, and a VM counter used by resolution store ids.

Control flow/state: `GrowVnodes` allocates a larger `rec_smolist` array, zeros the new tail, copies old entries, frees the old array, and updates the RVM pointer and count. `ExtractVolDiskInfo` copies disk info and validates stamp magic/version. `AvailVnode` distinguishes whole-slot emptiness from absence of a particular uniquifier.

Dependencies/integration: depends on `rvmlib`, Coda globals, volume/vnode types, and the volume-id hash. It is called during volume package init, bitmap growth, volume attach, and fid allocation. Risks include fatal exit when `ThisServerId` is unset, grow-by-copy transaction correctness, assumptions about `MaxVolId & 0x00FFFFFF`, and old free-list compatibility fields. Test signals: fresh RVM initialization, max-id overflow, grow small/large vnode arrays, invalid volume index checks, and `AvailVnode` for multi-uniquifier slots.

# sources/distributed-fs/coda/coda-src/vol/recovb.cc

Purpose: implements vnode and volume-disk-info accessors over recoverable storage.

Important APIs: `ExtractVnode`, `ObjectExists`, `GetParentFid`, `ReplaceVnode`, `NewVolDiskInfo`, `VolDiskInfoById`, `ReplaceVolDiskInfo`, and `FindVnode`. Private `DeleteVnode` removes a single recoverable vnode. `ReplaceVnode` allocates a new `VnodeDiskObject` when a uniquifier is not present, appends it to the class-local `rec_smolist`, increments small/large vnode counts, and writes the disk object. A `vNull` object triggers deletion.

Control flow/state: all lookups validate volume index and class-local slot bounds, select small or large vnode lists, then find entries by uniquifier. Parent fid derivation special-cases root large vnodes whose parent uniquifier is zero. Disk info writes validate version stamps and copy the full `VolumeDiskData` into RVM.

Dependencies/integration: used by vnode cache writeback, index wrappers, dump/debug, resolution, and volume creation. Risks include direct memcpy of fixed vnode sizes, reliance on unique `uniquifier` within each slot list, off-by-one style checks using `> MAXVOLS`, hard assertions on disk-info stamps, and missing concurrency protection outside transaction discipline. Test signals: replace existing vnode, allocate first vnode in a slot, delete vnode with `vNull`, root parent lookup, stale uniquifier lookup, and volume disk-info stamp corruption.

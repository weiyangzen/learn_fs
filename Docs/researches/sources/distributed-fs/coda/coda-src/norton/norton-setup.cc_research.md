# sources/distributed-fs/coda/coda-src/norton/norton-setup.cc

Purpose: initializes enough of the Coda server runtime for Norton tools to inspect and mutate recoverable storage without starting the full server.

APIs and flow: `LoadRVM` verifies log/data devices, initializes per-thread rvmlib data, configures RVM options including optional private mapping, runs `RVM_INIT`, and loads the RDS heap. `InitLWP` initializes LWP and IOMGR. `NortonInitVolPackage` initializes server list, LRU, volume table, and vnode classes. `NortonInit` refuses to run while `/vice/srv/pid` exists, initializes LWP/RVM/directory cache, marks program type as salvager, and starts the volume package subset.

State/dependencies: sets globals `norton_debug`, `mapprivate`, and `camlibRecoverableSegment`. Depends on RVM/RDS, LWP, codadir, volume, partition, and parser infrastructure. Risks include hard-coded `/vice`, abrupt exits, and partial runtime initialization assumptions.

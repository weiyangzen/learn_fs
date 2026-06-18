# sources/distributed-fs/coda/coda-src/norton/norton-recov.cc

Purpose: provides thin accessors from Norton code to recoverable server volume storage.

APIs: `GetMaxVolId` masks `SRV_RVM(MaxVolId)` to 24 bits. `VolByIndex` bounds-checks an index against max ID and `MAXVOLS`, then returns `SRV_RVM(VolumeList[index])`. `VolHeaderByIndex` returns the embedded header for a valid volume.

State/dependencies: reads RVM-mapped globals initialized by `NortonInit`. Risks are stale/corrupt RVM data and reliance on magic checks by callers. Test signal is all volume/vnode commands that enumerate by index.

# sources/distributed-fs/coda/coda-src/librepair/resolve.cc

Purpose: bridges Coda conflict replicas on disk with the resolution subsystem. It reads replica directories, gathers FIDs/version vectors/ACLs, groups entries by name and FID, classifies conflicts through predicate functions, and builds per-replica repair operation lists.

APIs and flow: `res_getfid`/`res_getmtptfid` call Venus pioctls, with symlink fallback for conflict roots. `getunixdirreps` walks replica directories into global `direntriesarr` and fills `resreplica` headers. `dirresolve` first handles name/name conflicts interactively or from a fixed directory, then sorts by FID/name and calls predicate/repair functions. `InitListHdr`, `InsertListHdr`, `InRepairList`, and `IsCreatedEarlier` maintain repair lists. `GetParent` maps child FIDs to parent path/FID via pioctls.

State and risks: uses process globals for directory entries, sorted arrays, total counts, and conflict count, so it is not reentrant. Memory ownership is manual; `InsertListHdr` leaks old repair arrays, and `resClean` skips freeing `lh[0].repairList`. Path assembly assumes replica paths and slash layout. Dependencies include Venus ioctls, `predicate.h`, `cure.h`, `repio.h`, ACL parsing, and parser prompts. Test signal is `restest.cc` plus repair integration.

# sources/distributed-fs/coda/coda-src/resolution/weres.cc

Purpose: subordinate handler for weakly-equal resolution. It forces a vnode's version vector forward to a coordinator-provided vector when the local vector is equal or strictly subsumed.

Important function: `RS_ForceVV` validates caller connection info, translates the VSG fid, gets the object with a write lock, verifies the volume is locked by the coordinator's host, compares local and target version vectors, applies the difference to both vnode and volume vectors when local is a subset, clears COP2 pending, optionally updates status fields from `ViceStatus`, breaks callbacks, and releases objects inside an RVM transaction.

Control flow and persistence: incompatible or dominating local vectors return `EINCOMPATIBLE`; equal vectors are effectively a no-op except possible COP2/status cleanup. Successful subset advancement mutates persistent vnode/volume version vectors and callback state.

Dependencies, risks, tests: depends on lock ownership, version-vector arithmetic (`SubVVs`, `AddVVs`), callback invalidation, RVM transaction release, and optional status propagation. Risks include strict coordinator lock requirement, updating metadata when `statusp->Date` is used as validity flag, and assertion on vnode release failures. Test equal, subset, dominating, and incomparable vectors; COP2 pending clear; coordinator mismatch; and status metadata update.

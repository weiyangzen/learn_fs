# sources/distributed-fs/coda/coda-src/resolution/subpreres.cc

Purpose: subordinate-side pre-resolution helpers used around repair and inconsistency cleanup. It fetches directory contents after repair and clears inconsistency flags when coordinator-supplied version vectors match.

Important functions: `RS_FetchDirContents` translates the VSG fid, obtains the directory with a read lock, packages directory data plus ACL via `Dir_n_ACL`, sends it through RPC2 SmartFTP `FILEINVM`, returns length and `ViceStatus`, then releases objects inside an RVM transaction. `RS_ClearIncon` validates the calling connection, translates the fid, gets the object with a write lock, verifies the volume lock belongs to the coordinator's remote host, compares version vectors ignoring inconsistency bits, clears the inconsistency flag, and breaks callbacks.

Control flow and persistence: both functions use `GetFsObj`/`VPutVnode`/`PutVolObj`. `RS_ClearIncon` mutates persistent vnode version-vector flags inside RVM recovery transaction boundaries when locks are released. `RS_FetchDirContents` mostly reads state but still releases handles inside a transaction.

Dependencies, risks, tests: depends on RPC2 side effects, `rvmlib`, `srv`, `volume`, `resutil`, and lock ownership. Risks include returning `EINVAL` for many setup failures, assuming side-effect buffers remain valid until transfer completes, and clearing inconsistency only under exact vector compatibility. Test with successful directory fetch, side-effect failures, coordinator mismatch, incompatible VV, and callback invalidation after clear.

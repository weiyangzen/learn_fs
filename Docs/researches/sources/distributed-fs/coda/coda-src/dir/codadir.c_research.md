# sources/distributed-fs/coda/coda-src/dir/codadir.c

## Purpose
Thread-safe `DirHandle` wrapper around low-level `DIR_*` directory-body functions. It handles locking, dirty marking, RVM/VM allocation, and ViceFid/DirFid conversion.

## APIs, Types, and Functions
Exports lock helpers `DH_LockW/R()` and `DH_UnLockW/R()`, lifecycle helpers `DH_Init()`, `DH_Alloc()`, `DH_FreeData()`, `DH_Data()`, and operation wrappers `DH_Length()`, `DH_Convert()`, `DH_Create()`, `DH_IsEmpty()`, `DH_Lookup()`, `DH_LookupByFid()`, `DH_Delete()`, `DH_Print()`, `DH_DirOK()`, `DH_MakeDir()`, and `DH_EnumerateDir()`.

## Control Flow, State, and Persistence
Read operations acquire a read lock, call the corresponding `DIR_*` function, then unlock. Mutations acquire a write lock, set `dh_dirty`, and call `DIR_Create()`, `DIR_Delete()`, or `DIR_MakeDir()`, with transaction checks delegated to lower layers when data is in RVM. Allocation chooses `rvmlib_rec_malloc()` or `malloc()` and zeros the buffer; freeing mirrors that choice.

## Dependencies and Integration
Depends on LWP locks, RVM library helpers, `codadir.h`, `dirbody.h`, and FID conversion routines from `fid.c`. It is the main integration surface for vnode/cache code that should not manipulate directory pages directly.

## Risks and Test Signals
Risks include `DH_FreeData()` returning while still holding the lock if `dh_data` is null, duplicate prototypes in the header, dirty-bit management requiring external commit discipline, and transaction-sensitive calls. Test signals are create/delete/lookup consistency, dirty flag transitions, `DIR_DirOK()` after mutations, and RVM transaction assertions.

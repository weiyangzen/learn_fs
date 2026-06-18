# sources/distributed-fs/coda/coda-src/dir/dirinode.c

## Purpose
Persistence bridge between contiguous `DirHandle` data and page-array `DirInode` objects, including RVM and VM copy/refcount management.

## APIs, Types, and Functions
Exports `DI_DiToDh()`, `DI_DhToDi()`, `DI_Dec()`, `DI_Inc()`, `DI_Count()`, `DI_Pages()`, `DI_Page()`, `DI_Copy()`, `DI_VMCopy()`, `DI_VMDec()`, and `DI_VMFree()`. Internal `DI_New()` allocates a new RVM inode.

## Control Flow, State, and Persistence
`DI_DiToDh()` allocates contiguous VM memory and copies each inode page into it for handle use. `DI_DhToDi()` runs in an RVM transaction, creates an inode if needed, copies each handle page into RVM page slots, updates refcount from the cache entry, and frees no-longer-needed pages. `DI_Dec()` and `DI_Inc()` mutate persistent refcounts, freeing pages and inode when the count reaches zero. Copy routines duplicate page arrays for RVM or VM.

## Dependencies and Integration
Depends on RVM allocation/range APIs, transaction checks, `DIR_Page()`, `DH_Length()`, and `DC_*` cache accessors. It integrates with vnode copy-on-write and commit paths.

## Risks and Test Signals
Risks include transaction requirements, assertion-heavy allocation failures, a likely reversed `memcpy()` in `DI_VMCopy()`, no decrement writeback in `DI_VMDec()` when refcount is above one, and fixed page-array limits. Test signals are page-count preservation, copy independence, refcount free behavior, RVM range coverage, and handle-to-inode round trips.

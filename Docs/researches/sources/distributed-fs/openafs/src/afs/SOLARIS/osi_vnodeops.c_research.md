# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vnodeops.c

## Purpose
Solaris vnode operations for OpenAFS, including VM page-in/page-out, segmap read/write, mmap, lock, pathconf, and wrappers from Solaris VOPs to common AFS operations.

## Important APIs, Types, and Functions
Defines `afs_fc2errno`, `afs_addmap`, `afs_delmap`, `afs_vmread`, `afs_vmwrite`, `afs_getpage`, `afs_GetOnePage`, `afs_putpage`, `afs_putapage`, `afs_nfsrdwr`, `afs_map`, `afs_pathconf`, `afs_ioctl`, `afs_rwlock`, `afs_rwunlock`, `afs_seek`, `afs_frlock`, `afs_space`, `afs_dump`, `afs_cmp`, `afs_realvp`, `afs_pageio`, `afs_dumpctl`, security-attribute stubs, `gafs_*` wrappers, `afs_inactive`, `gafs_inactive`, `gafs_fid`, and vnode op tables/templates.

## Control Flow
Read/write VOPs require the vcache rwlock and call `afs_nfsrdwr` under GLOCK. `afs_getpage` dispatches single pages to `afs_GetOnePage`; multipage faults register a range in `avc->multiPage` so cache eviction avoids deadlocking on already locked pages. `afs_GetOnePage` resolves/validates dcaches, creates or looks up pages, performs `afs_ustrategy` reads, marks page flags, and prefetches next chunks. `afs_putpage` gathers dirty pages and calls `afs_putapage`; read-only volume pages use a panic-on-dirty dummy callback. `afs_nfsrdwr` performs segmap-backed I/O, handles append/ulimit/large-file checks, fake opens, dirty state, partial writes, and NFS translator credentials. `gafs_*` functions wrap core AFS operations in GLOCK for the Solaris vnode ABI.

## State and Persistence
Mutates vcache length/date/dirty/mapped flags, dcache flags, `afs_indexFlags` page bits, Solaris pages, stored NFS translator credentials, vnode/VFS refs, and remote/cache data through core AFS calls. Inactive decrements Solaris vnode count and releases VFS refs.

## Dependencies and Integration Points
Depends on Solaris VM (`page_*`, `pvn_*`, `segmap_*`), VFS/vnode ABI variants for Solaris 10/11, common OpenAFS cache manager, `SOLARIS/osi_vm.c`, `SOLARIS/osi_vcache.c`, Rx/NFS translator request handling, and `afs_ops` registration in VFS init.

## Risks
This is a high-risk concurrency file. Page locks, vcache locks, dcache locks, GLOCK, and segmap faults must occur in the intended order. Dirty-page accounting and read-only volume pageout are correctness-sensitive. `afs_nfsrdwr` changes file length before data movement for writes and must clean up through fake close/partial writes on error.

## Test Signals
Mapped read/write, large multipage faults, cache eviction during faults, write past EOF, append and ulimit behavior, dirty page flush, read-only volume mmap, NFS translator credential reads, inactive after exec, frlock/space truncation, pathconf, and Solaris 10/11 vnode op registration.

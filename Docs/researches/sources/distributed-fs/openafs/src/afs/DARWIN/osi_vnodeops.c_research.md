# sources/distributed-fs/openafs/src/afs/DARWIN/osi_vnodeops.c

## Purpose
This is the Darwin vnode operation layer for OpenAFS. It maps Darwin VNOP/VOP callbacks to common OpenAFS file, directory, VM, lock, ioctl, and vnode-lifecycle operations, and provides special modern-Darwin handling for incomplete/dead vnodes and vnode finalization.

## Important APIs, Types, And Functions
The file exports `afs_vnodeop_entries`, `afs_vnodeop_opv_desc`, modern `afs_dead_vnodeop_entries`, and handlers for lookup, create, open, close, access, getattr, setattr, read/write, pagein/pageout, ioctl, select, mmap, fsync, remove, link, rename, mkdir/rmdir, symlink, readdir, readlink, inactive, reclaim, pathconf, advlock, block/offset conversion, and older lock/bmap/strategy/print/cmap support. `darwin_vn_hold`, `afs_darwin_getnewvnode`, and `afs_darwin_finalizevnode` manage vnode references and replacement.

## Control Flow
Vnode operations usually extract component names, acquire the AFS global lock, call the corresponding `afs_*` routine, release the lock, and repair Darwin vnode/name-cache state. Lookup uses `cache_lookup` on modern Darwin, filters internal fsevent contexts, handles create/rename `EJUSTRETURN`, and finalizes returned vcaches into real vnodes. Open calls `afs_open` and flushes pages; close calls `afs_close` and forces trace/error processing. Access maps KAUTH actions to AFS ACL bits, includes fakestat/dropbox special cases, and returns Darwin errno semantics. Pagein maps the UPL, builds a kernel uio, reads via `afs_read`, zero-fills short reads, and commits or aborts the UPL. Pageout validates bounds, maps the UPL, fake-opens the vcache, writes via `afs_write`, fake-closes it, and commits/aborts. Rename includes a modern cross-volume fallback through a background `BOP_MOVE`.

## State And Persistence
State spans vnode op vectors, dead-vnode op vectors, vnode fsnode pointers, vcache state bits (`CMAPPED`, `CEvent`, `CUnlinked`, `CVInit`, `CDeadVnode`), UBC size/page state, name cache entries, fake dirty/shadow vnode refs during finalization, and vcache hash/reclaim lists. Modern finalization replaces a temporary VNON dead vnode with a correctly typed vnode.

## Dependencies And Integration Points
Depends on Darwin VFS/VNOP, UPL/UBC, KAUTH, name cache, OpenAFS common operations, fakestat, background request queue, vcache lifecycle locks, and `osi_vfsops.c` mount state. It is the main Darwin syscall-facing integration point.

## Risks
Reference and lock ordering is the dominant risk: vnode iocounts/usecounts, AFS global lock, vcache locks, name-cache state, and UPL commit/abort must stay balanced. Dead-vnode finalization can race reclaim and must not touch a freed vcache after failure. Access semantics intentionally include Finder/dropbox/fsevents compatibility exceptions. Pageout must not extend files and must zero partial EOF pages. Rename cross-volume fallback depends on background daemon completion.

## Test Signals
Run full filesystem syscall coverage on Darwin: lookup/create/open/read/write/close, Finder resource-fork behavior, KAUTH access checks, pagein/pageout under memory pressure, remove/recycle unlinked files, rename including cross-volume mount-point fallback, readdir cookies/flags, advisory locks, reclaim under vcache pressure, and kext unload after all vnodes are gone.

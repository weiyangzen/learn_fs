# sources/distributed-fs/openafs/src/afs/afs_osi_vm.c

## Purpose
`afs_osi_vm.c` provides common virtual-memory/cache coordination logic around vcaches. It detects active mapped/open files, flushes stale VM pages after remote changes, flushes text mappings on older text-cache platforms, and releases VM pages during invalidation.

## Important APIs, types, and functions
Main functions are `osi_Active`, `osi_FlushPages`, optional `osi_FlushText_really`, and `osi_ReleaseVM`. Important vcache fields are `opens`, `f.states`, `mapDV`, `flushDV`, `execsOrWriters`, `f.m.DataVersion`, and `f.m.Length`.

## Control flow
`osi_Active` checks open counts and mapped/text flags using platform-specific mechanisms. `osi_FlushPages` ignores directories, performs a read-locked fast check to see whether the current data version has already been purged or whether local writers have dirty pages, then repeats under write lock. If flushing is needed, it records the original data version, traces the event, drops the vcache lock and global lock, calls platform `osi_VM_FlushPages`, reacquires locks, and sets `mapDV` to the original version so later calls know that version was purged.

`osi_FlushText_really` handles text-cache invalidation under `AFS_TEXT_ENV`, with platform-specific comments around avoiding Sun/HP-UX text object deadlocks. `osi_ReleaseVM` truncates VM state to zero; Solaris keeps the vcache lock held while other platforms release and reacquire it around `osi_VM_Truncate`.

## State and persistence behavior
No state is persisted. Runtime state changes include `mapDV`, `flushDV`, VM/page cache contents, and possible text-cache purge state.

## Dependencies and integration points
The file depends on platform VM hooks (`osi_VM_FlushPages`, `osi_VM_Truncate`, `afs_DirtyPages`), vnode type macros, global lock macros, vcache locks, and ICL tracing. It is used when callbacks, stores, invalidations, or remote updates require page-cache consistency.

## Risks and edge cases
The main risk is flushing pages that contain local dirty data, losing writes. The double-check under read then write lock is designed to avoid that. Another risk is skipping empty-file flushes; the code deliberately still flushes because some kernels cache zero pages for empty files. Lock drop/reacquire behavior differs by platform and can race if platform VM truncation requires locks not modeled here.

## Test signals
Test remote invalidation of mapped files, local writer dirty-page protection, directory no-op behavior, repeated flushes against `mapDV`, empty-file zero-page flushes, Solaris versus non-Solaris `osi_ReleaseVM` locking, and text flush behavior where `AFS_TEXT_ENV` still builds.

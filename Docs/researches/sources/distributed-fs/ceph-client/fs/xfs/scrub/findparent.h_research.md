<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.h

Purpose: Declares the parent-directory scan state and public helper API used by XFS online repair to discover, confirm, and publish a directory parent.

Important APIs, types, and functions: `struct xrep_parent_scan_info` stores the scrub context, embedded `xchk_iscan`, dirent hook, mutex, discovered `parent_ino`, and a `lookup_parent` flag. It declares scan lifecycle functions, confirmation helpers, dcache/self-reference shortcuts, and the inline `xrep_findparent_scan_found()` setter.

Control flow: Callers initialize the structure with `xrep_findparent_scan_start()` or `__xrep_findparent_scan_start()` when they need a custom notifier. `xrep_findparent_scan_found()` serializes parent updates through `pscan->lock`, allowing directory-update hooks and scan code to publish changes safely. Callers then scan, optionally finish early, and tear down hooks and iscan state.

State and persistence: All state is transient and in-memory. The only shared mutable field is `parent_ino`, guarded by the embedded mutex. No on-disk update is performed by this header.

Dependencies and integration points: Exposes `xchk_iscan`, `xfs_dir_hook`, `xfs_scrub`, and notifier integration to directory, parent-pointer, and repair code. The API assumes callers follow the locking contract documented in `findparent.c`.

Risks and test signals: Incorrect lifecycle ordering can leave dirent hooks registered or destroy the mutex while updates are possible. Test repeated start/scan/finish/teardown, early-finish paths, custom hook registration, concurrent updates to `parent_ino`, and callers reading the result only while holding the required inode locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.h -->

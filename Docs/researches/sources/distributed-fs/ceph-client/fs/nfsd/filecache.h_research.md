# sources/distributed-fs/ceph-client/fs/nfsd/filecache.h

## Purpose
`filecache.h` declares the NFSD open-file cache interface and defines the cache object layouts shared with request, VFS, and LOCALIO code.

## Important APIs, types, and functions
It defines `NFSD_FILE_GC_BATCH`, `struct nfsd_file_mark`, and `struct nfsd_file`. `struct nfsd_file` contains the rhashtable node, inode key, backing `struct file`, credential, net namespace, flag bits, refcount, permission mask, fsnotify mark, LRU/GC links, RCU head, birth time, and DIO alignment fields. Public declarations cover cache lifecycle, reference management, backing-file access, inode close helpers, cached-inode checks, acquisition variants, and stats display.

## Control flow
The header makes acquisition style explicit: `nfsd_file_acquire_gc()` returns a reusable GC-managed object, `nfsd_file_acquire()` and `nfsd_file_acquire_opened()` return non-GC objects, `nfsd_file_acquire_dir()` opens directories, and `nfsd_file_acquire_local()` supports LOCALIO access without a normal RPC request. Callers must release returned objects with `nfsd_file_put()` or the LOCALIO wrapper path.

## State and persistence
The state described here persists only while the NFSD filecache is initialized. The inode field intentionally is not a live inode reference and must only be compared while the cache guarantees its validity through surrounding VFS/file lifetime rules.

## Dependencies and integration points
It depends on fsnotify backend types and declarations from NFSD net/filehandle/request code. The API is used by NFSv3 procedure code, LOCALIO, export flushing, VFS unlink/rename handling, and stats presentation.

## Risks and test signals
Risks include callers dereferencing `nf_inode`, missing `nfsd_file_put()` on error exits, using the wrong acquisition variant for GC semantics, and failing to hold/release net references in LOCALIO. Test signals include build coverage for all acquisition variants, Coccinelle-style reference-pair checks, and runtime tests for directory opens, existing-opened-file acquisition, and local filehandle access.

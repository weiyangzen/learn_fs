# sources/distributed-fs/glusterfs/xlators/features/index/src/index.c

## Purpose
Implements the `index` translator, which tracks files needing heal or other background attention by creating hard-link based index entries under `.glusterfs/indices/{xattrop,dirty,entry-changes}`. It also exposes those index directories through virtual GFIDs returned by special getxattr keys and supports administrative readdir/unlink/rmdir over the virtual namespace.

## Important APIs, Types, and Functions
- `index_get_type_from_vgfid()`, `index_is_virtual_gfid()`, and `index_get_subdir_from_vgfid()` map generated internal virtual GFIDs to index categories.
- `index_inode_ctx_get()` creates per-inode state with `state[]`, queued stubs, `processing`, and `virtual_pargfid`.
- `index_add()`, `index_del()`, `index_entry_create()`, and `index_entry_delete()` maintain hard-link or directory entries in index subdirs.
- `index_xattrop()` and `index_fxattrop()` serialize tracked xattrop operations per inode and update indices both before and after the child fop.
- `index_getxattr()` returns virtual GFIDs and count xattrs such as `GF_XATTROP_INDEX_COUNT`.
- `index_lookup()`, `index_opendir()`, `index_readdir()`, `index_unlink()`, and `index_rmdir()` implement the virtual interface over on-disk index paths.
- `index_worker()` handles asynchronous call stubs on a private worker thread.
- `init()`, `fini()`, `notify()`, and callbacks manage lifecycle, worker drain, and cleanup.

## Control Flow
Tracked xattrop/fxattrop calls are identified by operation flags and configured watchlists. The wrapper stores local inode/xdata, queues a call stub per inode through `index_queue_process()`, pre-adds index entries for non-zero watched xattrs, optionally creates entry-change name indices, winds to the child, then the callback examines returned xattrs and removes index entries whose watched values are all zero.

The virtual namespace starts when clients request index GFIDs via getxattr. Lookups against those GFIDs or children are handled by a worker stub that maps the loc to an on-disk path, lstats it, constructs an iatt, and stores `virtual_pargfid` for entry-change child directories. Readdir opens the corresponding local directory via fd ctx and converts `dirent` records into `gf_dirent_t`; with `"get-gfid-type"` it launches a synctask to resolve each GFID’s actual type. Unlink/rmdir against virtual entries delete index links or directories instead of forwarding to the child.

## State and Persistence
Persistent state is encoded as files, hard links, and directories under the configured `index-base` path. `index_link_to_base()` creates a base file named `<subdir>-<uuid>` and hard-links GFID entries to it; link count is used to approximate pending counts. `entry-changes` uses per-parent-GFID directories with name entries. In-memory state includes generated internal virtual GFIDs, watchlist dicts, a pending-count cache, fd directory handles, inode ctx state, a worker queue, and synchronization primitives.

## Dependencies and Integration Points
Depends on libglusterfs syscall wrappers, syncop/synctask, inode/fd ctx APIs, dict watchlist helpers, gluster XDR dirent structures, statedump, pthreads, and POSIX directory APIs. Integrates with AFR/EC heal machinery through watchlist defaults (`trusted.afr.dirty`, `trusted.ec.dirty`, `trusted.afr.{{ volume.name }}`) and xattrs such as `GF_XATTROP_INDEX_GFID`, `GF_XATTROP_DIRTY_GFID`, `GF_XATTROP_ENTRY_CHANGES_GFID`, and entry in/out keys.

## Risks and Edge Cases
Hard-link count semantics are filesystem dependent and can hit `EMLINK`, forcing index UUID rotation. Stale base files are removed during readdir only when link count is one. Worker-thread drain is important on graph teardown; `notify()` waits on `stub_cnt` and child cleanup. Path building relies on `PATH_MAX`, UUID strings, and basename validation; entry names containing `/` are rejected. Some asynchronous synctask calls pass stack-allocated args and rely on completion timing. Watchlist matching uses prefix-style matching that should be validated for unintended overlaps.

## Test Signals
Tests should cover xattrop add/remove transitions for dirty and pending watchlists, non-zero to zero xattr transitions, entry-change create/delete, index-base creation failures, virtual GFID getxattr/lookup/readdir/unlink/rmdir, stale base-file cleanup, pending link-count xdata on lookup/fstat, and graph teardown with queued work.

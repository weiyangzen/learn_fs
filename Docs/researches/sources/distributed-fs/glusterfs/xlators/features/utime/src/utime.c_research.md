# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime.c

## Purpose
Implements the utime translator lifecycle and lookup behavior, while registering generated fop wrappers that set metadata timestamp update flags for ctime/mtime/atime handling.

## Important APIs, Types, and Functions
- Placeholder cbks/dumpops (`gf_utime_invalidate`, `gf_utime_forget`, fd/inode dump helpers, etc.) currently return success/no-op.
- `mem_acct_init()` initializes memory accounting to `utime_mt_end`.
- `gf_utime_lookup()` ensures lookup xdata asks for `GF_XATTR_MDATA_KEY`.
- `gf_utime_set_mdata_lookup_cbk()` checks lookup results and, when missing mdata, builds `struct mdata_iatt`, creates a separate frame, stubs the original lookup callback, and sends a child `setxattr` with `CTIME_MDATA_XDATA_KEY`.
- `gf_utime_set_mdata_setxattr_cbk()` logs but does not fail lookup when mdata setxattr fails, resumes the saved lookup stub, and destroys the helper frame.
- `init()`, `fini()`, and `reconfigure()` manage `utime_priv_t.noatime`.
- `fops` references generated wrappers and the custom lookup wrapper; `cbks`, `dumpops`, `options`, and `xlator_api` register the translator.

## Control Flow
Generated fops set `frame->root->ctime` and metadata flags, then pass through to the child. `gf_utime_lookup()` refs or creates xdata, adds `GF_XATTR_MDATA_KEY`, and winds lookup. If lookup succeeds and the mdata xattr is absent, the callback creates metadata from the returned `iatt`, issues an internal root-owned setxattr with `GF_CLIENT_PID_SET_UTIME`, stores a stub for the original lookup callback in the helper frame, and resumes that stub after the setxattr callback. If mdata already exists or lookup failed, it unwinds normally.

## State and Persistence
`utime_priv_t` stores only `noatime`. Per-call state is mostly xdata and helper-frame stubs. Persistent state is the on-disk metadata xattr written via `CTIME_MDATA_XDATA_KEY`.

## Dependencies and Integration Points
Depends on generated fops, `utime-helpers`, call stubs, metadata xattr helpers (`iatt_to_mdata`, `dict_set_mdata`), GlusterFS stack APIs, and the `ctime` feature. Option `noatime` is client-settable/doc-tagged under `ctime`.

## Risks
- Helper-frame/stub ownership is subtle; allocation failures must destroy frames and unref dicts/inodes.
- Lookup intentionally ignores mdata setxattr failure after logging, so metadata initialization can lag.
- Many dump/callback hooks are no-ops, which may limit observability.
- No child-count validation is present in `init()` in this file; graph correctness may rely on broader xlator conventions.

## Test Signals
Tests should cover lookup with missing/present mdata, internal setxattr pid/uid/gid, failure to allocate dict/mdata/stub/frame, noatime reconfigure, generated fop flag behavior, and build-time generation of all fop symbols in the fops table.

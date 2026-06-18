<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.c

Purpose: implements append-only variable-length blob storage on top of xfiles for scrub/repair code that needs to keep names or other variable-sized records and refer to them by opaque cookies.

Important APIs and functions: `struct xb_key` is the packed on-xfile header containing magic, blob size, and self offset. `xfblob_create()` creates the backing xfile and initializes `last_offset` to `PAGE_SIZE`, leaving the first page unused as a guard against null/zero cookies. `xfblob_store()` writes a key header and blob bytes, returns the starting offset as an `xfblob_cookie`, and advances `last_offset`. `xfblob_load()` validates the key magic/self-offset and reads the blob into a caller buffer. `xfblob_free()` validates and discards one stored blob. `xfblob_bytes()` and `xfblob_truncate()` report backing storage and reset to the initial offset.

Control flow: stores append sequentially: write header at `last_offset`, write payload after the header, publish cookie, then advance. If payload write fails, only the header range is discarded. Loads and frees first read the header from the cookie and reject stale/corrupt cookies with `-ENODATA`; loads also reject too-small destination buffers with `-EFBIG`.

State and persistence: blob data is transient xfile-backed memory, not durable filesystem metadata. `last_offset` is the only allocator state and there is no reuse of freed interior holes; truncate discards everything after the first page and resets append position. The key header adds lightweight integrity checking so callers can detect invalid cookies.

Dependencies and integration points: depends on xfile create/load/store/discard/bytes, scrub allocation flags, and `xfblob.h` name helpers for storing `struct xfs_name` strings. It complements `xfarray`: arrays can store fixed records containing blob cookies when variable-length names are needed elsewhere.

Risks and test signals: risks include unbounded growth without reuse, partial store cleanup discarding only the key header and leaving a failed partial payload to xfile behavior, no concurrency control around `last_offset`, size/cookie truncation bugs, and callers passing undersized buffers. Tests should cover create/destroy, store/load/free/truncate, invalid cookie magic/offset, load buffer too small, repeated frees, byte accounting, and storing names through the inline helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.c -->

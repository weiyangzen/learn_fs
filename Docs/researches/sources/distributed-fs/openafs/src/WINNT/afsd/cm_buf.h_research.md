# sources/distributed-fs/openafs/src/WINNT/afsd/cm_buf.h

## Purpose
`cm_buf.h` declares the Windows cache manager buffer abstraction: fixed-size cache pages, hash macros, queue and I/O flags, callback operations supplied by the data-cache layer, global lock/log symbols, buffer lifecycle APIs, dirty/writeback APIs, redirector extent APIs, validation/debug helpers, and checksum helpers.

## Important APIs, types, and macros
`cm_buf_t` is the central buffer header. It contains global queue links, queue/hash flags, magic, all/hash/file-hash/dirty links, a per-buffer mutex, refcount, dirty counter, FID/offset identity, mapped data pointer, local I/O flags/error, last writer user, cache-manager data version and cmFlags, sync wait counters, dirty byte range, optional disk-cache pointer, debug scache pointer, redirector queue/timestamps, and an MD5 checksum buffer.

`cm_buf_ops_t` is the callback table used by `cm_buf.c`: `Writep`, `Readp`, `Stabilizep`, and `Unstabilizep`. `CM_BUF_WRITE_SCP_LOCKED` is the write flag exported for callback coordination.

Hash macros are `BUF_HASH(fidp, offsetp)` for FID+offset and `BUF_FILEHASH(fidp)` for FID-only chains. Cache type constants are `CM_BUF_CACHETYPE_FILE` and `CM_BUF_CACHETYPE_VIRTUAL`; `CM_BUF_BLOCKSIZE` follows `CM_CONFIGDEFAULT_BLOCKSIZE`.

`cmFlags` describe scache-level activity (`CM_BUF_CMFETCHING`, `CM_BUF_CMSTORING`, `CM_BUF_CMFULLYFETCHED`, `CM_BUF_CMWRITING`). `qFlags` describe global queue membership (`CM_BUF_QINHASH`, `CM_BUF_QINLRU`, `CM_BUF_QINDL`, `CM_BUF_QREDIR`). `flags` describe buffer-local I/O/data state (`CM_BUF_READING`, `CM_BUF_WRITING`, `CM_BUF_DIRTY`, `CM_BUF_ERROR`, `CM_BUF_WAITING`, `CM_BUF_EOF`).

The public API covers initialization/shutdown, reference management, I/O waits, lookup, allocation, cleaning, dirty marking, reservation, truncation, vnode flush/clean/invalidate/version forcing, diagnostics, existence checks, redirector extent release/queue manipulation, and checksum computation/validation.

## Control flow and contracts
Callers initialize the package with `buf_Init(newFile, ops, nbuffers)` before using any buffer APIs. Buffers returned from `buf_Get` are held but unlocked; callers release with `buf_Release`. Functions with `Locked` in the name assume the caller already holds `buf_globalLock` or the buffer mutex as documented by the C file.

`buf_SetDirty` requires a locked, referenced buffer and a non-null user. `buf_Clean` and `buf_CleanLocked` push dirty bytes through the configured `Writep`. `buf_WaitIO` waits on `CM_BUF_READING`/`CM_BUF_WRITING` and uses buffer wait counters plus scache wakeups.

Redirector APIs treat `CM_BUF_QREDIR` as ownership by the Windows redirector; those buffers are not ordinary LRU candidates until the redirector releases or the cache manager shakes/clears the extent.

## State and persistence behavior
The header makes the split between persistent cache identity/data and volatile synchronization explicit. The buffer's FID, offset, data pointer, data version, dirty range, and flags are the meaningful page state. Reference counts, wait counters, queue membership, and redirector timestamps are runtime coordination state guarded by `buf_globalLock`, the buffer mutex, or `scp->mx`/redirector locks as noted in comments.

`CM_BUF_VERSION_BAD` marks unknown or invalid cached data. `dirtyCounter` is bumped on dirty-to-clean/error transitions and can be used by other layers to detect changes.

## Dependencies and integration points
The header includes `osi.h` and `opr/jhash.h` and relies on cache-manager definitions from surrounding OpenAFS headers for `cm_fid_t`, `cm_scache_t`, `cm_user_t`, and `cm_req_t`. It exposes `buf_globalLock` and `buf_logp` for modules that must coordinate directly with the buffer package. It integrates with redirector code through `AFSFileExtentCB`-driven release functions implemented in the C file, and with scache/dcache code through `cmFlags` and `cm_buf_ops_t`.

## Risks and edge cases
Refcount APIs have debug macro rewrites under `DEBUG_REFCOUNT`; mixed compilation units must include this header consistently.

The hash macros assume `cm_data.buf_hashSize` is a power of two because they mask with `hashSize - 1`. Initialization must preserve that invariant.

Queue membership flags are not interchangeable with buffer-local I/O flags. Bugs that clear `CM_BUF_QREDIR` without removing redirector queue links, or clear `CM_BUF_DIRTY` without dirty-list cleanup, lead to leaked holds and corrupted lists.

The `redirq_to_cm_buf_t` container macro depends on `offsetof(cm_buf_t, redirq)` and must only be used with valid `redirq` queue nodes.

`buf_SetNBuffers` is declared as if resizing is supported, but the implementation only accepts no-op same-size values or rejects shrinking/growing after cache creation.

## Test signals
Header/API tests should compile with and without `DEBUG_REFCOUNT`, validate the hash macros against initialized power-of-two hash sizes, verify all exported functions have matching definitions, exercise qFlag/flag transitions through public APIs, and include redirector queue container conversions under queue validation.

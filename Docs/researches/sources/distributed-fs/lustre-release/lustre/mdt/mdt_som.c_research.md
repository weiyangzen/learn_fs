# sources/distributed-fs/lustre-release/lustre/mdt/mdt_som.c

## Purpose

`mdt_som.c` implements MDT support for Lustre Size-on-MDS, especially lazy SOM revival (`LSOM`). It reads, writes, downgrades, and updates the `trusted.som` xattr that stores file size/block estimates on metadata targets so clients can sometimes avoid OST queries. It is deliberately conservative: strict SOM can be returned as inode size/blocks, lazy SOM is cached in `struct mdt_object`, and stale/strict transitions are guarded by `mot_som_mutex`.

## Important APIs, Types, and Functions

- `lustre_buf2som()` swabs on-disk `struct lustre_som_attrs` into in-memory `struct md_som`, treating zero-length or `-ENODATA` as no SOM.
- `mdt_get_som()` fetches `XATTR_NAME_SOM`, populates `ma->ma_som`, sets `MA_SOM`, returns strict size/blocks in `ma_attr`, and initializes lazy cached values in `mot_lsom_*`.
- `mdt_set_som()` writes a new SOM xattr with a supplied flag, size, and block count, and updates the in-memory lazy cache for `SOM_FL_LAZY`.
- `mdt_lsom_downgrade()` transitions strict SOM to stale while preserving the recorded size/blocks.
- `mdt_lsom_update()` decides whether close/truncate metadata should create or grow lazy SOM and writes `SOM_FL_LAZY` when appropriate.

## Control Flow

Reads use a fixed `mti_xattr_buf`, call `mo_xattr_get()`, swab the result, and interpret flags. Strict SOM marks `info->mti_som_strict` and overlays `LA_SIZE | LA_BLOCKS` into the inode attr. Lazy SOM initializes `mot_lsom_size`, `mot_lsom_blocks`, and `mot_lsom_inited` only if they are not already initialized and no one holds `mot_som_mutex`.

Writes build `struct lustre_som_attrs` in the thread xattr buffer, swab to disk order, and call `mo_xattr_set()`. Lazy writes also update the in-memory cache. Downgrade locks `mot_som_mutex`, reads current SOM into a scratch `md_attr`, and if strict, writes stale state with the same size/blocks.

Update first fast-exits when the caller's `la_valid` values do not increase cached size/blocks, the operation is not truncate, and the cache is initialized. Otherwise it fetches inode+SOM, ensures LOV EA is available, skips files without LOV, unlink files, and DoM-only files, and then computes a new lazy size/block pair. Non-truncate updates only grow cached values and skip strict SOM or stale SOM with no data modification. Truncate records the requested size and uses zero or a conservative block count of one when real blocks are unreliable. The final write is serialized by `mot_som_mutex` and rechecks cached values before updating.

## State and Persistence Behavior

Persistent state is the SOM xattr containing `lsa_valid`, `lsa_size`, and `lsa_blocks`. In-memory state on `struct mdt_object` mirrors lazy values through `mot_lsom_size`, `mot_lsom_blocks`, and `mot_lsom_inited`; `info->mti_som_strict` marks request-local strict SOM use. This file does not update OST data; it records metadata-side size/block hints based on attrs supplied by close/truncate paths and lower metadata reads.

## Dependencies and Integration Points

The code depends on `mo_xattr_get/set()`, `mdt_attr_get_complex()`, LOV xattr fetch helpers, `mdt_lmm_dom_only()`, thread-local buffers, `struct md_attr`, `struct lu_attr`, and `mot_som_mutex`. It is called from setattr/truncate and close-related paths in MDT code, including `mdt_reint_setattr()` before size changes and paths that need SOM downgrade on non-authoritative changes.

## Risks and Edge Cases

- Lazy SOM only grows on non-truncate updates; callers expecting shrink behavior must pass `truncate`.
- The first fast-exit relies on caller-provided `la_valid` and cached `mot_lsom_*`; missing valid bits can skip a needed update.
- `mti_big_lov_used` allows reusing existing LOV data, so callers must ensure it truly corresponds to the object.
- Truncate block count is intentionally approximate until a later close; consumers must not treat lazy blocks as strict truth.
- Strict-to-stale downgrade preserves size/blocks but clears strict validity; missing downgrade on data modification would expose stale strict sizes.

## Test Signals

Tests should cover no xattr, malformed/short xattr error propagation, strict SOM overriding inode size/blocks, lazy SOM cache initialization, set lazy updating cache, strict downgrade to stale, update skip when cached values are current, initial lazy creation with size+blocks valid, growth-only updates, stale-without-data-modified skip, truncate-to-zero, truncate-to-smaller-size block heuristic, DoM-only skip, unlink skip, and concurrent updates serialized by `mot_som_mutex`.

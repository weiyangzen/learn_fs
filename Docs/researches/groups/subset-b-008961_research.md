# subset-b-008961 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_ckpt.c -->
# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_ckpt.c

## Purpose
Implements checkpoint integration for the disaggregated block manager. It turns a checkpoint root page into a page-log object, packs that root page's disaggregated address as the checkpoint cookie stored in metadata, resolves shared-table metadata after successful checkpoints, and unpacks checkpoint cookies during checkpoint load.

## Important APIs, types, and functions
- `__wti_block_disagg_checkpoint` is the `WT_BM::checkpoint` implementation. It iterates checkpoint entries and fills newly added checkpoints.
- `__bmd_checkpoint_pack_raw` writes the root image with `__wti_block_disagg_write_internal`, packs a `WT_BLOCK_DISAGG_ADDRESS_COOKIE`, updates root-size accounting, and sets `WT_CKPT::size`.
- `__wti_block_disagg_checkpoint_resolve` wraps `__block_disagg_checkpoint_resolve` in the schema lock.
- `__block_disagg_checkpoint_resolve` updates shared/disaggregated metadata after a successful checkpoint.
- `__wti_block_disagg_checkpoint_load` unpacks a checkpoint cookie and repacks it as the root page address cookie.
- Important structures are `WT_BLOCK_DISAGG`, `WT_CKPT`, `WT_PAGE_BLOCK_META`, `WT_BLOCK_DISAGG_ADDRESS_COOKIE`, and connection-level `disaggregated_storage` metadata.

## Control flow
Checkpoint creation enters through the block-manager vtable. For every `WT_CKPT_ADD` checkpoint, `__bmd_checkpoint_pack_raw` either records an empty raw checkpoint when no root image exists or byteswaps the root page header, writes the page to the page log, restores the page header, and packs a cookie containing `page_id`, `disagg_lsn`, `base_lsn`, encoded size, and checksum. Root size is then applied to the live disaggregated block size and copied into `ckpt->size`.

Checkpoint resolve is separate from writing the root page. With the schema lock held, it skips failed checkpoints. For the shared metadata table it reads the local metadata entry, optionally persists updated key-encryption information, extracts the checkpoint config, and writes checkpoint metadata with timestamp and schema epoch. For ordinary shared tables it derives a table/layered name from the file name and enqueues a `WT_SHARED_METADATA_UPDATE` operation for the current schema epoch.

Checkpoint load is intentionally address-oriented: it does not fetch the root page itself. It unpacks the raw checkpoint cookie, records the current root size on the block handle, then packs the same cookie into the caller's `root_addr` buffer so the normal page read path can fetch the root.

## State and persistence behavior
The checkpoint cookie is the disaggregated page address for the root page. This coupling is explicitly relied on when old checkpoint root pages are discarded. `ckpt->size` is taken from `block_disagg->size` after root-size transition accounting, so metadata uses the same size view as live block accounting. Resolve writes checkpoint metadata into either system metadata for the shared metadata file or the shared metadata operation queue for ordinary stable/shared tables. `current_root_size`, `previous_root_size`, and checkpoint generation handling live in `block_disagg_size.c` but are driven here.

## Dependencies and integration points
This file depends on the page-log write path in `block_disagg_write.c`, checkpoint/address pack helpers, metadata cursors, the disaggregated metadata queue, key-provider crypt helper, and the schema lock. It is installed as `WT_BM::checkpoint`, `checkpoint_load`, and `checkpoint_resolve` in `block_disagg_mgr.c`.

## Risks and edge cases
- The root checkpoint cookie and address cookie are assumed identical; changing either format requires coordinated discard/checkpoint changes.
- Root-page byteswapping is done in place and restored after the write. Any early-return path around that operation must preserve restoration.
- `__bmd_checkpoint_pack_raw` panics on root-page write failure, making page-log availability a hard checkpoint requirement.
- File-name suffix stripping for `.wt` and `.wt_stable` is convention-sensitive and also supports suffix-less test files.
- Checkpoint size correctness depends on root-size adjustment happening before metadata persistence and rollback logic reversing failed generations.

## Test signals
Useful tests include successful and failed disaggregated checkpoints, empty root checkpoints, checkpoint load of packed root cookies, metadata resolve for both `WT_DISAGG_METADATA_FILE` and ordinary shared tables, key-provider metadata propagation, checkpoint failure rollback size checks, and recovery/open paths that verify `ckpt->size` matches disaggregated block size.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_ckpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_mgr.c -->
# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_mgr.c

## Purpose
Defines the disaggregated block manager facade exposed through `WT_BM`. It adapts WiredTiger's normal block-manager calls to page-log backed remote storage, wires the vtable, owns block-manager open/close/free/write/read/checkpoint dispatch, and decides whether a file handle belongs to the disaggregated manager.

## Important APIs, types, and functions
- `__wt_block_disagg_manager_open` allocates `WT_BM`, marks it remote, wires methods, strips `file:`, and opens a `WT_BLOCK_DISAGG`.
- `__wt_block_disagg_manager_owns_object` currently selects this manager for `file:` handles whose btree has a page log.
- Static adapters include `__bmd_write`, `__bmd_free`, `__bmd_close`, `__bmd_stat`, `__bmd_get_page_ids`, `__bmd_addr_invalid`, and `__bmd_write_size`.
- `__bmd_method_set` binds disaggregated implementations and unsupported stubs into the `WT_BM` method table.
- Important types are `WT_BM`, `WT_BLOCK_DISAGG`, `WT_PAGE_LOG_HANDLE`, `WT_BLKCACHE`, and `WT_DSRC_STATS`.

## Control flow
Open allocates a `WT_BM`, marks `is_remote`, calls `__bmd_method_set`, strips the URI prefix, and delegates to `__wti_block_disagg_open`. On failure it uses the vtable close path for cleanup. Write calls capacity throttling with checkpoint or eviction throttle tags, then delegates to `__wti_block_disagg_write`. Free delegates to `__wti_block_disagg_page_discard` and removes the address from the block cache when configured. Close delegates to `__wti_block_disagg_close` and frees the `WT_BM`.

`__bmd_get_page_ids` asserts a disaggregated btree, warns and returns success if the page-log hook is absent, otherwise asks the page-log handle for all page IDs at a checkpoint LSN.

## State and persistence behavior
This file owns no persistent format directly, but it is the vtable boundary for all persistence calls. It marks block managers as remote, routes writes and checkpoints into page-log storage, routes discard into page-log discard plus block-cache invalidation, and reports size/statistics from disaggregated checkpoint metadata. `can_truncate` always returns false because there is no local file tail to reclaim.

## Dependencies and integration points
The file integrates the block-disaggregated modules with the generic btree/block-manager layer. It references address validation/string helpers, checkpoint handlers, read/read-multiple handlers, write/write-size handlers, size/stat handlers, and unsupported operation stubs. It also integrates with capacity throttling and `WT_BLKCACHE` eviction of freed remote blocks.

## Risks and edge cases
- `__wt_block_disagg_manager_owns_object` is intentionally broad and keyed on page-log presence; incorrect page-log setup can route a file to the wrong manager.
- Several normal block-manager methods point to no-op stubs, so callers must tolerate unsupported local-file semantics.
- `__bmd_get_page_ids` silently succeeds when the page-log provider lacks the hook, which may hide missing functionality unless verbose warnings are monitored.
- The vtable has to stay in sync with `WT_BM` expectations; missing hooks such as compaction rewrite/progress can matter for generic btree operations.

## Test signals
Tests should cover manager selection, open/close reference cleanup, write throttling dispatch, free plus block-cache invalidation, page-ID fetch with and without provider support, and generic block-manager operations against disaggregated handles. Integration tests should validate every installed vtable slot used by checkpoint, eviction, verify, compact, and cursor reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_open.c -->
# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_open.c

## Purpose
Handles lifecycle and statistics for `WT_BLOCK_DISAGG` handles. It creates no physical file, opens or reuses page-log backed block handles from the connection block hash, closes and destroys those handles, and derives live block size/statistics from checkpoint metadata.

## Important APIs, types, and functions
- `__wt_block_disagg_manager_create` is the create hook and is currently a no-op because remote storage materializes on first access.
- `__wti_block_disagg_open` creates/reuses `WT_BLOCK_DISAGG`, stores table ID, opens the page-log handle, and inserts into the connection block hash.
- `__wti_block_disagg_close` decrements the block refcount under `block_lock` and destroys when it reaches zero.
- `__block_disagg_destroy` removes the block from the connection hash, frees its name, closes `plhandle`, and frees memory.
- `__wt_block_disagg_ckpt_size`, `__wti_block_disagg_stat`, and `__wti_block_disagg_manager_size` expose checkpoint-derived size information.

## Control flow
Create returns success without touching the storage source. Open hashes the filename, checks the connection block hash under `block_lock`, increments `ref` on a match, otherwise allocates a `WT_BLOCK_DISAGG`, inserts it into the hash early for cleanup safety, duplicates the name, marks history-store shared blocks, copies the btree table ID, and opens a page-log handle with `S2BT(session)->page_log->pl_open_handle`. Close locks the block hash, decrements the reference count, and calls destroy when the handle is no longer referenced.

Size/stat calls search the metadata for the file URI, read the most recent checkpoint size with `__wt_ckpt_last_size`, tolerate missing metadata as zero, and write block stats from that value because no local file length exists.

## State and persistence behavior
The connection block hash caches live `WT_BLOCK_DISAGG` handles keyed by filename. Each handle stores `name`, `ref`, `tableid`, optional history-store flag, and page-log handle. Persistent size is not in a filesystem stat; it is the last checkpoint size in the metadata entry. Opening a handle is tied to btree table ID and page-log provider state.

## Dependencies and integration points
This file depends on connection `block_lock`/`blockhash`, page-log provider open/close methods, metadata search and checkpoint config parsing, btree table IDs, history-store naming, and WT statistics. It is called by the manager facade in `block_disagg_mgr.c`.

## Risks and edge cases
- The block is inserted into the hash before all initialization succeeds; cleanup relies on the partially initialized object being destroyable.
- The open loop has a TODO to confirm the found block is the right block type, so name collisions across block-manager kinds would be dangerous.
- Page-log handle creation is asserted as mandatory; disaggregated tables cannot proceed without it.
- Metadata-not-found size returns zero, which is useful for create/open races but can mask missing metadata in diagnostics.
- Reference counting is protected by `block_lock`; any future direct manipulation must preserve that discipline.

## Test signals
Useful tests include create without local files, duplicate opens incrementing refcounts, close destroying only after the last ref, page-log close error propagation, history-store flagging for `WT_HS_FILE_SHARED`, metadata checkpoint-size reads, missing metadata size zero, and stats/manager size reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_read.c -->
# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_read.c

## Purpose
Implements disaggregated page reads through the page-log interface, including multi-buffer base-plus-delta fetch, block header validation, checksum/magic/version checking, page-header byteswap, metadata population, read statistics, debug reads by page ID, and corruption reporting.

## Important APIs, types, and functions
- `__wti_block_disagg_read_multiple` is the vtable read path for address-cookie referenced pages and deltas.
- `__block_disagg_read_multiple` calls `plh_get`, validates each returned buffer, and fills `WT_PAGE_BLOCK_META`.
- `__wti_block_disagg_read` returns `ENOTSUP`; single-buffer basic reads are not supported.
- `__wti_block_disagg_corrupt` reads and dumps block data for corruption diagnostics.
- `__wt_block_disagg_debug_read_page_id` fetches raw page-log results for debug tooling without validation/byteswap.
- `__block_disagg_check_lsn_frontier` warns if reads pass the materialization frontier.
- `__ut_block_disagg_header_version_compatible` exposes version compatibility to unit tests.

## Control flow
The public multi-read path unpacks a `WT_BLOCK_DISAGG_ADDRESS_COOKIE`, then calls the internal reader with page ID, flags, LSNs, cumulative size, and checksum. The internal reader builds `WT_PAGE_LOG_GET_ARGS`, tags cold storage when needed, increments read stats, checks the materialization frontier, and invokes `plh_get`. It expects one base image plus up to `WT_DELTA_LIMIT` deltas.

Validation walks results from newest delta back to base. For each buffer it copies the disaggregated header, treats nonzero modified-cache flags as cache-origin reads, checks the header checksum chain against the expected checksum, validates base/delta magic, validates compatible version, fills `WT_PAGE_BLOCK_META` from page-log get results on the newest buffer, byteswaps the page header, and then updates the expected checksum to `previous_checksum`. On mismatch it logs context, dumps data unless quiet corrupt mode is set, marks connection data corruption, and panics for ordinary reads.

## State and persistence behavior
Reads reconstruct page state from a page-log chain identified by `page_id`, `lsn`, `base_lsn`, size, flags, and checksum in the address cookie. `WT_PAGE_BLOCK_META` receives `page_id`, `backlink_lsn`, `base_lsn`, `disagg_lsn`, `delta_count`, `checksum`, and `cumulative_size`, allowing later reconciliation and delta writes to build on the read. The checksum chain through `previous_checksum` persists ordering assumptions between deltas and base images.

## Dependencies and integration points
This file depends on address unpacking, page-log `plh_get`, disaggregated block headers from the write path, page-header byteswap helpers, connection materialization frontier state, statistics, history-store/cold-storage flags, and debug btree tooling. It is installed as `WT_BM::read_multiple`; ordinary `read` intentionally fails.

## Risks and edge cases
- Single-block reads are unsupported, so all callers must use `read_multiple` for disaggregated btrees.
- Header version compatibility is one-way: a block whose `compatible_version` is newer than the reader is corrupt for this build.
- Modified victim-cache blocks skip part of the normal size/checksum assumptions, so validation differs from page-service reads.
- The read loop assumes result ordering with base at index 0 and deltas after it; page-log provider ordering bugs would corrupt reconstruction.
- Frontier violations currently warn and count stats rather than crash.

## Test signals
Tests should cover base-only reads, base-plus-delta chains, checksum-chain failures, wrong magic for base/delta, incompatible header versions, cold-tier reads, history-store reads, victim-cache modified blocks, materialization frontier warning stats, quiet corrupt behavior, and debug reads returning raw buffers without validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_size.c -->
# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_size.c

## Purpose
Maintains byte-size accounting for disaggregated block handles, including ordinary write/discard deltas, obsolete delta-chain removal, root-page size transitions during checkpoint, and rollback of checkpoint root-size accounting.

## Important APIs, types, and functions
- `__wti_block_disagg_get_size`, `__wti_block_disagg_increase_size`, and `__wti_block_disagg_decrease_size` are low-level atomic size operations on `WT_BLOCK_DISAGG`.
- `__wt_block_disagg_get_size`, `__wt_block_disagg_set_size`, and `__wt_block_disagg_obsolete_delta_chain` are btree/session-level wrappers for disaggregated trees.
- `__wti_block_disagg_apply_root_size` handles checkpoint root size replacement.
- `__wt_block_disagg_checkpoint_rollback` reverts root-size accounting if the current checkpoint generation fails.

## Control flow
Writes call increase; non-root discards and obsolete delta-chain notifications call decrease. Decrease saturates at zero if asked to subtract more than the current total. Checkpoint root handling saves the previous root size, records the new root size and checkpoint generation, subtracts the previous root, and adds the new root. Rollback checks that the btree is disaggregated and that the root-size generation matches the current checkpoint generation, then subtracts the current root and restores the previous root.

## State and persistence behavior
`WT_BLOCK_DISAGG::size` is an atomic live byte count used when checkpoint metadata records `WT_CKPT::size`. Root pages are special because old root discard occurs after checkpoint size is written; root transitions are accounted when the checkpoint is packed rather than when the old root is discarded. `current_root_size`, `previous_root_size`, and `root_size_gen` are transient block-handle state used to make failed checkpoints reversible.

## Dependencies and integration points
This file integrates with checkpoint packing in `block_disagg_ckpt.c`, page discard and write logic in `block_disagg_write.c`, delta-chain obsolete notifications from reconciliation, btree flags, and checkpoint generation tracking through `__wt_gen(session, WT_GEN_CHECKPOINT)`.

## Risks and edge cases
- There is an explicit FIXME for a disaggregated block size accounting bug; decrease currently saturates at zero instead of asserting.
- Size is updated atomically but root-size fields are not independently synchronized here; callers rely on checkpoint sequencing.
- Rollback only applies to the matching checkpoint generation, so generation mismanagement can leave wrong root-size accounting.
- Root pages are deliberately skipped by discard accounting; double subtraction would break verify/checkpoint size consistency.

## Test signals
Tests should validate write increments, discard decrements, saturation behavior for over-decrement, obsolete delta-chain size removal, root size replacement across checkpoints, rollback of failed checkpoints, no-op rollback on non-disaggregated btrees, and checkpoint metadata size matching live size after root transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_unsup.c -->
# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_unsup.c

## Purpose
Provides placeholder implementations for block-manager operations that either do not apply to disaggregated storage yet or are intentionally no-ops. This keeps the `WT_BM` vtable complete while avoiding local-file semantics such as mmap, salvage, sync, and traditional verify.

## Important APIs, types, and functions
The file defines no-op or fixed-return implementations for checkpoint start/unload, compaction start/skip/page-skip/end, mapping queries/discard, salvage start/next/valid/end, sync, verify start/address/end, and `__wti_block_disagg_is_mapped`.

## Control flow
Every function consumes the standard `WT_BM` arguments with `WT_UNUSED` and returns success, except `__wti_block_disagg_is_mapped`, which returns false. The compaction skip/page-skip functions do not set `*skipp`, so the caller must not depend on these stubs for meaningful compaction decisions unless initialized elsewhere.

## State and persistence behavior
No persistent state is read or written. The behavior advertises that disaggregated storage does not currently use memory mapping, local-file syncing, local salvage iteration, or traditional block verification through these paths.

## Dependencies and integration points
These functions are installed into `WT_BM` by `block_disagg_mgr.c`. They satisfy generic block-manager API expectations while most real work is delegated to page-log reads, writes, checkpoint packing, metadata, and discard.

## Risks and edge cases
- Silent success can hide unsupported behavior if generic callers assume the operation had an effect.
- Compaction and verify paths may report success without validating or moving any remote blocks.
- Future callers that require initialized out-parameters must update these stubs; several currently ignore pointer outputs.
- The functions are appropriate only if higher layers explicitly understand disaggregated storage limitations.

## Test signals
Tests should verify that unsupported operations do not crash, that mapped-state queries return false, that generic APIs using these hooks preserve expected user-visible semantics, and that compaction/verify/salvage tests either skip disaggregated storage or assert the documented no-op behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_unsup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_write.c -->
# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_write.c

## Purpose
Implements disaggregated page writes and discards. It builds disaggregated block headers, computes checksum chains, writes base or delta images through the page-log provider, packs address cookies, updates block metadata and size accounting, and forwards discard requests to the page log.

## Important APIs, types, and functions
- `__wti_block_disagg_write_size` adds disaggregated header space and rejects oversized writes.
- `__wti_block_disagg_write_internal` writes the buffer through `plh_put` and updates `WT_PAGE_BLOCK_META`.
- `__wti_block_disagg_write` is the vtable write path that byteswaps page headers, updates size accounting, and packs address cookies.
- `__wti_block_disagg_page_discard` decodes an address cookie, updates size accounting for non-root pages, and calls `plh_discard` when available.
- `__wt_block_disagg_header_byteswap_copy` and `__block_disagg_header_byteswap` are endian placeholders.
- `__block_disagg_addr_flags` encodes delta-chain status into address-cookie flags.

## Control flow
The high-level write path casts `WT_BLOCK` to `WT_BLOCK_DISAGG`, byteswaps the page header into storage order, calls the internal writer, increments the live block size by the stored size, restores the page header, and packs a `WT_BLOCK_DISAGG_ADDRESS_COOKIE`. For base images the cookie size is the block size. For deltas it is prior cumulative size plus this block size, and `block_meta->cumulative_size` is updated for future deltas.

The internal writer clears and fills the disaggregated block header, validates the buffer size, asserts the node is the layered-table leader, sets data-checksum/compression/encryption/base/delta/version fields, stores `previous_checksum`, computes the checksum, maps block metadata into `WT_PAGE_LOG_PUT_ARGS`, sets cold/compressed/encrypted/delta flags, calls `plh_put`, updates stats and histograms, logs verbose write details, and copies the returned LSN and checksum into `block_meta`.

Discard unpacks the cookie, logs it, subtracts size for non-root pages, tolerates missing `plh_discard`, and otherwise sends base/backlink LSNs to the page-log discard hook. For delta chains the discard base LSN is the cookie's `base_lsn`; for base images it is the page's own LSN.

## State and persistence behavior
The persisted block header stores magic, version, compatible version, checksum, previous checksum, data-checksum flag, compression/encryption flags, and base/delta identity. The address cookie stores page ID, LSNs, checksum, flags, and cumulative size. `WT_PAGE_BLOCK_META` is the mutable bridge from reconciliation to page log: it carries page ID, previous checksum, base LSN, backlink LSN, delta count, cumulative size, and receives the new disaggregated LSN/checksum after the write.

## Dependencies and integration points
This file depends on btree storage tier, layered-table leadership state, page-log `plh_put`/`plh_discard`, page-header byteswapping, address pack/unpack helpers, block size accounting, connection statistics, history-store flags, and checkpoint code that calls `__wti_block_disagg_write_internal` directly for root pages.

## Risks and edge cases
- Writes assert leader status; follower writes indicate a serious layered-table routing bug.
- Page headers are byteswapped in place and restored by the wrapper; direct internal writes must manage page-header order themselves.
- Checksum logic depends on whether full data checksums are requested and on compression skip semantics.
- Root discards deliberately skip size decrement because checkpoint root accounting is handled at checkpoint-pack time.
- Missing `plh_discard` is only a warning, so storage reclamation may be unavailable without failing the caller.

## Test signals
Tests should cover base writes, delta writes, compressed/encrypted flags, cold-tier flags, checksum validation on subsequent reads, cumulative size tracking, leader-only assertions, write-size overflow rejection, root versus non-root discard accounting, discard with and without provider support, and checkpoint root writes through the internal API.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_compact.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_compact.c

## Purpose
Implements btree compaction by walking internal pages, asking the block manager which referenced blocks are worth moving, rewriting selected disk addresses or marking clean in-memory pages dirty, and forcing checkpoints/eviction to materialize improved layout.

## Important APIs, types, and functions
- `__wt_compact` is the file-level compaction entry point.
- `__compact_walk_internal` reviews one internal page under the btree flush lock.
- `__compact_page` locks a `WT_REF`, rewrites on-disk addresses through the block manager, or delegates in-memory review.
- `__compact_page_inmem` and `__compact_page_inmem_check_addrs` decide whether an in-memory page should be rewritten.
- `__compact_page_replace_addr` installs a rewritten block cookie while preserving address time-window metadata.
- `__compact_walk_page_skip` makes the tree walk visit internal pages only.

## Control flow
`__wt_compact` first asks `bm->compact_skip` whether the file has useful compaction work. If not, it increments skip stats and logs once per table. Otherwise it repeatedly checks interruption/cache-stuck state, throttles by helping eviction, walks to the next internal page using `WT_READ_INTERNAL_OP`, `WT_READ_VISIBLE_ALL`, and `WT_READ_WONT_NEED`, and calls `__compact_walk_internal` while the page index is stable.

For each internal page, `__compact_walk_internal` acquires `flush_lock` to avoid racing checkpoint review. It visits child leaf refs and calls `__compact_page`. If no leaf moved and the parent is not root, it may compact the internal page itself. When any page is selected, it marks the parent/tree dirty and sets `session->compact_state = WT_COMPACT_SUCCESS`.

`__compact_page` locks the ref. Disk/deleted refs with addresses are passed to `bm->compact_page_rewrite`; if the block manager returns a new address, `__compact_page_replace_addr` swaps it in. In-memory clean pages have their original/replacement/multiblock addresses checked by `bm->compact_page_skip`; selected pages are marked modified and tagged `WT_PAGE_COMPACTION_WRITE`.

## State and persistence behavior
Compaction manipulates `WT_REF` address cookies and page dirty state rather than logical records. Rewritten addresses are installed in memory and become persistent through subsequent reconciliation/checkpoint. Address replacement preserves timestamp metadata unpacked from on-page address cells. `WT_PAGE_COMPACTION_WRITE` tells reconciliation to write new blocks. Statistics count selected in-memory pages, compact sessions, skipped files, conflicting checkpoints, eviction assistance, and reviewed pages.

## Dependencies and integration points
The file depends on the generic tree walk, hazard/ref locking, flush lock, block-manager compaction hooks (`compact_skip`, `compact_page_skip`, `compact_page_rewrite`, `compact_progress`), eviction assistance, page modification/reconciliation flags, address unpack/copy helpers, and session compact interruption checks.

## Risks and edge cases
- Holding `flush_lock` and `WT_REF` locks across block-manager checks/rewrite can block checkpoint and application work.
- Moving blocks while checkpoint is reviewing the tree could corrupt checkpoints; the flush lock is the key safety mechanism.
- In-memory dirty pages are not forced immediately because checkpoint is expected to write them eventually.
- Root pages are not directly moved as internal pages because forced checkpoint rewrites roots.
- Block-manager hooks must initialize skip outputs correctly; no-op block managers can make compaction ineffective.

## Test signals
Tests should exercise compact skip/no-work, block rewrite address replacement, in-memory clean-page selection, dirty-page handling, multiblock replacement addresses, deleted refs, checkpoint conflict/retry, interruption and cache-stuck exits, stats progress, and correctness after a checkpoint following compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_compact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_curnext.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_curnext.c

## Purpose
Implements forward btree cursor traversal for row-store and variable-length column-store pages. It walks insert lists, on-page cells, append lists, page boundaries, bounds, transaction visibility, prepare-conflict retry state, diagnostic key-order checks, and opportunistic eviction of pages with many deleted entries.

## Important APIs, types, and functions
- `__wt_btcur_next` is the public btree-cursor next implementation.
- `__cursor_row_next` iterates row-store insert slots and on-page rows in a unified slot namespace.
- `__cursor_var_next` iterates standard variable-length column-store records.
- `__cursor_var_append_next` iterates column-store append lists.
- `__wti_btcur_iterate_setup` initializes direction-independent iteration state after search or direction changes.
- Diagnostic builds add `__wti_cursor_key_order_check`, `__wt_cursor_key_order_init`, and `__wt_cursor_key_order_reset`.

## Control flow
`__wt_btcur_next` clears external key/value flags, initializes the cursor operation, optionally positions an unpositioned bounded cursor at its lower bound, initializes iteration state if changing direction, and then loops through the current page before walking to the next leaf. Column append lists are handled before normal column cells. Row traversal alternates odd insert-list slots and even on-page row slots. Column traversal advances record numbers through RLE cells, checks matching update insert lists, and skips large deleted RLE ranges by jumping to the next possible visible record.

Each candidate key is checked against upper bounds, then visibility is evaluated through `__wt_txn_read_upd_list` for insert/update lists or `__wt_txn_read` for on-page/history-store values. Tombstones and invalid updates are skipped, visible values are returned, and `WT_CURSTD_KEY_ONLY` can short-circuit value reads. If a page is exhausted, next may mark heavily deleted pages dirty and evict soon, then walks with snapshot-page skipping when possible.

## State and persistence behavior
This file updates cursor iteration fields such as `recno`, `slot`, `row_iteration_slot`, `ins_head`, `ins`, append/iterate flags, retry flags, cached RLE state, and diagnostic last-key state. It does not persist data directly, but it can mark pages dirty/evict-soon when traversal observes many globally visible tombstones so reconciliation can discard obsolete content. Read statistics and skip counters are updated.

## Dependencies and integration points
Forward traversal depends on row/column page formats, insert skip lists, transaction visibility and history-store reads, cursor bounds helpers in `bt_cursor.c`, tree walking, eviction, diagnostic debug tree dumps, collators, and page-skip helpers for snapshot isolation.

## Risks and edge cases
- RLE deleted ranges can be huge; the skip-jump logic is critical for performance and must not skip visible inserts.
- Prepare conflicts preserve retry state so user retry can continue from the same logical position.
- Direction changes rely on `__wti_btcur_iterate_setup` to map row-store positions into the shared slot namespace.
- Bounds positioning can return a record directly or require walking; diagnostic assertions verify lower-bound assumptions.
- Read-uncommitted traversal can observe out-of-order effects across page boundaries, so diagnostic order checks are reset in that case.

## Test signals
Tests should cover row and column next traversal, append lists, RLE values and deleted RLE gaps, insert-list visibility, tombstones, key-only cursors, lower/upper bounded next, prepare-conflict retry, direction changes with prev, snapshot page skipping, read-once `WT_READ_WONT_NEED`, deleted-page eviction triggers, and diagnostic key-order checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_curnext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_curprev.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_curprev.c

## Purpose
Implements reverse btree cursor traversal for row-store and variable-length column-store pages. It mirrors `bt_curnext.c` but adds reverse skip-list navigation, descending row-slot traversal, upper-bound positioning, lower-bound early exits, and reverse-specific prepare retry and diagnostic ordering behavior.

## Important APIs, types, and functions
- `__wt_btcur_prev` is the public btree-cursor previous implementation.
- `__cursor_skip_prev` moves backwards through an insert skip-list finger using search stacks.
- `__cursor_row_prev` iterates row-store insert and on-page entries backward.
- `__cursor_var_prev` iterates variable-length column-store records backward.
- `__cursor_var_append_prev` iterates column append lists backward.
- It reuses iteration setup and diagnostic key-order helpers from `bt_curnext.c`.

## Control flow
`__wt_btcur_prev` initializes cursor state, optionally positions an unpositioned bounded cursor at its upper bound, sets reverse tree-walk flags, and loops over append lists, current page content, and previous pages. On each page, column append entries are considered first when entering a new page. Standard column traversal decrements record numbers, searches the matching column cell, checks insert-list updates, reads on-page/history values, and jumps over deleted RLE ranges using the prior visible insert or RLE start. Row traversal descends the shared row iteration slot namespace and uses `__cursor_skip_prev` to move through insert lists.

`__cursor_skip_prev` reconstructs or adjusts the skip-list search stack so it points before the current insert. It uses acquire barriers to avoid weak-memory-order races with concurrent insert publication and restarts if the stack becomes inconsistent.

## State and persistence behavior
Reverse traversal updates the same cursor fields as forward traversal but in descending order. It tracks `page_deleted_count`, total skipped records, retry flags, append iteration flags, RLE cache state, and diagnostic last-key state. It can mark pages dirty and evict soon after encountering many globally visible tombstones, indirectly causing future reconciliation to clean obsolete content.

## Dependencies and integration points
The file depends on insert-list skip-stack conventions established by search, row/column page accessors, transaction visibility, history-store reads, bounds comparison/positioning, tree walk with `WT_READ_PREV`, eviction/page-dirty helpers, and diagnostic key-order helpers from next traversal.

## Risks and edge cases
- Reverse skip-list walking is concurrency-sensitive; acquire barriers and restart paths are essential to avoid skipping inserts.
- Deleted RLE jump logic must choose the largest update below the current record or the RLE start boundary.
- Bounds and prepare conflict handling differ subtly from forward traversal; retry flags must be cleared in the opposite direction.
- Row reverse traversal instantiates row leaf keys before walking a new page, which can add cost but is needed for backward key access.
- As with next, read-uncommitted isolation can require diagnostic order-check resets across page boundaries.

## Test signals
Tests should cover reverse row and column traversal, reverse append-list traversal, skip-list concurrent insert races, deleted RLE gap skipping, lower/upper bounded prev, prepare-conflict retry and direction switches, key-only cursors, snapshot page skipping, deleted-page eviction triggers, and diagnostic order checking.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_curprev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_cursor.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_cursor.c

## Purpose
Provides the core btree cursor operations above page traversal: search, search-near, insert, update, modify, reserve, remove, truncate, compare/equal, cursor reset/open/close, bounds positioning, validity checks, conflict checks, state save/restore, and optional eviction/reposition behavior.

## Important APIs, types, and functions
- `WT_CURFILE_STATE` stores external key/value/recno/flags so failed operations can restore cursor state.
- Search APIs: `__wt_btcur_search`, `__wt_btcur_search_near`, `__wt_btcur_search_prepared`.
- Mutation APIs: `__wt_btcur_insert`, `__wt_btcur_insert_check`, `__wt_btcur_remove`, `__wt_btcur_update`, `__wt_btcur_modify`, `__wt_btcur_reserve`.
- Range/compare APIs: `__wt_btcur_compare`, `__wt_btcur_equals`, `__wt_cursor_truncate`, `__wt_btcur_range_truncate`.
- Lifecycle APIs: `__wt_btcur_init`, `__wt_btcur_open`, `__wt_btcur_reset`, `__wt_btcur_close`, `__wt_btcur_free_cached_memory`.
- Helper families include bounds checks/positioning, valid-row/valid-column checks, search dispatch, modify dispatch, update-conflict checks, modify-chain full-update decisions, and evict-reposition.

## Control flow
Search localizes any pinned key, clears pinned values, checks bounds, optionally searches the pinned page, searches from the root when needed, validates visibility, returns key/value or key-only data, initializes diagnostic key-order state, and restores external state on failure. Search-near may reposition an out-of-bounds search key to the nearest bound, tries a row pinned-page optimization, searches from root, and if no valid exact record exists walks next then prev to find a neighbor.

Insert validates key/value sizes, disables bulk load, handles append-key allocation for column store, checks bounds, tries a pinned-page overwrite fast path, otherwise searches and either rejects duplicates or calls row/column modify. Remove and update share the pattern of pinned-page fast path, search with restart handling, conflict checking before visibility decisions, mutation through `__cursor_modify`, and state restoration on errors. Modify requires explicit snapshot transactions, materializes the current value, packs and applies modify entries, chooses a delta or full update based on value size and update-chain shape, and delegates to update. Reserve temporarily sets overwrite behavior and writes a reserve update.

Truncate logs the range when needed, then repeatedly searches/positions the start cursor, removes current records with the supplied remove function, advances with `next` in truncate mode, and stops at the end cursor or end of tree.

## State and persistence behavior
This file does not write blocks directly; persistence is through row/column modify calls that append updates/tombstones/reserve/modify records to page update chains. It carefully manages cursor external versus internal key/value flags, pinned pages, update values, retry state, overwrite/append flags, and transaction conflict checks. Truncate logs logical start/stop keys for recovery while in-memory updates are still tracked for rollback. Modify operations may persist compact delta updates or full values depending on chain state.

## Dependencies and integration points
The file integrates with row/column search and modify implementations, transaction visibility/conflict/autocommit code, history-store reads, cursor bounds comparison, next/prev traversal, eviction and hazard reset, btree bulk-load state, update-chain structures, truncate logging, collators, LSM insert-check behavior, prepared transaction resolution, and diagnostic format-test callbacks.

## Risks and edge cases
- Error paths must restore external cursor state while releasing pinned pages; `WT_CURFILE_STATE` correctness is central.
- Conflict checks must occur before visibility checks for remove/update or write conflicts can be missed.
- Pinned-page fast paths are disabled in several cases, including read-committed search and forced eviction, to avoid inconsistent results.
- Modify is restricted to explicit snapshot transactions because it relies on a stable current value.
- Bounds logic can reposition search-near and unpositioned next/prev; inclusive/exclusive bound handling has subtle exact-value cases.
- Truncate uses cursor positional equality for row-store fast paths, so cursors must be fully instantiated.

## Test signals
Tests should cover search/search-near with and without pinned pages, bounds inclusive/exclusive behavior, append inserts, overwrite and no-overwrite duplicate handling, update/remove conflict detection, prepared update resolution, reserve updates, modify in snapshot versus unsupported isolation/autocommit modes, modify-chain full-update thresholds, compare/equal for row and column stores, range truncate with logging and rollback, evict-reposition under snapshot isolation, and cursor close/free/reset memory behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_cursor.c -->

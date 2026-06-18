# subset-b-008992 research

Grouped research report for WiredTiger rollback-to-stable btree processing and schema lifecycle files. Each file section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_btree.c -->
# sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_btree.c

Purpose: implements the page-level rollback-to-stable mutation logic for row-store, variable-length column-store, and history-store btrees. It aborts unstable in-memory update chains, repairs unstable on-disk time windows by restoring older history-store records or installing tombstones, and marks modified pages dirty so reconciliation can persist the stable result.

Important APIs and functions: `__wti_rts_btree_abort_updates` is the exported page entry point called by the RTS tree walk. Internal helpers include `__rts_btree_abort_update` for update-chain pruning, `__rts_btree_abort_insert_list` for insert skip lists, `__rts_btree_ondisk_fixup_key` for history-store restoration, `__rts_btree_abort_ondisk_kv` for on-disk cell decisions, `__rts_btree_abort_col_var` for RLE column-store cells, and `__rts_btree_abort_row_leaf` for row leaf pages. `__rts_btree_row_modify` and `__rts_btree_col_modify` use btree cursor modify paths to prepend generated updates.

Control flow: the exported function first skips clean pages whose aggregate visibility says no rollback is needed. It then dispatches by page type. Update-chain processing scans from newest to oldest, aborting updates whose transaction id is not checkpoint-visible during recovery, whose durable timestamp exceeds the rollback timestamp, or whose prepare state is still in progress. Once a stable update is found, history-store flags may be cleared and newer history records for the key are deleted. On-disk processing checks the cell time window; unstable starts are replaced by a stable history-store version or tombstone, while unstable stops are cleared by restoring the original data-store value as an update. Column-store RLE processing optimizes by skipping deleted cells, cells where every recno has a stable update, and cells proven stable after the first checked recno.

State and persistence behavior: this file mutates only cache-resident page/update state immediately, but those changes are persistent once the page is reconciled. It sets update transaction ids to `WT_TXN_ABORTED`, creates `WT_UPDATE_STANDARD` and tombstone updates with restored timestamps, resets recovery-time transaction ids to `WT_TXN_NONE`, clears `WT_UPDATE_HS`/`WT_UPDATE_HS_MAX_STOP` where needed, removes history-store records through history cursors, and marks pages dirty. Dry-run mode marks candidate updates with `WT_UPDATE_RTS_DRYRUN_ABORT`, avoids data modifications, and frees generated updates.

Dependencies and integration points: depends on `rts_visibility.c` for transaction/page stability checks, `rts_history.c` for key-level history-store deletion, history-store cursor APIs (`__wt_curhs_open`, `__wt_curhs_search_near_before`), row/column modify primitives, time-window unpacking, timestamp/prepare metadata, and RTS statistics/verbose tags. It is called from `rts_btree_walk.c` with eviction-aware tree-walk flags and must cooperate with recovery mode, in-memory databases, history-store handles, and prepared-update semantics.

Risks: correctness relies on subtle timestamp ordering between data-store cells and history-store keys, especially with prepared transactions, max stop timestamps, obsolete tombstones, and checkpoint/eviction races. RLE column cells can cover many logical records, so off-by-one handling around insert recnos can lose or over-remove values. Dry-run and recovery paths must not leak generated updates or retain invalid transaction ids. History-store removals are destructive outside dry-run, so any visibility false positive risks data loss.

Test signals: rollback-to-stable tests should cover prepared commits/rollbacks, fast truncates, history-store restore from full values and modifies, in-memory rollback, variable column-store RLE cells, overflow-removed values, dry-run accounting, recovery checkpoint snapshots, and stats such as `txn_rts_upd_aborted`, `txn_rts_hs_removed`, `txn_rts_keys_removed`, and `txn_rts_keys_restored`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_btree_walk.c -->
# sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_btree_walk.c

Purpose: selects which btrees and pages need rollback-to-stable and drives the tree walk that invokes page-level rollback. It also implements RTS work-queue plumbing for parallel btree processing.

Important APIs and functions: `__wti_rts_btree_walk_btree_apply` evaluates a metadata entry and either processes or queues a btree. `__wti_rts_btree_walk_btree` rolls back the currently open btree. `__wti_rts_btree_work_unit`, `__wti_rts_pop_work`, and `__wti_rts_work_free` support worker threads. Internal helpers include `__rts_btree_walk_page_skip`, `__rts_btree_walk`, `__rts_btree`, `__rts_btree_int`, and `__rts_push_work`.

Control flow: metadata-level apply ignores non-btree, metadata, and history-store URIs, reads checkpoint metadata, computes maximum durable start/stop timestamp, detects prepared updates, captures newest transaction/write generation, and checks whether a cached dhandle is modified. If the object is dirty, has timestamps beyond stable, contains prepared updates, or was checkpointed with transactions newer than the recovery snapshot, it runs or queues rollback. The tree walk uses `WT_READ_NO_EVICT`, `WT_READ_VISIBLE_ALL`, `WT_READ_WONT_NEED`, and `WT_READ_SEE_DELETED`, emits progress periodically, and calls `__wti_rts_btree_abort_updates` on leaf refs. The page-skip callback skips stable on-disk pages and stable committed fast-deleted pages but instantiates unstable or prepared deleted pages.

State and persistence behavior: this file does not directly rewrite records; it opens/releases dhandles, enqueues `WT_RTS_WORK_UNIT` entries, increments progress counters, updates skip/process stats, and after a successful btree walk resets `btree->rec_max_txn` and `btree->rec_max_timestamp` so later reconciliation sees only stable data. It can truncate history-store entries for skipped non-timestamped btrees.

Dependencies and integration points: integrates with metadata checkpoint config parsing, handle-list locks, RTS thread-group condition variables, tree-walk APIs, page visibility checks from `rts_visibility.c`, page mutation from `rts_btree.c`, and history truncation from `rts_history.c`. It treats logged btrees and checkpoint handles as out of scope, and handles missing/corrupt files as skip conditions.

Risks: skip decisions are high impact because a false skip leaves unstable data behind. The checkpoint write-generation/newest-transaction test is recovery-specific and depends on correct metadata. Page-delete locking must restore the ref state exactly. Queue management must not lose work under concurrent RTS worker threads. Progress reporting relies on approximate page position and should not affect tree-walk state.

Test signals: useful coverage includes metadata-only skip decisions, dirty cached handles, prepared fast truncate pages, deleted-page skip cases, missing file and corruption skip handling, threaded and single-thread RTS paths, non-timestamped history-store truncation, progress counter movement, and logged/checkpoint handle no-op behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_btree_walk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_history.c -->
# sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_history.c

Purpose: contains history-store cleanup operations used by rollback-to-stable, including key-range deletion, whole-btree truncation, and the final pass that rolls back the history store itself.

Important APIs and functions: `__wti_rts_history_delete_hs` deletes history-store records for the current btree/key until it reaches a stable stop timestamp. `__wti_rts_history_btree_hs_truncate` truncates all history-store records for a btree id. `__wti_rts_history_final_pass` evaluates history-store checkpoint metadata and invokes the normal btree rollback walk on the history-store file when required.

Control flow: key deletion opens a history-store cursor for `S2BT(session)->id`, reads all committed history records for the key from newest backwards via `__wt_curhs_search_near_before`, and removes records whose stop timestamp is greater than the stable data-store timestamp. Whole-btree truncation delegates to `__wt_hs_btree_truncate` unless RTS is in dry-run mode. The final pass loads `WT_HS_URI` metadata, scans checkpoint entries for newest stop durable and newest stop timestamps, opens the history-store dhandle, and calls `__wti_rts_btree_walk_btree` if the history store is dirty or newer than the rollback timestamp. Partial backup restore additionally truncates ids listed in `backup.partial_remove_ids`.

State and persistence behavior: the file removes rows from the history store and increments RTS/history-store stats. Dry-run mode preserves records while still accounting. Final-pass processing can mutate the history-store btree through the same page rollback machinery used for data files. Metadata strings and dhandles are opened and released locally.

Dependencies and integration points: depends on history-store cursor APIs, metadata search/config parsing, `rts_btree_walk.c` for btree walking, connection backup partial-restore state, and RTS stats/verbose tags. It is called from `rts_btree.c` when a stable data-store update requires trimming newer history records and from top-level RTS sequencing for history-store cleanup.

Risks: deletion boundaries are timestamp-sensitive: stopping too early leaves unstable history, while deleting too far can remove versions needed for stable reads. The final pass uses history-store-specific max timestamp calculation because prepared updates can have unusual stop metadata. Best-effort truncation during partial restore must not hide serious corruption in normal operation.

Test signals: cover history-store key deletion around exact stable timestamps, globally visible starts, dry-run behavior, non-timestamped btree truncation, history-store final pass with dirty and clean metadata, prepared history records, and partial backup restore remove-id truncation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_history.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_visibility.c -->
# sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_visibility.c

Purpose: centralizes RTS visibility predicates used to decide whether update chains, transactions, and pages contain unstable content that must be rolled back.

Important APIs and functions: `__wti_rts_visibility_has_stable_update` detects a surviving non-aborted update in a processed chain. `__wti_rts_visibility_txn_visible_id` evaluates transaction-id visibility against the recovered checkpoint snapshot during recovery. `__wti_rts_visibility_page_needs_abort` inspects page/ref reconciliation metadata and returns whether a page must be read and processed. The static `__rts_visibility_get_ref_max_durable_timestamp` applies history-store-specific aggregate timestamp rules.

Control flow: transaction visibility is trivial outside recovery, true when no checkpoint snapshot exists, and otherwise delegates to snapshot-id visibility. Page visibility first treats in-memory btrees as needing rollback. It then checks reconciled replace and multiblock page-modify results, instantiated deleted-page metadata, on-page address cells, or off-page addresses. For each source it computes the relevant maximum durable timestamp, prepared flag, newest transaction id, and returns true if the durable timestamp exceeds rollback, prepared updates exist, or recovery transaction checks demand rollback.

State and persistence behavior: this file is read-only except for verbose logging. It reads `WT_REF`, `WT_PAGE_MODIFY`, `WT_ADDR`, `WT_TIME_AGGREGATE`, `WT_PAGE_DELETED`, btree flags, and connection recovery snapshot state.

Dependencies and integration points: used by page-skip logic in `rts_btree_walk.c` and update/on-disk processing in `rts_btree.c`. It depends on checkpoint aggregate metadata semantics, transaction snapshot helpers, history-store URI/handle detection, and recovery flags such as `WT_CHECK_RECOVERY_FLAG_TXNID`.

Risks: false negatives leave unstable content unread; false positives cause extra page reads and can instantiate deleted pages unnecessarily. History-store max timestamp rules differ from data-store rules, so sharing logic without the HS branch would miss prepared records. Recovery snapshot handling must match checkpoint metadata generation.

Test signals: validate page-needs-abort for in-memory trees, replace and multiblock reconciliation, instantiated fast-deleted pages, on-page/off-page addresses, prepared aggregate flags, recovery newest transaction checks, history-store aggregate timestamp behavior, and no-snapshot recovery visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_visibility.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_alter.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_alter.c

Purpose: implements `WT_SESSION::alter` across files, tables, column groups, indexes, tiered trees, tiered objects, and tiered object ranges by rewriting metadata atomically under schema/checkpoint locks.

Important APIs and functions: `__wt_schema_alter` obtains an internal session and metadata tracking. `__schema_alter` dispatches by URI type. Core helpers include `__alter_apply`, `__alter_file`, `__alter_tier`, `__alter_object`, `__alter_tree`, `__alter_table`, `__alter_tiered`, `__alter_get_object_id_range`, and `__alter_objects`.

Control flow: metadata update starts with the relevant base metadata config, overlays existing metadata and user config, collapses the result, and updates only if changed. File and tier alteration use exclusive lock-only handle operations. Index and column-group alteration first alter their underlying data-source URI and then their own metadata. Table alteration with `exclusive_refreshed=true` opens the table exclusively, locks it in meta tracking, updates all column groups and indexes, then updates table metadata. Tiered alteration closes handles when exclusive, opens the tiered handle, alters local/shared tiers and all object metadata in the oldest-current id range, then updates tiered metadata.

State and persistence behavior: persistent state is the WiredTiger metadata table; handle locks are tracked so rollback can release or restore state on failure. The function can skip actual metadata writes when the collapsed configuration is unchanged and increments `session_table_alter_skip`.

Dependencies and integration points: depends on schema locks, checkpoint lock, metadata search/update, config collapse, handle-operation helpers, table/index/column-group open helpers, tiered naming, and meta tracking. It assumes callers already hold the necessary global schema/checkpoint serialization.

Risks: non-exclusive alter is allowed only for simple table metadata; applying it elsewhere would leave open handles with stale in-memory configuration. Recursive alteration of column-group/index sources must remain atomic with parent metadata. Tiered object ranges can be sparse, so missing object metadata is expected and must not abort. Any base-config omission can drop defaulted metadata fields during collapse.

Test signals: alter simple and complex tables, indexes, column groups, files, tiers, tiered trees with sparse object ranges, unchanged config skip stats, exclusive-refreshed rejection for unsupported URI types, and failure rollback through metadata tracking.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_alter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_create.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_create.c

Purpose: implements `WT_SESSION::create` for WiredTiger schema objects: files, tables, column groups, indexes, layered/disaggregated tables, tiered objects, tiered trees, and custom data sources. It also handles import metadata, file-id allocation, timestamp safety checks, and metadata tracking for atomic schema creation.

Important APIs and functions: `__wt_schema_create` is the exported wrapper using an internal session. `__schema_create` validates config, enables meta tracking, sets import state, and dispatches by URI prefix. Major helpers include `__create_file`, `__create_colgroup`, `__create_index`, `__create_table`, `__create_layered`, `__create_tiered`, `__create_object`, `__create_tiered_tree`, `__create_data_source`, `__wt_generate_file_id`, `__wt_find_import_metadata`, `__create_parse_export`, `__create_fix_file_ids`, and `__check_imported_ts`.

Control flow: file create checks unsupported formats, existing metadata, import options, block-manager creation, file-id/version metadata, checkpoint-lsn stripping, import repair, timestamp safety, and exclusive handle open. Table create inserts table metadata, creates a default column group when needed, opens the table to validate it, and enqueues disaggregated metadata for layered tables. Column-group create resolves table membership, source URI, key/value formats, source creation, and column-group metadata. Index create opens the table, derives hidden primary-key columns, builds source key/value formats, creates the backing source, inserts index metadata, opens the index, and bulk-fills it from existing table data. Layered create builds ingest/stable constituent URIs and metadata, creates in-memory ingest and leader stable components, and enqueues shared metadata. Tiered create writes stripped tiered metadata and opens the tiered handle.

State and persistence behavior: mutates metadata, creates physical block-manager files or disaggregated manager placeholders, assigns namespaced btree ids, may read export metadata files into `session->import_list`, updates imported ids, opens/locks dhandles, enqueues shared metadata operations, and fills secondary indexes with table data. Meta tracking protects multi-object creation so failures can roll back created files and metadata. Import mode deliberately avoids tracking physical data-file removal.

Dependencies and integration points: depends on config parsing/collapse/merge, metadata APIs, block manager and disaggregated page-log/storage configuration, btree id namespace constants, import repair, checkpoint metadata parsing, table/index planning helpers from `schema_plan.c`, open helpers from `schema_open.c`, cursor/index application APIs, tiered naming/storage, and custom `WT_DATA_SOURCE` callbacks.

Risks: this is a high-blast-radius file. File-id generation must not collide across local/shared/special namespaces. Import timestamp checks can reject unsafe imports, but relaxed stable-timestamp import still lacks migrated history. Metadata-file import prefix matching can include overlapping names and relies on later exact lookup/dispatch. Index creation must preserve hidden primary-key columns and reject record-number index keys. Layered and disaggregated paths are sensitive to leader/follower behavior, unpublished schema epochs, logging disabled requirements, and page-log configuration.

Test signals: create file/table/index/colgroup combinations, existing-object exclusive behavior, import with file metadata, import repair, metadata-file import id remapping, timestamp rejection against oldest/stable, secondary index backfill, tiered shared table column groups, layered table creation on leader/follower disaggregated setups, custom data source validation, unsupported FLCS format rejection, and meta-tracking rollback after injected crash points.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_drop.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_drop.c

Purpose: implements `WT_SESSION::drop` for schema objects, including physical file removal scheduling, metadata cleanup, history-store truncation, layered shared-metadata removal, and tiered object cleanup.

Important APIs and functions: `__wt_schema_drop` wraps an internal session. `__schema_drop` enables meta tracking, parses force config, dispatches by URI type, and maps missing-object errors. Helpers include `__drop_file`, `__drop_colgroup`, `__drop_index`, `__drop_table`, `__drop_layered`, `__drop_issue_trim`, and `__drop_tiered`.

Control flow: file drop checks backup conflicts, closes dhandles under the handle-list write lock, records the file id for history-store truncation, removes metadata, schedules physical removal when configured, and best-effort truncates the history store. Column-group and index drop detach through their owning table/index metadata and recursively drop backing sources. Table drop opens the table exclusively to force cursor closure, reopens normally for schema traversal, drops incomplete simple-table files if needed, drops column-group and index sources before metadata entries, marks the table handle discarded, and removes table metadata. Layered drop may issue a page-log trim on the leader, enqueues shared metadata removal, drops stable and ingest constituents, then removes top-level layered metadata. Tiered drop closes tiered handles under the tiered lock, removes local/shared tier metadata and historical object metadata, schedules local/shared object deletion as configured, and removes queued tiered work.

State and persistence behavior: persistent mutations include metadata removals, queued physical file/object removals through meta tracking, shared metadata operations for disaggregated storage, history-store truncation, and tiered work-queue cleanup. During recovery/partial restore, meta tracking may avoid sync requirements because recovery ends with a checkpoint.

Dependencies and integration points: depends on schema/table locks, handle-list locks, backup conflict checks, metadata APIs, meta tracking, history-store truncation, table/index open helpers, tiered naming/storage queues, layered page-log trim, disaggregated shared metadata queue, and data-source `drop` callbacks.

Risks: drop ordering is critical: backing sources are removed before parent metadata to avoid inconsistent schemas, but failure between steps must be recovered by meta tracking. Force drop is intentionally unsupported for complex tables. Tiered shared-object deletion can affect external storage and is gated by `remove_files`/`remove_shared`. Follower layered drops tolerate missing stable local files, but leaders must not. Best-effort history truncation failure is logged rather than fatal.

Test signals: drop simple and complex tables, incomplete table cleanup after crash, busy handle and backup conflict sub-errors, force semantics, index/column-group recursive source drop, layered leader/follower drop behavior, tiered local/shared object cleanup and queued work removal, history-store truncate for dropped file ids, and recovery/partial-restore drop paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_drop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_list.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_list.c

Purpose: provides schema handle lookup/release and destruction helpers for tables, tiered handles, column groups, indexes, and layered table resources.

Important APIs and functions: exported helpers include `__wti_schema_get_tiered_uri`, `__wti_schema_release_tiered`, `__wt_schema_get_table_uri`, `__wt_schema_get_table`, `__wti_schema_release_table_gen`, `__wt_schema_release_table`, `__wti_schema_destroy_colgroup`, `__wti_schema_destroy_index`, `__wt_schema_close_table`, `__wt_schema_close_layered`, and `__wt_schema_destroy_layered`.

Control flow: table/tiered lookup saves the current dhandle, opens the requested dhandle with supplied flags, validates incomplete column-group state when requested, returns the typed handle, and restores the caller's dhandle pointer. Release helpers switch to the handle's dhandle and call session release, with optional visibility checks. Destroy helpers free owned names/config/source strings and terminate owned collators. Table close frees plans/formats, column groups, index arrays, resets completion flags, and asserts table-write lock or connection closing. Layered close removes the ingest btree from the layered manager and frees copied config strings; destroy also clears truncate state and destroys the rwlock.

State and persistence behavior: no metadata or disk state is written. The file manages in-memory schema object lifetimes, dhandle references, collator termination side effects, table completeness flags, and layered manager membership.

Dependencies and integration points: used throughout schema create/open/drop/alter/stat code to obtain and release schema handles safely. It depends on session dhandle APIs, table lock flags, collator ABI, layered table manager, and memory ownership conventions for `WT_TABLE`, `WT_INDEX`, `WT_COLGROUP`, and `WT_LAYERED_TABLE`.

Risks: dhandle save/restore is subtle; leaving `session->dhandle` changed can corrupt callers. Releasing tables with the wrong visibility setting can break concurrent schema operations. Index destruction must terminate only owned collators. Table close requires the table write lock to avoid races with cursor open or schema sweeps.

Test signals: handle leak checks, table lookup with incomplete column groups, release with visibility checks, index collator termination, table close during normal schema change and connection close, layered open/close manager membership, and memory sanitizer coverage for repeated open/drop cycles.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_open.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_open.c

Purpose: opens and validates in-memory schema structures for tables, column groups, indexes, layered tables, page logs, and storage sources, and rejects removed fixed-length column-store formats.

Important APIs and functions: `__wti_schema_open_colgroups`, `__wt_schema_open_index`, `__wt_schema_open_indices`, `__wt_schema_open_table`, `__wt_schema_open_layered`, `__wt_schema_open_page_log`, `__wt_schema_open_storage_source`, `__wt_schema_get_colgroup`, `__wti_schema_get_index`, `__wt_schema_tiered_shared_colgroup_name`, and `__wt_schema_unsupported_format`. Internal helpers include `__schema_colgroup_name`, `__open_index`, `__schema_open_index`, `__schema_open_table`, `__schema_open_layered`, and `__schema_open_layered_ingest`.

Control flow: table open parses key/value formats, column config, simplicity, column-group list, shared-tiered marker, allocates column-group slots, and opens column groups. Column-group open builds metadata URIs, tolerates missing metadata for incomplete tables, loads source and column config, checks complex-table coverage, and builds the projection plan. Index open scans metadata keys under `index:<table>:` in sorted order, synchronizes the table's in-memory index array with metadata, loads source/collator/formats, derives key and value projection plans, and sets completion flags after a full pass. Layered open validates disaggregated storage, rejects custom collators, loads key/value/ingest/stable URIs, opens the ingest table to record its btree id, and registers it with the layered manager.

State and persistence behavior: this file builds in-memory schema caches and manager registrations. It does not write metadata. It may allocate and free table/index/column-group structures, set completion flags, store projection strings, set immutable index flags, and add layered ingest ids to the manager.

Dependencies and integration points: depends on metadata cursors, config parsing, table write locks, read-uncommitted schema reads, collator configuration, format/planning helpers from `schema_plan.c`, layered manager APIs, extension queues for page logs/storage sources, and dhandle APIs for constituent opens.

Risks: index-array synchronization uses sorted metadata traversal and memmove; ordering mistakes can leak or stale indexes. Opening indexes before column groups are complete intentionally validates without caching. Layered shutdown needs the ingest btree id even while handles are being swept. The FLCS unsupported-format check must run during create/open upgrades to prevent use of removed formats.

Test signals: open simple and complex tables, incomplete tables, tiered shared column groups, index creation/open with collators and hidden primary-key columns, dropped-index synchronization, page-log/storage-source lookup failures, layered table open in disaggregated and non-disaggregated connections, and FLCS create/open rejection messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_plan.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_plan.c

Purpose: validates table column definitions and builds compact projection/format plans that map logical table columns to key/value columns in column groups and indexes.

Important APIs and functions: `__wti_schema_colcheck` verifies that named columns match key/value formats. `__wti_table_check` ensures every non-key column appears in a column group. `__wt_struct_plan` builds projection-plan strings. `__wt_struct_reformat` derives a format string for selected columns and optional hidden columns. `__wti_struct_truncate` returns the first N fields of a packing format. Internal helpers `__find_next_col` and `__find_column_format` locate column positions and packing types.

Control flow: column checking counts pack fields from key and value formats, counts configured column names, and rejects mismatches. Table checking skips key columns and verifies each value column can be found in a column group. Plan building iterates requested columns, finds their next matching location, emits column-group/key/value switch markers, skip counts, next/reuse operations, and handles duplicate columns by reusing values. Reformatting walks requested and extra columns, finds original packing types, and adjusts raw item `u`/`U` sizing when moving raw fields between final and non-final positions.

State and persistence behavior: no persistent state is changed. Output is appended into caller-provided `WT_ITEM` buffers and later stored in in-memory table/index plans or metadata-derived format strings.

Dependencies and integration points: used by schema create/open and projection execution. It depends on WiredTiger packing parser helpers, config parsers, table/column-group structures, projection op constants (`WT_PROJ_KEY`, `WT_PROJ_VALUE`, `WT_PROJ_SKIP`, `WT_PROJ_NEXT`, `WT_PROJ_REUSE`), and buffer utilities.

Risks: projection strings are interpreted by `schema_project.c`; any encoding mismatch corrupts cursor key/value packing. Duplicate column names and columns appearing in multiple groups require careful "next match" handling. Raw `u`/`U` conversion is easy to get wrong and can produce incompatible packed values. Empty plans and empty column lists are special cases.

Test signals: complex tables with multiple column groups, duplicate columns, key columns excluded from column-group values, index hidden primary-key columns, raw item fields in middle/end positions, empty projection plans, record-number formats, and round trips through project-in/out/merge/slice.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_plan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_project.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_project.c

Purpose: executes projection plans produced by schema planning code, moving packed key/value fields between application varargs, dependent cursors, raw value buffers, and merged output buffers.

Important APIs and functions: `__wt_schema_project_in` reads application varargs into the key/value buffers of dependent cursors. `__wt_schema_project_out` reads dependent cursor buffers back into application varargs. `__wt_schema_project_slice` projects from a raw packed value into cursor buffers, optionally key-only. `__wt_schema_project_merge` merges fields from dependent cursors into a single packed output buffer.

Control flow: all functions parse a compact plan string of cursor indices plus projection op characters. Key/value switch ops select the target cursor buffer and initialize the correct pack format, with record-number cursors using `"R"`. Skip ops advance or append default values for out-of-order insertion. Next ops consume a new application or raw value and write/read it once. Reuse ops read the same previously consumed value into another projected location without advancing the source varargs/value. Buffer edits preserve existing packed content by unpacking old fields, growing buffers, memmoving tail bytes, and rewriting fields in place.

State and persistence behavior: mutates `WT_CURSOR` key/value buffers and output `WT_ITEM` buffers only. It does not write metadata or storage directly, but its packed results are later used by cursor insert/update/search operations.

Dependencies and integration points: depends on projection plan strings from `schema_plan.c`, pack/unpack helpers, `WT_PACK_GET`/`WT_UNPACK_PUT` vararg macros, cursor key/value formats, record-number cursor conventions, and buffer growth utilities. Table, index, and column-group cursors use these helpers to expose logical table projections over physical stores.

Risks: plan parsing uses `strtoul` with embedded op chars, so malformed plans can desynchronize parsing. In-place packed-buffer edits are offset-sensitive and must preserve record-number key storage. Raw value projection must maintain compatible pack types between source and destination. Key-only slice mode must skip value writes without consuming the wrong plan state.

Test signals: projection round trips for multi-column tables, duplicate/reused columns, out-of-order inserts that append default values, record-number keys, raw `u`/`U` fields, key-only index extraction, merge/slice compatibility, and malformed plan assertions in diagnostic builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_project.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_publish.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_publish.c

Purpose: publishes table or layered schema changes at a requested disaggregated schema epoch.

Important APIs and functions: `__wt_schema_publish` parses `disaggregated.schema_epoch` from session publish config and calls the internal `__schema_publish_disagg_schema_epoch`.

Control flow: publishing requires the schema lock. The internal helper rejects epoch zero, rejects non-disaggregated connections, takes the transaction-global read lock to synchronize with stable schema epoch advancement, checks that the requested epoch is newer than any stable schema epoch, and queues publication by stripped table/layered name. Only `table:` and `layered:` URIs are supported.

State and persistence behavior: this file does not directly mutate local metadata. It enqueues shared metadata publication work through `__wt_disagg_shared_metadata_queue_publish`; that queue is the durable/integration path for disaggregated shared metadata visibility.

Dependencies and integration points: depends on schema lock ownership, transaction-global rwlock ordering, stable disaggregated schema epoch accessors, timestamp parsing, disaggregated connection detection, and shared metadata queue APIs.

Risks: publishing with an epoch older than the stable schema epoch would expose stale schema state and is explicitly rejected. Lock ordering must remain table/schema lock before transaction-global read lock. Unsupported URI types must fail clearly because only table/layered shared metadata names are enqueued.

Test signals: publish with zero epoch, older/equal/newer epochs, non-disaggregated connections, table and layered URI success, unsupported URI failure, and races with stable schema epoch advancement.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_publish.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_stat.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_stat.c

Purpose: initializes statistics cursors for schema-level objects by resolving table, column-group, and index URIs to the underlying statistics sources and aggregating component statistics when needed.

Important APIs and functions: `__wt_curstat_colgroup_init`, `__wt_curstat_index_init`, and `__wt_curstat_table_init` are the public initialization helpers. The static `__curstat_size_only` implements a fast path for table size-only stats on simple tables.

Control flow: column-group and index stats resolve the schema object, build `statistics:<source>`, and delegate to `__wt_curstat_init`. Table stats first try the size-only fast path when `WT_STAT_TYPE_SIZE` is set: it reads table metadata directly, confirms there are no named columns, detects layered tables, builds the underlying local filename or disaggregated stable-file URI, and asks the local/disagg size helper. If fast path does not complete, normal table stats open the table. Simple tables redirect to their single column group's statistics. Complex tables open statistics cursors for each column group, copy the first stats block, aggregate subsequent column groups and indexes, and finalize the aggregate.

State and persistence behavior: read-only with respect to metadata and data files. It initializes in-memory cursor stats structures and may open/close component statistics cursors. The fast path avoids schema/table-list locks when possible to reduce pressure under workloads with many create/drop operations.

Dependencies and integration points: depends on schema object lookup helpers, metadata search/config parsing, table open/index open code, statistics cursor initialization/open APIs, local and disaggregated size helpers, and data-source statistics aggregation/finalization functions.

Risks: the size-only fast path infers simple-table layout from metadata and must fall back cleanly on concurrent schema changes or unsupported layouts. Complex aggregation assumes compatible `WT_DSRC_STATS` layouts across column groups and indexes. Layered table size naming must match stable constituent metadata conventions.

Test signals: stats on column groups, indexes, simple tables, complex tables with multiple column groups and indexes, size-only fast path success/fallback, concurrent create/drop fallback, layered/disaggregated size stats, and aggregate finalization correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_stat.c -->

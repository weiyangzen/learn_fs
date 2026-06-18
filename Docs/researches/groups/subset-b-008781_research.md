# Research Group subset-b-008781

This grouped report covers the SQLite pager and page-cache source files assigned to `subset-b-008781`. Each file section is delimited for the reconciliation lane and mirrors the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/pager.h -->
# sources/storage-engines/sqlite/src/pager.h

## Purpose

`pager.h` is the public internal interface for SQLite's pager subsystem. The pager sits between btree/database logic and the VFS/page-cache layers. It reads and writes database files one page at a time, manages rollback journal or WAL modes, owns transactional state transitions, exposes page reference operations, and provides configuration hooks for cache size, page size, synchronous behavior, locking, mmap, savepoints, and checkpointing.

This header does not define the `Pager` structure itself. It declares the opaque `Pager` handle and the `DbPage` alias for `PgHdr`, so callers can manipulate pages without depending on pager internals. Its constants intentionally mirror API-visible behavior such as `PRAGMA journal_mode` values and btree open flags.

## Important APIs, Types, and Constants

The core types are `Pgno`, `Pager`, and `DbPage`. `Pgno` is a 32-bit page number with page 1 as the first valid database page and 0 reserved for "not a page". `Pager` is an opaque per-open-file manager. `DbPage` is a page handle backed by `PgHdr` from the pcache layer.

Open and close are handled by `sqlite3PagerOpen()`, `sqlite3PagerClose()`, and `sqlite3PagerReadFileheader()`. Pager configuration includes `sqlite3PagerSetPagesize()`, `sqlite3PagerMaxPageCount()`, `sqlite3PagerSetCachesize()`, `sqlite3PagerSetSpillsize()`, `sqlite3PagerSetMmapLimit()`, `sqlite3PagerSetFlags()`, `sqlite3PagerLockingMode()`, `sqlite3PagerSetJournalMode()`, `sqlite3PagerJournalSizeLimit()`, and `sqlite3PagerFlush()`.

Page access is through `sqlite3PagerGet()`, `sqlite3PagerLookup()`, `sqlite3PagerRef()`, `sqlite3PagerUnref()`, `sqlite3PagerUnrefNotNull()`, and `sqlite3PagerUnrefPageOne()`. Mutating a page requires `sqlite3PagerWrite()`, after which `sqlite3PagerDontWrite()` and `sqlite3PagerMovepage()` can adjust persistence behavior or page identity. `sqlite3PagerGetData()` and `sqlite3PagerGetExtra()` bridge from pager pages to page data and btree-owned extra storage.

Transaction and durability APIs include `sqlite3PagerBegin()`, `sqlite3PagerCommitPhaseOne()`, `sqlite3PagerSync()`, `sqlite3PagerCommitPhaseTwo()`, `sqlite3PagerRollback()`, `sqlite3PagerOpenSavepoint()`, `sqlite3PagerSavepoint()`, `sqlite3PagerSharedLock()`, and `sqlite3PagerExclusiveLock()`. WAL builds add `sqlite3PagerCheckpoint()`, `sqlite3PagerWalSupported()`, `sqlite3PagerWalCallback()`, `sqlite3PagerOpenWal()`, `sqlite3PagerCloseWal()`, and optional snapshot functions.

Key constants include `PAGER_OMIT_JOURNAL`, `PAGER_MEMORY`, `PAGER_LOCKINGMODE_*`, `PAGER_JOURNALMODE_*`, `PAGER_GET_NOCONTENT`, `PAGER_GET_READONLY`, and `PAGER_SYNCHRONOUS_*`. `PAGER_SJ_PGNO()` identifies the special journal page number used to mark a super-journal name payload.

## Control Flow and State

Typical control flow starts with `sqlite3PagerOpen()`, then configuration, then shared locking and page fetches. Read-only paths fetch pages with `sqlite3PagerGet()` or `sqlite3PagerLookup()`, increment or release references, and inspect page data. Write paths call `sqlite3PagerBegin()`, fetch a page, call `sqlite3PagerWrite()` to journal and mark it writable, update the page buffer, then commit through phase one, sync, and phase two, or roll back through `sqlite3PagerRollback()`.

The pager state machine is represented behind the opaque `Pager` type, but the API reveals its key transitions: lock acquisition, page-cache population, journal-mode selection, savepoint creation and rollback, write preparation, sync, commit finalization, and cache truncation. The `PAGER_GET_*` flags allow callers to avoid disk reads when the caller will overwrite page content or to accept a read-only page.

## Persistence Behavior

Persistence is controlled by journal mode, synchronous flags, locking mode, and savepoint state. Rollback journal modes include delete, persist, truncate, memory, and off; WAL mode is exposed when WAL is compiled in. Synchronous values map to `PRAGMA synchronous`, and additional bits map to fullfsync, checkpoint fullfsync, and cache spill. `sqlite3PagerDontWrite()` allows a page to remain dirty in memory while avoiding a database-file write in cases where pager invariants make the write unnecessary. `sqlite3PagerTruncateImage()` changes the pager's view of database size before the database file is physically truncated.

## Dependencies and Integration Points

`pager.h` depends on SQLite core types from `sqliteInt.h`, VFS handles (`sqlite3_vfs`, `sqlite3_file`), btree-compatible flags, the pcache `PgHdr` type, backup handles, WAL support, and optional snapshot/SEH/ZIPVFS features. Btree code uses this API for page-level transactional access. PRAGMA code configures pager modes and durability using these declarations. WAL and checkpoint subsystems use the WAL-specific functions. Test builds use `sqlite3PagerStats()`, `sqlite3PagerRefdump()`, and simulated I/O error toggles.

## Risks and Edge Cases

The numeric journal-mode values are API-visible and cannot be renumbered without compatibility breakage. `PAGER_OMIT_JOURNAL` and `PAGER_MEMORY` must match btree flags. Misuse of `sqlite3PagerWrite()` can corrupt persistence semantics because page buffers must be journaled before modification. Locking mode and WAL transitions require careful sequencing, and `sqlite3PagerOkToChangeJournalMode()` exists to guard unsafe changes. `PAGER_SJ_PGNO` depends on page size and the pending-byte location, so page-size changes interact with journal interpretation.

## Test Signals

Useful tests include transaction commit and rollback across all rollback journal modes, WAL open/close/checkpoint behavior, savepoint rollback of dirty pages, page-size changes with no outstanding references, mmap/direct-overflow reads, `PRAGMA synchronous` and `journal_mode` conformance, simulated I/O errors, power-loss style journal sync tests, lock timeout behavior when enabled, and reference-count sanity checks under debug builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/pager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/parse.y -->
# sources/storage-engines/sqlite/src/parse.y

## Purpose

`parse.y` is SQLite's Lemon grammar for SQL parsing. Lemon translates it into C code for `sqlite3Parser`, and the grammar actions directly build SQLite AST and schema/DML objects using the `Parse *pParse` context. This file is not a passive syntax declaration; reductions call functions such as `sqlite3StartTable()`, `sqlite3SelectNew()`, `sqlite3Insert()`, `sqlite3Update()`, `sqlite3DeleteFrom()`, `sqlite3CreateIndex()`, `sqlite3BeginTrigger()`, `sqlite3WindowAlloc()`, and many expression constructors.

The grammar covers transactions, savepoints, table/view/index/trigger/virtual-table DDL, SELECT including compound SELECT and VALUES, INSERT/UPSERT/RETURNING, UPDATE/DELETE with optional limited forms, expressions, functions, subqueries, CTEs, window functions, PRAGMA, VACUUM, ATTACH/DETACH, REINDEX, ANALYZE, and ALTER TABLE extensions.

## Important APIs, Types, and Grammar Constructs

Parser setup uses `%token_prefix TK_`, `%token_type {Token}`, `%default_type {Token}`, `%extra_context {Parse *pParse}`, `%syntax_error`, `%stack_overflow`, and `%name sqlite3Parser`. Parser stack memory is controlled by `parserStackRealloc()`, `parserStackFree()`, and `parserStackSizeLimit()`, the latter using `SQLITE_LIMIT_PARSER_DEPTH`.

Embedded helper types include `struct TrigEvent` and `struct FrameBound`. Helper functions include `parserSyntaxError()`, `disableLookaside()`, `updateDeleteLimitError()` for capable parsers without enabled limited UPDATE/DELETE, `parserDoubleLinkSelect()`, `attachWithToSelect()`, `tokenExpr()`, `sqlite3ExprAddOrderedsetFunction()`, `sqlite3PExprIsNull()`, `sqlite3PExprIs()`, and `parserAddExprIdListTerm()`.

Key nonterminals carry typed semantic values: `select`, `oneselect`, `expr`, `term`, `exprlist`, `sortlist`, `seltablist`, `fullname`, `xfullname`, `setlist`, `upsert`, `idlist`, `eidlist`, `wqlist`, `window`, `frame_bound`, and `trigger_cmd`. `%destructor` rules free AST fragments if parse errors or stack unwinding leave them unused.

Token declarations and precedence are deliberately ordered. Operator tokens are clustered so code generator assumptions in expression evaluation remain valid. `TK_SPACE`, `TK_COMMENT`, and `TK_ILLEGAL` are declared last for tokenizer expectations. A compile-time check rejects grammars where synthesized tokens exceed the 255-token boundary through `TK_SPAN`.

## Control Flow

Input reduces as `input ::= cmdlist`, with each statement reducing through `cmdx ::= cmd` and then `sqlite3FinishCoding(pParse)`. Transaction commands call transaction helpers directly. DDL reductions disable lookaside for schema objects that may outlive one connection and then call schema builders. SELECT reductions build `Select` chains, link compound SELECT nodes with `parserDoubleLinkSelect()`, enforce compound SELECT limits, and attach `WITH` objects when present.

DML reductions build source lists, expression lists, WHERE and RETURNING clauses, then dispatch to the corresponding code generator. UPDATE with a FROM clause normalizes multi-source FROM into a nested SELECT source before appending it to the target source list. INSERT handles `DEFAULT VALUES`, SELECT input, UPSERT chains, and RETURNING.

Expression parsing builds `Expr` nodes for literals, identifiers, dotted names, variables, function calls, vectors, unary/binary operators, LIKE/MATCH infix functions, BETWEEN, IN, subqueries, EXISTS, CASE, CAST, COLLATE, ordered-set aggregate syntax, filters, and window attachments. Several reductions perform early normalization, such as `expr IN ()` to constants when safe, single-constant `IN` to equality, and `IS NULL` optimizations.

Trigger grammar captures source spans with `scanpt` so trigger steps can retain original SQL text. Virtual-table argument grammar uses a broad `ANY` token stream and explicit extension calls to preserve module arguments. Window grammar is placed near the end so `WINDOW`, `OVER`, and `FILTER` get token values above ordinary tokenizer outputs.

## State and Persistence Behavior

The parser mutates `Parse` state throughout: error counts, `explain`, `disableLookaside`, create-state union `u1.cr`, `isCreate` debug state, rename token maps, `hasCompound`, `bHasWith`, trigger construction state, returning clauses, and schema initialization compatibility paths. It allocates AST objects from the database connection, and destructors define ownership transfer on successful reductions.

Although parsing itself does not persist database pages, many reductions create persistent schema objects or SQL text stored in `sqlite_schema`. Compatibility behavior is visible in `eidlist`: older schemas with ignored COLLATE or ASC/DESC decorations in identifier lists are still accepted while `db->init.busy` is true. DDL actions use `disableLookaside()` because schema objects can be shared across connections.

## Dependencies and Integration Points

`parse.y` includes `sqliteInt.h` and is tightly coupled to tokenizer token names, AST structures (`Expr`, `ExprList`, `Select`, `SrcList`, `IdList`, `With`, `Cte`, `Window`, `TriggerStep`), schema builders, expression helpers, pragma/vacuum/attach/alter/vtab modules, and the VDBE code-generation pipeline. Lemon-specific directives are part of the build process, so changes require regenerating parser C output through the established SQLite build tooling.

## Risks and Edge Cases

Parser conflicts and token ordering are high risk. The grammar documents an UPSERT ambiguity where `ON` after a SELECT JOIN is resolved as a JOIN constraint unless a WHERE clause disambiguates the UPSERT. New tokens before the final boundary can break assumptions about token values. Error handling must delete partially built ASTs exactly once; incorrect `%destructor` ownership causes leaks or double frees. Feature macros such as `SQLITE_OMIT_*`, `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, `SQLITE_ENABLE_ORDERED_SET_AGGREGATES`, and `SQLITE_UDL_CAPABLE_PARSER` create multiple grammars that all need coverage.

## Test Signals

Tests should cover full SQL syntax acceptance and rejection, parser stack depth limits, OOM/fault injection around parser stack reallocation and AST creation, rename-token mapping, schema-init compatibility parsing, all feature macro combinations used by builds, UPSERT ambiguity cases, RETURNING with INSERT/UPDATE/DELETE, UPDATE FROM, trigger statement restrictions, virtual-table argument preservation, CTE materialization hints, ordered-set aggregate errors, and window frame/filter/over combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/parse.y -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/pcache.c -->
# sources/storage-engines/sqlite/src/pcache.c

## Purpose

`pcache.c` implements SQLite's upper page-cache layer. It wraps the pluggable `sqlite3_pcache_methods2` backend with pager-facing `PgHdr` objects, dirty-page tracking, reference counting, page-size/cache-size/spill configuration, cache stress behavior, and dirty-list sorting. It is the bridge between the pager, which needs transaction-aware page state, and the lower pcache backend, which manages memory and lookup by page number.

The file's central invariant is that clean pages match backing storage, while dirty pages have modified contents that must be written, journaled, or otherwise resolved before they can be discarded. Dirty pages are maintained in an LRU-style list and can be sorted by page number when the pager needs a stable writeback order.

## Important Types and Functions

`struct PCache` stores dirty-list heads (`pDirty`, `pDirtyTail`), the `pSynced` optimization pointer, total references `nRefSum`, size settings (`szCache`, `szSpill`, `szPage`, `szExtra`), purgeability, `eCreate`, the pager stress callback, callback context, and the lower `sqlite3_pcache *pCache`.

Debug helpers include `sqlite3PcachePageSanity()` and optional tracing/dump helpers. Dirty-list management is centralized in `pcacheManageDirtyList()` with operations remove, add, and move-to-front. `pcacheUnpin()` delegates unpinning clean unreferenced purgeable pages to the backend.

Initialization and lifecycle APIs include `sqlite3PcacheInitialize()`, `sqlite3PcacheShutdown()`, `sqlite3PcacheSize()`, `sqlite3PcacheOpen()`, `sqlite3PcacheSetPageSize()`, `sqlite3PcacheClose()`, `sqlite3PcacheClear()`, and `sqlite3PcacheTruncate()`.

Fetch and reference APIs include `sqlite3PcacheFetch()`, `sqlite3PcacheFetchStress()`, `sqlite3PcacheFetchFinish()`, `sqlite3PcacheRelease()`, `sqlite3PcacheRef()`, `sqlite3PcacheDrop()`, `sqlite3PcacheRefCount()`, and `sqlite3PcachePageRefcount()`. Dirty-state APIs include `sqlite3PcacheMakeDirty()`, `sqlite3PcacheMakeClean()`, `sqlite3PcacheCleanAll()`, `sqlite3PcacheClearWritable()`, `sqlite3PcacheClearSyncFlags()`, `sqlite3PcacheMove()`, and `sqlite3PcacheDirtyList()`.

Sizing APIs include `sqlite3PcachePagecount()`, `sqlite3PcacheSetCachesize()`, `sqlite3PcacheSetSpillsize()`, `sqlite3PcacheShrink()`, `sqlite3HeaderSizePcache()`, and `sqlite3PCachePercentDirty()`.

## Control Flow

Opening a cache zeroes `PCache`, initializes defaults, records the pager stress callback, sets `eCreate` to the expensive-allocation path, then calls `sqlite3PcacheSetPageSize()` to allocate the lower cache through `pcache2.xCreate()`. Fetch is split for performance: `sqlite3PcacheFetch()` asks the backend for a raw `sqlite3_pcache_page`; `sqlite3PcacheFetchFinish()` converts the raw page into an initialized `PgHdr`, increments the page reference, and initializes page header fields only on first use.

If a create fetch fails because clean pages cannot be cheaply recycled, pager code can call `sqlite3PcacheFetchStress()`. That routine looks for an unreferenced dirty page, preferring one without `PGHDR_NEED_SYNC`, invokes the pager's `xStress` callback to clean/spill it, and then retries backend fetch with a hard create flag.

Dirty state transitions run through `sqlite3PcacheMakeDirty()` and `sqlite3PcacheMakeClean()`. Releasing a dirty page with refcount zero moves it to the front of the dirty list, while releasing a clean page unpins it in the backend. `sqlite3PcacheMove()` handles page-number changes by dropping any existing destination page, rekeying the backend, updating `PgHdr.pgno`, and moving NEED_SYNC dirty pages forward in the dirty list.

## State and Persistence Behavior

`PgHdr.flags` encode clean/dirty, writable, need-sync, don't-write, mmap, and WAL append state. `pcache.c` does not write disk content itself; persistence is enforced by preserving enough state for pager code to journal, sync, spill, and write in a safe order. The `PGHDR_NEED_SYNC` flag is deliberately independent of `PGHDR_WRITEABLE`, because pages may temporarily stop being writable and later become writable again while still requiring a journal sync before database writeback.

`pSynced` is an optimization for finding dirty pages safe to spill without forcing a journal sync. It may be approximate; correctness comes from checking flags while scanning. `eCreate` tracks whether the lower cache may allocate only cheaply or may try harder, based on whether the cache is purgeable and has dirty pages. Truncation cleans and discards pages above a page number, with a special case that preserves and zeroes page 1 if it is still referenced during full reset.

## Dependencies and Integration Points

This layer depends on `sqlite3GlobalConfig.pcache2`, `sqliteInt.h`, `pcache.h`, `PgHdr`, `Pager`, and pager-provided stress callbacks. Pager code relies on dirty-list output sorted by page number for commit/writeback work. The lower default backend is `pcache1.c`, but this layer also supports application-provided pcache implementations through `SQLITE_CONFIG_PCACHE2`.

## Risks and Edge Cases

Dirty-list corruption is the main local risk; `pDirtyNext`, `pDirtyPrev`, `pDirty`, `pDirtyTail`, and `pSynced` must remain consistent across dirty, clean, release, drop, move, and truncate operations. Reference counts must be balanced across fetch, finish, ref, release, and drop. `sqlite3PcacheSetPageSize()` requires no outstanding refs and no dirty pages. `sqlite3PcacheFetchStress()` must tolerate `SQLITE_BUSY` from the stress callback and must not recycle referenced pages. `sqlite3PcacheDirtyList()` repurposes `PgHdr.pDirty` as a singly linked sorted chain, so callers must not expect `pDirtyPrev` to remain meaningful in that returned list.

## Test Signals

Tests should check fetch/fetch-finish initialization, balanced refcounts, clean-page unpinning, dirty-page list membership, sorted dirty list order, moving pages over existing cached pages, truncating with page 1 referenced, cache-size and negative KiB cache-size behavior, spill threshold behavior, stress callback error and busy handling, debug page sanity assertions, `SQLITE_CHECK_PAGES` dirty iteration, and dirty percentage calculations.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/pcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/pcache.h -->
# sources/storage-engines/sqlite/src/pcache.h

## Purpose

`pcache.h` declares the pager-facing page-cache API and the public portion of `PgHdr`. It is the contract between pager code, btree page extras, and the pcache implementation in `pcache.c` plus the pluggable backend. The header defines how cached database pages expose page data, extra per-page storage, pager ownership, dirty linkage, page number, flags, and reference operations.

## Important APIs, Types, and Constants

The main types are `PgHdr` and `PCache`. `PgHdr` begins with fields visible to other modules: `sqlite3_pcache_page *pPage`, `pData`, `pExtra`, owning `PCache *pCache`, transient sorted-list pointer `pDirty`, owning `Pager *pPager`, optional `pageHash`, `pgno`, and `flags`. The later fields are private to `pcache.c`: `nRef`, `pDirtyNext`, and `pDirtyPrev`.

Flag bits define page state: `PGHDR_CLEAN`, `PGHDR_DIRTY`, `PGHDR_WRITEABLE`, `PGHDR_NEED_SYNC`, `PGHDR_DONT_WRITE`, `PGHDR_MMAP`, and `PGHDR_WAL_APPEND`. These flags are interpreted by pager and pcache code to decide whether pages can be modified, skipped, spilled, synced, or treated as mmap/WAL-specific pages.

Lifecycle APIs are `sqlite3PcacheInitialize()`, `sqlite3PcacheShutdown()`, `sqlite3PCacheBufferSetup()`, `sqlite3PcacheOpen()`, `sqlite3PcacheSetPageSize()`, `sqlite3PcacheSize()`, `sqlite3PcacheClose()`, `sqlite3PcacheClear()`, and `sqlite3PCacheSetDefault()`.

Fetch/reference APIs are `sqlite3PcacheFetch()`, `sqlite3PcacheFetchStress()`, `sqlite3PcacheFetchFinish()`, `sqlite3PcacheRelease()`, `sqlite3PcacheRef()`, `sqlite3PcacheRefCount()`, and `sqlite3PcachePageRefcount()`. Mutation and state APIs include `sqlite3PcacheDrop()`, `sqlite3PcacheMakeDirty()`, `sqlite3PcacheMakeClean()`, `sqlite3PcacheCleanAll()`, `sqlite3PcacheClearWritable()`, `sqlite3PcacheMove()`, `sqlite3PcacheTruncate()`, `sqlite3PcacheDirtyList()`, `sqlite3PcacheClearSyncFlags()`, and `sqlite3PcacheShrink()`.

Sizing and diagnostics include `sqlite3PcacheSetCachesize()`, optional `sqlite3PcacheGetCachesize()`, `sqlite3PcacheSetSpillsize()`, optional `sqlite3PcacheReleaseMemory()`, optional `sqlite3PcacheStats()`, `sqlite3HeaderSizePcache()`, `sqlite3HeaderSizePcache1()`, `sqlite3PCachePercentDirty()`, optional `sqlite3PCacheIsDirty()`, optional `sqlite3PcacheIterateDirty()`, and debug-only `sqlite3PcachePageSanity()`.

## Control Flow

Callers initialize the subsystem, allocate storage for a `PCache` using `sqlite3PcacheSize()`, open it with page and extra sizes, fetch raw pages, finish them into `PgHdr` objects, and release each successful fetch. Pages become dirty through `sqlite3PcacheMakeDirty()` after pager write authorization. Clean transitions happen after pager writeback or rollback. Truncation, move, and dirty-list retrieval support vacuum, rollback, commit, and database-size changes.

The fetch split is part of the interface: `sqlite3PcacheFetch()` returns a backend page object, and `sqlite3PcacheFetchFinish()` makes it safe to use as `PgHdr`. `sqlite3PcacheFetchStress()` is a second-stage allocation path used after a normal fetch cannot cheaply create a page.

## State and Persistence Behavior

`pcache.h` exposes state that determines persistence safety but delegates actual disk work to pager. `PGHDR_WRITEABLE` means the page has been journaled and may be modified. `PGHDR_NEED_SYNC` means the rollback journal must be synced before the page is written to the database. `PGHDR_DONT_WRITE` marks a dirty page whose content should not be written back. `PGHDR_WAL_APPEND` marks pages appended to WAL. Reference counts pin pages in memory; unreferenced clean pages can be recycled, while unreferenced dirty pages remain available for pager-managed spill.

## Dependencies and Integration Points

This header depends on `Pager`, `Pgno`, `sqlite3_pcache_page`, and SQLite configuration macros. It is included by pager and pcache implementation code, and it exposes header-size queries so SQLite can compute the full per-page memory layout used by btree, pcache, and pcache1. `sqlite3PCacheBufferSetup()` integrates with `sqlite3_config(SQLITE_CONFIG_PAGECACHE)`. `sqlite3PCacheSetDefault()` installs the default backend when no application backend is configured.

## Risks and Edge Cases

Consumers must respect which `PgHdr` fields are public and which are private. Incorrect flag manipulation can violate journaling invariants. Every successful fetch needs a release. `sqlite3PcacheSetPageSize()` requires no live page references. `sqlite3PcacheDirtyList()` returns a sorted list using `PgHdr.pDirty`, not the same links as the internal dirty LRU list. Optional compile flags change available diagnostics and direct-overflow behavior.

## Test Signals

Tests should cover flag transitions, dirty-list membership, page fetch/release reference accounting, cache close with no outstanding refs, configured pagecache buffer setup, spill-size and cache-size setting, memory-release builds, dirty iteration under `SQLITE_CHECK_PAGES`, debug sanity checks, and direct-overflow dirty detection when enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/pcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/pcache1.c -->
# sources/storage-engines/sqlite/src/pcache1.c

## Purpose

`pcache1.c` implements SQLite's default `sqlite3_pcache_methods2` backend. It provides page lookup by page number, page memory allocation and recycling, LRU management for unpinned pages, cache grouping for shared memory pressure, configured pagecache-buffer support, local bulk allocation, heap fallback, and optional memory release for `sqlite3_release_memory()`.

This layer does not know about pager dirty semantics beyond pinned versus unpinned page objects. It stores page content and backend headers in cache lines and gives `pcache.c` raw `sqlite3_pcache_page` handles. The file also installs itself through `sqlite3PCacheSetDefault()` when no application-defined cache backend is configured.

## Important Types and Functions

`PgHdr1` is the backend header and begins with `sqlite3_pcache_page` so it can be cast to the public backend page type. It stores `iKey`, bulk/local flags, hash-chain linkage, owning `PCache1`, and LRU links. A page is pinned when it is not on the LRU list.

`PGroup` groups one or more `PCache1` objects that can recycle each other's unpinned pages. It tracks shared limits (`nMaxPage`, `nMinPage`, `mxPinned`), total purgeable pages, an optional mutex, and a circular LRU anchor. Depending on configuration, each cache has a separate group or all caches share the global group.

`PCache1` stores page size, extra size, allocation size, purgeability, per-cache limits (`nMin`, `nMax`, `n90pct`), largest key, hash table state, count of recyclable and total pages, local free list, and local bulk allocation. `PCacheGlobal` stores global configured pagecache slots, free-slot list, pressure state, mutexes, and default group.

Allocation helpers include `sqlite3PCacheBufferSetup()`, `pcache1InitBulk()`, `pcache1Alloc()`, `pcache1Free()`, `pcache1AllocPage()`, `pcache1FreePage()`, `sqlite3PageMalloc()`, and `sqlite3PageFree()`. Cache helpers include `pcache1UnderMemoryPressure()`, `pcache1ResizeHash()`, `pcache1PinPage()`, `pcache1RemoveFromHash()`, `pcache1EnforceMaxPage()`, and `pcache1TruncateUnsafe()`.

The pluggable method implementations are `pcache1Init()`, `pcache1Shutdown()`, `pcache1Create()`, `pcache1Cachesize()`, `pcache1Shrink()`, `pcache1Pagecount()`, `pcache1Fetch()`, `pcache1Unpin()`, `pcache1Rekey()`, `pcache1Truncate()`, and `pcache1Destroy()`.

## Control Flow

Initialization zeroes global state, decides whether to use separate per-cache groups or one global group, allocates static mutexes when needed, and records local bulk-allocation policy. `pcache1Create()` allocates a cache plus optional per-cache group, initializes the LRU anchor, sets sizes, allocates a hash table, and contributes minimum page reservations for purgeable caches.

Fetch first searches the hash table. If found and unpinned, it is removed from LRU and returned pinned. If not found and `createFlag` is 0, fetch returns null. If `createFlag` is 1, `pcache1FetchStage2()` refuses allocation when too many pages are pinned or memory pressure is high. Otherwise it resizes the hash table when needed, tries to recycle the oldest unpinned LRU page if size and pressure rules allow, then allocates from local bulk memory, configured pagecache slots, or heap fallback. New pages are inserted into the hash table, marked pinned, and have their `pExtra` first pointer cleared so the upper layer can detect uninitialized `PgHdr`.

Unpin either frees the page immediately when reuse is unlikely or group limits are exceeded, or inserts it at the front of the circular LRU list. Rekey removes a page from its old hash bucket and inserts it under the new key. Truncate scans relevant hash buckets or the whole hash table to remove pages at or above a limit, pinning them first if they are on LRU. Destroy truncates all pages, updates group limits, frees bulk memory, hash table, and cache object.

## State and Persistence Behavior

The backend state is memory-residency state rather than disk persistence. Pinned pages are in active use by upper layers and cannot be recycled. Unpinned pages are candidates for reuse and are ordered in the group LRU. Purgeable caches count against group page limits and can donate pages to other caches in the same group. Non-purgeable caches, such as in-memory databases, do not use createFlag 1 and do not participate in the same purgeable accounting.

Page memory can come from three places: the general allocator, the global `SQLITE_CONFIG_PAGECACHE` buffer, or per-cache local bulk allocation. The configured pagecache pool tracks `nFreeSlot`, `nReserve`, and an atomic under-pressure flag. Local bulk allocation is initialized lazily on the first page allocation for a cache and is freed when the cache becomes empty.

## Dependencies and Integration Points

`pcache1.c` depends on SQLite memory allocation, mutex, status, atomic, and configuration APIs. It implements the `sqlite3_pcache_methods2` interface consumed by `pcache.c`. `sqlite3PCacheBufferSetup()` integrates startup configuration, `sqlite3PageMalloc()` and `sqlite3PageFree()` expose pagecache allocation for related SQLite internals, `sqlite3Pcache1Mutex()` supports status reporting, and optional `sqlite3PcacheReleaseMemory()` supports global memory pressure relief.

## Risks and Edge Cases

Hash table resizing releases and reacquires the group mutex around allocation, so callers must tolerate concurrent state changes under supported modes. Recycled pages must match allocation size; otherwise they are freed and a new allocation is attempted. LRU anchor handling depends on `isAnchor` and circular links being correct. `pcache1TruncateUnsafe()` has an optimized partial scan that depends on `iMaxKey` and hash modulo behavior. Global configured pagecache memory and local bulk memory are mutually exclusive in practice for initial bulk use, and pressure decisions must avoid overusing heap when a pagecache pool was expected to be sufficient.

The page layout intentionally places the backend header after page content so small btree overreads on corrupt databases land in initialized header memory. Structure padding choices and initialization are therefore correctness and tooling concerns, not only performance details.

## Test Signals

Tests should cover configured pagecache pools, heap fallback and overflow stats, local bulk allocation sizing, separate versus global group modes, hash lookup and resize, fetch createFlag 0/1/2 behavior, memory-pressure refusals, LRU recycling across caches, unpin with and without `reuseUnlikely`, rekey collision cases, truncate of pinned and unpinned pages, destroy after live pages have been truncated, `sqlite3_release_memory()` builds, status counters, and valgrind/ASAN runs against corrupt-page overread scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/pcache1.c -->

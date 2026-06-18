# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 10757-17068

## Scope

This chunk starts near the end of the public `sqlite3.h` API declarations and continues into the first internal SQLite amalgamation headers embedded in `sqliteInt.h`. The covered range includes:

- Statement scan-status constants and APIs.
- Cache flush, pre-update hook, low-level system error, WAL snapshot, serialization/deserialization, R-Tree, session/changeset, and FTS5 extension APIs.
- The close of `sqlite3.h` and the beginning of internal configuration defaults, platform/compiler macros, parser token numbers, generic hash-table contracts, OS wrapper declarations, pager declarations, btree declarations, and the start of VDBE/opcode declarations.

This range is mostly interface and macro contract code, not implementation bodies. It defines ABI/API surfaces and private subsystem boundaries that later source sections implement.

## Purpose

The public part of the chunk exposes optional SQLite features to embedders and extensions. It describes how applications inspect query-plan execution statistics, flush dirty cache pages mid-transaction, register pre-update callbacks, use WAL snapshots, serialize databases, register R-Tree geometry callbacks, capture and apply session changesets, and extend FTS5 with custom tokenizers and auxiliary functions.

The internal part prepares SQLite's core build environment and subsystem interfaces. It fixes compile-time limits, normalizes compiler/platform behavior, assigns parser token IDs, defines small shared data structures such as `Hash`, declares the VFS/OS access wrapper layer, and specifies the pager, btree, and VDBE contracts used by the actual storage and bytecode engine implementations later in the amalgamation.

Within WiredTiger, this is vendored third-party SQLite test infrastructure. The chunk is not WiredTiger's storage engine, but it affects the SQLite library and shell behavior used by the vendored SQLite test tree.

## Important APIs, Types, and Functions

- `SQLITE_SCANSTAT_*`, `sqlite3_stmt_scanstatus()`, `sqlite3_stmt_scanstatus_v2()`, and `sqlite3_stmt_scanstatus_reset()` expose predicted and measured query-plan loop data when `SQLITE_ENABLE_STMT_SCANSTATUS` is compiled in. The `SQLITE_SCANSTAT_COMPLEX` flag broadens reporting from loop nodes to all `EXPLAIN QUERY PLAN` elements.
- `sqlite3_db_cacheflush()` asks all schemas on a connection to write eligible dirty pager-cache pages to disk without changing the connection error state.
- `sqlite3_preupdate_hook()` plus `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, and `sqlite3_preupdate_blobwrite()` define the optional pre-update event API used by the sessions module.
- `sqlite3_system_errno()` exposes the OS-level error associated with recent I/O/open failures.
- `sqlite3_snapshot`, `sqlite3_snapshot_get()`, `sqlite3_snapshot_open()`, `sqlite3_snapshot_free()`, `sqlite3_snapshot_cmp()`, and `sqlite3_snapshot_recover()` define the experimental WAL snapshot lifecycle.
- `sqlite3_serialize()` and `sqlite3_deserialize()` move an entire schema database image between SQLite and caller-owned memory. Flags include `SQLITE_SERIALIZE_NOCOPY`, `SQLITE_DESERIALIZE_FREEONCLOSE`, `SQLITE_DESERIALIZE_RESIZEABLE`, and `SQLITE_DESERIALIZE_READONLY`.
- `sqlite3_rtree_geometry_callback()`, `sqlite3_rtree_query_callback()`, `sqlite3_rtree_geometry`, and `sqlite3_rtree_query_info` expose R-Tree custom geometry/query callbacks, including scored traversal state and within/partly-within/full-within outcomes.
- `sqlite3_session`, `sqlite3_changeset_iter`, and the `sqlite3session_*`, `sqlite3changeset_*`, `sqlite3changegroup_*`, and `sqlite3rebaser_*` declarations define change capture, changeset iteration, patchset generation, conflict-aware apply, change grouping, rebasing, and streaming variants.
- `Fts5ExtensionApi`, `Fts5Context`, `Fts5PhraseIter`, `fts5_extension_function`, `fts5_tokenizer_v2`, legacy `fts5_tokenizer`, and `fts5_api` define FTS5 extension hooks for auxiliary functions and tokenizers, including locale-aware tokenizer APIs and versioned API tables.
- `Hash` and `HashElem` are SQLite's generic internal string-keyed hash table types, with `sqlite3HashInit()`, `sqlite3HashInsert()`, `sqlite3HashFind()`, `sqlite3HashClear()`, and iteration macros.
- `TK_*` constants from `parse.h` assign parser token numbers for SQL syntax and expression operators. These values bind the tokenizer, lemon parser, expression tree code, and VDBE code generator.
- `sqlite3Os*` declarations wrap `sqlite3_file` and `sqlite3_vfs` methods behind SQLite's internal OS abstraction, including file I/O, locking, shared-memory WAL operations, mmap fetch/unfetch, dynamic loading, randomness, sleep, and current time.
- `Pager`, `DbPage`, `Pgno`, `PAGER_*` constants, and `sqlite3Pager*` declarations define page-cache, rollback journal, WAL, savepoint, sync, mmap, and page reference operations.
- `Btree`, `BtCursor`, `BtShared`, `BtreePayload`, `BTREE_*` constants, and `sqlite3Btree*` declarations define database btree opening, transactions, schema storage, table/index creation, cursor movement, payload reads/writes, metadata, WAL checkpoints, integrity checks, and shared-cache mutex entry/leave routines.
- `Vdbe`, `VdbeOp`, `VdbeOpList`, `SubProgram`, and `SubrtnSig` begin the VDBE contract. `P4_*`, `P5_Constraint*`, `COLNAME_*`, `ADDR()`, and initial `OP_*` opcodes describe instruction operands, ownership rules, result-column metadata slots, unresolved label encoding, and bytecode numbers.

## Control Flow

There is little direct runtime control flow in this chunk. The important flow is contractual:

- Scan-status callers prepare and run a statement, then query each loop or query-plan element by index. `idx == -1` may request whole-query information; out-of-range indexes leave output unchanged and return nonzero.
- `sqlite3_db_cacheflush()` walks schemas on the connection and attempts to flush non-pinned dirty pages. If locks cannot be obtained for one database, it may skip that database and continue, returning `SQLITE_BUSY` if skips occurred without other errors.
- Pre-update hooks are installed per connection, invoked before real-table row changes, and allow old/new column access only during the callback. Blob writes are reported as delete-style callbacks with `sqlite3_preupdate_blobwrite()` identifying the written column.
- Snapshot flow is explicit: a non-autocommit WAL read transaction is required or opened by `sqlite3_snapshot_get()`, the returned object is later used by `sqlite3_snapshot_open()`, compared with `sqlite3_snapshot_cmp()`, released with `sqlite3_snapshot_free()`, and recovered into the wal-index with `sqlite3_snapshot_recover()` when needed.
- Session flow starts with `sqlite3session_create()`, optional object configuration, table attach/filter setup, change recording through the pre-update hook, extraction through changeset or patchset APIs, iteration via `sqlite3changeset_start()` and `sqlite3changeset_next()`, and application through `sqlite3changeset_apply()` or `_v2()` with filter and conflict callbacks.
- Changeset conflict handling is callback-driven. A conflict handler returns `SQLITE_CHANGESET_OMIT`, `SQLITE_CHANGESET_REPLACE`, or `SQLITE_CHANGESET_ABORT`, and `_apply_v2()` can return rebase information for later `sqlite3rebaser_*` processing.
- FTS5 extension flow is version-table based. Applications obtain `fts5_api`, register tokenizers or auxiliary functions, then FTS5 calls tokenizer methods for document, query, prefix-query, or auxiliary tokenization and calls extension functions with `Fts5ExtensionApi` accessors for current-row and current-query metadata.
- Internal subsystem flow is layered. SQL text is tokenized into `TK_*` values, compiled into `VdbeOp` bytecode, VDBE opcodes call btree cursor operations, btree calls pager page and transaction operations, pager calls OS wrappers, and OS wrappers invoke the active VFS and `sqlite3_file` methods.

## State and Persistence Behavior

The public API declarations in this range mostly describe state owned elsewhere:

- Scan-status counters live on prepared statements and can be reset without re-preparing the statement.
- Cache flushing affects dirty pager-cache pages and durable database files, but not the connection's stored error code/message.
- Pre-update hooks are connection-local singleton callbacks. Session objects also use that hook, making application pre-update hooks and sessions mutually exclusive on the same connection.
- WAL snapshots are heap-owned handles representing historical WAL state. They are only meaningful while WAL content needed by the snapshot remains available and has not been checkpointed away.
- Serialization returns either a caller-freed heap copy or a temporary no-copy pointer into SQLite's contiguous in-memory representation. Deserialization replaces a schema with an in-memory database image and can transfer ownership of the buffer to SQLite.
- Session objects accumulate primary-key based change records in memory, then compare those records to current database content when generating changesets. Changes to rows with NULL primary-key fields are omitted, and changes to `sqlite_stat1` have special encoding compatibility behavior.
- Streaming session APIs avoid single large contiguous buffers by using input and output callbacks, with global stream chunk size controlled by `sqlite3session_config(SQLITE_SESSION_CONFIG_STRMSIZE, ...)`.
- `sqliteLimit.h` constants influence persistent file compatibility and resource ceilings, especially page size, maximum page count, SQL length, column count, trigger recursion, attached database count, and default cache/WAL settings.
- Pager and btree declarations define persistence-critical behavior: rollback journal modes, WAL support, savepoints, sync/fullfsync/cache-spill flags, auto-vacuum modes, schema metadata slots, database header versioning, and cursor payload insert/delete semantics.
- The locking constants around `PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, and `SHARED_SIZE` are file-format sensitive because lock bytes must not overlap allocated database pages.

## Dependencies and Integration Points

- Optional public APIs are gated by compile-time macros such as `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_OMIT_DESERIALIZE`, `SQLITE_RTREE_INT_ONLY`, `SQLITE_ENABLE_SESSION`, and FTS5 availability.
- The WASI branch forces `SQLITE_WASI`, disables loadable extensions, and defaults `SQLITE_THREADSAFE` to 0 if not specified.
- Configuration macros establish defaults for `SQLITE_THREADSAFE`, memory allocator selection, `SQLITE_DEFAULT_MEMSTATUS`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_POWERSAFE_OVERWRITE`, mmap limits, temp storage, worker threads, recursive triggers, and file-format version.
- Platform/compiler integration includes pointer/integer cast macros, inline/noinline attributes, MSVC intrinsics and SEH gating, byte-order detection, fixed-size integer typedefs, alignment macros, and debug/coverage helper macros such as `testcase()`, `ALWAYS()`, `NEVER()`, `TREETRACE()`, and `WHERETRACE()`.
- `parse.h` token IDs are generated from the parser grammar and must stay synchronized with tokenizer and parser tables later in `parse.c`.
- OS wrapper declarations depend on the public `sqlite3_file`, `sqlite3_io_methods`, and `sqlite3_vfs` APIs defined earlier in `sqlite3.h`. Pager and btree depend on those wrappers rather than calling VFS methods directly.
- Pager and btree constants intentionally mirror each other in some places: `PAGER_OMIT_JOURNAL` and `PAGER_MEMORY` must match `BTREE_OMIT_JOURNAL` and `BTREE_MEMORY`.
- Btree integrates with parser/codegen through `KeyInfo`, `UnpackedRecord`, `sqlite3_value`, cursor hints, and `BtreePayload`. It integrates with pager for page storage and WAL checkpoints.
- VDBE declarations bridge code generation and execution. `VdbeOp.p4` can carry pointers to `FuncDef`, `CollSeq`, `KeyInfo`, `Table`, `SubProgram`, virtual table objects, expressions, and other internal objects, so `p4type` ownership rules are critical.

## Risks and Edge Cases

- Many APIs in this range are compile-time optional. Downstream tests or code that assumes their symbols exist will fail when the corresponding macros are disabled.
- Scan-status `iScanStatusOp` values outside the documented constants have undefined behavior. The `_v2()` flags currently define only `SQLITE_SCANSTAT_COMPLEX`, leaving future flag expansion sensitive to callers passing stray bits.
- Pre-update helper APIs are only valid during the callback and with the same connection pointer. Misuse is explicitly undefined and can expose destroyed `sqlite3_value` objects after callback return.
- Session objects and application pre-update hooks conflict because both rely on the single connection pre-update hook slot.
- Snapshot APIs are constrained to WAL databases, non-autocommit transactions, no open write transaction for `get`, and no active statements for some `open` cases. Checkpoints can invalidate old snapshots, returning `SQLITE_ERROR_SNAPSHOT`.
- `SQLITE_SERIALIZE_NOCOPY` returns a borrowed pointer that is invalidated by the next write or connection close. `sqlite3_deserialize()` cannot target `temp`, fails if the schema is busy or in backup, and WAL-format serialized input must be converted to rollback mode before use.
- Session changesets ignore rows with NULL primary-key columns, compress multiple changes to the same key into net changes, and may represent primary-key updates as delete plus insert. These semantics are easy to misinterpret in replication tests.
- Conflict handlers for changeset apply must return values appropriate to the conflict type; returning `SQLITE_CHANGESET_REPLACE` for unsupported conflict classes makes apply fail with `SQLITE_MISUSE`.
- FTS5 tokenizer callbacks must report tokens in order and must not mark the first token as `FTS5_TOKEN_COLOCATED`. Versioned tokenizer structs differ in locale parameters, so mixing v1 and v2 callbacks incorrectly breaks ABI expectations.
- Raising limits such as `SQLITE_MAX_COLUMN`, page size, attached database count, or maximum variable number can overflow storage assumptions or create incompatible behavior. The code enforces some hard bounds but leaves many defaults compile-time tunable.
- Changing `PENDING_BYTE` is a subtle file-format compatibility change because the pager skips pages overlapping lock bytes.
- Internal `Hash` is not fully opaque because macros read fields directly. Structural changes have wide blast radius.
- `VdbeOp.p4type` values above `P4_FREE_IF_LE` do not own resources, while values at or below it require freeing. Incorrect tagging causes leaks, use-after-free, or double free.
- Opcode and token numeric values are generated contracts. Manual edits or mismatches with generated parser/opcode tables would corrupt SQL parsing or VDBE execution.

## Test Signals

Useful signals for this chunk are mostly API-contract and build-configuration tests:

- Build matrices toggling `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_OMIT_DESERIALIZE`, `SQLITE_ENABLE_SESSION`, FTS5, R-Tree, WAL, shared-cache, debug, and test options.
- Scan-status tests comparing `SQLITE_SCANSTAT_NLOOP`, `NVISIT`, `EST`, `NAME`, `EXPLAIN`, `SELECTID`, `PARENTID`, and `NCYCLE` output against `EXPLAIN QUERY PLAN`, plus reset behavior.
- Cache-flush tests with active readers, dirty pages, busy handlers, attached databases, and page 1 pinned.
- Pre-update hook tests for INSERT/UPDATE/DELETE, rowid vs WITHOUT ROWID tables, trigger depth, blob-write reporting, and invalid call sites.
- Snapshot tests covering WAL prerequisites, autocommit rejection, checkpoint invalidation, snapshot comparison, recovery, and active statement rejection.
- Serialize/deserialize tests for disk-backed, memory, read-only, resizeable, free-on-close, no-copy, busy schema, backup, temp schema rejection, and WAL-input failure.
- R-Tree tests registering geometry and scored query callbacks, checking `eWithin`, `rScore`, queue counts, level fields, and integer-only coordinate builds.
- Session tests for attach/filter behavior, primary-key requirements, NULL primary-key omission, `sqlite_stat1` special handling, changeset vs patchset output, streaming callbacks, conflict outcomes, and rebasing after `_apply_v2()`.
- FTS5 extension tests for auxiliary API version fields, column/phrase/instance accessors, auxdata lifetime, locale-aware tokenization, legacy tokenizer compatibility, prefix token handling, and synonym colocation rules.
- Internal regression tests should exercise parser token consistency, hash insertion/deletion/iteration, OS wrapper error propagation, pager journal/WAL/savepoint paths, btree cursor insert/delete/payload paths, shared-cache mutex no-op vs real paths, and VDBE opcode metadata consistency.

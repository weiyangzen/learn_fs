# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 17069-22525

## Scope

This chunk covers the transition from generated SQLite VDBE opcode metadata into a large part of SQLite's private internal header surface. It begins inside `opcodes.h` with opcode numeric assignments from `OP_IfNullRow` through `OP_Abortable`, includes opcode property flags and `SQLITE_MX_JUMP_OPCODE`, then resumes `vdbe.h`, `pcache.h`, `mutex.h`, most of `sqliteInt.h`, `os_common.h`, and the beginning of generated `ctime.c` compile-option reporting.

The range is mostly declarations, macro contracts, and structure layouts rather than function bodies. Its main purpose is to define the in-memory ABI used by the implementation chunks that follow: VDBE bytecode construction, pager cache pages, connection/schema state, parse-tree state, SQL function metadata, virtual table metadata, expression/select/upsert/window trees, memory/debug hooks, parser and code-generator entry points, and optional test or diagnostic surfaces.

## Purpose

The opcode section defines the bytecode vocabulary and metadata consumed by the VDBE code generator and interpreter. The generated values and `OPFLG_*` bitvectors describe which operands are inputs, outputs, jump targets, or cycle counters, and `SQLITE_MX_JUMP_OPCODE` is tuned so label-resolution helpers can scan jump opcodes efficiently.

The `vdbe.h` declarations expose the private API for building, mutating, preparing, explaining, resetting, finalizing, and introspecting VDBE programs. Parser and code-generation code uses these routines to append opcodes, patch operands, manage labels, attach P4 payloads such as `KeyInfo`, annotate explain output, and track coverage.

The `pcache.h` section defines the pager cache page header and the cache interface used between the pager, btree, and pcache implementations. It establishes how pages are fetched, pinned, marked dirty or clean, truncated, spilled, reference-counted, and iterated under debug/test builds.

The large `sqliteInt.h` section defines SQLite's central private object model. It describes database connections (`sqlite3`), attached database slots (`Db`), schemas (`Schema`), lookaside state (`Lookaside`), SQL functions (`FuncDef`), tables/indexes/columns/foreign keys, expression and SELECT trees, parser state, virtual tables, CTEs, window functions, global configuration, and the private function prototypes tying the tokenizer, parser, resolver, planner, code generator, btree/pager glue, virtual table subsystem, foreign key subsystem, memory allocator, and diagnostics together.

The final `os_common.h` and `ctime.c` start provide shared OS-layer test/tracing macros and the generated compile-option list returned by SQLite diagnostics.

## Important APIs, Types, and Functions

- `OP_*` opcode constants and `OPFLG_*`: define VDBE instruction IDs and operand behavior. This chunk includes control-flow opcodes (`OP_Seek*`, `OP_Rewind`, `OP_Next`, `OP_Goto`-adjacent jump metadata from prior chunk), record/table/index access (`OP_Column`, `OP_MakeRecord`, `OP_OpenRead`, `OP_Insert`, `OP_Delete`, `OP_IdxInsert`), aggregate/window support (`OP_AggStep`, `OP_AggInverse`, `OP_AggFinal`), virtual table opcodes (`OP_VOpen`, `OP_VColumn`, `OP_VNext`), and diagnostics (`OP_Trace`, `OP_Explain`).
- VDBE builder API: `sqlite3VdbeCreate`, `sqlite3VdbeAddOp0/1/2/3/4`, `sqlite3VdbeAddFunctionCall`, `sqlite3VdbeAddOpList`, `sqlite3VdbeChangeP1/P2/P3/P4/P5`, `sqlite3VdbeJumpHere`, `sqlite3VdbeResolveLabel`, `sqlite3VdbeMakeReady`, `sqlite3VdbeFinalize`, `sqlite3VdbeReset`, `sqlite3VdbeDelete`, and related helpers.
- VDBE diagnostics and coverage: `sqlite3VdbeExplain`, `sqlite3VdbeExplainPop`, `sqlite3VdbeExplainParent`, `VdbeComment`, `VdbeNoopComment`, `VdbeCoverage*`, `sqlite3VdbeScanStatus*`, and `sqlite3VdbePrintOp`.
- `PgHdr` and `PCache`: represent page-cache entries and cache instances. `PgHdr` stores page data, extra metadata, owner cache, pager, page number, flags, reference count, and dirty-list links.
- Pcache API: `sqlite3PcacheInitialize`, `sqlite3PcacheOpen`, `sqlite3PcacheFetch`, `sqlite3PcacheFetchStress`, `sqlite3PcacheFetchFinish`, `sqlite3PcacheRelease`, `sqlite3PcacheMakeDirty`, `sqlite3PcacheMakeClean`, `sqlite3PcacheDirtyList`, `sqlite3PcacheTruncate`, `sqlite3PcacheClear`, `sqlite3PcacheClose`, `sqlite3PcacheSetCachesize`, `sqlite3PcacheSetSpillsize`, and `sqlite3PcacheShrink`.
- Mutex selection macros: choose `SQLITE_MUTEX_OMIT`, `SQLITE_MUTEX_NOOP`, `SQLITE_MUTEX_PTHREADS`, or `SQLITE_MUTEX_W32` from `SQLITE_THREADSAFE` and OS macros. In omit mode, mutex APIs compile to no-op macros returning sentinel success values.
- `Db` and `Schema`: attach database handles to btrees and schema caches. `Schema` stores schema cookie, generation, hashes for tables/indexes/triggers/foreign keys, encoding, format, flags, and default cache size.
- `sqlite3`: the central connection object. This chunk defines the fields for VFS, VDBE list, mutex, attached databases, flags, transaction/autocommit state, error state, lookaside allocator, callbacks, progress/busy handlers, virtual table transactions, function/collation hashes, savepoints, deferred constraints, unlock notify, and extension handles.
- `Lookaside` and `LookasideSlot`: per-connection fixed-size allocation pools, including optional two-size lookaside. `DisableLookaside` and `EnableLookaside` manipulate `bDisable` and the fast-path `sz` field.
- `FuncDef`, `FuncDestructor`, and `FuncDefHash`: describe built-in and application SQL functions, aggregate/window callbacks, function flags, hashing, and reference-counted destructors for `sqlite3_create_function_v2`.
- `Column`, `CollSeq`, affinity and comparison flags: define column metadata, collation callbacks, affinity constants, NULL-comparison modifiers, hidden/generated column flags, and type-checking relationships used by code generation and VDBE comparison.
- `VTable`, `Table`, `FKey`, `Index`, `IndexSample`, `KeyInfo`, and `UnpackedRecord`: core schema/planner/runtime metadata for ordinary tables, virtual tables, foreign keys, btree indexes, STAT4 samples, collation/sort descriptors, and decoded index probe keys.
- Parser tree types: `Token`, `Expr`, `ExprList`, `SrcItem`, `SrcList`, `NameContext`, `Upsert`, `Select`, `SelectDest`, `AggInfo`, `Trigger`, `TriggerPrg`, `Parse`, `With`, `Cte`, `CteUse`, `Window`, `Walker`, and `DbFixer`.
- Code-generation and parser prototypes: declarations cover expression allocation/deletion/coding, SELECT preparation/execution, WHERE planning, DDL/DML generation, schema init/reset, table/index creation/drop, triggers, foreign keys, UPSERT, CTEs, virtual tables, name resolution, collation lookup, affinity handling, varints, value conversion, error propagation, memory allocation, parser entry points, and module registration.
- Debug/test/diagnostic hooks: `sqlite3FaultSim`, fault injector IDs, benign malloc markers, memory-debug type tags, `SimulateIOError`, `SimulateDiskfullError`, `OpenCounter`, parser tracing/coverage, I/O tracing, tree-view printers, VDBE coverage, scan status, and compile-option diagnostics.

## Control Flow and Contracts

There is little executable control flow in this chunk, but it defines several important control-flow contracts for later code:

- VDBE code generation constructs bytecode by appending opcodes, reserving labels, then patching unresolved `P2` jump targets with `sqlite3VdbeJumpHere()` or `sqlite3VdbeResolveLabel()`. `OPFLG_JUMP` and `SQLITE_MX_JUMP_OPCODE` let the VDBE builder and verifier identify jump instructions cheaply.
- `VdbeCoverage*` macros annotate branches at code-generation time. With `SQLITE_VDBE_COVERAGE`, they record the source line and expected branch shape; without it, they compile away.
- Page cache fetch is split into allocation and finish phases: `sqlite3PcacheFetch()` obtains an underlying `sqlite3_pcache_page`, `sqlite3PcacheFetchFinish()` maps it to a `PgHdr`, and each successful fetch pins the page until `sqlite3PcacheRelease()`.
- Dirty-page handling is list-based. `sqlite3PcacheMakeDirty()` places a page on the cache dirty list, `sqlite3PcacheMakeClean()` removes it, and `sqlite3PcacheDirtyList()` returns a page-number-sorted list for pager writeback.
- Schema access is guarded by mutex rules documented on `Schema`: normal schemas require the corresponding btree mutex and connection mutex; TEMP schema needs only the connection mutex.
- Parse state is split into a zero-initialized header, a non-recursive region, and a recursive tail. `PARSE_HDR_SZ`, `PARSE_RECURSE_SZ`, and `PARSE_TAIL_SZ` encode that layout for parser reentry and nested parse cleanup.
- Name resolution walks nested `NameContext` objects from innermost to outermost, increments `nRef` on a match, and records aggregate/window/subquery side effects with `NC_*` flags.
- SELECT code generation routes rows through `SelectDest.eDest`. The `SRT_*` constants distinguish output, memory scalar, set membership, ephemeral table, coroutine, queue, recursive queue, and update-from destinations.
- Virtual table state is per connection even when schema is shared. `VTable` objects are moved to `sqlite3.pDisconnect` for deferred disconnection to avoid mutex-order deadlocks.
- Compile-time feature macros replace entire subsystems with no-op stubs when omitted. Examples include virtual tables, foreign keys, CTEs, UPSERT, WAL, generated columns, window functions, shared cache, unlock notify, and memory debugging.

## State and Persistence Behavior

This chunk defines the in-memory state model that persists for the lifetime of a SQLite connection, statement, schema, or cache object:

- Persistent connection state lives in `sqlite3`: attached database array, open VDBEs, autocommit and transaction counters, error state, callback registrations, limits, flags, lookaside pools, function/collation registries, busy/progress handlers, savepoints, deferred constraints, virtual table transactions, and unlock-notify links.
- Persistent schema state lives in `Schema` and subordinate `Table`, `Index`, `Trigger`, and `FKey` structures. Schema cookies and generation counters detect changes; hash tables cache lookup by object name.
- Pager-cache state lives in `PCache` and `PgHdr`. Page flags (`PGHDR_DIRTY`, `PGHDR_WRITEABLE`, `PGHDR_NEED_SYNC`, `PGHDR_DONT_WRITE`, `PGHDR_MMAP`, `PGHDR_WAL_APPEND`) encode writeback, journaling, mmap, and WAL interactions.
- Parse state in `Parse` is transient but complex. It owns temporary registers, VDBE cursor allocation counters, label tables, constant-expression lists, cleanup callbacks, trigger programs, active WITH clauses, rename metadata, and recursive parse fields.
- Expression trees may be full, reduced, or token-only. `EP_Reduced` and `EP_TokenOnly` are memory-layout contracts; consumers must not read fields past the allowed prefix.
- `FuncDestructor` persists until all generated `FuncDef` variants release it. This is critical when a single application function definition expands into multiple encodings.
- `KeyInfo` is reference counted and shared between VDBE programs or cursors that need collation/sort metadata for index keys.
- Global process state is represented by `Sqlite3Config`, declared here for non-amalgamation builds. It stores allocator, mutex, pcache, mmap, logging, lookaside defaults, initialization flags, test hooks, compile-time tuning, and global diagnostics.
- `os_common.h` test state is global under `SQLITE_TEST`: simulated I/O error counters and open-file counts influence later OS backend behavior and test assertions.

The declarations themselves do not write durable data. Durable effects occur later through pager, journal, WAL, schema, and VDBE implementations that honor the structures and flags defined here.

## Dependencies and Integration Points

This chunk is a central integration point for the SQLite amalgamation:

- VDBE builder declarations are consumed by parser actions, expression code generation, DML/DDL emitters, trigger code, foreign key enforcement, virtual table code, and query planner output.
- Pcache interfaces connect the pager to the configured page-cache backend (`sqlite3_pcache_methods2`) and to memory-pressure logic via the `xStress` callback supplied to `sqlite3PcacheOpen()`.
- Mutex macros depend on `SQLITE_THREADSAFE`, `SQLITE_OS_UNIX`, and `SQLITE_OS_WIN`, then feed every subsystem that needs connection, global, pcache, malloc, or shared-cache locking.
- Schema and table/index metadata connect parser DDL, schema loading, query planning, name resolution, bytecode generation, ANALYZE statistics, foreign keys, triggers, generated columns, hidden columns, and virtual table support.
- `sqlite3` embeds public API callback state such as commit/rollback/update hooks, trace/profile hooks, WAL hooks, progress and busy handlers, collation-needed callbacks, preupdate hooks, autovacuum callbacks, and client data.
- `Parse` integrates the tokenizer/parser, resolver, code generator, VDBE program builder, trigger compiler, schema authorization, virtual table declaration mode, ALTER TABLE rename tracking, RETURNING handling, and cleanup queue.
- Private prototypes tie together source modules that are separate in canonical SQLite but fused in this amalgamation: `build.c`, `expr.c`, `select.c`, `where.c`, `vdbe*.c`, `btree.c`, `pager.c`, `pcache.c`, `vtab.c`, `fkey.c`, `insert.c`, `update.c`, `delete.c`, `resolve.c`, `alter.c`, `analyze.c`, `func.c`, `utf.c`, `util.c`, `fault.c`, and OS backends.
- `ctime.c` integrates with `sqlite3_compileoption_get()` / `sqlite3_compileoption_used()` implementations later in the file by constructing a sorted array of compile-time option strings.

Within WiredTiger, this is vendored third-party SQLite test code. The practical integration risk is not that WiredTiger uses these internal structures directly, but that WiredTiger's test build inherits SQLite compile-time feature selections, diagnostics, and fault/test surfaces from this amalgamated source.

## Risks and Edge Cases

- Opcode numeric values are generated and must remain consistent with VDBE interpreter switch cases, opcode-name tables, explain output, and property flags. Manual edits would break bytecode execution or diagnostics.
- `OPFLG_INITIALIZER` must align exactly with opcode IDs. A shifted or missing entry causes operand ownership/jump analysis mistakes in code generation and VDBE validation.
- Many bit values have documented equality constraints across subsystems, enforced by assertions elsewhere. Examples include `SQLITE_FUNC_*` versus public flags and VDBE operand flags, `EP_*` versus `NC_*` and `SF_*`, `COLFLAG_*` versus `TF_*`, `OPFLAG_*` versus btree flags, and `WHERE_USE_LIMIT` versus `SF_FixedLimit`.
- Structure layout is performance- and memory-sensitive. `Expr` supports truncated allocations, `Parse` has recursive/non-recursive layout boundaries, `KeyInfo` and flexible-array structs use `offsetof()` sizing macros, and `sqlite3` contains conditional fields controlled by compile-time options.
- Mutex omission mode returns sentinel mutex pointers and reports all mutexes as held/not-held. Any code path that assumes real mutex behavior in `SQLITE_THREADSAFE=0` builds would be wrong.
- Lookaside enable/disable mutates both `bDisable` and `sz`; mismatched nesting can leave lookaside accidentally disabled or enabled in parser/schema-loading paths.
- Virtual table lifetime is deliberately deferred through `sqlite3.pDisconnect`. Freeing or disconnecting `VTable` objects eagerly can deadlock or invalidate prepared statements.
- Foreign key support is split from trigger support. With `SQLITE_OMIT_TRIGGER` but not `SQLITE_OMIT_FOREIGN_KEY`, declarations allow parsing some FK metadata while enforcement helpers become no-ops.
- Debug/test macros can change control flow in test builds: simulated I/O and disk-full errors execute caller-supplied code blocks; VDBE coverage asserts if generated branches are unannotated; memory-debug tags assert allocator ownership.
- `SQLITE_ASCII` and locale-dependent ctype branches behave differently. SQLite's ASCII tables provide deterministic SQL token rules; falling back to libc ctype could vary by locale if configured that way.
- `SQLITE_OMIT_*` macros replace functions with no-op macros that may drop side effects from arguments if future callers are not careful.
- The compile-option array must remain sorted for diagnostics and binary-search style consumers later in `ctime.c`.

## Test Signals

Useful test and validation signals for this chunk include:

- Amalgamation builds compile with default features and with representative `SQLITE_OMIT_*` combinations, proving macro stubs and conditional fields remain coherent.
- VDBE bytecode generation tests pass under `SQLITE_DEBUG` with opcode property assertions enabled.
- VDBE branch coverage builds using `SQLITE_VDBE_COVERAGE` do not report missing `VdbeCoverage*` annotations for branch opcodes generated by later code.
- Pager/pcache tests exercise fetch/release reference counts, dirty-list ordering, page-size changes, truncation, cache spilling through `xStress`, mmap page flags, and sync flags.
- Threading tests cover `SQLITE_THREADSAFE=0`, pthread mutexes, Win32 mutexes, and noop mutex builds where applicable.
- Lookaside tests verify hit/miss/full counters, disable/enable nesting, two-size lookaside behavior, and schema parsing with lookaside disabled.
- Parser and resolver tests stress expression depth, token-only/reduced expression allocation, nested name contexts, aggregates, windows, CTE materialization flags, UPSERT target analysis, generated columns, hidden columns, and RIGHT/FULL join flags.
- Virtual table tests cover per-connection `VTable` handles, transaction hooks, eponymous modules, shadow table detection, `xConnect`/`xCreate` error propagation, and deferred disconnect cleanup.
- Foreign key tests cover builds with full FK enforcement, FK parsing without triggers, and complete FK omission.
- Fault-injection tests using `sqlite3FaultSim`, benign malloc markers, `SimulateIOError`, and `SimulateDiskfullError` confirm later pager/OS code responds to allocation and I/O failures without corrupting state.
- Compile-option diagnostic tests compare `sqlite3_compileoption_get()` and `sqlite3_compileoption_used()` against the build flags represented in `sqlite3azCompileOpt[]`.

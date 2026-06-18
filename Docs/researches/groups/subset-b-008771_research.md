# subset-b-008771 research

Grouped research for SQLite core files under `sources/storage-engines/sqlite/src`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/fault.c -->
# sources/storage-engines/sqlite/src/fault.c

## Purpose

`fault.c` provides the small test/build-support layer behind SQLite's "benign malloc failure" concept. It lets fault-injection harnesses register callbacks that bracket allocations whose failure is recoverable. The main in-tree user pattern is code that can keep operating after an allocation fails, such as hash-table growth in `hash.c`; those call sites mark the allocation window so tests do not treat the injected failure as a required `SQLITE_NOMEM` path.

## Important APIs, Types, And Functions

The file is compiled only when `SQLITE_UNTESTABLE` is not defined. `BenignMallocHooks` stores `xBenignBegin` and `xBenignEnd` function pointers in `sqlite3Hooks`, a `SQLITE_WSD` global. `sqlite3BenignMallocHooks()` installs the callbacks. `sqlite3BeginBenignMalloc()` and `sqlite3EndBenignMalloc()` invoke the callbacks if present.

The `SQLITE_OMIT_WSD` branch routes access through `GLOBAL(BenignMallocHooks, sqlite3Hooks)`, matching SQLite's writable-static-data abstraction for platforms that cannot directly use globals.

## Control Flow

Registration is direct assignment into the global hook pair. A benign allocation site calls `sqlite3BeginBenignMalloc()`, performs the allocation, then calls `sqlite3EndBenignMalloc()`. Each wrapper resolves the writable static state, checks for a non-null callback, and calls it. There is no nesting counter here; any nesting semantics belong to the registered test allocator or instrumentation.

## State And Persistence Behavior

State is process-global and in-memory only. It is not database state, is not persisted to the database file, and is not per connection. Because callbacks are global, test configuration affects all SQLite connections in the process.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, `SQLITE_WSD`, `GLOBAL()`, and the `SQLITE_UNTESTABLE` build gate. `hash.c` integrates with this facility around benign rehash allocations. SQLite test controls and memory fault injection can install hooks to avoid flagging these recoverable allocations as hard failures.

## Risks

The main risk is misclassifying an allocation as benign when callers actually require success for correctness. Another risk is callback globality: concurrent tests or multiple SQLite users in one process share the hook pair. Since this file does not count nesting, hook implementations must tolerate nested begin/end sequences if callers introduce them. Builds with `SQLITE_UNTESTABLE` omit the API body, so tests that depend on hooks must use a testable build.

## Test Signals

Useful tests inject malloc failures during hash-table resizing and verify operations continue with the old table shape. Platform coverage should include normal writable static data and `SQLITE_OMIT_WSD` builds. Test builds should also verify null hooks are harmless and that begin/end callback ordering is balanced across recoverable allocation sites.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/fkey.c -->
# sources/storage-engines/sqlite/src/fkey.c

## Purpose

`fkey.c` generates VDBE code and internal trigger programs that implement SQLite foreign key checks and actions. It does not parse `REFERENCES` clauses; instead it consumes `FKey`, `Table`, `Index`, `Parse`, `Expr`, `SrcList`, and `Trigger` structures built by schema and parser code, then emits row-operation checks for INSERT, DELETE, UPDATE, DROP TABLE, and ON UPDATE/ON DELETE actions.

The implementation is omitted when `SQLITE_OMIT_FOREIGN_KEY` is defined, and most code generation is also gated by `SQLITE_OMIT_TRIGGER` because SQLite implements FK actions through trigger-like subprograms.

## Important APIs, Types, And Functions

Public internal entry points are `sqlite3FkLocateIndex()`, `sqlite3FkReferences()`, `sqlite3FkClearTriggerCache()`, `sqlite3FkDropTable()`, `sqlite3FkCheck()`, `sqlite3FkOldmask()`, `sqlite3FkRequired()`, `sqlite3FkActions()`, and `sqlite3FkDelete()`.

`sqlite3FkLocateIndex()` validates that a parent key maps to an INTEGER PRIMARY KEY, PRIMARY KEY index, or UNIQUE index with matching column set and default collations. It returns the parent `Index *` when needed and can allocate an `aiCol` mapping from parent-index order back to child-column indexes.

`sqlite3FkCheck()` is the core DML hook. For child-side modifications it calls `fkLookupParent()` to find the referenced parent row and increments or decrements immediate/deferred FK counters. For parent-side modifications it calls `fkScanChildren()` to scan child rows that reference the parent key and updates counters. `sqlite3FkActions()` invokes cached action triggers built by `fkActionTrigger()` for CASCADE, SET NULL, SET DEFAULT, and RESTRICT.

Helper routines include `exprTableRegister()` and `exprTableColumn()` for building comparison expressions, `fkChildIsModified()` and `fkParentIsModified()` for UPDATE filtering, `isSetNullAction()` for avoiding redundant checks inside SET NULL action triggers, and `fkTriggerDelete()` for freeing cached trigger structures.

## Control Flow

Foreign key enforcement uses counters. Deferred constraints update the database-handle deferred counter and are checked at transaction commit. Immediate constraints usually update a statement-level counter and abort at statement end; single-row immediate INSERT can halt immediately because no statement transaction is opened.

For child INSERT/UPDATE-new-row paths, `sqlite3FkCheck()` locates the parent table and key index, opens the parent table or unique index, skips enforcement when any child key column is NULL, applies parent affinity, and emits `OP_NotExists` or `OP_Found` checks. Missing parent rows increment the proper FK counter or halt immediately in the single-row case. For child DELETE/UPDATE-old-row paths, the same lookup decrements counters when removing a row that had represented an outstanding violation.

For parent DELETE/UPDATE-old-row paths, `fkScanChildren()` builds a WHERE clause equating parent key register values to child key columns, resolves it against a `SrcList` for the child table, runs `sqlite3WhereBegin()`, and emits `OP_FkCounter` for each child row found. Self-referential FKs add terms to exclude the current row. For parent INSERT/UPDATE-new-row paths, scans may decrement counters for now-satisfied deferred violations.

`fkActionTrigger()` lazily synthesizes a `Trigger` containing one step: SELECT RAISE for RESTRICT, DELETE for ON DELETE CASCADE, or UPDATE for CASCADE/SET NULL/SET DEFAULT update-style actions. The trigger gets cached in `FKey.apTrigger[delete/update]` and reused until schema changes call `sqlite3FkClearTriggerCache()`.

`sqlite3FkDropTable()` emits a trigger-disabled `DELETE FROM <table>` before schema removal when FK checks require it, then verifies immediate counter zero before allowing schema changes that cannot be rolled back by a statement transaction.

## State And Persistence Behavior

The file does not persist data directly; it emits VDBE programs that read and modify table contents and update runtime FK counters. Persistent FK metadata lives in schema objects and `Schema.fkeyHash`, which maps parent table names to linked lists of child `FKey` objects. Cached action triggers are in-memory members of `FKey` and are freed on schema invalidation or FK deletion. `sqlite3FkDelete()` removes FKs from `fkeyHash`, frees cached triggers, and frees the `FKey` objects when a table schema object is destroyed.

## Dependencies And Integration Points

This code is tightly integrated with the parser/code generator (`Parse`, `NameContext`, expression builders), VDBE opcodes (`OP_FkCounter`, `OP_FkIfZero`, `OP_Found`, `OP_NotExists`, `OP_MustBeInt`, `OP_Halt` via `sqlite3HaltConstraint()`), the schema layer (`Table`, `Index`, `Schema.fkeyHash`), the WHERE planner (`sqlite3WhereBegin()`/`sqlite3WhereEnd()`), table locking, authorizer callbacks, trigger subprogram execution, and database flags such as `SQLITE_ForeignKeys`, `SQLITE_DeferFKs`, and `SQLITE_FkNoAction`.

## Risks

Correctness depends on exact parent-key matching rules: partial indexes, expression indexes, non-unique indexes, and mismatched collations must not satisfy FK parent requirements. UPDATE filtering via `aChange` and rowid handling must not skip changed parent or child keys. Self-referential constraints are high risk because the code must avoid counting the row against itself while still detecting other rows. DROP TABLE behavior is delicate because schema changes are not always statement-rollbackable. Cached triggers must be cleared on schema changes or they may refer to stale table/column metadata. Authorization `SQLITE_IGNORE` intentionally treats parent columns as NULL-like, which can affect generated checks.

## Test Signals

Strong signals include SQLite FK test suites covering immediate and deferred constraints, composite keys, INTEGER PRIMARY KEY parent keys, WITHOUT ROWID tables, self-referential FKs, ON UPDATE/DELETE CASCADE, SET NULL, SET DEFAULT, RESTRICT, `PRAGMA defer_foreign_keys`, `PRAGMA foreign_keys`, DROP TABLE with dependent constraints, missing parent tables during DROP, and foreign key mismatch diagnostics. Tests should also stress OOM during `aiCol` allocation and trigger synthesis, authorizer `SQLITE_IGNORE`, generated columns with SET DEFAULT, and schema invalidation after ALTER TABLE.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/fkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/func.c -->
# sources/storage-engines/sqlite/src/func.c

## Purpose

`func.c` implements and registers many SQLite built-in SQL scalar, aggregate, and window-capable functions. It covers core string/blob/numeric functions, LIKE/GLOB matching and planner metadata, aggregate state machines for sum/count/min/max/group_concat, optional math and percentile families, optional load-extension and diagnostics functions, and registration glue that populates the global `sqlite3BuiltinFunctions` hash during initialization.

Date/time, JSON, window-specific functions, and ALTER TABLE functions are registered from other modules but are coordinated by `sqlite3RegisterBuiltinFunctions()`.

## Important APIs, Types, And Functions

Externally visible internal functions are `sqlite3_strglob()`, `sqlite3_strlike()`, `sqlite3QuoteValue()`, `sqlite3RegisterPerConnectionBuiltinFunctions()`, `sqlite3RegisterLikeFunctions()`, `sqlite3IsLikeFunction()`, and `sqlite3RegisterBuiltinFunctions()`.

Scalar implementations include `minmaxFunc`, `typeofFunc`, `subtypeFunc`, `lengthFunc`, `bytelengthFunc`, `absFunc`, `instrFunc`, `printfFunc`, `substrFunc`, `roundFunc`, `upperFunc`, `lowerFunc`, `randomFunc`, `randomBlob`, `last_insert_rowid`, `changes`, `total_changes`, `nullifFunc`, `versionFunc`, `sourceidFunc`, `errlogFunc`, compile-option functions, `unistrFunc`, `quoteFunc`, `unicodeFunc`, `charFunc`, `hexFunc`, `unhexFunc`, `zeroblobFunc`, `replaceFunc`, `trimFunc`, `concatFunc`, `concatwsFunc`, optional `soundexFunc`, optional `loadExt`, optional math functions, and debug functions such as `filestatFunc`, `fpdecodeFunc`, and `parseuriFunc`.

Pattern matching is centered on `struct compareInfo`, `patternCompare()`, `likeFunc()`, `sqlite3_strlike()`, and `sqlite3_strglob()`. Aggregate/window state types include `SumCtx`, `CountCtx`, `GroupConcatCtx`, and optional `Percentile`.

Registration uses the `FUNCTION`, `VFUNCTION`, `DFUNCTION`, `SFUNCTION`, `LIKEFUNC`, `WAGGREGATE`, `MFUNCTION`, and `INLINE_FUNC` macros to describe function name, arity, encoding, user data, callbacks, and flags.

## Control Flow

Scalar functions receive `sqlite3_context`, argument count, and `sqlite3_value **`, then return using `sqlite3_result_*()` APIs. Most functions explicitly preserve NULL behavior by returning without setting a result. Allocation helpers such as `contextMalloc()` enforce `SQLITE_LIMIT_LENGTH` and translate OOM/too-large conditions into context errors.

String functions convert values through SQLite value APIs, which may change encoding or materialize text/blob data. Functions such as `length()`, `substr()`, `instr()`, `trim()`, `unistr()`, `char()`, and LIKE/GLOB explicitly walk UTF-8. Blob paths usually operate on byte counts.

`patternCompare()` recursively evaluates LIKE/GLOB wildcard semantics with optimizations for ASCII stop characters and a pattern length limit enforced by `likeFunc()`. `sqlite3IsLikeFunction()` exposes wildcard and case-sensitivity metadata to the query planner so LIKE range optimizations can be considered only for compatible built-ins and literal escapes.

Aggregate functions use `sqlite3_aggregate_context()` for per-group or per-window state. `sumStep()` keeps exact integer accumulation until overflow or non-integer input forces Kahan-Babuska-Neumaier floating accumulation. Window inverse callbacks subtract rows for `sum`, `count`, `group_concat`, and optional percentile. `group_concat` appends separators before values for historical compatibility and tracks separator lengths for sliding window removal. Optional percentile accumulates doubles, validates a stable percentile argument, sorts on demand, and keeps sorted order for window usage.

`sqlite3RegisterBuiltinFunctions()` builds a static `FuncDef` array, calls module registration hooks for alter/window/date/json functions, and inserts all built-ins into the global function hash. `sqlite3RegisterPerConnectionBuiltinFunctions()` overloads `MATCH` per connection for virtual-table behavior. `sqlite3RegisterLikeFunctions()` can replace LIKE implementations when case sensitivity changes.

## State And Persistence Behavior

Most state is transient per function invocation, aggregate group, window frame, or database connection. Random functions use SQLite PRNG state. `last_insert_rowid()`, `changes()`, and `total_changes()` read connection state. `sqlite_log()` writes to the configured log callback as a side effect. `load_extension()` can load process code only when the connection has enabled the SQL function. Built-in function definitions live in the process-global `sqlite3BuiltinFunctions` hash after initialization and are read-only afterward except for per-connection overloads and LIKE re-registration.

No database pages are written directly by this file, but function results can be persisted by SQL statements that store them.

## Dependencies And Integration Points

`func.c` depends on `sqliteInt.h`, `vdbeInt.h`, SQLite value/result APIs, collation handling (`OP_CollSeq`, `sqlite3MemCompare()`), memory APIs, UTF-8 helpers, string accumulators, PRNG, compile-option APIs, extension loading, VFS file-control diagnostics, parser URI logic, and libm when `SQLITE_ENABLE_MATH_FUNCTIONS` is enabled. It integrates with the planner through flags such as `SQLITE_FUNC_LIKE`, `SQLITE_FUNC_CASE`, `SQLITE_FUNC_LENGTH`, `SQLITE_FUNC_BYTELEN`, `SQLITE_FUNC_MINMAX`, `SQLITE_FUNC_COUNT`, `SQLITE_FUNC_ANYORDER`, `SQLITE_INNOCUOUS`, and `SQLITE_SELFORDER1`.

Build options significantly alter surface area: `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_ENABLE_MATH_FUNCTIONS`, `SQLITE_ENABLE_PERCENTILE`, `SQLITE_ENABLE_UNKNOWN_SQL_FUNCTION`, `SQLITE_SOUNDEX`, `SQLITE_DEBUG`, and `SQLITE_ENABLE_FILESTAT`.

## Risks

High-risk areas include memory-limit enforcement, UTF-8 boundary walking, text/blob coercion order, overflow handling, aggregate inverse correctness, LIKE/GLOB recursion and pattern complexity, and planner flags that allow transformations only when semantics are exact. `load_extension()` is intentionally security-sensitive. `quote()` and `unistr_quote()` must produce SQL literals without truncation or incorrect escaping except for documented embedded-NUL behavior. Optional percentile holds all non-null numeric values, so memory growth is proportional to input rows. Math and floating functions must handle NULL, domain errors, infinities, and compile-time libm availability consistently.

## Test Signals

Signals include SQL logic tests for every built-in function, NULL propagation, type coercion, UTF-8 multi-byte handling, invalid UTF-8 tolerance where expected, maximum length failures, OOM injection, LIKE/GLOB escape semantics and planner range optimization, case-sensitive LIKE re-registration, aggregate/window inverse equivalence to non-window results, integer overflow in `abs()` and `sum()`, `group_concat` with varying separators in windows, extension-loading authorization, optional math domain behavior, percentile validation and interpolation, and debug-only function availability under the correct build flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/func.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/global.c -->
# sources/storage-engines/sqlite/src/global.c

## Purpose

`global.c` defines process-global SQLite constants and mutable configuration state. It provides character classification/case tables, comparison opcode truth tables, default compile-time configuration values, the singleton `sqlite3Config`, the global built-in function hash, diagnostic counters, the default pending-byte location, tracing flags, opcode properties, the default collation name, and standard type-name metadata.

## Important APIs, Types, And Data

Key exported objects are `sqlite3UpperToLower`, `sqlite3aLTb`, `sqlite3aEQb`, `sqlite3aGTb`, `sqlite3CtypeMap`, `sqlite3Config`, `sqlite3BuiltinFunctions`, optional `sqlite3CoverageCounter`, optional `sqlite3NProfileCnt`, `sqlite3PendingByte`, `sqlite3TreeTrace`, `sqlite3WhereTrace`, `sqlite3OpcodeProperty`, `sqlite3StrBINARY`, `sqlite3StdTypeLen`, `sqlite3StdTypeAffinity`, and `sqlite3StdType`.

`sqlite3UpperToLower` maps bytes for ASCII or EBCDIC lowercasing. It intentionally appends 18 boolean entries used by comparison opcode truth tables to avoid out-of-bounds indexing. `sqlite3CtypeMap` is SQLite's compact replacement for libc character classifiers. `sqlite3Config` is a `SQLITE_WSD struct Sqlite3Config` initialized from many compile-time defaults such as URI behavior, lookaside size, mmap limits, sorter settings, memory methods, mutex methods, page-cache methods, deserialize limits, localtime fault hooks, and debug tuning fields.

## Control Flow

The file mostly has static initialization, not executable control flow. SQLite startup and configuration APIs read and mutate `sqlite3Config` during initialization. VDBE, tokenizer, parser, expression comparison, and planner code read the lookup tables and globals directly. `opcodes.h` supplies `OPFLG_INITIALIZER` for `sqlite3OpcodeProperty`.

## State And Persistence Behavior

State is process-global. `sqlite3Config` is mutable during global initialization and through `sqlite3_config()` paths, then much of it becomes effectively fixed while SQLite is initialized. `sqlite3PendingByte` can be changed by test control when writable static data is available, but changing it away from `0x40000000` makes database file locking layout incompatible and is for testing only. Trace flags and coverage counters are diagnostic process state. None of these globals are stored in a database file, although settings such as pending-byte location and mmap limits influence file access behavior.

## Dependencies And Integration Points

This file depends on `sqliteInt.h` and generated `opcodes.h`. It is consumed broadly by tokenizer and identifier logic, SQL comparison opcodes, memory/mutex/page-cache initialization, VDBE opcode metadata, built-in function registration in `func.c`, type-affinity code, and test-control/debug facilities. Compile-time macros heavily shape the initialized values: `SQLITE_ASCII`, `SQLITE_EBCDIC`, `SQLITE_USE_URI`, `SQLITE_ALLOW_COVERING_INDEX_SCAN`, `SQLITE_SORTER_PMASZ`, `SQLITE_STMTJRNL_SPILL`, `SQLITE_DEFAULT_LOOKASIDE`, `SQLITE_MEMDB_DEFAULT_MAXSIZE`, `SQLITE_ENABLE_SQLLOG`, `SQLITE_VDBE_COVERAGE`, `SQLITE_OMIT_DESERIALIZE`, `SQLITE_ALLOW_ROWID_IN_VIEW`, `SQLITE_DEBUG`, `VDBE_PROFILE`, and `SQLITE_OMIT_WSD`.

## Risks

The highest risks are ABI/layout drift in `Sqlite3Config` initialization, table contents that must match tokenizer/collation/opcode assumptions, and compile-time option combinations that change array contents or struct fields. The appended comparison truth-table trick relies on comparison opcodes being consecutive and ordered as expected. Character classification is deliberately ASCII/EBCDIC-centric and not Unicode case mapping. `sqlite3PendingByte` must not be changed in production. Since these are globals, thread-safety depends on SQLite's initialization and mutex protocol.

## Test Signals

Signals include startup/configuration tests, tokenizer and identifier classification tests, ASCII and EBCDIC build coverage where supported, comparison opcode truth-table assertions, type-affinity tests for standard type names, opcode-property generation checks, `sqlite3_config()` option tests, test-control coverage for pending-byte relocation, trace flag tests, and UBSAN/ASAN runs validating no out-of-bounds table access.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/global.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/hash.c -->
# sources/storage-engines/sqlite/src/hash.c

## Purpose

`hash.c` implements SQLite's small internal case-insensitive string-key hash table. It is used for schema and function lookup structures where keys are stable strings owned elsewhere. The implementation combines a global doubly linked element list with an optional bucket table that is allocated only after the table grows.

## Important APIs, Types, And Functions

The public internal API is `sqlite3HashInit()`, `sqlite3HashClear()`, `sqlite3HashFind()`, and `sqlite3HashInsert()`, declared in `hash.h`. Internal helpers are `strHash()`, `insertElement()`, `rehash()`, `findElementWithHash()`, and `removeElement()`.

`strHash()` computes a case-insensitive hash with Knuth multiplicative mixing, masking off the ASCII or EBCDIC case bit. Equality is still checked with `sqlite3StrICmp()`. `rehash()` allocates the bucket array with `sqlite3Malloc()` inside benign malloc hooks, caps size with `SQLITE_MALLOC_SOFT_LIMIT`, uses `sqlite3MallocSize()` to account for actual allocation size, and reinserts all elements into buckets. `sqlite3HashInsert()` inserts, replaces, or deletes by passing non-null data, replacement data, or NULL data respectively.

## Control Flow

Initialization zeroes the `Hash` object. Lookups compute the hash and either scan the bucket's chain/count range or linearly scan the global list when no bucket table exists. Insert first searches for an existing key. If found, non-null data replaces the payload and key pointer while NULL data removes the element. If not found and data is non-null, it allocates a `HashElem`, stores the caller-owned key pointer and data pointer, increments count, optionally rehashes when count is at least five and more than twice the bucket count, then links the element into the bucket/list. Deleting the last element calls `sqlite3HashClear()` to release the bucket table and reset the structure.

## State And Persistence Behavior

All state is in-memory in the caller-provided `Hash` object plus heap-allocated `HashElem` and bucket array memory. Keys and payloads are not owned by the hash table; `sqlite3HashClear()` frees elements and buckets but not `pKey` strings or `data` payloads. There is no persistence and no built-in locking.

## Dependencies And Integration Points

The implementation depends on `sqliteInt.h`, SQLite memory APIs, `sqlite3StrICmp()`, benign malloc hooks from `fault.c`, `SQLITE_MALLOC_SOFT_LIMIT`, and the `Hash`/`HashElem` layout in `hash.h`. It is used by schemas (`tblHash`, `idxHash`, `trigHash`, `fkeyHash`) and by global function registration/lookup.

## Risks

Callers must keep key strings alive and must separately manage payload lifetime. An allocation failure during new-element allocation is hard for insertion and returns the input data pointer, while rehash allocation failure is benign and leaves the table valid but potentially slower. The bucket `chain` pointer references the first element in a contiguous run within the global linked list; insertion/removal must preserve bucket counts and list order. Case-insensitive hashing means keys differing only by case replace each other. No thread safety exists without external schema/function mutexes.

## Test Signals

Signals include insertion, replacement, deletion, deleting the last element, lookup before and after rehash, forced rehash OOM preserving all entries, case-insensitive key matching, `sqliteHashFirst()`/`sqliteHashNext()` iteration over all elements, soft-limit builds, and schema/function lookup tests that exercise hash lifetime under schema reset.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/hash.h -->
# sources/storage-engines/sqlite/src/hash.h

## Purpose

`hash.h` declares SQLite's generic internal hash-table structure and access macros. It exposes enough layout for efficient iteration and count checks while documenting that callers should modify tables only through the functions implemented in `hash.c`.

## Important APIs, Types, And Functions

The header defines `Hash` and `HashElem`. `Hash` contains bucket count, entry count, the first element of the global list, and an optional bucket array whose entries store a count plus a pointer to the first element for that hash. `HashElem` contains next/previous list links, payload pointer, caller-owned key pointer, and cached hash value.

Declared functions are `sqlite3HashInit(Hash*)`, `sqlite3HashInsert(Hash*, const char *pKey, void *pData)`, `sqlite3HashFind(const Hash*, const char *pKey)`, and `sqlite3HashClear(Hash*)`. Macros are `sqliteHashFirst(H)`, `sqliteHashNext(E)`, `sqliteHashData(E)`, and `sqliteHashCount(H)`.

## Control Flow

The header itself has no runtime control flow. It establishes the iteration idiom: start at `sqliteHashFirst(&h)`, advance with `sqliteHashNext(p)`, and fetch payloads with `sqliteHashData(p)`. Deletion is expressed through `sqlite3HashInsert()` with a NULL payload.

## State And Persistence Behavior

`Hash` instances are embedded in higher-level in-memory objects such as schemas or function registries. The table owns its `HashElem` nodes and bucket array but not payloads or key strings. Nothing in the header represents persistent database state.

## Dependencies And Integration Points

`hash.h` is included by SQLite internals via `sqliteInt.h` and is coupled to `hash.c`'s bucket/list invariants. Schema code and function lookup code access `Hash` through this API and sometimes rely on the exposed macros for iteration and counts.

## Risks

Because the structures are visible, accidental direct mutation can corrupt bucket/list invariants. Iterating while inserting or deleting requires caller discipline. The key pointer is not copied, so transient key storage is unsafe. The commented-out key/keysize macros indicate the current implementation does not expose key data to callers through the public macro set.

## Test Signals

Signals are mostly the `hash.c` behavior tests plus compile coverage for users that embed `Hash`, iteration over schema hash tables, count accuracy through `sqliteHashCount()`, and ABI-sensitive builds that include this header through amalgamation and non-amalgamation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/hwtime.h -->
# sources/storage-engines/sqlite/src/hwtime.h

## Purpose

`hwtime.h` provides an inline `sqlite3Hwtime()` routine for high-resolution timing in profiling, debugging, and analysis builds. It is not intended for normal deliverables; unsupported platforms fall back to a zero-returning function.

## Important APIs, Types, And Functions

The only API is `sqlite3Hwtime()`, returning a `sqlite_uint64` or `sqlite3_uint64` counter value depending on branch typedef usage. Implementations are selected for MSVC/Win32 via `QueryPerformanceCounter()`, GCC x86/i586 and x86_64 via `rdtsc`, GCC aarch64 via `mrs cntvct_el0`, GCC ppc via a stable time-base read loop, and a fallback stub returning zero.

## Control Flow

Preprocessor checks choose exactly one inline implementation. The x86 variants read low/high TSC registers and combine them. The aarch64 branch reads the virtual counter register. The ppc branch reads upper/lower/upper time-base values until the upper value is stable. The fallback has no timing side effect.

## State And Persistence Behavior

There is no mutable SQLite state and no persistence. Return values are raw platform counters, not normalized wall-clock time. Their units, monotonicity, synchronization across cores, and availability depend on platform and privilege behavior.

## Dependencies And Integration Points

The header depends on platform compiler macros and, on Windows, `windows.h` plus `profileapi.h`. It is referenced by profiling/debug code such as `VDBE_PROFILE` paths, with `global.c` offering `sqlite3NProfileCnt` as an alternate counter in some profiling builds.

## Risks

Inline assembly and platform macros are the main portability risks. `rdtsc` can be non-serializing and may not represent elapsed real time across frequency changes or CPU migration on older systems. Aarch64 access to `cntvct_el0` depends on OS configuration. The fallback silently returns zero, so profiling consumers must tolerate no timing support. Typedef spelling differences (`sqlite_uint64` vs `sqlite3_uint64`) must match surrounding SQLite headers.

## Test Signals

Signals include compilation on each supported architecture/compiler branch, smoke tests that repeated calls are callable and generally nondecreasing where the platform promises it, and profiling builds verifying zero fallback does not break VDBE profile output. Cross-compilation is useful because most risk is preprocessor/assembler compatibility rather than algorithmic behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/hwtime.h -->

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 30979-39365

Chunk id: `subset-b-009016`

Source range researched: `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c` lines 30979-39365.

## Purpose

This chunk covers several core SQLite subsystems inside the amalgamated `sqlite3.c` copy vendored under WiredTiger tests:

- the memory allocator facade, connection-scoped allocation helpers, lookaside allocator handling, OOM propagation, and API exit error normalization;
- SQLite's locale-independent printf/string-accumulator implementation, reference-counted strings, and debug parse-tree rendering;
- process-global random bytes, portable worker thread wrappers, UTF-8/UTF-16 conversion helpers, numeric parsing, varint encoding, endian helpers, overflow-safe arithmetic, logarithmic estimates, VList symbol storage, and generic hash tables;
- opcode-name metadata for VDBE explain/debug builds;
- the complete experimental `kvvfs` key/value VFS and the start of the Unix VFS declarations and syscall indirection table.

The code is foundational infrastructure rather than a single feature path. It is used by nearly every upper SQLite layer in the amalgamation: parser, VDBE, btree/pager, virtual tables, test controls, extension APIs, and VFS dispatch.

## Important APIs, Types, And Functions

Memory and OOM handling:

- `sqlite3Malloc()`, `sqlite3_malloc()`, `sqlite3_malloc64()`, `sqlite3_free()`, `sqlite3Realloc()`, `sqlite3_realloc()`, and `sqlite3_realloc64()` wrap the configured global allocator in `sqlite3GlobalConfig.m`, enforce `SQLITE_MAX_ALLOCATION_SIZE`, maintain memory status counters when `bMemstat` is enabled, and use `mem0.mutex` around global memory accounting.
- `sqlite3DbMallocRaw()`, `sqlite3DbMallocRawNN()`, `sqlite3DbMallocZero()`, `sqlite3DbFreeNN()`, `sqlite3DbNNFreeNN()`, `sqlite3DbFree()`, `sqlite3DbRealloc()`, and `sqlite3DbReallocOrFree()` add connection-aware behavior, including lookaside allocation, `db->mallocFailed` consistency, `db->pnBytesFreed` measurement mode, and memory-debug type tags.
- `sqlite3OomFault()`, `sqlite3OomClear()`, `apiHandleError()`, and `sqlite3ApiExit()` centralize how an OOM flips `db->mallocFailed`, disables lookaside, interrupts active VDBEs, records parse errors, and maps API returns to `SQLITE_NOMEM_BKPT`.
- String duplication helpers include `sqlite3DbStrDup()`, `sqlite3DbStrNDup()`, `sqlite3DbSpanDup()`, and `sqlite3SetString()`.

Formatting and string accumulation:

- `sqlite3_str_vappendf()` implements SQLite's custom formatter. It supports standard conversions plus SQLite extensions: `%q`, `%Q`, `%w`, `%z`, `%T`, `%S`, `%r`, and the alternate `!` flag for UTF-8 character width/precision or higher precision floating-point formatting.
- `StrAccum` APIs include `sqlite3StrAccumSetError()`, `sqlite3StrAccumEnlarge()`, `sqlite3_str_append()`, `sqlite3_str_appendall()`, `sqlite3_str_appendchar()`, `sqlite3_str_appendf()`, `sqlite3StrAccumFinish()`, `sqlite3ResultStrAccum()`, `sqlite3_str_new()`, `sqlite3_str_finish()`, `sqlite3_str_reset()`, `sqlite3_str_errcode()`, `sqlite3_str_length()`, and `sqlite3_str_value()`.
- Public printf wrappers are `sqlite3_vmprintf()`, `sqlite3_mprintf()`, `sqlite3_vsnprintf()`, `sqlite3_snprintf()`, and `sqlite3_log()`. Internal wrappers include `sqlite3VMPrintf()` and `sqlite3MPrintf()`.
- `sqlite3RCStrRef()`, `sqlite3RCStrUnref()`, `sqlite3RCStrNew()`, and `sqlite3RCStrResize()` manage heap strings with a small reference-count header.

Debug tree views:

- Under `SQLITE_DEBUG`, `sqlite3TreeViewLine()`, `sqlite3TreeViewExpr()`, `sqlite3TreeViewExprList()`, `sqlite3TreeViewSelect()`, `sqlite3TreeViewSrcList()`, `sqlite3TreeViewWith()`, `sqlite3TreeViewWindow()`, `sqlite3TreeViewWinFunc()`, `sqlite3TreeViewUpsert()`, `sqlite3TreeViewTrigger()` and related `sqlite3Show*()` entry points print parser structures for diagnostics.

Randomness and threading:

- `sqlite3_randomness()` exposes random bytes from a process-global ChaCha20 PRNG state, seeded from the active VFS using `sqlite3OsRandomness()`.
- `sqlite3PrngSaveState()` and `sqlite3PrngRestoreState()` are test-control helpers when not compiled with `SQLITE_UNTESTABLE`.
- `sqlite3ThreadCreate()` and `sqlite3ThreadJoin()` abstract worker execution across pthreads, Win32 threads, or a no-real-thread fallback depending on platform macros and `SQLITE_MAX_WORKER_THREADS`.

Text encoding and utility functions:

- UTF helpers include `sqlite3AppendOneUtf8Character()`, `sqlite3Utf8Read()`, `sqlite3Utf8ReadLimited()`, `sqlite3VdbeMemTranslate()`, `sqlite3VdbeMemHandleBom()`, `sqlite3Utf8CharLen()`, `sqlite3Utf16to8()`, `sqlite3Utf16ByteLen()`, and test-only `sqlite3UtfSelfTest()`.
- Error utilities include `sqlite3Error()`, `sqlite3ErrorClear()`, `sqlite3SystemError()`, `sqlite3ErrorWithMsg()`, `sqlite3ProgressCheck()`, `sqlite3ErrorMsg()`, and `sqlite3ErrorToParser()`.
- Token/string helpers include `sqlite3Dequote()`, `sqlite3DequoteExpr()`, `sqlite3DequoteNumber()`, `sqlite3DequoteToken()`, `sqlite3TokenInit()`, `sqlite3_stricmp()`, `sqlite3StrICmp()`, `sqlite3_strnicmp()`, and `sqlite3StrIHash()`.
- Numeric helpers include `sqlite3AtoF()`, `sqlite3Int64ToText()`, `sqlite3Atoi64()`, `sqlite3DecOrHexToI64()`, `sqlite3GetInt32()`, `sqlite3Atoi()`, `sqlite3FpDecode()`, and `sqlite3GetUInt32()`.
- Binary encoding helpers include `sqlite3PutVarint()`, `sqlite3GetVarint()`, `sqlite3GetVarint32()`, `sqlite3VarintLen()`, `sqlite3Get4byte()`, `sqlite3Put4byte()`, `sqlite3HexToInt()`, and `sqlite3HexToBlob()`.
- Safety/math/planner helpers include `sqlite3SafetyCheckOk()`, `sqlite3SafetyCheckSickOrOk()`, `sqlite3AddInt64()`, `sqlite3SubInt64()`, `sqlite3MulInt64()`, `sqlite3AbsInt32()`, `sqlite3FileSuffix3()`, `sqlite3LogEstAdd()`, `sqlite3LogEst()`, `sqlite3LogEstFromDouble()`, and `sqlite3LogEstToInt()`.
- `sqlite3VListAdd()`, `sqlite3VListNumToName()`, and `sqlite3VListNameToNum()` implement a compact integer-array-backed variable-name map.
- `sqlite3HashInit()`, `sqlite3HashClear()`, `sqlite3HashFind()`, and `sqlite3HashInsert()` implement SQLite's case-insensitive string-key hash table.

VFS code:

- `sqlite3OpcodeName()` maps VDBE opcode integers to names and optional explain comments.
- `KVVfsFile`, `sqlite3OsKvvfsObject`, `kvvfs_db_io_methods`, `kvvfs_jrnl_io_methods`, and `sqlite3_kvvfs_methods` define the experimental key/value VFS.
- `kvstorageRead()`, `kvstorageWrite()`, and `kvstorageDelete()` are the native low-level key/value adapter; WASM builds may replace them through `sqlite3KvvfsMethods`.
- `kvvfsEncode()`, `kvvfsDecode()`, `kvvfsDecodeJournal()`, `kvvfsReadFileSize()`, and `kvvfsWriteFileSize()` implement the text-only persistence encoding for binary database pages and rollback journals.
- `kvvfsOpen()`, `kvvfsReadDb()`, `kvvfsWriteDb()`, `kvvfsReadJrnl()`, `kvvfsWriteJrnl()`, `kvvfsTruncateDb()`, `kvvfsTruncateJrnl()`, `kvvfsSyncJrnl()`, `kvvfsFileControlDb()`, and related methods implement the `sqlite3_io_methods` and `sqlite3_vfs` contracts.
- The start of `os_unix.c` defines Unix VFS feature macros, `unixFile`, `UnixUnusedFd`, syscall wrappers such as `osOpen`, `osClose`, `osRead`, `osPread`, `osWrite`, `osPwrite`, and related platform configuration.

## Control Flow

Allocation flow usually enters through either a public API allocator or a connection-scoped helper. Public calls initialize SQLite unless auto-init is omitted, reject zero or oversized allocations, and delegate to `sqlite3Malloc()` or `sqlite3Realloc()`. With memory statistics enabled, allocations enter `mem0.mutex`, round up sizes via the configured allocator, check soft and hard memory limits, possibly fire the malloc alarm, perform allocation, and update status counters. Connection-scoped allocations first try lookaside if enabled and the request fits; otherwise they call heap allocation and, on failure, set the connection OOM state.

OOM flow is deliberately sticky per connection. Once `db->mallocFailed` is set, later `sqlite3DbMallocRawNN()` calls fail consistently until `sqlite3OomClear()` sees no active VDBEs. `sqlite3ApiExit()` is the normal API-exit gate that converts pending OOM state or `SQLITE_IOERR_NOMEM` into `SQLITE_NOMEM_BKPT` and updates the connection error object.

Formatting flow in `sqlite3_str_vappendf()` scans ordinary text until `%`, parses flags, width, precision, length modifiers, and conversion type, then dispatches through `fmtinfo`. Integer conversions build output backwards into a stack or temporary buffer. Floating-point conversions call `sqlite3FpDecode()` and then render fixed, exponential, or generic form. SQL escaping conversions count required extra bytes before allocation, then duplicate quotes or emit `unistr()`-style escapes for alternate forms. Internal-only `%T` and `%S` return immediately if the `SQLITE_PRINTF_INTERNAL` flag is absent.

`StrAccum` grows lazily. Appends use the current buffer if possible, otherwise `sqlite3StrAccumEnlarge()` doubles toward the maximum allocation and preserves stack-buffer content when switching to heap. Error states are sticky and reset/free allocated buffers when necessary.

Tree-view routines recursively walk parse structures. `sqlite3TreeViewPush()` and `sqlite3TreeViewPop()` maintain indentation state, while each structure-specific routine computes how many child nodes remain so printed branches have correct continuation markers. These routines are compiled only in debug/test-oriented builds.

The PRNG flow locks `SQLITE_MUTEX_STATIC_PRNG`, optionally resets state for `N<=0` or null buffer, seeds ChaCha20 state from the active VFS on first use, and emits bytes from a cached 64-byte block, generating new blocks and incrementing the block counter as needed.

Thread wrapper flow creates an opaque `SQLiteThread` object. On pthread/Win32 builds it attempts to spawn a worker unless core mutexes are disabled or fault simulation requests deterministic sequential execution. The fallback implementation records the task and either runs it at create time or join time.

UTF translation branches by source and destination encoding. UTF-16 endian swaps happen in-place after making the `Mem` writeable. UTF-8/UTF-16 conversions allocate a worst-case output buffer, iterate code points with validation behavior controlled by compile-time options, release the old `Mem`, and install the new text buffer.

Numeric parsing uses conservative, encoding-aware scanners. `sqlite3AtoF()` parses sign, significand, decimal point, exponent, and trailing whitespace, then performs double-double scaling with `dekkerMul2()` for precision. `sqlite3Atoi64()` skips spaces and zeros, accumulates a 64-bit unsigned magnitude, compares 19-digit values to 2^63, and returns detailed status codes for overflow or trailing text.

Varint flow uses short fast paths for 1- and 2-byte encodings and a longer optimized decoder that reads alternating bytes into bit slots for up to 9 bytes. Hash-table insertion first searches by case-insensitive hash and key, replaces/removes existing elements if found, otherwise allocates a `HashElem`, resizes when count exceeds bucket pressure, and links into both the global list and optional bucket chain.

`kvvfs` maps SQLite file operations to text keys. Database pages are keyed by page number and encoded as text. Rollback journal writes accumulate in memory and persist on `xSync` as a length-prefixed encoded blob. Database size is stored separately under key `sz` and refreshed on lock acquisition. The VFS accepts only `local`, `session`, `local-journal`, and `session-journal` names.

The Unix VFS section in this chunk is setup-oriented: it selects feature macros, includes platform headers, defines `unixFile` state, and begins the syscall table so later VFS code can call `osOpen`, `osRead`, etc. through runtime-overridable function pointers.

## State And Persistence Behavior

Global process state includes:

- `sqlite3GlobalConfig`, especially allocator methods, logging callback, test callback, and core mutex mode;
- `mem0`, which tracks memory mutex, alarm threshold, hard limit, and near-full status;
- `sqlite3Prng`, a writable-static-data PRNG state vector with cached output bytes;
- `randomnessPid` in the Unix VFS prelude, used later to detect fork-related PRNG reseeding needs;
- `aSyscall[]`, the Unix VFS syscall indirection table, which can be overridden for tests and sandboxing.

Connection-local state includes:

- `db->lookaside` freelists and statistics, including optional two-size lookaside pools;
- `db->mallocFailed`, `db->bBenignMalloc`, `db->nVdbeExec`, `db->u1.isInterrupted`, `db->pParse`, `db->pErr`, `db->errCode`, `db->errByteOffset`, and `db->iSysErrno`;
- `db->pnBytesFreed`, which switches free paths into size-measurement mode instead of actually freeing.

`StrAccum` instances carry their own buffer pointer, allocation size, maximum allocation, character count, error code, database pointer, and flags indicating whether the buffer is heap-owned or internal formatting is allowed.

`kvvfs` persists state externally through text keys. Native non-WASM builds implement those keys as local files named `kvvfs-<class>-<key>`. Database page keys are page numbers; `sz` stores file size; `jrnl` stores the rollback journal. The VFS keeps per-open in-memory cache state in `KVVfsFile`: `aData`, `aJrnl`, `nJrnl`, `szPage`, `szDb`, and the selected storage class.

The hash table keeps an insertion/global iteration list (`Hash.first`) plus an optional bucket table (`Hash.ht`). Keys are not copied on insertion, so callers own key lifetimes.

## Dependencies And Integration Points

This chunk depends heavily on definitions from earlier parts of the amalgamation: `sqlite3`, `Mem`, `Parse`, `Expr`, `Select`, `SrcList`, `With`, `Window`, `Trigger`, `Hash`, `HashElem`, `VList`, `FpDecode`, `StrAccum`, `PrintfArguments`, allocator/debug macros, opcodes, token constants, mutex APIs, VFS APIs, and VDBE memory APIs.

External and platform dependencies include:

- C runtime functions such as `memcpy`, `memset`, `strlen`, `strspn`, `strncmp`, `strcmp`, `strtoll`, `fopen`, `fputs`, `fread`, `fclose`, and `fprintf`;
- math `isnan()` where available;
- pthreads or Win32 `_beginthreadex()` for worker threads;
- Unix headers and calls such as `open`, `close`, `access`, `stat`, `fstat`, `fcntl`, `read`, `pread`, `write`, `pwrite`, `ftruncate`, `unlink`, `mkdir`, `rmdir`, `gettimeofday`, and optional mmap/locking headers.

Integration points include:

- application-facing APIs: `sqlite3_malloc*`, `sqlite3_free`, `sqlite3_realloc*`, `sqlite3_mprintf`, `sqlite3_snprintf`, `sqlite3_str_*`, `sqlite3_log`, `sqlite3_randomness`, `sqlite3_stricmp`, and `sqlite3_strnicmp`;
- parser and error reporting: `%T`/`%S` formatter extensions, error byte offsets, `sqlite3ErrorMsg()`, `sqlite3ErrorToParser()`, and tree-view debugging;
- VDBE and pager encoding: varints, endian integer access, UTF memory translation, rowid/numeric parsing, opcode names, and overflow-checked arithmetic;
- VFS registration: `sqlite3_os_init()` for `SQLITE_OS_KV`, `sqlite3KvvfsInit()` for optional Unix `kvvfs`, and the Unix VFS syscall abstraction used by later file I/O code.

## Risks And Edge Cases

- The allocator path relies on correct mutex discipline. Many connection-scoped functions assert that `db->mutex` is held; violating that can corrupt lookaside freelists or read stale OOM state.
- Lookaside pointer classification is range-based. Incorrect `pStart`, `pMiddle`, `pEnd`, or `pTrueEnd` setup would cause wrong free-list routing or wrong size reporting.
- `db->mallocFailed` is intentionally sticky. Code that bypasses `sqlite3ApiExit()` or clears it too early can make later allocation assumptions unsafe.
- `sqlite3_str_vappendf()` handles width, precision, SQL escaping, UTF-8 character counting, and floating-point rendering in one large state machine. Risks concentrate around large precision/width values, `mxAlloc` enforcement, `%z` ownership transfer, and internal-only format strings being exposed incorrectly.
- `sqlite3_log()` intentionally uses a fixed stack buffer and no dynamic allocation because it can be called while allocator mutexes are held. Format strings used while logging from allocator-sensitive paths must avoid conversions that require temporary allocation.
- UTF conversion behavior around invalid surrogate pairs differs with `SQLITE_REPLACE_INVALID_UTF`. Callers should not assume all malformed UTF is rejected in the same way across builds.
- Numeric parsing has many boundary conditions: 2^63, `SMALLEST_INT64`, signed zero, huge exponents, UTF-16 high bytes, digit separators in quoted numbers, and optional hexadecimal integers.
- Varint decoding assumes callers have enough readable bytes for the encoded value. Short or corrupt database records are normally guarded by higher-level page/record validation.
- Hash keys are not copied by `sqlite3HashInsert()`. The table becomes unsafe if callers pass temporary key storage.
- `kvvfsDecodeJournal()` appears sensitive to malformed length prefixes; the loop increments `i` before using `zTxt[i]` for digit value, so corrupted or unexpected text could produce an incorrect allocation size before decode failure. This VFS is explicitly experimental.
- `kvvfs` has no real locking, returns zero randomness, supports only rollback-journal style methods, and stores binary database content through text expansion. It is mainly a constrained or WASM-oriented storage bridge, not a general durable multi-process filesystem replacement.
- `kvvfsReadDb()` uses a large fixed `SQLITE_KVOS_SZ` scratch buffer and special handling for reads below offset 512. The page-size and offset assertions matter for pager integration.
- The Unix VFS prelude is compile-option dense. Platform macro drift can change locking style, pread/pwrite selection, WASI behavior, permissions, and syscall availability.

## Test Signals

Useful validation signals for this chunk include:

- SQLite OOM and malloc tests that exercise `sqlite3FaultSim()`, malloc alarms, hard memory limits, lookaside allocation and release, `db->mallocFailed` stickiness, and `sqlite3ApiExit()` conversion to `SQLITE_NOMEM`.
- Formatter tests covering `%q`, `%Q`, `%w`, `%z`, `%!s`, `%!c`, `%r`, large width/precision limits, NaN/Infinity handling, UTF-8 width accounting, `sqlite3_mprintf()`, `sqlite3_snprintf()`, and `sqlite3_str_*` growth/error states.
- Parser diagnostics that verify error messages, byte offsets, and debug tree-view output under `SQLITE_DEBUG` and `TREETRACE_ENABLED`.
- PRNG tests using `sqlite3_test_control()` save/restore/reset controls and checks that `sqlite3_randomness()` initializes from the active VFS and is mutex-protected.
- Thread tests with `SQLITE_MAX_WORKER_THREADS>0`, pthread/Win32 paths, and `sqlite3FaultSim(200)` deterministic fallback.
- UTF tests including BOM removal, endian swap, UTF-8 to UTF-16 and back, malformed surrogate handling, `sqlite3Utf8ReadLimited()`, and `sqlite3UtfSelfTest()`.
- Numeric and binary-format tests for integer overflow, 32-bit extraction, decimal/hex parsing, floating-point round trips, varint encode/decode length, big-endian 4-byte helpers, and blob literal conversion.
- Hash and VList tests that cover insertion, replacement, deletion, rehashing after bucket pressure, case-insensitive lookup, and OOM during benign hash resize.
- `EXPLAIN` or debug builds that confirm `sqlite3OpcodeName()` returns names matching generated opcode numbers.
- `kvvfs` tests that open `local` and `session` databases, write pages, sync and reload size state, create/read/truncate rollback journals, delete journal keys, simulate short reads, and exercise optional WASM method replacement.
- Unix VFS tests later in the file should observe that syscall overrides can replace entries in `aSyscall[]` and that feature macros select the intended locking and I/O paths for target platforms.

## Cross-Chunk Notes

This chunk begins in the middle of `malloc.c`; preceding lines define `mem0`, memory-subsystem initialization, and the start of `mallocWithAlarm()`. Later chunks continue `os_unix.c` from the syscall table into concrete Unix file, locking, shared-memory, and VFS method implementations. The final merged research for `sqlite3.c` should connect this infrastructure to the pager, btree, VDBE, parser, and platform VFS code covered in adjacent chunks.

# Research: subset-b-008981

Grouped research for WiredTiger include headers. Each section preserves the source path in the title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/intpack_inline.h -->
# sources/storage-engines/wiredtiger/src/include/intpack_inline.h

## Purpose
Defines WiredTiger's lexicographically ordered variable-length integer encoding for signed and unsigned 64-bit values, plus fixed 32-bit integer packing helpers. The encoding is designed so the byte representation sorts in the same order as the numeric value, which is important for packed keys and other byte-comparable serialized structures.

## Important APIs, Types, And Functions
- Marker and range macros: `NEG_MULTI_MARKER`, `NEG_2BYTE_MARKER`, `NEG_1BYTE_MARKER`, `POS_1BYTE_MARKER`, `POS_2BYTE_MARKER`, `POS_MULTI_MARKER`, `NEG_1BYTE_MIN`, `NEG_2BYTE_MIN`, `POS_1BYTE_MAX`, and `POS_2BYTE_MAX` define the first-byte classes and compact value ranges.
- `GET_BITS` extracts first-byte payload bits; `WT_SIZE_CHECK_PACK` and `WT_SIZE_CHECK_UNPACK` enforce bounded pack/unpack access with different error semantics (`ENOMEM` for insufficient write space, `EINVAL` for malformed/truncated read input).
- `WT_LEADING_ZEROS` has compiler-specific implementations for GCC, MSVC, and a portable fallback.
- `__wt_vpack_uint`, `__wt_vpack_int`, `__wt_vunpack_uint`, and `__wt_vunpack_int` are the primary variable-length integer serialization APIs.
- `__wt_vsize_uint` and `__wt_vsize_int` compute encoded lengths without writing.
- `__wt_pack_fixed_uint32` and `__wt_unpack_fixed_uint32` provide endian-aware fixed-width 32-bit packing.

## Control Flow
Packing first checks for the compact one-byte or two-byte ranges. Values outside those ranges are normalized by subtracting the compact range boundary and delegated to `__wt_vpack_posint` or `__wt_vpack_negint`, which encode a length nibble in the first byte followed by big-endian payload bytes. Signed packing sends non-negative values through the unsigned path and uses separate negative markers for negative values.

Unpacking reads the high nibble of the first byte, dispatches to the matching compact or multi-byte decoder, validates required length before reading, and advances the caller-owned pointer only after the consumed bytes are known. The special unsigned value `POS_2BYTE_MAX + 1` is deliberately encoded as two bytes so encoded size does not shrink at the multi-byte boundary.

## State And Persistence Behavior
The functions are stateless except for advancing caller-supplied buffer pointers. Their output is a persistent on-disk/on-wire encoding contract used by higher-level packing and key serialization. Endianness is normalized for fixed-width 32-bit values under `WORDS_BIGENDIAN`; variable-length integer payloads are written most-significant byte first to preserve lexical ordering.

## Dependencies And Integration Points
This header depends on global WiredTiger error macros (`WT_RET`, `WT_RET_TEST`), constants such as `WT_INTPACK64_MAXSIZE`, byte-swap helpers, and compiler/platform headers for leading-zero intrinsics. It is consumed by `packing_inline.h` for struct format packing and by any code that needs ordered integer byte encodings.

## Risks
The marker ranges and boundary constants are part of persistent data format; changing them would break compatibility or ordering. Length checks treat `maxlen == 0` as unchecked, so callers that parse untrusted buffers must pass real limits. Casting `int64_t *` to `uint64_t *` in signed unpack relies on two's-complement representation and alignment expectations. Compiler-specific leading-zero behavior and GCC warning suppressions need coverage across supported toolchains.

## Test Signals
Useful tests include round-trip and expected-byte tests for all range boundaries, lexicographic ordering comparisons across negative/positive values, malformed/truncated buffer handling, `maxlen` enforcement, big-endian fixed-uint32 behavior, and MSVC/GCC builds for intrinsic paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/intpack_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/json.h -->
# sources/storage-engines/wiredtiger/src/include/json.h

## Purpose
Declares `WT_JSON`, a small state holder used when converting between JSON-formatted strings and WiredTiger configuration/format items for cursor keys and values.

## Important APIs, Types, And Functions
- `struct __wt_json` stores `key_buf` and `value_buf`, which own or reference JSON-formatted string buffers.
- `key_names` and `value_names` are `WT_CONFIG_ITEM` slices naming the key and value columns used during conversion.

## Control Flow
This header has no executable logic. It supplies the structure that JSON conversion routines populate and pass around while formatting or parsing cursor key/value material.

## State And Persistence Behavior
The structure is transient per conversion or cursor operation. The buffers may contain serialized user-visible JSON but the struct itself is not a persistent file format. `WT_CONFIG_ITEM` fields are length-delimited slices, so callers must respect length and ownership rather than assuming null-terminated strings.

## Dependencies And Integration Points
Depends on `WT_CONFIG_ITEM` from the config subsystem and integrates with packing/format code that supports JSON strings (`packing_inline.h` internally references JSON string length/copy helpers).

## Risks
The header does not encode ownership rules for `key_buf` and `value_buf`; freeing and reuse must be handled consistently by the conversion implementation. The name fields are slices and can be invalid if the underlying config string expires.

## Test Signals
JSON cursor format tests should cover named and generated key/value columns, non-null-terminated `WT_CONFIG_ITEM` slices, escaped strings, buffer cleanup, and round trips between packed values and JSON output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/json.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/load_control.h -->
# sources/storage-engines/wiredtiger/src/include/load_control.h

## Purpose
Defines connection-level load-control state used to reject or throttle reads/writes when cache pressure reaches configured thresholds.

## Important APIs, Types, And Functions
- `struct __wt_connection_load_control` stores `control_threshold`, atomic/shared `read_load` and `write_load`, maximum byte-equivalent load bounds, and a `flags` field.
- `WT_CONN_LOAD_CONTROL` enables the load-control checks.

## Control Flow
This header only declares state. Runtime checks are implemented in `load_control_inline.h`, where readers compare current load counters against `control_threshold` if the enable flag is set.

## State And Persistence Behavior
Load-control fields are connection memory state, not persistent metadata. `read_load`, `write_load`, and max values are marked `wt_shared`, indicating concurrent access from multiple threads and requiring atomic or carefully synchronized reads/writes.

## Dependencies And Integration Points
The struct is embedded in `WT_CONNECTION_IMPL` and accessed via `S2C(session)->load_control`. It depends on WiredTiger's flag macros and atomic/shared-field conventions.

## Risks
Threshold tuning affects user-visible availability and latency. Non-atomic reads of shared fields would be unsafe; callers should use the inline helpers or atomic accessors. A disabled flag must reliably bypass rejection even if stale load counters are high.

## Test Signals
Load-control tests should exercise disabled/enabled states, read and write thresholds, boundary equality at `control_threshold`, concurrent updates to load counters, and integration with cache eviction/load measurements.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/load_control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/load_control_inline.h -->
# sources/storage-engines/wiredtiger/src/include/load_control_inline.h

## Purpose
Provides inline predicates for deciding whether the connection is read- or write-overloaded according to `WT_CONNECTION_LOAD_CONTROL`.

## Important APIs, Types, And Functions
- `__wt_conn_load_control_read_overload(WT_SESSION_IMPL *)` returns true when load control is enabled and `read_load >= control_threshold`.
- `__wt_conn_load_control_write_overload(WT_SESSION_IMPL *)` does the same for `write_load`.

## Control Flow
Both functions fetch the connection load-control object through `S2C(session)`, test `WT_CONN_LOAD_CONTROL` with `F_ISSET`, atomically load the relevant `uint8_t` load counter with relaxed ordering, compare it against the threshold, and otherwise return false.

## State And Persistence Behavior
The functions read volatile connection runtime state only. They do not mutate state or persist anything. Relaxed atomics mean decisions may be approximate, which is acceptable for throttling/load shedding but not for exact accounting.

## Dependencies And Integration Points
Depends on `load_control.h`, `session.h` (`S2C`), flag macros from `misc.h`, and atomic functions supplied by the platform abstraction. Callers can use these predicates in front-door operation admission paths.

## Risks
Using relaxed loads can produce stale decisions under concurrency; the design assumes load control is heuristic. A low threshold can reject work aggressively, while a disabled flag must be respected even with high counters.

## Test Signals
Unit tests can directly set `control_threshold`, `read_load`, `write_load`, and flags on a synthetic connection. Integration tests should validate operation behavior under cache pressure and ensure disabled load control never reports overload.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/load_control_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/meta.h -->
# sources/storage-engines/wiredtiger/src/include/meta.h

## Purpose
Centralizes metadata filenames, metadata/system URI constants, metadata classification helpers, turtle-file locking, incremental backup state, and disaggregated metadata payload definitions.

## Important APIs, Types, And Functions
- File and URI constants include `WT_WIREDTIGER`, `WT_SINGLETHREAD`, `WT_BASECONFIG`, `WT_USERCONFIG`, `WT_METADATA_TURTLE`, `WT_METAFILE_URI`, history-store URIs, shared/disaggregated metadata URIs, and system timestamp URIs.
- URI classification macros include `WT_BTREE_PREFIX`, `WT_URI_IS_STABLE`, `WT_URI_IS_STABLE_CHECKPOINT`, `WT_URI_IS_INGEST`, `WT_IS_URI_HS`, `WT_HS_ID_TO_URI`, and `WT_IS_URI_METADATA`.
- Handle classification macros include `WT_IS_METADATA`, `WT_IS_DISAGG_META`, and `WT_IS_HS`.
- `WT_MIN_STARTUP_VERSION` defines the minimum compatible startup version.
- `WT_WITH_TURTLE_LOCK` serializes turtle-file operations.
- `struct __wt_blkincr` tracks block-incremental backup id, granularity, and flags.
- `WT_DISAGG_METADATA` holds checkpoint/key-provider strings, timestamps, schema epoch, file-id watermark, and metadata compatibility versions.

## Control Flow
Most definitions are constants or tests. `WT_HS_ID_TO_URI` switches known history-store IDs to URIs and asserts on unknown IDs. `WT_WITH_TURTLE_LOCK` asserts the session is not already marked as holding the turtle lock, then delegates to generic lock acquisition/release around the caller-provided operation.

## State And Persistence Behavior
The constants define persistent filenames, metadata keys, and stable URI identities used in database directories and metadata tables. `WT_DISAGG_METADATA` contains length-delimited metadata strings that are explicitly not null-terminated. `WT_BLKINCR` is connection runtime state for backup bookkeeping but refers to persistent checkpoint/file state.

## Dependencies And Integration Points
Depends on string macros from `misc.h`, data-handle flags, session lock flags, version types, timestamps, and schema locking macros. Integrated broadly with metadata open/upgrade, history store, backup, turtle file management, disaggregated storage, and system timestamp metadata.

## Risks
Changing constants can break existing database directories or metadata compatibility. Substring tests such as `WT_URI_IS_STABLE` are intentionally broad and must not be reused where strict suffix matching is required. `WT_DISAGG_METADATA` strings require length-aware handling. Turtle lock usage must match the global schema/metadata lock order to avoid deadlocks.

## Test Signals
Signals include upgrade/startup compatibility tests, metadata URI classification tests, history-store ID mapping assertions, turtle lock ordering tests, backup/incremental backup metadata tests, and disaggregated metadata parse/serialize tests with non-null-terminated strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/meta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/misc.h -->
# sources/storage-engines/wiredtiger/src/include/misc.h

## Purpose
Provides broad internal utility macros and small inline helpers used throughout WiredTiger: inlining controls, unused/result suppression, numeric constants, pointer/size helpers, allocation wrappers, flag manipulation, sorting/searching, string matching, item ownership helpers, diagnostic wrappers, queue-safe removal, variadic buffer formatting, atomic decrement, and fuzzy statistic min/max updates.

## Important APIs, Types, And Functions
- `WT_INLINE` switches to `noinline` under code coverage builds.
- `WT_UNUSED`, `WT_NOT_READ`, and `WT_IGNORE_RET` suppress warnings intentionally.
- Size/time constants, `WT_ALIGN`, `WT_MIN`, `WT_MAX`, `WT_CLAMP`, `WT_ELEMENTS`, pointer-difference macros, and `WT_BLOCK_FITS` are general primitives.
- Allocation wrappers include `__wt_calloc_def`, `__wt_calloc_one`, `__wt_realloc_def`, `__wt_free`, `__wt_overwrite_and_free`, and `__wt_overwrite_and_free_len`.
- Flag macros `FLD_*`, `F_*`, and `LF_*` implement field, struct, and local flag manipulation, using relaxed atomics in TSan builds.
- `FLD_AREALLSET`, `WT_INSERTION_SORT`, `__wt_qsort`, and `WT_BINARY_SEARCH` provide small algorithms.
- String helpers include `WT_PREFIX_MATCH`, `WT_SUFFIX_MATCH`, `WT_PREFIX_SKIP`, `WT_STREQ`, `WT_STRING_LIT_MATCH`, `WT_STRING_MATCH`, and `__wt_string_slice_cmp`.
- `WT_DECL_ITEM`, `WT_DECL_RET`, `WT_DATA_IN_ITEM`, `WT_ITEM_SET`, and `WT_ITEM_MOVE` standardize common local state and item ownership.
- Diagnostic wrappers add callsite information to hazard, scratch, and page-in/swap functions.
- `WT_VA_ARGS_BUF_FORMAT` repeatedly formats into an extendable `WT_ITEM`.
- `__wt_atomic_decrement_if_positive` and `WT_ATOMIC_STATS_MFUNC` generate simple atomic statistic helpers.

## Control Flow
Most utilities are macro substitutions. Allocation wrappers compute element sizes and growth targets, then call core allocation functions. `__wt_free` clears the caller's pointer by passing its address to `__wt_free_int`. Flag macros mutate or test bitfields in place, with a TSan-specific atomic implementation. Formatting loops call `va_start`/`va_end` repeatedly, retrying after buffer extension until formatted output fits.

## State And Persistence Behavior
This header mostly affects in-memory state. Some helpers protect persistent-data correctness indirectly by zero-padding, formatting error messages, validating block bounds, and optionally overwriting freed memory in diagnostic builds. `WT_ITEM_MOVE` transfers ownership and clears the source to avoid double frees.

## Dependencies And Integration Points
Depends on WiredTiger allocation, buffer, atomic, config, hazard/page, stats, and diagnostic infrastructure. Because it is included nearly everywhere, it forms a low-level contract for flag fields, memory ownership, and string matching across the codebase.

## Risks
Macros can evaluate arguments multiple times unless written carefully; callers must avoid side effects where the macro contract does not guarantee single evaluation. Non-TSan flag macros are not atomic and require external synchronization unless the field is thread-local or otherwise safe. `__wt_realloc_def` depends on connection debug flags. Variadic formatting macros rely on `fmt` being available for repeated `va_start`. Size narrowing through `WT_STORE_SIZE` assumes callers already know the value fits in 32 bits.

## Test Signals
Broad signals include unit tests for string matching and slice comparison, memory wrapper tests with diagnostic overwrite enabled, TSan builds for flag races, formatting tests that force buffer extension, insertion/binary sort tests, allocation growth behavior under `WT_CONN_DEBUG_REALLOC_EXACT`, and static analysis for macro side effects.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/misc_inline.h -->
# sources/storage-engines/wiredtiger/src/include/misc_inline.h

## Purpose
Defines small inline runtime helpers for condition waits, hex encoding, safe arithmetic, string duplication/length/concatenation, snprintf wrappers, spin backoff, timing-stress/failpoint delays, and checksum compatibility matching.

## Important APIs, Types, And Functions
- `__wt_cond_wait` wraps `__wt_cond_wait_signal` when the caller does not need the signalled result.
- `__wt_hex`, `__wt_safe_sub`, `__wt_strdup`, `__wt_strnlen`, and `__wt_strcat` provide simple utility behavior with WiredTiger error conventions.
- `__wt_snprintf`, `__wt_vsnprintf`, `__wt_snprintf_len_set`, `__wt_vsnprintf_len_set`, and `__wt_snprintf_len_incr` wrap lower-level length-tracking formatting.
- `__wt_spin_backoff` escalates from counting, to yielding, to bounded sleeping.
- `__wt_timing_stress`, `__wt_timing_stress_sleep_random`, and `__wt_failpoint` implement configured stress delays and probabilistic failpoints.
- `__wt_checksum_match` compares checksums, with an alternate hardware checksum compatibility path on AMD64 when enabled.

## Control Flow
String formatting functions initialize or update a length variable, call the shared `__wt_vsnprintf_len_incr`, and convert truncation into `ERANGE`. Spin backoff allows a small number of tight iterations, then yields up to a larger threshold, then sleeps with a microsecond delay capped at 1000. Timing stress first checks connection flags, optionally emits an Antithesis marker, then sleeps for a configured or random duration biased toward short waits. Failpoints check stress flags and compare a random draw against an X-in-10000 probability.

## State And Persistence Behavior
Most helpers are stateless. Timing/failpoint functions read connection stress flags and session RNG state, and can affect scheduling but not persistent state. `__wt_strdup` allocates session-owned memory. Checksum matching influences whether previously written data is accepted, including compatibility for old Windows checksum behavior.

## Dependencies And Integration Points
Uses condition-variable, allocation, string, formatting, sleep/yield, random, eviction, checksum, verbose, and connection flag infrastructure. It integrates with diagnostic/stress testing, failpoint injection, error handling, and file/block checksum validation.

## Risks
Stress and failpoint behavior intentionally perturbs timing; misuse in production paths could mask or create latency. `__wt_strcat` assumes `dest` is already null-terminated within `size`. The alternate checksum path is platform-conditional and must remain compatible with historical data. `__wt_spin_backoff` must balance CPU usage and latency.

## Test Signals
Tests should cover formatting truncation and length accounting, safe subtraction underflow, bounded string concatenation, timing stress flag behavior, failpoint probability boundaries, spin-backoff progression, and checksum compatibility on supported hardware/compiler combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/misc_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/modify_inline.h -->
# sources/storage-engines/wiredtiger/src/include/modify_inline.h

## Purpose
Defines iteration and sizing helpers for WiredTiger modify records: compact delta updates that replace byte ranges within an existing value.

## Important APIs, Types, And Functions
- `WT_MODIFY_FOREACH_BEGIN`, `WT_MODIFY_FOREACH_REVERSE`, and `WT_MODIFY_FOREACH_END` decode packed modify entries from a byte buffer.
- `__wt_modify_max_memsize` computes the maximum temporary buffer size needed to apply a packed modify to a base value.
- `__wt_modify_max_memsize_format` adds string-terminator space for `S` value formats.
- `__wt_modify_max_memsize_unpacked` computes the size for an unpacked `WT_MODIFY` array.
- `__wt_modifies_max_memsize` computes the size needed to apply a vector of modify updates in update-chain order.

## Control Flow
Packed modify buffers start with entry metadata laid out as triples of `size_t` values followed by concatenated data bytes. Forward iteration decodes each triple, points `mod.data.data` into the data area, and skips entries already applied. Reverse iteration walks metadata and data backwards. Sizing applies each modify's `offset` and `data.size` to the current maximum with `WT_MAX`, then adds a string terminator for `S` formats.

## State And Persistence Behavior
The helpers are stateless but interpret packed modify update payloads that may live in update chains or durable history. They do not apply modifications; they estimate safe memory bounds for later application.

## Dependencies And Integration Points
Depends on `WT_MODIFY`, `WT_UPDATE`, `WT_UPDATE_VECTOR`, `WT_ITEM`, and `WT_MAX`. Integrated with update application, history store/value reconstruction, and cursor reads that materialize modify chains.

## Risks
The packed layout is architecture-sensitive because it stores `size_t` triples; it is suitable for in-memory update payload interpretation, not portable cross-platform disk format unless higher layers guarantee compatibility. Incorrect `nentries`, `napplied`, or `datasz` can walk past the buffer. Size calculations must guard against overflow in callers allocating buffers.

## Test Signals
Tests should cover forward/reverse iteration, `napplied` skipping, zero-length data, large offsets, `S` value terminator sizing, chained modifies through `WT_UPDATE_VECTOR`, and malformed packed buffers under diagnostic or fuzz testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/modify_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/msvc.h -->
# sources/storage-engines/wiredtiger/src/include/msvc.h

## Purpose
Provides the MSVC/x64 compiler and atomic abstraction layer for WiredTiger, including barriers, pause instructions, packing attributes, printf-format attribute no-ops, atomic load/store/add/sub/CAS helpers, and Windows-compatible type behavior.

## Important APIs, Types, And Functions
- Requires `_M_AMD64`; defines `inline` for C and maps `__PRETTY_FUNCTION__` to `__FUNCSIG__`.
- Defines MSVC format strings `WT_PTRDIFFT_FMT` and `WT_SIZET_FMT`.
- `WT_PACKED_STRUCT_BEGIN` and `WT_PACKED_STRUCT_END` implement packed structure declarations with `__pragma(pack)`.
- `WT_COMPILER_BARRIER`, `WT_FULL_BARRIER`, `WT_PAUSE`, `WT_ACQUIRE_BARRIER`, and `WT_RELEASE_BARRIER` wrap MSVC intrinsics.
- `WT_ATOMIC_FUNC_STORE_LOAD`, `WT_ATOMIC_CAS_FUNC`, and `WT_ATOMIC_FUNC` generate typed atomic APIs for integer, bool, size, and uintmax types.
- Pointer and generic relaxed load/store macros, enum atomics, and double relaxed accessors fill out platform compatibility.

## Control Flow
Atomic generator macros emit families of static inline functions. Read/write relaxed helpers are plain loads/stores on x86/x64 for historical/performance reasons. Add/sub and CAS use `_Interlocked*` intrinsics. Acquire/release wrappers issue compiler barriers because x86 TSO provides the needed hardware ordering for these cases.

## State And Persistence Behavior
This header does not own persistent state, but it defines how shared in-memory state is synchronized on Windows builds. Its behavior affects correctness for locks, flags, reference states, statistics, and vtable wrappers throughout WiredTiger.

## Dependencies And Integration Points
Depends on `<intrin.h>` and Windows/MSVC intrinsic signatures. It must match the GCC/Clang atomic API names used by shared WiredTiger code. Integrated with mutexes, sessions, file handles, ref state, load control, statistics, and all `wt_shared` fields.

## Risks
Relaxed helpers are not true C11 atomics and rely on x86 memory model and WiredTiger's historical assumptions. Casts to interlocked intrinsic pointer types must match size/alignment. The header only supports x64 MSVC; accidental ARM or 32-bit builds fail intentionally. Differences from GCC atomics can hide or expose races differently across platforms.

## Test Signals
Windows CI should compile every generated atomic family, exercise locks and ref-state CAS, run TSan-equivalent/static race checks where possible, validate packed structure layout, and stress concurrent flag/stat updates under MSVC.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/msvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/mutex.h -->
# sources/storage-engines/wiredtiger/src/include/mutex.h

## Purpose
Declares WiredTiger synchronization primitives: condition variables, semaphores, read/write locks, and spin locks, along with tracked initialization macros for statistics.

## Important APIs, Types, And Functions
- `struct __wt_condvar` stores a mutex, condition variable, waiter count, and adaptive wait-duration state.
- `struct __wt_semaphore` wraps platform semaphores with a debug name.
- `struct __wt_rwlock` stores ticket-style read/write state in a shared 64-bit union, stat offsets, condition variables for readers/writers, and optional TSan synchronization.
- `WT_RWLOCK_INIT_TRACKED` and `WT_RWLOCK_INIT_SESSION_TRACKED` initialize locks and populate connection/session statistic offsets.
- `struct __wt_spinlock` abstracts GCC bool spinlocks, pthread mutex/adaptive mutexes, or Windows critical sections, plus ownership session id, stat offsets, and initialization state.

## Control Flow
This header is mostly structure layout. Tracked init macros call lower-level initialization, then compute stat-array offsets from generated stat fields so inline acquisition code can update counters without knowing concrete stat structures.

## State And Persistence Behavior
All state is in-memory synchronization state. `waiters`, rwlock ticket fields, spinlock session id, and initialization flags are shared across threads. No fields are persistent, but correctness protects persistent metadata and data structures elsewhere.

## Dependencies And Integration Points
Depends on platform typedefs (`wt_mutex_t`, `wt_cond_t`, `wt_sem_t`), stats offset macros, `WT_SESSION_IMPL`, connection stats, and spinlock type configuration. Used by connection locks, schema locks, table/handle locks, cache/session locks, RTS queues, and many internal data structures.

## Risks
Structure layout must match inline implementations in `mutex_inline.h` and platform OS headers. Stat offsets use `int16_t`; generated stat layouts must remain within range. Spinlock type selection changes performance and semantics. Misusing spinlocks for long critical sections can harm latency.

## Test Signals
Concurrency tests should cover rwlock read/write exclusion, condition variable signaling and timeout behavior, semaphore wakeups, stat tracking, initialization/destruction idempotence, and all configured `SPINLOCK_TYPE` variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/mutex_inline.h -->
# sources/storage-engines/wiredtiger/src/include/mutex_inline.h

## Purpose
Implements inline spinlock lifecycle, acquisition, ownership checks, unlock behavior, and tracked statistic updates across GCC atomics, pthread mutexes, adaptive pthread mutexes, and MSVC critical sections.

## Important APIs, Types, And Functions
- `WT_SPIN_SESSION_ID_SAFE` maps a possibly null session to a valid tracking id.
- `__spin_init_internal` initializes common spinlock metadata.
- `__wt_spin_init`, `__wt_spin_destroy`, `__wt_spin_trylock`, `__wt_spin_lock`, and `__wt_spin_unlock` have platform-specific implementations.
- `__wt_spin_locked`, `__wt_spin_owned`, and `__wt_spin_unlock_if_owned` inspect or conditionally release ownership.
- `WT_ASSERT_SPINLOCK_OWNED` validates ownership in diagnostic assertions.
- `WT_SPIN_INIT_TRACKED` and `WT_SPIN_INIT_SESSION_TRACKED` attach stat offsets.
- `__wt_spin_lock_track` and `__wt_spin_trylock_track` update acquisition counts and wait-time stats.

## Control Flow
GCC spinlocks use `__atomic_test_and_set`, pause loops up to `WT_SPIN_COUNT`, then yield. Pthread variants initialize and use mutex APIs, optionally adaptive, panicking on unexpected lock/unlock errors. MSVC uses critical sections. All successful acquisitions record `session_id`; unlock resets it before releasing. Tracked locks measure elapsed clock time, increment connection and optional session stat counters, and separate application versus internal sessions.

## State And Persistence Behavior
The functions mutate in-memory lock state and lock ownership metadata only. They affect persistent safety by guarding shared data structures. Stat counters are runtime diagnostic/performance state.

## Dependencies And Integration Points
Depends on platform locking APIs, atomic helpers, session IDs, stats macros, `WT_SESSION_INTERNAL`, clocks, panic/error handling, and `mutex.h` layout. Used by schema/metadata locks, page locks, scratch locks, RTS queues, and any code requiring short critical sections.

## Risks
Ownership tracking is diagnostic and must stay synchronized with actual lock state. Pthread lock/unlock failures panic, so incorrect lifecycle handling is severe. The GCC spin path can consume CPU under contention; callers should keep critical sections small. Null-session lock calls are supported but produce `WT_SESSION_ID_NULL` ownership, which limits ownership assertions.

## Test Signals
Signals include platform CI for every spinlock backend, lock contention stress tests, ownership assertion tests, stat counter validation, null-session acquisition paths, destroy-after-init behavior, and deadlock/race testing under TSan.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/mutex_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/optrack.h -->
# sources/storage-engines/wiredtiger/src/include/optrack.h

## Purpose
Defines lightweight per-session operation tracking records and macros that log function entry/exit timestamps to a session buffer for later decoding.

## Important APIs, Types, And Functions
- `WT_OPTRACK_MAXRECS`, `WT_OPTRACK_BUFSIZE`, and `WT_OPTRACK_VERSION` define buffer and file-format sizing/version.
- `struct __wt_optrack_header` records version, internal-session flag, timestamp ratio, padding, and epoch seconds.
- `struct __wt_optrack_record` is a 16-byte event containing timestamp, function id, operation type, and explicit padding.
- `WT_TRACK_OP`, `WT_TRACK_OP_DECL`, `WT_TRACK_OP_INIT`, and `WT_TRACK_OP_END` instrument functions.

## Control Flow
Instrumented functions declare a static function id. On entry, `WT_TRACK_OP_INIT` checks the connection optrack flag and excludes the default session. It lazily records the function name/id mapping, then appends a start record. `WT_TRACK_OP_END` appends a stop record. `WT_TRACK_OP` writes into the circular buffer and flushes when the pointer reaches `WT_OPTRACK_MAXRECS`.

## State And Persistence Behavior
Per-session buffers and file handles are runtime state, but flushed optrack logs are persistent diagnostic artifacts with a versioned binary layout. Function ids are process-local mappings recorded separately for decoding.

## Dependencies And Integration Points
Depends on session optrack fields, connection flags, clocks, function-id recording, and buffer flush routines. It integrates with performance diagnostics and requires instrumentation at function boundaries.

## Risks
The macros intentionally avoid synchronization on the session buffer and can lose records if a session is used by multiple threads. Static function ids are per-process and need mapping records to decode. The default session is excluded because it can be multi-threaded and used during error paths.

## Test Signals
Tests should enable operation tracking, instrument simple functions, verify start/stop records and flush boundaries, decode function mappings, confirm default-session exclusion, and stress concurrent misuse to ensure failures are bounded to lost diagnostics rather than memory corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/optrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os.h -->
# sources/storage-engines/wiredtiger/src/include/os.h

## Purpose
Defines generic OS abstraction helpers for syscall error normalization/retry, time-difference conversion, file-handle queue management, platform-specific file handle layouts, in-memory file handles, and stream abstraction state.

## Important APIs, Types, And Functions
- `WT_SYSCALL` normalizes syscall return conventions into WiredTiger error codes.
- `WT_SYSCALL_RETRY` retries transient filesystem/resource errors up to `WT_RETRY_MAX`.
- `WT_TIMEDIFF_*` and `WT_CLOCKDIFF_*` convert `timespec` or WiredTiger clock deltas.
- `WT_FILE_HANDLE_INSERT` and `WT_FILE_HANDLE_REMOVE` maintain both global and hash file-handle queues.
- `struct __wt_fh` is the internal wrapper for a `WT_FILE_HANDLE`, with name, hash, sync/write accounting, queues, refcount, and file type.
- `struct __wt_file_handle_win`, `struct __wt_file_handle_posix`, and `struct __wt_file_handle_inmem` hold platform/in-memory handle specifics.
- `struct __wt_fstream` wraps stream state and function pointers for close, flush, getline, and printf.

## Control Flow
Syscall wrappers inspect return values, convert `-1` through `errno`, and retry selected transient errors with a short sleep. Queue macros insert/remove a file handle from two TAILQ lists in a single operation. Stream functions are implemented in `os_fstream_inline.h` by dispatching through `WT_FSTREAM` function pointers.

## State And Persistence Behavior
File handle structures represent open persistent files or in-memory files. `written` and `last_sync` track runtime durability state. POSIX mmap fields track memory-mapped file state and resizing/use counts. Stream state includes offsets, size, buffer, mode flags, and underlying `WT_FH`.

## Dependencies And Integration Points
Depends on queue macros, filesystem extension interfaces (`WT_FILE_HANDLE`, `WT_FILE_SYSTEM`), platform OS typedefs, error handling, and timing constants. Used by all filesystem, block manager, metadata, log, backup, and stream code.

## Risks
Queue insert/remove must keep both lists consistent. Retry policy can hide transient errors briefly but must not retry non-transient failures. POSIX mmap resizing and use counts are concurrency-sensitive. File handle name duplication requires consistent ownership. Stream flags and function pointers must match how a stream was opened.

## Test Signals
Signals include syscall retry tests with injected `EINTR`/`EAGAIN`/`ENOSPC`, file-handle queue consistency checks, POSIX mmap resize stress, Windows/POSIX handle lifecycle tests, in-memory filesystem tests, stream mode tests, and durability accounting around `written`/`last_sync`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_darwin.h -->
# sources/storage-engines/wiredtiger/src/include/os_darwin.h

## Purpose
Provides Darwin-specific semaphore typedefs for the WiredTiger OS abstraction.

## Important APIs, Types, And Functions
- Includes `<dispatch/dispatch.h>`.
- Defines `wt_sem_t` as `dispatch_semaphore_t`.

## Control Flow
No executable logic is defined here. Platform-specific semaphore implementation code uses `wt_sem_t` through common names.

## State And Persistence Behavior
Semaphore state is in-memory kernel/runtime synchronization state only.

## Dependencies And Integration Points
Integrated by platform selection headers and semaphore code in the OS layer. Must be consistent with `mutex.h`'s `WT_SEMAPHORE` wrapper.

## Risks
Darwin semaphore lifecycle must use dispatch semaphore APIs, not POSIX `sem_t` calls. Type mismatches would surface at compile time or during semaphore initialization/destruction.

## Test Signals
Darwin builds should compile semaphore code and run thread signaling tests covering wait, post, timeout, and destruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_darwin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_fhandle_inline.h -->
# sources/storage-engines/wiredtiger/src/include/os_fhandle_inline.h

## Purpose
Defines inline wrappers around `WT_FILE_HANDLE` operations, adding WiredTiger assertions, verbose tracing, statistics, latency histograms, corruption flags, panic checks, and write accounting.

## Important APIs, Types, And Functions
- `__wt_fsync` dispatches to blocking or nonblocking sync operations and updates fsync stats.
- `__wt_fextend` extends files through `fh_extend_nolock` or `fh_extend`.
- `__wt_file_lock` wraps file locking.
- `__wt_read` dispatches `fh_read`, tracks active readers/read I/O, records latency, and flags data corruption on read failure.
- `__wt_filesize` wraps `fh_size`.
- `__wt_ftruncate` wraps `fh_truncate` with readonly and diagnostic backup assertions.
- `__wt_write` checks readonly/panic state, dispatches `fh_write`, records latency/stats, and increments `fh->written`.

## Control Flow
Each wrapper logs the operation, fetches the vtable from `fh->handle`, and calls the configured method if available. Unsupported extend/truncate operations return `ENOTSUP` through WiredTiger error handling. Read/write paths bracket vtable calls with active-thread counters and clock measurements. Write performs a panic check immediately before I/O to avoid continuing writes after a fatal state.

## State And Persistence Behavior
These functions perform durable file operations through the filesystem extension layer. They mutate runtime counters and `fh->written`; sync/truncate/extend/write change persistent file state. Diagnostic backup checks prevent shrinking files during backup.

## Dependencies And Integration Points
Depends on `WT_FH`, `WT_FILE_HANDLE` vtables, connection readonly/in-memory flags, stats/histograms, verbose logging, panic checks, backup state, atomic counters, and filesystem extension implementations. Integrated with block manager, logging, metadata, checkpoint, and backup code.

## Risks
Vtable methods may be null; callers must handle `ENOTSUP`. Read failure sets a connection data-corruption flag, which can affect startup/error handling. `__wt_write` allows readonly writes only for the single-thread lock file path. Diagnostic backup assertions depend on accurate file size methods.

## Test Signals
Filesystem tests should inject vtable success/failure/null methods, verify stat and histogram updates, check readonly enforcement, validate panic-before-write behavior, assert data-corruption flag on read error, and cover backup shrink assertions under diagnostic builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_fhandle_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_fs_inline.h -->
# sources/storage-engines/wiredtiger/src/include/os_fs_inline.h

## Purpose
Provides inline wrappers around `WT_FILE_SYSTEM` directory and file-name operations, adding WiredTiger path resolution, readonly assertions, verbose tracing, diagnostic open-handle checks, durable flags, and cleanup of allocated paths.

## Important APIs, Types, And Functions
- `__wt_fs_file_system` returns the active filesystem, honoring session bucket storage.
- `__wt_fs_directory_list` and `__wt_fs_directory_list_single` resolve directory paths and call filesystem list methods.
- `__wt_fs_directory_list_free` releases list memory through the filesystem.
- `__wt_fs_exist` resolves and tests file existence.
- `__wt_fs_remove` removes a file with optional durability and diagnostic open-handle validation.
- `__wt_fs_rename` resolves both paths and renames durably if requested.
- `__wt_fs_size` resolves a path and returns file size.

## Control Flow
Wrappers initialize output pointers, build full paths with `__wt_filename`, call the active `WT_FILE_SYSTEM` vtable with `(WT_SESSION *)session`, and free temporary path strings. Remove and rename assert not readonly and, in diagnostic builds, reject operations on open handles.

## State And Persistence Behavior
Directory listings and existence/size checks are read-only filesystem observations. Remove and rename mutate persistent filesystem state, optionally with `WT_FS_DURABLE`. Temporary path buffers are allocated and freed per call.

## Dependencies And Integration Points
Depends on session filesystem selection (`S2FS`/bucket storage), path construction, filesystem extension vtables, diagnostic handle lookup, readonly flags, durable flags, and memory management. Used by metadata, backup, checkpoint, salvage, import, and file lifecycle code.

## Risks
Every path allocation must be freed on all error paths. Diagnostic open-handle checks are intentionally layering-violating but catch unsafe file lifecycle operations. Filesystem extensions must implement list-free pairing correctly. Bucket-storage sessions can route to alternate filesystems.

## Test Signals
Tests should cover default and bucket filesystem selection, list/list-free pairing, path allocation cleanup on errors, readonly remove/rename assertions, durable flag propagation, open-handle diagnostic failures, and filesystem extension error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_fs_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_fstream_inline.h -->
# sources/storage-engines/wiredtiger/src/include/os_fstream_inline.h

## Purpose
Defines inline stream helpers that dispatch through `WT_FSTREAM` function pointers and provide a durable flush-close-rename sequence for replacing files.

## Important APIs, Types, And Functions
- `__wt_getline` calls `fstr_getline`.
- `__wt_fclose` nulls the caller's stream pointer and calls `close`.
- `__wt_fflush` calls `fstr_flush`.
- `__wt_vfprintf` and `__wt_fprintf` dispatch formatted writes through `fstr_printf`.
- `__wt_sync_and_rename` flushes a stream, fsyncs its file handle, closes it, and renames a temporary file into place durably.

## Control Flow
Simple wrappers call the configured stream method. `__wt_fclose` is null-safe and clears ownership before closing. `__wt_sync_and_rename` accumulates errors with `WT_TRET` for flush/fsync/close, returns any accumulated error before rename, and only renames after the temporary file is durably closed.

## State And Persistence Behavior
Stream operations mutate stream offsets/buffers and underlying file contents. `__wt_sync_and_rename` is a persistence-critical sequence used for atomic-ish replacement of metadata/config-style files: write temp, flush, fsync, close, durable rename.

## Dependencies And Integration Points
Depends on `WT_FSTREAM` vtables, `__wt_fsync`, `__wt_fs_rename`, error accumulation macros, and formatted-output attributes. Integrated with metadata/turtle/config file writing and other text/binary stream users.

## Risks
Clearing `*fstrp` before close prevents double close but requires callers not to reuse the pointer after error. Rename is skipped if flush/fsync/close fails. Correct durability depends on filesystem implementation of fsync and durable rename.

## Test Signals
Tests should cover null close, method error propagation, formatted write variadics, flush/fsync/close error precedence, successful durable temp-file replacement, and filesystem extensions with custom stream implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_fstream_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_linux.h -->
# sources/storage-engines/wiredtiger/src/include/os_linux.h

## Purpose
Provides Linux-specific semaphore typedefs for the WiredTiger OS abstraction.

## Important APIs, Types, And Functions
- Includes `<semaphore.h>`.
- Defines `wt_sem_t` as `sem_t`.

## Control Flow
No executable logic is defined here. Common semaphore code uses the platform typedef.

## State And Persistence Behavior
Semaphore state is runtime synchronization state only.

## Dependencies And Integration Points
Integrated by platform selection and `WT_SEMAPHORE` in `mutex.h`. It must match Linux semaphore initialization, wait/post, and destroy implementations.

## Risks
Linux uses POSIX semaphores while Darwin uses dispatch semaphores and Windows uses handles. Cross-platform semaphore code must not assume a shared representation.

## Test Signals
Linux CI should run semaphore wait/post/timeout tests and thread-group signaling paths that use `wt_sem_t`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_windows.h -->
# sources/storage-engines/wiredtiger/src/include/os_windows.h

## Purpose
Defines Windows-specific threading, synchronization, calling-convention, POSIX-compatibility, and fsync aliases for WiredTiger.

## Important APIs, Types, And Functions
- `wt_cond_t`, `wt_mutex_t`, and `wt_sem_t` map to `CONDITION_VARIABLE`, `CRITICAL_SECTION`, and `HANDLE`.
- `wt_thread_t` stores a creation flag, unused name index, and Windows thread handle.
- `WT_THREAD_CALLBACK`, `WT_THREAD_RET`, and `WT_THREAD_RET_VALUE` match `_beginthreadex`.
- `WT_CDECL` maps to `__cdecl`.
- Defines `struct timespec` for older MSVC, POSIX-like `u_int`, `u_char`, `u_long`, and optionally `ssize_t`.
- Maps `fsync` to `_commit`.

## Control Flow
No functions are implemented here; it establishes types and macros consumed by common threading and filesystem code.

## State And Persistence Behavior
Thread, mutex, condition, and semaphore state is runtime state. Mapping `fsync` to `_commit` affects durability behavior for Windows file descriptors.

## Dependencies And Integration Points
Depends on Windows headers included before or nearby in the platform build. Used by mutex, thread, semaphore, and OS file code. It must align with `msvc.h` atomic and barrier definitions.

## Risks
Thread callback signatures must exactly match `_beginthreadex`; mismatches can corrupt stack/calling conventions. `ssize_t` typedef is guarded to avoid Python/header conflicts. The older-MSVC `timespec` definition must not conflict with newer toolchains.

## Test Signals
Windows CI should compile thread callbacks, run condition/mutex/semaphore tests, validate fsync aliasing through file sync tests, and build with supported MSVC versions around the `timespec`/`ssize_t` guards.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/os_windows.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/packing_inline.h -->
# sources/storage-engines/wiredtiger/src/include/packing_inline.h

## Purpose
Implements WiredTiger's struct packing format iterator, size calculation, pack, and unpack logic. It bridges application/key/value format strings, variable-length integer encoding, strings/items, JSON-internal formats, padding, and variadic C APIs.

## Important APIs, Types, And Functions
- `WT_PACK_VALUE` holds one parsed format value, including integer/string/item union, explicit size, size flag, and type.
- `WT_PACK` tracks format iteration state: session, current/end/original pointers, repeat count, and last repeated value.
- `WT_PACK_NAME` tracks generated or configured field names for JSON/projection-style output.
- `__pack_initn`, `__pack_init`, `__pack_name_init`, and `__pack_name_next` initialize iterators and field names.
- `__pack_next` parses the next format item, validates sizes/types, and expands repeated integral types.
- `WT_PACK_GET` extracts variadic arguments into `WT_PACK_VALUE`.
- `__pack_size`, `__pack_write`, and `__unpack_read` compute, write, and read individual values.
- `WT_UNPACK_PUT` writes unpacked values back to variadic output pointers.
- `__wt_struct_packv`, `__wt_struct_sizev`, and `__wt_struct_unpackv` are the va_list versions of the public struct APIs.
- `__wt_struct_size_adjust` adjusts packed sizes when the serialized size field must include its own encoded length.

## Control Flow
Format parsing rejects leading byte-order/alignment markers, skips an optional leading `.`, parses decimal size prefixes, handles padding/string/item/bitfield/integer types, and expands repeat counts for numeric types. Packing fetches each value from `va_list`, computes or writes it according to type, and advances a buffer pointer with size checks. Unpacking mirrors that flow, reading from the input buffer and writing pointers/scalars to caller-provided destinations. Single-character formats take a fast path.

## State And Persistence Behavior
Packing emits persistent byte representations for keys/values and metadata payloads. Integer fields use `intpack_inline.h` to preserve ordering. Strings/items may be fixed-size, null-padded, null-terminated, or length-prefixed depending on type and size prefix. JSON-internal `j/J/K` handling copies through JSON string helpers. The iterator state itself is transient.

## Dependencies And Integration Points
Depends on integer packing, JSON string helpers, config iteration, snprintf, `WT_ITEM`, WiredTiger error macros, and variadic APIs. It integrates with cursor key/value packing, schema formats, JSON conversion, metadata encoding, and record-number formats (`r/R`).

## Risks
The format language is a persistent and public API contract; type semantics must remain compatible. Variadic argument extraction must match C default promotions exactly. Unpacking variable-size `u` without an explicit size consumes remaining input, so callers must provide correct format boundaries. Direct `uint64_t` stores for `R` assume alignment/endianness semantics intended by that internal format. Size calculations need overflow awareness in callers.

## Test Signals
Tests should cover every format character, size prefixes, repeats, padding, JSON internal formats, fixed and variable strings/items, integer ordering, pack/size/unpack round trips, malformed formats, truncated buffers, `__wt_struct_size_adjust`, and API compatibility against known byte encodings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/packing_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/posix.h -->
# sources/storage-engines/wiredtiger/src/include/posix.h

## Purpose
Defines POSIX-platform compatibility types and constants for WiredTiger threading, file flags, and numeric limits.

## Important APIs, Types, And Functions
- Includes `<sys/statvfs.h>`.
- Supplies `ULLONG_MAX`, `LLONG_MAX`, and `LLONG_MIN` if the system headers did not.
- Defines `O_BINARY` as `0` on POSIX.
- Defines `wt_cond_t` as `pthread_cond_t` and `wt_mutex_t` as `pthread_mutex_t`.
- Defines `wt_thread_t` with creation flag, name index, and `pthread_t` id.
- Defines thread callback macros `WT_THREAD_CALLBACK`, `WT_THREAD_RET`, and `WT_THREAD_RET_VALUE`.
- Defines Linux `WT_THREAD_NAME_MAX_LEN` as 16.
- Defines `WT_CDECL` as empty.

## Control Flow
No executable logic is present. The macros/types allow common code to compile across POSIX and Windows.

## State And Persistence Behavior
Thread and synchronization fields are runtime state only. `O_BINARY` being zero documents that POSIX does not distinguish binary/text open modes.

## Dependencies And Integration Points
Depends on pthread and POSIX headers included by the platform build. Used by mutex/thread code, file open logic, and cross-platform function declarations.

## Risks
Thread name length is Linux-specific and must be enforced by callers using `pthread_setname_np`. Fallback numeric limits must match platform width assumptions. `WT_THREAD_CALLBACK` includes a lint suppression because the macro intentionally produces a function declarator shape.

## Test Signals
POSIX CI should compile thread callback declarations, run thread creation/join/naming tests, mutex/condition tests, and file open tests that include `O_BINARY`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/queue.h -->
# sources/storage-engines/wiredtiger/src/include/queue.h

## Purpose
Provides a WiredTiger-local, stripped-down FreeBSD `sys/queue.h` implementation for tail queues (`TAILQ`) with compatibility undefines to avoid conflicts with system or Windows headers.

## Important APIs, Types, And Functions
- Undefines existing `TAILQ_*`, trace, and queue helper macros before defining WiredTiger's versions.
- `TAILQ_HEAD`, `TAILQ_CLASS_HEAD`, `TAILQ_ENTRY`, and `TAILQ_CLASS_ENTRY` declare queue heads and links.
- Iteration macros include forward/reverse and safe variants.
- Mutation macros include `TAILQ_INIT`, `TAILQ_INSERT_HEAD`, `TAILQ_INSERT_TAIL`, `TAILQ_INSERT_AFTER`, `TAILQ_INSERT_BEFORE`, `TAILQ_REMOVE`, `TAILQ_CONCAT`, and `TAILQ_SWAP`.
- Access macros include `TAILQ_EMPTY`, `TAILQ_FIRST`, `TAILQ_LAST`, `TAILQ_NEXT`, and `TAILQ_PREV`.

## Control Flow
TAILQ heads maintain first element and pointer-to-last-next. Insertions update neighboring `tqe_prev` pointers and the head's tail pointer. Removal repairs either the next element's previous pointer or the head tail pointer, then patches the previous next pointer. Safe iteration variants precompute the next/previous element before the body runs.

## State And Persistence Behavior
Queue links are in-memory intrusive list state embedded in owning structures. No persistent data is encoded directly, but queues organize persistent-resource handles, sessions, work units, and metadata objects.

## Dependencies And Integration Points
Self-contained apart from C/C++ type syntax. Used broadly by file-handle queues, session handle caches, cursors, RTS work queues, schema structures, and many internal lists.

## Risks
Intrusive macros do no runtime validation in this stripped version; double insert/remove or wrong field/head type can corrupt memory. Because all conflict macros are undefined, including this header intentionally overrides platform definitions. C++ class variants must be used for class types.

## Test Signals
Unit tests or sanitizer tests should cover insert/remove at head/tail/middle, concat, swap, safe iteration while removing elements, empty queues, C++ class entries, and misuse detection under debug instrumentation where available.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/ref_inline.h -->
# sources/storage-engines/wiredtiger/src/include/ref_inline.h

## Purpose
Defines the controlled API for reading, writing, CASing, locking, and unlocking `WT_REF` page-reference states, plus a helper for detecting root references.

## Important APIs, Types, And Functions
- `__wt_ref_is_root` treats a ref with null `home` as the root reference.
- `__ref_set_state` writes the ref state with a release barrier.
- `WT_REF_SET_STATE` wraps state writes and optionally records diagnostic history with `HAVE_REF_TRACK`.
- `__ref_get_state` and `WT_REF_GET_STATE` read the volatile state with relaxed atomics.
- `__ref_cas_state` and `WT_REF_CAS_STATE` CAS from an old to new state and optionally record callsite history.
- `__ref_lock`/`WT_REF_LOCK` spin until the state becomes `WT_REF_LOCKED`, returning the previous state.
- `__ref_try_lock`/`WT_REF_TRYLOCK` attempt one lock transition.
- `WT_REF_UNLOCK` restores a previous state through `WT_REF_SET_STATE`.

## Control Flow
Locking repeatedly reads the current state, yields between attempts, and CASes any non-locked state to `WT_REF_LOCKED`. Trylock performs a single read/CAS and returns `EBUSY` if already locked or if the CAS loses a race. Diagnostic tracking stores session, function, line, timestamp, and state in a ring without strict synchronization to avoid hot-path overhead.

## State And Persistence Behavior
The ref state is volatile in-memory page-tree state controlling access to pages and their lifecycle. It is not persistent itself, but it protects loading, eviction, split, and reconciliation behavior for persistent pages.

## Dependencies And Integration Points
Depends on `WT_REF`, `WT_REF_STATE`, atomics, TSan suppression helpers, barriers, session diagnostics, yield, and `WT_ASSERT`. Used by page eviction, tree walking, hazard handling, reconciliation, and page split logic.

## Risks
Direct access to `ref->__state` outside these macros breaks synchronization and diagnostics. Relaxed reads are acceptable only within the documented state protocol. Diagnostic history intentionally races and cannot be treated as authoritative under contention. Locking spins, so callers must avoid holding refs locked for long operations.

## Test Signals
Concurrency tests should cover CAS state transitions, lock/trylock contention, unlock restoring previous states, root-ref detection, ref tracking history in diagnostic builds, and TSan runs for page-tree operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/ref_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/rollback_to_stable.h -->
# sources/storage-engines/wiredtiger/src/include/rollback_to_stable.h

## Purpose
Defines rollback-to-stable (RTS) verbose tags, statistics helpers, phase identifiers, worker queue units, singleton RTS state, and session-walk callback state.

## Important APIs, Types, And Functions
- `WT_RTS_VERB_TAG_*` constants label fine-grained RTS verbose messages.
- `WT_CHECK_RECOVERY_FLAG_TXNID` checks whether a transaction id belongs to the recovery checkpoint snapshot range.
- `WT_VERB_RECOVERY_RTS` selects recovery+RTS verbose categories during recovery or RTS alone otherwise.
- `WT_RTS_STAT_CONN_INCR` and `WT_RTS_STAT_CONN_DATA_INCR` increment live or dry-run statistic variants.
- `WT_RTS_PHASE_*` constants identify progress phases.
- `WT_RTS_MAX_WORKERS` caps RTS workers.
- `struct __wt_rts_work_unit` stores queued URI rollback work.
- `struct __wt_rollback_to_stable` stores RTS methods, thread group, worker counts, spin-protected queue, dry-run flag, and progress counters/timers.
- `struct __wt_rts_cookie` returns active transaction/cursor findings from session walks.

## Control Flow
The header is mostly declarative. Stat macros branch on `S2C(session)->rts->dryrun`. Recovery verbose category selection branches on `WT_CONN_RECOVERING`. Work units are queued through a TAILQ protected by `rts_lock`; worker execution is implemented elsewhere through the method pointers and thread group.

## State And Persistence Behavior
RTS itself mutates persistent table/history-store state to roll data back to stable timestamps, but this header defines the connection-level runtime state and progress accounting. Dry-run mode redirects stats without applying live stat increments. Progress fields are shared and updated across RTS worker threads.

## Dependencies And Integration Points
Depends on connection flags, verbose categories, stats macros, TAILQ, spinlocks, thread groups, timestamps, timers, and session walk logic. Integrated with recovery, history store, btree rollback, metadata scanning, and shutdown RTS.

## Risks
RTS is correctness-critical for timestamp recovery. Dry-run branching must mirror real stats. Shared progress counters need atomic/safe access. Queue locking must protect work-unit membership. Verbose tags are diagnostic contracts used by tests/log analysis.

## Test Signals
Signals include RTS recovery tests, dry-run stat tests, worker queue/thread-count tests, progress phase reporting, verbose tag assertions in log-based tests, active transaction/cursor preflight checks, and timestamp boundary rollback scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/rollback_to_stable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/schema.h -->
# sources/storage-engines/wiredtiger/src/include/schema.h

## Purpose
Declares schema-level data structures for column groups, indexes, tables, layered tables, truncate tracking, and import lists, plus lock helper macros that enforce schema/metadata/table/handle/backup lock order and re-entrant session lock tracking.

## Important APIs, Types, And Functions
- Projection characters: `WT_PROJ_KEY`, `WT_PROJ_NEXT`, `WT_PROJ_REUSE`, `WT_PROJ_SKIP`, and `WT_PROJ_VALUE`.
- `WT_COLGROUP`, `WT_INDEX`, `WT_TABLE`, `WT_TRUNCATE`, `WT_LAYERED_TABLE`, `WT_IMPORT_ENTRY`, and `WT_IMPORT_LIST` define schema object state.
- Flags include `WT_INDEX_IMMUTABLE`, `WT_LAYERED_TABLE_OPEN`, and `WT_IMPORT_INVALID_FILE_ID`.
- `WT_COLGROUPS` computes default/tiered-shared column group count.
- Lock-state masks combine handle-list, table, and hot-backup read/write flags.
- Generic lock macros `WT_WITH_LOCK_WAIT` and `WT_WITH_LOCK_NOWAIT` support re-entrant spinlocks using `session->lock_flags`.
- Specialized macros acquire checkpoint, handle-list read/write, metadata, schema, table read/write, and hot-backup read/write locks.

## Control Flow
Schema/table structures are passive state. Lock macros test session lock flags first to allow re-entrant use by the owning thread. Otherwise they acquire the correct spinlock or rwlock, set the session flag, execute caller-provided `op`, clear the flag, and unlock. Nowait variants surface `EBUSY` through `__wt_session_set_last_error`. Assertions enforce lock ordering, such as schema lock before handle-list/table locks and write locks not being taken while read locks are held.

## State And Persistence Behavior
Schema structures mirror persistent metadata entries for tables, column groups, indexes, layered table constituents, and imports. Truncate entries store transaction/timestamp visibility state and key ranges for layered table fast truncate. Lock flags are transient per-session state but protect persistent metadata and handle lifecycle updates.

## Dependencies And Integration Points
Depends on config items, data handles, collators, TAILQ, rwlocks/spinlocks, session lock flags, connection locks, backup state, session error reporting, and table/layered-table metadata. Integrated with schema create/drop/alter/open, import, tiered/layered tables, checkpoint, hot backup, and handle cache management.

## Risks
Lock macros execute arbitrary `op` inline; `op` must not bypass error handling or jump over unlock cleanup. Misordered locks can deadlock and are guarded mainly by assertions. Session lock flags assume a session is used by one thread at a time. Layered truncate state mixes lock-protected membership with lock-free committed visibility, so callers must honor the documented synchronization split.

## Test Signals
Schema tests should cover lock ordering assertions, nowait lock conflict error codes, re-entrant lock behavior, table/index/column-group open/close lifecycle, import sorting by file id including invalid ids, layered table truncate visibility, hot-backup read/write exclusion, and concurrent schema operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/schema.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/serial_inline.h -->
# sources/storage-engines/wiredtiger/src/include/serial_inline.h

## Purpose
Implements inline serialized insertion and update paths for page skip lists and update chains, including column-store append record allocation, page dirtying, cache footprint accounting, newest timestamp heuristics, and obsolete update checks.

## Important APIs, Types, And Functions
- `__insert_simple_func` CAS-inserts a `WT_INSERT` into already-linked skiplist positions without taking the page lock.
- `__insert_serial_func` inserts into a skiplist with validation and tail maintenance.
- `__col_append_serial_func` allocates record numbers for append operations and updates `btree->last_recno`.
- `__wt_page_modify_update_timestamp` stores the approximate newest seen global timestamp into page modify state.
- `__wt_col_append_serial` serializes column-store append insertion, cache accounting, dirty marking, and timestamp update.
- `__wt_insert_serial` serializes row/column insertions, using the simple lock-free path when possible.
- `__wt_update_serial` CAS-inserts a `WT_UPDATE` into an update chain, validates transaction rules on races, updates cache/dirty/timestamp state, and may trim obsolete updates.

## Control Flow
Insert helpers read each target skiplist pointer once with an acquire barrier, validate it still matches `new_ins->next[i]`, and CAS in the new insert. Failure at level zero returns `WT_RESTART`; upper-level failure returns success because lower levels are sufficient. Append logic assigns a new record number when the caller used `WT_RECNO_OOB`, positions insert stacks at tails, inserts, and updates `last_recno`. Public insert/append wrappers take the page lock unless the caller has exclusive access, transfer ownership of allocated memory, free it on error, then update cache footprint and dirty state after publication.

Update serialization repeatedly CASes a new update onto the chain; if it loses a race, it revalidates with `__wt_txn_modify_check` before retrying. After publication it updates cache and dirty state, skips obsolete checks under configured conditions/history store/exclusive access/short chains, may advance oldest transaction state, avoids ingest garbage collection races, and finally calls `__wt_update_obsolete_check`.

## State And Persistence Behavior
These helpers mutate in-memory page insert lists, update chains, btree `last_recno`, page cache footprint, dirty state, and page modify timestamps. They prepare changes that later reconciliation/checkpoint can persist. They also influence eviction by timestamp and obsolete-update metadata.

## Dependencies And Integration Points
Depends on page locks, skiplist structures, atomics/barriers, transaction visibility/modify checks, cache accounting, page modify state, history-store detection, eviction controls, btree flags, and session/connection timestamp state. Integrated with cursor insert/update/modify paths and reconciliation/eviction.

## Risks
Memory ordering is critical: structure setup must be visible before list publication. Lost upper skiplist levels are tolerated but reduce skiplist efficiency. Ownership transfer means callers must not free `*new_insp`/`*updp` after calling. Obsolete trimming after insertion must not race with history store or ingest btree readers. Updating `last_recno` assumes rightmost-page locking discipline.

## Test Signals
Concurrency tests should stress insert/update races, `WT_RESTART` behavior, append record allocation, skiplist tail maintenance, cache footprint accounting, dirty marking, timestamp heuristic updates, obsolete update trimming, history-store exceptions, and exclusive versus locked paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/serial_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/session.h -->
# sources/storage-engines/wiredtiger/src/include/session.h

## Purpose
Defines `WT_SESSION_IMPL`, the central per-session internal state object, plus supporting structs/macros for data handle caches, hazard pointers, prefetch, error reporting, session-to-connection/btree/filesystem access, cursor sweeping, lock flags, operational flags, generation management, and operation tracking.

## Important APIs, Types, And Functions
- `WT_DATA_HANDLE_CACHE` stores per-session cached data handles in list and hash queues.
- `WT_HAZARD` and `WT_HAZARD_ARRAY` track pages protected from eviction, initially sized by `WT_SESSION_INITIAL_HAZARD_SLOTS`.
- `WT_PREFETCH` tracks sequential disk-read prefetch signals.
- `WT_ERROR_INFO` stores last API error, sub-error, message, and message buffer; constants define empty/success messages.
- `S2C`, `S2BT`, `S2BT_SAFE`, and `S2FS` map sessions to connection, btree, and active filesystem.
- Cursor sweep constants control cached cursor cleanup.
- `WT_SESSION_IMPL` includes public interface, event handler, session identity, operation timeouts, current data handle, bucket storage, handle/cursor caches, backup/compact/import/history-store/metadata tracking, lock callback state, scratch buffers, diagnostic thread checks, reconciliation/eviction timelines, transaction state, prefetch, checkpoint, operation handle lists, stats buckets, lock flags, operational flags, persistent-across-close RNG/hash/generation/stash/hazard/optrack state, and session stats.
- `WT_SESSION_CLEAR_SIZE` identifies the prefix cleared on session close/reuse.
- Generation constants classify checkpoint, eviction, snapshot, hazard, split, and commit generations.
- `WT_SESSION_FIRST_USE` tests whether hazard arrays have been initialized.
- `WT_READING_CHECKPOINT` detects open checkpoint handles.

## Control Flow
This header primarily defines layout and access macros. The session lifecycle clears fields up to `WT_SESSION_CLEAR_SIZE`, preserving RNG state, cached cursor/handle hash arrays, generation/stash/hazard memory, operation tracking fields, and stats as documented. Access macros assume `session->iface.connection` and `session->dhandle` are valid for their use cases.

## State And Persistence Behavior
`WT_SESSION_IMPL` is runtime state, but it coordinates persistent operations: current data handle, transactions, metadata tracking, checkpoint state, reconciliation/eviction timelines, backup cursors, import lists, and history-store cursors. Some memory persists past session close because other threads may still reference hazard/generation-protected memory; stash entries are released only when generations permit.

## Dependencies And Integration Points
Depends on almost every subsystem: connection, btree, filesystem, cursors, data handles, metadata, locks, transactions, checkpoint, cache/eviction/reconciliation, prefetch, backup, compact, import, operation tracking, stats, and diagnostics. It is the common context passed into most internal APIs.

## Risks
Because this struct is central and large, layout changes can affect session clearing, memory retention, diagnostics, and performance. `S2BT` requires a non-null data handle; misuse can crash. Session lock flags assume single-threaded session access. Persisted-after-close fields must not be accidentally cleared while other threads can observe them. Flag-space additions must stay within generated ranges and avoid collisions.

## Test Signals
Signals include session open/close/reuse tests, hazard pointer lifecycle, generation stash reclamation, cursor/handle cache sweeping, metadata transaction nesting, API timeout behavior, diagnostic single-thread checks, operation tracking buffers, checkpoint/eviction/reconciliation timeline capture, and flag-generation validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/session_inline.h -->
# sources/storage-engines/wiredtiger/src/include/session_inline.h

## Purpose
Provides diagnostic-only inline checks enforcing WiredTiger's contract that a non-default session is used by only one thread at a time, while allowing re-entrant API calls by the owning thread.

## Important APIs, Types, And Functions
- `__wt_single_thread_check_start(WT_SESSION_IMPL *)` records or verifies the owning thread on API entry.
- `__wt_single_thread_check_stop(WT_SESSION_IMPL *)` decrements re-entry depth and releases ownership when the outermost API call exits.

## Control Flow
In non-diagnostic builds both functions are no-ops. In diagnostic builds, start obtains the current thread id, reads the current owner with relaxed atomics, and, if this is a non-default session not already owned by the same thread, tries to take `thread_check.lock`. Failure asserts with detailed session state. On success it stores the current owner and increments `entry_count`. Stop decrements `entry_count`; when it reaches zero for non-default sessions, it clears the owner and unlocks.

## State And Persistence Behavior
This logic mutates diagnostic runtime fields under `WT_SESSION_IMPL.thread_check`. It does not persist data, but it protects the broader invariant that session-local fields can be treated as thread-local by many lock macros and subsystems.

## Dependencies And Integration Points
Depends on diagnostic build flags, thread id retrieval, spinlock trylock/unlock, relaxed atomic load/store, session names/last operations, API call depth, and data-handle names. It supports assumptions used in schema lock flags, operation tracking, cursor/session state, and error handling.

## Risks
The checks are compiled out in production, so they detect but do not prevent misuse in release builds. The default session intentionally permits concurrent access because it is used during connection initialization and error paths. Relaxed atomics are chosen to avoid hiding bugs; correctness relies on the spinlock for ownership transitions.

## Test Signals
Diagnostic tests should cover same-thread re-entry, cross-thread sequential use, concurrent cross-thread assertion, default-session exemption, owner clearing on final stop, and assertion messages containing useful active operation/session details.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/session_inline.h -->

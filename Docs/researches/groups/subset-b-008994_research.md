# subset-b-008994 research

Grouped research report for WiredTiger support sources. Each section preserves the source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/global.c -->
# sources/storage-engines/wiredtiger/src/support/global.c

## Purpose
`global.c` owns process-wide WiredTiger initialization. It defines the global `WT_PROCESS __wt_process`, the timing stress name-to-flag table `__wt_stress_types`, validates runtime endianness against build configuration, initializes process locks and connection queues, installs checksum entry points, and calibrates the clock path used by `__wt_clock`.

## Important APIs, Types, and Functions
The exported entry point is `__wt_library_init`, which must run before most library work. It calls `__endian_check`, then `__wt_once(__global_once)` behind a local `first` guard and returns any cached initialization failure through `__wt_pthread_once_failed`. `__global_once` initializes `__wt_process.spinlock`, `__wt_process.connqh`, checksum functions from `wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func`, and clock configuration through `__global_setup_clock`.

On `__amd64` and `__aarch64__`, the file also contains TSC calibration helpers: `__reset_thread_tick`, `__get_epoch_and_tsc`, `__compare_uint64`, `__get_epoch_call_ticks`, `__get_epoch_and_ticks`, and `__global_calibrate_ticks`. These compute a `tsc_nsec_ratio` by measuring `__wt_epoch` latency and comparing elapsed wall-clock nanoseconds to `__wt_rdtsc` ticks across a short sleep.

## Control Flow
Initialization begins with a hard compatibility check: a build compiled for the wrong endian mode returns `EINVAL` and emits a stderr diagnostic. The one-time global initializer sets up synchronization and queues, then defaults clocking to `__wt_epoch`. On supported CPU families, calibration tries to obtain low-jitter wall-clock/TSC pairs, sleeps for `CLOCK_CALIBRATE_USEC`, and only switches `__wt_process.use_epochtime` to `false` if the measured ratio is meaningful.

## State and Persistence Behavior
All state is in process memory. `__wt_process` persists for the life of the process and stores lock state, the connection queue, checksum callbacks, clock calibration fields, and standalone-build flags. `__wt_pthread_once_failed` persists the first initialization failure. No disk state is written.

## Dependencies and Integration Points
This file depends on WiredTiger internal primitives from `wt_internal.h`: `__wt_once`, spin locks, `TAILQ_INIT`, CRC32C selector functions, clock helpers, TSC reads, sleeps, qsort, and timing macros. It integrates with connection open paths that call `__wt_library_init`, runtime timing-stress configuration via `__wt_stress_types`, and any code using `__wt_clock`.

## Risks
Clock calibration is intentionally best-effort; noisy scheduling, low timer granularity, virtualized TSC behavior, or unstable CPU counters can leave the engine on the epoch-time fallback. The qsort comparator casts a `uint64_t` difference to `int`, which is acceptable for relative ordering in this local calibration set only if differences remain small enough not to produce misleading comparator results. The local `first` optimization is fronting a true once primitive, so correctness depends on `__wt_once` for race safety, while the local flag only reduces overhead.

## Test Signals
Useful tests include startup on big- and little-endian builds, repeated concurrent calls to `__wt_library_init`, injected spin-lock initialization failure, deterministic mapping of every `__wt_stress_types` name to a unique flag, and clock behavior on TSC-capable and non-TSC platforms. Runtime stats or targeted tests should verify that `use_epochtime` remains true when calibration fails and flips only after a valid ratio is measured.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/global.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/hash_city.c -->
# sources/storage-engines/wiredtiger/src/support/hash_city.c

## Purpose
`hash_city.c` embeds WiredTiger's wrapper around Google's CityHash64 implementation. It provides a fast, deterministic 64-bit hash for byte strings and is used by support data structures such as the internal hash map.

## Important APIs, Types, and Functions
The public WiredTiger-facing API is `__wt_hash_city64(const void *s, size_t len)`, which returns `CityHash64(s, len)`. Internal helpers include the `uint128` pair structure, `UNALIGNED_LOAD64`, `UNALIGNED_LOAD32`, endian-normalizing `Fetch64` and `Fetch32`, `Hash128to64`, `Rotate`, `RotateByAtLeast1`, `ShiftMix`, `HashLen16`, and length-specialized hash routines for `0..16`, `17..32`, and `33..64` byte ranges. Longer inputs use `WeakHashLen32WithSeeds` and a 64-byte chunk loop.

## Control Flow
The hash path branches by input length. Short inputs mix one or more fetched words with CityHash constants. Medium inputs combine front, middle, and tail words. Inputs longer than 64 bytes seed state from the tail, then iterate over 64-byte chunks while rotating and mixing `x`, `y`, `z`, `v`, and `w`, and finally collapse the state through nested `HashLen16` calls.

## State and Persistence Behavior
The implementation is stateless. It uses compile-time constants `k0` through `k3` and stack-local state only. There is no allocation, locking, or persistence.

## Dependencies and Integration Points
The file includes `wt_internal.h` for basic types and WiredTiger byte-swap fallbacks. Big-endian builds map native loads through platform byte-swap routines or WiredTiger byte-swap helpers so the hash result follows the expected byte order. `hash_map.c` uses `__wt_hash_city64` to choose buckets.

## Risks
CityHash64 is not a cryptographic hash and should not be used where adversarial collision resistance is required. Determinism across architectures depends on the endian conversion branches staying correct. Callers must pass a valid memory range of at least `len` bytes; the function deliberately performs unaligned fixed-width loads near both ends of the buffer for performance. Because this is third-party algorithm code, local style refactors can accidentally change hash compatibility.

## Test Signals
Golden-vector tests should cover lengths 0, 1, 3, 4, 8, 16, 17, 32, 33, 64, 65, and multi-block inputs. Cross-platform tests should compare little- and big-endian outputs for the same byte sequence. Hash-map tests indirectly exercise distribution and bucket selection, but direct deterministic vectors are the strongest signal against accidental algorithm drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/hash_city.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/hash_map.c -->
# sources/storage-engines/wiredtiger/src/support/hash_map.c

## Purpose
`hash_map.c` implements a small internal hash map with separately locked buckets. It stores copied key/value blobs in `WT_HASH_MAP_ITEM` entries linked from bucket `TAILQ`s and supports lookup, optional insert-on-miss for fixed-size values, and bucket lock handoff to callers.

## Important APIs, Types, and Functions
`__wt_hash_map_init` allocates the `WT_HASH_MAP`, bucket array, and per-bucket spin locks. `__wt_hash_map_destroy` frees every item, its copied key and data, destroys locks, and nulls the caller's map pointer. `__wt_hash_map_get` performs lookup and can insert a zeroed fixed-size value when `insert_if_not_found` is true. `__wt_hash_map_unlock` releases the bucket lock retained by a successful `get(..., keep_locked=true)`. The static `__hash_map_insert_new` allocates and inserts a new item into an already locked bucket.

## Control Flow
Initialization allocates arrays sized by `hash_size`, initializes every bucket queue, then initializes every bucket lock. Lookup hashes the key with `__wt_hash_city64(key, key_size) % hash_size`, locks that bucket, scans entries with size and `memcmp` equality, and either returns the stored data pointer or inserts a fixed-size zeroed item. Error paths release locks unless the caller explicitly requested a successful locked return.

## State and Persistence Behavior
Map state is entirely in memory: bucket queues, bucket locks, copied keys, copied values, `hash_size`, and an externally configured `value_size`. There is no resizing, disk persistence, or background cleanup. Data pointers returned by `get` are owned by the map and remain valid until removal by destroy.

## Dependencies and Integration Points
The map depends on WiredTiger allocation helpers, spin locks, `TAILQ`, and `__wt_hash_city64`. It is intended for internal components that need a simple synchronized key/value table without adopting a larger indexing structure. The `keep_locked` option allows callers to perform compound operations on the returned value while holding the bucket lock.

## Risks
`hash_size` must be nonzero or bucket selection divides by zero. Insert-on-miss requires `hash_map->value_size` to be set; otherwise the function returns `EINVAL`. There is no delete API or growth policy, so long-lived maps with many keys can develop long bucket chains. The `keep_locked` contract is sharp: callers must call `__wt_hash_map_unlock` with the same key bytes and size, and must not use it after a failed get.

## Test Signals
Tests should cover init failure cleanup, destroy of null and populated maps, collision chains, get-not-found returning `WT_NOTFOUND`, fixed-size insert-on-miss zeroing, data size reporting, keep-locked mutation followed by explicit unlock, and concurrent access to separate and identical buckets. Edge tests should reject insert-on-miss when `value_size` is zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/hash_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/hazard.c -->
# sources/storage-engines/wiredtiger/src/support/hazard.c

## Purpose
`hazard.c` implements WiredTiger hazard pointers, the per-session mechanism that pins in-memory pages so eviction cannot free a page while another thread is reading or modifying it. It is a core correctness layer between B-tree page access, eviction, and session lifecycle management.

## Important APIs, Types, and Functions
`__wt_hazard_set_func` publishes a hazard pointer for a `WT_REF`, returning `busyp=true` when the page is not safely usable. `__wt_hazard_clear` releases a hazard pointer and panics if the session did not hold it. `__wt_hazard_close` reports and clears leaked hazards during session close. `__wt_hazard_check` walks sessions to find any hazard pointer on a ref, optionally returning the owning session. `__wt_hazard_count` counts this session's hazards for a ref, and `__wt_hazard_check_assert` verifies no hazard remains, optionally waiting. `hazard_grow`, `hazard_get_reference`, and `__hazard_check_callback` are internal helpers.

## Control Flow
Setting a hazard first skips no-evict trees, then checks the ref state for `WT_REF_MEM`. It grows the session hazard array if full, finds or exposes a slot, writes `hp->ref`, issues a full barrier, and rechecks the ref state. If the ref is still memory-resident, the hazard becomes active; otherwise the slot is cleared and the caller sees `busy`. Clearing searches in reverse, release-stores `NULL`, decrements `num_active`, and may reset `inuse` to zero. System-wide checks enter the hazard generation, walk all sessions, and leave the generation after the scan.

## State and Persistence Behavior
Hazard state lives in `session->hazards`: the pointer array, `size`, atomic `inuse`, and `num_active`. Growth allocates a doubled array, release-publishes it, increments the hazard generation, and stashes the old array for deferred freeing through `__wt_stash_add`. Diagnostic builds also store the function and line that set each hazard.

## Dependencies and Integration Points
This file is tightly integrated with B-tree ref states, eviction, session arrays, generation management, statistics, stashed memory reclamation, and diagnostic reporting. Correctness depends on WiredTiger's memory-barrier macros, atomic loads/stores, and the eviction protocol that locks refs before checking hazards.

## Risks
The code is deliberately barrier-heavy because stale ordering can produce use-after-free or out-of-bounds reads after hazard-array growth. `__wt_hazard_clear` panics when a matching ref is absent because continuing would imply an unpinned page was used. Session close tolerates leaked hazards but logs them, which prevents a close-time leak from becoming an eviction pin. Generation entry around global scans is required because another thread can grow and retire a hazard array while eviction is walking it.

## Test Signals
Stress tests should race page access, eviction, splits, and hazard-array growth. Diagnostic tests should verify function/line dump output for leaked hazards. Assertions should cover no-evict btrees, repeated set/clear, clear of missing hazard producing panic, `__wt_hazard_check_assert` with and without wait, and deferred freeing under hazard generation. Eviction tests should demonstrate that a page with any session hazard is not discarded.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/hazard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/hex.c -->
# sources/storage-engines/wiredtiger/src/support/hex.c

## Purpose
`hex.c` converts between raw bytes and printable hexadecimal or escaped-hex strings, and provides bounded diagnostic dumping of raw buffers. It supports logging, debugging, metadata display, and APIs that need textual byte encodings.

## Important APIs, Types, and Functions
`__wt_fill_hex` wraps the inline `__fill_hex` raw-to-hex converter. `__wt_log_data_dump` logs a formatted preamble and a hex dump in 1 KiB chunks, capped at 64 KiB. `__wt_raw_to_hex` and `__wt_raw_to_esc_hex` convert raw data into `WT_ITEM` buffers. `__wti_hex2byte` parses two hex characters into one byte. `__wt_hex_to_raw`, `__wt_nhex_to_raw`, and `__wt_esc_hex_to_raw` parse printable encodings back into raw bytes. `__hex_fmterr` centralizes invalid-hex errors.

## Control Flow
Raw-to-hex reserves one byte for NUL termination and emits two hex digits per source byte while capacity remains. Escaped-hex keeps printable characters as-is, doubles literal backslashes, and emits backslash plus two hex digits for non-printable bytes. Raw hex parsing rejects odd-length inputs, initializes an output buffer at half the input size, then decodes pairs. Escaped parsing copies ordinary bytes and decodes backslash escapes unless the escape is a doubled backslash.

## State and Persistence Behavior
The functions mutate caller-provided `WT_ITEM` buffers or temporary scratch buffers. No persistent state is maintained. `__wt_log_data_dump` allocates scratch items for the preamble and chunk text and frees them on all paths.

## Dependencies and Integration Points
The file uses WiredTiger buffer allocation, scratch buffers, printf-style buffer formatting, logging through `__wt_errx`, character classification, and `__wt_hex`. It is used by debug and logging paths and by higher-level serialization code that needs printable byte strings.

## Risks
The length reported by `__fill_hex` includes the terminating NUL because it measures after writing it; callers must understand that convention. Size calculations like `size * 2 + 1` and `size * 3 + 1` require upstream sizes to be reasonable enough not to overflow `size_t`. `__wt_log_data_dump` intentionally truncates large dumps, so logs are diagnostic rather than complete evidence for very large buffers. Escaped parsing treats malformed or incomplete escapes as format errors.

## Test Signals
Tests should round-trip raw hex and escaped hex over empty input, printable ASCII, backslash, NUL bytes, high-bit bytes, odd-length hex, invalid hex characters, and incomplete escapes. Logging tests should verify empty-buffer output, chunk boundaries at 1024 bytes, and truncation after 64 KiB. Buffer tests should check NUL termination and reported sizes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/hex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/json.c -->
# sources/storage-engines/wiredtiger/src/support/json.c

## Purpose
`json.c` converts between WiredTiger's packed key/value byte formats and a constrained JSON representation, and provides a tokenizer plus JSON string helpers used by cursor JSON mode. It binds schema column names to packed values so keys and values can be displayed and accepted as named JSON fields.

## Important APIs, Types, and Functions
Primary exported/internal APIs include `__wt_json_alloc_unpack`, `__wt_json_close`, `__wt_json_unpack_str`, `__wt_json_column_init`, `__wt_json_token`, `__wt_json_tokname`, `__wt_json_to_item`, `__wt_json_strlen`, and `__wt_json_strncpy`. Internal helpers include `__json_unpack_char`, `__json_unpack_put`, `__json_struct_size`, `__json_struct_unpackv`, `json_string_arg`, `json_int_arg`, `json_uint_arg`, `__json_pack_struct`, and `__json_pack_size`. The `WT_PACK_JSON_GET` macro maps pack-value types to JSON argument parsers.

## Control Flow
Unpacking initializes a pack iterator and a pack-name iterator, calculates the JSON buffer size by simulating field output, allocates or grows `json->key_buf` or `json->value_buf`, and writes `"name" : value` pairs separated by comma-newline. Strings are escaped with short JSON escapes where possible or `\u00XX` notation for forced byte-oriented output. Packing first validates field names, token order, and value types, computes the packed size, allocates a `WT_ITEM`, and writes packed values into it.

## State and Persistence Behavior
State is stored in `cursor->json_private` as a `WT_JSON` object containing key/value output buffers and key/value column-name config items. `__wt_json_close` frees those buffers and name strings. The tokenizer and string helpers are stateless and operate over caller memory.

## Dependencies and Integration Points
The file depends on WiredTiger pack/unpack internals (`WT_PACK`, `WT_PACK_VALUE`, `__pack_next`, `__pack_write`, `__unpack_read`, `__pack_name_next`), config item naming, cursor URI projection parsing, buffer allocation, hex parsing, character classification, and error-reporting helpers. It integrates with cursor JSON mode and schema metadata describing key/value formats and column names.

## Risks
This is not a general-purpose JSON engine. It tokenizes enough JSON for WiredTiger's schema-shaped representation and accepts only decimal integer forms for integer pack types. Unicode handling is byte-oriented: input `\uXXXX` must fit into `\u00XX` for `__wt_json_strncpy`, and higher Unicode bytes are rejected. Field names and order are validated against schema names, so callers must preserve the generated order. Floating-point tokens are recognized by the tokenizer but are not consumed by the pack macro shown here unless supported elsewhere by format handling. Buffer sizing relies on the sizing pass matching the writing pass exactly.

## Test Signals
Tests should cover JSON unpacking for strings, byte arrays, signed and unsigned integers, recno-like formats, empty strings, embedded control bytes, quotes, backslashes, and column projections. Packing tests should reject wrong field names, missing colons or commas, negative unsigned values, malformed strings, invalid Unicode hex, high-byte Unicode, extraneous trailing input, and destination buffers that are too small. Round-trip tests should compare packed input to JSON and back for representative key/value formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/json.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/lock_ext.c -->
# sources/storage-engines/wiredtiger/src/support/lock_ext.c

## Purpose
`lock_ext.c` exposes WiredTiger spin locks through the extension API. It lets extension code allocate, lock, unlock, and destroy a `WT_EXTENSION_SPINLOCK` while reusing core WiredTiger spin-lock implementation and memory ownership.

## Important APIs, Types, and Functions
`__wt_ext_spin_init` allocates a `WT_SPINLOCK` using the connection default session, initializes it with `__wt_spin_init`, and stores it in `ext_spinlock->spinlock`. `__wt_ext_spin_lock` and `__wt_ext_spin_unlock` cast the opaque extension pointer back to `WT_SPINLOCK` and operate with the caller's session. `__wt_ext_spin_destroy` destroys and frees the allocated lock and nulls the extension handle.

## Control Flow
Initialization clears the opaque pointer, obtains `default_session` from `wt_api->conn`, allocates the lock, initializes it, and unwinds allocation on initialization failure. Lock and unlock are direct wrappers. Destroy uses the default session to match initialization context, then frees the lock.

## State and Persistence Behavior
The only state is the heap-allocated spin lock referenced by `WT_EXTENSION_SPINLOCK.spinlock`. It is process memory owned by the extension lock handle. There is no persistence.

## Dependencies and Integration Points
The file bridges public extension API types (`WT_EXTENSION_API`, `WT_EXTENSION_SPINLOCK`, `WT_SESSION`) to internal connection/session and `WT_SPINLOCK` types. It depends on WiredTiger allocation and spin-lock primitives and is part of the API surface used by loadable extensions.

## Risks
Callers must destroy only initialized locks and must not lock after destroy. The wrappers do not null-check `ext_spinlock->spinlock` in lock/unlock paths. Destroy uses the connection default session, so the API connection must remain valid for the lock lifetime. Extension code must avoid recursive or mismatched lock usage according to the underlying spin-lock semantics.

## Test Signals
Extension API tests should initialize and destroy locks, handle allocation or spin-init failures, lock/unlock from extension sessions, verify the pointer is nulled after destroy, and run concurrent extension threads through the wrapper. Negative tests should document behavior for uninitialized or double-destroy cases if the public API promises anything there.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/lock_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/modify.c -->
# sources/storage-engines/wiredtiger/src/support/modify.c

## Purpose
`modify.c` packs, applies, and reconstructs WiredTiger modify operations. A modify represents byte-range replacements against a value, allowing updates to store deltas rather than full values. The file supports cursor API modify calls and reconstructs full values by rolling visible modify updates forward from a base value.

## Important APIs, Types, and Functions
`__wt_modify_idempotent` checks whether every modify entry replaces exactly as many bytes as it writes. `__wt_modify_pack` serializes an array of `WT_MODIFY` entries into a scratch `WT_ITEM`. `__wt_modify_apply_item` applies a packed modify to a `WT_ITEM`, using `__modify_fast_path`, `__modify_apply_no_overlap`, and `__modify_apply_one`. `__wt_modify_apply_api` is the cursor-facing path that packs entries, grows the cursor value buffer, and applies the modify. `__wt_modify_reconstruct_from_upd_list` rebuilds a full value from a modify update and earlier updates or on-page data.

## Control Flow
Packing writes the entry count, then fixed-size metadata triples, then entry data contiguously to reduce unaligned access. Applying removes the trailing NUL for string format `S`, tries an in-place fast path for same-size overwrites, detects sorted non-overlapping modifications for reverse single-pass construction, and otherwise applies entries one by one with padding, overwrite, shrink, or grow behavior. Reconstruction walks the update list from the current modify until it finds a full standard update or falls back to the on-page value, collects visible modify updates, grows the destination buffer to the computed maximum, and applies modifies from oldest to newest.

## State and Persistence Behavior
Packed modify buffers are transient scratch items or `WT_UPDATE` payloads. Applying mutates the supplied `WT_ITEM` buffer in memory and may grow it before modification. Reconstruction populates `WT_UPDATE_VALUE`, carrying time-window fields from the original modify and producing a standard full value. The persistent implication is indirect: modify updates stored in update chains or history can be reconstructed into full values for reads and reconciliation.

## Dependencies and Integration Points
The file depends on cursor internals, `WT_MODIFY_FOREACH` macros, update vectors, transaction visibility macros, prepared-update state, on-page value return, buffer growth helpers, value-format semantics, and statistics counters. It integrates with `WT_CURSOR::modify`, update-chain reads, reconciliation, checkpoint handling, and transaction isolation.

## Risks
Offsets are cumulative in API order, so sorted/non-overlap fast paths must preserve modify semantics exactly. Buffer sizing is guarded by `WT_ASSERT_ALWAYS`; bad max-size calculation would be memory unsafe in non-diagnostic paths. Read-uncommitted readers cannot safely reconstruct values when concurrent aborts may remove required base data, so the function returns rollback for that case. Prepared rollback races require special handling of locked/in-progress prepare states. Applying modifies over tombstones or missing full base values is invalid and protected by assertions and retry logic.

## Test Signals
Tests should cover idempotent and resizing modifies, append beyond end with padding, replacement larger/smaller/same-size, sorted non-overlap fast path, overlapping fallback path, string `S` trailing-NUL preservation, cursor API stats increments, reconstruction from full update and from on-page value, read-uncommitted rollback, prepared rollback races, overflow item retry, and missing base-update assertions. Fuzzing offset/size combinations is valuable because arithmetic and memmove boundaries are central risks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/mtx_rw.c -->
# sources/storage-engines/wiredtiger/src/support/mtx_rw.c

## Purpose
`mtx_rw.c` implements WiredTiger's ticket-based reader/writer lock. It provides shared and exclusive locking with fast paths, queued reader groups, writer ordering, condition-variable fallback, statistics accounting, and ThreadSanitizer synchronization annotations.

## Important APIs, Types, and Functions
The public internal APIs are `__wt_rwlock_init`, `__wt_rwlock_destroy`, `__wt_try_readlock`, `__wt_readlock`, `__wt_readunlock`, `__wt_try_writelock`, `__wt_writelock`, `__wt_writeunlock`, and `__wt_rwlock_islocked`. Static wait predicates `__read_blocked` and `__write_blocked` are used by condition waits. The `WT_RWLOCK` state packs `current`, `next`, `reader`, `readers_queued`, and `readers_active` into one atomically updated 64-bit value.

## Control Flow
Try-read succeeds only when no writer is active or queued for the current ticket and reader count will not overflow. Blocking read first tries the no-writer fast path; if a writer is active, readers queue behind existing writers by sharing `reader = next`, subject to a cap tied to active writers. Queued readers spin, yield, then wait until their ticket becomes current. Writers allocate a unique ticket by incrementing `next`, avoiding wrap into `current`, then wait until their ticket is current and active readers drain. Unlocking a writer advances `current` and, if the next ticket belongs to queued readers, promotes queued readers to active.

## State and Persistence Behavior
Lock state is entirely in memory in `WT_RWLOCK.u.v`, two condition variables, stats-offset fields, and temporary session fields `current_rwlock` and `current_rwticket` during waits. No persistent state is written. Statistics are accumulated in connection and session stats arrays when offsets are configured and stats are enabled.

## Dependencies and Integration Points
The implementation depends on WiredTiger atomic 64-bit CAS/load/store wrappers, condition variables, pause/yield/wait helpers, stat infrastructure, session flags, diagnostic yield hooks, and memory-barrier macros. It is a foundational synchronization primitive for shared WiredTiger subsystems that need read-mostly concurrency with exclusive updates.

## Risks
Correctness depends on reading and CASing the whole 64-bit lock word, because separate field reads can observe mixed batches. The ticket fields are one byte and wrap at 256, so writers must wait when allocation would catch `current`. Reader counts can overflow and must reject or stall new readers. The queued-reader cap is a throughput/fairness tradeoff; incorrect changes can starve writers or destabilize write-heavy workloads. Acquire/release barriers are required because ownership is not established merely by ticket allocation.

## Test Signals
Concurrency tests should cover many readers, writer exclusivity, reader-to-writer handoff, writer-to-reader-group handoff, try-lock failure behavior, ticket wrap pressure, reader count overflow handling, stats increments and wait-time accounting, condition-variable wakeups after spin/yield, and TSan builds. Stress tests should include write-heavy workloads to validate queued-reader limits and fairness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/mtx_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/pow.c -->
# sources/storage-engines/wiredtiger/src/support/pow.c

## Purpose
`pow.c` contains small power-of-two and integer log helpers. It provides active helpers for integer log2, power-of-two testing, and rounding up to a power-of-two multiple, plus optional unused next-largest-power-of-two routines behind `__WIREDTIGER_UNUSED__`.

## Important APIs, Types, and Functions
The active functions are `__wt_log2_int(uint32_t n)`, `__wt_ispo2(uint32_t v)`, and `__wt_rduppo2(uint32_t n, uint32_t po2)`. Optional compiled-out helpers are `__wt_nlpo2_round` and `__wt_nlpo2`, both based on classic bit-hack propagation of the highest set bit.

## Control Flow
`__wt_log2_int` shifts right until the input becomes zero and counts shifts, returning floor log2 for positive inputs. `__wt_ispo2` returns true when `v & (v - 1)` is zero. `__wt_rduppo2` first verifies `po2` with `__wt_ispo2`, computes the shift count, rounds `n` up to the next multiple using shift arithmetic, and asserts no overflow; it returns zero if `po2` is not a power of two.

## State and Persistence Behavior
The functions are pure and maintain no state. They do not allocate, lock, or persist anything.

## Dependencies and Integration Points
The file includes `wt_internal.h` for types, assertions, and build macros. These helpers are used by internal sizing and alignment code that needs cheap integer math without floating point.

## Risks
`__wt_ispo2(0)` returns true by design of the bit expression, and the comment explicitly calls this out. Callers that require positive powers of two must check nonzero separately. `__wt_rduppo2` can produce surprising output for `n == 0` because unsigned arithmetic wraps through `n - 1`; callers should avoid zero unless that behavior is intended. Very large `n` can overflow the rounded result, caught by assertion but still a contract concern in release builds.

## Test Signals
Tests should cover log2 for 0, 1, powers of two, and adjacent values; `__wt_ispo2` for 0, powers, and non-powers; and `__wt_rduppo2` for common alignments, non-power `po2`, already aligned input, just-over-boundary input, zero input, and values near `UINT32_MAX`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/pow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/rand.c -->
# sources/storage-engines/wiredtiger/src/support/rand.c

## Purpose
`rand.c` implements WiredTiger's fast pseudo-random number generation. It uses George Marsaglia's multiply-with-carry generator for 32-bit values, supports deterministic default seeding for skiplist behavior, session-specific random seeding, and Antithesis instrumentation override.

## Important APIs, Types, and Functions
`__wt_random_init_default` initializes a `WT_RAND_STATE` to fixed default seeds. `__wt_random_init_seed` mixes a caller-provided 64-bit seed into the state using circular shifts. `__wt_session_rng_init_once` initializes per-session RNGs on first use: `rnd_skiplist` with the default seed and `rnd_random` with session id, clock, and process id. `__wt_random` produces a 32-bit value and repairs zero components. `__wt_random_init` seeds a new state from a session RNG or from clock and pid when no session exists. `__left_circular_shift64` and `MAKE_SEED` support seed mixing.

## Control Flow
Default initialization writes fixed W/Z constants. Seed initialization creates a mixed 64-bit value from the input and rotated variants, then combines the component fields with default constants. `__wt_random` optionally delegates to `fuzz_get_random` under `ENABLE_ANTITHESIS`; otherwise it copies W and Z locally, replaces zero components with defaults, advances both multiply-with-carry components, stores them back, and returns the combined 32-bit result.

## State and Persistence Behavior
State is the in-memory `WT_RAND_STATE`, either embedded in a session or supplied by a caller. Session RNGs persist for the session lifetime and survive session reset. No persistent random seed is stored on disk.

## Dependencies and Integration Points
The file depends on WiredTiger session state, `__wt_clock`, process id, first-use detection, and optional Antithesis instrumentation. It integrates with skiplist behavior, randomized internal choices, and tests that rely on stable default-seed behavior.

## Risks
The generator is not cryptographically secure. The comments explicitly warn not to change default-seed behavior because existing WiredTiger usage has been validated against it. Concurrent calls may produce duplicate values, which is allowed, but the implementation is careful to avoid corrupting W/Z into unrecoverable zero states by working with local copies. Any new caller that requires strong randomness or cross-thread uniqueness needs a different primitive.

## Test Signals
Tests should include golden sequences for default initialization, seeded sequences for selected seeds, zero-component repair, session first-use initialization, no-session initialization, repeated session reset preserving RNGs, and Antithesis builds returning instrumentation values. Concurrency stress can confirm state does not collapse to permanent zero under races.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/rand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/scratch.c -->
# sources/storage-engines/wiredtiger/src/support/scratch.c

## Purpose
`scratch.c` implements general `WT_ITEM` buffer growth/formatting helpers and per-session scratch-buffer caching. It provides reusable temporary buffers for internal code, printable byte/string formatting, byte-size formatting, and extension scratch allocation/free wrappers.

## Important APIs, Types, and Functions
Buffer helpers include `__wt_buf_grow_worker`, `__wt_buf_fmt`, `__wt_buf_catfmt`, `__wt_buf_set_printable`, `__wt_buf_set_printable_format`, and `__wt_buf_set_size`. Scratch lifecycle APIs include `__wt_scr_alloc_func`, `__wt_scr_discard`, `__wt_ext_scr_alloc`, and `__wt_ext_scr_free`. Diagnostic builds track allocation function and line in `session->scratch_track`.

## Control Flow
`__wt_buf_grow_worker` handles three cases: empty buffers, data already inside `buf->mem`, and data outside the buffer that must be copied local. Formatting helpers grow buffers through the common varargs buffer-format macros. Printable-format conversion tries schema-aware pack unpacking, then falls back to raw printable bytes if the byte string does not match the format. Scratch allocation optionally locks internal sessions, scans for the best free buffer or empty slot, grows the scratch pointer array in chunks of ten when needed, initializes or grows the chosen buffer, marks it in use, and returns it. Discard reports any still-in-use scratch buffers before freeing all scratch memory.

## State and Persistence Behavior
Scratch state lives on `WT_SESSION_IMPL`: `scratch`, `scratch_alloc`, `scratch_cached`, `scratch_lock`, and diagnostic `scratch_track`. Buffers are cached in memory for reuse and freed when the session discards scratch buffers. Extension scratch allocation returns raw `mem` pointers backed by session scratch `WT_ITEM`s.

## Dependencies and Integration Points
The file depends on WiredTiger allocation/reallocation, buffer initialization/free, varargs formatting macros, raw hex helpers, pack/unpack helpers, session flags, spin locks for shared internal sessions, extension API types, and diagnostic logging. It is a broad support dependency because many subsystems need temporary buffers.

## Risks
Scratch buffers are single-owner while marked `WT_ITEM_INUSE`; failure to free them is reported at session discard and can inflate per-session memory. Internal sessions need `scratch_lock` because they may be shared across threads. Extension free searches by raw memory pointer and logs an error for unknown pointers; callers must return exactly the pointer from `__wt_ext_scr_alloc`. `__wt_buf_grow_worker` must preserve `data` offsets correctly for overflow-item buffers where `data` points inside `mem` after a header. Formatted append asserts that existing data is local to the buffer.

## Test Signals
Tests should cover grow with null data, local offset data, external data copy, append formatting, printable fallback after format mismatch, exact and approximate byte-size formatting, scratch reuse choosing the best-sized free buffer, scratch array growth, diagnostic leak reporting, internal-session concurrent scratch allocation, extension alloc/free with default session fallback, and freeing an unknown extension pointer.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/scratch.c -->

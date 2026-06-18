<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_txn.c -->
# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_txn.c

## Purpose
Implements WiredTiger's database and file checkpoint transaction orchestration. It coordinates checkpoint configuration parsing, schema/checkpoint locking, snapshot transaction creation, timestamp selection, data handle selection, per-tree reconciliation, history store checkpointing, metadata checkpointing, log checkpoint records, tiered/disaggregated storage checkpoint metadata, fsync, and failure teardown.

## Important APIs, Types, and Functions
`WT_CHECKPOINT_DB_CONFIG` carries parsed checkpoint options such as `force`, `use_timestamp`, named checkpoint state, checkpoint drops, and flush-tier settings. `WT_PRECISE_CKPT_SAVED_TRIGGERS` saves eviction thresholds modified for precise checkpoint mode. Public/internal entry points include `__wt_checkpoint_db`, `__wt_checkpoint_file`, `__wt_checkpoint_close`, `__wt_checkpoint_sync`, `__wt_checkpoint_get_handles`, `__wt_checkpoint_update_generation`, `__wt_checkpoint_tree_reconcile_update`, `__wt_checkpoint_progress_stats`, `__wt_checkpoint_snapshot_clear`, `__wt_checkpoint_verbose_timer_started`, and `__wt_checkpoint_reset_stats`. The main private stages are `__checkpoint_db_internal`, `__checkpoint_prepare`, `__checkpoint_selected_dhandles`, `__checkpoint_tree`, `__checkpoint_hs`, `__checkpoint_fsync_post`, `__checkpoint_metadata`, and `__checkpoint_teardown`.

## Control Flow
`__wt_checkpoint_db` resets cursors, opens metadata, sets checkpoint session flags, optionally waits for previous flush-tier work, and serializes work with the checkpoint lock before calling `__checkpoint_db_wrapper`. The wrapper publishes `checkpoint_running`, invokes `__checkpoint_db_internal`, then clears the flag and wakes tiered storage. `__checkpoint_db_internal` parses config, skips clean checkpoints when safe, validates named checkpoints, initializes stats, establishes a monotonic wall-clock checkpoint time, updates the global oldest transaction ID, calls data source checkpoints, optionally scrubs dirty cache, logs prepare/start records, raises precise-checkpoint eviction triggers, bumps the checkpoint generation, and under the schema lock calls `__checkpoint_prepare`.

`__checkpoint_prepare` starts a snapshot transaction, enables metadata tracking, marks the connection clean, copies the checkpoint transaction into global checkpoint state, removes its session table entry from ordinary visibility, sets stable-timestamp and disaggregated schema-epoch state, drains commit generation, refreshes the snapshot, prepares a worker snapshot for parallel checkpoints, optionally switches tiered metadata, and gathers checkpoint handles. After prepare, the database path logs start, checkpoints selected dhandles via `__checkpoint_tree_helper`, checkpoints the history store and shared history store, processes disaggregated metadata, updates sysinfo, releases checkpoint snapshots, presyncs handles, fsyncs data files, commits worker and main checkpoint transactions, flushes logs, checkpoints/syncs metadata, updates last checkpoint timestamp and database-size accounting, writes/advances disaggregated checkpoint metadata, and tears down.

`__checkpoint_tree` handles one btree: it may fake checkpoints for original bulk-loadable trees, dirties the root defensively, marks the btree clean with a full barrier, logs per-file checkpoint start, starts the block-manager checkpoint, reconciles/evicts file pages, syncs metadata/standalone cases before metadata update, writes the checkpoint list, resolves the block-manager checkpoint or records a meta-track event, logs stop, marks failures dirty, and saves a postprocessed checkpoint list for reuse.

## State and Persistence Behavior
The file is persistence-critical. It controls when the checkpoint transaction is visible globally, when its snapshot is released, when logs are flushed, when block-manager checkpoint state is resolved, and when metadata/turtle state becomes durable. Timestamped checkpoints save stable timestamp and disaggregated schema epoch into `txn_global`; non-timestamped checkpoints clear last-checkpoint timestamp state. The checkpoint time in `session->ckpt.current_sec` is monotonic relative to connection checkpoint time and tiered flush time. `conn->modified`, `btree->modified`, `btree->checkpoint_gen`, clean-checkpoint timers, checkpoint lists, drop lists, history-store size stats, checkpoint progress stats, and disaggregated database size deltas are all updated here.

Failure handling intentionally differs by storage mode. Classic checkpoints attempt rollback and mark trees dirty for a future checkpoint. Flush-tier failures panic at the top level because block managers may point at incorrect blocks. Disaggregated storage panics if failure occurs after the checkpoint transaction starts, because durable object storage can be ahead of in-memory state and there is no WAL replay contract to repair it.

## Dependencies and Integration Points
This code is tied to transaction visibility (`__wt_txn_begin`, oldest-id update, snapshot bump/release, commit/rollback), schema and checkpoint locks, metadata tracking/cursors, btree data handles, eviction and cache scrub controls, reconciliation (`__wt_sync_file`, `__wt_evict_file`), block-manager checkpoint start/resolve/sync, logging checkpoint records and log fsync, history store checkpointing, tiered storage switching/waiting, hot backup constraints, named checkpoint metadata sysinfo, disaggregated shared metadata queues and checkpoint metadata, key-provider checkpoint metadata, parallel checkpoint workers, statistics, verbose progress, and debug crash/timing stress hooks.

## Risks and Edge Cases
Ordering is the main risk: handle gathering must happen under schema lock after snapshot setup to avoid missing updates or racing schema metadata changes; metadata must be durable before checkpoint resolution; log flushing must cover writes included by eviction; and snapshot release must not happen before required sysinfo/disaggregated metadata work. Clean-tree skip logic must not drop checkpoints needed by hot backup or open checkpoint cursors. Named checkpoint validation prevents unsupported non-file data sources. Timestamped checkpoints assert oldest timestamp is not later than stable timestamp. Parallel checkpoint snapshots must remain read-only and consistent for workers. Any change in disaggregated root-page semantics affects early checkpoint resolve and root-page discard. Close/file checkpoint paths have narrower locking and metadata tracking rules than full database checkpoints.

## Test Signals
Relevant tests include Python checkpoint suites such as `test_checkpoint07.py` for clean checkpoint skip timers, `test_checkpoint15.py`, `test_checkpoint17.py`, `test_checkpoint25.py`, and `test_checkpoint31.py` for timestamped checkpoint behavior, layered/disaggregated checkpoint tests such as `test_layered_checkpoint04.py`, `test_layered_checkpoint07.py`, and `test_layered_checkpoint08.py`, and checkpoint cleanup tests under `test_cc*.py`. `test/catch2/misc_tests/test_checkpoint_skip.cpp` directly exercises `__ut_checkpoint_skip_ckptlist`. Format tests drive named checkpoints, hot backup interactions, flush-tier checkpoints, and stress flags. Crash-point and timing-stress options in this file are explicit regression hooks for recovery ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_txn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/arm64/crc32-arm64.c -->
# sources/storage-engines/wiredtiger/src/checksum/arm64/crc32-arm64.c

## Purpose
Provides the ARM64 CRC32C dispatch implementation. On Linux builds with hardware CRC enabled, it detects `HWCAP_CRC32` and returns functions that use ARM CRC32 instructions; otherwise it returns WiredTiger's software CRC32C routines.

## Important APIs, Types, and Functions
The exported symbols are `wiredtiger_crc32c_func(void)` and `wiredtiger_crc32c_with_seed_func(void)`, both declared with default visibility under GCC. Hardware helpers are `__checksum_hw` and `__checksum_with_seed_hw`. Inline assembly macros `CRC32CX`, `CRC32CW`, `CRC32CH`, and `CRC32CB` issue 64-bit, 32-bit, 16-bit, and 8-bit ARM CRC32C instructions. External fallbacks are `__wt_checksum_sw` and `__wt_checksum_with_seed_sw`.

## Control Flow
`wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func` cache the chosen function pointer in a static local. On first call they read `getauxval(AT_HWCAP)` and choose the hardware helper only when `HWCAP_CRC32` is present. The hardware seeded helper starts with `~seed`, processes two 64-bit words per loop with `memcpy` loads, then handles remaining 8-, 4-, 2-, and 1-byte fragments according to the remaining length bits, and returns the complemented CRC. The unseeded helper calls the seeded helper with seed zero.

## State and Persistence Behavior
The only state is the process-local cached function pointer. There is no persistence, allocation, or WiredTiger session state. The function choice affects all block/page checksum persistence indirectly because callers use the returned CRC32C function when writing and validating on-disk checksums.

## Dependencies and Integration Points
This file depends on `wiredtiger_config.h`, Linux `getauxval`, `asm/hwcap.h`, compiler inline assembly support, and the software checksum implementation. It integrates with the global checksum API used by block writes, block reads, disaggregated page checks, examples, and tests through `wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func`.

## Risks and Edge Cases
Hardware dispatch is Linux-only and can be disabled with `HAVE_NO_CRC32_HARDWARE`. The static pointer cache is intentionally unsynchronized; concurrent first calls may repeat detection but should converge on the same function. `memcpy` avoids unaligned-load undefined behavior. Correctness depends on seed complement semantics matching software and other architecture implementations. Zero-length seeded calls must return the seed.

## Test Signals
`test/catch2/misc_tests/test_crc32.cpp` verifies zero-length and seeded behavior plus known CRC values and chunked seeded computation. `test/csuite/wt2695_checksum/main.c` compares hardware dispatch against `__wt_checksum_sw` across known strings, all-zero/all-0xff data, random data, cumulative chunking, and misalignment cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/arm64/crc32-arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/loongarch64/crc32-loongarch64.c -->
# sources/storage-engines/wiredtiger/src/checksum/loongarch64/crc32-loongarch64.c

## Purpose
Provides the LoongArch64 architecture dispatch shim for WiredTiger CRC32C. In this implementation it always selects the portable software checksum routines.

## Important APIs, Types, and Functions
The exported symbols are `wiredtiger_crc32c_func(void)` and `wiredtiger_crc32c_with_seed_func(void)`, with GCC default visibility when available. They return external software implementations `__wt_checksum_sw` and `__wt_checksum_with_seed_sw`.

## Control Flow
Both dispatch functions are direct returns with no runtime feature checks, static cache, allocation, or architecture-specific computation. The unseeded API returns the software function accepting `(const void *, size_t)`. The seeded API returns the software function accepting `(uint32_t, const void *, size_t)`.

## State and Persistence Behavior
This file has no mutable state. Its persisted-data impact is indirect: LoongArch64 builds produce and validate WiredTiger CRC32C values through the common software implementation, preserving on-disk checksum compatibility with other architectures.

## Dependencies and Integration Points
It depends on `wiredtiger_config.h`, integer and size types, and the software checksum object. It satisfies the same exported checksum dispatch contract used by block manager writes/reads, recovery verification, tools, examples, and checksum tests.

## Risks and Edge Cases
The main risk is performance, not correctness: hardware support is not used even if a LoongArch64 platform exposes CRC acceleration. ABI compatibility depends on the exported function signatures and visibility matching other architecture shims. Any change to software seeded semantics must remain compatible with this dispatch file.

## Test Signals
The generic CRC tests exercise this path on LoongArch64: `test_crc32.cpp` checks zero-length, known-value, and chunked seeded behavior, while `wt2695_checksum` compares the selected checksum path with the software implementation across random data and misalignment cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/loongarch64/crc32-loongarch64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/clang_workaround.h -->
# sources/storage-engines/wiredtiger/src/checksum/power8/clang_workaround.h

## Purpose
Provides compatibility wrappers that let the POWER8 vector CRC implementation compile under Clang despite differences from GCC vector builtins and historical `vec_xxpermdi` behavior.

## Important APIs, Types, and Functions
The header maps missing `__builtin_crypto_vpmsumw` and `__builtin_crypto_vpmsumd` to `__builtin_crypto_vpmsumb`, defines an overloadable `vec_ld` wrapper using `__builtin_altivec_lvx`, provides `__builtin_pack_vector`, and provides `__builtin_unpack_vector_0` and, when `REFLECT` is not defined, `__builtin_unpack_vector_1`. For older Clang or missing `vec_xxpermdi`, unpacking uses vector indexing with endian-aware macros; newer Clang uses `vec_xxpermdi`.

## Control Flow
This is a compile-time adaptation layer. `vec_crc32.c` includes it only when `__clang__` is defined. Preprocessor branches select big-endian versus little-endian packing order and older versus newer Clang unpack implementations.

## State and Persistence Behavior
The header has no runtime state or persistence. It affects checksum persistence indirectly by ensuring Clang-built POWER8 CRC code performs the same vector lane packing and unpacking as the GCC path.

## Dependencies and Integration Points
It depends on AltiVec vector types and Clang/GCC-compatible builtin names. It is tightly coupled to `vec_crc32.c`, especially the reflected CRC mode controlled by `REFLECT` from `crc32_constants.h`.

## Risks and Edge Cases
Endian handling is delicate: incorrect lane order would silently generate incompatible CRC values. The fallback mapping of vpmsum builtins assumes Clang accepts the byte builtin for the required vector polynomial operations. Clang version checks around `vec_xxpermdi` are compatibility-sensitive; future compiler changes could require updating this header.

## Test Signals
POWER8 builds with Clang should pass the generic CRC tests. `wt2695_checksum` is particularly important because it compares hardware/vector output with software output for known values, random chunks, cumulative seeded checksums, and 0-15 byte misalignment patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/clang_workaround.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/crc32_constants.h -->
# sources/storage-engines/wiredtiger/src/checksum/power8/crc32_constants.h

## Purpose
Contains generated constants for the POWER8 vector CRC32C implementation. The file is generated from the `crc32-vpmsum` tooling for reflected CRC32C polynomial `0x1edc6f41` with final XOR enabled and a maximum folding block size of 32768 bytes.

## Important APIs, Types, and Functions
This header defines `CRC`, `CRC_XOR`, `REFLECT`, and `MAX_SIZE`. Under `CRC_TABLE`, it provides `crc_table[]` for byte-at-a-time alignment and tail handling. Under `POWER8_INTRINSICS`, it provides aligned vector tables `vcrc_const[255]` for large-block folding, `vcrc_short_const[16]` for short and tail reductions, and `v_Barrett_const[2]` for final Barrett reduction. The vector tables have endian-specific lane ordering.

## Control Flow
There is no executable control flow. Consumers compile in different constant sets via `CRC_TABLE` and `POWER8_INTRINSICS`. `vec_crc32.c` defines both before including this header, using `crc_table` in `crc32_align`, the long and short vector constants in `__crc32_vpmsum`, and `v_Barrett_const` during final polynomial reduction.

## State and Persistence Behavior
All data is static constant state. The constants define the actual CRC32C polynomial arithmetic used to persist and verify block checksums on POWER8 hardware builds. They must remain bit-for-bit compatible with software CRC32C and other architecture implementations.

## Dependencies and Integration Points
The header is private to the POWER8 checksum implementation and assumes AltiVec vector types when `POWER8_INTRINSICS` is defined. It integrates with `vec_crc32.c` and, through `crc32_wrapper.c`, with the exported WiredTiger checksum dispatch API.

## Risks and Edge Cases
The file explicitly says it is generated and should not be edited manually. Risks include accidental table corruption, regenerating with the wrong polynomial/reflection/XOR settings, or breaking endian-specific ordering. Because checksum values are persisted in block headers and address cookies, a constants mismatch is a data-compatibility bug rather than a local performance issue.

## Test Signals
The strongest validation is cross-checking this POWER8 path against `__wt_checksum_sw` in `wt2695_checksum`, including known CRC32C vectors, seeded cumulative checksums, random data, and misalignment. `test_crc32.cpp` also verifies known values and chunked seeded behavior through the public dispatch API.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/crc32_constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/crc32_wrapper.c -->
# sources/storage-engines/wiredtiger/src/checksum/power8/crc32_wrapper.c

## Purpose
Provides the POWER8 checksum dispatch wrapper. On `__powerpc64__` builds with hardware CRC enabled, it returns wrappers around the vector polynomial multiply-sum implementation; otherwise it falls back to the portable software CRC32C functions.

## Important APIs, Types, and Functions
The file declares `crc32_vpmsum(unsigned int crc, const unsigned char *p, unsigned long len)` from `vec_crc32.c`. Hardware wrappers `__checksum_hw` and `__checksum_with_seed_hw` adapt that function to WiredTiger's unseeded and seeded CRC signatures. Exported dispatch functions are `wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func`.

## Control Flow
The dispatch functions use compile-time selection only. If the build target is POWER64 and hardware CRC is not disabled, they return the vector wrappers. Otherwise they return `__wt_checksum_sw` and `__wt_checksum_with_seed_sw`. There is no runtime CPU feature probe or cached function pointer.

## State and Persistence Behavior
No mutable state exists in this wrapper. It determines which implementation produces persisted CRC32C values for block writes and validates those values on reads. Compatibility relies on `crc32_vpmsum` matching the software algorithm for all seeds and lengths.

## Dependencies and Integration Points
It depends on `wiredtiger_config.h`, the POWER8 vector implementation, and software checksum routines. It is the exported bridge between architecture-specific code in `src/checksum/power8` and the rest of WiredTiger's checksum API.

## Risks and Edge Cases
Compile-time selection assumes POWER64 builds that include this hardware path run on processors supporting the required vector crypto instructions. Unlike ARM64, there is no runtime HWCAP gate here. Signature adaptation must preserve seeded semantics, especially zero-length input returning the seed. Build configuration must exclude this path when hardware support is unavailable.

## Test Signals
`wt2695_checksum` validates the selected function against software over known vectors, random data, seeded cumulative chunks, and misalignment. `test_crc32.cpp` validates the public dispatch API and chunked seeded computation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/crc32_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/vec_crc32.c -->
# sources/storage-engines/wiredtiger/src/checksum/power8/vec_crc32.c

## Purpose
Implements the POWER8 hardware-accelerated CRC32C algorithm using AltiVec/crypto vector builtins and the generated constants in `crc32_constants.h`. It handles unaligned prefixes/tails in scalar code, folds aligned data in vector lanes, and performs final Barrett reduction.

## Important APIs, Types, and Functions
The exported function is `crc32_vpmsum(unsigned int crc, const unsigned char *p, unsigned long len)`. Private helpers include scalar `crc32_align` and aligned vector reducer `__crc32_vpmsum`. Important macros/constants include `VMX_ALIGN`, `VMX_ALIGN_MASK`, `POWER8_INTRINSICS`, `CRC_TABLE`, `GROUP_ENDING_NOP`, `BYTESWAP_DATA`, `VEC_PERM`, and the included `crc_table`, `vcrc_const`, `vcrc_short_const`, and `v_Barrett_const`.

## Control Flow
`crc32_vpmsum` applies the optional initial XOR, uses `crc32_align` for small inputs or unaligned prefixes, calls `__crc32_vpmsum` for the aligned 16-byte multiple, handles the remaining tail with `crc32_align`, then applies the final XOR. `__crc32_vpmsum` has a short path for inputs under 256 bytes that uses `vcrc_short_const`, and a long path that processes data in up to `MAX_SIZE` blocks, folding eight parallel 128-bit chunks to mask vpmsum latency. After long-block processing it reduces tail data, xors parallel lanes together, and performs reflected Barrett reduction to a 32-bit CRC result.

## State and Persistence Behavior
The implementation is stateless. It directly determines CRC32C values stored in WiredTiger block headers and address cookies on POWER8 hardware builds. Seeded operation is provided by passing the prior CRC into `crc32_vpmsum`, so chunked checksums must equal one-shot checksums.

## Dependencies and Integration Points
This file compiles only for `__powerpc64__` when hardware CRC is enabled. It depends on `altivec.h`, compiler vector crypto builtins, `crc32_constants.h`, and `clang_workaround.h` for Clang. `crc32_wrapper.c` exposes it through `wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func`.

## Risks and Edge Cases
The algorithm is sensitive to alignment, endian/reflection handling, vector lane ordering, and polynomial constants. The scalar prefix/tail path must match vector folding exactly. The long loop uses modulo scheduling and `GROUP_ENDING_NOP` to avoid POWER8 load-hit-store dispatch penalties; compiler changes can affect generated code. Inputs around 0, 1-15 bytes, 16-byte alignment boundaries, 128/256-byte thresholds, and `MAX_SIZE` block boundaries are important edge cases.

## Test Signals
`wt2695_checksum` is the key regression signal because it compares hardware/vector and software CRC values for fixed vectors, all-zero/all-ones inputs, random power-of-two and random sizes, cumulative seeded chunks, and every small length/misalignment combination under 16 bytes. `test_crc32.cpp` verifies zero-length seeded semantics, known CRC32C values, and chunked computation through the dispatch wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/vec_crc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/riscv64/crc32-riscv64.c -->
# sources/storage-engines/wiredtiger/src/checksum/riscv64/crc32-riscv64.c

## Purpose
Provides the RISC-V 64-bit architecture dispatch shim for WiredTiger CRC32C. This implementation always selects the portable software checksum routines.

## Important APIs, Types, and Functions
The exported symbols are `wiredtiger_crc32c_func(void)` and `wiredtiger_crc32c_with_seed_func(void)`, with GCC default visibility where supported. They return `__wt_checksum_sw` and `__wt_checksum_with_seed_sw`.

## Control Flow
Both exported functions are direct fallbacks. There is no runtime feature detection, hardware intrinsic use, static caching, or local checksum loop.

## State and Persistence Behavior
The file has no mutable state or direct persistence logic. Its choice of software CRC affects persisted block checksums only by routing RISC-V builds through the shared portable algorithm, preserving cross-platform checksum compatibility.

## Dependencies and Integration Points
It depends on the common WiredTiger configuration header, standard integer/size types, and software checksum symbols. It satisfies the architecture-specific checksum dispatch contract consumed by block write/read paths, tools, examples, and tests.

## Risks and Edge Cases
The primary risk is missing hardware acceleration on RISC-V platforms that may support CRC extensions. Correctness depends on the software implementation and on maintaining ABI-compatible exported function signatures. Seeded zero-length and chunked checksum behavior are inherited from `__wt_checksum_with_seed_sw`.

## Test Signals
Generic checksum tests cover this dispatch on RISC-V builds. `test_crc32.cpp` checks zero-length, known vectors, and seeded chunking, while `wt2695_checksum` compares selected checksum behavior with software over known, random, cumulative, and misaligned inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/riscv64/crc32-riscv64.c -->

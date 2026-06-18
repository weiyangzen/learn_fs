# subset-b-009223 Research

Grouped research for fio files under `sources/test-tools/fio`. Each file section preserves the source path in its title and is bounded for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/sha512.c -->
# sources/test-tools/fio/crc/sha512.c

Purpose: Implements fio's local SHA-512 hashing routine, adapted from GPL SHA-512 code, for verification/hash benchmark paths that should not depend on an external crypto library.

Important APIs/functions: Exports `fio_sha512_init()`, `fio_sha512_update()`, and `fio_sha512_final()`. Internal helpers implement SHA-512 primitives: `Ch`, `Maj`, `RORuint64_t`, `e0/e1/s0/s1`, `sha512_transform()`, `LOAD_OP()`, and `BLEND_OP()`. The transform uses the 80-round SHA-512 schedule and constants, loading big-endian 64-bit words through `__be64_to_cpu`.

Control flow: `fio_sha512_init()` seeds the eight hash state words and clears the 128-bit bit count. `fio_sha512_update()` tracks bit length, fills a 128-byte partial block, processes full blocks through `sha512_transform()`, and leaves trailing bytes in `sctx->buf`. `fio_sha512_final()` serializes the saved bit count, applies SHA padding to reach 112 mod 128, appends the 16-byte length, then writes the final 64-byte digest into `sctx->buf`.

State/persistence: All mutable hash state lives in caller-owned `struct fio_sha512_ctx`; the digest is written into the caller-provided buffer pointer in that context. No global mutable state or persistence is used.

Dependencies/integration: Depends on `../lib/bswap.h` for endian conversion and `sha512.h` for the context contract. Used by fio verification/checksum code and by `crc/test.c` performance benchmarking.

Risks: The context requires a non-null `buf` large enough for at least 128 bytes because it is used both as a block buffer and output buffer. `fio_sha512_update()` accepts `unsigned int len`, so very large inputs must arrive in chunks. The `LOAD_OP()` cast may rely on alignment behavior; portability depends on compiler/platform tolerance or upstream assumptions. The unused SHA-384 constants are dead weight in this file.

Test signals: Known SHA-512 vectors and multi-update boundary tests around 111/112/127/128 bytes are the key correctness signals. The fio checksum benchmark can exercise throughput but does not itself validate digest values.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/sha512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/sha512.h -->
# sources/test-tools/fio/crc/sha512.h

Purpose: Declares fio's SHA-512 context and three-step hashing API.

Important APIs/types: `struct fio_sha512_ctx` contains `state[8]`, a four-word bit counter `count[4]`, caller-owned `uint8_t *buf`, and `W[80]` message schedule scratch. Functions are `fio_sha512_init()`, `fio_sha512_update()`, and `fio_sha512_final()`.

Control flow: Callers allocate a context, set `ctx.buf` to a suitable digest/block buffer, call init, then update zero or more times, then final. The header does not expose digest size constants, so callers infer buffer requirements from implementation or surrounding code.

State/persistence: The context is fully caller-owned and can be stack or heap allocated. No allocations are performed by the API.

Dependencies/integration: Includes `<inttypes.h>` for fixed-width integer types. Integrated by checksum, verification, and `crc/test.c`.

Risks: The `buf` pointer is part of the context instead of embedded storage; callers that forget to initialize it or provide fewer than 128 bytes can corrupt memory. The API mutates the context during finalization, so it is not reusable for further updates without reinitialization.

Test signals: Compile-time consumers should verify `struct fio_sha512_ctx` is initialized with a valid `buf`; runtime tests should cover one-shot and chunked hashing.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/sha512.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/test.c -->
# sources/test-tools/fio/crc/test.c

Purpose: Implements `fio_crctest()`, fio's checksum/hash throughput benchmark for built-in CRC, cryptographic hash, and non-cryptographic hash implementations.

Important APIs/functions: Defines `struct test_type` with name, selection mask, benchmark function, and accumulator. Benchmark functions include `t_md5`, `t_crc64`, `t_crc32`, `t_crc32c`, `t_crc16`, `t_crc7`, `t_sha1`, `t_sha256`, `t_sha512`, `t_xxhash`, `t_murmur3`, `t_jhash`, `t_fnv`, and SHA3 variants. `get_test_mask()` parses comma-separated names. `list_types()` prints available algorithms. `fio_crctest()` is the public entry point.

Control flow: `fio_crctest()` probes accelerated CRC32C implementations, derives a mask from the requested type or selects all, allocates a 128 KiB buffer, fills it with deterministic random data, warms the CPU/data path on the first selected test, then times each selected function over 2048 chunks and prints MiB/s. Each function loops over `NR_CHUNKS`; streaming hashes use their context APIs while simple CRC/hash functions accumulate a result to discourage optimization.

State/persistence: Uses stack contexts and one heap buffer. `struct test_type.output` persists across runs in the static table and can accumulate if `fio_crctest()` is invoked more than once in-process.

Dependencies/integration: Pulls fio time utilities, random buffer generation, and every local checksum header. Integrated through the fio command path that exposes CRC test/list behavior.

Risks: Several streaming hash benchmark loops initialize/finalize outside or inside loops inconsistently; this is a throughput exerciser, not a digest correctness test. `malloc(CHUNK)` is not checked before filling. `get_test_mask()` ignores unknown comma elements unless the aggregate mask is zero. Static `output` is not reset per invocation.

Test signals: Expected signals are successful listing, nonzero throughput for every algorithm, and no crashes under ASAN/UBSAN. Digest correctness needs separate known-vector tests.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/test.h -->
# sources/test-tools/fio/crc/test.h

Purpose: Provides the small public declaration for fio's checksum benchmark command.

Important APIs/types: Exports `int fio_crctest(const char *type);`, where `type` is null for all algorithms, `help`/`list` for names, or a comma-separated subset.

Control flow: Consumers include the header and dispatch to `fio_crctest()`; all parsing and printing are handled in `test.c`.

State/persistence: No state is declared here.

Dependencies/integration: Guarded by `FIO_CRC_TEST_H`; consumed by fio command-line/test plumbing.

Risks: The header does not describe accepted names or side effects, so callers must rely on `test.c` behavior.

Test signals: A build that includes the benchmark should link exactly one `fio_crctest()` implementation and expose list/help behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/xxhash.c -->
# sources/test-tools/fio/crc/xxhash.c

Purpose: Vendor-style implementation of 32-bit xxHash for fast, deterministic, non-cryptographic hashing inside fio.

Important APIs/functions: Implements `XXH32()`, `XXH32_init()`, `XXH32_update()`, `XXH32_digest()`, `XXH32_intermediateDigest()`, `XXH32_sizeofState()`, and `XXH32_resetState()`. Internal helpers cover endian detection, unaligned reads, byte swapping, rotations, the block mixing loop, and final avalanche.

Control flow: One-shot `XXH32()` dispatches to `XXH32_endian_align()` with endianness and alignment policy. Streaming mode allocates or accepts a `struct XXH_state32_t`, initializes accumulators from the seed, buffers less than 16 bytes in `memory`, mixes 16-byte stripes into four lanes, and finalizes by folding lanes plus remaining 4-byte and 1-byte tails. `XXH32_digest()` computes the intermediate digest and frees heap state created by `XXH32_init()`.

State/persistence: Streaming state holds total length, seed, four accumulators, a small tail buffer, and `memsize`. Heap allocation is used only by `XXH32_init()`; static allocation is supported through the header state-space API.

Dependencies/integration: Includes `xxhash.h`, `stdlib.h`, and `string.h`. Used by fio's hash/checksum paths and the CRC benchmark.

Risks: `XXH32_init()` does not check `malloc()` before resetting state. Update length is signed `int`; negative values would corrupt `total_len` and pointer arithmetic if misused. Optional null-input handling is disabled, so null pointers with nonzero length fault. Some unaligned/aligned compile-time branches are subtle and architecture-sensitive.

Test signals: SMHasher-style vectors, one-shot versus streaming equivalence across chunk boundaries, endian cross-checks, and state-space allocation tests provide confidence. Fio `crc/test.c` exercises performance only.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/xxhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/xxhash.h -->
# sources/test-tools/fio/crc/xxhash.h

Purpose: Declares the embedded xxHash 32-bit API and streaming state layout.

Important APIs/types: Defines `struct XXH_state32_t`, `XXH_errorcode`, one-shot `XXH32()`, heap streaming API `XXH32_init/update/digest`, caller-allocated state API `XXH32_sizeofState()` and `XXH32_resetState()`, `XXH32_stateSpace_t`, and deprecated macro aliases.

Control flow: Callers either hash a single buffer with `XXH32()` or initialize state, feed packets with `XXH32_update()`, optionally sample `XXH32_intermediateDigest()`, and finish/free with `XXH32_digest()`.

State/persistence: The state structure is public and can be stack allocated, but callers must preserve its contents between updates. `XXH32_digest()` frees heap states and must not be used on stack state unless the caller intentionally allocated compatible heap memory.

Dependencies/integration: Includes `<inttypes.h>` and supports C++ linkage. Used by local fio checksum consumers.

Risks: Public exposure of the internal state makes ABI drift risky. `XXH32_SIZEOFSTATE` must remain large enough; the implementation asserts this at compile time. Documentation says some lengths are limited by `int` although the one-shot prototype uses `uint32_t`.

Test signals: Compile tests should validate both heap and stack state modes; runtime tests should compare intermediate digest preservation with continued updates.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/xxhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/dataplacement.c -->
# sources/test-tools/fio/dataplacement.c

Purpose: Implements fio data placement support for Flexible Data Placement (FDP) and streams, mapping write IOs to placement identifiers through random, round-robin, or scheme-file policies.

Important APIs/functions: Public functions are `dp_init()`, `fdp_free_ruhs_info()`, and `dp_fill_dspec_data()`. Internal helpers `fdp_ruh_info()`, `init_ruh_info()`, and `init_ruh_scheme()` fetch or construct reclaim unit handle information and optional offset-to-PLI schemes.

Control flow: `dp_init()` walks each file in a thread. For streams mode, `init_ruh_info()` builds `fio_ruhs_info` directly from user-supplied stream IDs. For FDP, it asks the IO engine's `fdp_fetch_ruhs` callback for the RUH count, reallocates to include PLIs, fetches the full list, validates optional user-selected indices, and stores a reduced PLI list on the file. If scheme selection is enabled, `init_ruh_scheme()` reads CSV lines of `start,end,pli` into a fixed-size scheme array. During each IO, `dp_fill_dspec_data()` clears non-write or uninitialized IOs; otherwise it selects a PLI by round-robin, scheme match, or random selection and writes `io_u->dtype`/`dspec`.

State/persistence: Placement metadata is per `fio_file` in `ruhs_info` and `ruhs_scheme`. Round-robin position is mutable in `pli_loc`; random selection uses `td->fdp_state`.

Dependencies/integration: Requires fio thread/file/io_u structures, engine support for `fdp_fetch_ruhs`, shared allocation helpers, and logging/debug channels. The selected fields are consumed by engines that translate `dtype/dspec` into device directives.

Risks: Scheme parsing is permissive and lacks range-order validation. `fdp_free_ruhs_info()` returns early when `ruhs_info` is null, leaving `ruhs_scheme` allocated if that impossible-looking split state occurs. FDP index validation treats user IDs as indices into fetched PLIs, not raw PLIs, which must match documentation.

Test signals: Tests should cover streams without IDs rejection, FDP engines without fetch callback, selected index bounds, max PLI clamping, scheme default-to-zero, and write-only directive population.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/dataplacement.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/dataplacement.h -->
# sources/test-tools/fio/dataplacement.h

Purpose: Defines fio data placement constants, selection modes, state structures, and public functions.

Important APIs/types: Constants include `STREAMS_DIR_DTYPE`, `FDP_DIR_DTYPE`, `FIO_MAX_DP_IDS`, and `DP_MAX_SCHEME_ENTRIES`. Mode enums define random/round-robin/scheme selection and none/FDP/streams placement type. Structures are `fio_ruhs_info`, `fio_ruhs_scheme_entry`, and `fio_ruhs_scheme`. Public APIs mirror `dataplacement.c`.

Control flow: Headers provide contracts for initialization, cleanup, and per-IO directive fill; callers must call `dp_init()` before `dp_fill_dspec_data()` can attach directives.

State/persistence: `fio_ruhs_info` uses a flexible array for PLIs and tracks current round-robin position. Scheme state is a fixed array of at most 32 entries.

Dependencies/integration: Includes `io_u.h`, so it participates directly in fio IO unit definitions.

Risks: `FIO_MAX_DP_IDS` and `DP_MAX_SCHEME_ENTRIES` are fixed compile-time caps. The flexible array requires careful allocation sizing by users.

Test signals: Compile-time integration should ensure `fio_file` and `io_u` users agree on these structures; runtime tests should exercise all selection modes.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/dataplacement.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/debug.c -->
# sources/test-tools/fio/debug.c

Purpose: Provides the debug print implementation when fio is built with `FIO_INC_DEBUG`.

Important APIs/functions: Defines `__dprint(int type, const char *str, ...)`, which asserts the debug channel is valid and forwards the formatted varargs to `log_prevalist()`.

Control flow: The `dprint` macro in `debug.h` checks the runtime bitmask, then calls `__dprint()` only for enabled categories. This file is compiled to real behavior only under `FIO_INC_DEBUG`.

State/persistence: No local state. It consumes global debug mask state declared elsewhere and writes to fio logging.

Dependencies/integration: Includes `debug.h` and `log.h`. Every fio subsystem using `dprint()` depends on this contract in debug builds.

Risks: The assert catches invalid channel numbers only in assert-enabled builds. Format-string safety is declared in the header, not here.

Test signals: Debug builds should verify each channel emits when enabled and remains silent when disabled; non-debug builds should compile away calls.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/debug.h -->
# sources/test-tools/fio/debug.h

Purpose: Defines fio debug categories, warning-once helpers, and the `dprint()` interface.

Important APIs/types: The debug enum spans categories such as file, io, diskutil, job, time, network, zbd, and `FD_DEBUG_MAX`. Externs include `fio_debug_jobno`, `fio_debug_jobp`, and `fio_warned`. `fio_did_warn()` sets warning bits. Warning masks include root flush, verify buffer, zoned bug, iolog drop, fadvise, and btrace zero. In debug builds it declares `struct debug_level`, `debug_levels`, `fio_debug`, `__dprint()`, and a filtering macro; otherwise `dprint()` is an empty inline.

Control flow: Runtime code calls `dprint(category, ...)`; debug builds test `fio_debug` and forward to logging, while normal builds discard the call.

State/persistence: Warning bits are global through `fio_warned`; debug mask/job selection are global. `fio_did_warn()` mutates the shared warning mask.

Dependencies/integration: Includes fio boolean types and is widely included across the codebase.

Risks: `fio_did_warn()` assumes `fio_warned` is initialized. Warning bit allocation is manual and can collide if extended carelessly. Non-debug builds still type-check only the inline signature, not format strings.

Test signals: Unit or integration tests should verify warning-once behavior and debug category filtering with `FIO_INC_DEBUG`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/dedupe.c -->
# sources/test-tools/fio/dedupe.c

Purpose: Initializes deterministic seed arrays used by fio's dedupe working-set data generation mode, including optional global dedupe across jobs.

Important APIs/functions: `init_global_dedupe_working_set_seeds()` iterates all thread jobs that request global dedupe. `init_dedupe_working_set_seeds(struct thread_data *td, bool global_dedup)` allocates and fills `td->dedupe_working_set_states`.

Control flow: The per-thread initializer exits unless dedupe percentage is set and mode is `DEDUPE_MODE_WORKING_SET`. It computes how many RNG advancements correspond to one write block, derives the number of unique pages from job size and working-set percentage, allocates an array of `frand_state`, copies the thread buffer state as the first seed, then advances and records seeds for each unique page. In global mode it periodically switches the source seed to another thread's `buf_state` so duplicate buffers can span jobs.

State/persistence: Persists allocated seed arrays and `num_unique_pages` on `thread_data`. The global initializer relies on all jobs' seeds already being initialized.

Dependencies/integration: Uses fio job iteration, random state helpers, compression chunk sizing, block size options, and global `thread_number`/`tnumber_to_td()`.

Risks: If `num_unique_pages` computes to zero, the code allocates zero bytes then writes index zero, which is a likely bug for tiny sizes or zero percentages after integer truncation. Global distribution depends on stable thread numbering and initialized `buf_state`. Memory cleanup is outside this file.

Test signals: Test tiny jobs, compression chunk interactions, single-thread and multi-thread global dedupe, and deterministic repeatability of generated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/dedupe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/dedupe.h -->
# sources/test-tools/fio/dedupe.h

Purpose: Declares dedupe working-set seed initialization helpers.

Important APIs/types: Exports `init_dedupe_working_set_seeds(struct thread_data *td, bool global_dedupe)` and `init_global_dedupe_working_set_seeds(void)`.

Control flow: The caller initializes per-job or global dedupe state after job seeds are available and before data generation that needs the working set.

State/persistence: No state is declared in the header; state is stored in `thread_data`.

Dependencies/integration: Relies on `struct thread_data` and `bool` from fio headers included before this header.

Risks: The header does not include its own type dependencies, so include order matters.

Test signals: Build tests should include it from typical fio compilation units; runtime tests should validate seed setup before workload start.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/dedupe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/diskutil.c -->
# sources/test-tools/fio/diskutil.c

Purpose: Tracks Linux block device utilization for fio jobs by mapping files to sysfs block devices and periodically accumulating `/sys/block/.../stat` counters.

Important APIs/functions: Public functions are `setup_disk_util()`, `init_disk_util()`, `update_io_ticks()`, and `disk_util_prune_entries()`. Internal helpers locate devices (`get_device_numbers()`, `find_block_dir()`, `read_block_dev_entry()`), add devices and slaves (`disk_util_add()`, `find_add_disk_slaves()`), read stats (`get_io_ticks()`), handle 32-bit stat wrap (`safe_32bit_diff()`), and update accumulated counters (`update_io_tick_disk()`).

Control flow: `setup_disk_util()` creates a global semaphore. `init_disk_util()` skips diskless/nodiskutil jobs, then maps each file to a `disk_util`. Mapping stats the file or parent directory, finds a matching sysfs block directory, normalizes partitions to parent queues, creates a `disk_util`, snapshots initial stats, adds it to global `disk_list`, and recursively adds slave devices. The helper thread calls `update_io_ticks()`, which locks the list, skips work during shutdown, reads each active device's stat file, accumulates deltas, and updates elapsed msec. Prune removes all entries and semaphore state.

State/persistence: Maintains global `disk_list`, a global semaphore, and a last major/minor lookup cache. Each `disk_util` stores sysfs paths, last and accumulated stats, slave links, a per-device lock, timestamps, and user count.

Dependencies/integration: Linux-specific sysfs, fio semaphores, helper thread shutdown, fio file/job iteration, smalloc/sfree, debug logging, and optional Valgrind DRD annotations.

Risks: Extensive path manipulation uses fixed buffers and some `sprintf` calls. Sysfs layout assumptions may fail for unusual devices. Slave discovery increments users and attaches slave list entries; lifetime/refcount correctness is sensitive. `disk_util_mod()` takes an int delta but applies it to unsigned users, so unmatched decrements can underflow.

Test signals: Tests should cover regular files, block devices, missing files, partitions, device-mapper/slave devices, helper shutdown, 32-bit counter wrap, and disabled diskutil engines.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/diskutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/diskutil.h -->
# sources/test-tools/fio/diskutil.h

Purpose: Declares disk utilization data structures, inline user-count helpers, and feature-gated public APIs.

Important APIs/types: Defines `disk_util_stats`, `disk_util_stat`, `disk_util_agg`, and `disk_util`. Inline helpers `disk_util_mod()`, `disk_util_inc()`, and `disk_util_dec()` mutate active-user counts for a device and its slaves. `DISK_UTIL_MSEC` sets the polling interval. `disk_list` is extern.

Control flow: Jobs call increment/decrement helpers around active device use; the helper thread consumes public update/prune/setup/init APIs when `FIO_HAVE_DISK_UTIL` is enabled. Disabled builds compile to no-ops, with `update_io_ticks()` returning `helper_should_exit()`.

State/persistence: Per-device state stores sysfs root, stat path, major/minor, accumulated and last counters, aggregate fields, slave lists, timestamp, lock, and users.

Dependencies/integration: Requires fio helper thread, semaphores, flist, and fio's IEEE754 wrapper for aggregated utilization.

Risks: Inline mutation of slave users happens while holding only the master lock, not each slave lock. Feature-gated no-ops mean callers must tolerate absence of disk utilization.

Test signals: Compile both enabled and disabled configurations; validate user counts and slave propagation in software RAID/device-mapper setups.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/diskutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/doc/Makefile -->
# sources/test-tools/fio/doc/Makefile

Purpose: Sphinx documentation build Makefile for fio, providing common output formats.

Important APIs/targets: Variables include `SPHINXOPTS=-W --keep-going`, `SPHINXBUILD`, `PAPER`, `BUILDDIR`, `ALLSPHINXOPTS`, and `I18NSPHINXOPTS`. Targets include `html`, `dirhtml`, `singlehtml`, `pickle`, `json`, `htmlhelp`, `qthelp`, `applehelp`, `devhelp`, `epub`, `epub3`, `latex`, `latexpdf`, `latexpdfja`, `text`, `man`, `texinfo`, `info`, `gettext`, `changes`, `linkcheck`, `doctest`, `coverage`, `xml`, `pseudoxml`, `dummy`, and `clean`.

Control flow: Each target invokes `sphinx-build` with the selected builder, shared doctree output under `output/doctrees`, and builder-specific output directories. PDF/info targets run secondary make commands inside generated trees.

State/persistence: Generated documentation lives under `doc/output`; `clean` removes its contents.

Dependencies/integration: Depends on Sphinx, optional LaTeX/tooling for PDF, qthelp/devhelp/applehelp tools for platform-specific formats, and `conf.py`.

Risks: `-W` treats warnings as errors, so documentation warnings break builds. `make -C` for `info` uses bare `make` instead of `$(MAKE)`. The help target lists many builders, but environment support may vary.

Test signals: `make dummy` provides a syntax-only signal; CI usually uses `html` or `man` to catch warning regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/doc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/doc/conf.py -->
# sources/test-tools/fio/doc/conf.py

Purpose: Sphinx configuration for fio documentation.

Important APIs/functions: Sets project metadata, source suffix, master document, templates, excluded patterns, pygments style, HTML theme, help output base names, LaTeX/man/Texinfo document definitions, and `todo_include_todos`. `fio_version()` reads or generates `FIO-VERSION-FILE` by invoking `FIO-VERSION-GEN`, then derives `version` and `release`.

Control flow: During Sphinx startup, Python imports this file, computes version/release, and applies builder settings. If the version file is missing, it calls the generator script in the workspace root and falls back to `Unknown` on failure.

State/persistence: May create/update `FIO-VERSION-FILE` through the generator. Generated docs go to Makefile output paths, not controlled here.

Dependencies/integration: Requires Sphinx, Python `os.path` and `subprocess`, the fio version generator, and `.rst` docs rooted at `index`/`fio_doc`.

Risks: `fio_version()` assumes the version file splits on `-` with at least two fields; malformed content can raise `IndexError`. Shell execution of `FIO-VERSION-GEN` depends on executable bit and shell environment. `master_doc='index'` while man pages point at `fio_doc`, so both source docs must exist.

Test signals: Run `sphinx-build -b dummy` or `make dummy`, plus a missing-version-file scenario to verify generation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/doc/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/cmdprio.c -->
# sources/test-tools/fio/engines/cmdprio.c

Purpose: Shared command-priority helper for fio asynchronous engines such as libaio and io_uring, handling option parsing, per-IO random priority assignment, and priority-specific completion latency stats.

Important APIs/functions: Public functions are `fio_cmdprio_init()`, `fio_cmdprio_cleanup()`, and `fio_cmdprio_set_ioprio()`. Internal helpers parse `cmdprio_bssplit`, generate block-size priority descriptors, assign `clat_prio_index`, allocate `thread_stat.clat_prio`, and compute whether an IO should receive a command priority.

Control flow: Init records options, detects whether percentage or block-size split mode is active, rejects simultaneous modes, defaults missing class to real-time, then builds either per-direction percentage entries or sorted block-size descriptors. During queueing, an engine calls `fio_cmdprio_set_ioprio()`: it finds the applicable percentage, draws a random 0-99 value from `td->prio_state`, and if selected stores `io_u->ioprio` plus the precomputed completion-latency priority index. Cleanup frees per-block-size arrays and clears the options pointer.

State/persistence: `struct cmdprio` owns generated descriptor arrays; option storage belongs to the engine option struct inside `td->eo`. Thread stats receive allocated per-priority latency buckets.

Dependencies/integration: Uses fio option parsing (`str_split_parse`, `split_parse_prio_ddir`), ioprio helpers, latency stat allocation, random state, and read/write direction predicates. Trim is intentionally ignored.

Risks: Error paths rely on cleanup to free partially built descriptors. The bssplit lookup is linear over block sizes in the hot path. Percentage sums above 100 are rejected per block size, but zero or unmatched block sizes silently use default priority.

Test signals: Cover mutually exclusive option rejection, default priority class, read/write enablement filtering, bssplit percentages by block size, clat priority bucket creation, and deterministic selection using seeded `prio_state`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/cmdprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/cmdprio.h -->
# sources/test-tools/fio/engines/cmdprio.h

Purpose: Declares command-priority structures, option macros, and helper APIs shared by IO engines.

Important APIs/types: Defines `CMDPRIO_RWDIR_CNT`, mode enum, `cmdprio_prio`, `cmdprio_bsprio`, `cmdprio_bsprio_desc`, `cmdprio_options`, and `cmdprio`. The `CMDPRIO_OPTIONS(opt_struct, opt_group)` macro expands fio option table entries when `FIO_HAVE_IOPRIO_CLASS` is available, or unsupported option stubs otherwise.

Control flow: Engine option structs embed `cmdprio_options`; their option tables include `CMDPRIO_OPTIONS`; engine init calls `fio_cmdprio_init()`; queue paths call `fio_cmdprio_set_ioprio()`; cleanup calls `fio_cmdprio_cleanup()`.

State/persistence: Runtime descriptors are held in `struct cmdprio`; user options are in the engine-specific option struct.

Dependencies/integration: Includes `../fio.h` and `../optgroup.h`, and relies on fio option offsets, priority constants, and `struct io_u`.

Risks: The macro assumes the embedding option struct has a member named `cmdprio_options`. Unsupported builds still expose option names but mark them unsupported. Only read/write directions are represented.

Test signals: Compile engines with and without `FIO_HAVE_IOPRIO_CLASS`; parse all option names; verify unsupported builds reject use clearly.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/cmdprio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/cpu.c -->
# sources/test-tools/fio/engines/cpu.c

Purpose: Implements the `cpuio` diskless/no-IO engine that burns CPU at a configured load, either by spinning or repeated qsort work.

Important APIs/functions: Registers one `ioengine_ops` named `cpuio`. Options are `cpuload`, `cpumode`, `cpuchunks`, and `exit_on_io_done`. Internal functions include `mwc32()`, qsort comparators, `do_qsort()`, `fio_cpuio_queue()`, `fio_cpuio_init()`, and cleanup/open callbacks.

Control flow: Init validates `cpuload`, clamps it to 100, temporarily sets setup runstate, configures thinktime so completed queue calls are interleaved with idle time, forces one pseudo file, and initializes either noop logging or qsort data. Queue optionally exits when other IO threads are done, then spins for `cpucycle` or runs qsort passes. In qsort mode, each work cycle measures elapsed time and recalculates thinktime to maintain requested CPU load.

State/persistence: Per-thread `cpu_options` stores load, mode, cycle, exit flag, and optional qsort data. Qsort data is allocated once and freed in cleanup.

Dependencies/integration: Uses fio engine registration, time helpers, runstate management, thinktime scheduling, and `fio_running_or_pending_io_threads()`.

Risks: `cpuload=0` is invalid, while very low loads can produce large thinktime. Qsort allocation is sizable and calibration may vary with CPU frequency/concurrency. `qsort_size` is static global but only used read-only.

Test signals: Run noop and qsort modes, validate load throttling behavior, cleanup under early termination, and `exit_on_io_done` with mixed jobs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/dev-dax.c -->
# sources/test-tools/fio/engines/dev-dax.c

Purpose: Implements a synchronous `dev-dax` engine that reads and writes device DAX character devices through mmap and persistent memory copies.

Important APIs/functions: Registers `dev-dax` with init, prep, queue, open/close, and get-file-size callbacks. Internal helpers map full or limited regions: `fio_devdax_file()`, `fio_devdax_prep_full()`, `fio_devdax_prep_limited()`, and `fio_devdax_prep()`.

Control flow: Open delegates to `generic_open_file()` and allocates per-file `fio_devdax_data`. File size discovery validates character device type, checks sysfs subsystem is `dax`, reads `/sys/dev/char/MAJ:MIN/size`, and stores size. Prep reuses an existing mapping if the IO falls inside it; otherwise it unmaps, attempts a full-file mapping unless partial mode is set or size overflows, then falls back to a limited mapping capped at 1 GiB. Queue performs `memcpy()` for reads and `pmem_memcpy_persist()` for writes; sync-like directions complete as no-ops.

State/persistence: Per-file engine data stores mapping pointer, mapped size, and offset. Partial mmap state is tracked in fio file flags.

Dependencies/integration: Requires libpmem, mmap, sysfs char device metadata, fio verify flags, and generic file open/close.

Risks: Pointer arithmetic on `void *` relies on compiler extension. `fio_devdax_get_file_size()` logs a non-DAX device but does not immediately return after the basename mismatch. Mapping alignment and block-size constraints depend on device/page size. Close frees mapping metadata but does not explicitly unmap an active mapping in this file.

Test signals: Exercise DAX device detection, full and limited mapping fallback, read/write persistence, offset bounds, verify-enabled write protections, and cleanup with changing mappings.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/dev-dax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/dfs.c -->
# sources/test-tools/fio/engines/dfs.c

Purpose: Implements the DAOS File System (`dfs`) fio engine using DAOS pool/container handles, DFS objects, and asynchronous DAOS event queues.

Important APIs/functions: Registers `dfs` with setup/init/prep/cleanup, file open/close/stat/unlink/invalidate, queue/getevents/event, and per-IO init/free. Global helpers initialize and clean DAOS/DFS connections. Queue operations call `dfs_write()`, `dfs_read()`, and DAOS event APIs.

Control flow: Per-thread init allocates `daos_data`, creates an IO pointer array sized to `iodepth`, and under a mutex initializes global DAOS state on first use: `daos_init`, pool connect, container open, DFS mount, and optional object class lookup. It then creates a per-thread event queue and increments thread count. File open maps fio create/read/write options to DFS flags and opens a DFS object. Queue builds a one-element scatter/gather list, initializes a DAOS event, issues async read/write, increments queued count, and returns queued. `getevents()` polls the DAOS event queue until `min` completions, transfers errors/resid to `io_u`, finalizes events, and returns completed `io_u`s through `event()`. Cleanup destroys the event queue, frees per-thread data, and closes global DAOS state when the last thread exits.

State/persistence: Global pool/container/DFS handles and object class are shared across threads; per-thread state includes event queue, one open object pointer, queued count, and completion array. Per-IO `daos_iou` holds event and SGL state.

Dependencies/integration: Requires DAOS/DFS libraries and version-specific APIs. Integrates with fio diskless/nodiskutil behavior and file lifecycle callbacks.

Risks: Only init/cleanup are mutex-protected; shared global handles are used concurrently. `daos_data` stores a single `dfs_obj_t *`, so multiple files per job may overwrite object state. Some error paths after `daos_event_init()` do not finalize the event. Poll loop ignores timeout argument and can spin with sleeps only through DAOS nowait polling.

Test signals: DAOS integration tests should cover missing options, version-specific UUID/label paths, multi-thread init/cleanup, multiple files, read/write completion errors, unlink, and iodepth saturation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/e4defrag.c -->
# sources/test-tools/fio/engines/e4defrag.c

Purpose: Implements an `e4defrag` engine that simulates ext4 defragmentation by issuing `EXT4_IOC_MOVE_EXT` ioctls from a donor file to the target file.

Important APIs/functions: Registers engine callbacks for init, queue, generic file open/close/size, and cleanup. Options are `donorname` and `inplace`. Internal state `e4defrag_data` stores donor fd and block size.

Control flow: Init requires a donor name, prefixes it with job directory if present, opens/creates the donor, optionally preallocates donor space for the workload range, stats it to learn block size, and stores state. Queue accepts only write directions, optionally fallocates donor space for the IO range in inplace mode, fills `struct move_extent` with donor fd and block ranges derived from offset/length, calls `ioctl(EXT4_IOC_MOVE_EXT)`, maps moved length to fio residual/error, and truncates donor back to zero in inplace mode. Cleanup closes donor and frees state.

State/persistence: Donor file persists on disk unless external cleanup removes it. Engine state is per-thread.

Dependencies/integration: Depends on ext4 move-extent ioctl, fallocate/ftruncate, fio read-only checks, and generic file callbacks.

Risks: Only meaningful on ext4 with compatible files. Donor path construction uses `sprintf` into `PATH_MAX`. Inplace truncate errors can override earlier success. The engine treats defrag as write-only even though data content should be unchanged.

Test signals: Tests need ext4 support, donor required validation, preallocated and inplace modes, partial moved lengths near EOF, and read-only mode rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/e4defrag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/exec.c -->
# sources/test-tools/fio/engines/exec.c

Purpose: Implements a diskless/no-IO `exec` engine that launches an external program during a fio job and terminates it when the fio runtime expires.

Important APIs/functions: Options are `program`, `arguments`, `grace_time`, and `std_redirect`. Internal helpers include `str_replace()`, `expand_variables()`, `exec_background()`, queue/init/cleanup/open callbacks, and the registered `exec` engine.

Control flow: Init requires a program, sets a 50 ms thinktime loop, and forces one pseudo file. On first queue call, `exec_background()` expands `%r` to runtime seconds and `%n` to job name, optionally opens `<job>.stdout` and `<job>.stderr`, forks, redirects child stdio, splits `program arguments` on spaces into an argv array, and calls `execvp()`. Subsequent queue calls sleep for thinktime, check elapsed job runtime, send SIGTERM after timeout, then sleep the grace interval. Cleanup sends SIGKILL if a child pid remains.

State/persistence: Per-thread options store the child pid. Redirect files are created in the current working directory and persist after completion.

Dependencies/integration: Uses fork/execvp, signals, fio time/runstate/thinktime, and fio logging.

Risks: Argument parsing is whitespace-only with no quote or escape handling. Child failure paths may return from the child into fio code rather than `_exit()`. Parent does not wait/reap the child, so zombies are possible until process exit. Timeout handling may send repeated SIGTERM. `str_replace()` can return the original pointer on allocation failure, and `expand_variables()` then frees it as if allocated, creating a potential invalid free.

Test signals: Tests should cover variable expansion, no-argument commands, quoted argument limitations, redirect file creation, timeout/grace termination, cleanup kill, and child exec failure.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/falloc.c -->
# sources/test-tools/fio/engines/falloc.c

Purpose: Implements a synchronous `falloc` engine that models IO with `fallocate()` operations rather than data transfer.

Important APIs/functions: Custom `open_file()` opens files/block devices read-write with fio's file hash. `fio_fallocate_queue()` maps fio directions to fallocate modes. The registered engine uses generic close/size callbacks and `FIO_SYNCIO | FIO_SYNCFS`.

Control flow: Open rejects non-file/non-block targets and stdin/stdout, uses `file_lookup_open()` and `add_file_hash()` to share descriptors, and records errors through `td_verror()`. Queue performs read as `FALLOC_FL_KEEP_SIZE`, write as extending fallocate mode `0`, trim as `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`, and sync directions through `do_io_u_sync()`. Errors set `io_u->error = errno`.

State/persistence: File allocation changes persist in the filesystem or block device. No extra engine state is stored.

Dependencies/integration: Depends on Linux fallocate flags, fio file hash, generic close/size, sync helpers, and read-only checks.

Risks: Requires filesystem support for selected fallocate modes. Opening block devices with `O_CREAT` is harmless or platform-dependent but unusual. Data is not read/written, so verification semantics differ from real IO.

Test signals: Exercise file and block targets, trim hole punching support, sync directions, unsupported filesystem errors, and file hash reuse.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/falloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/fileoperations.c -->
# sources/test-tools/fio/engines/fileoperations.c

Purpose: Implements six metadata-only engines: `filecreate`, `filestat`, `filedelete`, `dircreate`, `dirstat`, and `dirdelete`, measuring create/stat/delete latency without normal data IO.

Important APIs/functions: Shared `fc_data` records operation type and latency direction. Options for stat engines choose `stat`, `lstat`, or `statx`. Helpers include `setup_dirs()`, `open_file()`, `stat_file()`, `delete_file()`, `queue_io()`, `get_file_size()`, `init()`, `cleanup()`, and `remove_dir()`.

Control flow: Init infers file versus directory operation from the engine name and selects read/write latency bucket. Directory stat/delete setup creates target directories first. The open callback is repurposed as the measured operation: create engines create a file or directory, stat engines perform the configured stat call, and delete engines unlink/rmdir. Each measured path records completion latency via `add_clat_sample()` unless latency is disabled. Queue only handles sync operations and otherwise completes immediately.

State/persistence: Per-thread `fc_data` is allocated in init and freed in cleanup. Files/directories are created or removed on disk according to engine semantics.

Dependencies/integration: Uses POSIX file APIs, fio statx wrapper, latency sampling, generic close, and engine registration.

Risks: `fio_mkdir(f->file_name, S_IFDIR)` in `open_file()` for directory create is unusual because mode bits normally use permissions. `statx` path uses `realpath()`, so it fails for missing paths rather than measuring negative lookup. `init()` does not check `calloc()` failure.

Test signals: Run each engine with multiple files, latency enabled/disabled, all stat types, preexisting directories, delete of missing files, and sync directions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/fileoperations.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/ftruncate.c -->
# sources/test-tools/fio/engines/ftruncate.c

Purpose: Implements a fake synchronous `ftruncate` engine that models writes by truncating files to requested offsets.

Important APIs/functions: `fio_ftruncate_queue()` is the main queue callback; the engine uses generic file open/close/size and flags `FIO_SYNCIO | FIO_FAKEIO | FIO_SYNCFS`.

Control flow: Queue performs read-only checks, calls `ftruncate(f->fd, io_u->offset)` for write directions, delegates sync directions to `do_io_u_sync()`, rejects other directions with `EINVAL`, and maps syscall failures to `io_u->error`.

State/persistence: File size changes persist on disk. No extra engine state is allocated.

Dependencies/integration: POSIX `ftruncate`, fio generic file lifecycle, sync helpers, and fake-IO semantics.

Risks: It truncates to `offset`, not `offset + xfer_buflen`, so fio write sizes influence accounting but not final length directly. No data is written, making verify workloads inappropriate.

Test signals: Verify write offsets produce expected file sizes, sync paths work, unsupported directions fail, and generic open/close integration is clean.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/ftruncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/gfapi.h -->
# sources/test-tools/fio/engines/gfapi.h

Purpose: Shared declarations for GlusterFS gfapi fio engines.

Important APIs/types: Defines `gf_options` for volume, brick, and single-instance mode, plus `gf_data` for `glfs_t *fs`, `glfs_fd_t *fd`, and async completion array. Declares shared option table and common setup/cleanup/file callbacks implemented in `glusterfs.c`.

Control flow: Sync and async engine files include this header, use the shared options, call `fio_gf_setup()` during init, and delegate file lifecycle to common helpers.

State/persistence: `gf_data` is per-thread engine state; single-instance global sharing is implemented in `glusterfs.c`, not the header.

Dependencies/integration: Includes GlusterFS gfapi headers and fio core headers.

Risks: Exposes a single `fd` in `gf_data`, which constrains or complicates multi-file jobs. Header consumers must link with `glusterfs.c`.

Test signals: Build both gfapi engines and verify shared options populate `gf_options` consistently.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/gfapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/glusterfs.c -->
# sources/test-tools/fio/engines/glusterfs.c

Purpose: Provides common GlusterFS gfapi option handling, connection sharing, and file lifecycle for `gfapi` and `gfapi_async` engines.

Important APIs/functions: Defines `gfapi_options`, `fio_gf_setup()`, `fio_gf_cleanup()`, `fio_gf_get_file_size()`, `fio_gf_open_file()`, `fio_gf_close_file()`, and `fio_gf_unlink_file()`. Internal helpers manage `glfs_info` instances with a global list and mutex for `single-instance` sharing.

Control flow: Setup allocates `gf_data`, obtains a glfs handle either by creating a new one or refcounting a shared volume/brick instance, and stores it on `td->io_ops_data`. New glfs handles call `glfs_new`, configure logging and volfile server, initialize, sleep, and verify root lstat. Open maps fio read/write/direct/sync options to gfapi flags, creates/opens the file, extends and fills read targets if too short, optionally fsyncs created content, and applies fadvise when compiled. Close closes the gfapi fd. Cleanup frees async arrays, closes fd, releases glfs handle, and frees data.

State/persistence: Global `glfs_list_head` stores shared glfs handles with refcounts. Per-thread `gf_data` stores one current fd and optional async event array. Files are created/extended/unlinked in GlusterFS.

Dependencies/integration: Requires GlusterFS libgfapi, fio file sizing/layout helpers, optional new gfapi APIs and fadvise support.

Risks: `fio_gf_unlink_file()` finalizes `g->fs` and frees `g` directly instead of using the shared refcount release path, which can conflict with single-instance mode. `fio_gf_put_glfs()` frees `volume`/`brick` but not the `glfs_info` struct itself. Single `g->fd` makes multi-file behavior fragile. There is a fixed `/tmp/fio_gfapi.log` path.

Test signals: Cover single-instance refcounting, multi-thread setup/cleanup, file extension for read jobs, create_fsync, unlink, direct/sync flags, and both old/new gfapi compile configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/glusterfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/glusterfs_async.c -->
# sources/test-tools/fio/engines/glusterfs_async.c

Purpose: Implements the experimental asynchronous GlusterFS gfapi fio engine `gfapi_async`.

Important APIs/functions: Defines per-IO `fio_gf_iou`, async callback `gf_async_cb()`, `fio_gf_async_queue()`, polling `fio_gf_getevents()`, `fio_gf_event()`, per-IO init/free, and setup wrapping the shared gfapi setup.

Control flow: Setup logs that async is experimental, initializes common gfapi state, forces thread mode, and allocates an `aio_events` array sized by iodepth. Queue submits gfapi async read/write, optional discard, fdatasync, or fsync operations with `io_u` as callback data. The callback marks `io_complete`. `getevents()` scans fio's in-flight IO list until enough completed flags are found, clears each flag, and stores completed `io_u`s in `aio_events`.

State/persistence: Each `io_u` has `fio_gf_iou` state with a completion flag. Per-thread `gf_data` stores completion array and shared file/glfs state.

Dependencies/integration: Depends on gfapi async APIs, shared `gfapi.h` helpers, fio in-flight IO list, and optional trim/new API compile flags.

Risks: Completion flag is not atomic or locked between callback and polling thread. Callback ignores return status, so IO errors are not propagated. `getevents()` busy-waits with `usleep(100)` and ignores timeout. The engine is explicitly marked experimental.

Test signals: Integration tests should cover read/write/sync completions, callback error propagation gaps, iodepth behavior, timeout behavior, and thread-safety under high concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/glusterfs_async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/glusterfs_sync.c -->
# sources/test-tools/fio/engines/glusterfs_sync.c

Purpose: Implements the synchronous GlusterFS gfapi fio engine `gfapi`.

Important APIs/functions: Uses common gfapi setup/file callbacks and defines `fio_gf_prep()` plus `fio_gf_queue()`. Registers engine flags `FIO_SYNCIO | FIO_DISKLESSIO`.

Control flow: Prep seeks the gfapi fd to the IO offset when the next read/write offset is not already the file's last engine position. Queue handles reads with `glfs_read`, writes with `glfs_write`, sync with `glfs_fsync`, datasync with `glfs_fdatasync`, and rejects unsupported directions. It updates `engine_pos`, sets residuals for short positive transfers, and logs errors through fio.

State/persistence: Uses shared per-thread `gf_data` and `fio_file.engine_pos` for seek avoidance. File content persists in GlusterFS.

Dependencies/integration: Depends on gfapi sync APIs and common `glusterfs.c`.

Risks: Uses a single `g->fd`; multi-file jobs may not behave correctly. Short reads/writes are treated as successful residuals. New/old gfapi sync prototypes are compile-time selected.

Test signals: Test sequential seek optimization, random offset seeks, short transfer handling, sync/datasync paths, and multi-file workloads.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/glusterfs_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/http.c -->
# sources/test-tools/fio/engines/http.c

Purpose: Implements a synchronous diskless HTTP(S) engine using libcurl easy APIs for WebDAV-style, S3, and Swift object IO.

Important APIs/functions: Registers `http` engine with setup, queue, cleanup, event stubs, open, and invalidate callbacks. Options configure HTTPS mode, host, basic auth, S3 credentials/security token/region/SSE/storage class, Swift token, mode, verbosity, and object mode. Helpers implement AWS URI encoding, SHA256/MD5 hex, base64, HMAC-SHA256, curl trace logging, S3 Signature V4 headers, Swift headers, range headers, curl read/write/seek callbacks, and queue execution.

Control flow: Setup allocates `http_data`, initializes a CURL handle, configures verbosity, protocols, TLS verification policy, callbacks, optional basic auth, stores state, and forces thread mode. Queue builds an object path either per block (`file_offset_len`) or per file with optional HTTP `Range`. It sets URL, stream state, and upload size; adds S3 or Swift auth headers; then performs PUT for writes, GET for reads, and DELETE for trims. Status codes are mapped to success for expected ranges; missing read objects produce zero-filled buffers; other failures set `EIO`.

State/persistence: Per-thread state is one reusable CURL easy handle. Per-request state is stack-local stream and header list. Remote objects persist according to PUT/DELETE operations.

Dependencies/integration: Requires libcurl, OpenSSL HMAC/SHA/MD5, fio option parsing, diskless sync engine semantics, and server-specific S3/Swift/WebDAV behavior.

Risks: `_add_aws_auth_header()` and `_add_swift_header()` receive `slist` by value; appended header list is not returned to `fio_http_queue()`, so the local `slist` freed at exit may remain null and the CURL handle may retain/freeze header ownership incorrectly. Swift read/trim call `_add_swift_header()` with `dsha == NULL` but format it with `%s`, which is undefined. Fixed-size canonical request buffers can truncate long paths/tokens. S3 signing includes storage class for all methods, which may not match every S3-compatible service. TLS insecure mode disables both peer and host checks.

Test signals: Tests should cover WebDAV PUT/GET/DELETE, S3 SigV4 canonical output against known vectors, SSE-C headers, Swift write/read/trim, range reads near EOF, 404 zero-fill, TLS modes, and leak/error checks around repeated header lists.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/http.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/ime.c -->
# sources/test-tools/fio/engines/ime.c

Purpose: Implements three DDN Infinite Memory Engine fio engines: `ime_psync`, `ime_psyncv`, and `ime_aio`, using IME native APIs instead of POSIX IO.

Important APIs/functions: Shared helpers handle IME filename prefixing, file size/open/close/unlink, setup, engine init/finalize, and event lookup. `ime_psync` uses blocking `ime_native_pread/pwrite/fsync`. `ime_psyncv` batches contiguous IOs into one preadv/pwritev request with commit/getevents. `ime_aio` batches contiguous iovecs into async IME requests with callback-driven completion. Registration exposes all three engines.

Control flow: Setup initially sets file sizes to zero to avoid POSIX sizing before fork/thread setup. Engine init calls `ime_native_init()`, marks global initialized, and temporarily sets fio file sizes to desired IO extents. Open prefixes filenames with `DEFAULT_IME_FILE_PREFIX`, rejects trim, maps fio flags, opens through IME, sizes/truncates write files as needed, and rejects too-small read files. Psync completes immediately per queue. Psyncv queues only contiguous same-fd/same-direction iovecs until commit, then reports events after the blocking vector call. AIO queues iovecs into a ring, starts one or more `ime_native_aio_read/write` requests on commit, and `getevents()` waits on per-request condition variables until completions arrive.

State/persistence: Global `fio_ime_is_initialized` tracks process/thread-level IME initialization. Per-engine `ime_data` stores iovec rings, `io_u` arrays, event arrays, queue indices, last offset, and either sync or async request state. IME files persist through native storage and prefixed filenames.

Dependencies/integration: Requires `ime_native.h`, pthread condition/mutex primitives, fio queue/commit/getevents contracts, diskless flags to avoid POSIX paths, and native IME lifecycle calls.

Risks: Global initialization flag is not locked and may race in thread mode. Several allocations in psyncv/aio init are unchecked. Psyncv completion loops over `queued` using linear indices even though ring fields exist, which is safe only because it resets after each commit. AIO residual calculation distributes aggregate bytes over iovecs and may be confusing for partial completions. `fio_ime_unlink_file()` calls POSIX `unlink()` on the prefixed path rather than an IME native unlink.

Test signals: Validate all three engines with read/write/sync, contiguous and non-contiguous batching, iodepth ring wrap, async callback errors, fork versus thread lifecycle, too-small read rejection, file extension, and trim rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/ime.c -->

# subset-b-009228 research

Grouped research report for fio replay, logging, utility library, initialization, memory, option grouping, and mock-test files under `sources/test-tools/fio`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/iolog.c -->
# sources/test-tools/fio/iolog.c

Purpose: implements fio IO logging, replay, runtime sample flushing, and optional compressed log storage. It supports writing version 3 textual iologs, reading version 2/3 iologs or blktrace inputs, queueing replay `io_piece` records, and persisting latency/bandwidth/IOPS/histogram logs.

Important APIs/functions: `init_iolog`, `read_iolog_get`, `log_io_u`, `log_file`, `log_io_piece`, `unlog_io_piece`, `trim_io_piece`, `setup_log`, `flush_samples`, `flush_log`, `td_writeout_logs`, `fio_writeout_logs`, `iolog_compress_init/exit`, `iolog_file_inflate`, and `log_chunk_sizes`. Internal helpers parse versioned iolog lines, handle open/close/unlink pseudo-IOs, generate replay delays, serialize samples, and compress/decompress chunks with zlib when configured.

Control flow: initialization chooses read, write, or no-op mode. Replay reads file/socket/stdin headers, parses records into `td->io_log_list`, then `read_iolog_get` dequeues pieces into `io_u` objects, applying file actions and replay timing. Verification logging inserts successful writes into a list or red-black tree depending on overlap risk. Runtime logging accumulates samples in `struct io_log`, optionally hands full buffers to a compression workqueue, and final writeout locks per-file log names before flushing or sending logs to server/GUI clients.

State/persistence: mutates `thread_data` replay cursors, timing offsets, total IO size, max block sizes, IO history trees/lists, compression chunk lists, pending sample buffers, and output files. Textual iologs are append-created with a version line; normal logs may append or overwrite depending on `per_job_logs` and compressed-store mode.

Dependencies/integration: tightly integrated with `fio.h`, file lifecycle helpers, trim tracking, blktrace, data placement, pshared mutexes, workqueues, server output, `lib/rbtree`, `lib/roundup`, zlib, Unix sockets, and fio's runstate machine.

Risks/test signals: parsing uses fixed 256-byte `%s` file/action buffers and line-oriented input; malformed actions are logged and skipped. Compression depends on ordered chunk sequence and deferred frees, so leaks or stale pointers are possible around async paths. Replay timing can drift through `time_offset`. Signals are successful replay/writeout, decompression compatibility, no duplicate verification pieces after overlap pruning, and no lost samples when logs regrow or compress.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/iolog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/iolog.h -->
# sources/test-tools/fio/iolog.h

Purpose: public contract for fio iolog replay pieces and statistical log buffers. It defines sample encoding, log metadata, IO history records, compression chunk records, and exported log/replay APIs used by the backend, stats, verify, and output paths.

Important APIs/types: `struct io_stat`, `io_hist`, `io_sample`, `io_logs`, `io_log`, `io_piece`, `log_params`, and `iolog_compress`. Macros encode optional sample fields in high bits of `__ddir` (`LOG_OFFSET_SAMPLE_BIT`, `LOG_PRIO_SAMPLE_BIT`, `LOG_AVG_MAX_SAMPLE_BIT`, `LOG_ISSUE_TIME_SAMPLE_BIT`) and compute variable sample sizes via `log_entry_sz`, `log_sample_sz`, and `get_sample`.

Control flow/state: callers initialize `io_piece` with `init_ipo`, queue or store it, and later replay or verify from lists/trees. Callers create `io_log` objects through `setup_log`, append samples elsewhere in fio, and flush or free them through the declared functions. `per_unit_log` and `inline_log` guide writeout and aggregation behavior.

Dependencies/integration: exposes fio-specific types from `rbtree.h`, `ieee754.h`, `flist.h`, and `ioengines.h`. `struct io_log` embeds pthread mutexes for compressed chunks and deferred frees, binding users to pshared/threaded log handling.

Risks/test signals: the flexible-array `aux[]` layout requires every producer/consumer to agree on optional fields. `ipo_bytes_align` assumes power-of-two replay alignment. Test coverage should exercise offset/priority/issue-time combinations, histogram samples, compressed logs, and replay file actions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/iolog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/json.c -->
# sources/test-tools/fio/json.c

Purpose: small JSON object model and pretty-printer for fio output. It creates objects/arrays/values, attaches values to parents, escapes strings, frees full trees, and writes formatted JSON into a `buf_output`.

Important APIs/functions: `json_create_object`, `json_create_array`, `json_object_add_value_type`, `json_array_add_value_type`, `json_free_object`, and `json_print_object`. Static constructors handle integer, float, string, object, and array value types; `strdup_escape` escapes backslash and double quote for string output.

Control flow: add-value functions clone scalar/string values or wrap an existing object/array, create parent pairs or array entries, then grow pointer arrays with `realloc`. Printing computes indentation by walking parent pointers and recursively prints objects, arrays, pairs, and scalar values.

State/persistence: owns heap-allocated `json_object`, `json_array`, `json_pair`, value nodes, string copies, and dynamic child arrays. No file persistence occurs directly; output accumulates in `struct buf_output`.

Dependencies/integration: uses `json.h`, `log.h`, and `buf_output` through `log_buf`. It is integrated with fio's normal JSON output paths rather than a general JSON parser.

Risks/test signals: allocation failures are surfaced as `ENOMEM`, but object/array wrapping transfers ownership expectations to the JSON tree. String escaping only covers backslash and quote, not control characters. Tests should cover nested ownership/free, array/object parent levels, null-string handling through inline wrappers, and valid escaping.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/json.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/json.h -->
# sources/test-tools/fio/json.h

Purpose: declares fio's lightweight JSON tree structures and convenience builders. It is an output-building API, not a parser.

Important APIs/types: integer constants for value and parent types; `struct json_value`, `json_array`, `json_object`, and `json_pair`; object/array constructors; `json_free_object`; typed add wrappers for int, float, string, object, and array; `json_array_last_value_object`; and `json_print_object`.

Control flow/state: inline wrappers construct a temporary `json_value` descriptor and delegate to the generic add functions in `json.c`, which allocate the owned tree nodes. Parent pointers in values, arrays, objects, and pairs allow the printer to derive indentation depth.

Dependencies/integration: includes `lib/output_buffer.h` because printing targets `struct buf_output`. The header is consumed by fio output/stat formatting code that needs hierarchical JSON construction.

Risks/test signals: the API does not expose `json_free_array` for standalone arrays, so top-level ownership is expected to be an object. `json_array_last_value_object` assumes the array is non-empty and the last value is an object. Tests should cover wrapper behavior for null strings and ownership expectations for nested arrays/objects.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/json.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/axmap.c -->
# sources/test-tools/fio/lib/axmap.c

Purpose: implements a hierarchical bitmap set optimized for tracking used/free block numbers. Higher levels mark full words in lower levels, making full maps cheaper to search.

Important APIs/functions: `axmap_new`, `axmap_free`, `axmap_reset`, `axmap_set`, `axmap_set_nr`, `axmap_isset`, and `axmap_next_free`. Internal helpers walk levels bottom-up or top-down, set contiguous bits up to a word boundary, and find the first free bit with wraparound support.

Control flow: construction computes the number of levels from `nr_bits`, allocates one map per level, and zeroes them. Setting a bit updates level 0 and then propagates one-bit fullness indicators upward. `axmap_next_free` first checks the current level-0 word and then performs a top-down search, wrapping to zero if needed.

State/persistence: state is entirely in heap-allocated `struct axmap` levels and unsigned-long maps. No locking is present; callers must serialize concurrent updates.

Dependencies/integration: depends on architecture `BITS_PER_LONG`, `ffz`, `types.h` bool, and `min`. It is suitable for fio random maps and allocator-style free-slot discovery.

Risks/test signals: boundary handling around `bit_nr == nr_bits` and partial final words is delicate; `axmap_isset` uses `<= nr_bits`, which deserves attention because valid bits end at `nr_bits - 1`. Tests should cover 32/64-bit builds, full maps, wraparound, contiguous set truncation, and repeated duplicate sets.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/axmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/axmap.h -->
# sources/test-tools/fio/lib/axmap.h

Purpose: declares the opaque hierarchical bitmap API used to set, query, reset, and find free numeric slots.

Important APIs/types: opaque `struct axmap`, allocator/free pair, `axmap_set`, `axmap_set_nr`, `axmap_isset`, `axmap_next_free`, and `axmap_reset`.

Control flow/state: callers create a bounded map for values `0..nr_bits-1`, then mutate it through set calls and query availability. `axmap_set_nr` reports how many contiguous bits were newly set, which lets callers deal with already-used ranges.

Dependencies/integration: includes `inttypes.h` and fio bool definitions from `types.h`. The implementation relies on arch bit width and internal bit helpers, but users see only the opaque handle.

Risks/test signals: callers must free the map and must not share it concurrently without external synchronization. Tests should verify that the header contract matches implementation behavior at empty, full, reset, and boundary states.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/axmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/bloom.c -->
# sources/test-tools/fio/lib/bloom.c

Purpose: implements a Bloom filter with five hash functions for approximate duplicate detection over word arrays or strings.

Important APIs/functions: `bloom_new`, `bloom_free`, `bloom_set`, and `bloom_string`. Static hash wrappers bind Jenkins, XXH32, murmur3, crc32c, and FNV to a shared seed; `__bloom_check` computes indexes, checks all bits, and optionally sets missing bits.

Control flow: construction probes crc32c acceleration, allocates the filter and a zeroed `uint32_t` map sized by entry count. A check hashes the input five times, mods by `nentries`, and tests or sets the corresponding bit positions.

State/persistence: heap-owned filter with `nentries` and mutable bit map. It is probabilistic and in-memory only.

Dependencies/integration: depends on fio hash and crc libraries, `types.h`, and platform crc probes. It can be used by verify/dedupe-style flows that need compact seen-set behavior.

Risks/test signals: `bloom_new` does not check allocation of `struct bloom` before assigning `nentries`; zero `entries` would also make modulo invalid. False positives are expected. Tests should cover allocation failure assumptions, repeated insert returning already-seen, non-setting lookup, and string length handling.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/bloom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/bloom.h -->
# sources/test-tools/fio/lib/bloom.h

Purpose: exposes the Bloom filter API with an opaque `struct bloom`.

Important APIs/types: `bloom_new`, `bloom_free`, `bloom_set` for `uint32_t` word arrays, and `bloom_string` for byte strings with optional set behavior.

Control flow/state: callers allocate with an expected bit count, insert/check data, and free the map. Return values indicate whether all hash bits were already set, not whether the element is certainly present.

Dependencies/integration: includes fio bool support and integer types. It intentionally hides hash implementation choices.

Risks/test signals: callers must treat positive results as probabilistic and avoid zero-sized filters. Tests should verify set-versus-check mode and stable behavior across hash backends.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/bloom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/bswap.h -->
# sources/test-tools/fio/lib/bswap.h

Purpose: provides big-endian-to-CPU conversion helpers for 32-bit and 64-bit integers.

Important APIs/functions: inline `__be32_to_cpu` and `__be64_to_cpu`. On little-endian builds they manually rearrange bytes; on other builds they return the input unchanged.

Control flow/state: no state. The helpers are pure integer transformations selected at compile time by `CONFIG_LITTLE_ENDIAN`.

Dependencies/integration: includes `inttypes.h` and relies on fio configure endianness macros. It is used where fio reads serialized big-endian values.

Risks/test signals: correctness depends on build-time endian macros matching runtime architecture, which `libfio.c` also checks during initialization. Tests should use known constants such as `0x01020304` and cross-check both endian build paths.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/bswap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/ffz.h -->
# sources/test-tools/fio/lib/ffz.h

Purpose: implements "find first zero" bit helpers and a 64-bit find-first-set primitive used by bitmap code.

Important APIs/functions: `ffs64`, `ffz`, and `ffz64`. If `ARCH_HAVE_FFZ` is set, `ffz` maps to `arch_ffz`; otherwise it inverts the word and uses `ffs64`.

Control flow/state: pure inline bit scanning with staged masks for 32, 16, 8, 4, 2, and 1-bit narrowing. No state or allocation.

Dependencies/integration: includes integer types and optionally architecture-provided bit operations. `axmap.c` uses these helpers to find free positions.

Risks/test signals: return values for all-ones or zero inputs must match callers' expectations; `ffs64(0)` returns 64 after falling through, so callers should avoid undefined semantic cases or handle them explicitly. Tests should cover low/high bit positions and all-zero/all-one masks.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/ffz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/flist_sort.c -->
# sources/test-tools/fio/lib/flist_sort.c

Purpose: stable merge-sort implementation for fio intrusive doubly-linked lists.

Important APIs/functions: exported `flist_sort`; static `merge` and `merge_and_restore_back_links`. The comparator receives caller private data and two `flist_head` entries.

Control flow: the circular doubly-linked list is temporarily converted into null-terminated singly-linked runs. The algorithm accumulates sorted partial lists by binary carry merging, then merges the last parts while restoring `prev` links and circular head/tail links.

State/persistence: mutates only the provided list links. No allocation occurs; maximum efficient list length is bounded by `MAX_LIST_LENGTH_BITS`, with a log warning if exceeded.

Dependencies/integration: depends on fio `flist.h` and `log.h`. Comparator callbacks may do scheduling or side effects; the final restoration loop deliberately calls `cmp` during long tail processing.

Risks/test signals: link corruption is the main risk. Tests should cover empty, one-element, already-sorted, reverse-sorted, duplicate-key stability, and very long lists near the warning threshold.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/flist_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/fls.h -->
# sources/test-tools/fio/lib/fls.h

Purpose: provides `__fls`, a 32-bit find-last-set helper.

Important APIs/functions: inline `__fls(int x)` returns 0 for input 0 and otherwise a 1-based index of the most significant set bit.

Control flow/state: pure bit manipulation using left shifts and decrementing an initial result of 32. No state or dependencies beyond the header guard.

Dependencies/integration: used by `roundup.h` to compute powers of two, and by any code needing generic bit operations without arch intrinsics.

Risks/test signals: takes `int`, so callers with wider unsigned values must not expect 64-bit behavior. Tests should cover 0, 1, high bit, and mixed-bit values.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/fls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/gauss.c -->
# sources/test-tools/fio/lib/gauss.c

Purpose: produces pseudo-Gaussian-distributed offsets/ranges from fio's random generator.

Important APIs/functions: `gauss_init` and `gauss_next` are declared in the header; implementation initializes range, deviance, center, and seed state, then sums repeated uniform draws (`GAUSS_ITERS`) to approximate a normal distribution before mapping into `nranges`.

Control flow/state: initialization seeds an embedded `frand_state` and computes center offset. Each next call samples the RNG repeatedly, scales the result by deviance, hashes/offsets as needed, and returns a bounded range value.

Dependencies/integration: depends on `math.h`, fio hash helpers, and `rand.h`. It is part of fio's random distribution options alongside Zipf/Pareto.

Risks/test signals: statistical quality depends on `GAUSS_ITERS`, deviance parameters, and modulo mapping. Tests should check bounds, deterministic seed repeatability, center behavior, and distribution sanity rather than exact full sequences unless seed and algorithm are fixed.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/gauss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/gauss.h -->
# sources/test-tools/fio/lib/gauss.h

Purpose: declares Gaussian distribution state and API for fio random offset generation.

Important APIs/types: `struct gauss_state` stores `nranges`, deviance, random offset, and an embedded `frand_state`; `gauss_init` seeds/configures it; `gauss_next` returns the next bounded value.

Control flow/state: callers keep one state per distribution stream and repeatedly call `gauss_next`. State mutation happens through the embedded RNG.

Dependencies/integration: includes `rand.h` and integer types. Used by workload option code that selects non-uniform random distributions.

Risks/test signals: callers must initialize before use and treat output as deterministic for a given seed/config. Tests should cover range boundaries and center/deviation options.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/gauss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/getrusage.c -->
# sources/test-tools/fio/lib/getrusage.c

Purpose: compatibility shim for platforms lacking a working `getrusage`.

Important APIs/functions: `getrusage(int who, struct rusage *r_usage)` returns `-1` and sets `errno = EINVAL` in this fallback implementation.

Control flow/state: no state; every call fails deterministically.

Dependencies/integration: includes `errno.h` and `getrusage.h`. Build configuration selects this file only when fio needs the fallback.

Risks/test signals: consumers must tolerate failure and not assume resource accounting is available. Tests should verify graceful degradation in stats paths when `getrusage` returns an error.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/getrusage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/getrusage.h -->
# sources/test-tools/fio/lib/getrusage.h

Purpose: declares the fallback `getrusage` signature for platforms where fio supplies it.

Important APIs/types: includes `sys/time.h` and `sys/resource.h`, then declares `getrusage(int, struct rusage *)`.

Control flow/state: no state; callers use the normal libc-style function signature regardless of whether the platform or fio fallback supplies the body.

Dependencies/integration: used by portability builds and resource-stat code.

Risks/test signals: duplicate declaration conflicts are possible if build configuration includes this while libc also exposes an incompatible prototype. Compile tests across supported OS configurations are the main signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/getrusage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/hweight.c -->
# sources/test-tools/fio/lib/hweight.c

Purpose: implements Hamming weight/popcount helpers for fio bit masks.

Important APIs/functions: functions declared in `hweight.h`, including 8/32/64-bit weights. The implementation uses standard bit-counting masks and shifts rather than platform intrinsics.

Control flow/state: pure arithmetic; no allocation, global state, or side effects.

Dependencies/integration: includes only `hweight.h`. Used by bitmap/stat code that needs portable bit counts.

Risks/test signals: tests should cover zero, all-ones, alternating masks, and high-bit-only values for each width. Performance is predictable but may be lower than compiler builtins on some platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/hweight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/hweight.h -->
# sources/test-tools/fio/lib/hweight.h

Purpose: declares portable Hamming weight functions.

Important APIs/functions: `hweight8`, `hweight32`, and `hweight64` declarations over fixed-width integer types.

Control flow/state: no state in the header; callers receive integer counts of set bits.

Dependencies/integration: includes `inttypes.h` and is used by portable bit-manipulation code.

Risks/test signals: compile-time type widths matter. Tests should compare results against known popcounts and, where available, compiler builtin popcounts.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/ieee754.c -->
# sources/test-tools/fio/lib/ieee754.c

Purpose: serializes and deserializes floating-point values into IEEE-754-style integer bit patterns.

Important APIs/functions: `pack754(long double f, unsigned bits, unsigned expbits)` and `unpack754(uint64_t i, unsigned bits, unsigned expbits)`. The header wraps these for double-sized 64-bit values.

Control flow: packing handles zero, records sign, normalizes into `[1,2)`, computes significand and biased exponent, and combines sign/exponent/significand bits. Unpacking reverses that process by extracting significand, applying exponent bias, and restoring sign.

State/persistence: pure conversion helpers; no state. Used when fio wants stable binary representation independent of native floating layout.

Dependencies/integration: public-domain algorithm from Beej's guide, included through `ieee754.h`. Used by stats structures that store `fio_fp64_t`.

Risks/test signals: does not explicitly handle NaN, infinities, denormals, or overflow. Tests should round-trip zero, positive/negative normal doubles, large/small finite values, and known bit encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/ieee754.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/ieee754.h -->
# sources/test-tools/fio/lib/ieee754.h

Purpose: exposes IEEE-754 packing helpers and fio's portable 64-bit floating storage type.

Important APIs/types: `pack754`, `unpack754`, macros `fio_double_to_uint64` and `fio_uint64_to_double`, and `fio_fp64_t`, whose union provides a `uint64_t`, `double`, and padding bytes.

Control flow/state: no state in the header. Callers use macros for double conversion or store means/statistics in `fio_fp64_t`.

Dependencies/integration: includes fixed-width integer types. `iolog.h` and stats code use `fio_fp64_t` to keep alignment and serialization predictable.

Risks/test signals: native union access and explicit pack/unpack are different paths; tests should ensure the selected path preserves values and alignment on strict architectures.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/ieee754.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/lfsr.c -->
# sources/test-tools/fio/lib/lfsr.c

Purpose: implements a maximal-length linear feedback shift register generator for deterministic non-repeating random-like sequences over a bounded range.

Important APIs/functions: `lfsr_init`, `lfsr_reset`, and `lfsr_next`. Static tap tables define primitive polynomials for 3-63 bits; helpers create XOR masks, choose a tap width for the requested size, and prepare "spin" behavior.

Control flow: initialization chooses taps whose period exceeds the requested range, builds masks, validates spin <= 15, and seeds the state. `lfsr_next` advances the register by `spin` steps, handles precomputed spin sub-cycles, rejects values above `max_val`, and stops after all values have been produced.

State/persistence: all mutable sequence state lives in `struct fio_lfsr`: last value, generated count, max value, XOR mask, cached top bit, spin, and cycle counters. No heap allocation.

Dependencies/integration: includes `compiler.h` for fallthrough annotations. Used by fio random map modes that require repeatable coverage without replacement.

Risks/test signals: all-ones seed is illegal for the XNOR form; sizes needing >=64-bit taps fail. Spin cycle math is subtle and should be tested for repeat-free coverage. Signals include deterministic sequences, no out-of-range values, and correct exhaustion.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/lfsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/lfsr.h -->
# sources/test-tools/fio/lib/lfsr.h

Purpose: declares LFSR state and public sequence functions.

Important APIs/types: `FIO_MAX_TAPS`, `struct lfsr_taps`, `struct fio_lfsr`, `lfsr_init`, `lfsr_reset`, and `lfsr_next`.

Control flow/state: callers allocate the state struct, initialize with size/seed/spin, then repeatedly call `lfsr_next` until it returns nonzero. `lfsr_reset` restarts with a new seed while preserving configuration.

Dependencies/integration: fixed-width integer types only. The state struct is designed for embedding inside fio job/random state.

Risks/test signals: callers must check initialization and reset failures for unsupported sizes or illegal seeds. Tests should cover exhaustion and repeatability.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/lfsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/memalign.c -->
# sources/test-tools/fio/lib/memalign.c

Purpose: provides allocator-independent aligned allocation and matching free helpers.

Important APIs/functions: `__fio_memalign(size_t alignment, size_t size, malloc_fn fn)` and `__fio_memfree(void *ptr, size_t size, free_fn fn)`. An `align_footer` stored at `ret + size` records the offset from raw allocation to aligned pointer.

Control flow: allocation asserts power-of-two alignment, overallocates by alignment plus footer room, aligns the returned address, and records the raw-pointer offset. Free recomputes the footer location from the caller-provided size and frees `ptr - offset`.

State/persistence: no global state; metadata is persisted adjacent to the returned allocation and requires the same `size` at free time.

Dependencies/integration: includes `memalign.h` and `smalloc.h` but works with caller-supplied malloc/free functions. Useful for both libc and fio smalloc-style allocators.

Risks/test signals: passing a different size to free reads the wrong footer. Pointer arithmetic on `void *` relies on compiler extensions. Tests should cover alignments, zero/odd sizes, and mismatched allocator pairs under sanitizers.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/memalign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/memalign.h -->
# sources/test-tools/fio/lib/memalign.h

Purpose: declares generic aligned allocation helpers and callback types.

Important APIs/types: `malloc_fn`, `free_fn`, `__fio_memalign`, and `__fio_memfree`.

Control flow/state: callers provide allocation/free callbacks, requested alignment, and size. The implementation stores hidden footer metadata and therefore requires free to receive the original size.

Dependencies/integration: includes integer and bool headers. Used by code that needs alignment without depending on `posix_memalign`.

Risks/test signals: callback signatures must match the allocator family, and the requested alignment must be a power of two. Tests should verify returned pointer alignment and correct freeing.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/memalign.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/memcpy.c -->
# sources/test-tools/fio/lib/memcpy.c

Purpose: standalone fio microbenchmark for comparing memory copy routines across block sizes.

Important APIs/functions: exported `fio_memcpy_test`; static test functions for `memcpy`, `memmove`, bytewise `simple_memcpy`, and a `hybrid` selector; `setup_tests`, `free_tests`, `get_test_mask`, and `list_types`.

Control flow: the entry point parses an optional comma-separated type list or help/list command, allocates two 32 MiB buffers, fills the source with deterministic random data, warms the CPU/data, then times repeated copies for sizes from 8 bytes to 512 KiB and prints MiB/s.

State/persistence: mutates static `tests[]` entries with shared source/destination buffers during a run. No persistent output beyond stdout.

Dependencies/integration: uses fio RNG, timing, spin, and OS helpers. Intended as a tool/helper path, not the main IO data path.

Risks/test signals: benchmark results are noisy and affected by compiler optimization, CPU state, cache warmth, and libc implementation. `t_hybrid` appears to use `simple_memcpy` for larger sizes and libc for smaller ones, which should be intentional or reviewed. Build/run tests should check allocation cleanup and type filtering.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/memcpy.h -->
# sources/test-tools/fio/lib/memcpy.h

Purpose: declares the memory-copy benchmark entry point.

Important APIs/functions: `fio_memcpy_test(const char *type)`, where `type` may be null for all tests, `help`/`list`, or a comma-separated set of copy method names.

Control flow/state: no header state; callers run the benchmark and receive process-style success/failure integer status.

Dependencies/integration: implementation depends on fio timing and RNG, but the header is intentionally minimal.

Risks/test signals: this API prints directly and is unsuitable for library-style quiet use. Tests should cover unknown type handling and help/list behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/memcpy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/mountcheck.c -->
# sources/test-tools/fio/lib/mountcheck.c

Purpose: portability helper to detect whether a device path is currently mounted.

Important APIs/functions: `device_is_mounted(const char *dev)`. The implementation has compile-time branches for `getmntent`, BSD `getmntinfo` with `statfs`, NetBSD `statvfs`, and a default unsupported path returning 0.

Control flow: supported branches enumerate mount table entries and compare the mount source name with `dev`, returning 1 on exact match and 0 otherwise.

State/persistence: no persistent state. The `getmntent` branch opens `/etc/mtab` and closes it with `endmntent`.

Dependencies/integration: selected by configure macros and OS headers. Used by fio safety checks around devices/files.

Risks/test signals: exact string matching may miss symlinks, canonicalized paths, bind mounts, or systems where `/etc/mtab` is stale. Tests should use temporary mounts or mocked platform calls where possible and verify unsupported builds fail closed as "not mounted".
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/mountcheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/mountcheck.h -->
# sources/test-tools/fio/lib/mountcheck.h

Purpose: declares `device_is_mounted`.

Important APIs/functions: `int device_is_mounted(const char *)`, returning nonzero when the configured platform implementation finds the device in the mount table.

Control flow/state: no state in the header; callers query synchronously.

Dependencies/integration: implementation is platform-selected. Used by code that wants to warn or refuse operations on mounted devices.

Risks/test signals: return 0 can mean "not mounted" or "mount enumeration unsupported/unavailable." Callers should account for that ambiguity.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/mountcheck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/nowarn_snprintf.h -->
# sources/test-tools/fio/lib/nowarn_snprintf.h

Purpose: wraps `vsnprintf` while locally suppressing GCC 8+ `-Wformat-truncation` diagnostics.

Important APIs/functions: inline `nowarn_snprintf(char *str, size_t size, const char *format, ...)`.

Control flow/state: starts a `va_list`, pushes diagnostic state for GCC >= 8, calls `vsnprintf`, restores diagnostics, ends the varargs, and returns the `vsnprintf` result.

Dependencies/integration: includes `stdio.h` and `stdarg.h`. Used where truncation is intentional or externally bounded and the normal warning would be noisy.

Risks/test signals: suppressing warnings can hide real truncation bugs, so use should be narrow. Tests should verify return values match `snprintf` and that truncation behavior is still caller-checked where correctness matters.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/nowarn_snprintf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/num2str.c -->
# sources/test-tools/fio/lib/num2str.c

Purpose: converts numeric quantities to human-readable strings with SI/IEC prefixes and units.

Important APIs/functions: `bytes2str_simple` writes a two-decimal IEC byte string into a caller buffer; `num2str` returns a malloc-owned compact string constrained by a maximum numeric length and unit type.

Control flow: `bytes2str_simple` repeatedly divides by 1024 and formats `"%.2f %sB"`. `num2str` chooses SI or IEC prefixes, optionally converts bytes to bits, adjusts the starting prefix from `base`, divides until the integer part fits `maxlen`, applies carry rounding, and formats with `asprintf`.

State/persistence: no global mutable state. `num2str` allocates and transfers ownership to the caller; `bytes2str_simple` uses caller storage.

Dependencies/integration: uses fio `asprintf`, compile-time assertions, and `num2str.h` units. Used in human-readable status/stat output.

Risks/test signals: comments acknowledge rounding imprecision. Multiplying by 8 for bit units can overflow `uint64_t`. Tests should cover exact boundaries around 1000/1024, carry rounding, all unit modes, and allocation failure behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/num2str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/num2str.h -->
# sources/test-tools/fio/lib/num2str.h

Purpose: declares numeric formatting helpers and unit kinds.

Important APIs/types: `enum n2s_unit` values for none, per-second, byte, bit, byte/s, and bit/s; `num2str`; and `bytes2str_simple`.

Control flow/state: callers choose base, prefix family, maximum length, and units, then free `num2str` results. `bytes2str_simple` is non-allocating.

Dependencies/integration: includes fixed-width integers. Used by fio output code.

Risks/test signals: callers must manage allocated strings and provide adequate buffers for simple formatting. Tests should verify all enum values and boundary formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/num2str.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/output_buffer.c -->
# sources/test-tools/fio/lib/output_buffer.c

Purpose: dynamic append-only byte buffer used by fio formatted output helpers.

Important APIs/functions: `buf_output_init`, `buf_output_free`, and `buf_output_add`.

Control flow: initialization zeroes capacity, length, and pointer. Add grows the buffer by at least 1024 bytes or the required deficit, zeroes part of the newly exposed region, copies the input bytes to the current end, and advances length. Free releases storage and resets the struct.

State/persistence: owns heap storage in `struct buf_output`; contents are not automatically NUL-terminated by length, though growth zeroing often leaves spare zero bytes after appended data.

Dependencies/integration: uses `minmax.h`. Consumed by JSON and logging functions for in-memory output assembly.

Risks/test signals: `realloc` failure is not checked before assigning `out->buf`, which can lose the old buffer and crash on subsequent `memset`/`memcpy`. Tests should cover growth, zero-length additions, large additions, and allocation-failure behavior under fault injection.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/output_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/output_buffer.h -->
# sources/test-tools/fio/lib/output_buffer.h

Purpose: declares `struct buf_output` and append/free helpers for dynamic output accumulation.

Important APIs/types: `struct buf_output { char *buf; size_t buflen; size_t max_buflen; }`, `buf_output_init`, `buf_output_free`, and `buf_output_add`.

Control flow/state: callers initialize before first use, append bytes, read `buf`/`buflen`, then free. The buffer can contain arbitrary bytes, not only C strings.

Dependencies/integration: includes `stddef.h`. Used by `log_buf` and JSON printing.

Risks/test signals: callers must not assume `buf` is non-null or NUL-terminated without checking length/capacity behavior. Tests should verify lifecycle and repeated append behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/output_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/pattern.c -->
# sources/test-tools/fio/lib/pattern.c

Purpose: parses, copies, compares, and fills fio buffer verification patterns. Inputs can combine quoted strings, quoted file contents, decimal values, hexadecimal byte strings, and placeholder formats such as `%o`.

Important APIs/functions: `parse_and_fill_pattern_alloc`, `cpy_pattern`, `cmp_pattern`, `paste_format_inplace`, and `paste_format`. Internal parsers handle file reads, quoted strings, decimal/hex numbers, and format descriptors.

Control flow: parsing first supports a sizing pass with `out == NULL`, then allocates and performs a fill pass. `cpy_pattern` copies one pattern chunk and duplicates it exponentially across the output. `cmp_pattern` first checks repeated pattern structure inside the buffer, then compares against the expected pattern offset. Paste functions reserve descriptor-sized holes and later invoke descriptor callbacks to write dynamic fields.

State/persistence: file pattern parsing reads external files; allocated pattern buffers are returned to callers. Format arrays are caller-provided and filled with offsets and descriptors.

Dependencies/integration: uses `strntol`, fio `min`, `strcasestr`, `strndup`, file I/O, errno values, and pattern descriptors from `pattern.h`. It integrates with verify buffer generation and dynamic offset insertion.

Risks/test signals: quoted strings cannot escape quotes; file reads can truncate to `out_len`; decimal parsing is limited to `INT_MIN..INT_MAX`; hex parsing has special handling for adjacent `0x`. Tests should cover malformed inputs, maximum pattern size, file patterns, placeholders crossing pattern length, copy/compare offsets, and negative decimal byte order.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/pattern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/pattern.h -->
# sources/test-tools/fio/lib/pattern.h

Purpose: public interface for fio pattern parsing and dynamic placeholder filling.

Important APIs/types: `MAX_PATTERN_SIZE`, `struct pattern_fmt_desc` with format string, reserved length, and paste callback; `struct pattern_fmt` with output offset and descriptor; parse, paste, copy, and compare function declarations.

Control flow/state: callers define supported placeholder descriptors, parse user pattern text into a pattern buffer plus `pattern_fmt` entries, and later paste runtime values into those entries before IO or verification.

Dependencies/integration: no includes; designed for use by option parsing and verify buffer code.

Risks/test signals: descriptor callbacks must tolerate partial lengths when a format extends beyond a shorter output buffer. Tests should validate descriptor count accounting and callback error propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/pattern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/pow2.h -->
# sources/test-tools/fio/lib/pow2.h

Purpose: inline helper for power-of-two validation.

Important APIs/functions: `is_power_of_2(uint64_t val)` returns true for nonzero values with a single set bit.

Control flow/state: pure bit test `(val & (val - 1)) == 0` with explicit nonzero guard.

Dependencies/integration: includes fixed-width integers and fio bool definitions. Used by option validation and alignment/math code.

Risks/test signals: none beyond type width. Tests should cover zero, one, powers of two, and adjacent non-powers.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/pow2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/prio_tree.c -->
# sources/test-tools/fio/lib/prio_tree.c

Purpose: radix priority search tree for storing intervals and enumerating overlaps in `O(log n + m)` style.

Important APIs/functions: `prio_tree_replace`, `prio_tree_insert`, `prio_tree_remove`, and `prio_tree_next`. Static helpers expand root index width, navigate left/right/parent during overlap iteration, and compare interval overlap.

Control flow: insertion expands the tree when the new interval's heap index exceeds current capacity, swaps nodes to maintain priority by highest `last`, and branches by radix index then interval size. Removal replaces the removed node with a descendant preserving heap priority. Iteration initializes on first `prio_tree_next`, performs pre-order traversal, prunes branches whose heap/radix ranges cannot overlap, and returns matching nodes.

State/persistence: mutates caller-embedded `prio_tree_node` links and root index bits. No allocation or locking.

Dependencies/integration: derived from Linux priority tree code, uses `compiler.h` init attribute to fill `index_bits_to_maxindex`. Suitable for interval overlap queries such as file/page ranges.

Risks/test signals: tree invariants are complex, especially expansion and removal. Tests should cover duplicate intervals, nested/overlapping/non-overlapping intervals, removal of root/internal/leaf nodes, and full traversal after mutations.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/prio_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/prio_tree.h -->
# sources/test-tools/fio/lib/prio_tree.h

Purpose: declares priority search tree node/root/iterator structures and inline initialization/query helpers.

Important APIs/types: `struct prio_tree_node` with `start` and inclusive `last`, `struct prio_tree_root`, `struct prio_tree_iter`, initialization macros, `prio_tree_iter_init`, emptiness/root helpers, `prio_tree_entry`, and mutation/iteration prototypes.

Control flow/state: callers embed nodes in their own objects, initialize roots and nodes, set interval bounds before insertion, and use `prio_tree_iter_init` plus repeated `prio_tree_next` for overlap queries.

Dependencies/integration: includes fixed-width integers. The implementation assumes sentinel self-pointers for empty child/root states.

Risks/test signals: callers must initialize nodes and must not alter `start/last` while inserted. Tests should assert iterator correctness for inclusive endpoints.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/prio_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/rand.c -->
# sources/test-tools/fio/lib/rand.c

Purpose: fio pseudo-random generator initialization and buffer-filling utilities.

Important APIs/functions: `init_rand`, `init_rand_seed`, `__init_rand64`, `__fill_random_buf`, `fill_random_buf`, `__fill_random_buf_percentage`, and `fill_random_buf_percentage`. It supports 32-bit Taus88 and 64-bit Taus258 state from inline generators in `rand.h`.

Control flow: seeding uses LCG steps with minimum state constraints and cranks the generator several times. Buffer filling obtains a seed, hashes it through one or multiple seed buckets, and writes deterministic 64-bit words plus tail bytes. Percentage filling alternates random chunks with zero or caller pattern chunks per segment.

State/persistence: mutates caller-owned `frand_state`; writes caller buffers. Global `arch_random` is declared but not used in this file.

Dependencies/integration: depends on `pattern.h` for `cpy_pattern` and `hash.h` for `__hash_u64`. Used throughout fio for repeatable data patterns and random decisions.

Risks/test signals: expressions like `(2^31)` are C XOR, not exponentiation, but may be inherited intentionally from old seeding code; changing them affects reproducibility. Percentage math and segment tails need boundary tests. Signals include deterministic seeds, identical buffers for identical seeds, and correct pattern/random ratios.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/rand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/rand.h -->
# sources/test-tools/fio/lib/rand.h

Purpose: declares fio random state types and inline random number generation helpers.

Important APIs/types: `struct taus88_state`, `taus258_state`, `frand_state`, max constants, `rand_max`, copy helpers, inline `__rand32`, `__rand64`, `__rand`, `__rand_0_1`, bounded `rand32_upto`/`rand64_upto`, `rand_between`, `__get_next_seed`, and external initialization/fill functions.

Control flow/state: callers choose 32- or 64-bit mode in `frand_state`; every random draw mutates embedded Tausworthe state. Bounded helpers scale random integers through double arithmetic.

Dependencies/integration: includes fio bool and assertions. Used by distributions, data fill, benchmarks, and workload selection.

Risks/test signals: bounded generation can have rounding bias, especially for large 64-bit ranges. Tests should cover repeatability, state copying, boundary values, and 32/64-bit mode assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/rand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/rbtree.c -->
# sources/test-tools/fio/lib/rbtree.c

Purpose: Linux-derived red-black tree balancing and traversal primitives for fio intrusive tree users.

Important APIs/functions: `rb_insert_color`, `rb_erase`, `rb_first`, and `rb_next`. Internal helpers rotate left/right and repair colors after deletion.

Control flow: callers perform ordinary BST insertion with `rb_link_node`, then call `rb_insert_color` to rebalance. Erase handles zero/one/two-child removal, swaps successor state when needed, and rebalances black-height violations. Traversal returns leftmost node and in-order successor.

State/persistence: mutates caller-embedded `fio_rb_node` parent/color and child pointers plus root. No allocation or locking.

Dependencies/integration: includes `rbtree.h`. Used by iolog verification history and other ordered fio structures.

Risks/test signals: callers own key comparison and duplicate handling; misuse can violate tree order even if colors are valid. Tests should insert/erase varied key sequences, verify in-order traversal, and validate color/black-height invariants.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/rbtree.h -->
# sources/test-tools/fio/lib/rbtree.h

Purpose: declares intrusive red-black tree data structures and helper macros.

Important APIs/types: `struct fio_rb_node`, `struct rb_root`, color/parent macros, `RB_ROOT`, `rb_entry`, empty/clear helpers, `rb_insert_color`, `rb_erase`, `rb_first`, `rb_next`, and `rb_link_node`.

Control flow/state: callers embed `fio_rb_node`, maintain search/insert order, link a red node, rebalance, and erase/traverse as needed. Parent pointer and color share low bits in `rb_parent_color`.

Dependencies/integration: uses `container_of`, expected from fio/linux-style headers. Alignment is set to `sizeof(long)` to preserve low pointer bits.

Risks/test signals: nodes must be aligned and initialized/cleared before empty-node checks. Tests should cover embedding through `rb_entry` and parent/color bit packing on supported architectures.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/rbtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/roundup.h -->
# sources/test-tools/fio/lib/roundup.h

Purpose: rounds an unsigned depth up to a power-of-two-style size used for log buffers.

Important APIs/functions: `roundup_pow2(unsigned depth)` returns `1UL << __fls(depth - 1)`.

Control flow/state: pure inline computation using `__fls` from `lib/fls.h`. For powers of two it returns the same value; for non-powers it returns the next power of two.

Dependencies/integration: included by iolog setup to size pending sample buffers when iodepth exceeds default entries.

Risks/test signals: `depth == 0` underflows before `__fls`; callers must avoid zero. Tests should cover powers, non-powers, and documented caller preconditions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/roundup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/seqlock.h -->
# sources/test-tools/fio/lib/seqlock.h

Purpose: lightweight sequence lock for single-writer/multiple-reader style data snapshots.

Important APIs/types: `struct seqlock` with volatile or C++ atomic sequence, `seqlock_init`, `read_seqlock_begin`, `read_seqlock_retry`, `write_seqlock_begin`, and `write_seqlock_end`.

Control flow: readers spin until they observe an even sequence, read protected data externally, then retry if the sequence changed. Writers increment to odd at begin and store-release an even value at end.

State/persistence: one sequence counter; protected payload lives outside this struct. No writer serialization is provided by this type itself.

Dependencies/integration: depends on fio arch atomics, barriers, and `nop`. Used where fio wants low-cost lockless reads.

Risks/test signals: multiple concurrent writers require external locking. Readers can spin if a writer stalls mid-update. Tests should exercise retry behavior and memory ordering on supported architectures.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/seqlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/strntol.c -->
# sources/test-tools/fio/lib/strntol.c

Purpose: bounded-length wrapper around `strtol`.

Important APIs/functions: `strntol(const char *str, size_t sz, char **end, int base)`.

Control flow: skips leading spaces within the bounded region, rejects empty or too-large slices for its 24-byte stack buffer, copies exactly `sz` bytes to a NUL-terminated buffer, calls `strtol`, and maps the returned end pointer back into the original string.

State/persistence: no state. Returns 0 and sets `end` to original `str` on rejected sizes.

Dependencies/integration: used by pattern parsing when decimal text must stop before a later `0x` sequence or other bounded region.

Risks/test signals: the fixed buffer assumes LONG_MIN/MAX decimal representations fit under 24 bytes. Overflow is left as `strtol` result and errno behavior. Tests should cover leading spaces, partial strings, overflow, invalid input, and end-pointer mapping.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/strntol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/strntol.h -->
# sources/test-tools/fio/lib/strntol.h

Purpose: declares bounded string-to-long conversion.

Important APIs/functions: `long strntol(const char *str, size_t sz, char **end, int base)`.

Control flow/state: no header state; callers provide an explicit slice length and optional end pointer.

Dependencies/integration: includes `stdint.h` but the signature also relies on `size_t` being available from prior includes in some translation units.

Risks/test signals: the missing direct include for `stddef.h` can be fragile if included standalone. Compile tests should include this header in isolation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/strntol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/types.h -->
# sources/test-tools/fio/lib/types.h

Purpose: portability typedefs for bool and kernel async IO flags.

Important APIs/types: defines `bool`, `false`, and `true` when `CONFIG_HAVE_BOOL` is absent and not compiling as C++; otherwise includes `stdbool.h`. Defines `__kernel_rwf_t` as `int` when the platform lacks it.

Control flow/state: compile-time compatibility only; no runtime behavior.

Dependencies/integration: included by many fio utility headers so they can use bool consistently across C/C++ and old systems.

Risks/test signals: macro/config mismatches can conflict with system definitions. Compile matrix coverage across C, C++, and platforms with/without kernel `rwf_t` is the main signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/zipf.c -->
# sources/test-tools/fio/lib/zipf.c

Purpose: implements Zipf and Pareto non-uniform random distributions for fio range selection.

Important APIs/functions: `zipf_init`, `zipf_next`, `pareto_init`, `pareto_next`, and `zipf_disable_hash`. Static `zipf_update` computes the zeta normalization up to `min(nranges, 10M)`, and `shared_rand_init` seeds common state and center offset.

Control flow: Zipf init stores theta/zeta constants and precomputes normalization. `zipf_next` draws a uniform random value, maps it through Zipf equations, optionally hashes it, adds a random or centered offset, and mods by `nranges`. Pareto uses a precomputed exponent from `h` and similar hash/offset mapping.

State/persistence: mutable `zipf_state` contains distribution parameters, RNG state, offset, and hash-disable flag. No heap allocation.

Dependencies/integration: depends on `math.h`, fio RNG, hash, and min macros. Used by random workload distribution options.

Risks/test signals: `nranges == 0`, invalid theta/h, or extreme values can cause division/modulo issues. The 10M cap trades accuracy for startup time. Tests should check bounds, determinism, center behavior, hash disable behavior, and rough distribution shape.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/zipf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/lib/zipf.h -->
# sources/test-tools/fio/lib/zipf.h

Purpose: declares shared state and APIs for Zipf/Pareto random distributions.

Important APIs/types: `struct zipf_state` with range count, theta, zeta values, Pareto exponent, embedded RNG, random offset, and hash-disable bool; `zipf_init`, `zipf_next`, `pareto_init`, `pareto_next`, and `zipf_disable_hash`.

Control flow/state: callers initialize one state per stream and repeatedly call next functions. The same struct supports both Zipf and Pareto depending on initialization.

Dependencies/integration: includes `rand.h` and bool types. Consumed by fio workload randomization code.

Risks/test signals: callers must not mix next functions with the wrong initialization without understanding shared fields. Tests should verify API-level bounds and reproducible sequences.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/lib/zipf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/libfio.c -->
# sources/test-tools/fio/libfio.c

Purpose: central fio library initialization, teardown, runstate utilities, termination signaling, IO counter resets, and environment/architecture metadata.

Important APIs/functions: `clear_io_state`, `reset_all_stats`, `reset_fio_state`, `fio_get_os_string`, `fio_get_arch_string`, `runstate_to_name`, `td_set_runstate`, `td_bump_runstate`, `td_restore_runstate`, `fio_mark_td_terminate`, `fio_terminate_threads`, `fio_running_or_pending_io_threads`, `fio_set_fd_nonblocking`, `initialize_fio`, and `deinitialize_fio`.

Control flow: initialization performs compile-time layout assertions, runtime endian validation, architecture init, smalloc init, file lock and file hash init, locale setup, page-size discovery, and keyword initialization. Reset paths zero counters, close/reposition files, reseed random generators when requested, clear inflight IO, reset runtime/stat timestamps, and helper state. Termination iterates thread data and either marks terminate, sends SIGTERM, or calls engine terminate hooks depending on state.

State/persistence: owns global `disk_list`, `arch_flags`, `page_mask`, and `page_size`; mutates thread/job globals such as group and segment counters; updates `thread_data` runstate and termination fields.

Dependencies/integration: includes core fio headers, OS/arch layers, file locks, helper threads, file hashes, locale, signals, and fcntl. It is an integration hub for almost every fio subsystem.

Risks/test signals: endian/config mismatch aborts initialization; runstate transitions are not independently synchronized here; termination behavior depends on process/thread model and IO engine hooks. Tests should cover initialization failure paths, page-size setup, runstate naming assertions, and reset behavior across time-based/verify jobs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/libfio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/log.c -->
# sources/test-tools/fio/log.c

Purpose: common text logging for fio info, error, debug-prefix, buffer-backed, backend, and syslog outputs.

Important APIs/functions: `log_info_buf`, `log_valist`, optional `log_prevalist`, `log_info`, `__log_buf`, `log_info_flush`, `log_err`, and `log_get_level`.

Control flow: info logging first tries backend server text output, then syslog, then `f_out`. Error logging formats into a heap buffer, sends to backend if possible, otherwise syslog or `stderr` plus `f_err`. `__log_buf` formats into temporary storage and appends to a `buf_output`. Debug prefixing adds level name and thread id when debug filtering allows it.

State/persistence: uses global output streams `f_out`, `f_err`, and global flags such as `is_backend` and `log_syslog`. It allocates temporary formatted strings with `vasprintf/asprintf`.

Dependencies/integration: includes `fio.h`, server output paths, syslog, and `oslib/asprintf`. `log_buf` in the header routes callers here.

Risks/test signals: `fwrite` return values are item counts, not byte counts, so callers should not overinterpret returned lengths. Error logging writes to both stderr and `f_err` when distinct. Tests should cover backend fallback, syslog mode, null info buffer, and buffer appends.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/log.h -->
# sources/test-tools/fio/log.h

Purpose: declares fio logging APIs and severity constants.

Important APIs/types: global `FILE *f_out`/`f_err`, printf-checked `log_err` and `log_info`, `__log_buf`, `log_valist`, `log_prevalist`, `log_info_buf`, `log_info_flush`, `log_get_level`, and macro `log_buf`.

Control flow/state: `log_buf` writes into a provided `buf_output` or falls back to `log_info` when the buffer is null. Severity enum values map debug/info/error levels.

Dependencies/integration: includes `output_buffer.h`, stdio, stdarg, and unistd. Widely used across fio for status and diagnostics.

Risks/test signals: macro evaluates the buffer argument more than once only as written in the conditional expression; callers should avoid side-effect arguments. Compile tests should preserve printf attribute checking.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/memory.c -->
# sources/test-tools/fio/memory.c

Purpose: implements IO buffer memory allocation, freeing, and optional memory pinning for fio jobs.

Important APIs/functions: `fio_pin_memory`, `fio_unpin_memory`, `allocate_io_mem`, and `free_io_mem`. Static helpers allocate/free memory via SysV shared memory, anonymous/file mmap, malloc, CUDA device memory, and hugepage variants.

Control flow: pinning maps anonymous memory and `mlock`s up to requested `lockmem`, clamping against physical memory with 128 MiB reserve. IO allocation computes total buffer size including direct-IO/page/mem alignment overhead, respects IO-engine custom allocators unless user options conflict, then dispatches by `mem_type`. Free mirrors the selected allocation path, closing/unlinking mmap files when appropriate and destroying CUDA resources.

State/persistence: mutates `thread_data` fields such as `pinned_mem`, `orig_buffer`, `orig_buffer_size`, `shm_id`, `mmapfd`, mmap keep flags, CUDA context/device pointers, and option-owned `mmapfile`. Shared memory and mmap files are OS resources that must be cleaned up.

Dependencies/integration: relies on fio options, IO engine flags/hooks, OS memory macros, hugepage config, CUDA config, logging, and error recording.

Risks/test signals: resource cleanup is complex on partial failure, especially shm attach failure, mmap open/truncate failure, and CUDA context allocation. `free_mem_mmap` uses `td->orig_buffer_size` in `munmap` despite receiving `total_mem`, so alignment-overhead accounting should be scrutinized. Tests should cover each memory mode, hugepage failures, engine allocator conflict, and mmapfile keep/unlink behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/minmax.h -->
# sources/test-tools/fio/minmax.h

Purpose: type-checking min/max macros and a nonzero-aware minimum helper.

Important APIs/macros: `min(x,y)`, `max(x,y)`, and `min_not_zero(x,y)`.

Control flow/state: macros capture operands into temporary typed variables, compare addresses to force compatible types at compile time, and return the selected value. `min_not_zero` treats zero as "unset" unless both are zero.

Dependencies/integration: GCC statement-expression and `__typeof__` extensions are required. Widely used in fio utility and parsing code.

Risks/test signals: operands are evaluated once, but these macros are not portable ISO C. Tests are mostly compile-time/type-safety checks plus runtime checks for zero/nonzero combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/minmax.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/mock-tests/Makefile -->
# sources/test-tools/fio/mock-tests/Makefile

Purpose: build and run isolated fio mock tests, currently focused on latency precision.

Important targets/variables: `CC`, `CFLAGS`, `TEST_DIR`, `LIB_DIR`, `BUILD_DIR`, `TESTS`, `all`, `test`, `test-tap`, `test-%`, `clean`, and `help`.

Control flow: `all` creates `build` and compiles each test from `tests/*.c` with the TAP header dependency. `test` runs built binaries directly and counts failures. `test-tap` uses `prove -v` when available, otherwise falls back to direct execution.

State/persistence: creates and removes `mock-tests/build`; test output is printed to stdout/stderr. No integration with the top-level fio test runner is shown in this file.

Dependencies/integration: requires a C compiler, math library flag in `CFLAGS`, TAP-compatible test programs, and optionally Perl `prove`.

Risks/test signals: `-lm` appears in `CFLAGS` before the source/output in the compile rule, which can matter for linkers that require libraries after objects. Tests should run `make test` on target toolchains and verify `test-%` target names match declared test names.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/mock-tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/mock-tests/lib/tap.h -->
# sources/test-tools/fio/mock-tests/lib/tap.h

Purpose: header-only minimal Test Anything Protocol emitter for mock C tests.

Important APIs/functions: `tap_init`, `tap_plan`, `tap_ok`, `tap_skip`, `tap_diag`, `tap_within_tolerance`, and `tap_done`. Static header variables track test count, failure count, and whether a plan was printed.

Control flow: tests initialize, optionally plan, emit ok/not-ok lines with formatted descriptions, emit diagnostics prefixed with `#`, and return `tap_done` as process exit status. If no plan was printed, `tap_done` prints one using the observed count.

State/persistence: per-translation-unit static counters in the header. No allocation or files.

Dependencies/integration: standard C stdio/stdarg/stdbool only. Used by `mock-tests/tests/test_latency_precision.c`.

Risks/test signals: because state is header-static, including it in multiple translation units would create independent TAP counters. `tap_skip` prints `ok N # SKIP` without a dash description. Tests should verify TAP output remains accepted by `prove`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/mock-tests/lib/tap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/mock-tests/tests/test_latency_precision.c -->
# sources/test-tools/fio/mock-tests/tests/test_latency_precision.c

Purpose: isolated regression-style mock test for latency sum precision and long-running average recovery in fio steady-state/stat calculations.

Important APIs/functions: mock `fio_fp64_t` and `clat_stat`; `calc_lat_sum_original`; `calc_lat_sum_improved`; test groups `test_normal_values`, `test_edge_cases`, `test_accumulation_precision`, `test_precision_improvements`, `test_overflow_detection`, `test_long_running_precision`; and `main`.

Control flow: `main` emits a TAP plan for 15 tests, runs each group, and returns `tap_done`. Tests compare original and improved calculations for ordinary values, zero samples, near-overflow safe values, accumulation across mock threads, fractional precision, overflow detection using doubles, and recovering per-second latency after a large sample history.

State/persistence: all state is local mock data; no fio runtime structures or files are used. The long-running test mutates an average using the same incremental mean formula described in comments.

Dependencies/integration: includes math/float/stdint/string and the local TAP helper. It is a focused model of a fio stats concern, not linked against fio proper.

Risks/test signals: some tests assert original and improved values are equal, so they mostly protect refactoring and edge handling rather than proving a behavioral difference. Test 10 always passes after printing direct/cast values. The strongest signal is the long-running per-second latency tolerance.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/mock-tests/tests/test_latency_precision.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/optgroup.c -->
# sources/test-tools/fio/optgroup.c

Purpose: maps fio option category and category-group bitmasks to user-facing group names.

Important APIs/functions: `opt_group_from_mask` and `opt_group_cat_from_mask`, both backed by static `fio_opt_groups`, `fio_opt_cat_groups`, and `group_from_mask`.

Control flow: callers pass a mutable mask. `group_from_mask` returns null for invalid/all/zero masks, scans the configured table for the first matching bit, clears that bit from the caller mask, and returns the matching descriptor. Repeated calls enumerate all set groups.

State/persistence: static read-only group tables; caller-owned mask is mutated to track enumeration progress.

Dependencies/integration: includes `optgroup.h` and compiler compile-time assertions. Used by option help/output formatting to organize options.

Risks/test signals: table coverage must stay in sync with enum bits; new enum values without table entries will be silently skipped until the mask is exhausted. Tests should iterate every category/group bit and verify expected display names or intentional omissions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/optgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/optgroup.h -->
# sources/test-tools/fio/optgroup.h

Purpose: declares option grouping bitmasks and lookup functions for fio options.

Important APIs/types: `struct opt_group`, `enum opt_category`, `enum opt_category_group`, bitmask constants such as `FIO_OPT_C_IO` and `FIO_OPT_G_IOLOG`, invalid sentinels, and lookup prototypes.

Control flow/state: categories are powers of two intended to be combined into `uint64_t` masks. Lookup functions consume masks bit by bit and return descriptors from implementation tables.

Dependencies/integration: requires `uint64_t` from prior includes or translation-unit context; implementation includes `inttypes.h`, but the header itself does not. Used by parser/help code assigning options to categories.

Risks/test signals: enum order and bit assignments are ABI-like within fio help/parser data. Header standalone compilation should be checked because it uses `uint64_t` without including `<stdint.h>`/`<inttypes.h>`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/optgroup.h -->

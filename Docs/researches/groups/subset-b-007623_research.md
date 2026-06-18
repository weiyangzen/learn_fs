# Research Group subset-b-007623

This grouped report covers the LizardFS `src/common` files assigned to `subset-b-007623`. Each section is delimited for reconciliation into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/compact_vector.h -->
# sources/distributed-fs/lizardfs/src/common/compact_vector.h

Purpose: implements `compact_vector`, a memory-compact `std::vector`-like container for cases where payload storage matters more than amortized growth. It deliberately keeps capacity equal to size and uses internal storage or pointer/size packing on 64-bit builds.

Important APIs/types/functions: `detail::compact_vector_storage` has three storage variants: generic pointer+size, trivial small internal buffer, and 64-bit pointer-obfuscating storage that packs size into unused pointer bits. `compact_vector_base` owns allocation/deallocation. `detail::normal_iterator` provides random-access iterator behavior. `compact_vector` exposes constructors, assignment, `resize`, iterators, element access, `push_back`, `emplace`, `insert`, `erase`, relational operators, and `swap`.

Control flow: mutating operations allocate exactly the new size, construct new elements, move/copy existing ranges, then call `set_new_ptr` to destroy/deallocate old storage. In-place insert paths are used when the allocator returns the same internal buffer. Exception paths destroy partially constructed ranges and restore the old pointer.

State and persistence: state is only in-memory: packed storage, optional debug pointer, size, and element payload. It has no persistence or synchronization. Iterator/pointer invalidation is aggressive because any size change can reallocate.

Dependencies and integration: depends on allocator traits, `platform.h`, standard algorithms, and raw placement/destruction. Used by `id_pool.h` as a dense bit-vector block and likely throughout common code where lower object size is desirable.

Risks: the 64-bit pointer packing relies on allocator alignment and virtual-address assumptions; `assert` guards vanish in release builds. `reserve` is a no-op, so callers expecting vector amortization can get O(n^2) behavior. The overload set at the bottom uses `compact_vector<Tp, Alloc>` and therefore treats the second template argument as the size type, not allocator, which is easy to misuse with the three-parameter template.

Test signals: `compact_vector_unittest.cc` compares core behavior with `std::vector`, checks iterator traversal, insert/erase, move assignment, and validates internal-storage size and address behavior on 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/compact_vector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/compact_vector_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/compact_vector_unittest.cc

Purpose: GoogleTest coverage for `compact_vector` behavior against `std::vector` expectations.

Important APIs/types/functions: defines comparison helpers between `compact_vector<T>` and `std::vector<T>`, then tests construction/copy/move, range insert, erase, iterator arithmetic and conversion, internal storage, and a GCC6 regression around pushing a `uint32_t`.

Control flow: tests build equivalent standard and compact vectors, perform identical mutations, and assert content equality. The internal-storage test branches out on non-64-bit platforms, then checks object size, `max_size`, and whether `data()` points into the vector object before and after crossing inline capacity.

State and persistence: test-only heap/stack state; no persistence.

Dependencies and integration: includes `common/compact_vector.h`, `gtest`, `algorithm`, and `numeric`. It validates ABI-sensitive behavior that other compact data structures, notably `IdPoolBlock`, rely on.

Risks: coverage does not stress exceptions, non-trivial throwing element types, allocator variants, or all insert corner cases. It also relies on pointer-obfuscation assumptions that may differ under sanitizers or unusual allocators.

Test signals: the file itself is the signal; it verifies parity with `std::vector` for representative operations and explicitly guards the 64-bit packed/internal-storage contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/compact_vector_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/connection_pool.cc -->
# sources/distributed-fs/lizardfs/src/common/connection_pool.cc

Purpose: implements a thread-safe connection reuse pool keyed by `NetworkAddress`.

Important APIs/types/functions: `ConnectionPool::putConnection` stores a file descriptor with timeout; `getConnection` returns a valid descriptor or `-1`; `cleanup` removes timed-out connections and closes their descriptors.

Control flow: `getConnection` loops while stale descriptors are found. It locks, pops the oldest connection for an address, unlocks, then either returns the descriptor if still valid or closes it and retries. `cleanup` walks all address lists under lock, records stale fds, erases empty map entries, unlocks, and closes descriptors outside the mutex.

State and persistence: state is in-memory `std::map<NetworkAddress, std::list<Connection>>` guarded by `mutex_`. There is no persistence; fd ownership transfers to the pool on `putConnection` and back to the caller on successful `getConnection`.

Dependencies and integration: depends on `connection_pool.h`, `massert` assertions, and `tcpclose` from sockets. It integrates with network clients that want short-lived TCP connection reuse.

Risks: `putConnection` asserts `fd > 0`, excluding descriptor `0`; normal sockets usually satisfy this but the API is stricter than POSIX fd validity. `getConnection` leaves empty address entries in the map until `cleanup`. No maximum pool size is enforced, so repeated puts can accumulate until timeouts.

Test signals: no direct unittest in this subset. Behavior is mostly validated indirectly by networking users and would benefit from fake-clock/fake-close tests for timeout and concurrency paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/connection_pool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/connection_pool.h -->
# sources/distributed-fs/lizardfs/src/common/connection_pool.h

Purpose: declares `ConnectionPool`, a small synchronized cache of reusable network file descriptors grouped by remote address.

Important APIs/types/functions: public methods are `getConnection(const NetworkAddress&)`, `putConnection(int, const NetworkAddress&, int timeout)`, and `cleanup()`. The private nested `Connection` stores `fd_` and a `Timeout validUntil_` and exposes `fd()` and `isValid()`.

Control flow: the header establishes the ownership model: callers insert open descriptors with a timeout, later retrieve one descriptor or `-1`, and periodically call cleanup to close expired entries.

State and persistence: state is the guarded map of address to FIFO connection lists. The timeout uses `common/time_utils.h`; there is no durable state.

Dependencies and integration: depends on `NetworkAddress` ordering for use as a `std::map` key, `std::mutex`, and `Timeout`. It is an integration utility for common networking code.

Risks: the API lacks RAII ownership for returned descriptors; callers must close descriptors they retrieve and do not use. The class is non-copyable by implication because of `std::mutex`, but copy/delete semantics are not explicitly stated.

Test signals: no direct test in the mapped files; source inspection shows simple API surface but edge cases around timeout and fd lifecycle need integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/connection_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/coroutine.h -->
# sources/distributed-fs/lizardfs/src/common/coroutine.h

Purpose: provides stackless coroutine macros adapted from Boost.Asio-style coroutine support.

Important APIs/types/functions: `coroutine` stores an integer continuation value and reports parent/child/complete state. `detail::coroutine_ref` updates the stored state and marks coroutines complete when a reenter block exits without modification. Macros `CORO_REENTER`, `CORO_YIELD`, `CORO_FORK`, and aliases `reenter`/`yield` implement switch/goto-based suspension.

Control flow: user code wraps a stateful function body in `reenter(c)`, where `yield` stores a unique line/counter value and returns to the caller. Re-entry switches back to that case label. `fork` stores negative continuation values to distinguish child and parent flows.

State and persistence: state is a single integer in a `coroutine` object; no heap, no persistence, no thread safety.

Dependencies and integration: only depends on `platform.h`. It is meant for event-driven code that needs resumable logic without C++20 coroutines.

Risks: macro control flow is fragile: yields must not share line numbers on non-MSVC builds, scopes/cases can surprise users, and normal C++ lifetime rules around local variables crossing yields require care. It is not exception-aware beyond RAII of `coroutine_ref`.

Test signals: no direct test in this group; the code is a known pattern but should be exercised by users that depend on resumable protocol state machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/coroutine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/counting_sort.h -->
# sources/distributed-fs/lizardfs/src/common/counting_sort.h

Purpose: implements stable counting-sort helpers for integer-keyed ranges with small-vector-backed count/index storage.

Important APIs/types/functions: `counting_sort_copy(first,last,output,get_key)` builds prefix counts and writes sorted elements into `output`. `counting_sort(OutputIterator first,last,get_key)` intends to sort a range in place. `counting_sort(DataContainer&,get_key)` sorts a vector-like container by creating a same-sized result.

Control flow: `counting_sort_copy` resizes an index array to `max_key + 2`, accumulates counts shifted by one, prefix-sums them, then moves each input into `output[element_index[key]++]`, preserving relative order for equal keys.

State and persistence: temporary in-memory index vector and result storage only.

Dependencies and integration: depends on `small_vector.h` and iterator traits. It is useful for bounded non-negative key domains in planning and scheduling code.

Risks: keys are assumed non-negative and reasonably bounded after conversion to `std::size_t`; huge keys can allocate huge index vectors. The iterator overload appears defective: after sorting into `result`, it calls `std::copy(first, last, result.begin())`, which copies the original range into the result buffer rather than copying `result` back to `first`. The container overload uses the copy helper directly and assigns `data = std::move(result)`.

Test signals: `counting_sort_unittest.cc` covers only `counting_sort_copy`, including stability; it does not catch the in-place iterator overload issue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/counting_sort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/counting_sort_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/counting_sort_unittest.cc

Purpose: tests `counting_sort_copy` for normal sorting and stability.

Important APIs/types/functions: `CountingSort.SimpleSort` compares sorted random integers against `std::sort`. `CountingSort.StableSort` prepares pairs, sorts by secondary field first, then checks that counting sort by primary field matches `std::stable_sort`.

Control flow: the tests fill random vectors, allocate output vectors, call `counting_sort_copy`, then compare with standard-library sorted data.

State and persistence: test-only vectors; no persistence.

Dependencies and integration: includes `common/counting_sort.h`, `gtest`, `algorithm`, and `numeric`.

Risks: random data is unseeded and deterministic under many C libraries but not explicitly controlled. The tests do not call either `counting_sort` overload, so the iterator overload's copy-direction bug is not covered.

Test signals: validates copy-mode correctness for positive integer keys and stable ordering, but coverage is incomplete for API surface and pathological key sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/counting_sort_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/crc.cc -->
# sources/distributed-fs/lizardfs/src/common/crc.cc

Purpose: provides LizardFS CRC32 calculation, CRC concatenation, initialization, and empty-block CRC repair.

Important APIs/types/functions: `mycrc32`, `mycrc32_combine`, `mycrc32_init`, legacy table generators `crc_generate_main_tables` and `crc_generate_combine_tables`, and `recompute_crc_if_block_empty`.

Control flow: build-time branches select a fake CRC implementation when `ENABLE_CRC` is off, `crcutil::GenericCrc` when available, or legacy endian-aware table code otherwise. The legacy implementation aligns byte input, processes 32-byte and 4-byte chunks through precomputed tables, and uses GF(2) matrix-derived combine tables to concatenate CRCs. `recompute_crc_if_block_empty` checks for zero CRC and all-zero `MFSBLOCKSIZE` block before assigning the cached zero-block CRC.

State and persistence: legacy mode has static CRC tables and a static cached empty-block CRC. No persistence or synchronization; callers must ensure initialization where required.

Dependencies and integration: depends on `crc.h`, `protocol/MFSCommunication.h` for `CRC_POLY` and `MFSBLOCKSIZE`, optional `generic_crc.h`, and endian macros. It underpins block integrity and chunk verification.

Risks: fake CRC mode can mask corruption and must be build-controlled. The all-zero check uses `memcmp(block, block + 1, MFSBLOCKSIZE - 1)` and assumes the full block buffer is readable. Static initialization of `emptyBlockCrc` calls combine macros after `mycrc32_init` should have run in legacy mode.

Test signals: `crc_unittest.cc` covers known CRC values, zero block equivalence, and combine behavior across multiple tail lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/crc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/crc.h -->
# sources/distributed-fs/lizardfs/src/common/crc.h

Purpose: declares the CRC32 public API and helper macros used by data-integrity code.

Important APIs/types/functions: `mycrc32(crc, block, leng)`, `mycrc32_combine(crc1, crc2, leng2)`, `mycrc32_init()`, `recompute_crc_if_block_empty`, and macros for zero blocks, zero-expanded blocks, and XORed block CRCs.

Control flow: the macros compose the two fundamental functions to calculate CRC effects for implicit zero data and XOR relationships without reading full buffers.

State and persistence: the header itself has no state; implementation may use static tables.

Dependencies and integration: depends on `platform.h`, integer types, and the implementation's protocol constants. It is included by chunk storage and tests.

Risks: macro arguments can be evaluated multiple times, so callers should avoid side effects. The API uses 32-bit lengths; larger buffers require chunking.

Test signals: `crc_unittest.cc` validates public functions and zero-block macro behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/crc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/crc_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/crc_unittest.cc

Purpose: GoogleTest coverage for LizardFS CRC32 and CRC combination semantics.

Important APIs/types/functions: tests call `mycrc32`, `mycrc32_zeroblock`, and `mycrc32_combine` using fixed strings and `MFSBLOCKSIZE` buffers.

Control flow: `MyCrc32` compares several repeated-`a` strings to known external CRC32 values. `MfsCrc32Zeroblock` compares explicit zero-buffer CRC to the macro. `MyCrc32Combine` splits a full block at powers-of-two-related offsets and verifies combined CRC equals whole-buffer CRC.

State and persistence: test-only vectors and strings.

Dependencies and integration: includes `common/crc.h`, `protocol/MFSCommunication.h`, and `gtest`.

Risks: tests assume CRC is enabled or fake implementation is configured consistently; fake CRC would make known-value tests fail unless test selection changes. Coverage does not test `recompute_crc_if_block_empty` directly.

Test signals: strong signal for normal and concatenate CRC correctness over block-sized data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/crc_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cwrap.cc -->
# sources/distributed-fs/lizardfs/src/common/cwrap.cc

Purpose: implements small RAII and exception wrappers over POSIX/C filesystem APIs.

Important APIs/types/functions: `FileDescriptor` constructors/destructor, `get`, `reset`, `close`, `isOpened`; deleters `CFileCloser` and `CDirCloser`; `errorString`; namespace `fs` functions `exists`, `rename`, `remove`, `dirname`, `getCurrentWorkingDirectory`, and `getCurrentWorkingDirectoryNoThrow`.

Control flow: `FileDescriptor` closes an owned fd on reset/destruction. Filesystem wrappers call C APIs and throw `FilesystemException` on errors except `exists`, which treats `ENOENT` as false. `getCurrentWorkingDirectoryNoThrow` catches `FilesystemException`, logs a warning, and returns `"???"`.

State and persistence: `FileDescriptor` owns one fd in memory; wrappers mutate the filesystem through rename/remove but keep no persistent state themselves.

Dependencies and integration: depends on `cwrap.h`, `exceptions.h`, `massert`, `libgen`, `unistd`, and syslog helpers through exception/logging headers. It centralizes errno-to-exception behavior.

Risks: `FileDescriptor::close` ignores `::close` failure and asserts only that the fd was open. `dirname` uses `strdup` without checking null. `errorString` wraps `strerror`, which may be thread-local or static depending on platform.

Test signals: no direct tests in subset; behavior needs filesystem/error-injection coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cwrap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cwrap.h -->
# sources/distributed-fs/lizardfs/src/common/cwrap.h

Purpose: declares RAII wrappers and filesystem helper functions around C/POSIX resources.

Important APIs/types/functions: `FileDescriptor` is non-copyable and owns an integer fd. `CFileCloser`, `CDirCloser`, `cstream_t`, and `cdirectory_t` provide unique-pointer ownership for `FILE*` and `DIR*`. `errorString` and namespace `fs` expose existence, rename, remove, dirname, and cwd helpers.

Control flow: callers use wrappers to convert errno-producing C APIs into exceptions or RAII cleanup.

State and persistence: only owned descriptors/handles; filesystem effects are delegated to implementation.

Dependencies and integration: includes `dirent.h`, `sys/types.h`, `<cstdio>`, `<memory>`, and `<string>`. Used by common code that needs portable cleanup and consistent error reporting.

Risks: the documentation for `fs::exists` says "True iff given file does not exists", but implementation returns true when it exists. The API does not expose close error status.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cwrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/datapack.h -->
# sources/distributed-fs/lizardfs/src/common/datapack.h

Purpose: provides inline big-endian serialization/deserialization helpers for fixed-width integers in MooseFS/LizardFS protocol buffers.

Important APIs/types/functions: `put64bit`, `put32bit`, `put16bit`, `put8bit`, `get64bit`, `get32bit`, `get16bit`, and `get8bit`.

Control flow: each `put` writes bytes in network/big-endian order and advances a mutable `uint8_t**`. Each `get` reconstructs the integer from a `const uint8_t**` and advances the read pointer.

State and persistence: no internal state; it mutates caller-provided buffer pointers and buffer contents.

Dependencies and integration: depends only on `platform.h` and integer types. Used in low-level wire/disk record packing where avoiding stream abstractions matters.

Risks: no bounds checks, alignment checks, or null checks; callers must guarantee sufficient buffer. The pointer-to-pointer API is efficient but easy to misuse.

Test signals: no direct tests in this subset; protocol round-trip tests elsewhere likely cover it indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/datapack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/defective_file_info.h -->
# sources/distributed-fs/lizardfs/src/common/defective_file_info.h

Purpose: defines a small serializable record describing a defective file and associated error flags.

Important APIs/types/functions: uses `LIZARDFS_DEFINE_SERIALIZABLE_CLASS(DefectiveFileInfo, std::string file_name, uint8_t error_flags)`.

Control flow: all construction, field access, and serialization behavior is generated by the macro from `serialization_macros.h`.

State and persistence: serialized state consists of `file_name` and `error_flags`; persistence format is governed by the serialization macro framework.

Dependencies and integration: depends on `platform.h` and serialization macros. It integrates with reporting or protocol paths that send defective-file metadata.

Risks: behavior is opaque in this file because macro-generated code controls invariants and compatibility. Error flag semantics are not documented here.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/defective_file_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/disk_info.cc -->
# sources/distributed-fs/lizardfs/src/common/disk_info.cc

Purpose: implements accumulation of disk I/O statistics.

Important APIs/types/functions: `HddStatistics::add(const HddStatistics&)` sums byte, time, and operation counters and preserves maxima for read/write/fsync latency.

Control flow: simple field-wise addition, followed by max comparisons for `usecreadmax`, `usecwritemax`, and `usecfsyncmax`.

State and persistence: mutates the receiving `HddStatistics` object; serialized representation is defined in `disk_info.h`.

Dependencies and integration: depends on `common/disk_info.h`. Used by disk reporting to aggregate minute/hour/day or multi-disk statistics.

Risks: arithmetic can overflow silently on long-running or aggregated counters. No locking is provided for non-atomic `HddStatistics`.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/disk_info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/disk_info.h -->
# sources/distributed-fs/lizardfs/src/common/disk_info.h

Purpose: declares disk and HDD statistics structures for serialization and runtime atomic collection.

Important APIs/types/functions: `HddAtomicStatistics` stores atomic byte/time/op/max counters with `clear()`. `HddStatistics` is a serializable non-atomic snapshot with `clear()` and `add()`. `DiskInfo` serializes disk entry size, path, flags, last error chunk/time, space usage, chunk count, and minute/hour/day stats. Flags include delete, damaged, and scan-in-progress masks.

Control flow: atomic stats are reset by assigning zero to each atomic. Serializable macros generate snapshot fields and likely serialization functions.

State and persistence: `DiskInfo` and `HddStatistics` are persistence/protocol records. `HddAtomicStatistics` is runtime state intended for concurrent counters but max updates are just assignments in clear, not compare-exchange update helpers.

Dependencies and integration: depends on `MooseFsString` and `serialization_macros.h`. Used by chunkserver/master status and admin interfaces.

Risks: consumers must safely snapshot atomics into `HddStatistics`; this file does not provide that conversion. Flag masks are constants but there are no typed helpers enforcing valid combinations.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/disk_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/ec_read_plan.h -->
# sources/distributed-fs/lizardfs/src/common/ec_read_plan.h

Purpose: defines `ECReadPlan`, the erasure-coded slice read plan implementation that reconstructs missing parts through Reed-Solomon.

Important APIs/types/functions: `ECReadPlan : SliceReadPlan`; nested `RecoverParity` computes a parity part from continuous data parts; `postProcessRead` invokes base slice post-processing then calls `recoverParts` if requested parts were unavailable; `recoverParts` configures `ReedSolomon` fragment maps and erased map.

Control flow: `postProcessRead` builds an availability bitset from available chunk parts. If any requested part was missing, `recoverParts` chooses up to `k` available parts as data inputs, maps read operation buffers by slice part, maps missing requested parts to output positions, and calls `rs.recover`.

State and persistence: read-plan state is inherited: requested parts, read operations, buffer sizes, and slice type. No persistence.

Dependencies and integration: depends on `read_plan.h`, `slice_read_plan.h`, `reed_solomon.h`, `Goal::Slice::Type`, and protocol block size. It integrates with `SliceReadPlanner` and `ChunkReadPlanner`.

Risks: relies heavily on assertions for valid EC type, buffer bounds, and matching slice type. The recovery map chooses erased parts once `available_count >= k`, which is correct for decoding but sensitive to read operation preparation.

Test signals: `ec_read_plan_unittest.cc` exercises missing data/parity reads and whole-chunk reconstruction through planner/tester utilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/ec_read_plan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/ec_read_plan_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/ec_read_plan_unittest.cc

Purpose: tests EC read planning and reconstruction behavior through higher-level planners.

Important APIs/types/functions: helper `ec(k,m,part_index)`, `checkReadingParts`, and `checkReadingChunk`. Tests `VerifyRead1` through `VerifyRead5` target slice-part reads; `VerifyChunkRead1` targets standard chunk reconstruction from EC parts.

Control flow: helpers synthesize part data, prepare planners with target and available parts, assert reading is possible, build a plan, execute it through `ReadPlanTester`, then compare output buffer regions against expected part data.

State and persistence: test-only maps of part data and planner buffers.

Dependencies and integration: includes `slice_read_planner.h`, `chunk_read_planner.h`, chunk type constants, and test plan executor. It validates integration rather than only `ECReadPlan` internals.

Risks: tests cover a small set of `(3,2)` EC cases and do not sweep larger data/parity counts, all parity losses, or impossible read scenarios.

Test signals: strong integration signal that EC planner and Reed-Solomon recovery produce expected buffers for representative missing parts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/ec_read_plan_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/errno_defs.h -->
# sources/distributed-fs/lizardfs/src/common/errno_defs.h

Purpose: provides missing POSIX errno constants on Windows builds.

Important APIs/types/functions: defines `ENODATA`, `ENOTBLK`, `EDQUOT`, and `ETXTBSY` under `_WIN32`.

Control flow: preprocessor-only compatibility shim.

State and persistence: none.

Dependencies and integration: includes `platform.h`; used where cross-platform code references Unix errno names.

Risks: numeric values are compatibility choices and may not map to native Windows errors. Definitions are skipped on non-Windows platforms to avoid conflicts.

Test signals: no direct tests; build coverage on Windows is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/errno_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/event_loop.cc -->
# sources/distributed-fs/lizardfs/src/common/event_loop.cc

Purpose: implements the global single-threaded event loop used by daemon-style LizardFS components.

Important APIs/types/functions: global `gExitingStatus`, `gReloadRequested`, lists of poll/time/destruct/can-exit/want-exit/reload/each-loop handlers, `eventloop_run`, registration functions, time registration/change/unregister, `eventloop_want_to_terminate`, `eventloop_want_to_reload`, and `eventloop_updatetime`.

Control flow: each loop builds poll descriptors by calling registered `desc` callbacks, polls for up to 50 ms or nonblocking once, updates time, serves poll callbacks, runs each-loop callbacks, handles clock jumps, fires due timers, reloads config after the current iteration, and progresses graceful exit from `kWantExit` to `kCanExit` to `kDoExit`.

State and persistence: global in-memory callback lists and atomic current time values. No persistence. It is not designed for multiple independent loop instances.

Dependencies and integration: depends on `event_loop.h`, `cfg_reload`, `Exception`, `massert`, syslog, `poll` or `tcppoll`. It is a core integration point for modules that register periodic, IO, cleanup, reload, and shutdown handlers.

Risks: global mutable state makes tests and reentrancy hard. Callback registration/unregistration is not synchronized. Timer handles are raw addresses into a `std::list`; unregistering unknown handles aborts. Exceptions are caught only in destruct/reload callbacks, not poll/timer/each-loop callbacks.

Test signals: no direct tests in subset; daemon integration tests are needed for lifecycle, timers, and shutdown sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/event_loop.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/event_loop.h -->
# sources/distributed-fs/lizardfs/src/common/event_loop.h

Purpose: declares the global event-loop API and exit state machine.

Important APIs/types/functions: `ExitingStatus` enum, globals `gExitingStatus` and `gReloadRequested`, registration functions for destruct/can-exit/want-exit/reload/poll/each-loop, timer registration/change/unregister APIs in seconds and milliseconds, nonblocking poll request, termination/reload triggers, loop run/release/destruct, and time accessors.

Control flow: callers register callbacks before `eventloop_run`, then interact through termination/reload/time APIs during runtime.

State and persistence: declares global state owned by `event_loop.cc`; no persistent data.

Dependencies and integration: includes `poll.h` or Winsock types and standard containers. It is used by long-running LizardFS processes as a central scheduler.

Risks: C function-pointer API limits capture/context and pushes state to globals. The exposed globals allow external mutation outside API invariants.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/event_loop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/exception.h -->
# sources/distributed-fs/lizardfs/src/common/exception.h

Purpose: defines the base LizardFS exception class and macros for derived exception classes.

Important APIs/types/functions: `Exception` derives from `std::exception`, stores `message_` and `status_`, appends `lizardfs_error_string(status)` for known non-OK statuses, and exposes `what()`, `message()`, and `status()`. Macros create named exception classes with standard constructors.

Control flow: constructors set the message/status and assert that status is not `LIZARDFS_STATUS_OK`. Macro-generated derived classes forward to base constructors.

State and persistence: exception objects carry message/status only; no persistence.

Dependencies and integration: depends on `MFSCommunication.h` for status constants and `mfserr.h` for status strings. Used broadly by common wrappers and higher-level code.

Risks: macros generate many small classes but hide declarations from tools. `what()` returns a pointer into `std::string`, valid only while the exception object lives.

Test signals: no direct tests here; usage is exercised by exception-throwing modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/exception.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/exceptions.h -->
# sources/distributed-fs/lizardfs/src/common/exceptions.h

Purpose: declares common exception categories for configuration, filesystem, initialization, connections, reads, writes, CRC, and parsing.

Important APIs/types/functions: macro-created classes include `ConfigurationException`, `FilesystemException`, `InitializeException`, `ConnectionException`, read/write recoverable and unrecoverable variants, and no-valid-copies variants. `ChunkCrcException` adds server and `ChunkPartType` context. `ParseException` can prefix messages with a line number.

Control flow: exceptions are constructed with messages/statuses and thrown by subsystem code. `ChunkCrcException` embeds server text in the base message and retains structured fields.

State and persistence: exception objects only; no persistence.

Dependencies and integration: depends on chunk part types, network address, error status strings, and `Exception`. It is a shared error taxonomy for IO and configuration paths.

Risks: category hierarchy implies recoverability semantics; callers must catch the right layer. `ChunkCrcException` stores copies of address and chunk type, which is useful but can be overlooked if only `what()` is logged.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/exceptions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/exit_status.h -->
# sources/distributed-fs/lizardfs/src/common/exit_status.h

Purpose: centralizes process exit status constants.

Important APIs/types/functions: defines `LIZARDFS_EXIT_STATUS_SUCCESS`, `LIZARDFS_EXIT_STATUS_NOT_ALIVE`, `LIZARDFS_EXIT_STATUS_ERROR`, and `LIZARDFS_EXIT_STATUS_GENTLY_KILL`.

Control flow: no runtime flow; included by binaries/scripts that need consistent status codes.

State and persistence: none.

Dependencies and integration: includes `platform.h`. Used by daemon entry points and control tools.

Risks: macro constants are untyped and globally visible.

Test signals: no direct tests; correctness is convention/integration based.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/exit_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/flat_map.h -->
# sources/distributed-fs/lizardfs/src/common/flat_map.h

Purpose: implements a memory-efficient sorted-vector associative map with an interface close to `std::map`.

Important APIs/types/functions: template `flat_map<Key,T,C,Compare>` stores pairs in `flat_set<value_type, C, internal_compare>`. It exposes constructors, `operator[]`, `at`, insert/erase, iterators, `data()`, lookup, `find_nth`, bounds, comparators, relational operators, and `swap`.

Control flow: lookup delegates to `flat_set` lower-bound logic using `internal_compare`, which can compare key-to-pair and pair-to-key. `operator[]` lower-bounds by key and inserts default mapped values when absent.

State and persistence: in-memory sorted vector-like container. No persistence, no synchronization. Iterators are vector iterators and invalidate on inserts/erases as the underlying container dictates.

Dependencies and integration: depends on `flat_set.h` and standard algorithms. Used by goal label maps and other small associative data where cache locality matters.

Risks: insert is O(n); this is good for small maps but poor for large/mutation-heavy workloads. Constructor with `sorted=true` trusts caller ordering and uniqueness. `operator[](const key_type &&key)` uses a const rvalue reference, which prevents true move semantics for key input.

Test signals: `flat_map_unittest.cc` covers constructors, swap, iterators, insert/erase, `at`, count, custom compare, find/lower_bound, and nth lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/flat_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/flat_map_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/flat_map_unittest.cc

Purpose: validates `flat_map` behavior against map-like expectations.

Important APIs/types/functions: helper `fill_map`; tests constructors, swap, iterator variants, insertion/erasure, `at`, `count`, custom comparator `CCmp`, `find`, `lower_bound`, and `find_nth`.

Control flow: tests build maps through `operator[]` and inserts, then assert sorted iteration, size, lookup, thrown exceptions, and data equality.

State and persistence: test-only containers.

Dependencies and integration: includes `flat_map.h`, `gtest`, strings, and iterators. It exercises `flat_map` through its public API and indirectly tests `flat_set` as storage.

Risks: tests do not cover sorted-constructor duplicate misuse, move-only keys/values, iterator invalidation contracts, or large-scale performance.

Test signals: good behavioral coverage for intended small associative use, including custom ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/flat_map_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/flat_set.h -->
# sources/distributed-fs/lizardfs/src/common/flat_set.h

Purpose: implements a sorted vector-backed set with `std::set`-like API and better memory locality for small collections.

Important APIs/types/functions: template `flat_set<T,C,Compare>` privately inherits comparator for EBO. It provides constructors including sorted/trusted input, assignment, iterators, `data`, capacity, `reserve`, insert with optional hint, range insert, erase, lookup, equal range, comparators, relational operators, and `swap`.

Control flow: normal inserts lower-bound and insert only if no equivalent value exists. Hint inserts check neighboring values to insert in O(1) when the hint is valid, otherwise search a narrowed range. Range/initializer inserts reserve once and insert each element.

State and persistence: in-memory vector-like storage. No persistence or synchronization. Iterators are invalidated by underlying container mutations.

Dependencies and integration: depends on standard algorithms and containers. Used by `flat_map`, `Goal` slice containers, and other common structures.

Risks: O(n) insertion/erase, trusted sorted construction can store duplicates or unsorted data if caller lies, and `swap` implemented as `std::swap(*this, other)` may recurse into ADL/swap patterns depending on overload resolution though tests cover basic use.

Test signals: `flat_set_unittest.cc` covers redundant inserts, hint insert, range insert, equal range, iterators, swap, erase, constructors, and assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/flat_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/flat_set_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/flat_set_unittest.cc

Purpose: tests sorted-vector set semantics for `flat_set`.

Important APIs/types/functions: helper `simple_insert`; tests redundant inserts, hint insertion for lvalue/rvalue values, range and initializer inserts, equal range, simple find/iteration, swap, erase, constructors, and assignment.

Control flow: tests create sets, mutate them through public APIs, compare order/size/content with expected sequences, and ensure duplicates are suppressed.

State and persistence: test-only heap/stack state.

Dependencies and integration: includes `flat_set.h`, `gtest`, `algorithm`, and `numeric`.

Risks: no tests for malformed `sorted=true` input, custom comparator, move-only values, or performance. The hints test focuses on duplicate insert, not successful insertion with valid hints.

Test signals: solid coverage for standard small-set operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/flat_set_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/galois_coeff.h -->
# sources/distributed-fs/lizardfs/src/common/galois_coeff.h

Purpose: builds compile-time GF(2^8) logarithm and exponent lookup tables for erasure coding.

Important APIs/types/functions: `detail::gf_mul2`, recursive constexpr `gf_log` and `gf_exp`, `get_gf_log_table`, `get_gf_exp_table`, and global constexpr arrays `gf_log_table` and `gf_exp_table`.

Control flow: template expansion over `make_index_sequence<255>()` evaluates finite-field powers at compile time. `gf_mul2` uses polynomial reduction with `0x1d`.

State and persistence: global constexpr arrays with static storage; no runtime mutation or persistence.

Dependencies and integration: depends on `integer_sequence.h` and `<array>`. Used by `galois_field_isal.cc` for multiplication/inversion.

Risks: recursive constexpr functions assume valid nonzero/log inputs and would recurse indefinitely for invalid values if called improperly at compile time. The field polynomial must match the rest of the Reed-Solomon implementation.

Test signals: no direct test in subset, but EC read tests exercise downstream Reed-Solomon behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/galois_coeff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/galois_field.h -->
# sources/distributed-fs/lizardfs/src/common/galois_field.h

Purpose: declares the finite-field matrix/table/encoding API used for Reed-Solomon erasure coding.

Important APIs/types/functions: `gf_gen_rs_matrix`, `gf_gen_cauchy1_matrix`, `gf_invert_matrix`, `ec_init_tables`, and `ec_encode_data`.

Control flow: callers generate an encoding matrix, invert matrices for recovery, initialize 32-byte-per-coefficient tables, and encode/decode source buffers into destination buffers.

State and persistence: no state in header; implementations use caller-provided buffers.

Dependencies and integration: depends on `<cstdint>` and `platform.h`. It abstracts ISA-L-derived finite-field routines for `ReedSolomon` and EC read/write paths.

Risks: raw pointer API has no dimension/bounds validation. Matrix inversion mutates its input matrix. Buffer aliasing and alignment requirements are implementation-sensitive.

Test signals: EC planner tests indirectly validate recovery; no direct GF unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/galois_field.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/galois_field_encode.cc -->
# sources/distributed-fs/lizardfs/src/common/galois_field_encode.cc

Purpose: implements table-driven erasure-code encoding with scalar and optional SIMD variants.

Important APIs/types/functions: `ec_encode_data_default`, target-attributed `ec_encode_data_ssse3`, `ec_encode_data_avx`, optional `ec_encode_data_avx2`, `ec_get_encode_function`, static `gEncodeFunction`, and public `ec_encode_data`.

Control flow: each encoder loops over destination rows, then source columns, applying 32-byte GF coefficient tables by splitting input bytes into low/high nibbles. SIMD variants process 16 or 32 bytes per iteration and fall back to scalar tails. With CPU feature detection, a static function pointer is selected at startup.

State and persistence: static function pointer selected once; no persistence.

Dependencies and integration: depends on GCC vector extensions, `__builtin_cpu_supports`, optional `immintrin.h`, and table layout from `ec_init_tables`. Used by Reed-Solomon encoding/recovery.

Risks: low-level vector casts and target attributes are compiler/architecture sensitive. CPU dispatch is compile-time gated by GCC version and `LIZARDFS_HAVE_CPU_CHECK`. No runtime validation of buffer alignment, lengths, or table sizes.

Test signals: no direct tests here; EC read tests indirectly exercise encoding/decoding paths depending on build configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/galois_field_encode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/galois_field_isal.cc -->
# sources/distributed-fs/lizardfs/src/common/galois_field_isal.cc

Purpose: ISA-L-derived finite-field support for matrix generation, inversion, coefficient table initialization, and GF multiplication/inversion.

Important APIs/types/functions: `gf_mul`, `gf_inv`, `gf_gen_rs_matrix`, `gf_gen_cauchy1_matrix`, `gf_invert_matrix`, `gf_vect_mul_init`, and `ec_init_tables`.

Control flow: `gf_mul` and `gf_inv` use compile-time log/exp tables. Matrix generators write identity data rows plus parity rows. `gf_invert_matrix` performs Gauss-Jordan elimination with row swapping over GF(2^8), mutating input and writing inverse. `gf_vect_mul_init` expands a coefficient into low/high nibble tables, with optimized 64-bit layout when available. `ec_init_tables` repeats table expansion for each row/coefficient.

State and persistence: no internal mutable global state; all outputs go to caller-provided buffers.

Dependencies and integration: depends on `galois_coeff.h`, `cstring`, and ISA-L algorithm conventions. Used by Reed-Solomon code backing EC reads/writes.

Risks: raw pointer matrix dimensions are unchecked. `gf_inv(0)` returns zero, which is convenient but mathematically undefined; callers must avoid zero pivots except where handled. Matrix inversion mutates input, which can surprise callers.

Test signals: no direct GF tests; EC read plan tests indirectly exercise recovery correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/galois_field_isal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/generic_lru_cache.h -->
# sources/distributed-fs/lizardfs/src/common/generic_lru_cache.h

Purpose: implements a generic fixed-capacity LRU-style cache that stores large keys once.

Important APIs/types/functions: `GenericLruCache<Key,Value,DefaultCapacity,Hasher,Comparator>`, `Queue` list of key/value pairs, `CacheMap` from `reference_wrapper<const Key>` to queue iterator, `insert`, rvalue insert, `emplace`, `clear`, `size`, `find`, `findByValue`, and iterators.

Control flow: inserts evict the queue back when at capacity, then check map existence, push new entries to the front, and insert a map reference to the list key. Finds use the map and splice found entries to the front. `findByValue` scans the list and also promotes the result.

State and persistence: in-memory list plus unordered map. No persistence or synchronization.

Dependencies and integration: depends on `<list>`, `<unordered_map>`, `<functional>`, and `<algorithm>`. It is suitable for caches with expensive key copies.

Risks: if `capacity_` is zero, insert tries to access `queue_.back()` on an empty list. The code evicts before checking whether the key already exists, so inserting an existing key at full capacity can evict an unrelated entry and then return the old entry without updating value. `reference_wrapper` keys require list node keys to outlive map entries, which is maintained only if erase/pop paths stay correct.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/generic_lru_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/goal.cc -->
# sources/distributed-fs/lizardfs/src/common/goal.cc

Purpose: implements goal slice type metadata, slice merging, validity, expected-copy counting, and string rendering.

Important APIs/types/functions: static slice type parts/names, `Goal::Slice::getExpectedCopies`, `Slice::mergeIn`, `Slice::isValid`, `makeLabelsUnion`, `labelsDistance`, `Goal::mergeIn`, `Goal::getExpectedCopies`, and `to_string` overloads.

Control flow: `Slice::mergeIn` builds a cost matrix comparing every local part to every incoming part, uses `linear_assignment::auctionOptimization` to assign compatible parts, then unions assigned label maps. `makeLabelsUnion` merges sorted label counts, special-casing wildcard labels so total copy requirements are preserved with minimal explicit labels. `Goal::mergeIn` inserts missing slices or merges matching slice types.

State and persistence: mutates in-memory `Goal` and `Slice` flat storage. String functions expose config-like rendering; serialization is not in this file.

Dependencies and integration: depends on `goal.h`, `linear_assignment_optimizer.h`, `exceptions.h`, and media labels. It is central to chunk placement policy and goal parsing/rendering.

Risks: correctness depends on sorted `flat_map` label ordering and wildcard being ordered last as assumed by `makeLabelsUnion`. Merging uses assertions for slice compatibility. Cost formula uses `10 * kMaxExpectedCopies`; changes to max copy limits can affect assignment scoring.

Test signals: `goal_unittest.cc` covers basic operations, standard/xor merges, repeated merges, and goal merge across slice types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/goal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/goal.h -->
# sources/distributed-fs/lizardfs/src/common/goal.h

Purpose: declares the domain model for LizardFS replication goals, including standard, tape, XOR, and erasure-code slice layouts with label constraints.

Important APIs/types/functions: `detail::SliceType` maps integer type IDs to names and expected part counts, including EC types. `SliceIterator` iterates part proxies. `Goal::Slice` stores part sizes and label data in compact flat vectors, exposes label-map proxies per part, copy counting, merge, validity, equality, and iterators. `GoalId` validates goal IDs 1..40. `Goal` stores named slices in a `flat_set`, exposes `setSlice`, `mergeIn`, `find`, `operator[]`, `size`, name access, iterators, and equality.

Control flow: callers build or parse goals by accessing slices and part label maps. Missing `Goal::operator[]` creates a new slice for a type; const access throws when absent.

State and persistence: goals are in-memory policy objects with compact storage. They integrate with config/parsing layers but do not persist themselves here.

Dependencies and integration: depends on `MediaLabel`, `flat_map`, `flat_set`, `small_vector`, and `vector_range`. Used by chunk placement, slice traits, read planners, and configuration.

Risks: proxy objects are invalidated by inserts that resize underlying flat storage; comments warn that modifying one part can invalidate others. `SliceType::isValid` covers numeric range, not semantic availability in a deployment. Assertions protect many invariants only in debug builds.

Test signals: `goal_unittest.cc` validates representative slice operations and merge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/goal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/goal_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/goal_unittest.cc

Purpose: tests the goal/slice data model and merge algorithm.

Important APIs/types/functions: macro `sneakyPartType`; tests `BasicSliceOperations`, `BasicSliceMerge`, `BasicXorMerge` variants, and `GoalMerge`.

Control flow: tests construct standard and XOR slices, assign media labels and wildcard labels, check expected copy counts and string rendering, merge slices with different part-label arrangements, and verify merged results.

State and persistence: test-only goal objects.

Dependencies and integration: includes `common/goal.h` and `gtest`.

Risks: coverage is focused on standard/xor cases; EC slice types and invalid-goal paths are not directly exercised. The tests use expected exact string output, which is useful but can be brittle if formatting changes.

Test signals: good signal for the assignment/union behavior that preserves minimal target parts during goal merge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/goal_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/hashfn.h -->
# sources/distributed-fs/lizardfs/src/common/hashfn.h

Purpose: provides fast non-cryptographic hash helpers, checksum composition, byte-array hashing, and tuple hashing.

Important APIs/types/functions: `hash32`, `hash32mult`, `hash6432`, `hash64`; template `hash<T>` with primitive specializations; `hashCombineRaw`, variadic `hashCombine`; `ByteArray` and its specialization; `addToChecksum`, `removeFromChecksum`; `AlmostGenericTupleHash`.

Control flow: primitive hashes use Thomas Wang-style avalanche mixes. `hashCombine` recursively hashes values into a seed. `ByteArray` iterates bytes and combines each byte hash. Tuple hashing expands indexes via `make_index_sequence`.

State and persistence: no state; checksum helpers mutate caller-provided integers.

Dependencies and integration: depends on `integer_sequence.h`, tuples, and integer types. Used where deterministic internal hash/checksum values are needed, not for security.

Risks: not cryptographic. The generic `hash<T>` is declared but undefined to force unsupported-type link errors, which can be less clear than compile-time static assertions. `addToChecksum`/`removeFromChecksum` are XOR symmetric and order-insensitive, suitable only for specific checksum semantics.

Test signals: `hashfn_unittest.cc` checks string byte hashing distinctions, combine order sensitivity, primitive uniqueness over a million ints, and variadic combine equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/hashfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/hashfn_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/hashfn_unittest.cc

Purpose: tests hash helpers and combination semantics.

Important APIs/types/functions: tests `hash(ByteArray)`, `hash<T>` primitive specializations, `hashCombineRaw`, and variadic `hashCombine`.

Control flow: string test checks different byte arrays produce different hashes. Combine test checks different seeds and argument orders produce different results. Primitive test creates one million integer hashes and checks uniqueness, then compares hashes across primitive types. Variadic test compares repeated one-by-one combine with one variadic call.

State and persistence: test-only vectors and seeds.

Dependencies and integration: includes `hashfn.h`, `gtest`, and `algorithm`.

Risks: uniqueness over a finite range is a useful smoke test but not a formal distribution test. The second million-hash loop duplicates `int` input rather than truly using 32-bit variable diversity.

Test signals: good regression coverage for deterministic hashing and combine behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/hashfn_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/human_readable_format.cc -->
# sources/distributed-fs/lizardfs/src/common/human_readable_format.cc

Purpose: implements formatting helpers for byte counts, IP addresses, timestamps, and transfer rates.

Important APIs/types/functions: internal `convertToHumanReadableFormat`, public `convertToSi`, `convertToIec`, `ipToString`, `timeToString`, and `bpsToString`.

Control flow: byte formatting chooses exponent by logarithms, adjusts near-boundary values, emits one decimal for values below 10 and zero decimals otherwise, and uses SI or IEC suffixes. IP formatting shifts a host-order `uint32_t` into dotted decimal. Time formatting uses `strftime(localtime(...))`. `bpsToString` asserts positive microseconds and formats `(bytes * 1e6 / usec)` as IEC bytes per second.

State and persistence: no state; formatting only.

Dependencies and integration: depends on `<cmath>`, `<iomanip>`, `<sstream>`, `massert`, and the header declarations. Used in CLI/admin/status output.

Risks: `localtime` uses static storage and is not thread-safe on many platforms. Floating conversion from `uint64_t` can lose precision at high values but output is intentionally approximate. `bpsToString` mixes floating result into a `uint64_t`-typed formatter through implicit conversion.

Test signals: `human_readable_format_unittest.cc` covers SI and IEC boundary outputs extensively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/human_readable_format.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/human_readable_format.h -->
# sources/distributed-fs/lizardfs/src/common/human_readable_format.h

Purpose: declares user-facing formatting utilities.

Important APIs/types/functions: `convertToSi`, `convertToIec`, `ipToString`, `timeToString`, and `bpsToString`.

Control flow: callers pass raw numeric values and receive display strings.

State and persistence: none.

Dependencies and integration: includes `platform.h`, `<cstdint>`, `<ctime>`, and `<string>`. Used by reporting surfaces where raw counters need compact text.

Risks: units and rounding are fixed by implementation; callers needing locale-aware or exact formatting need a different API.

Test signals: implementation tests cover byte formatting; IP/time/bps are not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/human_readable_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/human_readable_format_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/human_readable_format_unittest.cc

Purpose: tests SI and IEC byte-count formatting.

Important APIs/types/functions: `HumanReadableFormatTests.ConvertToSi` and `ConvertToIec`.

Control flow: tests assert exact strings for zero/small values, base boundaries, decimal rounding, petabyte/exabyte outputs, and `uint64_t` maximum.

State and persistence: none beyond test inputs.

Dependencies and integration: includes `human_readable_format.h` and `gtest`.

Risks: only byte count functions are covered; `ipToString`, `timeToString`, and `bpsToString` have no direct tests here.

Test signals: strong expected-output regression coverage for unit suffix and rounding choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/human_readable_format_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/id_pool.h -->
# sources/distributed-fs/lizardfs/src/common/id_pool.h

Purpose: implements an optimized reusable ID allocator over a bounded numeric range.

Important APIs/types/functions: `detail::IdPoolBlock<ValueType,SizeType>` manages a bitset block with memory released when fully free or fully used. `IdPool<IDT>` exposes `acquire`, `release`, `markAsAcquired`, `checkIfAvailable`, `maxSize`, `size`, and static `nullId`.

Control flow: constructor reserves id `0`. `acquire` first consumes a small cache of released ids, then uses the first free block, lazily adding blocks up to max. `release` validates range, optionally stores ids in `cache_`, otherwise flips a bit in the block and updates the free-list. `markAsAcquired` forces an id unavailable, allocating blocks if needed.

State and persistence: in-memory unordered cache, vector of bit blocks, forward-list of free block indexes, used count, range limits. No persistence or synchronization.

Dependencies and integration: depends on `compact_vector` for compact bit storage. Used wherever metadata identifiers need fast allocation/recycling.

Risks: many invariants rely on block/free-list bookkeeping; corruption can throw runtime errors. Cache path stores released ids as `size_t`, so duplicate release detection checks cache and block. No thread safety. `used_count_` is adjusted for reserved id during construction and normal IDs thereafter, so callers should interpret `size()` as acquired non-null IDs.

Test signals: `id_pool_unittest.cc` covers full acquisition, release/reacquire, null handling, uniqueness, and `markAsAcquired`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/id_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/id_pool_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/id_pool_unittest.cc

Purpose: validates bounded ID allocation and recycling.

Important APIs/types/functions: tests `acquire`, `release`, `nullId`, `maxSize`, and `markAsAcquired` using `IdPool<uint32_t>`.

Control flow: tests consume entire pools, verify exhaustion returns zero, repeatedly release/acquire IDs, reject null release, check all IDs are unique, and ensure marked IDs are never acquired.

State and persistence: test-only pool objects and a `std::set` of taken IDs.

Dependencies and integration: includes `id_pool.h` and `gtest`.

Risks: tests use small ranges/block sizes; they do not stress very large ranges, cache overflow patterns with random release orders, or multi-threaded use.

Test signals: good coverage for core allocator contract and edge handling around zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/id_pool_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/integer_sequence.h -->
# sources/distributed-fs/lizardfs/src/common/integer_sequence.h

Purpose: backports `std::integer_sequence`, `std::index_sequence`, and make-sequence utilities for older C++ standards.

Important APIs/types/functions: `integer_sequence<T, Is...>`, `merge_integer_sequence`, recursive `make_integer_sequence<T,N>`, `index_sequence<Is...>`, `merge_index_sequence`, and recursive `make_index_sequence<N>`.

Control flow: recursive templates split `N` into halves and merge sequences while offsetting the right side by the left length.

State and persistence: compile-time types only.

Dependencies and integration: depends on `<cstddef>`. Used by `galois_coeff.h` and tuple hashing.

Risks: deep template recursion is logarithmic but still compile-time work. This custom implementation can conflict semantically if mixed with `std::integer_sequence` APIs expecting exact standard names in namespace `std`.

Test signals: `integer_sequence_unittest.cc` converts generated sequences into vectors and compares with `iota` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/integer_sequence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/integer_sequence_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/integer_sequence_unittest.cc

Purpose: tests custom integer and index sequence generation.

Important APIs/types/functions: helper overloads `convert_to_vector`; tests `make_integer_sequence<int,100>` and `make_index_sequence<101>`.

Control flow: expected vectors are filled with `std::iota`; generated type packs are expanded into result vectors and compared.

State and persistence: test-only vectors.

Dependencies and integration: includes `integer_sequence.h`, `numeric`, and `gtest`.

Risks: only moderate sizes are tested; no explicit zero/one case tests even though template specializations exist.

Test signals: verifies normal recursive sequence generation for both value and index aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/integer_sequence_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/intrusive_list.h -->
# sources/distributed-fs/lizardfs/src/common/intrusive_list.h

Purpose: implements a non-owning doubly linked intrusive list for nodes deriving from `intrusive_list_base_hook`.

Important APIs/types/functions: `intrusive_list_base_hook` stores `prev_node_` and `next_node_`; `intrusive_list_iterator` provides bidirectional iteration; `intrusive_list<Node>` exposes front/back, push/pop, dispose variants, clear, erase, insert, swap, iterators, and whole-list `splice`.

Control flow: list operations directly rewrite hooks inside user-owned nodes. Dispose variants remove nodes then call a supplied disposer. `splice` inserts all nodes from another list before a position and empties the source.

State and persistence: list stores only front/back pointers and size; node linkage lives inside nodes. No ownership, persistence, or synchronization.

Dependencies and integration: depends on standard iterator/type traits and `platform.h`. Useful where allocation overhead of `std::list` is undesirable.

Risks: nodes must not be inserted into multiple lists or destroyed while linked. The list destructor does not unlink or delete elements. Assertions catch only some misuse. Iterator comparisons include ordering operators that compare raw addresses, not list order.

Test signals: `intrusive_list_unittest.cc` covers push_back, erase, insert, splice, and disposal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/intrusive_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/intrusive_list_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/intrusive_list_unittest.cc

Purpose: tests intrusive-list operations against `std::vector` ordering.

Important APIs/types/functions: local `Node` derives from `intrusive_list_base_hook`; comparison helpers compare list content with vector content. Tests cover `PushBack`, `Erase`, `Insert`, and `Splice`.

Control flow: tests allocate nodes with `new`, add them to lists, mutate the list and an expected vector in parallel, compare, and call `clear_and_dispose` to delete nodes.

State and persistence: heap-allocated test nodes owned by test cleanup.

Dependencies and integration: includes `intrusive_list.h`, `gtest`, `algorithm`, and `numeric`.

Risks: tests do not cover push_front, pop variants, empty-list operations, move/swap, or misuse cases like double insertion.

Test signals: good coverage for common ordering and splice behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/intrusive_list_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limit_group.h -->
# sources/distributed-fs/lizardfs/src/common/io_limit_group.h

Purpose: defines the type used to identify I/O limiting groups.

Important APIs/types/functions: `typedef std::string IoLimitGroupId` and constant `kUnclassified = "unclassified"`.

Control flow: no runtime behavior; consumers pass group IDs to limiting configuration and request paths.

State and persistence: no state; group IDs may be persisted by configuration elsewhere.

Dependencies and integration: included by `io_limiting.h` and config loaders. It standardizes the default unclassified group name.

Risks: plain string typedef does not prevent mixing arbitrary strings with validated group identifiers.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limit_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limiting.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limiting.cc

Purpose: implements the core runtime behavior for per-group I/O bandwidth limiting.

Important APIs/types/functions: `Limiter::registerReconfigure`, `RTClock::now`, `RTClock::sleepUntil`, and `Group` internals: `attempt`, `enqueue`, `dequeue`, `notifyQueue`, `isFirst`, `askMaster`, `wait`, and `die`.

Control flow: `Group::wait` enqueues a request, waits until it is at the front, then loops until deadline. It returns `ENOENT` if the group dies, succeeds if reserve covers the request, sleeps until the next allowed master request after failed grants, or calls `askMaster` to request enough bytes for pending plus recent past requests. Completed requests are moved into `pastRequests_`, removed from pending, and the next waiter is notified.

State and persistence: per-group in-memory queue of pending requests, recent past requests, reserve bytes, last request timestamps, success flag, dead flag, and injected clock. Shared state references a `Limiter` and throttle delta. No persistence.

Dependencies and integration: depends on `io_limiting.h`, `io_limits_config_loader.h`, `massert`, protocol status constants, and `std::thread` sleep. It integrates local workers with a master/local limiter implementation through `Limiter::request`.

Risks: correctness depends on callers holding and passing the same mutex around `wait`. `die()` sets a flag but does not notify all pending waiters directly; callers must also arrange wakeups or rely on queue progression. Reserve accounting is time-window based and sensitive to clock behavior and limiter latency.

Test signals: no direct tests in this subset. The injectable `Clock` and abstract `Limiter` are designed for tests, but mapped files contain only implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limiting.cc -->

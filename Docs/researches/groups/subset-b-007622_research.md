# subset-b-007622 Research

Grouped source research for LizardFS chunkserver networking/storage helpers, common ACL/config/chart infrastructure, chunk part/planner models, chunk copy-state calculators, and chunkserver statistics. Each listed source file has a dedicated marker-delimited section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.h

## Purpose

This header declares the chunkserver network worker thread and the per-connection state records used by the chunkserver event loop. It is the shared contract between socket polling, read/write request handling, forwarding-chain writes, background jobs, request logging, and packet output buffering.

## Important APIs, Types, and Functions

Important enums are `ChunkserverEntryMode` (`HEADER`, `DATA`) and `ChunkserverEntryState` (`IDLE`, `READ`, `GET_BLOCK`, write-chain states, and close states). `packetstruct` tracks packet memory, cursor state, and optional `OutputBuffer`. `csserventry` is the large connection state object: sockets, poll descriptor positions, header buffers, input/output packet queues, read/write job ids, forwarding state, chunk id/version/type/range, serializer, and timers. `NetworkWorkerThread` exposes `operator()()`, `askForTermination()`, `addConnection()`, and `bgJobPool()`.

## Control Flow

The worker owns a list of `csserventry` objects and repeatedly prepares poll descriptors, serves poll events, and terminates on request. Each connection advances through header/data modes and state-machine states. Write forwarding uses `fwdsock`, `fwdinitpacket`, `fwdinputpacket`, and `partiallyCompletedWrites` to synchronize local writes with downstream acknowledgements.

## State and Persistence Behavior

All state is in-memory and connection-scoped except the background job pool pointer shared with worker jobs. `csserventry` owns queued packets and output buffers but not persistent chunk data. The thread uses an atomic termination flag, a mutex-protected connection list, and a notification pipe/wakeup fd.

## Dependencies and Integration Points

It integrates with `network_stats`, `OutputBuffer`, `ChunkPartType`, `NetworkAddress`, `slice_traits`, protocol packet headers, request logging, and a `MessageSerializer`. Implementations in the chunkserver network worker and read/write handlers consume this header.

## Risks and Edge Cases

The state object mixes many ownership domains, so stale sockets, poll positions, packet pointers, or job ids can cause leaks or use-after-close behavior. Move construction is defaulted for `csserventry` even though it holds raw pointers into internal buffers and linked packet queues, so actual list operations must avoid invalid assumptions. Forwarded writes can wedge if local completion and downstream ACK tracking diverge.

## Test Signals

Useful signals are chunkserver read/write integration tests, write-chain forwarding failures, nonblocking socket close paths, worker termination under active jobs, and packet queue flushing through `OutputBuffer`. There is no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/open_chunk.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/open_chunk.h

## Purpose

`OpenChunk` is an RAII wrapper for a chunkserver `Chunk` that has been found/locked and may have an open file descriptor and optional MooseFS CRC data buffer. It centralizes cleanup of descriptors, error reporting, and `hdd_chunk_release()`.

## Important APIs, Types, and Functions

The class has default, `Chunk*`, and move constructors, move assignment, destructor, `canRemove()`, `purge()`, and `crc_data()`. It stores `Chunk *chunk_`, fallback descriptor `fd_`, and `std::unique_ptr<MooseFSChunk::CrcDataContainer> crc_`.

## Control Flow

Construction captures the chunk pointer and current descriptor and allocates CRC storage for MooseFS-format chunks. Destruction closes `chunk_->fd` when present, reports close failures as damaged chunks, resets the chunk descriptor to `-1`, and releases the locked chunk. If `purge()` was called, the wrapper forgets the chunk, keeps the descriptor, and closes only that descriptor later.

## State and Persistence Behavior

The class does not persist metadata itself, but it mutates persistent chunk state indirectly through close-error reporting and damage reporting. Its correctness depends on the caller already holding the chunk lock.

## Dependencies and Integration Points

It depends on `chunkserver/chunk.h`, `hddspacemgr.h`, `hdd_chunk_trylock()`, `hdd_chunk_release()`, `hdd_error_occured()`, and `hdd_report_damaged_chunk()`.

## Risks and Edge Cases

Move assignment overwrites any existing owned chunk/fd without first releasing it, so callers should only move into empty/discarded wrappers. `crc_data()` asserts that CRC storage exists and is only valid for MooseFS chunks. `purge()` requires `chunk_` and changes ownership semantics; misuse can leak locks or close the wrong descriptor.

## Test Signals

Expected coverage is chunkserver HDD tests that close chunks on success/error, remove locked chunks, purge inaccessible chunks, and read MooseFS CRC data. No direct unit test is included in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/open_chunk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.cc

## Purpose

This file implements `OutputBuffer`, a fixed-capacity byte buffer used to accumulate packet/file data and flush it to a nonblocking descriptor.

## Important APIs, Types, and Functions

Implemented methods are the constructor/destructor, `writeOutToAFileDescriptor()`, `bytesInABuffer()`, `clear()`, `copyIntoBuffer(int,size_t,off_t*)`, `copyIntoBuffer(const void*,size_t)`, and `checkCRC()`.

## Control Flow

The constructor allocates `internalBufferCapacity` bytes and initializes unflushed cursors. Memory copies append directly to the unflushed tail. File copies loop with `pread()` until the requested length is read or a nonpositive result occurs. Flush loops with `write()` until all buffered bytes are written, returns `WRITE_AGAIN` on `EAGAIN` or zero writes, and `WRITE_ERROR` for other failures.

## State and Persistence Behavior

State is the internal vector and two cursor indices. It does not own input or output descriptors and does not advance the optional `offset` pointer passed to `copyIntoBuffer`, so callers must manage file position semantics themselves.

## Dependencies and Integration Points

It depends on POSIX `pread`/`write`, `common/crc.h` for `mycrc32`, and assertion helpers. Chunkserver network code stores `OutputBuffer` instances inside outgoing packet records.

## Risks and Edge Cases

Capacity violations abort through `eassert`. `copyIntoBuffer(int, ..., offset)` repeatedly passes the same offset value and does not increment `*offset`, which is only correct if callers intend fixed-offset reads or pass null for implicit offset zero behavior; otherwise it can duplicate data. `checkCRC()` uses an assertion that rejects checking from index zero, so boundary cases are debug-sensitive.

## Test Signals

`output_buffer_unittest.cc` covers memory append and pipe flush. More signals should include short writes, `EAGAIN`, file reads with offsets, CRC success/failure, and buffer boundary assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.h

## Purpose

The header declares the fixed-capacity `OutputBuffer` interface for chunkserver output packet buffering and descriptor flushing.

## Important APIs, Types, and Functions

`OutputBuffer::WriteStatus` defines `WRITE_DONE`, `WRITE_AGAIN`, and `WRITE_ERROR`. Public methods include file/memory/vector `copyIntoBuffer()` overloads, `checkCRC()`, `writeOutToAFileDescriptor()`, `bytesInABuffer()`, `data()`, and `clear()`.

## Control Flow

The header only declares behavior. The intended flow is append bytes into the internal buffer, optionally verify a suffix CRC, repeatedly flush to an output descriptor until done/again/error, then clear or reuse.

## State and Persistence Behavior

The buffer owns an in-memory `std::vector<uint8_t>` of fixed capacity plus first/one-after-last unflushed indices. No file descriptors are owned.

## Dependencies and Integration Points

It includes standard byte/container headers and is included by chunkserver connection packet state in `network_worker_thread.h`.

## Risks and Edge Cases

The API exposes raw `data()` for read-only inspection but cursor state is private, so callers must not assume the returned pointer starts at unflushed data after partial writes. All capacity management is caller responsibility. The vector overload calls `mem.data()` even for empty vectors, relying on C++ guarantees and zero-length copy behavior.

## Test Signals

The provided unit test exercises basic memory-to-pipe flow. Stronger tests would cover partial flush cursor behavior, zero-length appends, capacity overflow assertions, and CRC checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer_unittest.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/output_buffer_unittest.cc

## Purpose

This GoogleTest file validates the simplest `OutputBuffer` write path: append bytes from memory, flush them to a pipe, read them back, and compare byte values.

## Important APIs, Types, and Functions

It defines `TEST(OutputBufferTests, outputBuffersTest)`. The test uses `pipe2(..., O_NONBLOCK)` when available, optional `F_SETPIPE_SZ`, `OutputBuffer::copyIntoBuffer()`, `writeOutToAFileDescriptor()`, and `read()`.

## Control Flow

The test creates a 512 KiB buffer and pipe, fills a 10-byte memory buffer with value 17, appends it, then loops flushing until `WRITE_DONE`, sleeping if the nonblocking pipe returns `WRITE_AGAIN`. It reads the pipe and asserts all bytes match.

## State and Persistence Behavior

State is limited to the test pipe descriptors and stack buffer. It closes both pipe ends at the end of the test.

## Dependencies and Integration Points

It depends on GoogleTest, POSIX pipe/fcntl/read/close APIs, and the `OutputBuffer` public interface.

## Risks and Edge Cases

Coverage is narrow: it does not force partial writes, `WRITE_ERROR`, file-copy input, CRC checking, `clear()`, or buffer exhaustion. On systems without `pipe2`, the pipe may be blocking despite the test's nonblocking intent.

## Test Signals

Passing this test signals basic memory append and descriptor write correctness. It is not sufficient to validate nonblocking network behavior under backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.cc

## Purpose

This file implements the chunkserver replication bandwidth limiter by wrapping the common `ioLimiting` framework with one logical group named `replication`.

## Important APIs, Types, and Functions

Implemented methods are `ReplicationBandwidthLimiter::ReplicationBandwidthLimiter()`, `setLimit()`, `unsetLimit()`, `wait()`, nested `ReplicationLimiter::request()`, `setLimit()`, and `unsetLimit()`. A static `mutex_` serializes waits.

## Control Flow

Construction initializes shared IO-limiter state with a 20 ms update interval. `setLimit()` programs the database limit in KiB/s and lazily creates a `Group`. `unsetLimit()` drops the group and clears limits. `wait()` returns immediately if no group exists; otherwise it locks the static mutex and delegates to `Group::wait()` with an absolute deadline.

## State and Persistence Behavior

State is in-memory: `IoLimitsDatabase`, `RTClock`, shared state, optional group, and a class-wide mutex. Limit changes are not persisted.

## Dependencies and Integration Points

It depends on `common/io_limiting.h` and LizardFS status codes. Replication paths should call `wait()` before transferring requested bytes.

## Risks and Edge Cases

The static mutex serializes waits across all limiter instances, which is simple but can reduce concurrency. `setLimit()` updates database state but does not recreate an existing group, so correctness relies on the shared state seeing database updates. A limit of zero or very small timeout behavior is delegated to `ioLimiting`.

## Test Signals

Expected tests should verify immediate success without a limit, delayed or timed-out waits with limits, concurrent wait serialization, `unsetLimit()` recovery, and runtime limit updates. No direct test is in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.h

## Purpose

The header declares a minimal replication-specific API for IO bandwidth throttling.

## Important APIs, Types, and Functions

`ReplicationBandwidthLimiter` exposes `setLimit(uint64_t limit_kBps)`, `unsetLimit()`, and `wait(uint64_t requestedSize, SteadyDuration timeout)`. The nested `ReplicationLimiter` implements `ioLimiting::Limiter::request()` and owns an `IoLimitsDatabase`.

## Control Flow

Callers configure or clear a limit, then call `wait()` before replication operations. The nested limiter translates group requests into database requests using the current steady-clock time.

## State and Persistence Behavior

The limiter owns volatile limit state and a lazily created `ioLimiting::Group`; no on-disk persistence is provided.

## Dependencies and Integration Points

It integrates chunkserver replication code with `common/io_limiting.h`, `IoLimitsDatabase`, `ioLimiting::SharedState`, and `ioLimiting::Group`.

## Risks and Edge Cases

The API has no explicit synchronization around `setLimit()`/`unsetLimit()` versus `wait()` except the wait mutex in the implementation, so callers should avoid racing configuration changes with active transfers unless `ioLimiting` guarantees safety. Unit conversion is KiB/s as documented, not bytes/s.

## Test Signals

Tests should assert status codes for no-limit, limited, timed-out, and limit-cleared scenarios and should include concurrent waiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner.h

## Purpose

`SliceRecoveryPlanner` builds `ReadPlan` objects that recover a single missing chunk part from available parts. It chooses between direct slice reads, chunk-data reconstruction, and parity recomputation.

## Important APIs, Types, and Functions

Important members are `prepare()`, `setScores()`, `isReadingPossible()`, and `buildPlan()`. The internal `BlockConverter` copies selected blocks from reconstructed full chunk data into the recovered part. Recovery modes are `kReadDataPart`, `kRecoverDataPart`, and `kRecoverParityPart`.

## Control Flow

`prepare()` first tries `SliceReadPlanner` for the exact requested part. If that fails and the target is a data part, it prepares `ChunkReadPlanner` for the corresponding full-chunk block positions. If the target is parity, it prepares `ChunkReadPlanner` for the data blocks needed to recompute parity. `buildPlan()` then either returns a direct slice plan, attaches `BlockConverter`, or attaches XOR/EC parity recovery functors.

## State and Persistence Behavior

Planner state is transient and stores the requested part, block range, selected mode, and helper planners. It does not persist data; returned plans describe reads and postprocessing.

## Dependencies and Integration Points

It depends on `ChunkReadPlanner`, `SliceReadPlanner`, `slice_traits`, `XorReadPlan`, `ECReadPlan`, `ReadPlan`, and `MFSBLOCKSIZE`.

## Risks and Edge Cases

Most validation is assert-only. Calling `buildPlan()` without a successful `prepare()` can hit impossible-state assertions. Correctness relies on `slice_traits` mapping part indices and data/parity counts exactly for standard, XOR, and EC layouts.

## Test Signals

`slice_recovery_planner_unittest.cc` covers XOR direct recovery, standard-to-XOR conversion, parity recovery, and recovery from other XOR levels. EC-specific coverage is not present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner_unittest.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner_unittest.cc

## Purpose

This file verifies that `SliceRecoveryPlanner` can build executable plans that reproduce expected chunk-part bytes.

## Important APIs, Types, and Functions

Helpers are `xor_part()`, `checkPartRecovery(...)` overloads, and tests `VerifyRecovery1` through `VerifyRecovery4`. It uses `ReadPlanTester::buildData()`, `executePlan()`, and `compareBlocks()`.

## Control Flow

Each helper prepares synthetic part data, calls `SliceRecoveryPlanner::prepare()`, asserts recovery is possible, builds a plan, executes it through the tester, and compares the output to the target part block range.

## State and Persistence Behavior

State is test-local maps of `ChunkPartType` to byte vectors. No persistent state is touched.

## Dependencies and Integration Points

It integrates with chunk type constants, the planner, and the unit-test read-plan executor.

## Risks and Edge Cases

The tests focus on XOR layouts and do not cover EC parity recovery, unavailable plans, nonzero first-block ranges broadly, invalid block counts except the helper's `-1` shorthand, or score-based selection.

## Test Signals

Passing tests signal that generated read plans and postprocessors produce correct bytes for representative XOR data/parity recovery scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/common/CMakeLists.txt

## Purpose

This CMake file collects and builds the `mfscommon` shared library and its unit tests.

## Important APIs, Types, and Functions

Important build macros/functions are `include_directories`, `collect_sources(COMMON)`, `shared_add_library(mfscommon ...)`, `shared_target_link_libraries`, `create_unittest`, and `link_unittest`.

## Control Flow

CMake includes the common source directory, collects common sources, removes unsupported files on MinGW, removes alternative Galois-field implementations when ISA-L is available, builds `mfscommon`, conditionally links CRC, zlib, rt, allocator, socket, ISA-L, and Judy libraries, then builds the common unittest target with an extra master goal-config loader source.

## State and Persistence Behavior

It affects generated build-system state only. It does not create runtime persistence.

## Dependencies and Integration Points

This is the central build integration for all common files in this subset. It gates optional compression/checksum/allocator/socket/ISA-L support through CMake feature variables.

## Risks and Edge Cases

The `JEALLOC_LIBRARY` conditional links `${JEMALLOC_LIBRARY}`, suggesting a spelling mismatch that could skip or break jemalloc linkage depending on outer CMake variables. Removing Galois files under `ISAL_LIBRARY` assumes ISA-L replacements are complete.

## Test Signals

Signals are successful `mfscommon` builds on Linux and MinGW, optional-library matrix builds, and execution of `${COMMON_TESTS}`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list.cc -->
# sources/distributed-fs/lizardfs/src/common/access_control_list.cc

## Purpose

This file implements string parsing and formatting for `AccessControlList`.

## Important APIs, Types, and Functions

Implemented public methods are `AccessControlList::fromString()` and `toString()`. Internal helpers are `accessMaskToChar()`, `accessMaskFromChar()`, `entryTypeFromChar()`, and `eat()`.

## Control Flow

`fromString()` requires an `A` prefix and three octal permission digits for owner, group, and other. It then parses slash-delimited extended entries of the form `u:id:mask`, `g:id:mask`, or `m::mask`, checks repeated entries and missing ids, and populates ACL entries. `toString()` emits minimal permissions, named users, named groups, and an optional mask in deterministic order.

## State and Persistence Behavior

The parser returns a new in-memory ACL. Persistence occurs only when callers serialize or store the resulting object elsewhere.

## Dependencies and Integration Points

It depends on `AccessControlList` storage methods and exception type. Metadata, ACL xattr, and CLI layers can use this compact `A...` grammar.

## Risks and Edge Cases

Numeric ids use `strtol()` and are stored in `uint32_t`; overflow and negative text are not explicitly rejected beyond malformed pointer progress. Only masks `0` through `7` are valid. Grammar is strict about delimiters, so output compatibility depends on exact formatting.

## Test Signals

`access_control_list_unittest.cc` covers round-trip formatting for minimal/extended ACLs and many malformed strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list.h -->
# sources/distributed-fs/lizardfs/src/common/access_control_list.h

## Purpose

This header defines LizardFS's compact POSIX-like ACL object, including storage, serialization, permission evaluation, and string conversion API.

## Important APIs, Types, and Functions

Key type is `AccessControlList::Entry`, packed as id plus 4-bit type and 4-bit access mask. Entry types include named user/group, owner user, owner group, other, mask, and invalid. Public APIs include `toString()`, `fromString()`, `getMode()`, `setMode()`, `setEntry()`, `removeEntry()`, `getEntry()`, `getEffectiveRights()`, `minimalAcl()`, `applyMask()`, iterators, comparisons, and generated serialization methods.

## Control Flow

Basic permissions are stored in four nibbles inside `basic_permissions_`: other, group, owner, and mask. Named entries are kept in a compact sorted `flat_set`. Permission evaluation checks owner first, then named user with mask, then owning/named groups ORed together with mask, and finally other.

## State and Persistence Behavior

The object is value-type state. Serialization includes `basic_permissions_` and the named-entry set. `kMaskUnset` (`0xF`) marks absent mask state.

## Dependencies and Integration Points

It depends on compact containers, exceptions, and serialization macros. It is used by ACL converters, metadata, and permission checks.

## Risks and Edge Cases

Many invalid-type paths are assert-only. `setEntry()` silently drops named entries if the compact vector reaches max size. Effective rights require the group container to be searchable by linear `std::find`, so caller container semantics matter. Packed bitfields are serialized manually to avoid ABI layout dependence.

## Test Signals

String grammar tests are present. Additional signals should include serialization round trips, effective-rights cases with masks and multiple groups, maximum named-entry capacity, and mode changes on extended ACLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/access_control_list_unittest.cc

## Purpose

This file tests ACL string parsing and formatting.

## Important APIs, Types, and Functions

Macros `EXPECT_GOOD_ACL` and `EXPECT_WRONG_ACL` wrap `AccessControlList::fromString()` and `toString()`. Tests are `ToStringMimial`, `ToStringExtended`, and `ToStringErrors`.

## Control Flow

Good cases parse a string and require the serialized string to match exactly. Bad cases assert `IncorrectStringRepresentationException`.

## State and Persistence Behavior

Only local ACL values are created. No persistent state is used.

## Dependencies and Integration Points

The tests use GoogleTest and the ACL string API.

## Risks and Edge Cases

The test name has a typo (`Mimial`). Coverage is centered on string grammar; it does not cover effective rights, binary serialization, mode setters, or ACL converter xattrs.

## Test Signals

Passing tests signal stable canonical string output and robust rejection of malformed ACL strings, duplicate entries, missing ids, and invalid masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter.cc -->
# sources/distributed-fs/lizardfs/src/common/acl_converter.cc

## Purpose

This file converts between Linux POSIX ACL xattr binary format and LizardFS `AccessControlList`.

## Important APIs, Types, and Functions

Public functions are `aclConverter::extractAclObject()` and `aclObjectToXattr()`. Internal helpers/constants define POSIX ACL tags, permission bits, version `0x0002`, `convertTag()`, `extractEntry()`, and `storeEntry()`.

## Control Flow

Extraction checks the xattr version, scans 8-byte entries, converts little-endian tags/perms/ids, validates permission masks and undefined ids for owner/group/mask/other, rejects invalid/repeated required tags, and requires minimal user/group/other entries. Serialization writes the version, owner user, named users, owner group, named groups, optional mask, and other entry.

## State and Persistence Behavior

No global state is used. The output vector is the persistent xattr payload that can be stored by filesystem metadata layers.

## Dependencies and Integration Points

It depends on `AccessControlList`, endian helpers, and ACL converter exceptions. It is the bridge between internal ACL state and external POSIX xattr representation.

## Risks and Edge Cases

The code uses unaligned casts to `uint16_t*`/`uint32_t*`, which can be risky on strict-alignment architectures. It does not explicitly require the total buffer size after the version to be a multiple of 8; a trailing partial entry becomes invalid through `extractEntry()`. Only repeated minimal tags are rejected; named entry duplicates are normalized by `AccessControlList::setEntry()` before duplicate checking for named tags.

## Test Signals

The unit-test file contains xattr fixtures but the active tests are commented out, so this converter currently lacks active direct coverage in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter.h -->
# sources/distributed-fs/lizardfs/src/common/acl_converter.h

## Purpose

The header declares ACL conversion APIs between raw xattr bytes and `AccessControlList`.

## Important APIs, Types, and Functions

Namespace `aclConverter` defines exceptions `AclConversionException` and `PosixExtractionException`, plus `extractAclObject(const uint8_t*, uint32_t)` and `aclObjectToXattr(const AccessControlList&)`.

## Control Flow

The header is declarative. Callers pass raw xattr storage into extraction or an ACL object into serialization and handle conversion exceptions on malformed data.

## State and Persistence Behavior

No state is declared. The returned vector from `aclObjectToXattr()` is intended for persistent xattr storage.

## Dependencies and Integration Points

It depends on `AccessControlList` and common exception macros. Metadata/xattr handlers use this layer to cross the POSIX ACL boundary.

## Risks and Edge Cases

Callers must distinguish ACL conversion errors from missing xattrs or unsupported ACL types outside this API. `PosixExtractionException` is declared but not used by the implementation in this subset.

## Test Signals

Expected signals are binary xattr round trips, malformed version/tag/id/mask rejection, and compatibility with Linux POSIX ACL xattr ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/acl_converter_unittest.cc

## Purpose

This file contains intended ACL converter fixtures and tests, but the actual test bodies are commented out.

## Important APIs, Types, and Functions

Fixtures `kMinimalXattr` and `kExtendedXattr` encode POSIX ACL xattr byte sequences. Commented tests describe minimal, extended, and failed ACL conversion checks.

## Control Flow

No active test control flow is compiled besides includes and fixture definitions. The commented flow would extract POSIX/xattr data, convert to ACL, serialize back, and mutate fixture bytes to verify failures.

## State and Persistence Behavior

No runtime state is created by active tests.

## Dependencies and Integration Points

It includes `acl_converter.h` and GoogleTest, but currently contributes no assertions.

## Risks and Edge Cases

Because all meaningful tests are disabled, regressions in endian handling, id validation, tag ordering, and malformed xattr rejection can pass the test suite unnoticed.

## Test Signals

The current signal is only compile coverage. Re-enabling and updating these tests would provide direct converter validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_type.h -->
# sources/distributed-fs/lizardfs/src/common/acl_type.h

## Purpose

This header defines the ACL namespace/type enum used in metadata and serialization.

## Important APIs, Types, and Functions

`enum class AclType : uint8_t` has `kAccess`, `kDefault`, and `kRichACL`. Helpers are `hashCombineRaw()`, `serializedSize()`, `serialize()`, and `deserialize()`.

## Control Flow

Serialization writes the enum as one byte. Deserialization reads a byte and switches only over known values, throwing `IncorrectDeserializationException` for malformed values.

## State and Persistence Behavior

The enum value is serialized into metadata/protocol buffers wherever ACL type needs persistence.

## Dependencies and Integration Points

It depends on hash and serialization helpers and is used by ACL-bearing metadata structures.

## Risks and Edge Cases

Adding enum values requires updating `deserialize()` or old readers will reject them. The hash helper maps through `uint64_t`, so enum numeric stability matters for hashed structures.

## Test Signals

Useful signals are serialization round trips for all values and rejection of unknown byte values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/attributes.h -->
# sources/distributed-fs/lizardfs/src/common/attributes.h

## Purpose

This header defines the fixed-size attribute byte array used for LizardFS file metadata transport.

## Important APIs, Types, and Functions

The only public definition is `typedef std::array<uint8_t, 35> Attributes`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

`Attributes` is value storage for a 35-byte metadata attribute record. Its size is part of protocol and metadata layout expectations.

## Dependencies and Integration Points

It depends on `<array>` and `<cstdint>`. Protocol, metadata, and client/server code can use this alias for packed attribute blobs.

## Risks and Edge Cases

Changing the size is an ABI/protocol change. The alias carries no field-level semantics, so callers must use matching pack/unpack logic elsewhere.

## Test Signals

Signals are compile-time size checks and protocol round trips that encode/decode file attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/attributes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor.cc -->
# sources/distributed-fs/lizardfs/src/common/block_xor.cc

## Purpose

This file implements in-place XOR of one byte buffer with another, optimized to let the compiler generate vectorized aligned loops when possible.

## Important APIs, Types, and Functions

Public function is `blockXor(uint8_t* dest, const uint8_t* source, size_t size)`. Internal helpers are `blockXorAligned()` and `blockXorUnaligned()`, with `ALIGNMENT` set to 16 and optional `__builtin_assume_aligned`.

## Control Flow

`blockXor()` compares source and destination pointer alignment modulo 16. If they can become jointly aligned, it XORs an unaligned prefix and then calls the aligned loop for the remainder. Otherwise it uses the byte loop for all data.

## State and Persistence Behavior

The function mutates `dest` in-place and has no other state.

## Dependencies and Integration Points

It depends on `massert` for debug assertions. XOR/EC read plans and parity calculations can use this helper.

## Risks and Edge Cases

The test currently passes `v2.data() + i` while varying `j`, so it does not fully exercise differing source/destination alignments. Overlapping buffers are not documented; byte-wise XOR is deterministic for exact same pointer but arbitrary overlaps can produce unintended results.

## Test Signals

`block_xor_unittest.cc` verifies no exceptions/crashes over some offsets and sizes. Stronger tests should compare bytes against a scalar reference across all offset pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor.h -->
# sources/distributed-fs/lizardfs/src/common/block_xor.h

## Purpose

This header declares the common in-place XOR primitive used by chunk/parity code.

## Important APIs, Types, and Functions

It declares `void blockXor(uint8_t* dest, const uint8_t* source, size_t size)`.

## Control Flow

No control flow is present in the header. Callers provide destination, source, and byte count; implementation selects aligned or unaligned processing.

## State and Persistence Behavior

The API mutates the destination buffer only.

## Dependencies and Integration Points

It includes platform and integer headers. It is a low-level dependency for erasure/parity reconstruction.

## Risks and Edge Cases

The contract does not specify null handling for zero size, overlap behavior, or alignment requirements. Callers should provide valid byte ranges.

## Test Signals

Expected tests compare output bytes for varied alignments, zero length, and large block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/block_xor_unittest.cc

## Purpose

This GoogleTest file smoke-tests `blockXor()` across several offsets and sizes.

## Important APIs, Types, and Functions

It defines `TEST(BlockXorTests, BlockXor)` and calls `blockXor()` for sizes 6000, 32, and 5.

## Control Flow

Two 7000-byte vectors are allocated. Nested loops call `blockXor()` for offset values, but both pointers use `+ i`, so `j` does not affect the source offset.

## State and Persistence Behavior

Only local vectors are mutated. No persistence is involved.

## Dependencies and Integration Points

It depends on GoogleTest and `block_xor.h`.

## Risks and Edge Cases

The test asserts only that calls do not throw; it does not verify XOR results. Because the source offset ignores `j`, many intended alignment combinations are not exercised.

## Test Signals

Passing this test is a weak crash-safety signal. Correctness needs byte comparisons against expected XOR output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/case_sensitivity.h -->
# sources/distributed-fs/lizardfs/src/common/case_sensitivity.h

## Purpose

This header defines a small enum for APIs that need to choose case-sensitive or case-insensitive behavior.

## Important APIs, Types, and Functions

`enum class CaseSensitivity` has `kIgnore` and `kSensitive`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

The enum is value state only. No serialization helpers are declared here.

## Dependencies and Integration Points

It includes `common/platform.h`. Path/name matching code can use this type to avoid boolean ambiguity.

## Risks and Edge Cases

Because no serialization or parsing helpers are present, each caller must define its own external representation if needed.

## Test Signals

Compile coverage of case-sensitivity-aware callers is the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/case_sensitivity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cfg.cc -->
# sources/distributed-fs/lizardfs/src/common/cfg.cc

## Purpose

This file implements a legacy process-global configuration file parser and typed getters.

## Important APIs, Types, and Functions

Public functions are `cfg_load()`, `cfg_reload()`, `cfg_term()`, `cfg_filename()`, `cfg_isdefined()`, and generated getters for strings, integers, unsigned integers, int sizes, uint sizes, and double. Internal state is a linked list of `paramstr` nodes plus `cfgfname` and `logundefined`.

## Control Flow

`cfg_load()` resets global state, duplicates the filename, and calls `cfg_do_load()`. The parser reads lines up to 1000 bytes, accepts uppercase/underscore names, `=`, printable values, trailing whitespace or comments, and replaces duplicate definitions. Getters linearly scan the list and convert with `strtol`/`strtoul`/`strtod` or duplicate strings, logging defaults when configured.

## State and Persistence Behavior

Configuration is stored in process-global heap memory until `cfg_term()`. `cfg_reload()` tears down and reloads the current filename.

## Dependencies and Integration Points

It depends on C stdio/string allocation, logging, and assertion helpers. Many LizardFS daemons use these getters for startup/reload configuration.

## Risks and Edge Cases

The subsystem is not thread-safe. `cfg_load()` does not call `cfg_term()` before replacing existing state. Numeric conversions do not validate full-string consumption, overflow, or signed-to-unsigned range. `cfg_term()` frees globals but does not reset pointers, so repeated termination without reload can double-free.

## Test Signals

Useful tests parse comments, whitespace, duplicate keys, malformed lines, all numeric types, reload behavior, and repeated term/load lifecycles. No direct unit test is present here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cfg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cfg.h -->
# sources/distributed-fs/lizardfs/src/common/cfg.h

## Purpose

The header declares the global configuration loader/getter API and typed convenience wrappers.

## Important APIs, Types, and Functions

Public declarations include `cfg_load`, `cfg_reload`, `cfg_term`, `cfg_filename`, `cfg_isdefined`, typed `cfg_get*` functions, overloads `cfg_get()`, `cfg_ranged_get()`, templates `cfg_get_minvalue()`, `cfg_get_maxvalue()`, `cfg_get_minmaxvalue()`, and `cfg_warning_on_value_change()`.

## Control Flow

Callers load a config file, request typed values with defaults, optionally clamp ranges, and terminate on shutdown. Range helpers log when values are outside accepted bounds.

## State and Persistence Behavior

The header exposes a process-global runtime config model implemented in `cfg.cc`. Returned `char*` values from `cfg_getstr`/string-copy paths are heap allocations requiring caller discipline.

## Dependencies and Integration Points

It depends on `slogger` and standard integer/string types. It is a cross-daemon common API.

## Risks and Edge Cases

Template helpers use `std::to_string`, so they require numeric-like types. `cfg_get(const char*, const std::string defaultValue)` passes default by value rather than const reference. The API does not express ownership for `char*` getters in the type system.

## Test Signals

Coverage should include clamping logs, changed-value warnings, default logging, string ownership, and each typed getter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/charts.cc -->
# sources/distributed-fs/lizardfs/src/common/charts.cc

## Purpose

This legacy subsystem stores rolling time-series statistics and renders them as binary data, CSV, or indexed PNG charts.

## Important APIs, Types, and Functions

Public functions include `charts_init()`, `charts_term()`, `charts_add()`, `charts_store()`, `charts_get()`, `charts_datasize()`, `charts_makedata()`, `charts_make_csv()`, `charts_get_csv()`, `charts_make_png()`, and `charts_get_png()`. Important internals are fixed constants `LENG=950`, four ranges, static `series`, `pointers`, `timepoint`, chart buffers, PNG templates, optional zlib stream, `charts_load()`, old-format importers, `charts_filltab()`, `charts_makechart()`, and CRC/compression helpers.

## Control Flow

Initialization copies chart definitions, allocates fixed ring buffers, loads prior stats from disk, initializes time pointers, advances empty current slots, and initializes zlib if available. `charts_add()` maps timestamps into one-minute, six-minute, thirty-minute, and daily ranges, rolling pointers and aggregating values by add/max mode. Rendering fills display arrays, scales axes, draws chart pixels/text, packs 4-bit indexed pixels, compresses or fake-compresses, and emits PNG or CSV.

## State and Persistence Behavior

The file uses extensive process-global mutable state. `charts_store()` persists a binary stats file containing version, length, chart names, timepoint, and ring data. `charts_load()` restores matching names and imports older three/four-range formats.

## Dependencies and Integration Points

It depends on zlib when available, CRC helpers, datapack endian helpers, filesystem current-directory helpers, logging, and the definitions supplied by master/chunkserver stats code.

## Risks and Edge Cases

The subsystem is not thread-safe; PNG/CSV buffers are singletons. File IO uses fixed records and partial-write errors leave truncated files. Calculation definitions are stack-machine programs without strong validation. Large values require overflow mitigation during scaling. Date/time handling mixes localtime/gmtime and optional GMT offset behavior.

## Test Signals

Strong signals would include persistence round trips, old-format imports, chart id validation, CSV timestamp checks across ranges, PNG CRC validation, zlib/no-zlib builds, and concurrent render/add protection if used from multiple threads. No direct unit test is present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/charts.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/charts.h -->
# sources/distributed-fs/lizardfs/src/common/charts.h

## Purpose

This header defines the chart subsystem's public constants, chart definition structures, expression macros, and rendering/storage API.

## Important APIs, Types, and Functions

Important macros define aggregation modes, scales, expression opcodes, direct/calc chart ids, `CHARTS_NODATA`, and helper expression builders such as `CHARTS_ADD`, `CHARTS_DIV`, and `CHARTS_CALCDEF`. `statdef` describes direct series; `estatdef` describes extended three-color charts. Public functions mirror the implementation in `charts.cc`.

## Control Flow

The header is declarative, but the macros are used to build reverse-polish calculation programs consumed by `charts_filltab()`.

## State and Persistence Behavior

Chart definitions passed to `charts_init()` define how runtime series are stored and persisted. `CHARTS_NODATA` is the sentinel value for missing samples.

## Dependencies and Integration Points

It includes integer and stdio headers and is consumed by services that publish charts to CGI/status endpoints.

## Risks and Edge Cases

`CHARTS_SUB(x,y)` expands to `CHARTS_OP_ADD`, which appears inconsistent with the `CHARTS_OP_SUB` opcode and can silently compute wrong calculated charts. Macro expression programs are untyped and validated only at runtime.

## Test Signals

Tests should compile representative `STATDEFS`, `CALCDEFS`, and `ESTATDEFS`, verify all arithmetic opcodes, and render direct and calculated charts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/charts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_connector.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_connector.cc

## Purpose

This file implements TCP connection creation/reuse for communication with chunkservers.

## Important APIs, Types, and Functions

Implemented functions are `timeoutTime()`, `ChunkConnector::ChunkConnector()`, `startUsingConnection()`, `endUsingConnection()`, `ChunkConnectorUsingPool::ChunkConnectorUsingPool()`, `startUsingConnection()`, and `endUsingConnection()`.

## Control Flow

`startUsingConnection()` loops until the caller's `Timeout` expires: create socket, optionally bind source IP, compute retry timeout from RTT and retry count capped by remaining time, attempt `tcpnumtoconnect()`, and retry on connection failure. On success it sets `TCP_NODELAY`. The pool subclass first asks `ConnectionPool` for an existing descriptor, otherwise falls back to creating one; returning a connection puts it back into the pool.

## State and Persistence Behavior

Base connector stores source IP and RTT estimate. The pool connector references external pool state. No persistent state is used.

## Dependencies and Integration Points

It integrates sockets wrappers, `NetworkAddress`, `Timeout`, `ConnectionPool`, logging, and `ChunkserverConnectionException`.

## Risks and Edge Cases

Connection failures throw exceptions after closing descriptors. RTT backoff uses bit shifting on retry count and can grow quickly. Pool reuse assumes descriptors are still valid and protocol-clean. Source-IP bind failure stops retries immediately.

## Test Signals

Signals include successful connect, timeout behavior, bind failure, `TCP_NODELAY` warning-only behavior, pool hit/miss, and put-back expiration. No direct unit test is present here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_connector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_connector.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_connector.h

## Purpose

This header declares connector abstractions and an RAII connection wrapper for chunkserver TCP connections.

## Important APIs, Types, and Functions

`ChunkConnector` exposes virtual `startUsingConnection()`/`endUsingConnection()` plus RTT/source-IP setters. `Connection` opens in its constructor, closes in `destroy()`, returns to connector in `endUsing()`, and closes in its destructor if still owned. `ChunkConnectorUsingPool` integrates a `ConnectionPool`.

## Control Flow

Callers create `Connection`, use `fd()`, then either call `endUsing()` to return it to connector/pool or let destruction close it. The pool subclass changes end behavior from close to timed pool insertion.

## State and Persistence Behavior

The RAII object owns one descriptor at a time and marks it `-1` after destroy/end. The connector stores connection tuning only.

## Dependencies and Integration Points

It depends on socket wrappers, network address, connection pool, and timeout utilities. Chunk readers/writers use this abstraction for chunkserver IO.

## Risks and Edge Cases

`Connection::endUsing()` does not set `fd_ = -1`, so the destructor will also call `destroy()` and close the descriptor after returning it to the pool. That is a serious ownership hazard unless callers avoid letting returned connections destruct normally or the code path is otherwise unused. The move constructor transfers the descriptor and invalidates the source.

## Test Signals

Tests should validate RAII close, move semantics, pool return without double close, and exception safety on failed connects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_connector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.cc

## Purpose

This file implements reconciliation between currently available chunk parts and a target `Goal`, including operation counts, target permutation optimization, redundancy evaluation, removal safety, and full-copy counting.

## Important APIs, Types, and Functions

Implemented public methods include constructors, `setTarget()`, `addPart()` via header inline, `removePart()`, `optimize()`, `evalRedundancyLevel()`, `isSafeEnoughToWrite()`, `updateRedundancyLevel()`, `countPartsToMove()`, `canRemovePart()`, `canMovePartToDifferentLabel()`, `getLabelsToRecover()`, `getRemovePool()`, and `getFullCopiesCount()`. Key helpers are `operationCount()`, `evalOperationCount()`, `evalSliceRedundancyLevel()`, and `removePartBasicTest()`.

## Control Flow

`optimize()` uses a linear-assignment optimizer per slice to permute target parts to minimize recover/remove operations. It then evaluates operation counts and redundancy. Operation counting compares available and target label multisets, with wildcard labels absorbing otherwise-extra copies. Redundancy treats standard copies as `copies - 1`, XOR/EC slices as available distinct part count minus required data count, and combines slices into whole-chunk redundancy.

## State and Persistence Behavior

State is in-memory `Goal available_`, `Goal target_`, cached redundancy levels, per-slice operation counts, and total operation count. Nothing is persisted directly.

## Dependencies and Integration Points

It depends on `Goal`, `MediaLabel`, `slice_traits`, `linear_assignment_optimizer`, `ChunksAvailabilityState`, and flat/small containers. Master chunk maintenance logic can use it to schedule replication/deletion.

## Risks and Edge Cases

Query methods assume `optimize()` or `evalRedundancyLevel()` has been called. `removePart()` copies the label map proxy into `auto labels` and erases from that copy-like object; correctness depends on `Goal::Slice` proxy semantics. Wildcard handling is subtle and easy to regress. Unknown slice types are treated as lost.

## Test Signals

`chunk_copies_calculator_unittest.cc` covers add/remove, state transitions, optimization, redundancy updates, removal safety, recovery label selection, remove pools, and move counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.h

## Purpose

The header declares `ChunkCopiesCalculator`, the master-side helper for deciding how to transform available chunk parts into a desired goal and how safe the current chunk is.

## Important APIs, Types, and Functions

Public APIs include target setup, part add/remove, `optimize()`, redundancy evaluation/update, safety checks, removal/move queries, label recovery/removal queries, operation counts, full-copy counts, state getters, and mutable access to available/target goals. Internal containers cache per-slice redundancy and operation counts.

## Control Flow

The intended lifecycle is set available/target state, call `optimize()`, then query required recover/delete/move operations and safety. `evalRedundancyLevel()` can be used separately when only state is needed.

## State and Persistence Behavior

The object is an in-memory calculator. `Goal` inputs and outputs may reflect persisted metadata elsewhere, but this class does not write storage.

## Dependencies and Integration Points

It depends on `ChunkPartType`, `ChunksAvailabilityState`, `Goal`, `MediaLabel`, and compact maps/vectors. It is integrated with replication/deletion scheduling and chunk health reporting.

## Risks and Edge Cases

Several getters return mutable references to internal goals, so callers can invalidate cached redundancy/operation counts without the class noticing. Many methods assert valid part indices rather than returning errors. Querying before optimization can return stale/default counts.

## Test Signals

Unit tests in this subset exercise the main lifecycle. Additional tests should cover EC goals, wildcard-heavy goals, mutation through `getAvailable()` after optimization, and large expected-copy limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator_unittest.cc

## Purpose

This file validates `ChunkCopiesCalculator` behavior for goal matching, redundancy, optimization, and operation queries.

## Important APIs, Types, and Functions

Tests include `addPart`, `removePart`, `getState`, `evalRedundancyLevel`, `optimize`, `updateRedundancyLevel`, `canRemoveExtraPartsFromSliceSimple`, `canRemoveExtraPartsFromSlice`, `getLabelsToRecover`, `getRemovePool`, and `countPartsToMove`. It uses `goal_config::parseLine()` and chunk type constants.

## Control Flow

Tests build goals from text, add/remove parts with media labels, call `optimize()` or redundancy methods, and assert state/operation/label results.

## State and Persistence Behavior

All state is test-local `Goal` and calculator objects. No disk persistence is involved.

## Dependencies and Integration Points

It integrates the calculator with goal parsing, `slice_traits`, media labels, and chunk type constants.

## Risks and Edge Cases

Coverage is strong for XOR and standard cases but does not visibly cover EC slices, wildcard-only targets broadly, or mutation after cached optimization. Several tests mutate internal `Goal&` references, matching real usage but also bypassing encapsulation.

## Test Signals

Passing tests signal that scheduling counts and safety decisions match expected XOR/standard goal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_part_type.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_part_type.h

## Purpose

This header defines compact identifiers for chunk part types, including legacy one-byte encoding and modern two-byte encoding that supports more slice types and parts.

## Important APIs, Types, and Functions

`legacy::ChunkPartType` stores an 8-bit id with `kMaxPartsCount=11` and `kMaxType=9`. Modern `ChunkPartType` stores a 16-bit id with `kMaxPartsCount=64` and `kMaxTypeCount=2048`. Both expose constructors, `getSliceType()`, `getSlicePart()`, `getId()`, `isValid()`, `toString()`, comparisons, and serialization/deserialization. Modern type converts to/from legacy.

## Control Flow

Ids are computed as `slice_type * max_parts + part`. Deserialization validates that the resulting type/part is valid for `Goal::Slice::Type`. Legacy conversion clamps unsupported modern values to an invalid-but-representable legacy type.

## State and Persistence Behavior

The id is serialized into protocols/metadata. Numeric stability is critical for compatibility.

## Dependencies and Integration Points

It depends on `Goal`, `slice_traits`, and serialization helpers. It is used by planners, chunk metadata structs, network messages, and calculators.

## Risks and Edge Cases

Changing `kMaxPartsCount` or `Goal::Slice::Type` numbering changes the wire/storage encoding. Legacy conversion intentionally loses information for unsupported types. Assertions guard constructor ranges only in debug builds.

## Test Signals

`chunk_part_type_unittest.cc` covers serialization, valid id space, chunk part lengths, and block counts for standard/XOR/EC-related traits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_part_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_part_type_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_part_type_unittest.cc

## Purpose

This file validates chunk part type serialization, id validity, and slice length/block calculations.

## Important APIs, Types, and Functions

Tests are `SerializeDeserialize`, `validChunkTypeIDTest`, `chunkTypeLengthTest`, and `GetNumberOfBlocks`. It uses `slice_traits` helpers and chunk type constants.

## Control Flow

The tests enumerate standard, tape, XOR levels, and EC data/parity combinations, marking valid ids across the 16-bit space. They serialize/deserialize known types and check length/block arithmetic for representative chunk lengths.

## State and Persistence Behavior

Only local vectors/booleans are used.

## Dependencies and Integration Points

It integrates `ChunkPartType` with `Goal::Slice::Type` and `slice_traits`.

## Risks and Edge Cases

The valid-id test is broad but can be expensive because it scans all 65536 ids. Length tests are representative, not exhaustive for every EC layout.

## Test Signals

Passing tests are strong signals that type encoding and core slice arithmetic remain compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_part_type_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_read_planner.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_read_planner.h

## Purpose

`ChunkReadPlanner` builds a `ReadPlan` that reads a contiguous full-chunk block range from available chunk parts, including split XOR/EC layouts.

## Important APIs, Types, and Functions

Public APIs are constructor, `prepare()`, `setScores()`, `isReadingPossible()`, and `buildPlan()`. Internal helpers are `BlockConverter`, `getTypeList()`, and `getRequiredParts()`.

## Control Flow

`prepare()` collects slice types present in available parts, then scans each type. For each type it computes required data part indices for the requested full-chunk block range, asks `SliceReadPlanner` if those parts are readable, and records block/part ranges for the first successful type. `buildPlan()` gets a part-level plan and, for nonstandard types, appends `BlockConverter` to reorder split part blocks into contiguous chunk order.

## State and Persistence Behavior

The planner stores transient selected type, required parts, and range metadata. Returned plans own executable read/postprocess steps; no persistent state is written.

## Dependencies and Integration Points

It depends on `SliceReadPlanner`, `slice_traits`, `ReadPlan`, `small_vector`, and `MFSBLOCKSIZE`. `SliceRecoveryPlanner` uses it for reconstructing missing parts from full chunk data.

## Risks and Edge Cases

Type selection is first-successful, not globally cheapest, despite score support inside `SliceReadPlanner`. TODOs note over-reading for multi-lane requests. Validation is mostly assert-only; invalid ranges in release builds can produce bad plans.

## Test Signals

`chunk_read_planner_unittest.cc` exercises representative XOR reads and output byte comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_read_planner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_read_planner_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_read_planner_unittest.cc

## Purpose

This file verifies that `ChunkReadPlanner` can reconstruct contiguous chunk data from available split parts.

## Important APIs, Types, and Functions

Helpers are `xor_part()` and `checkReadingChunk()` overloads. Active tests are `VerifyRead1` through `VerifyRead4`.

## Control Flow

Tests build synthetic part data, prepare a planner for a full-chunk block range, assert readability, execute the returned plan through `ReadPlanTester`, and compare output bytes with the standard chunk data.

## State and Persistence Behavior

Only local byte maps and planner/tester objects are used.

## Dependencies and Integration Points

It depends on the planner, chunk type constants, and `ReadPlanTester`.

## Risks and Edge Cases

Unrecoverable tests are present but commented out. EC layouts, score preference, invalid ranges, and no-plan cases are not covered here.

## Test Signals

Passing tests signal correct block extraction/reordering for representative XOR layouts and block ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_read_planner_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_type_with_address.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_type_with_address.h

## Purpose

This header defines serializable records pairing a chunkserver address with a chunk part type, including a modern version carrying chunkserver version metadata.

## Important APIs, Types, and Functions

`legacy::ChunkTypeWithAddress` stores `NetworkAddress address` and legacy `ChunkPartType chunkType`. Modern `ChunkTypeWithAddress` stores `NetworkAddress address`, `ChunkPartType chunk_type`, and `uint32_t chunkserver_version`. Both define equality, ordering, and serialization methods.

## Control Flow

No runtime algorithm is present. Comparisons use address and part type; modern comparisons intentionally ignore `chunkserver_version`.

## State and Persistence Behavior

Instances are serialized in messages/metadata that list where a chunk part is stored. Modern serialization includes chunkserver version for compatibility decisions.

## Dependencies and Integration Points

It depends on network address, chunk part type, slice traits, and serialization macros. Readers, repair planners, and chunkserver selection code consume these records.

## Risks and Edge Cases

Ignoring `chunkserver_version` in equality/order is intentional for CRC error counting, but containers keyed by this type cannot distinguish same address/type with different versions. Legacy and modern field names differ.

## Test Signals

Useful tests are serialization round trips and set/map behavior proving version-insensitive comparison where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_type_with_address.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_version_with_todel_flag.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_version_with_todel_flag.h

## Purpose

This header defines helpers for packing a chunk version and deletion flag into one 32-bit field.

## Important APIs, Types, and Functions

In namespace `common`, `chunk_version_t` is `uint32_t`, `TODEL_MASK` is the high bit, `VERSION_MASK` is the low 31 bits, and constexpr helpers are `combineVersionWithTodelFlag()`, `getChunkVersion()`, and `getTodelFlag()`.

## Control Flow

All behavior is constexpr bit masking/or-ing.

## State and Persistence Behavior

The packed value is used in chunk info sent in `cstoma::chunkNew` and `cstoma::registerChunks` packets, making the bit layout a protocol contract.

## Dependencies and Integration Points

It integrates chunkserver/master registration messages and any code that interprets deletion state alongside versions.

## Risks and Edge Cases

Versions larger than 31 bits collide with the deletion flag; callers must ensure raw chunk versions fit `VERSION_MASK`. `getTodelFlag()` returns bool from a masked integer.

## Test Signals

Tests should cover packing/unpacking with flag false/true, max 31-bit version, and accidental high-bit input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_version_with_todel_flag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_address_and_label.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_with_address_and_label.h

## Purpose

This header defines serializable chunk-location records that include network addresses, media labels, and chunk part types.

## Important APIs, Types, and Functions

Legacy and modern `ChunkPartWithAddressAndLabel` classes store `NetworkAddress address`, `std::string label`, and a chunk part type. Modern `ChunkWithAddressAndLabel` stores `chunk_id`, `chunk_version`, and a vector of chunk parts.

## Control Flow

No algorithmic control flow exists. Equality/order for part records compare address, label, and chunk type.

## State and Persistence Behavior

These value objects are serialized into protocol or metadata messages describing all known locations/labels for a chunk.

## Dependencies and Integration Points

It depends on media labels, network addresses, chunk part types, and serialization macros. Master/client/chunkserver reporting paths can use these records for placement and goal decisions.

## Risks and Edge Cases

Labels are serialized as strings, so normalization must happen elsewhere. Legacy and modern chunk type encodings differ; conversions must be explicit at message boundaries.

## Test Signals

Expected tests include serialization round trips, ordering in sorted containers, and compatibility conversion from legacy records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_address_and_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_version.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_with_version.h

## Purpose

This header defines a minimal serializable pair of chunk id and version.

## Important APIs, Types, and Functions

`LIZARDFS_DEFINE_SERIALIZABLE_CLASS(ChunkWithVersion, uint64_t id, uint32_t version)` generates the value class and serialization methods.

## Control Flow

There is no explicit control flow beyond generated serialization.

## State and Persistence Behavior

Instances carry persistent chunk identity/version data in protocol or metadata messages.

## Dependencies and Integration Points

It depends on serialization macros and fixed-width integer types.

## Risks and Edge Cases

The macro hides generated constructors/operators, so readers must inspect macro definitions for exact behavior. Version flag packing, if needed, is not handled here.

## Test Signals

Serialization round trips and protocol compatibility tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_version_and_type.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_with_version_and_type.h

## Purpose

This header defines serializable chunk id/version/type records with legacy and modern chunk part type encodings.

## Important APIs, Types, and Functions

Both `legacy::ChunkWithVersionAndType` and modern `ChunkWithVersionAndType` store `uint64_t id`, `uint32_t version`, and a chunk part type. They provide constructors, `toString()`, ordering, equality, and serialization. The modern type can construct from the legacy type.

## Control Flow

`toString()` formats hex chunk id and version plus the part type string. Comparisons order by `(id, version, type)`.

## State and Persistence Behavior

Instances are wire/storage value records for chunk metadata. Modern and legacy types preserve compatibility across protocol versions.

## Dependencies and Integration Points

It depends on `ChunkPartType`, `slice_traits`, and serialization macros.

## Risks and Edge Cases

String output is hex and zero-padded, which is useful for diagnostics but should not be parsed unless explicitly documented. Legacy-to-modern conversion is straightforward; modern-to-legacy can lose unsupported type information elsewhere.

## Test Signals

Expected signals are serialization compatibility, ordering behavior, and string output for standard/XOR/EC types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_version_and_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunks_availability_state.h -->
# sources/distributed-fs/lizardfs/src/common/chunks_availability_state.h

## Purpose

This header defines aggregate counters for chunk availability and replication/delete needs by goal.

## Important APIs, Types, and Functions

`detail::SerializableGoalIdArray<T>` stores arrays indexed by goal id but serializes only non-default entries as a map. `ChunksAvailabilityState` tracks safe, endangered, and lost counts per goal. `ChunksReplicationState` tracks chunks to replicate by missing-part count and chunks to delete by redundant-part count.

## Control Flow

Add/remove methods increment/decrement indexed counters. Serialization compacts sparse goal arrays. Replication state clamps missing/redundant part counts at `kMaxPartsCount - 1`.

## State and Persistence Behavior

State is in-memory counters that serialize for status/protocol transport. It does not guard underflow.

## Dependencies and Integration Points

It depends on `GoalId`, serialization helpers, and `Goal`. Master status, CGI, and replication accounting can consume these counters.

## Risks and Edge Cases

`SerializableGoalIdArray::deserialize()` asserts the array is default-initialized before loading, so reusing a nonempty object in release builds may merge stale data. Remove operations can underflow `uint64_t` counters if misbalanced. `kMaxPartsCount` is 11, matching legacy reporting rather than all modern part counts.

## Test Signals

`chunks_availability_state_unittest.cc` covers add/remove counters and clamping of large missing/redundant values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunks_availability_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunks_availability_state_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunks_availability_state_unittest.cc

## Purpose

This file tests availability and replication-state counters.

## Important APIs, Types, and Functions

Tests are `ChunksAvailabilityStateTests.AddRemoveChunk`, `ChunksReplicationStateTests.AddRemoveChunk`, and `ChunksReplicationStateTests.MaximumValues`.

## Control Flow

The tests add counters for multiple goals/states, move counts between states by remove/add, remove counts back to zero, and verify replication/delete matrix counters including clamping for very large part counts.

## State and Persistence Behavior

Only local counter objects are used; serialization is not tested.

## Dependencies and Integration Points

It uses GoogleTest and the state header.

## Risks and Edge Cases

Underflow and serialization sparse-map behavior are not covered. Goal ids near `GoalId::kMax` are not tested directly.

## Test Signals

Passing tests signal basic counter indexing and clamping correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunks_availability_state_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats.cc -->
# sources/distributed-fs/lizardfs/src/common/chunkserver_stats.cc

## Purpose

This file implements thread-safe per-chunkserver pending-operation and defect scoring, plus a proxy that auto-unregisters operations.

## Important APIs, Types, and Functions

Implemented methods include `ChunkserverEntry::ChunkserverEntry()`, `score()`, `ChunkserverStats` register/unregister/get/mark methods, and all `ChunkserverStatsProxy` methods including destructor and `allPendingDefective()`.

## Control Flow

`ChunkserverStats` methods lock a mutex and update or return a copy of the entry for an address. Defects increment up to 1000 and reset a timeout; `score()` returns reduced score while the defect timeout is active. The proxy registers operations in both global stats and local maps, and its destructor unregisters all locally pending counts.

## State and Persistence Behavior

Stats are in-memory only. `globalChunkserverStats` is declared in the header but not defined in this file segment. Defect state decays by timeout rather than persistence.

## Dependencies and Integration Points

It depends on `NetworkAddress`, `Timeout`, mutex/unordered_map, and chunkserver selection/read/write code.

## Risks and Edge Cases

Unregister methods decrement unsigned counters without underflow checks. Proxy `unregister*()` decrements local map counters even if not present, which can underflow and cause destructor over-unregistration. `getStatisticsFor()` creates entries on read.

## Test Signals

`chunkserver_stats_unittest.cc` covers counters, defect score, proxy cleanup, and marking pending operations defective.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats.h -->
# sources/distributed-fs/lizardfs/src/common/chunkserver_stats.h

## Purpose

This header declares chunkserver load/defect statistics and a scoped proxy for operation registration.

## Important APIs, Types, and Functions

`ChunkserverStats::ChunkserverEntry` exposes pending read/write counts, total operation count, and `score()`. `ChunkserverStats` exposes read/write register/unregister and defect/working markers. `ChunkserverStatsProxy` exposes the same operation methods plus `allPendingDefective()` and unregisters tracked operations on destruction.

## Control Flow

Users register operations before IO, unregister afterward, and use scores/counts to prefer less loaded/nondefective chunkservers. The proxy is intended for scoped cleanup.

## State and Persistence Behavior

The stats object owns an address-to-entry map protected by a mutex. Entries track pending counters, defect count, and timeout. No disk persistence exists.

## Dependencies and Integration Points

It integrates with chunk readers/writers and global mount-instance stats through `extern ChunkserverStats globalChunkserverStats`.

## Risks and Edge Cases

The proxy is explicitly not thread-safe. Register/unregister balancing is required to avoid unsigned underflow. Because `getStatisticsFor()` returns by value, callers cannot mutate entries directly.

## Test Signals

Unit tests validate basic behavior. Additional tests should cover underflow attempts, defect timeout expiry, and concurrent register/unregister operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunkserver_stats_unittest.cc

## Purpose

This file tests chunkserver operation counters, defect scoring, and proxy cleanup behavior.

## Important APIs, Types, and Functions

Tests are `ChunkserverStatsCounters`, `ChunkserverStatsDefectTracking`, `ChunkserverStatsProxy`, `AllPendingDefectiveRead`, `AllPendingDefectiveWrite`, and `AllPendingDefectiveLonger`.

## Control Flow

Tests register/unregister reads and writes against sample addresses, inspect copied stats, mark defective/working, scope a proxy to trigger destructor cleanup, and mark only still-pending proxy operations defective.

## State and Persistence Behavior

Only local `ChunkserverStats` and proxy objects are used. Timeout expiry is not tested because checks happen immediately.

## Dependencies and Integration Points

It uses GoogleTest, `NetworkAddress`, and the stats classes.

## Risks and Edge Cases

The tests do not cover unregister underflow, concurrent access, or defect-score recovery after timeout. They verify immediate score reduction but not exact score values except equality to 1.

## Test Signals

Passing tests signal correct normal balanced operation accounting and proxy destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats_unittest.cc -->

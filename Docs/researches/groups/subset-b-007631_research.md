# Research: subset-b-007631

Grouped source research for the LizardFS metarestore and mount/client subset. Each file section preserves the source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metarestore/main.cc -->
# sources/distributed-fs/lizardfs/src/metarestore/main.cc

## Purpose
`main.cc` implements the `metarestore` command-line tool. It loads a LizardFS metadata image, optionally selects the best metadata backup automatically, replays changelog files through the metarestore merger, verifies or prints metadata checksums, and either dumps metadata/chunk state to stdout-like diagnostic paths or writes a restored metadata file.

## Important APIs, Types, And Functions
- `changelog_checkname(const char*)` recognizes current changelog filenames (`kChangelogFilename`, `kChangelogMlFilename`) and older MooseFS/LizardFS names such as `changelog.*.mfs`.
- `usage(const char*)` prints supported restore, dump, autorestore, version-probe, and version-display modes.
- `meta_version_on_disk(std::string)` computes the metadata version a master can recover from the on-disk metadata and changelog sequence.
- `main(int,char**)` parses flags, initializes hash-string storage, loads metadata with `fs_init`, selects changelogs, invokes `merger_start`/`merger_loop`, and persists with `fs_term` or diagnostic dumps.

## Control Flow
Startup calls `prepareEnvironment()`, opens syslog, and parses options `-g`, `-v`, `-m`, `-o`, `-d`, `-a`, `-b`, `-B`, `-i`, `-f`, `-c`, `-k`, `-z`, `-x`, and hidden `#` no-lock mode. It rejects incompatible modes: version recovery requires `-d`, autorestore cannot be combined with explicit metadata/output files, and normal mode requires `-m` with no data path. Version recovery calls `meta_version_on_disk` and exits. Autorestore scans known metadata backup candidates, chooses the highest readable metadata version, and sets output to `<data path>/metadata.mfs`.

After `fs_init`, the tool rejects metadata version `0`, scans changelogs either from the data directory or remaining command-line arguments, skips stale logs unless `-f` is set, and feeds selected files to `merger_start`. `merger_loop` replays records. If replay fails and `-b` was not set, the program exits before writing. Otherwise it computes the forced checksum, prints/checks it if requested, and either calls `fs_dump`/`chunk_dump` or rotates and writes the output metadata with `fs_term`.

## State And Persistence
The file operates on global master filesystem state initialized by `fs_init` and mutated by changelog restore calls. It can lock metadata unless hidden no-lock mode is used. Persistence happens only at the end via `fs_term(metaout)`, with `rotateFiles` applied when overwriting the source metadata path. Autorestore chooses among `metadata_ml.mfs.back.1`, `metadata.mfs.back.1`, `.1` variants, and current metadata names.

## Dependencies And Integration Points
It depends on common config/setup/logging, metadata version helpers, master filesystem/chunk restore internals, hstring memory storage, `rotateFiles`, and `metarestore/merger`. Changelog parsing and replay are delegated to `changelogGetFirstLogVersion`, `changelogGetLastLogVersion`, and `restore` through the merger module.

## Risks
- The hidden `#` no-lock option can bypass metadata locking and is risky if used while a master is active.
- `atoi` for `-B` does not validate negative or malformed input.
- Autorestore chooses the highest readable metadata candidate before changelog replay; bad but version-high metadata can still drive recovery.
- Skipping changelogs uses first/last version heuristics and `forcealllogs`; incorrect changelog version metadata may omit required records.
- `meta_version_on_disk` compares `fullFileName != kChangelogFilename`, but `fullFileName` includes the directory path, so the warning condition is effectively true for missing later candidates after any older changelog exists.

## Test Signals
Useful tests would cover CLI mode rejection, changelog name recognition for old and new formats, autorestore candidate selection, checksum return codes (`0` OK, `2` mismatch), and behavior with malformed metadata/changelogs. Integration coverage should exercise replay into a temporary metadata file and backup rotation count handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metarestore/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metarestore/merger.cc -->
# sources/distributed-fs/lizardfs/src/metarestore/merger.cc

## Purpose
`merger.cc` merges multiple changelog streams in ascending change-id order and replays them into master restore logic. It is the replay engine used by `metarestore/main.cc`.

## Important APIs, Types, And Functions
- Internal `hentry` stores an open changelog file, filename, line buffer, parse pointer, and next record id.
- `merger_start(const std::vector<std::string>&, uint64_t)` opens files, reads the first usable record from each, and initializes a min-heap ordered by `nextid`.
- `merger_loop()` repeatedly restores the smallest next record and advances/removes heap entries until all logs are exhausted or restore fails.
- `merger_nextentry`, `merger_heap_sort_up`, `merger_heap_sort_down`, `merger_delete_entry`, and `merger_new_entry` are internal heap and file-lifetime helpers.

## Control Flow
`merger_start` allocates a heap sized to the file list, opens each changelog, reads its first line, drops entries with invalid first ids, and heapifies incrementally. `merger_loop` takes `heap[0]`, calls `restore(filename,nextid,ptr,RestoreRigor::kIgnoreParseErrors)`, advances that file with `merger_nextentry`, removes exhausted or invalid files, and restores heap order after each step.

`merger_nextentry` parses the decimal id at the beginning of each line with `strtoull`, retaining the rest of the line in `ptr` for restore. It accepts only monotonically increasing ids with a gap less than `maxidhole`; otherwise it logs garbage at EOF and marks the file exhausted.

## State And Persistence
The module uses static global `heap`, `heapsize`, and `maxidhole`; it is single-session and not reentrant. It owns file descriptors, duplicated filename strings, and line buffers. It does not persist data directly; persistence happens after replay in `main.cc`.

## Dependencies And Integration Points
It integrates with `master/restore.h` for record application and LizardFS status/error codes. Syslog is used for invalid changelog or file-open messages. `BSIZE` fixes the maximum line read buffer at 200000 bytes.

## Risks
- `maxidhole` is assigned after initial `merger_nextentry` calls in `merger_start`; because initial `nextid` is `0`, first lines are accepted, but the ordering is fragile.
- Static global state means concurrent merger runs in one process would collide.
- `malloc(sizeof(hentry)*filenames.size())` with an empty vector may return null on some implementations; `main.cc` calls it with empty lists in some modes, although `merger_loop` then does no work.
- Changelog lines longer than `BSIZE-1` are split by `fgets`, likely causing parse errors or false garbage detection.
- The code frees C allocations manually and assumes all heap slots have been initialized by `merger_new_entry` before deletion.

## Test Signals
Targeted tests should feed multiple changelog files with interleaved ids, duplicate/non-monotonic ids, large id gaps, unreadable files, empty files, and restore failure propagation. A fake `restore` hook would make ordering assertions straightforward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metarestore/merger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metarestore/merger.h -->
# sources/distributed-fs/lizardfs/src/metarestore/merger.h

## Purpose
`merger.h` declares the public metarestore merger interface used by the `metarestore` CLI.

## Important APIs, Types, And Functions
- `int merger_start(const std::vector<std::string>& filenames, uint64_t maxhole)` initializes changelog inputs and id-gap tolerance.
- `uint8_t merger_loop(void)` replays all initialized changelog records and returns a LizardFS status code.

## Control Flow
The header enforces a two-step usage model: initialize with a file list, then call `merger_loop`. It exposes no object handle, indicating that implementation state is process-global.

## State And Persistence
The header itself has no state. Its API implies hidden global state owned by `merger.cc`; callers must not expect multiple independent merger instances.

## Dependencies And Integration Points
It includes `common/platform.h`, `<cstdint>`, `<string>`, and `<vector>`, and is included by `metarestore/main.cc`.

## Risks
- The API lacks an explicit cleanup function and exposes no ownership token, so lifecycle correctness is entirely inside `merger_loop`.
- Return type `uint8_t` conveys LizardFS status values but does not document the status domain in the declaration.

## Test Signals
Compile-time tests are minimal. Behavioral tests should include `merger.h` through `main.cc` or a small harness and verify that one initialized run completes and releases resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metarestore/merger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/mount/CMakeLists.txt

## Purpose
This CMake file defines the core `mount` shared library build and its unit-test target, and conditionally enters the client library subdirectory.

## Important APIs, Types, And Functions
- `include_directories(${CMAKE_CURRENT_SOURCE_DIR})` exposes mount headers to local targets.
- `collect_sources(MOUNT)` gathers source and test lists according to project macros.
- `shared_add_library(mount ${MOUNT_SOURCES})` builds the shared/static/PIC variants expected by the repository.
- `create_unittest(mount ${MOUNT_TESTS})` and `link_unittest(mount mount mfscommon)` wire mount tests.
- `if (ENABLE_CLIENT_LIB) add_subdirectory(client) endif()` controls client library builds.

## Control Flow
CMake first gathers all mount sources, builds the `mount` library linked against `mfscommon` and additional platform libraries, creates tests, then optionally builds C/C++ client wrappers.

## State And Persistence
This file contributes build graph state only. It does not create runtime state or installed artifacts directly except through targets.

## Dependencies And Integration Points
It relies on project-defined macros such as `collect_sources`, `shared_add_library`, `shared_target_link_libraries`, `create_unittest`, and `link_unittest`. The client subdirectory depends on `ENABLE_CLIENT_LIB`.

## Risks
- Broad `include_directories` affects all following targets in this directory scope.
- Source collection depends on project macros; missing or misclassified files in those macros can silently change library contents.

## Test Signals
Build configuration tests should cover `ENABLE_CLIENT_LIB` on/off and validate that mount unit tests link with `mount` and `mfscommon`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/acl_cache.h -->
# sources/distributed-fs/lizardfs/src/mount/acl_cache.h

## Purpose
`acl_cache.h` defines the ACL cache entry type and loader function used by mount-side permission handling.

## Important APIs, Types, And Functions
- `AclAcquisitionException` wraps non-ENOATTR ACL retrieval failures.
- `RichACLWithOwner` stores a `RichACL` plus owner uid.
- `AclCacheEntry` is `std::shared_ptr<RichACLWithOwner>`.
- `AclCache` is an `LruCache` keyed by inode, uid, and gid, configured with `UseTreeMap` and `Reentrant`.
- `getAcl(uint32_t inode, uint32_t uid, uint32_t gid)` calls `fs_getacl` and returns an entry, null on `ENOATTR`, or throws on other errors.

## Control Flow
`getAcl` allocates a cache entry, asks master communication (`fs_getacl`) for ACL and owner, returns the entry on success, returns an empty shared pointer if no ACL attribute exists, and throws `AclAcquisitionException(status)` for all other statuses.

## State And Persistence
The file defines cache value structure but not a global cache instance. Persistence remains in master metadata; cached ACLs are transient and credential-scoped by key.

## Dependencies And Integration Points
It depends on `mount/mastercomm.h` for `fs_getacl`, `RichACL`, `LruCache`, and LizardFS status codes. It integrates with any caller using `LruCache` to memoize ACL fetches.

## Risks
- Empty `AclCacheEntry` is a meaningful negative-cache value; callers must distinguish missing ACL from acquisition errors.
- Exceptions from `getAcl` cross cache loader boundaries and must be handled by permission code.
- The cache key includes uid/gid, which is correct for credential-sensitive ACL evaluation but can increase cache cardinality.

## Test Signals
Tests should stub `fs_getacl` for OK, `ENOATTR`, and other error codes, ensuring returned owner/ACL propagation, negative result behavior, and exception status preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/acl_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_locator.cc -->
# sources/distributed-fs/lizardfs/src/mount/chunk_locator.cc

## Purpose
`chunk_locator.cc` implements master lookups for read and write chunk locations. It translates master statuses into read/write exception classes and maintains read-side caching and write-side lock lifecycle.

## Important APIs, Types, And Functions
- `ReadChunkLocator::locateChunk(inode,index)` returns a cached or freshly fetched `ChunkLocationInfo`.
- `ReadChunkLocator::invalidateCache(inode,index)` clears the one-entry cache if it matches.
- `WriteChunkLocator::locateAndLockChunk(inode,index)` asks the master for write locations and a lock id via `fs_lizwritechunk`.
- `WriteChunkLocator::unlockChunk()` sends `WRITE_END` with chunk id, lock id, inode, and final file length.

## Control Flow
Read lookup first checks a mutex-protected one-entry cache. On miss it calls either legacy `fs_readchunk` parsing raw server address data, or modern `fs_lizreadchunk` filling `locations`. Master `ENOENT` is treated as unrecoverable, other nonzero read errors as recoverable. The result is cached under lock.

Write lookup asserts a single active inode/index, clears prior locations, keeps old lock/file length, calls `fs_lizwritechunk`, maps transient statuses (`IO`, no chunkservers, locked, busy, lost) to `RecoverableWriteException`, maps others to unrecoverable and clears `lockId_`, and preserves previous file length when refreshing an existing lock. Unlock sends `fs_lizwriteend`; communication IO is recoverable, returned non-OK after unlock is unrecoverable.

## State And Persistence
Read state is a single cached `shared_ptr<const ChunkLocationInfo>` plus inode/index protected by a mutex. Write state is inode/index, lock id, and mutable `locationInfo_` file length. Locks are persisted/owned at the master until `WRITE_END`; the destructor in the header attempts unlock if needed.

## Dependencies And Integration Points
It integrates with `mount/mastercomm.h`, `protocol/MFSCommunication.h`, common exceptions, request logging, and chunkserver address/type structures. `ChunkReader` and `ChunkWriter` consume these locators.

## Risks
- `ReadChunkLocator` default constructor in the header does not initialize `inode_`/`index_`; cache checks are safe only because `cache_` gates their use.
- Write locators assume one chunk at a time; misuse across multiple inode/index pairs trips `sassert`.
- Destructor unlock failures are logged but cannot be propagated.
- Recoverable/unrecoverable classification controls retry behavior and must stay aligned with master semantics.

## Test Signals
Tests should mock master calls for cache hits/misses, legacy parsing, status-to-exception mapping, repeated write-lock refresh preserving file length, unlock IO failure, and destructor unlock logging behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_locator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_locator.h -->
# sources/distributed-fs/lizardfs/src/mount/chunk_locator.h

## Purpose
`chunk_locator.h` declares data structures and classes for locating file chunks on chunkservers and managing write locks.

## Important APIs, Types, And Functions
- `ChunkLocationInfo` stores `chunkId`, `version`, `fileLength`, and `std::vector<ChunkTypeWithAddress> locations`; `isEmptyChunk()` reports sparse chunks with id `0`.
- `ReadChunkLocator` is a thread-safe per-descriptor read locator with a one-entry cache.
- `WriteChunkLocator` owns a master write lock and exposes `locateAndLockChunk`, `unlockChunk`, `chunkIndex`, `updateFileLength`, and `locationInfo`.
- `TruncateWriteChunkLocator` adapts master-owned locks for truncation so the client destructor does not unlock them.

## Control Flow
Callers use `ReadChunkLocator::locateChunk` before reads and invalidate after stale data signals. Writers call `locateAndLockChunk`, pass `locationInfo` to `ChunkWriter`, update file length as writes complete, and eventually call `unlockChunk`. `WriteChunkLocator` also unlocks in its destructor if a lock remains.

## State And Persistence
The header declares transient locator state only. `WriteChunkLocator` state mirrors a master lock and final file length that will be persisted when write-end reaches the master.

## Dependencies And Integration Points
It depends on `ChunkTypeWithAddress`, logging, exceptions, and master communication implementation in the `.cc`. It is consumed by chunk read/write classes and truncate paths.

## Risks
- The destructor catches only `Exception&`; non-LizardFS exceptions from unlock would escape a destructor.
- `updateFileLength` has a cosmetic `locationInfo_. fileLength` spacing issue but compiles.
- The API exposes `locationInfo` by const reference while internal file length can later change.

## Test Signals
Unit tests should verify destructor behavior with fake locators, single-chunk invariant, `TruncateWriteChunkLocator` not unlocking, and `isEmptyChunk` sparse-read decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_locator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_reader.cc -->
# sources/distributed-fs/lizardfs/src/mount/chunk_reader.cc

## Purpose
`chunk_reader.cc` implements chunk-level read planning and execution. It chooses the best chunkserver locations for each chunk part, handles sparse/EOF reads, and tracks CRC-failed locations to avoid retrying bad copies.

## Important APIs, Types, And Functions
- `ChunkReader::prepareReadingChunk(inode,index,force_prepare)` locates a chunk and prepares part-location maps and planner scores.
- `ChunkReader::readData(buffer,offset,size,connectTimeout,waveTimeout,communicationTimeout,prefetchXorStripes)` reads available data and appends it to `buffer`.
- Static `ChunkReader::preparations` counts prepare calls for diagnostics.

## Control Flow
Preparing a new chunk clears CRC error memory, invalidates the read locator cache, fetches `ChunkLocationInfo`, returns early for sparse empty chunks, then iterates locations. For each chunk part type it selects the highest-scoring chunkserver from `globalChunkserverStats`, skipping locations previously associated with CRC exceptions. Scores and available part types are handed to `ChunkReadPlanner`.

Reading clamps the requested range to file length. Empty chunks append zeros. Non-empty chunks plan reads from block-aligned ranges, require the planner to report possible reconstruction, optionally disable XOR prefetch, and execute through `ReadPlanExecutor`. On `ChunkCrcException`, the failing server/type is recorded and the exception is rethrown. The buffer is then resized back to the actual available byte count to remove block-rounding padding.

## State And Persistence
State is per `ChunkReader`: current inode/index, cached location pointer, planner, available part list, selected location map, CRC-error list, and `chunkAlreadyRead` prefetch hint. There is no persistence; it reads chunkserver data and relies on master metadata.

## Dependencies And Integration Points
It integrates with `ReadChunkLocator`, `ChunkReadPlanner`, `ReadPlanExecutor`, `ChunkConnector`, `globalChunkserverStats`, `Timeout`, and common exception classes. Higher-level read paths call prepare/read for each file chunk.

## Risks
- `readData` assumes `prepareReadingChunk` has populated `location_`; callers must respect that lifecycle.
- `blockToReadCount` is computed from `availableSize` but not adjusted for nonzero intra-block offset; correctness depends on planner/executor handling first block offset semantics.
- CRC error memory is cleared only when changing chunks, so repeated forced prepares avoid bad locations within the same chunk.
- Prefetch is disabled at EOF or after first full read, which depends on page cache assumptions.

## Test Signals
Tests should cover sparse reads returning zeros, EOF clamping, planner failure raising `NoValidCopiesReadException`, highest-score server selection, CRC error suppression on retry, and buffer resizing for partial final blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_reader.h -->
# sources/distributed-fs/lizardfs/src/mount/chunk_reader.h

## Purpose
`chunk_reader.h` declares the `ChunkReader` class that performs prepared chunk reads using a connector and erasure/replication-aware planning.

## Important APIs, Types, And Functions
- Constructor accepts a `ChunkConnector` and `bandwidth_overuse` score/planner parameter.
- `prepareReadingChunk` locates the chunk and selects candidate chunkservers.
- `readData` appends bytes to a caller-owned buffer.
- Accessors expose whether a chunk is located, current inode/index, chunk id, and version.
- `preparations` is a static atomic diagnostic counter.

## Control Flow
The class separates prepare from read: a caller can prepare once per chunk and call `readData` for ranges. Force prepare bypasses the same-chunk short-circuit.

## State And Persistence
All state is transient and per reader. It includes the locator, selected locations, planner, and CRC-failed server/type list. No on-disk state is modified.

## Dependencies And Integration Points
It includes chunk connector, read planner/executor, connection pool, network address, time utilities, and `chunk_locator.h`. It is a mount read-path component.

## Risks
- Accessors `chunkId()` and `version()` dereference `location_`; callers must check `isChunkLocated` or ensure preparation.
- No explicit synchronization exists in `ChunkReader`; it appears intended for descriptor/path-local use rather than concurrent calls.

## Test Signals
Header-level tests are through implementation: lifecycle checks, accessor behavior after prepare, and correct use by higher-level read data code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_writer.cc -->
# sources/distributed-fs/lizardfs/src/mount/chunk_writer.cc

## Purpose
`chunk_writer.cc` implements chunk-level write execution. It batches write-cache blocks into full stripes, reads missing data for parity goals, sends writes to chunkservers through `WriteExecutor`, and tracks completion status back to write operations.

## Important APIs, Types, And Functions
- `ChunkWriter::init(locator, timeout)` creates one executor per chunk part type and sends write-init packets.
- `addOperation(WriteCacheBlock&&)` appends a writable/read block to the journal and groups compatible blocks into operations.
- `startNewOperations(can_expect_next_block)` starts operations when they are full enough and non-conflicting.
- `processOperations(msTimeout)` polls data-chain and chunkserver sockets, sends queued packets, receives statuses, and detects connection errors/timeouts.
- `finish(msTimeout)` sends end packets and returns connections to the connector.
- `abortOperations()` closes sockets immediately.
- Internal `Operation` tracks journal positions, parity buffers, unfinished writes, and end offset.
- `fillStripe`, `readBlocks`, and `computeParityBlock` materialize full stripes for XOR/EC parity writes.
- `processStatus` validates chunk ids, maps write ids to operation ids, updates file length, and erases completed journal blocks.

## Control Flow
Initialization walks master-provided locations, groups multiple chunkservers for the same part into one executor chain, computes least-common-multiple combined stripe size, opens connections, and queues `WRITE_INIT` packets under pending operation id `0`.

New write-cache blocks are converted from writable to read-only before journal insertion. Compatible blocks with the same chunk/range/stripe expand the last operation; otherwise a new operation is created. Starting operations preserves order, holds back the last partial stripe when more data is expected, and avoids overlapping pending operations to prevent parity reads from seeing stale data. `startOperation` fills missing stripe elements by reading old data, computes parity blocks for parity executors, allocates write ids for each data packet, and records the operation as pending.

`processOperations` builds a `pollfd` list for a wakeup pipe and executor sockets. It drains wakeup bytes, sends queued data on writable sockets, receives statuses on readable sockets, raises on poll/hangup/error/timeout, and delegates status completion. Finished non-init operations update locator file length and erase their journal blocks.

## State And Persistence
State is per `ChunkWriter`: connector/stat references, active locator, id counter, accept/flush mode, combined stripe size, optional data-chain fd, executor map keyed by socket fd, journal list, new operation list, write-id map, and pending operation map. Persistent effects are remote chunkserver writes and master-visible file length update later sent by `WriteChunkLocator::unlockChunk`.

## Dependencies And Integration Points
It integrates with `WriteChunkLocator`, `WriteExecutor`, `ChunkConnector`, `ChunkserverStats`, read planners/executors for read-modify-write, XOR/Reed-Solomon helpers, socket polling, request logging, and mount read-data configuration.

## Risks
- Correctness depends on operation ordering and collision detection; regressions can corrupt parity for partial-stripe writes.
- `finish` exits when timeout expires even if executors remain; callers need to treat remaining connections/pending packets carefully.
- `processOperations` throws recoverable exceptions on several transport/status failures, so higher layers must retry or abort while preserving journal data via `releaseJournal`.
- `readBlocks` uses read timeout settings from read path for write parity reads; misconfiguration affects writes.
- Manual fd ownership is split between connector-managed connections and raw `tcpclose` in abort paths.

## Test Signals
Tests should cover full-stripe write batching, partial-stripe read-fill, XOR and EC parity computation, collision blocking, status id mapping, file length update, init/end packet lifecycle, data-chain wakeups, timeout behavior, and journal release after abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_writer.h -->
# sources/distributed-fs/lizardfs/src/mount/chunk_writer.h

## Purpose
`chunk_writer.h` declares `ChunkWriter`, the stateful engine that turns write-cache blocks for one chunk into network write operations.

## Important APIs, Types, And Functions
- Constructor binds `ChunkserverStats`, `ChunkConnector`, and optional `dataChainFd`.
- `init`, `addOperation`, `startNewOperations`, `processOperations`, `finish`, and `abortOperations` form the write lifecycle.
- `startFlushMode` stops accepting new operations and allows all queued work to flush.
- `dropNewOperations` discards work not yet started and stops accepting more.
- `releaseJournal` transfers remaining journal blocks back to the caller after abort/defer.
- Nested `Operation` groups journal positions, parity buffers, unfinished write count, and file end offset.

## Control Flow
Callers initialize against a locked chunk locator, add write blocks, periodically start/process operations, enter flush mode, wait for pending operations to finish, then call `finish`. On retry paths, callers can abort and recover the journal.

## State And Persistence
The header exposes transient write state members. Persistent write completion is indirect through chunkservers and the associated locator’s final file length.

## Dependencies And Integration Points
It depends on chunk part/address structures, `WriteExecutor`, `WriteChunkLocator`, and `WriteCacheBlock`. It is used by the mount write cache/workers.

## Risks
- The class is noncopyable and appears not thread-safe internally; external worker serialization is required.
- `locator_` is a raw pointer that must outlive the writer lifecycle.
- `allocateId` can wrap around after `uint32_t` overflow and collide with outstanding ids in extreme long-lived cases.

## Test Signals
Header behavior is validated through writer unit/integration tests for lifecycle order, noncopyability, journal release, and operation grouping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/chunk_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/mount/client/CMakeLists.txt

## Purpose
This CMake file builds and installs the LizardFS client libraries: C API, C++ wrapper, shared dynamic-mount shim, and headers.

## Important APIs, Types, And Functions
- `shared_add_library(lizardfs-client client.cc lizardfs_c_api.cc client_error_code.cc)` builds the C API library.
- `shared_add_library(lizardfs-client-cpp client.cc client_error_code.cc)` builds the C++ wrapper without C API implementation.
- `add_library(lizardfs-client_shared SHARED ...)` creates an installed shared object named `liblizardfs-client`.
- `add_library(lizardfsmount_shared SHARED ${MOUNT_SOURCES} lizard_client_c_linkage.cc)` creates the dynamic shim loaded by `Client`.
- `install(FILES lizardfs_c_api.h ... lizardfs_error_codes.h ...)` installs public headers.

## Control Flow
The script collects client sources, defines shared/PIC target variants, links against `mount` or `mount_pic`, links C dynamic-loader libraries where needed, and installs targets to library/include subdirectories.

## State And Persistence
It affects build/install artifacts only. The produced `lizardfsmount_shared` is loaded at runtime by `client.cc`.

## Dependencies And Integration Points
It relies on parent `MOUNT_SOURCES`, project shared-library macros, `${CMAKE_DL_LIBS}`, `mount_pic`, and install directory variables.

## Risks
- `lizardfsmount_shared` embeds all mount sources plus linkage wrappers; ABI drift between exported wrappers and `client.cc` dlsym list will fail at runtime.
- Multiple targets compile overlapping source files, so compile definitions and PIC settings must remain consistent.

## Test Signals
Build tests should verify all targets build with `ENABLE_CLIENT_LIB`, installed headers compile from C and C++, and `Client::linkLibrary` can load `liblizardfsmount_shared.so`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/client.cc -->
# sources/distributed-fs/lizardfs/src/mount/client/client.cc

## Purpose
`client.cc` implements the C++ object wrapper `lizardfs::Client` around the singleton-style `LizardClient` namespace. It dynamically loads a mount shim, resolves unmangled function exports, converts integer status codes to `std::error_code`, and manages open file/directory handles.

## Important APIs, Types, And Functions
- `Client::linkLibrary()` loads `liblizardfsmount_shared.so`; for multiple instances it copies the shared object to a temporary file so each instance gets isolated singleton state.
- Constructors initialize `FsInitParams` and call `init`.
- Destructor releases tracked fileinfos, terminates the filesystem, closes the dynamic library, and decrements instance count.
- `init` resolves all `lizardfs_*` symbols via `dlsym` and calls `lizardfs_fs_init`.
- Methods wrap metadata, directory, file IO, xattr, ACL, chunk info, chunkserver info, and lock operations in throwing and `std::error_code` forms.
- `toXattrList` parses null-separated xattr names into strings.

## Control Flow
Every public throwing overload creates a local `std::error_code`, calls the corresponding nonthrowing overload, and throws `std::system_error` on failure. Nonthrowing overloads call resolved C-linkage function pointers, assign `ec = make_error_code(ret)`, and return output values. `open`/`opendir` allocate `FileInfo` and push it into an intrusive list under mutex; `release`/`releasedir` remove and delete. `read` dispatches to special-inode or regular read wrappers. `setlk` is split into send, optional interrupt-registration callback, and blocking receive.

## State And Persistence
Per instance state includes a dynamic library handle, resolved function pointers, an intrusive list of live `FileInfo` objects, a mutex, and an atomic opendir session id. Static `instance_count_` controls first-instance direct loading versus temp-copy loading. Persistent filesystem effects are performed by the underlying LizardClient/mount functions.

## Dependencies And Integration Points
It depends on `lizard_client_c_linkage.h`, `client_error_code.h`, `richacl_converter`, POSIX `dlopen/dlsym/dlclose`, and the installed `LIB_PATH`. It is the backend for `lizardfs_c_api.cc` and for C++ consumers of `lizardfs-client-cpp`.

## Risks
- Several throwing overloads appear to recurse into themselves instead of calling the `std::error_code` overload: `readlink(Context&,Inode)`, `fsync(Context&,FileInfo*)`, and `setacl(Context&,Inode,const RichACL&)`. These would cause infinite recursion/stack overflow when used.
- `mkdir(Context&,...)` throwing overload calls the nonthrowing overload but does not check `ec` and throw.
- `linkLibrary` copies the shared object with stream insertion without checking source/destination open/write errors.
- Temporary library copy uses `/tmp` and unlinks after `dlopen`; failures before close/unlink can leak fd/path briefly.
- Destructor releases all fileinfos while invoking methods that also lock/modify the list; correctness depends on list operations and no external concurrent use during destruction.

## Test Signals
Tests should instantiate multiple clients, verify independent dynamic state, assert every `dlsym` is required, exercise throwing vs nonthrowing overloads, detect recursion bugs, and verify fileinfo tracking across open/release/opendir/releasedir/destructor. ABI tests should load the built `lizardfsmount_shared`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/client.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/client.h -->
# sources/distributed-fs/lizardfs/src/mount/client/client.h

## Purpose
`client.h` declares the public C++ `lizardfs::Client` wrapper API and its dynamic linkage state.

## Important APIs, Types, And Functions
- Type aliases expose `LizardClient` concepts: `FsInitParams`, `Inode`, `JobId`, `Context`, `EntryParam`, `ReadResult`, directory/trash/reserved replies, and `FlockWrapper`.
- `Stats` mirrors statfs fields.
- `FileInfo` extends `LizardClient::FileInfo` with inode/opendir session id and an intrusive-list hook.
- Public methods cover group updates, lookup/create/link/symlink/mkdir/unlink/rmdir/rename, open/read/write/flush/fsync/release, directory ops, trash/reserved reads, attributes, snapshots, goals, statfs, xattrs, rich ACLs, chunk/chunkserver info, and POSIX locks.
- Protected typedefs store function-pointer types for every dynamic C-linkage symbol.

## Control Flow
The class presents paired overloads for most operations: throwing and `std::error_code&`. Initialization loads symbols, stores them in member function pointers, and calls the dynamic filesystem init.

## State And Persistence
Members include all resolved function pointers, `dl_handle_`, an intrusive `FileInfoList`, a mutex, and `nextOpendirSessionID_`. `instance_count_` coordinates library loading across instances. Filesystem state is external.

## Dependencies And Integration Points
It depends on the C-linkage export header, RichACL, Boost intrusive lists, and dynamic library path `LIB_PATH "/liblizardfsmount_shared.so"`. C API implementation uses this class as the high-level client object.

## Risks
- The API exposes raw `FileInfo*`; ownership is manual and must pair with `release`/`releasedir`.
- Function pointer members must match `lizard_client_c_linkage.h` exactly or runtime calls become undefined.
- Thread-safety is limited to fileinfo list modifications; underlying singleton state may not be safe for arbitrary concurrent operations.

## Test Signals
Tests should compile consumers of the header, validate C++ method overload resolution, and exercise handle ownership and dynamic symbol coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/client_error_code.cc -->
# sources/distributed-fs/lizardfs/src/mount/client/client_error_code.cc

## Purpose
`client_error_code.cc` implements the LizardFS `std::error_category`, including human-readable messages and equivalence with standard `std::errc` conditions.

## Important APIs, Types, And Functions
- `lizardfs_error_category::instance_` is the singleton category instance.
- `message(int)` delegates to `lizardfs_error_string`.
- `equivalent(int,const std::error_condition&)` maps LizardFS error enum values to standard conditions.
- `equivalent(const std::error_code&,int)` maps standard codes back to LizardFS conditions.

## Control Flow
Both equivalence functions first check exact/default equivalence, then switch over selected `lizardfs::error` values and compare with `std::errc` codes or conditions. Platform-specific mappings are used for `attribute_not_found` and `no_message` on Apple/FreeBSD versus other systems.

## State And Persistence
Only the static error category singleton is stored. No filesystem state is changed.

## Dependencies And Integration Points
It depends on `common/mfserr.h` for `lizardfs_error_string` and on `client_error_code.h` enum values. `client.cc` and C API wrappers use `make_error_code`.

## Risks
- Only selected LizardFS errors are mapped to standard conditions; callers comparing unmapped errors to `std::errc` will not match.
- Enum spelling mistakes in the header (`incorrecet_password`, `wating_for_completion`) become stable API names.

## Test Signals
Unit tests should check message text for representative codes and equivalence in both directions for each mapped `std::errc`, including platform-conditional `no_message` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/client_error_code.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/client_error_code.h -->
# sources/distributed-fs/lizardfs/src/mount/client/client_error_code.h

## Purpose
`client_error_code.h` declares the LizardFS C++ error enum and integrates it with `<system_error>`.

## Important APIs, Types, And Functions
- `enum class lizardfs::error` enumerates success and LizardFS-specific failures in protocol/status order.
- `detail::lizardfs_error_category` derives from `std::error_category`.
- `make_error_condition(error)`, `make_error_code(error)`, and `make_error_code(int)` construct category-bound condition/code values.
- `std::is_error_code_enum` and `std::is_error_condition_enum` specializations enable implicit system_error integration.

## Control Flow
Consumers convert integer status codes or enum values to `std::error_code` using the inline factories. Equivalence/message behavior is implemented in the `.cc`.

## State And Persistence
No runtime state beyond the category singleton declared in implementation.

## Dependencies And Integration Points
It is included by C++ client code and any external C++ consumer wanting typed LizardFS error handling.

## Risks
- The integer enum order must stay synchronized with common LizardFS error codes; inserting or reordering values can break ABI/behavior.
- Typos in public enumerator names are API-visible and hard to fix without compatibility impact.

## Test Signals
Compile-time tests should validate `std::is_error_code_enum<lizardfs::error>`, and runtime tests should compare integer status conversions against known LizardFS constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/client_error_code.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/iovec_traits.h -->
# sources/distributed-fs/lizardfs/src/mount/client/iovec_traits.h

## Purpose
`iovec_traits.h` provides small inline helpers for copying contiguous buffers and other iovec arrays into caller-provided iovec destinations. It also defines a fallback `struct iovec` on Windows-like builds.

## Important APIs, Types, And Functions
- `memcpyIoVec(const iovec*, int, const char*, size_t)` copies a contiguous buffer into an iovec sequence.
- `copyIoVec(const iovec* buf, int bufcnt, const iovec* iov, int iovcnt)` copies from one iovec sequence into another and returns bytes copied.

## Control Flow
Both helpers iterate destination/source segments, copying the minimum available bytes per segment and advancing through zero-length or exhausted entries. Assertions enforce non-null pointers and nonnegative counts.

## State And Persistence
No state or persistence. These are pure memory-copy helpers.

## Dependencies And Integration Points
`lizardfs_c_api.cc` uses `copyIoVec` for `liz_readv`, copying a `ReadCache::Result` converted to iovecs into user buffers. The header uses POSIX `<sys/uio.h>` outside Windows.

## Risks
- `copyIoVec` initializes `iov_base` and `buf_base` from the first entries before checking whether counts are zero; zero counts with invalid pointers can still be problematic despite assertions.
- Parameter names are confusing: `buf` is destination and `iov` is source.
- Assertions disappear in release builds, so invalid pointers/counts become undefined behavior.

## Test Signals
Tests should cover multi-segment copies, zero-length segments, partial destination capacity, zero requested bytes, and source/destination count edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/iovec_traits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/lizard_client_c_linkage.cc -->
# sources/distributed-fs/lizardfs/src/mount/client/lizard_client_c_linkage.cc

## Purpose
`lizard_client_c_linkage.cc` exposes unmangled wrapper functions around the singleton `LizardClient` namespace so `client.cc` can load them with `dlsym`. It catches exceptions and returns LizardFS integer status codes or status/value pairs.

## Important APIs, Types, And Functions
- `lizardfs_fs_init`/`lizardfs_fs_term` start and stop `LizardClient`.
- Metadata wrappers include lookup, mknod, link, symlink, mkdir, rmdir, unlink, undel, rename, getattr, setattr, goals, snapshots, xattrs, and statfs.
- IO wrappers include open, read, read special inode, write, release, flush, fsync, opendir/readdir/releasedir.
- Cluster wrappers include chunks info and chunkserver list.
- Lock wrappers include getlk, setlk send/recv, and interrupt.

## Control Flow
Each wrapper calls the corresponding `LizardClient` function in a `try` block. `RequestException` is converted to its embedded LizardFS error code; other exceptions become `LIZARDFS_ERROR_IO` except termination, which suppresses all exceptions. Pair-returning functions return `{status, default_value}` on failure. `lizardfs_readdir` updates the readdir session with the last returned inode and `releasedir` drops that session.

## State And Persistence
The file does not own state directly but operates on global/singleton `LizardClient` state. It mutates filesystem metadata/data through underlying calls and updates readdir session state.

## Dependencies And Integration Points
It depends on `mount/lizard_client.h`, lock protocol types, and `lizard_client_c_linkage.h`. It is compiled into `lizardfsmount_shared`, which `Client` dynamically loads.

## Risks
- C-linkage functions return C++ types such as `std::pair`, `std::vector`, and `std::string` references; this is intended for same-toolchain dynamic loading, not a stable C ABI.
- Catch-all conversion to IO can obscure programming errors.
- `Context` is passed by value for some wrappers and by reference for others; consistency matters for context mutations.
- ABI mismatch between this file and `client.h` function pointer typedefs will fail at runtime or worse.

## Test Signals
Tests should verify every declared symbol is exported and loadable, each wrapper maps `RequestException` to status, generic exceptions to IO, readdir session updates/drop calls, and lock send/recv sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/lizard_client_c_linkage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/lizard_client_c_linkage.h -->
# sources/distributed-fs/lizardfs/src/mount/client/lizard_client_c_linkage.h

## Purpose
`lizard_client_c_linkage.h` declares unmangled functions exported by `lizardfsmount_shared` for dynamic lookup by the C++ `Client` wrapper.

## Important APIs, Types, And Functions
The header declares `extern "C"` wrappers for filesystem init/term, metadata operations, directory operations, file IO, special inode reads, xattrs, goals, snapshots, statfs, chunks/chunkservers, and POSIX lock operations. Return conventions are integer LizardFS status codes or `std::pair<status,value>` for value-returning calls.

## Control Flow
The header is a dynamic ABI contract: `client.cc` uses `decltype(&lizardfs_*)` typedefs and `dlsym` names that must match these declarations exactly.

## State And Persistence
No state is declared. The functions operate on underlying singleton `LizardClient` state.

## Dependencies And Integration Points
It includes `mount/lizard_client.h` and `protocol/lock_info.h`. It intentionally bridges C++ singleton code and dynamic library instance isolation.

## Risks
- Despite `extern "C"`, many signatures use C++ standard-library types, so this is not a portable C ABI.
- The comment warns implementations should not throw; any uncaught exception crossing the dynamic boundary would be dangerous.
- Header and implementation drift affects runtime symbol calls.

## Test Signals
ABI tests should compile both producer and consumer, run `dlsym` for every symbol, and exercise representative pair-returning functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/lizard_client_c_linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/lizardfs_c_api.cc -->
# sources/distributed-fs/lizardfs/src/mount/client/lizardfs_c_api.cc

## Purpose
`lizardfs_c_api.cc` implements the public C API declared in `lizardfs_c_api.h` on top of the C++ `lizardfs::Client`. It converts opaque C handles to C++ objects, provides POSIX-style return values, manages caller-visible allocation layouts, and stores a thread-local last LizardFS error.

## Important APIs, Types, And Functions
- `liz_set_default_init_params` initializes `liz_init_params_t` with `LizardClient::FsInitParams` defaults and enum compatibility checks.
- `gLastErrorCode` backs `liz_last_err`.
- Conversion helpers `to_entry`, `to_attr_reply`, and `to_stat` map C++ reply structs to C structs.
- Context/instance lifecycle: `liz_create_context`, `liz_create_user_context`, `liz_destroy_context`, `liz_init`, `liz_init_with_params`, `liz_destroy`.
- File/directory operations: `liz_open`, `liz_read`, `liz_readv`, `liz_write`, `liz_release`, `liz_flush`, `liz_opendir`, `liz_readdir`, `liz_destroy_direntry`, `liz_releasedir`.
- Metadata operations: lookup, mknod, link, symlink, mkdir, rmdir, unlink, undel, rename, getattr, setattr, readlink, reserved/trash listing, goals, snapshots, statfs.
- Xattr/ACL operations: set/get/list/remove xattr, ACL create/destroy/print/add/get/apply/set/get.
- Cluster/lock operations: chunks info, chunkservers info, set/get/interrupt locks.

## Control Flow
Most functions cast opaque pointers to `Client`, `Context`, or `FileInfo`, call the matching `Client` nonthrowing overload, write `gLastErrorCode = ec.value()`, and return `0`/`-1`, byte counts, or pointers according to C API convention. Initialization translates passwords to MD5 digests and copies all compatible init parameters into `FsInitParams`.

Returned directory/named-inode/chunk/chunkserver arrays use packed allocation patterns: names or part tables are allocated in one buffer attached to the first returned element, then freed by paired destroy functions. `liz_readv` converts `ReadCache::Result` into small-vector iovecs and copies into the caller’s iovec.

## State And Persistence
The file owns no global client state except thread-local `gLastErrorCode`. Opaque `liz_t` points to a heap `Client`; contexts and ACLs are heap-allocated C++ objects. Persistent filesystem effects occur through the client. Some returned result buffers allocate memory that the caller must release through matching C API destroy functions.

## Dependencies And Integration Points
It depends on the public C header, common error codes, MD5 helpers, `small_vector`, `iovec_traits`, and `client.h`. It is compiled into `lizardfs-client`.

## Risks
- `liz_error_conv` and `liz_error_string` call themselves recursively because their names shadow common helpers; calls will recurse indefinitely unless qualified or renamed.
- Many API functions rely on `assert` for null pointer validation; release builds can crash or corrupt memory on invalid arguments.
- `liz_get_acl_entry` checks `(size_t)n > richacl.size()` but should reject `n == size()`; current code can advance to end and dereference.
- `liz_readlink` copies at most `size` bytes but returns the full link length without reporting truncation.
- Packed allocation destroy functions free memory through the first element; callers must not pass shifted pointers.
- `liz_get_chunkservers_info` does not set `chunks_count` even though the public struct contains it.

## Test Signals
Tests should cover lifecycle, last-error isolation per thread, parameter default parity, password/md5 handling, every allocation/destroy pair, short-buffer behavior, null/zero-size validation, readv copying, ACL boundary checks, chunks/chunkservers ownership, lock interrupt callback flow, and recursion hazards in error helper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/lizardfs_c_api.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/lizardfs_c_api.h -->
# sources/distributed-fs/lizardfs/src/mount/client/lizardfs_c_api.h

## Purpose
`lizardfs_c_api.h` declares the public C interface for applications using LizardFS client functionality without the FUSE mount process. It defines configuration, opaque handles, data structs, constants, and lifecycle/metadata/IO/ACL/chunk/lock functions.

## Important APIs, Types, And Functions
- `liz_init_params_t` exposes connection, authentication, read/write cache, timeout, directory/attribute/ACL cache, and IO limit settings.
- Opaque handles: `liz_t`, `liz_fileinfo_t`, `liz_context_t`, and `liz_acl_t`.
- Public structs include entries, attributes, direntries, named inode entries, xattr replies, statfs, chunk part/chunk info, chunkserver info, ACL ACEs, and lock interrupt data.
- Constants define special inodes, set-attribute masks, xattr modes, rich ACL flags/masks/special IDs, max goal/readlink sizes, and sugid clear modes.
- Functions cover context lifecycle, init/destroy, group updates, lookup/create/link/symlink/open/read/readv/write/release/flush/fsync/getattr/setattr, directory listing, trash/reserved lists, mkdir/rmdir/unlink/undel/rename, snapshots, goals, statfs, xattrs, ACLs, chunks/chunkservers, and locks.

## Control Flow
The API follows C/POSIX conventions: pointers are returned for created objects or open handles; most operations return `0` on success and `-1` on failure; byte operations return byte counts or `-1`; `liz_last_err` exposes the last LizardFS error for the calling thread. Several functions document required paired cleanup calls for allocated result buffers.

## State And Persistence
The header defines no implementation state. It documents opaque objects whose implementation owns connections, contexts, file handles, and ACL memory. Operations persist metadata/data changes through the LizardFS cluster.

## Dependencies And Integration Points
It includes POSIX headers for file modes, stat, and iovec. It is installed as the public header for `lizardfs-client` along with `lizardfs_error_codes.h`.

## Risks
- Some ACL helper macros appear inconsistent: `LIZ_ACL_POSIX_MODE_EXECUTE` uses `EXECUTE`, and `LIZ_ACL_POSIX_MODE_ALL` references `LIZ_POSIX_MODE_EXEC`, which are not defined in this header.
- The C API requires strict ownership discipline for buffers allocated by read directory, named inode, chunk, chunkserver, and ACL calls.
- Struct field sizes and enum values are ABI-sensitive.
- Comments mention parameters such as ACL `type` or setgoal `job_id` that are not present in the actual signatures, indicating documentation drift.

## Test Signals
Public ABI tests should compile C and C++ consumers, verify default init setup, exercise each cleanup contract under ASan/Valgrind, check macro availability, and validate struct layout compatibility across supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client/lizardfs_c_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client_common.h -->
# sources/distributed-fs/lizardfs/src/mount/client_common.h

## Purpose
`client_common.h` declares shared mount-client helpers and operation identifiers used by the LizardFS mount client implementation.

## Important APIs, Types, And Functions
- Anonymous enum assigns operation ids (`OP_STATFS` through `OP_FLOCK`, plus `STATNODES`) used for stats counters.
- `MagicFile` stores mutable pseudo-file value state with a mutex and read/write flags.
- `PthreadMutexWrapper` is an RAII wrapper around `pthread_mutex_t` with explicit unlock/relock support.
- `LizardClient::stats_inc`, `attr_to_stat`, and `makeattrstr` are declared utility functions.

## Control Flow
The enum provides indexes for statistics. `PthreadMutexWrapper` locks in its constructor, unlocks in its destructor if still locked, and allows manual unlock/lock with assertions. `MagicFile` is a small synchronized state container for special files.

## State And Persistence
No globals are defined here. `MagicFile` instances hold transient in-memory data. Attribute conversion helpers operate on metadata replies.

## Dependencies And Integration Points
It includes common attributes and `mount/lizard_client.h`. Operation ids are used by mount request handling and stats reporting.

## Risks
- Enum ordering is likely externally meaningful for stats arrays; inserting values can break reporting.
- `PthreadMutexWrapper` is noncopy-safe by convention only; no deleted copy constructor is declared.
- Assertions guard misuse but release builds may allow incorrect lock/unlock sequencing.

## Test Signals
Tests should verify RAII unlock behavior, explicit unlock/relock assertions in debug, operation count matching stats arrays, and attribute conversion output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/client_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/direntry_cache.h -->
# sources/distributed-fs/lizardfs/src/mount/direntry_cache.h

## Purpose
`direntry_cache.h` implements a credential-aware directory entry cache for the mount client. It supports lookup by parent/name, parent/index, and inode, plus FIFO expiration/removal.

## Important APIs, Types, And Functions
- `DirEntryCache::DirEntry` stores uid/gid, parent inode, inode, directory index, next index, timestamp, name, attributes, and Boost intrusive hooks.
- Intrusive containers: `LookupSet`, `IndexSet`, `InodeMultiset`, and `FifoList`.
- `lookup(ctx,inode,attr)` and `lookup(ctx,parent,name,inode,attr)` are thread-safe read-lock lookups.
- `insert`, `insertSequence`, and `overwriteEntry` add or update cache entries.
- `invalidate`, `lockAndInvalidateInode`, `lockAndInvalidateParent`, `removeExpired`, `removeOldest`, and `clear` remove entries.
- `updateTime` refreshes internal microsecond time from `Timer`.

## Control Flow
Insertions reject stale data (`timestamp + timeout_ <= current_time_`), remove a bounded number of expired FIFO entries, erase conflicting lookup/index entries, and add new intrusive entries. `insertSequence` updates index-order entries from directory listing batches, resolving name/index collisions and overwriting existing entries in-place when possible. Lookups take a shared lock, update time, find by inode or parent/name, reject expired entries and inode `0`, and copy attributes out.

Invalidation by directory index follows the linked `next_index` chain from a starting index. Parent/inode invalidations take a unique lock and erase matching entries. `erase` removes an entry from all four intrusive containers before deleting it.

## State And Persistence
The cache owns heap-allocated `DirEntry` objects referenced by multiple intrusive containers. `current_time_` is atomic, `timeout_` is configurable, and `rwlock_` protects thread-safe operations where documented. The cache is purely transient and derived from master directory replies.

## Dependencies And Integration Points
It depends on `Attributes`, shared mutex utilities, `Timer`, `LizardClient::Context`, `DirectoryEntry`, and Boost intrusive containers. Mount readdir/lookup/getattr paths can use it to avoid master round trips.

## Risks
- Only explicitly marked methods are thread-safe; raw `find`, `insert`, `insertSequence`, and some removal helpers require external locking discipline.
- `setTimeout` is not synchronized.
- `insert` takes `const std::string name` by value and `addEntry` copies several values; performance is acceptable but not zero-copy.
- `lookup(ctx,inode)` searches multiset by inode then uid/gid but does not include parent/name, so multiple credential-matching aliases return the first.
- Inconsistency logging after `addEntry` detects but does not repair index divergence.

## Test Signals
Existing unit tests cover ordering, overwrite, repetitions, and random-order updates. Additional tests should cover expiration, invalidation chains, credential isolation, inode lookup with multiple names, concurrent lookup under write invalidation, and stale timestamp rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/direntry_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/direntry_cache_unittest.cc -->
# sources/distributed-fs/lizardfs/src/mount/direntry_cache_unittest.cc

## Purpose
`direntry_cache_unittest.cc` contains GoogleTest coverage for `DirEntryCache` ordering and update behavior.

## Important APIs, Types, And Functions
- `DirEntryCacheIntrospect` derives from `DirEntryCache` and exposes begin/end iterators for lookup, index, and inode containers.
- `TEST(DirEntryCache, Basic)` verifies insertion, overwrite, credential separation, index ordering, lookup ordering, and inode multiset lookup.
- `TEST(DirEntryCache, Repetitions)` exercises repeated insertion of the same name/index followed by oldest removal.
- `TEST(DirEntryCache, RandomOrder)` verifies updates when readdir entries arrive in nonsequential index/name order.

## Control Flow
Tests create dummy `Attributes`, insert vectors of `DirectoryEntry` under specific contexts and parent inodes, then compare intrusive-container traversal against expected tuples. `Basic` also checks that inode lookup returns entries with expected attribute bytes.

## State And Persistence
All state is in-memory test cache state. No filesystem or persistent resources are used.

## Dependencies And Integration Points
It depends on GoogleTest, `mount/direntry_cache.h`, `LizardClient::Context`, and `DirectoryEntry` constructors.

## Risks
- Tests do not cover expiration, locking, invalidation, stale inserts, or parent/inode invalidation paths.
- `Repetitions` has no assertions beyond not crashing.
- No tests exercise credential-specific lookup misses.

## Test Signals
These tests are strong signals for intrusive set ordering and overwrite correctness. Coverage should be extended around timeout and invalidation behavior for confidence in cache consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/direntry_cache_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/exports.h -->
# sources/distributed-fs/lizardfs/src/mount/exports.h

## Purpose
`exports.h` exposes a single mutable process-local flag controlling whether non-root users may use a filesystem mounted in meta mode.

## Important APIs, Types, And Functions
- `inline bool& nonRootAllowedToUseMeta()` returns a reference to a function-local static bool.

## Control Flow
Callers read or assign through the returned reference. The static defaults to `false`.

## State And Persistence
The function-local static bool is process-local runtime state. It is not persisted.

## Dependencies And Integration Points
It includes `common/platform.h`. Mount authorization code can use this flag to gate meta-mode access for non-root users.

## Risks
- Returning a mutable global reference allows any includer to change policy without central auditing.
- Thread-safety is limited to C++ static initialization; reads/writes to the bool are not synchronized.

## Test Signals
Tests should verify default false value and policy behavior in code that consults the flag. Multi-threaded mutation should be avoided or synchronized by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/exports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/mount/fuse/CMakeLists.txt

## Purpose
This CMake file builds FUSE-based mount executables for FUSE 2 and FUSE 3 when the corresponding libraries are found.

## Important APIs, Types, And Functions
- `collect_sources(MOUNT_FUSE)` gathers FUSE mount sources.
- `add_executable(mfsmount ...)` builds the FUSE 2 executable with `FUSE_USE_VERSION=26`.
- `add_executable(mfsmount3 ...)` builds the FUSE 3 executable with `FUSE_USE_VERSION=30` and `CFGNAME=mfsmount`.
- Each target links `mount`, `mfscommon`, and the relevant FUSE library and installs to `${BIN_SUBDIR}`.

## Control Flow
The build enters current include scope, collects sources, conditionally creates/install `mfsmount` if `FUSE_FOUND`, and conditionally creates/install `mfsmount3` if `FUSE3_FOUND`.

## State And Persistence
Build artifacts only; no runtime state.

## Dependencies And Integration Points
It depends on parent-provided `${MOUNT_FUSE_MAIN}`, `${MOUNT_FUSE_SOURCES}`, FUSE discovery variables, and install directory variables.

## Risks
- Compile definitions differ between FUSE 2 and 3; shared source must remain compatible with both.
- If both FUSE versions are found, both executables are installed and must not conflict in config handling.

## Test Signals
CI should configure with FUSE 2 only, FUSE 3 only, both, and neither, verifying target creation and compile definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/daemonize.cc -->
# sources/distributed-fs/lizardfs/src/mount/fuse/daemonize.cc

## Purpose
`daemonize.cc` implements a small fork-and-wait helper for mount startup. The child runs a supplied function and reports its startup status to the parent through a pipe.

## Important APIs, Types, And Functions
- Static `gWaiter[2]` stores pipe fds.
- `daemonize_return_status(int status)` writes a status to the child pipe endpoint and closes it.
- `daemonize_and_wait(std::function<int()> run_function)` creates the pipe, forks, waits in the parent for an int status, and runs the function in the child.

## Control Flow
`daemonize_and_wait` initializes fds, creates a pipe, forks, and handles errors by printing to stderr and returning `1`. The parent closes the write end and reads an int; short read means failure status `1`. The child closes the read end, executes `run_function`, reports the returned status via `daemonize_return_status`, and returns it.

## State And Persistence
State is process-global pipe fd array. There is no persistence. After fork, parent and child have separate copies of the fds.

## Dependencies And Integration Points
It uses POSIX `pipe`, `fork`, `read`, `write`, and `close`; `daemonize.h` declares the functions. FUSE mount startup code can use it to report whether daemonized startup succeeded.

## Risks
- This helper forks but does not perform full daemonization steps such as `setsid`, cwd change, umask, or stdio redirection; those may happen elsewhere or not at all.
- On fork failure after pipe creation, fds are not closed.
- Parent does not close `gWaiter[0]` after read.
- Global `gWaiter` is not thread-safe or reentrant.

## Test Signals
Tests should cover run function success/failure, explicit early `daemonize_return_status`, short-read failure when child exits without writing, and pipe/fork error handling where injectable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/daemonize.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/daemonize.h -->
# sources/distributed-fs/lizardfs/src/mount/fuse/daemonize.h

## Purpose
`daemonize.h` declares the mount daemon startup status helper functions.

## Important APIs, Types, And Functions
- `void daemonize_return_status(int status)` lets the child report startup result to the waiting parent.
- `int daemonize_and_wait(std::function<int()> run_function)` forks, runs the callback in the child, and returns the reported status in the parent.

## Control Flow
Callers pass the main mount startup function to `daemonize_and_wait`; child code may call `daemonize_return_status` earlier if it wants to unblock the parent before returning.

## State And Persistence
No header state. Implementation uses a process-global pipe.

## Dependencies And Integration Points
It includes `<functional>` and `common/platform.h`, and is used by FUSE mount startup code.

## Risks
- The callback executes after `fork`; it must be safe in the child process context.
- No API surface exposes fd cleanup or cancellation.

## Test Signals
Compile and behavior tests should include a simple callback returning a known status and a callback that reports before returning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/daemonize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/lock_conversion.h -->
# sources/distributed-fs/lizardfs/src/mount/fuse/lock_conversion.h

## Purpose
`lock_conversion.h` converts FUSE/POSIX lock operation representations to and from LizardFS internal `FlockWrapper` flags.

## Important APIs, Types, And Functions
- `flockOpConv(int op)` maps `LOCK_UN`, `LOCK_EX`, `LOCK_SH`, and optional `LOCK_NB` to internal lock flags.
- `posixOpConv(int op, bool sleep)` maps `F_UNLCK`, `F_RDLCK`, and `F_WRLCK` plus nonblocking behavior.
- `flockOpValid(int op)` and `posixOpValid(int op)` validate operation inputs.
- `convertPLock(struct flock&, bool sleep)` builds an internal `FlockWrapper` from POSIX `flock`.
- `convertToFlock(FlockWrapper&)` builds a POSIX `struct flock` from internal flags.

## Control Flow
Conversion functions are inline and branch on lock operation bits or `flock.l_type`. Internal flags include `kUnlock`, `kShared`, `kExclusive`, `kNonblock`, and `kInvalid`. `convertToFlock` asserts on unknown internal lock types.

## State And Persistence
No state or persistence. These are pure conversion helpers.

## Dependencies And Integration Points
It includes `<fcntl.h>`, `<sys/file.h>`, serialization macros, and `protocol/lock_info.h`. It is used by FUSE lock handling to translate kernel lock requests into LizardFS protocol structures.

## Risks
- `flockOpValid` accepts any op with `LOCK_UN`, `LOCK_SH`, or `LOCK_EX` bits set, even with unrelated extra bits; conversion also prioritizes unlock over exclusive/shared if multiple bits are set.
- `convertToFlock` takes non-const `FlockWrapper&` though it does not modify it.
- Assertions catch invalid internal types only in debug builds.

## Test Signals
Tests should cover valid/invalid flock and POSIX combinations, nonblocking flag preservation, multi-bit ambiguous flock inputs, and round-trip conversion for shared/exclusive/unlock locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/lock_conversion.h -->

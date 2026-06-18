# Research: subset-b-000549

Grouped research for BeeGFS common toolkit and tests. Each section preserves the source path and is bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.cpp

**Purpose:** Implements `NodesTk`, the common BeeGFS helper for discovering management nodes and downloading node, target, buddy group, state, and storage pool metadata from management or peer nodes.

**Important APIs/types/functions:** `waitForMgmtHeartbeat`, `downloadNodeInfo`, `downloadNodes`, `downloadTargetMappings`, `downloadMirrorBuddyGroups`, `downloadTargetStates`, `downloadStatesAndBuddyGroups`, `downloadStoragePools`, `moveNodesFromListToStore`, `applyLocalNicListToList`, and `getRetryDelayMS`. The implementation uses BeeGFS messages such as `HeartbeatRequestMsg`, `HeartbeatMsg`, `GetNodesMsg`, `GetTargetMappingsMsg`, `GetMirrorBuddyGroupsMsg`, `GetTargetStatesMsg`, `GetStatesAndBuddyGroupsMsg`, and `GetStoragePoolsMsg`.

**Control flow:** Discovery sends UDP heartbeat requests to the configured management hostname with increasing retry delays and waits for `NodeStoreServers::waitForFirstNode`. `downloadNodeInfo` opens a TCP socket, optionally authenticates the channel, sends a heartbeat request, receives one message via `MessagingTk::recvMsgBuf`, validates heartbeat type and node type, and constructs a `Node` from the response. The download helpers build request/response arguments, optionally suppress connection/retry logs outside debug builds, call `MessagingTk::requestResponse`, then move or release response-owned containers into caller outputs.

**State and persistence behavior:** This file does not persist data itself. It mutates caller-provided output containers, clears moved node vectors after adding handles to a store, and updates connection-pool local NIC capability state on downloaded nodes. Retry timing is transient and based on `Time` plus `Random`.

**Dependencies and integration points:** Integrates the messaging layer, `Node`, `AbstractNodeStore`, `NodeStoreServers`, target state and buddy group maps, storage pool vectors, sockets, IP address resolution, and local NIC capability detection. It is a bootstrap and synchronization utility for daemons and tools that need a current cluster view before connecting to nodes.

**Risks:** Hostname resolution failures can terminate discovery after configured retries. `downloadNodeInfo` treats unexpected message type or node type as a hard null result. The output lists for target states and buddy groups rely on positional 1:1 correspondence. `applyLocalNicListToList` must be called before connection pools are used, or existing connection state may not reflect updated local NICs. Retry delay uses weak randomness and is backoff-oriented, not security-sensitive.

**Test signals:** No direct test file in this subset targets `NodesTk`; coverage would require mocked `MessagingTk`/network endpoints, response message validation, node-type mismatches, retry delay boundaries, and NIC capability propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.h

**Purpose:** Declares the static `NodesTk` cluster-node utility interface used by BeeGFS services and tools for node discovery, management downloads, target state retrieval, and node-store population.

**Important APIs/types/functions:** The public API mirrors the implementation: management heartbeat waiting; single-node heartbeat download; bulk node, target mapping, buddy group, target state, combined state/group, and storage pool downloads; movement of `NodeHandle` vectors into `AbstractNodeStore`; local NIC list application; and retry-delay calculation.

**Control flow:** Callers use the class as a pure namespace; construction is blocked by a private constructor. Most methods are synchronous and either return `bool` plus filled output parameters or return richer pairs/handles for target mappings and node info.

**State and persistence behavior:** The header declares no member state. It defines ownership transfer expectations: `downloadNodes` fills a vector of handles, and `moveNodesFromListToStore` transfers those handles into a node store and clears the vector.

**Dependencies and integration points:** Includes datagram listener, node stores, buddy group and target state structures, and BeeGFS common types. It is a shared contract for management bootstrap code across storage, metadata, client, and administrative components.

**Risks:** Several APIs use parallel lists instead of typed aggregate records, so callers must preserve order. Optional output pointers can be null. `silenceLog` behavior depends on build mode in the implementation. There is no asynchronous or cancellation token model besides `waitForMgmtHeartbeat` accepting a `PThread`.

**Test signals:** Compile-time coverage should ensure all included forward types remain available. Runtime coverage comes from tests or integration scenarios that mock node stores and message responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ObjectReferencer.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ObjectReferencer.h

**Purpose:** Provides a small template wrapper that stores an object reference, tracks a manual reference count, and optionally owns/deletes the referenced object when the wrapper is destroyed.

**Important APIs/types/functions:** `ObjectReferencer(T referencedObject, bool ownReferencedObject=true)`, destructor, `reference`, `release`, `getReferencedObject`, `getRefCount`, `setOwnReferencedObject`, and `getOwnReferencedObject`.

**Control flow:** `reference` increments `refCount` and returns the stored object. `release` decrements and returns the new count; when `DEBUG_REFCOUNT` is enabled it logs and avoids decrementing below zero if release is called at count zero. The destructor deletes `referencedObject` only when ownership is enabled.

**State and persistence behavior:** State is in-memory only: `refCount`, `ownReferencedObject`, and `referencedObject`. There is no mutex or atomic protection, so the counter is not thread-safe.

**Dependencies and integration points:** Uses `LogContext` only for debug underflow diagnostics. The type is intended for pointer-like `T` values because the destructor calls `delete referencedObject`.

**Risks:** Manual reference counting is easy to misuse and is not RAII-safe for borrowed references. Non-pointer `T` will not compile or will behave incorrectly due to `delete`. Unsynchronized increments/decrements can race. Disabling ownership after references exist changes destruction behavior globally.

**Test signals:** No direct tests in this subset. Useful tests would cover ownership on/off, debug underflow behavior, reference/release balance, and single-thread-only assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ObjectReferencer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/OfflineWaitTimeoutTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/OfflineWaitTimeoutTk.h

**Purpose:** Computes the millisecond timeout a caller should wait for target offline state propagation, parameterized over storage or metadata configuration classes.

**Important APIs/types/functions:** Template class `OfflineWaitTimeoutTk<Cfg>` with static `calculate(Cfg* cfg)`. It requires config methods `getSysUpdateTargetStatesSecs()` and `getSysTargetOfflineTimeoutSecs()`.

**Control flow:** If an explicit target-state update interval is configured, the timeout is `(5 + 3 * updateInterval + offlineTimeout) * 1000`. If the update interval is zero/defaulted, the code assumes update interval equals one third of offline timeout and returns `(5 + 2 * offlineTimeout) * 1000`.

**State and persistence behavior:** Stateless pure calculation. It does not cache config values or mutate configuration.

**Dependencies and integration points:** Used where services wait for management/target state convergence. The five-second constant reflects the `InternodeSyncer` loop interval, so this helper is coupled to that background synchronization cadence.

**Risks:** If `InternodeSyncer` timing or default update interval semantics change, this calculation can become stale. It accepts a raw config pointer and does not guard null. It returns `unsigned int` milliseconds, so very large second values can overflow.

**Test signals:** Unit tests should cover explicit update interval, zero/default interval, boundary values, and overflow-sensitive large config values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/OfflineWaitTimeoutTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Pipe.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/Pipe.h

**Purpose:** Wraps a POSIX pipe as two BeeGFS `FileDescriptor` objects with optional thread-safe read and write sides.

**Important APIs/types/functions:** Constructor `Pipe(bool threadsafeReadside, bool threadsafeWriteside)`, destructor, `getReadFD`, `getWriteFD`, and `waitForIncomingData(int timeoutMS)`. Constants define read/write fd indices.

**Control flow:** Construction initializes fd slots to `-1`, calls `pipe`, and wraps both descriptors. Destruction deletes wrappers and closes both raw descriptors. `waitForIncomingData` polls the read side for `POLLIN`, returns false only on timeout, and returns true for readiness or error so callers can read and observe the actual error.

**State and persistence behavior:** Holds process-local file descriptors and wrapper objects only. It does not persist data beyond the kernel pipe buffer.

**Dependencies and integration points:** Depends on `FileDescriptor`, POSIX `pipe`, `poll`, and `close`. It is suitable for intra-process wakeups or producer/consumer coordination where BeeGFS code expects `FileDescriptor`.

**Risks:** The constructor ignores `pipe` failure and still creates wrappers around `-1`, so callers must be careful in low-fd or resource-exhaustion scenarios. Ownership is raw-pointer based. Closing after deleting `FileDescriptor` may double-close if the wrapper also owns the fd; that depends on `FileDescriptor` semantics outside this file.

**Test signals:** No direct tests in this subset. Tests should simulate data readiness, timeout, fd creation failure if possible, and descriptor lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Pipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/PreallocatedFile.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/PreallocatedFile.h

**Purpose:** Provides a template for fixed-size, preallocated on-disk storage of one serializable value with a one-byte validity tag, intended for writes that should not fail for lack of space inside the allocated range.

**Important APIs/types/functions:** `detail::PreallocatedFileDefaultSize<T>` defaults size to `sizeof(T)` for trivial types. `PreallocatedFile<T, Size>` exposes a constructor, `write(const T&)`, and `read() const` returning `boost::optional<T>`.

**Control flow:** Construction opens/creates the file read-write and calls `posix_fallocate` for `Size + 1`. `write` serializes into a stack buffer at offset 1, sets tag byte 1, validates serializer success, and `pwrite`s the full fixed region. `read` `pread`s the full fixed region; tag byte 0 returns `boost::none`, otherwise the remaining bytes are deserialized into `T`.

**State and persistence behavior:** Persists a fixed-size file. Byte 0 is validity state; bytes 1..Size contain serialized object data. Writes are not fsynced, so persistence across power loss depends on caller/fsync policy.

**Dependencies and integration points:** Uses `FDHandle`, BeeGFS `Serializer`/`Deserializer`, `boost::optional`, POSIX `open`, `posix_fallocate`, `pwrite`, and `pread`. Tests in this subset cover allocation and read/write behavior.

**Risks:** The buffer is stack-allocated, so large `Size` can overflow stacks. Serialization larger than `Size` throws. Short reads/writes are treated as system errors using current `errno`, which may not fully describe partial I/O. Network filesystems may violate the preallocation guarantees described in the comments.

**Test signals:** `TestPreallocatedFile.cpp` verifies allocated size/blocks, large allocation failure, successful `uint64_t` write/read, too-small buffer failure, empty-file optional behavior, and truncated-file read failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/PreallocatedFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Random.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/Random.h

**Purpose:** Small per-instance pseudo-random helper based on `rand_r`, used for non-cryptographic jitter and random test data.

**Important APIs/types/functions:** Constructors seed from current `timeval.tv_usec` or explicit seed. `getNextInt` returns a non-negative integer. `getNextInRange(min, max)` returns an inclusive bounded value using modulo reduction.

**Control flow:** Each call invokes `rand_r(&seed)`, normalizes negative results with bitwise complement, and updates the internal seed. Range selection uses `% (max - min + 1)` and adds `min`.

**State and persistence behavior:** Holds one mutable unsigned seed in memory. No persistent state.

**Dependencies and integration points:** Depends on BeeGFS common headers for system includes. Used by retry jitter, string generation, and tests such as `TestBitStore` and `TestRWLock`.

**Risks:** Not cryptographically secure, not statistically ideal due to modulo bias, and not thread-safe if the same instance is shared. `getNextInRange` assumes `max >= min` and can divide by zero or overflow otherwise.

**Test signals:** Indirectly exercised by randomized tests and retry helpers. Deterministic explicit-seed tests would be useful for range boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/RandomReentrant.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/RandomReentrant.h

**Purpose:** Variant of `Random` intended to reduce duplicate seeds under concurrent use without full locking or atomic synchronization.

**Important APIs/types/functions:** Constructors seed from microseconds or explicit seed. `getNextInt` copies and increments a volatile seed, calls `rand_r`, writes back the updated temporary seed, and normalizes negative results. `getNextInRange` mirrors `Random`.

**Control flow:** The seed pre-increment is intended to make simultaneous threads less likely to feed the same seed to `rand_r`. It is best-effort only.

**State and persistence behavior:** Maintains a volatile unsigned seed in memory. No persistence and no synchronization guarantees.

**Dependencies and integration points:** Shared utility for places that want cheap random values from multiple threads without a mutex. Its comment explicitly limits the reentrancy claim.

**Risks:** `volatile` does not make updates atomic or race-free in C++. Concurrent access can still lose updates and is technically data-racy. Like `Random`, it is not cryptographic and range selection is modulo-biased.

**Test signals:** No direct tests. Multithreaded tests should avoid assuming deterministic behavior and should focus on absence of crashes plus valid range bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/RandomReentrant.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/SessionTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/SessionTk.h

**Purpose:** Provides static helpers for BeeGFS storage-session file handle IDs and conversion from BeeGFS access flags to POSIX open flags.

**Important APIs/types/functions:** `fileIDFromHandleID`, `ownerFDFromHandleID`, `generateFileHandleID`, and `sysOpenFlagsFromFhgfsAccessFlags`.

**Control flow:** Handle IDs are encoded as `<ownerFDHex>#<fileID>`. Parsing locates `#`; missing separators return the original handle as file ID or owner fd `0`. Access flag conversion starts with `O_LARGEFILE`, picks read/write mode from BeeGFS flags, and adds direct, sync, and nonblocking flags when requested.

**State and persistence behavior:** Stateless string/flag transformation. The handle ID string is part of session-level protocol/state elsewhere but not persisted here.

**Dependencies and integration points:** Uses `StorageDefinitions` access flag constants, `StringTk` hex conversion, and POSIX open flag constants. Comments note this is not for metadata servers, which should use `EntryInfo`.

**Risks:** Malformed handle IDs degrade silently. If multiple access mode bits are set, read-write wins over write-only. `O_DIRECT` imposes alignment constraints not handled here.

**Test signals:** Useful tests would cover malformed IDs, hex owner parsing, all access flag combinations, and compatibility with session backup/restore logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/SessionTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.cpp

**Purpose:** Implements BeeGFS storage filesystem utilities for directory creation/removal, filesystem statistics, lock/pid files, storage format files, persistent ID/token files, directory enumeration, chunk path layout, recursive deletion, mount lookup, and bounded file reads.

**Important APIs/types/functions:** Implements `initHashPaths`, `createPathOnDisk` path and fd-relative variants, `removePathDirsFromDisk`, `statStoragePath`, `statStoragePathOverride`, basename/dirname helpers, `lockWorkingDirectory`, `createAndLockPIDFile`, format-file creation/loading/updating, `deprecateNodeStringIDFiles`, target/registration/numeric ID file helpers, filtered `readdir`, `readCompleteDir`, chunk path helpers, `removeDirRecursive`, `findLongestMountedPrefix`, `findMountForPath`, `readFile`, and private `readNumFromFile`.

**Control flow:** Directory creation walks path elements and accepts existing directories after stat/fstat validation. Format writing serializes key/value lines through `TempFileTk::storeTmpAndMove`; loading reads via `MapTk`, validates a `version` key, and rejects incompatible versions. ID helpers read existing files first and atomically create missing files with generated IDs or numeric values. Mount lookup parses `/proc/self/mounts`-style streams, unescapes octal path escapes, and tracks the longest prefix match. Recursive deletion uses `nftw` depth-first.

**State and persistence behavior:** Persists and updates important node/storage state: `format.conf`, lock pid files, `targetID`, `targetNumID`, `nodeNumID`, `storagePoolID`, `registrationToken`, deprecated string ID marker files, and optional free space/inode override files. `StorageTk::idCounter` is process-global, initialized from current seconds shifted into the high 32 bits, and used for file/target/registration IDs.

**Dependencies and integration points:** Uses BeeGFS config/file helpers (`ICommonConfig`, `MapTk`, `TempFileTk`, `LockFD`, `FDHandle`, `Path`, `PathInfo`, `HashTk`, `UnitTk`), POSIX/Linux APIs (`mkdir`, `mkdirat`, `statfs`, `flock`, `nftw`, `realpath`, `open`, `lseek`, `read`), and BeeGFS storage constants. It is central to daemon startup, storage target initialization, chunk layout, and capacity reporting.

**Risks:** Many methods throw `InvalidConfigException` on invalid persistent files; callers must distinguish initialization from fatal corruption. `readFile` performs a single `read` after sizing, so short reads are not retried. Recursive deletion removes everything under the supplied path and must receive trusted paths. `findMountForPath` requires `realpath`, so non-existing paths fail despite prefix lookup supporting non-existing raw paths. ID generation assumes clocks do not move backward across restarts and fewer than 2^32 IDs per second.

**Test signals:** `TestLockFD.cpp`, `TestPreallocatedFile.cpp`, and path-related tests indirectly exercise lock files, recursive removal, and file allocation. Dedicated storage tests should cover format version upgrades, ID file mismatch handling, mount escape parsing, Btrfs free-space behavior, override files, and partial I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.h

**Purpose:** Declares the `StorageTk` static utility surface and storage path/format constants used throughout BeeGFS common, metadata, and storage code.

**Important APIs/types/functions:** Defines filenames (`format.conf`, `nodeNumID`, `targetID`, `targetNumID`, `storagePoolID`, session backups), chunk-hash constants, `Mount`, `CloseDirDeleter`, and the public storage helper API. Inline helpers cover path existence, child detection, file ID generation, ID counter reset, dirent type conversion, hash split/merge, chunk path V2/V3 generation, timestamp-to-path mapping, `createFile`, and hash computations.

**Control flow:** Inline chunk path selection depends on `PathInfo::hasOrigFeature`: old format uses two-level hash directories, while newer layout uses UID, timestamp-derived year/month/day-like directories, parent ID, and entry ID. `generateFileID` combines counter, timestamp, and local node ID as hex components. `resetIDCounterToNow` refuses to move the timestamp backward.

**State and persistence behavior:** Declares static `idCounter`, with high 32 bits timestamp and low 32 bits sequence. The constants name persistent files used by `StorageTk.cpp` and daemon startup/shutdown.

**Dependencies and integration points:** Pulls in BeeGFS path, stat, striping, quota/storage pool, locking, hashing, atomics, and POSIX directory types. It is a broad common header, so changes have wide compile impact.

**Risks:** Many inline APIs take strings by value and expose raw POSIX semantics. `pathHasChildren` treats non-directories and missing paths the same as empty. Chunk path logic is compatibility-critical for on-disk layout. `createFile` treats `EEXIST` as success and only optionally tells the caller whether creation happened.

**Test signals:** Existing tests exercise related `Path`, `LockFD`, and `PreallocatedFile` behavior; additional tests should verify chunk path compatibility and hash distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.cpp

**Purpose:** Implements common string trimming, splitting/joining, numeric conversion, formatting, timespan formatting, vector conversion, numeric validation, and random alphanumeric string generation.

**Important APIs/types/functions:** `trim`, `explode`, `explodeEx`, `implode`, `strToInt`, `strToUInt`, `strHexToUInt`, `strOctalToUInt`, `strToInt64`, `strToUInt64`, `strToBool`, integer/hex/double formatters, `timespanToStr`, `uint16VecToStr`, `strToUint16Vec`, `isNumeric`, and `genRandomAlphaNumericString`.

**Control flow:** Split functions walk delimiter positions and skip empty elements; `explodeEx` optionally trims before insertion. Numeric parsing intentionally uses legacy `atoi`, `atoll`, and `sscanf` behavior with weak error reporting. Formatting uses fixed-size stack buffers and `snprintf`/`sprintf`. Random string generation appends characters chosen from digits and ASCII letters via `Random`.

**State and persistence behavior:** Stateless except for caller-provided output containers/strings. No persistence.

**Dependencies and integration points:** Used broadly for config parsing, ID handling, unit conversion, storage path generation, and display. Depends on `Random` for random strings and BeeGFS common typedefs.

**Risks:** Legacy parsers silently accept malformed input or overflow according to C library behavior. `timespanToStr` appears to compute `seconds = seconds % 60` after initializing seconds to zero when minutes are present, so seconds for spans >=60 are always zero. `strToUint16Vec` casts through signed `int16_t` despite returning unsigned vector values. Random generation is not security-grade.

**Test signals:** No direct `StringTk` tests in this subset, but `EntryIdTk`, `UnitTk`, `SessionTk`, and storage helpers depend on its conversions. Dedicated tests should pin legacy parsing semantics before refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.h

**Purpose:** Declares the static `StringTk` API and inline helpers for string/numeric conversion, safe copying, entry-ID timestamp extraction, vector joining, and multi-line joining.

**Important APIs/types/functions:** Public declarations match `StringTk.cpp`. Inline overloads accept `std::string`, `strToDouble`, `strncpyTerminated`, `timeStampFromEntryID`, template `implode`, and template `implodeMultiLine`.

**Control flow:** `timeStampFromEntryID` parses entry IDs of the form `counter-timestamp-node`, returning special IDs unchanged when no separator exists and returning `FhgfsOpsErr_INTERNAL` when only one separator exists. Template `implode` streams vector values with a delimiter. `implodeMultiLine` accumulates delimited elements until a maximum line length would be exceeded.

**State and persistence behavior:** Stateless. The extracted timestamp feeds storage chunk path layout but is not persisted here.

**Dependencies and integration points:** Includes BeeGFS common and storage error definitions. The `STRINGTK_ID_SEPARATOR` contract is shared with storage entry ID generation and chunk path derivation.

**Risks:** Inline parsers inherit weak C conversion behavior. `strncpyTerminated` does nothing when `count == 0`, leaving destination untouched. `implodeMultiLine` uses stream position as element length and can produce leading delimiter behavior after line breaks.

**Test signals:** Entry ID format validation tests in `TestEntryIdTk.cpp` are adjacent but do not directly test `timeStampFromEntryID`; such coverage would be useful for special IDs and malformed IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/SynchronizedCounter.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/SynchronizedCounter.h

**Purpose:** Provides a mutex/condition-protected unsigned counter that threads can wait on until it reaches an exact value.

**Important APIs/types/functions:** Constructor initializes count to zero. `waitForCount`, `timedWaitForCount`, `incCount`, and `resetUnsynced`.

**Control flow:** Wait methods lock the mutex and wait on the condition. `waitForCount` loops until exact equality. `timedWaitForCount` waits once and returns false on timeout or when count remains below the desired value. `incCount` increments and broadcasts.

**State and persistence behavior:** In-memory `count`, `Mutex`, and `Condition` only. No persistence.

**Dependencies and integration points:** Uses BeeGFS threading primitives and `std::lock_guard`. Useful for tests or coordination barriers inside common code.

**Risks:** `resetUnsynced` does not lock or broadcast and is only safe under external synchronization. Exact-equality waits can block forever if `count` jumps past `waitCount`; timed wait partially handles count below but returns true if count is greater. Overflow is not guarded.

**Test signals:** No direct tests. Concurrency tests should cover exact match, overshoot, timeout, broadcast behavior, and safe reset usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/SynchronizedCounter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.cpp

**Purpose:** Implements atomic-ish file replacement by writing content to a temporary file, fsyncing it, renaming it over the final path, and fsyncing the containing directory.

**Important APIs/types/functions:** `TempFileTk::storeTmpAndMove(const std::string&, const void*, size_t)` plus vector and string overloads.

**Control flow:** Builds `filename + ".tmp-XXXXXX"`, opens with `mkstemp`, registers a local cleanup object to unlink the temp file on error, writes until all bytes are written, fsyncs the temp file, renames it to the final filename, disables cleanup, then opens and fsyncs the directory. Directory fsync failure is logged as a warning but returns success.

**State and persistence behavior:** Persists caller-provided bytes to the target path using rename replacement. It avoids leaving partial final files and removes temp files on most error paths.

**Dependencies and integration points:** Used by `StorageTk` for format files and ID/token files. Depends on `FDHandle`, BeeGFS logging and error conversion, `mkstemp`, `write`, `fsync`, `rename`, `dirname`, and directory `open`.

**Risks:** Vector/string overloads use `&contents[0]`, which is undefined for empty vectors/strings in older C++ assumptions even though size is zero. A zero-byte `write` result would spin because only `-1` is treated as failure. File permissions come from `mkstemp` defaults. Directory fsync warning is accepted to avoid rollback complexity.

**Test signals:** Indirectly covered by storage ID/format operations if present. Dedicated tests should cover empty content, rename failure, cleanup of temp files, and crash-consistency expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.h

**Purpose:** Declares the `TempFileTk` namespace API for durable temporary-file replacement writes.

**Important APIs/types/functions:** Three overloads of `storeTmpAndMove`: raw pointer/size, `std::vector<char>`, and `std::string`.

**Control flow:** Header-only behavior is limited to declarations; implementation handles temp file creation, write, fsync, rename, and directory fsync.

**State and persistence behavior:** The API persists bytes to the requested filename via replacement. Return value is `FhgfsOpsErr`, allowing callers to map storage/config write failures.

**Dependencies and integration points:** Includes `StorageErrors`. Used by storage format and ID helpers where partial writes would corrupt startup state.

**Risks:** Callers must pass valid buffers for raw pointer calls and handle non-success return codes. The API does not expose file mode or fsync policy knobs.

**Test signals:** Tests should verify the overloads produce identical file contents and propagate errors from unwritable directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Time.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/Time.cpp

**Purpose:** Implements global clock selection and validation for the monotonic `Time` class.

**Important APIs/types/functions:** Static `Time::clockID`, `Time::testClock`, and `Time::testClockID`.

**Control flow:** `testClock` calls `clock_gettime` using the current default clock. If it fails and the current clock is not the safe clock, it switches to `CLOCK_MONOTONIC` and retries. If the safe clock fails, it throws `TimeException`. `testClockID` simply returns whether `clock_gettime` succeeds for a supplied id.

**State and persistence behavior:** Mutates process-global `Time::clockID` if the preferred coarse monotonic clock is unavailable. No persistence.

**Dependencies and integration points:** Depends on `System::getErrString`, `TimeException`, and POSIX clocks. All `Time` instances use the selected static clock unless derived classes override.

**Risks:** `clockID` is a mutable static without synchronization; clock testing should happen during startup before concurrent use. The unreachable `return false` after throw is defensive only.

**Test signals:** Tests should force or mock invalid clock IDs where possible, verify fallback to safe clock, and confirm `TimeFine` remains independent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Time.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Time.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/Time.h

**Purpose:** Defines BeeGFS's coarse monotonic time wrapper for elapsed-time measurement, timeout arithmetic, ordering, and serialization.

**Important APIs/types/functions:** Constructors for now, zero/uninitialized, existing `timespec`, and copy; comparisons; assignment; `getIsZero`; `addMS`; virtual `setToNow`, `elapsedMS`, `elapsedMicro`; `elapsedSinceMS`, `elapsedSinceMicro`; static clock test methods and `getClockID`; `getTimeSpec`; and template `serialize`.

**Control flow:** Default construction captures `clock_gettime(clockID)`. Elapsed methods construct a fresh `Time` and subtract the stored timestamp. `addMS` normalizes nanoseconds above one second. Serialization writes seconds and nanoseconds as signed 64-bit values through serdes casts.

**State and persistence behavior:** Stores one `timespec` per instance and a static clock ID. Serialized form can persist or transmit monotonic timestamp values, though monotonic times are only meaningful relative to the same boot/session.

**Dependencies and integration points:** Used by retry logic, lock tests, thread timing, and timeout calculations. Depends on BeeGFS serialization helpers and POSIX clocks.

**Risks:** Elapsed calculations return unsigned and can underflow if the compared time is in the future. Microsecond elapsed can overflow for long intervals. Monotonic timestamps should not be interpreted as wall-clock times.

**Test signals:** `TestRWLock` uses `Time` heavily for ordering and runtime assertions. Dedicated tests should cover zero time, add normalization, serialization round trips, and future-time underflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeAbs.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TimeAbs.h

**Purpose:** Provides a wall-clock, epoch-based time wrapper using `gettimeofday`, intended for absolute timestamps rather than monotonic intervals.

**Important APIs/types/functions:** Constructors, comparisons, assignment, `setToNow`, `elapsedSinceMS`, `elapsedSinceMicro`, `elapsedMS`, `getTimeval`, `getTimeS`, `getTimeMS`, and `getTimeMicroSecPart`.

**Control flow:** Instances capture `gettimeofday`. Elapsed methods subtract an earlier `TimeAbs` from the stored timestamp. Accessors expose seconds, milliseconds, and the microsecond field.

**State and persistence behavior:** Holds a `timeval` that represents system wall clock time and may be persisted or displayed as epoch time. It can move backward or forward if system time changes.

**Dependencies and integration points:** Used where BeeGFS needs real timestamps rather than steady durations. Includes only common/POSIX time dependencies.

**Risks:** Wall-clock jumps can make elapsed calculations negative; unsigned returns can underflow. `getTimeval` exposes a mutable pointer to internal state. Microsecond elapsed can overflow for long intervals.

**Test signals:** Tests should cover epoch conversion, assignment/comparison, and behavior when earlier/later order is inverted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeAbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeException.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TimeException.h

**Purpose:** Declares the named exception type used for fatal time/clock initialization failures.

**Important APIs/types/functions:** `DECLARE_NAMEDEXCEPTION(TimeException, "TimeException")`.

**Control flow:** The macro expands to an exception class consistent with BeeGFS named exception conventions. `Time::testClock` throws this type when even the safe monotonic clock fails.

**State and persistence behavior:** No state besides exception payload inherited from the macro-generated type.

**Dependencies and integration points:** Depends on `NamedException` and common headers. It keeps time errors distinguishable from generic config or system exceptions.

**Risks:** Macro-generated behavior is defined elsewhere, so changes to `NamedException` affect this type. It is very small and has no local tests.

**Test signals:** Compile-time use by `Time.cpp`; exception-specific tests should check type and message propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeFine.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TimeFine.h

**Purpose:** Defines a high-resolution monotonic time subclass for sub-millisecond elapsed measurements.

**Important APIs/types/functions:** Constructor, overridden `setToNow`, `elapsedMS`, and `elapsedMicro`.

**Control flow:** Construction calls `Time(false)` to skip base initialization, then captures `CLOCK_MONOTONIC` directly. Elapsed methods compare against a freshly constructed `TimeFine`, bypassing the possibly coarse static `Time::clockID`.

**State and persistence behavior:** Holds inherited `timespec` only. No persistence beyond any caller serialization through base facilities.

**Dependencies and integration points:** Used when coarse monotonic clock precision is insufficient. Shares base comparison and elapsed-since helpers with `Time`.

**Risks:** Always uses `CLOCK_MONOTONIC` and does not test availability itself. Same unsigned underflow/overflow concerns as `Time` apply.

**Test signals:** Tests should compare ordering and elapsed precision against `Time`, and verify override behavior after `Time::clockID` fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeFine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TimeTk.h

**Purpose:** Provides `std::chrono` helper aliases and stream formatting utilities for durations.

**Important APIs/types/functions:** `highest_resolution_steady_clock`, `as_double_duration`, `operator<<` for `std::chrono::duration`, `print_nice_time_t`, `operator<<` for nice printing, and `print_nice_time`.

**Control flow:** The duration stream operator prints count plus a unit derived from the period, with specializations for ns, microseconds, ms, s, min, and hr. `print_nice_time` chooses the largest unit whose duration exceeds three of that unit, falling back to the original duration.

**State and persistence behavior:** Stateless formatting helpers. No persistence.

**Dependencies and integration points:** Integrates standard chrono code with BeeGFS logging/CLI output. `highest_resolution_steady_clock` chooses high-resolution clock only if it is steady, otherwise steady clock.

**Risks:** The microsecond unit literal uses a non-ASCII symbol, which can matter for terminals or logs. Threshold comparisons use `>` rather than `>=`, so exactly three units prints in the next smaller unit. It overloads `operator<<` for standard duration in namespace `TimeTk`, so callers need namespace visibility.

**Test signals:** Formatting tests should cover SI unit specializations, generic ratio formatting, and nice-time thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UInt128.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UInt128.h

**Purpose:** Defines BeeGFS's unsigned 128-bit integer alias plus helpers for construction, splitting, hashing, hex formatting, and stream output.

**Important APIs/types/functions:** `typedef unsigned __int128 uint128_t`, `Uint128Vector`, `uint128::Hash`, `make`, `lower64`, `upper64`, `toHexStr`, and global `operator<<`.

**Control flow:** `make` shifts the most significant word into the upper 64 bits and ORs the lower word. Formatting emits two zero-padded 16-hex-digit halves. Hashing XORs upper and lower halves to avoid standard library implementations that ignore the high half.

**State and persistence behavior:** Stateless value helpers. Hex string output is deterministic and suitable for logs or textual persistence.

**Dependencies and integration points:** Used by serialization byte swapping and any common code needing 128-bit IDs or hashes. Depends on GCC/Clang `unsigned __int128`.

**Risks:** Non-standard integer type may limit portability. XOR hash is simple and can collide for values with swapped/equal halves. Stream operator is global for `uint128_t`.

**Test signals:** Tests should verify make/split round trips, hex padding, hash high-half sensitivity, and byte-swap interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UInt128.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.cpp

**Purpose:** Implements interactive terminal confirmation prompts for yes/no and exact typed confirmation flows.

**Important APIs/types/functions:** `uitk::userYNQuestion` and `uitk::userExactConfirmPrompt`.

**Control flow:** `userYNQuestion` repeatedly prints a prompt with default-sensitive casing, reads one line, uppercases and trims it, returns the default on empty input when provided, and accepts yes/no variants. Without a default, empty input clears `std::cin` and prompts again. `userExactConfirmPrompt` uppercases the required token and input, then loops until exact confirmation or `n`/`no`.

**State and persistence behavior:** No persistent state. It reads from an input stream but writes prompts to `std::cout` directly.

**Dependencies and integration points:** Uses Boost string algorithms and optional defaults. Useful for administrative commands that need destructive-action confirmation while permitting injectable input streams for tests.

**Risks:** Prompt output is always `std::cout`, even when input is a custom stream. Case-insensitive exact confirmation may be less strict than expected. Infinite loops are possible on EOF because stream state is not comprehensively handled.

**Test signals:** Tests should provide `std::istringstream` input for default, yes/no, exact match, abort, whitespace, and EOF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.h

**Purpose:** Declares terminal UI confirmation helpers in namespace `uitk`.

**Important APIs/types/functions:** `userYNQuestion(question, defaultAnswer=boost::none, input=std::cin)` and `userExactConfirmPrompt(question, requiredInput, input=std::cin)`.

**Control flow:** The header exposes synchronous blocking calls. Input stream injection supports tests or scripted prompts, while output behavior is handled in the implementation.

**State and persistence behavior:** Stateless API; no persistence.

**Dependencies and integration points:** Includes Boost optional, iostream, and string. Used by CLI/admin flows requiring user confirmation.

**Risks:** Blocking prompts are inappropriate for daemon/non-interactive contexts. Callers should ensure stdin is interactive or provide a controlled input stream.

**Test signals:** Compile and unit tests can inject streams to avoid real terminal input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.cpp

**Purpose:** Implements binary size conversion, human-readable size/time parsing and formatting, and quota block count conversion.

**Important APIs/types/functions:** Byte conversion functions for KiB through PiB, `byteToMebibyte`, `byteToXbyte`, `mebibyteToXbyte`, `xbyteToByte`, `strHumanToInt64`, `int64ToHumanStr`, `isValidHumanString`, `timeStrHumanToInt64`, `isValidHumanTimeString`, `quotaBlockCountToByte`, and `quotaBlockCountToHumanStr`.

**Control flow:** Size parsing inspects the last character and multiplies the numeric prefix by binary powers for K/M/G/T/P; no suffix falls back to integer parsing. Formatting chooses the largest binary unit that divides evenly. Display conversion repeatedly divides by 1024 and optionally rounds to one decimal. Time parsing supports D/H/M suffixes; validation also accepts S/s even though parser treats seconds by falling back to raw parsing.

**State and persistence behavior:** Stateless conversions. Used for config values, free-space override files, quota display, and user-facing output.

**Dependencies and integration points:** Depends on `StringTk` and quota filesystem type enums. `StorageTk::statStoragePathOverride` uses `strHumanToInt64` for override files.

**Risks:** Uses integer parsing with weak error behavior inherited from `StringTk`. `xbyteToByte` has no EiB branch despite display supporting EiB. `timeStrHumanToInt64("10s")` falls back to parsing `"10s"` as integer, which works with `atoi`-style behavior but is implicit. Multiplication can overflow.

**Test signals:** No direct tests in this subset. Tests should pin suffix parsing, validation/parser mismatch for seconds, quota XFS 512-byte conversion, and round formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.h

**Purpose:** Declares static unit-conversion helpers for binary sizes, human-readable strings, durations, and quota block display.

**Important APIs/types/functions:** Public declarations for all conversion and validation functions plus inline `std::string` overloads for `strHumanToInt64` and `timeStrHumanToInt64`.

**Control flow:** Header is a namespace-like class with private constructor and static functions only. Callers pass output unit strings by pointer for display conversion functions.

**State and persistence behavior:** Stateless declaration. Values converted by this API feed configuration and persistent override behavior elsewhere.

**Dependencies and integration points:** Includes BeeGFS quota definitions. Used by configuration parsing, storage capacity overrides, and CLI output.

**Risks:** Pointer output parameters must be non-null. Header does not document overflow/error behavior; implementation uses permissive numeric parsing.

**Test signals:** Compile-time use is broad; unit tests should include string overloads and null-pointer avoidance by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ZipIterator.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ZipIterator.h

**Purpose:** Provides simple two- and three-container zip iterators/ranges that expose pointers to corresponding elements.

**Important APIs/types/functions:** `triple<F,S,T>`, `ZipIterator<F,S,T>`, two-value specialization `ZipIterator<F,S,void>`, `ZipIterRange`, and `ZipConstIterRange` specializations.

**Control flow:** Increment advances all underlying iterators. Dereference constructs and stores a pair/triple of pointers to current elements and returns it by reference. Range wrappers hold begin and end zip iterators and provide `operator()`, `empty`, and prefix increment for manual loops.

**State and persistence behavior:** Iterators hold underlying iterator copies and a cached pointer tuple/pair. No persistence.

**Dependencies and integration points:** Used where BeeGFS code stores related values in parallel containers, such as target IDs and states. It assumes containers have equal lengths.

**Risks:** Equality requires all underlying iterators to equal their corresponding end; if container lengths differ, loops can dereference past the shortest container. Returned pointers become invalid when containers mutate or the iterator advances. Iterator category is input-only and lacks standard post-increment/const dereference completeness. `triple` defines ordering but relies on an equality operator not declared locally.

**Test signals:** Tests should cover equal and mismatched lengths, const ranges, pointer mutation of underlying containers, and range loop idioms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ZipIterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/hash_library/sha256.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/hash_library/sha256.cpp

**Purpose:** Implements a standalone SHA-256 hash class derived from Stephan Brumme's public code, supporting streaming input and one-shot hashing.

**Important APIs/types/functions:** Constructor, `reset`, private `processBlock`, `add`, `processBuffer`, `getHash` hex and raw-byte variants, and `operator()` overloads for memory blocks and strings. Internal helpers implement rotate, byte swap, and SHA-256 mixing functions.

**Control flow:** `reset` initializes standard SHA-256 constants. `add` fills a 64-byte buffer, processes full blocks, and stores leftover bytes. `processBlock` expands message words to 64 entries and applies the eight rounds of SHA-256 compression. `processBuffer` pads the final block(s) with a 1 bit, zeroes, and 64-bit bit length. `getHash` saves current hash state, processes buffered data, emits bytes or hex, and restores hash words so it can be called without resetting.

**State and persistence behavior:** Maintains streaming state: processed byte count, buffer size, pending buffer, and eight hash words. No persistent storage.

**Dependencies and integration points:** Uses fixed-width integer types and endian detection. It can be used anywhere BeeGFS needs SHA-256 without external crypto library linkage.

**Risks:** This is not a constant-time or hardened crypto abstraction beyond the hash algorithm. `getHash` restores hash words but `processBuffer` mutates the pending buffer, so repeated use after `getHash` should be treated carefully. It casts input to `uint32_t*`, which can raise alignment concerns on strict architectures. Length tracking uses 64-bit bits per SHA-256 limits.

**Test signals:** No direct tests here. Known SHA-256 vectors for empty string, `abc`, long messages, chunked `add`, and repeated `getHash` calls should be present before refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/hash_library/sha256.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/hash_library/sha256.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/hash_library/sha256.h

**Purpose:** Declares the standalone `SHA256` streaming hash API.

**Important APIs/types/functions:** Constants `BlockSize` and `HashBytes`; constructor; one-shot `operator()(const void*, size_t)` and `operator()(const std::string&)`; `add`; `getHash` hex and raw-byte forms; `reset`; private `processBlock` and `processBuffer`; state fields `m_numBytes`, `m_bufferSize`, `m_buffer`, and `m_hash`.

**Control flow:** The API supports either one-shot calls that reset internally or streaming calls that add chunks and retrieve a digest.

**State and persistence behavior:** State is per-object and mutable. No file/network persistence.

**Dependencies and integration points:** Includes fixed-width integer types, with MSVC typedef fallback. It is a lightweight embedded hash implementation.

**Risks:** Object instances are not thread-safe. Callers must understand whether `operator()` resets state. Header comments identify third-party origin; updates should preserve license/disclaimer expectations.

**Test signals:** Compile tests should cover GCC and MSVC typedef paths where supported; behavioral tests should compare against standard SHA-256 vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/hash_library/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.cpp

**Purpose:** Implements a minimal map from file descriptors to `Pollable` objects.

**Important APIs/types/functions:** `add`, `remove`, `removeByFD`, and `getPollableByFD`.

**Control flow:** `add` inserts the pollable under `pollable->getFD()`. `remove` delegates to `removeByFD`. Lookup returns `NULL` when the fd is absent.

**State and persistence behavior:** Mutates an in-memory `std::map<int, Pollable*>`. It does not own pollable objects or persist state.

**Dependencies and integration points:** Used by code that builds `poll`/`select` dispatch tables over objects implementing `Pollable`.

**Risks:** `insert` does not replace an existing fd mapping, so adding a second object with the same fd silently leaves the old mapping. Raw pointers require external lifetime management. No synchronization.

**Test signals:** Tests should cover duplicate fd insertion, removal by pointer/fd, absent lookup, and lifetime expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.h

**Purpose:** Declares the `PollList` fd-to-`Pollable*` container.

**Important APIs/types/functions:** Type aliases `PollMap`, `PollMapIter`, `PollMapVal`; class methods `add`, `remove`, `removeByFD`, `getPollableByFD`, and `getPollMap`.

**Control flow:** The header exposes the underlying map by pointer, allowing callers to iterate or build poll arrays externally.

**State and persistence behavior:** Holds only in-memory raw pointer mappings.

**Dependencies and integration points:** Depends on `Pollable` and BeeGFS common typedefs. Integrates with event loops that need to translate fd readiness back to owning objects.

**Risks:** Exposing `getPollMap` permits unsynchronized external mutation and invariant bypass. No ownership semantics are expressed.

**Test signals:** Compile and unit tests should ensure external map iteration matches add/remove behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/Pollable.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/poll/Pollable.h

**Purpose:** Defines the abstract interface for objects that can expose a file descriptor to polling code.

**Important APIs/types/functions:** Virtual destructor and pure virtual `int getFD() const`.

**Control flow:** Implementers return a descriptor suitable for `poll` and `select`; `PollList` and event loops consume the descriptor.

**State and persistence behavior:** Interface-only; no state.

**Dependencies and integration points:** It is the base contract for fd-backed sockets, pipes, or other pollable resources in BeeGFS common code.

**Risks:** The interface cannot express descriptor lifetime, ownership, readiness semantics, or invalid fd states. Callers must handle stale descriptors externally.

**Test signals:** Mock implementations are sufficient for tests of `PollList` and poll dispatchers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/Pollable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Byteswap.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Byteswap.h

**Purpose:** Supplies byte-swap functions and host/little-endian/big-endian conversion macros for 16-, 32-, 64-, and 128-bit values.

**Important APIs/types/functions:** `byteswap16`, `byteswap32`, `byteswap64`, `byteswap128`, and macros `HOST_TO_LE_*`, `HOST_TO_BE_*`, `LE_TO_HOST_*`, and `BE_TO_HOST_*`.

**Control flow:** Wider swaps compose smaller swaps. `byteswap128` swaps the lower and upper 64-bit halves and uses `uint128::make`. Macro definitions depend on compile-time `BYTE_ORDER`.

**State and persistence behavior:** Stateless transformations. They define the wire/on-disk little-endian representation used by `Serialization.h`.

**Dependencies and integration points:** Depends on `UInt128.h` and system endian macros. Serializer/deserializer primitive conversions use these macros.

**Risks:** The `BE_TO_HOST_*` macros are defined through `HOST_TO_LE_*`, which is correct for little-endian hosts but suspicious for big-endian hosts where big-endian-to-host should be identity; this should be reviewed before using BE macros. Macro-based conversions can double-evaluate expressions if expanded with side effects.

**Test signals:** Unit tests should verify all swap widths and all conversion macros under little- and big-endian configurations, especially `BE_TO_HOST_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Byteswap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Serialization.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Serialization.h

**Purpose:** Defines BeeGFS's core binary serialization framework: `Serializer`, `Deserializer`, collection support, primitive endian conversion, padding, raw string/block views, backed pointer helpers, atomic helpers, and buffer allocation.

**Important APIs/types/functions:** Traits `ListSerializationHasLength`, `MapSerializationHasLength`, `IsSerdesPrimitive`, `SerializeAs`; classes `Serializer`, `Deserializer`, `PadFieldTo`; namespace `serdes` helpers `as`, `rawString`, `stringAlign4`, `backedPtr`, `rawBlock`, `atomicAs`, and `base`; string operators; collection operators; and `serializeIntoNewBuffer`.

**Control flow:** `Serializer` can run in sizing mode with null buffer or writing mode with a buffer. It writes primitives in little-endian form, emits optional collection total length plus element count, and can mark an earlier position to patch lengths. `Deserializer` bounds-checks reads, sets bad state on overflow/format mismatch, validates collection lengths when present, and can enforce EOF with `parseEof`. Padding RAII objects align field sizes by skipping/writing zero bytes on destruction.

**State and persistence behavior:** Serialized output is a compact little-endian binary wire/storage format. Deserializer raw string/block helpers expose pointers into the input buffer, so the input buffer lifetime is part of deserialized state for those views.

**Dependencies and integration points:** Used throughout BeeGFS net messages, storage metadata, tests, and `PreallocatedFile`. It depends on `Byteswap`, `UInt128`, BeeGFS `Atomic`, and Boost traits/scoped arrays.

**Risks:** Serialization contracts are compatibility-critical; changing length fields, alignment, or primitive encodings breaks wire/on-disk compatibility. Sizing mode increments offsets even after bad state, so callers must check `good`. Raw pointer helpers can dangle if buffers are freed. Collection deserialization inserts items as it goes and can leave partial data on failure after `clear`. `serializeIntoNewBuffer` allocates based on the first sizing pass and returns `-1` on allocation or second-pass failure.

**Test signals:** `TestBitStore.cpp` exercises serializer/deserializer round trips for `BitStore`. Broader tests should cover primitives, endian conversion, collection length validation, string null terminators, raw block views, backed pointers, atomics, alignment, EOF checks, and malformed buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Serialization.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/SerializeStr.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/SerializeStr.cpp

**Purpose:** Implements specialized serialization for collections of `std::string` (`list`, `vector`, and `set`) using a compact concatenated null-terminated string array.

**Important APIs/types/functions:** Templates `serializeStringCollection` and `deserializeStringCollection`; overloads of `%` for `std::list<std::string>`, `std::vector<std::string>`, and `std::set<std::string>`.

**Control flow:** Serialization reserves total length and element count at the start, writes each string bytes plus a null terminator, counts elements, then patches length/count through a marked serializer. Deserialization reads total length and count, validates that the encoded region ends with a null byte, skips over the region, then walks null-terminated strings into the target collection and verifies both count and remaining length reach zero.

**State and persistence behavior:** Defines the wire format for string collections: total byte length, element count, and contiguous null-terminated strings. It clears destination collections before filling.

**Dependencies and integration points:** Extends the core `Serialization.h` operators and is linked wherever string collection serialization is needed.

**Risks:** `totalLen - consumed` can underflow if the encoded total length is smaller than header bytes before `good` catches semantic invalidity. Embedded null bytes inside `std::string` values are not preserved because deserialization reconstructs using C string termination. Partial failure after `clear` can leave empty or partial output.

**Test signals:** Tests should cover empty collections, multiple values, malformed total lengths, missing final null, embedded null characters, set ordering, and all three collection types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/SerializeStr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestBitStore.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestBitStore.cpp

**Purpose:** GoogleTest coverage for `BitStore` sizing, bit access, mutation, clearing, and serialization.

**Important APIs/types/functions:** Fixture `TestBitStore` exposes private `lowerBits` and `higherBits`. Tests include `calculateBitBlockCount`, `setSizeAndReset`, `getter`, `setter`, helper `checkSerialization`, and `serialization`.

**Control flow:** Block-count tests iterate sizes up to 242 and compare expected limb counts. Getter/setter tests set one bit at a time, inspect the exact lower/higher limb values, and clear between iterations. Serialization computes size with a sizing serializer, writes to a buffer, deserializes into a second `BitStore`, checks `good`, byte consumption, and equality. Random-value serialization sets 75 random bits.

**State and persistence behavior:** Test-only in-memory state. It validates `BitStore` binary serialization compatibility through the common serializer.

**Dependencies and integration points:** Depends on `BitStore`, `Random`, `Serialization`, Boost scoped arrays, and GoogleTest. It is a direct test signal for `Serialization.h`.

**Risks:** `setSizeAndReset` has `bool finished = false; while(finished)` and therefore never executes, leaving intended resize/reset coverage disabled by a logic bug. Random test is nondeterministic. Private-field access in the fixture couples tests to implementation layout.

**Test signals:** Existing active tests cover block count, single-bit getter/setter, and serialization. Fixing the loop would restore reset coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestBitStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestEntryIdTk.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestEntryIdTk.cpp

**Purpose:** Tests entry ID token and full entry ID format validation.

**Important APIs/types/functions:** Tests `EntryIdTk::isValidHexToken` and `EntryIdTk::isValidEntryIdFormat`.

**Control flow:** Token tests accept non-empty hex strings up to eight characters and reject empty, too-long, and non-hex tokens. Format tests accept three dash-separated hex tokens and reject extra, missing, leading-empty, trailing-empty, and all-empty separator cases.

**State and persistence behavior:** No persistent state; validates textual ID contracts used by storage metadata.

**Dependencies and integration points:** Depends on `EntryIdTk` and GoogleTest. Entry ID format is tied to `StorageTk::generateFileID` and `StringTk::timeStampFromEntryID`.

**Risks:** Tests are concise and do not cover lowercase/uppercase variants exhaustively, root/special IDs, or numeric range semantics beyond token length.

**Test signals:** Good guard against accepting malformed separators and non-hex characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestEntryIdTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestIPAddress.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestIPAddress.cpp

**Purpose:** Tests `IPAddress` parsing, classification, formatting, equality, hashing, IPv4-mapped IPv6 handling, binary conversion, and CIDR network containment.

**Important APIs/types/functions:** Fixtures and tests cover `IPAddress::resolve`, `isIPv4`, `isIPv6`, `isLoopback`, `isLinkLocal`, `equals`, `toString`, default constructor, unordered maps with `std::hash<IPAddress>`, `toIPv4InAddrT`, `hash`, and `IPNetwork::fromCidr().containsAddress`.

**Control flow:** A table drives parse/classification expectations for IPv4, IPv6, zero, loopback, link-local, mapped IPv4, ULA, and invalid strings. Separate tests compare loopbacks/all-addresses, mapped IPv4 equality and data equivalence, network masks from /0 to /128, and expected hash values from upper/lower 64-bit halves.

**State and persistence behavior:** In-memory tests only. They validate stable textual and binary representations that may be persisted in configs or protocol fields elsewhere.

**Dependencies and integration points:** Depends on `IPAddress`, `IPNetwork`, GoogleTest, and unordered map hashing. These signals matter for network interface selection and node addressing.

**Risks:** Some tests assume host byte order values for `in_addr_t` expectations. The `testMap` loop only inserts `"::"` due to the condition, despite the comment mentioning `::0`; coverage may be narrower than intended.

**Test signals:** Strong coverage for IPv4-mapped IPv6 normalization and CIDR containment across IPv4/IPv6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestIPAddress.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestListTk.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestListTk.cpp

**Purpose:** Tests bounded advancement of a list iterator through BeeGFS `ListTk`.

**Important APIs/types/functions:** Single `TEST(ListTk, advance)` uses `ListTk::advance`.

**Control flow:** Builds a 10-element integer list, advances from begin by 5 and expects value 5, then advances by 44 and expects the iterator to equal `end`.

**State and persistence behavior:** Test-only list state; no persistence.

**Dependencies and integration points:** Depends on `ListTk`, BeeGFS integer list typedefs, and GoogleTest.

**Risks:** Only covers forward advancement from a valid iterator and overshoot to end. It does not cover zero advancement, already-end iterators, negative values if the API permits signed counts, or empty lists.

**Test signals:** Confirms safe end clamping for large positive advance values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestListTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestLockFD.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestLockFD.cpp

**Purpose:** Tests `LockFD` file locking, duplicate lock failure, cleanup unlink behavior, and lock-file content updates.

**Important APIs/types/functions:** Fixture creates a temporary directory with `mkdtemp` and removes it with `StorageTk::removeDirRecursive`. Tests call `LockFD::lock`, `FDHandle`, POSIX `flock`, `access`, `update`, and `updateWithPID`.

**Control flow:** `testInitialLock` obtains a lock, opens the same file, and confirms a nonblocking exclusive flock fails with `EWOULDBLOCK`. `testLockTwice` verifies a second `LockFD::lock` fails with that error. `testDoesUnlink` releases the lock and expects the path to disappear. `testUpdate` checks content update failure/success semantics and PID writing.

**State and persistence behavior:** Creates and removes temporary lock files. Validates that lock file content reflects update calls and that released locks unlink their files.

**Dependencies and integration points:** Directly tests `LockFD`; indirectly uses `StorageTk` cleanup. Relevant to daemon pid files and working-directory locks used by `StorageTk`.

**Risks:** Relies on local filesystem flock semantics and temporary directories under current working directory. Tests may be sensitive to platform differences in advisory locking.

**Test signals:** Good coverage for lock exclusivity and PID file update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestLockFD.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestNIC.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestNIC.cpp

**Purpose:** Tests network interface discovery and NIC preference rule matching.

**Important APIs/types/functions:** `NetworkInterfaceCard::findAll`, `findNicPosition`, `IPAddress::resolve`, `NicAddress`, `NICADDRTYPE_STANDARD`, `NICADDRTYPE_RDMA`, and protocol fields.

**Control flow:** `testFindNICs` discovers non-loopback interfaces and asserts each has a name, standard or RDMA type, and IPv4 or IPv6 protocol, with at least one NIC found. `testFindNicPosition` builds synthetic IPv4/IPv6 standard/RDMA NICs and evaluates preference/deny rule lists including wildcard, protocol preference, interface preference, RDMA preference, address-specific rules, and negation.

**State and persistence behavior:** Reads live host NIC state in `testFindNICs`; synthetic tests are in-memory.

**Dependencies and integration points:** Important for node connection selection and `NodesTk::applyLocalNicListToList`. Depends on actual network environment for discovery test.

**Risks:** Live NIC discovery can fail in minimal CI containers without non-loopback interfaces. Rule parsing coverage is good but does not test malformed rules.

**Test signals:** Strong coverage for preference order and deny semantics in NIC selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestNIC.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestPath.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestPath.cpp

**Purpose:** Tests basic `Path` parsing of an absolute path into components.

**Important APIs/types/functions:** Constructs `Path` from `/xyz/subdir/file`, checks `size`, and indexes components with `operator[]`.

**Control flow:** Builds the path string from an expected vector, constructs `Path`, then verifies each parsed component equals the original vector element.

**State and persistence behavior:** In-memory parsing only; no filesystem access.

**Dependencies and integration points:** `Path` is used heavily by `StorageTk` for on-disk path creation, format files, and chunk layout.

**Risks:** Very narrow coverage: no relative paths, trailing slashes, duplicate slashes, root-only path, dirname/operator `/`, or absolute flag checks.

**Test signals:** Confirms baseline absolute path component extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestPath.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestPreallocatedFile.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestPreallocatedFile.cpp

**Purpose:** Tests `PreallocatedFile` allocation guarantees, allocation failure, serialization size enforcement, optional empty state, and truncated-file error handling.

**Important APIs/types/functions:** Fixture creates/removes temp directories. Tests construct `PreallocatedFile<char, 1024*1024>`, `PreallocatedFile<char, max off_t>`, `PreallocatedFile<uint64_t>`, and `PreallocatedFile<uint64_t, 1>`; call `write`, `read`, `stat`, and `truncate`.

**Control flow:** Allocation test checks logical size `Size + 1` and block allocation at least that many bytes. Failure test expects huge preallocation to throw `std::system_error`. Read/write test writes a `uint64_t`, verifies too-small serialization throws, reads the value back, confirms unwritten file returns `boost::none`, truncates the good file, and expects read to throw.

**State and persistence behavior:** Creates real temporary files and removes them through `StorageTk::removeDirRecursive`.

**Dependencies and integration points:** Direct test signal for `PreallocatedFile.h` and indirect signal for `StorageTk` recursive deletion.

**Risks:** Allocation block-count expectations depend on filesystem behavior; sparse/preallocation semantics may differ. Huge allocation failure assumption is practical but environment-dependent.

**Test signals:** Covers the main API contract and important failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestPreallocatedFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestRWLock.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestRWLock.cpp

**Purpose:** Contains disabled GoogleTest scenarios for BeeGFS `RWLock` reader/writer locking, try-lock behavior, ordering, and runtime under concurrent randomized threads.

**Important APIs/types/functions:** Helper methods `sortThreadsInLockTimestamp`, `checkRandomRuntime`, `checkRandomExecutionOrder`, `checkRandomExecutionOrderReader`, and `checkRandomExecutionOrderWriter`. Disabled tests cover reader-on-reader, reader-on-writer, writer-on-reader, writer-on-writer, random readers/writers, try-read, try-write, and random try-lock cases.

**Control flow:** Tests create `RWLock`, start `TestLockThread` workers from the companion header, sleep before unlocking initial locks, join with timeouts, and assert whether locks should or should not have been acquired. Random tests sort threads by lock timestamp, verify writers do not overlap with prior readers/writers, allow overlapping readers, and compare runtime against minimum sequential/parallel expectations.

**State and persistence behavior:** In-memory concurrency state only. Uses `Time` timestamps and `Random` delays.

**Dependencies and integration points:** Depends on BeeGFS `RWLock`, `PThread`, `Time`, `Random`, `StringTk`, and GoogleTest. These are stress-style tests for low-level synchronization primitives.

**Risks:** All tests are disabled via `DISABLED_` macro, probably due to long runtime/flakiness. Timing assertions are sensitive to scheduler delays and coarse clock resolution. Helper sorting uses a simple bubble sort and copies thread result state, not live threads.

**Test signals:** Valuable manual/stress coverage when enabled, but not part of normal test runs unless disabled tests are explicitly requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestRWLock.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestRWLock.h -->
## sources/distributed-fs/beegfs/common/tests/TestRWLock.h

**Purpose:** Defines the `TestRWLock` fixture and nested `TestLockThread` worker used by the disabled RW lock stress tests.

**Important APIs/types/functions:** Test constants for thread counts, delays, sleeps, and timeouts; fixture helper declarations; nested `TestLockThread` constructors, `init`, `copy`, state getters, and `run`.

**Control flow:** `TestLockThread::run` sleeps for a configured start delay, attempts a read or write lock using either blocking or try-lock API, timestamps successful lock acquisition, sleeps while holding the lock, then timestamps and unlocks if it acquired the lock. The fixture uses getters to analyze ordering and runtime.

**State and persistence behavior:** Per-thread in-memory fields track lock pointer, sleep/delay, read/write mode, try mode, success flags, and timestamps. No persistence.

**Dependencies and integration points:** Depends on `Condition`, `RWLock`, `PThread`, `Time`, GoogleTest, and `unistd`. It is tightly coupled to `TestRWLock.cpp`.

**Risks:** `getSleepTimeMS` returns `bool` despite `sleepTimeMS` being `int`, truncating values for runtime analysis; this looks like a bug that can weaken `checkRandomRuntime`. Worker state is unsynchronized after join, which is acceptable if only read post-join. Long constants make tests expensive.

**Test signals:** Supports disabled stress tests; fixing the return type would make runtime validation meaningful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestRWLock.h -->

# subset-b-007624 Research

Grouped source research for LizardFS common I/O limiting, utility containers, serialization helpers, metadata/changelog helpers, networking buffers, read execution, Reed-Solomon coding, and RichACL logic. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limiting.h -->
# sources/distributed-fs/lizardfs/src/common/io_limiting.h

## Purpose
Declares the high-level I/O limiting abstraction used by mounts, masters, and tests to request bandwidth assignments by I/O group and to wait on local group queues. The source was read completely for this report.

## Important APIs, Types, And Functions
`ioLimiting::Limiter::request`, `registerReconfigure`, `Clock`, `RTClock`, `SharedState`, and `Group::wait/die` define the public limiting contract. `Group` tracks pending requests, past requests, reservations, throttling delta, and a death flag.

## Control Flow
Callers register a reconfiguration callback, build shared limiter state, and call `Group::wait` while holding an external mutex. The group queues requests, asks the limiter/master when needed, reserves granted bytes, sleeps through the injected clock, and notifies queued waiters.

## State And Persistence Behavior
No file persistence. Runtime state is in per-group lists, reservation counters, timestamps for request pacing/freshness, condition variables, and the referenced limiter.

## Dependencies And Integration Points
Depends on `io_limit_group.h`, `io_limits_database.h`, and `time_utils.h`; integrates with master-side limit databases and mount-side throttling code.

## Risks And Edge Cases
Concurrency correctness depends on callers holding the expected mutex and on condition-variable notification order. Stale reservation timestamps or too-small deltas can over-throttle or over-request from the master.

## Test Signals
Test through limiter mocks, fake clocks, wait/deadline behavior, queue fairness, group removal wakeups, and integration with the database/token-bucket implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limiting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.cc

## Purpose
Implements parsing for simple I/O limit configuration streams containing `subsystem` and `limit` directives plus shell-style full-line comments. The source was read completely for this report.

## Important APIs, Types, And Functions
`IoLimitsConfigLoader::load(std::istream&&)` clears previous limits, reads commands, fills `subsystem_` and `limits_`, rejects duplicate groups, and throws `ParseException` on malformed input.

## Control Flow
The parser streams token by token until EOF. `subsystem` consumes one string, `limit` consumes group and numeric limit, comments beginning with `#` skip the rest of the line, and unknown commands fail immediately. If any classified group is present, a subsystem is mandatory.

## State And Persistence Behavior
State lives in the loader object: a map of group limits and the last parsed subsystem. No persistence is performed here.

## Dependencies And Integration Points
Uses `common/exceptions.h` and `io_limit_group.h` for `kUnclassified`. The parsed map is consumed by `IoLimitsDatabase::setLimits` and reconfiguration paths.

## Risks And Edge Cases
Inline trailing comments after a numeric limit are tolerated only because formatted extraction stops before `#`; malformed numeric tokens poison the stream. Reusing a loader keeps the old subsystem unless overwritten.

## Test Signals
Covered by `io_limits_config_loader_unittest.cc` for valid files, missing subsystem, bad numeric values, unknown keywords, repeated groups, comments, and unclassified-only configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.h -->
# sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.h

## Purpose
Declares the loader object for I/O limit configuration files. The source was read completely for this report.

## Important APIs, Types, And Functions
`IoLimitsConfigLoader`, `LimitsMap = std::map<std::string,uint64_t>`, `load`, `subsystem`, and `limits` are the visible API.

## Control Flow
Header-only control flow is limited to simple const accessors; parsing is implemented in the `.cc` file.

## State And Persistence Behavior
Stores a subsystem string and ordered limits map. The ordered map matters because database reconciliation walks limits and existing groups in sorted order.

## Dependencies And Integration Points
Provides input for `IoLimitsDatabase`; depends on standard streams/maps and `platform.h`.

## Risks And Edge Cases
The rvalue-reference stream API encourages temporary streams, but callers must still supply a live stream object for the duration of `load`.

## Test Signals
Tests are in `io_limits_config_loader_unittest.cc`; compile coverage should also exercise consumers that include only the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limits_config_loader_unittest.cc

## Purpose
Validates the I/O limits configuration grammar and loader state after parsing. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses GoogleTest macros plus helpers `PAIR`, `LIMITS`, and `ASSERT_LIMITS_EQ` around `IoLimitsConfigLoader`.

## Control Flow
Each test constructs an in-memory string, feeds it through `std::istringstream`, and asserts either parsed subsystem/limits or `ParseException`.

## State And Persistence Behavior
No persistent state; each test creates a fresh loader.

## Dependencies And Integration Points
Depends on `common/exceptions.h`, `io_limits_config_loader.h`, and gtest.

## Risks And Edge Cases
The suite documents important edge cases but does not test loader reuse after a previous subsystem, negative limits, overflow, or CRLF handling.

## Test Signals
Passing tests are strong signals for directive parsing, duplicate detection, and the special unclassified-only case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limits_database.cc

## Purpose
Implements a per-I/O-group token-bucket database that grants byte counts according to configured KB/sec limits and accumulation windows. The source was read completely for this report.

## Important APIs, Types, And Functions
`setLimits`, `getGroups`, `getGroupsAndLimits`, and `request` are the active methods. `setLimits` reconciles the ordered group map with the parsed config and reconfigures each `TokenBucket`.

## Control Flow
Configuration walks existing groups and new limits in sorted order, erasing removed groups, inserting new `TokenBucket(now)` states, and converting limits from KB/sec to bytes/sec and max accumulated bytes. Requests dispatch to the matching bucket and return the granted byte count.

## State And Persistence Behavior
Runtime state is an ordered `std::map<GroupId, TokenBucket>`. No disk persistence; limits are reconstructed from config/reconfigure events.

## Dependencies And Integration Points
Consumes `IoLimitsConfigLoader::LimitsMap`; emits serializable `IoGroupAndLimit` records for management/status protocols.

## Risks And Edge Cases
Limit arithmetic multiplies by 1024 and `accumulate_ms`; large limits can overflow `uint64_t` in extreme configs. Unknown groups throw `InvalidGroupIdException`.

## Test Signals
Unit tests cover group listing, partial grants, token accumulation caps, and request timing progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database.h -->
# sources/distributed-fs/lizardfs/src/common/io_limits_database.h

## Purpose
Declares the I/O limits database and the serializable group/limit pair used to expose configured limits. The source was read completely for this report.

## Important APIs, Types, And Functions
`IoGroupAndLimit`, `IoLimitsDatabase::InvalidGroupIdException`, `setLimits`, `getGroups`, `getGroupsAndLimits`, and `request` define the contract.

## Control Flow
The header describes token-bucket-backed limiting; executable behavior is in `io_limits_database.cc` and `token_bucket.h`.

## State And Persistence Behavior
Holds a `std::map<GroupId, TokenBucket>` keyed by string group id. The map is mutable runtime state and not synchronized internally.

## Dependencies And Integration Points
Depends on `io_limits_config_loader.h`, `serialization_macros.h`, `token_bucket.h`, and `time_utils` through bucket APIs.

## Risks And Edge Cases
Callers must provide external synchronization if accessed concurrently. The comment says limits are bytes/sec, while implementation consumes loader limits as KB/sec and converts them.

## Test Signals
Validated by `io_limits_database_unittest.cc`; integration tests should cover concurrent reconfiguration and mount/master request loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limits_database_unittest.cc

## Purpose
Tests token-bucket semantics for the I/O limits database. The source was read completely for this report.

## Important APIs, Types, And Functions
Exercises `setLimits`, `getGroups`, and `request` using artificial `SteadyTimePoint` values.

## Control Flow
The tests configure groups, advance virtual time, issue requests, and assert exact granted byte counts, including partial and exhausted buckets.

## State And Persistence Behavior
No persistent state; each test owns its `IoLimitsDatabase` and fake time point.

## Dependencies And Integration Points
Depends on gtest and `time_utils.h`.

## Risks And Edge Cases
Coverage focuses on deterministic arithmetic. It does not cover missing group exceptions, reconfiguration removal, or integer overflow.

## Test Signals
Passing tests indicate correct KB-to-byte conversion, accumulation caps, and replenishment over time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/job_info.h -->
# sources/distributed-fs/lizardfs/src/common/job_info.h

## Purpose
Defines a small serializable job descriptor used for protocol/storage paths that need an id and human-readable description. The source was read completely for this report.

## Important APIs, Types, And Functions
`LIZARDFS_DEFINE_SERIALIZABLE_CLASS(JobInfo, uint64_t id, std::string description)` generates constructors/accessors/serialization support according to the project macro contract.

## Control Flow
There is no handwritten runtime flow; serialization macros provide pack/unpack behavior.

## State And Persistence Behavior
Instances persist only where callers serialize them in protocol messages or metadata-like structures.

## Dependencies And Integration Points
Depends on `serialization_macros.h`; integrates with generic serialization helpers.

## Risks And Edge Cases
ABI/schema risk is field order: changing `id` or `description` order changes serialized representation.

## Test Signals
Compile and serialization round-trip tests in consumers are the main signal; no dedicated test file is in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/job_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/judy_map.h -->
# sources/distributed-fs/lizardfs/src/common/judy_map.h

## Purpose
Provides a `std::map`-like wrapper around JudyL arrays for compact ordered maps with key and value types no larger than `Word_t`. The source was read completely for this report.

## Important APIs, Types, And Functions
Important types include `judy_map`, `detail::judy_pair`, `detail::judy_iterator`, iterators, `insert`, `erase`, `find`, `find_nth`, `lower_bound`, `upper_bound`, `operator[]`, `at`, `clear`, and comparison operators.

## Control Flow
Keys are converted to raw `Word_t` indices, JudyL stores mapped values, and iterators reconstruct a pair-like object with local key storage plus a reference to Judy memory. Insert uses placement construction; erase/destruction manually calls key/value destructors and deletes Judy nodes.

## State And Persistence Behavior
Owns a `Pvoid_t data_` Judy array. State is heap memory managed by Judy; no persistence. Erase partially invalidates iterators until `reload` is called.

## Dependencies And Integration Points
Requires Judy (`<Judy.h>`) and is compiled/tests guarded by `LIZARDFS_HAVE_JUDY`. Used where dense ordered integer maps benefit from Judy performance.

## Risks And Edge Cases
Raw reinterpretation means key ordering follows binary representation, not necessarily semantic ordering for signed or non-integral small types. Manual lifetime management and exception paths are high risk.

## Test Signals
`judy_map_unittest.cc` covers constructors, swap, iterators, insert/erase, equality, `at`, and `find_nth` when Judy support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/judy_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/judy_map_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/judy_map_unittest.cc

## Purpose
Tests the Judy-backed map facade when Judy support is enabled. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `judy_map<int,int>` and gtest across constructors, range construction, move/copy, swap, iteration, insert/erase, equality, and nth lookup.

## Control Flow
Tests fill maps, mutate entries through `operator[]`, erase by key/iterator, and compare iteration order to expected integer order.

## State And Persistence Behavior
No persistent state; tests allocate Judy arrays and rely on destructors/clear.

## Dependencies And Integration Points
Compiled only under `LIZARDFS_HAVE_JUDY`, depending on the Judy library.

## Risks And Edge Cases
Does not test custom small POD keys, exception safety, iterator `reload`, or signed negative key ordering.

## Test Signals
Passing tests signal the basic map facade works on the configured platform/Judy build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/judy_map_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lambda_guard.h -->
# sources/distributed-fs/lizardfs/src/common/lambda_guard.h

## Purpose
Defines a move-only RAII guard that invokes a supplied callable in its destructor unless ownership was moved away. The source was read completely for this report.

## Important APIs, Types, And Functions
`LambdaGuard<Function>`, move constructor, destructor, and `makeLambdaGuard` are the API.

## Control Flow
Construction stores a callable and marks it valid. Move construction transfers the callable and invalidates the source. Destruction calls the callable only when valid.

## State And Persistence Behavior
State is just a bool plus the callable. No persistence.

## Dependencies And Integration Points
Used by code paths needing cleanup on multiple exits, such as connection or resource handling.

## Risks And Edge Cases
The callable must be safe in a destructor; throwing from it would propagate during destruction and can terminate if another exception is active. Copy is disabled for safety.

## Test Signals
`lambda_guard_unittest.cc` confirms moved-from guards do not execute and moved-to guards execute at scope exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lambda_guard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lambda_guard_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/lambda_guard_unittest.cc

## Purpose
Validates the RAII cleanup behavior of `LambdaGuard`. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `makeLambdaGuard`, lambda captures, and move construction.

## Control Flow
The test nests guards, moves them, lets inner scope destruct, checks the side effect, then relies on outer destruction after the expectation.

## State And Persistence Behavior
No persistent state; state is a local integer counter.

## Dependencies And Integration Points
Depends on gtest and `lambda_guard.h`.

## Risks And Edge Cases
Coverage is intentionally minimal and does not test throwing callables or assignment, which is not defined.

## Test Signals
Passing test confirms single execution after move transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lambda_guard_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/legacy_acl.h -->
# sources/distributed-fs/lizardfs/src/common/legacy_acl.h

## Purpose
Provides legacy ACL serialization/conversion wrappers around the newer `AccessControlList` representation. The source was read completely for this report.

## Important APIs, Types, And Functions
`legacy::ExtendedAcl`, nested `Entry`, and `legacy::AccessControlList` convert named user/group entries, owning group masks, and POSIX mode into the old serialized form.

## Control Flow
Assignment from modern ACL extracts group mask and named entries. Conversion back reconstructs a modern ACL and sets mode. Serialization macros write mode and optional extended ACL data.

## State And Persistence Behavior
State is in-memory `mode`, optional `ExtendedAcl`, and entry vectors; persistence occurs only through project serialization.

## Dependencies And Integration Points
Depends on `access_control_list.h`, `massert.h`, and serialization macros. Integrates with metadata/protocol compatibility for older ACL formats.

## Risks And Edge Cases
The copy assignment only resets `extendedAcl` when the source has one; assigning from a legacy ACL without an extended ACL after one with an extended ACL may leave stale state. Schema/order compatibility is sensitive.

## Test Signals
Needs round-trip tests with minimal ACLs, extended ACLs, named users/groups, move/copy assignment, and legacy metadata compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/legacy_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer.h -->
# sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer.h

## Purpose
Implements the Bertsekas auction algorithm with epsilon scaling for square integer maximization assignment problems. The source was read completely for this report.

## Important APIs, Types, And Functions
`linear_assignment::auctionOptimization` overloads and `detail::auctionStep` are the main APIs. Inputs are fixed-size matrix-like containers and `std::array<int,N>` assignment outputs.

## Control Flow
For size 0/1 it returns directly. For larger sizes it scales every matrix value by `size+1`, initializes prices, repeatedly runs auction steps with decreasing epsilon, then finalizes with epsilon 1.

## State And Persistence Behavior
No persistence. It mutates the input value matrix in place and writes assignment/object-assignment arrays.

## Dependencies And Integration Points
Depends only on standard containers/algorithms/asserts. Used where chunk/data placement needs optimal pairings.

## Risks And Edge Cases
In-place scaling is surprising and can overflow for large values. Assertions enforce assumptions only in debug builds; release builds rely on sane size and value ranges.

## Test Signals
`linear_assignment_optimizer_unittest.cc` compares random cases up to size 10 against brute-force optimum and covers size 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer_unittest.cc

## Purpose
Tests the auction optimizer against exhaustive search for small random assignment matrices. The source was read completely for this report.

## Important APIs, Types, And Functions
`getMaximumAssignmentValue` recursively enumerates all assignments; tests call `auctionOptimization` and compare objective values.

## Control Flow
For sizes 2 through 10, the test fills random values, copies the matrix, solves with auction, and compares to brute force on the original copy.

## State And Persistence Behavior
No persistence; all matrices are stack arrays.

## Dependencies And Integration Points
Depends on gtest and `common/random.h` for random input generation.

## Risks And Edge Cases
Brute force grows factorially, so coverage is intentionally bounded. It does not check overflow or negative/extreme values systematically.

## Test Signals
Passing tests are strong algorithmic correctness signals for small integer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.cc -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.cc

## Purpose
Maps LizardFS protocol/status error codes to stable human-readable strings. The source was read completely for this report.

## Important APIs, Types, And Functions
`lizardfs_error_string(uint8_t status)` indexes a static string table sized by `LIZARDFS_ERROR_MAX + 1` and clamps unknown codes to the max/unknown slot.

## Control Flow
The function is pure table lookup: normalize status, return `const char*`.

## State And Persistence Behavior
State is a static const string array; no persistence.

## Dependencies And Integration Points
Must stay synchronized with `lizardfs_error_codes.h`; used by read executors and other protocol error reporting paths.

## Risks And Edge Cases
Enum/table drift yields wrong messages. The max enum currently maps to an unknown string, so adding codes requires table and max updates together.

## Test Signals
Needs tests checking selected enum-to-string pairs and out-of-range clamping; no dedicated test in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.h -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.h

## Purpose
Defines the canonical wire/status error code enum for LizardFS operations. The source was read completely for this report.

## Important APIs, Types, And Functions
`enum lizardfs_error_code` lists status 0 plus protocol, filesystem, chunk, lock, metadata, and POSIX-like errors through `LIZARDFS_ERROR_MAX`; declares `lizardfs_error_string`.

## Control Flow
No runtime flow in the header.

## State And Persistence Behavior
Values are protocol ABI and may be persisted or sent over the network.

## Dependencies And Integration Points
Consumed by `mfserr.cc`, protocol handlers, and clients; includes `<stdint.h>` for C-compatible code.

## Risks And Edge Cases
Renumbering or reusing codes breaks wire compatibility. New codes must be added consistently across string and errno conversion tables.

## Test Signals
Compile coverage plus explicit ABI/value tests are recommended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_statistics.h -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_statistics.h

## Purpose
Defines a serializable statistics snapshot for filesystem/global resource counters. The source was read completely for this report.

## Important APIs, Types, And Functions
`LizardFsStatistics` fields include version, memory/space counters, trash/reserved node counts, node counts, chunks, chunk copies, and regular copies.

## Control Flow
No handwritten control flow; generated serialization handles data movement.

## State And Persistence Behavior
Instances are transient snapshots but serialized over management protocols or stored where callers choose.

## Dependencies And Integration Points
Depends on `serialization_macros.h`; integrates with status/reporting APIs.

## Risks And Edge Cases
Field order and widths are schema-sensitive. Counters must be updated atomically/consistently by producers outside this header.

## Test Signals
Round-trip serialization and compatibility tests with management clients are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_statistics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_version.h -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_version.h

## Purpose
Defines compact numeric version encoding and milestone constants used for protocol feature gating. The source was read completely for this report.

## Important APIs, Types, And Functions
`LIZARDFS_VERSION`, `lizardfsVersion`, `lizardfsVersionToString`, `kDisconnectedChunkserverVersion`, `kStdVersion`, `kFirstXorVersion`, `kFirstECVersion`, `kACL11Version`, `kRichACLVersion`, and `kEC2Version` are the visible contract.

## Control Flow
Version encoding is `major << 16 | minor << 8 | micro` via arithmetic constants. String conversion decodes the three byte-like components.

## State And Persistence Behavior
No mutable state. Constants are compile-time protocol gates.

## Dependencies And Integration Points
Used by read request serialization to choose legacy/XOR/EC packet formats and by ACL feature checks.

## Risks And Edge Cases
Components above 255 are representable arithmetically but collide with the byte-style convention; disconnected chunkserver deliberately uses major 256.

## Test Signals
`lizardfs_version_unittest.cc` checks representative encoded values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_version_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_version_unittest.cc

## Purpose
Tests numeric encoding of LizardFS versions. The source was read completely for this report.

## Important APIs, Types, And Functions
Calls `lizardfsVersion` for representative major/minor/micro combinations.

## Control Flow
Straight-line expectations compare against hexadecimal encoded constants.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Depends on gtest and `lizardfs_version.h`.

## Risks And Edge Cases
Does not test `lizardfsVersionToString`, milestone constants, or boundary values.

## Test Signals
Passing tests protect the base encoding formula used by protocol feature gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_version_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lockfile.cc -->
# sources/distributed-fs/lizardfs/src/common/lockfile.cc

## Purpose
Implements advisory lockfile creation, locking, optional stale-file rejection, removal, and message storage. The source was read completely for this report.

## Important APIs, Types, And Functions
`Lockfile::lock`, `unlock`, `isLocked`, `hasMessage`, `eraseMessage`, and `writeMessage` are implemented using POSIX open/fcntl/fstat/ftruncate/write.

## Control Flow
Locking checks for an existing file, optionally rejects stale files, opens/creates the path, then applies a write lock with `F_SETLK`. Unlock closes the fd and removes the file. Message helpers operate on the opened lockfile fd.

## State And Persistence Behavior
Persistent state is the lockfile path and its contents. Runtime state is the owned `FileDescriptor`; `isLocked` is equivalent to fd open.

## Dependencies And Integration Points
Depends on `cwrap`, `massert`, `exceptions`, POSIX file APIs, and `fs` helpers. Used to protect singleton daemons/metadata operations.

## Risks And Edge Cases
Open-before-lock races and stale-file semantics are subtle. `writeMessage` does not retry partial writes. `unlock` removes the path even if another process created a new file at the same name after close in unusual races.

## Test Signals
Needs process-level tests for stale rejection, contention, message truncation/write, and cleanup on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lockfile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lockfile.h -->
# sources/distributed-fs/lizardfs/src/common/lockfile.h

## Purpose
Declares the `Lockfile` RAII-like manager and typed `LockfileException`. The source was read completely for this report.

## Important APIs, Types, And Functions
`Lockfile::StaleLock`, constructor/destructor, lock/message APIs, and `LockfileException::Reason` define the interface.

## Control Flow
The header describes operational flow; implementation performs POSIX locking in the `.cc` file.

## State And Persistence Behavior
Stores the lockfile name and `FileDescriptor`; persisted data is the actual lockfile and optional message.

## Dependencies And Integration Points
Depends on `cwrap.h` and `exceptions.h`; consumed by metadata locking and daemon startup paths.

## Risks And Edge Cases
The destructor does not automatically unlock, so callers must invoke `unlock` or rely on fd close/object ownership carefully.

## Test Signals
Integration tests should confirm behavior across processes, not only within one process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lockfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/loop_watchdog.cc -->
# sources/distributed-fs/lizardfs/src/common/loop_watchdog.cc

## Purpose
Provides static storage and SIGALRM handler wiring for `SignalLoopWatchdog`. The source was read completely for this report.

## Important APIs, Types, And Functions
Defines `SignalLoopWatchdog::exit_loop_`, `alarmHandler`, `kHandlerInitialized`, and debug `refcount_`.

## Control Flow
At static initialization, the SIGALRM handler is registered. The handler sets a volatile flag consumed by active watchdog instances.

## State And Persistence Behavior
Global process signal handler state is modified; no file persistence.

## Dependencies And Integration Points
Depends on `loop_watchdog.h` and platform signal APIs.

## Risks And Edge Cases
Installing a process-wide SIGALRM handler can conflict with other components. Volatile bool is minimal signal communication, and debug refcount asserts only one watchdog.

## Test Signals
Needs runtime tests carefully isolating SIGALRM interactions; unit coverage is not present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/loop_watchdog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/loop_watchdog.h -->
# sources/distributed-fs/lizardfs/src/common/loop_watchdog.h

## Purpose
Declares watchdog helpers for bounding long loop execution time. The source was read completely for this report.

## Important APIs, Types, And Functions
`SignalLoopWatchdog` uses `setitimer(ITIMER_REAL)`/SIGALRM; `ActiveLoopWatchdog` uses a `Timer`. Both expose `setMaxDuration`, `start`, and `expired`.

## Control Flow
Signal watchdog starts an interval timer and later observes `exit_loop_`. Active watchdog resets a timer and compares elapsed microseconds each poll.

## State And Persistence Behavior
Signal watchdog owns process-global signal/timer state; active watchdog owns only local duration and timer state.

## Dependencies And Integration Points
Depends on `time_utils.h`, signals, sys/time, and assertions. Used by algorithms that need cooperative loop cutoffs.

## Risks And Edge Cases
Signal mode is unsafe around other SIGALRM users and timers; active mode adds per-iteration time checks. Negative/zero durations are not guarded at runtime.

## Test Signals
Tests should cover immediate expiry, non-expiry, reset behavior, and signal-handler conflicts in integration environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/loop_watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lru_cache.h -->
# sources/distributed-fs/lizardfs/src/common/lru_cache.h

## Purpose
Defines a generic time- and capacity-bounded cache over one or more key fields, with optional hash/tree map and optional internal locking. The source was read completely for this report.

## Important APIs, Types, And Functions
`LruCacheOption`, `LruCache`, `get`, `cleanup`, `erase`, range `erase`, `clear`, and atomic counters `cacheHit/cacheExpired/cacheMiss/maxTime_ms` are the public contract.

## Control Flow
`get` checks for an unexpired key, releases the mutex before obtaining missing values, inserts new values, and performs bounded cleanup of expired or over-capacity oldest entries. A set keyed by timestamp and key-pointer tracks eviction order.

## State And Persistence Behavior
Runtime state is key-to-(timestamp,value) map plus time-to-key-pointer set. No persistence. Reentrant mode serializes internal mutation with a mutex.

## Dependencies And Integration Points
Depends on tuple hashing, `massert`, and `time_utils`. Used for memoized metadata/status computations and similar hot paths.

## Risks And Edge Cases
LRU naming is approximate: hits do not refresh timestamps, so eviction is insertion-time/expiry based. Concurrent misses can compute duplicate values; races return the just-computed value without updating the cache.

## Test Signals
`lru_cache_unittest.cc` covers memoization, erase, expiry, capacity behavior, and optional multithreaded access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lru_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lru_cache_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/lru_cache_unittest.cc

## Purpose
Exercises the generic cache for memoization, explicit erase, max age, max size, and optional multithreaded operation. The source was read completely for this report.

## Important APIs, Types, And Functions
Defines hash/non-reentrant and tree/reentrant cache typedefs and uses gtest plus `std::async` when available.

## Control Flow
Tests recursively compute Fibonacci through the cache, record calls for erase/expiry/capacity behavior, and concurrently get/erase ranges.

## State And Persistence Behavior
All state is local test cache instances and vectors of observed arguments.

## Dependencies And Integration Points
Depends on `lru_cache.h`, `massert`, gtest, and optional `std::future` support.

## Risks And Edge Cases
Multithreaded test does not wait explicitly in the shown snippet by calling `get` on futures, so failures may rely on future destructor behavior depending on standard/library behavior.

## Test Signals
Passing tests indicate the common cache policies work for expected single-threaded and reentrant use cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lru_cache_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/main.h -->
# sources/distributed-fs/lizardfs/src/common/main.h

## Purpose
Declares global extra command-line option storage and lookup helpers shared by daemon entry points. The source was read completely for this report.

## Important APIs, Types, And Functions
`gExtraArguments`, `main_get_extra_arguments`, and `main_has_extra_argument` are the visible API.

## Control Flow
No implementation in the header; callers retrieve the vector or test membership with optional case-sensitivity mode.

## State And Persistence Behavior
State is the process-global `std::vector<std::string> gExtraArguments`; no persistence.

## Dependencies And Integration Points
Depends on `case_sensitivity.h`; populated by main option parsing code.

## Risks And Edge Cases
Global mutable state is not synchronized. Semantics depend on the implementation matching the `CaseSensitivity` enum.

## Test Signals
Needs tests for case-sensitive and insensitive lookups and parsing integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/main_options.cc -->
# sources/distributed-fs/lizardfs/src/common/main_options.cc

## Purpose
Implements storage and lookup for extra `-o` style command-line options. The source was read completely for this report.

## Important APIs, Types, And Functions
Defines `gExtraArguments`, `main_get_extra_arguments`, and `main_has_extra_argument`.

## Control Flow
`main_has_extra_argument` optionally transforms the searched name and each option to lowercase, then scans for equality.

## State And Persistence Behavior
Process-global vector stores options for the lifetime of the process.

## Dependencies And Integration Points
Depends on `main.h` and `<algorithm>`; used by daemon/mount option logic.

## Risks And Edge Cases
The implementation lowercases when `mode == CaseSensitivity::kSensitive`, which appears inverted relative to the enum name and should be verified against `case_sensitivity.h` callers. It also passes `char` directly to `tolower`.

## Test Signals
No local unit tests are in this subset; add tests for mixed-case options and both enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/main_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/massert.h -->
# sources/distributed-fs/lizardfs/src/common/massert.h

## Purpose
Defines project assertion/abort macros with syslog diagnostics and optional exception throwing for tests. The source was read completely for this report.

## Important APIs, Types, And Functions
`massert`, `passert`, `sassert`, `eassert`, `zassert`, `mabort`, and `ABORT_OR_THROW` are the primary macros.

## Control Flow
Each macro checks a condition/status, logs a formatted error through `lzfs_pretty_syslog`, and aborts or throws depending on `THROW_INSTEAD_OF_ABORT`.

## State And Persistence Behavior
No persistent state; side effects are logs and process termination/exception.

## Dependencies And Integration Points
Depends on `mfserr.h` and `slogger.h`. Used throughout low-level code for invariants and system-call assertions.

## Risks And Edge Cases
Macros evaluate expressions in-place and terminate the process in production, so they must not guard recoverable external input. `errno` capture is handled in error macros but callers must preserve it when needed.

## Test Signals
Tests usually exercise this indirectly; dedicated tests can define `THROW_INSTEAD_OF_ABORT` to assert failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/massert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/md5.cc -->
# sources/distributed-fs/lizardfs/src/common/md5.cc

## Purpose
Implements MD5 digest routines plus LizardFS challenge-response and hex digest parsing helpers. The source was read completely for this report.

## Important APIs, Types, And Functions
`md5_init`, `md5_update`, `md5_final`, `md5_challenge_response`, and `md5_parse` are exported; internal helpers encode/decode little-endian words and run the MD5 transform rounds.

## Control Flow
MD5 update accumulates bit counts, buffers partial blocks, transforms complete 64-byte blocks, finalizes with padding and length, then zeroes the context. Challenge response hashes first half of challenge, data string, then second half.

## State And Persistence Behavior
State is caller-owned `md5ctx`; finalization clears it. No persistence.

## Dependencies And Integration Points
Used by authentication/password paths. Depends on fixed-width types and `md5.h`.

## Risks And Edge Cases
MD5 is cryptographically weak and should be treated as compatibility authentication only. `md5_parse` resizes output before validating and assumes NUL-terminated input.

## Test Signals
Needs known MD5 vector tests, challenge-response vectors, and invalid hex length/character tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/md5.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/md5.h -->
# sources/distributed-fs/lizardfs/src/common/md5.h

## Purpose
Declares the MD5 context and digest/authentication helper functions. The source was read completely for this report.

## Important APIs, Types, And Functions
`md5ctx` stores four state words, two count words, and a 64-byte buffer; functions initialize, update, finalize, build challenge responses, and parse 32-character hex strings.

## Control Flow
Header has no runtime flow beyond declarations.

## State And Persistence Behavior
Caller owns all digest state; serialized/persisted digest use happens in higher layers.

## Dependencies And Integration Points
Used by password/auth protocol code.

## Risks And Edge Cases
The API uses raw pointers and a `uint32_t` input length, limiting a single update call to 4 GiB-1 bytes and relying on caller buffer validity.

## Test Signals
Compile coverage plus known-vector tests are recommended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/md5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label.cc -->
# sources/distributed-fs/lizardfs/src/common/media_label.cc

## Purpose
Implements global string-to-16-bit-handle interning for chunk media labels and validation rules. The source was read completely for this report.

## Important APIs, Types, And Functions
`MediaLabelManager::iGetHandle`, `iGetLabel`, `isLabelValid`, wildcard constants, and `MediaLabel::kWildcard` are implemented.

## Control Flow
The manager initializes wildcard `_` to max handle. New labels receive monotonically increasing handles starting at 1, with rollback if reverse-map insertion fails. Label lookup by handle throws on invalid handle.

## State And Persistence Behavior
State is a function-local static manager containing two unordered maps and the next handle. No disk persistence, but handles may be serialized by callers.

## Dependencies And Integration Points
Integrates with chunk part/media label placement algorithms; uses `<cctype>` style `isalnum` through included headers.

## Risks And Edge Cases
The singleton maps are not synchronized, so concurrent first-use/new-label registration can race. `isLabelValid` should cast to unsigned char before `isalnum` for non-ASCII safety.

## Test Signals
`media_label_unittest.cc` covers validation, handle round trips, wildcard, and invalid handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label.h -->
# sources/distributed-fs/lizardfs/src/common/media_label.h

## Purpose
Declares media label interning and the lightweight `MediaLabel` value wrapper. The source was read completely for this report.

## Important APIs, Types, And Functions
`MediaLabelManager::HandleValue`, `getHandle`, `getLabel`, `isLabelValid`, `kWildcard`; `MediaLabel` constructors, string/handle conversions, comparisons, and hash functor are public.

## Control Flow
Most methods forward to the singleton manager or compare the stored handle.

## State And Persistence Behavior
`MediaLabel` stores only a 16-bit handle; the manager owns label/handle maps globally.

## Dependencies And Integration Points
Used by chunk storage/media-label selection code and unordered containers via `MediaLabel::hash`.

## Risks And Edge Cases
Default-constructed label has handle 0 and converting it to string throws because 0 is not registered. Handles are process-local assignments unless callers guarantee consistent registration ordering.

## Test Signals
Unit tests should cover default invalid conversion, ordering, hashing, and concurrent registration if used across threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/media_label_unittest.cc

## Purpose
Tests media label validation and handle/string round trips. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `MediaLabelManager::isLabelValid`, `getHandle`, `getLabel`, `MediaLabel`, and wildcard constants.

## Control Flow
Tests assert accepted alphanumeric/underscore labels up to length 32, reject empty/space/punctuation/too-long labels, and validate handle behavior.

## State And Persistence Behavior
Global singleton state persists across tests in-process, so labels registered in one test remain registered.

## Dependencies And Integration Points
Depends on gtest and `media_label.h`.

## Risks And Edge Cases
Does not test concurrent registration or default invalid `MediaLabel` string conversion.

## Test Signals
Passing tests protect the user-visible label grammar and basic interning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/message_receive_buffer.cc -->
# sources/distributed-fs/lizardfs/src/common/message_receive_buffer.cc

## Purpose
Implements socket reads into a fixed-size message buffer and removal of consumed LizardFS packets. The source was read completely for this report.

## Important APIs, Types, And Functions
`MessageReceiveBuffer::readFrom` and `removeMessage` are implemented.

## Control Flow
`readFrom` receives available bytes after the current fill position through `tcprecv` and updates `bytesReceived_`. `removeMessage` computes header plus payload size, memmoves any extra bytes down, and reduces the received count.

## State And Persistence Behavior
Runtime state is the vector buffer and received byte count. No persistence.

## Dependencies And Integration Points
Depends on packet header serialization and socket wrappers. Used by connection handlers reading framed protocol messages.

## Risks And Edge Cases
Callers must check `isMessageTooBig` before the buffer fills, otherwise `readFrom` asserts when full. `removeMessage` assumes a full message is present.

## Test Signals
Needs tests for partial header, full body, multiple messages in buffer, oversized messages, and socket error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/message_receive_buffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/message_receive_buffer.h -->
# sources/distributed-fs/lizardfs/src/common/message_receive_buffer.h

## Purpose
Declares a helper for accumulating framed LizardFS packets from sockets. The source was read completely for this report.

## Important APIs, Types, And Functions
`readFrom`, `removeMessage`, `hasMessageHeader`, `hasMessageData`, `isMessageTooBig`, `getMessageHeader`, and `getMessageData` define the API.

## Control Flow
Inline checks parse the packet header once enough bytes are present and compare received bytes to header length.

## State And Persistence Behavior
Owns a fixed-capacity byte vector and count of received bytes.

## Dependencies And Integration Points
Depends on `datapack.h`, `massert.h`, and `protocol/packet.h`.

## Risks And Edge Cases
Returned data pointer is valid only until the next read/remove. Header length is trusted for size checks and can represent malicious large payloads.

## Test Signals
Protocol-buffer unit tests and fuzzing of malformed headers would be useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/message_receive_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadata.cc -->
# sources/distributed-fs/lizardfs/src/common/metadata.cc

## Purpose
Implements metadata/changelog filename constants, metadata version validation, changelog version scanning, and one-time old changelog migration. The source was read completely for this report.

## Important APIs, Types, And Functions
`metadataGetVersion`, `changelogGetFirstLogVersion`, `changelogGetLastLogVersion`, `changelogsMigrateFrom_1_6_29`, filename constants, and `gMetadataLockfile` are defined.

## Control Flow
Metadata version parsing opens the file, validates known signatures, extracts version, then verifies the expected EOF marker. Changelog first-version reads a prefix and parses digits before colon. Last-version mmaps the file, requires final LF, walks backward to the previous line, and parses digits before colon. Migration renames `<name>.<i>.mfs` to `<name>.mfs[.<i>]` when safe.

## State And Persistence Behavior
Persistent state is metadata, changelog, sessions files, and the global metadata lockfile pointer. Functions perform filesystem reads/renames but do not modify metadata contents.

## Dependencies And Integration Points
Depends on POSIX file/mmap APIs, `cwrap`, `datapack`, `mfserr`, `slogger`, lockfile, and exception types.

## Risks And Edge Cases
Missing `fstat` error check in last-log path, mmap lifetime on exceptions before `munmap`, and strict newline/colon parsing are notable risks. Migration logs conflicts but leaves manual cleanup.

## Test Signals
Needs filesystem tests with old/new signatures, truncated EOF markers, empty/truncated/malformed changelogs, mmap failures, and migration collision cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadata.h -->
# sources/distributed-fs/lizardfs/src/common/metadata.h

## Purpose
Declares metadata/changelog/session filenames, version helper functions, migration helper, and the global metadata lockfile pointer. The source was read completely for this report.

## Important APIs, Types, And Functions
Visible APIs are filename externs, `metadataGetVersion`, `changelogGetFirstLogVersion`, `changelogGetLastLogVersion`, `changelogsMigrateFrom_1_6_29`, `MetadataCheckException`, and `gMetadataLockfile`.

## Control Flow
The header has no runtime flow beyond declarations and exception macro expansion.

## State And Persistence Behavior
The named files are persisted metadata/changelog/session artifacts controlled by master processes.

## Dependencies And Integration Points
Depends on `exception.h` and `lockfile.h`; used by metadata startup/recovery code.

## Risks And Edge Cases
The global lockfile pointer makes lifecycle/order important during startup/shutdown.

## Test Signals
Integration tests should exercise the declarations through real recovery/startup code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadataserver_list_entry.h -->
# sources/distributed-fs/lizardfs/src/common/metadataserver_list_entry.h

## Purpose
Defines a serializable metadataserver address/version entry. The source was read completely for this report.

## Important APIs, Types, And Functions
`MetadataserverListEntry` contains `uint32_t ip`, `uint16_t port`, and `uint32_t version` via serialization macros.

## Control Flow
No handwritten control flow.

## State And Persistence Behavior
Instances are serialized in master/shadow master listing protocols.

## Dependencies And Integration Points
Depends on `serialization_macros.h`.

## Risks And Edge Cases
Field order and IP byte-order expectations are ABI-sensitive.

## Test Signals
Round-trip serialization and list protocol tests are recommended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadataserver_list_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/mfserr.cc -->
# sources/distributed-fs/lizardfs/src/common/mfserr.cc

## Purpose
Converts LizardFS status codes to POSIX errno values and provides a thread-safe stable `strerror` wrapper. The source was read completely for this report.

## Important APIs, Types, And Functions
`lizardfs_error_conv(uint8_t)` maps selected protocol codes; `strerr(int)` caches `strerror` strings in a mutex-protected unordered map.

## Control Flow
Error conversion is a switch with default `EINVAL`. `strerr` checks the cache, calls `strerror`, stores a copy, and returns the stored C string.

## State And Persistence Behavior
State is the static error-description cache and mutex. No persistence.

## Dependencies And Integration Points
Depends on `errno_defs.h`, `lizardfs_error_codes.h`, and platform errno definitions.

## Risks And Edge Cases
Returned pointers remain valid unless the unordered_map rehash invalidates string objects; because strings are stored as values, rehash moves them and can invalidate previous `c_str()` pointers. Callers should not keep pointers long-term.

## Test Signals
Needs tests for representative status-to-errno mappings and concurrent `strerr` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/mfserr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/mfserr.h -->
# sources/distributed-fs/lizardfs/src/common/mfserr.h

## Purpose
Declares POSIX error conversion helpers for LizardFS status codes. The source was read completely for this report.

## Important APIs, Types, And Functions
`strerr(int)` and `lizardfs_error_conv(uint8_t)` are exported.

## Control Flow
No control flow in header.

## State And Persistence Behavior
No owned state in header; implementation owns the cache.

## Dependencies And Integration Points
Includes `lizardfs_error_codes.h` and protocol constants; used broadly by assertions, sockets, and user-facing errors.

## Risks And Edge Cases
Conversion coverage must track new protocol errors.

## Test Signals
Compile coverage plus mapping tests should protect callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/mfserr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_string.h -->
# sources/distributed-fs/lizardfs/src/common/moosefs_string.h

## Purpose
Implements MooseFS-compatible length-prefixed string serialization without NUL termination. The source was read completely for this report.

## Important APIs, Types, And Functions
`MooseFsString<LengthType>` inherits `std::string` and provides `maxLength`, `serializedSize`, `serialize`, and `deserialize`.

## Control Flow
Serialize writes length as `LengthType`, copies raw bytes, and advances the destination pointer. Deserialize reads length, checks remaining bytes, asserts the target is empty, assigns bytes, and advances source/count.

## State And Persistence Behavior
State is the inherited string content. Persistence is the serialized length+bytes format.

## Dependencies And Integration Points
Depends on `serialization.h`; used in legacy protocol/metadata compatibility.

## Risks And Edge Cases
Inheritance from `std::string` is pragmatic but can surprise users. Deserialize asserts empty output, so reusing objects without clearing aborts in debug/throw builds.

## Test Signals
`moosefs_string_unittest.cc` covers 8/16/32-bit lengths and max-length behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_string_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/moosefs_string_unittest.cc

## Purpose
Tests MooseFS-compatible string serialization for multiple length widths. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `MooseFsString<uint8_t/uint16_t/uint32_t>`, project serialize/deserialize helpers, and in/out pair macros.

## Control Flow
Builds long test strings, serializes substrings sized for each length width, deserializes, and checks equality and buffer size. Max-length test validates overflow rejection for 8-bit length.

## State And Persistence Behavior
No persistence beyond in-memory byte buffers.

## Dependencies And Integration Points
Depends on gtest and `unittests/inout_pair.h`.

## Risks And Edge Cases
Does not test deserializing into non-empty strings or malformed/truncated buffers except indirectly.

## Test Signals
Passing tests protect length-prefix sizing and round-trip compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_string_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_vector.h -->
# sources/distributed-fs/lizardfs/src/common/moosefs_vector.h

## Purpose
Implements MooseFS-compatible vector serialization that omits an explicit element count. The source was read completely for this report.

## Important APIs, Types, And Functions
`MooseFSVector<T>` inherits `std::vector<T>` and defines `serializedSize`, `serialize`, and `deserialize`.

## Control Flow
Serialize writes each element in sequence. Deserialize repeatedly appends default elements and deserializes until the supplied byte count reaches zero.

## State And Persistence Behavior
State is inherited vector contents. Persisted form is concatenated element encodings with length known externally.

## Dependencies And Integration Points
Depends on `serialization.h`; used for legacy protocol structures where array size is implied by packet size.

## Risks And Edge Cases
Malformed element encodings can leave a partially appended default element if deserialization throws. The assertion requiring bytes to decrease protects infinite loops but only under assertions.

## Test Signals
`moosefs_vector_unittest.cc` checks std::vector-like behavior and serialization round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_vector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_vector_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/moosefs_vector_unittest.cc

## Purpose
Tests the MooseFS vector wrapper behaves like `std::vector` and serializes without a length prefix. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `MooseFSVector<T>`, std vectors, gtest, and project in/out pair helpers.

## Control Flow
General behavior compares construction, copy, mutation, and equality. Serialization tests round-trip vector contents through byte buffers.

## State And Persistence Behavior
No persistent state.

## Dependencies And Integration Points
Depends on gtest and serialization test helpers.

## Risks And Edge Cases
Coverage does not include malformed/truncated element streams.

## Test Signals
Passing tests protect compatibility with code expecting vector-like semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_vector_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.cc -->
# sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.cc

## Purpose
Implements vectored writes over multiple buffers, with a Windows compatibility `writev` implementation. The source was read completely for this report.

## Important APIs, Types, And Functions
`MultiBufferWriter::addBufferToSend` and `writeTo` are implemented; Windows builds also define `writev` using socket send/poll wrappers.

## Control Flow
Buffers are appended as `iovec`s. `writeTo` calls `writev` starting at the first unsent buffer, then advances `buffersCompletelySent_` and adjusts the first partial iovec after short writes.

## State And Persistence Behavior
Runtime state is the vector of iovecs and count of fully sent buffers. It references caller-owned memory; no persistence.

## Dependencies And Integration Points
Depends on sockets wrappers on Windows and POSIX `writev` elsewhere. Used by packet send paths needing scatter/gather writes.

## Risks And Edge Cases
Caller must keep buffer memory alive and immutable until fully sent. `writeTo` assumes it is not called after all buffers are sent unless underlying `writev` tolerates zero count.

## Test Signals
Needs tests for full write, partial write, EAGAIN/error, empty/all-sent behavior, and Windows compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.h -->
# sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.h

## Purpose
Declares a helper that sends several caller-owned buffers through one vectored-write sequence. The source was read completely for this report.

## Important APIs, Types, And Functions
`MultiBufferWriter`, constructor, `addBufferToSend`, `writeTo`, `hasDataToSend`, and internal `iovec` vector are the API/state.

## Control Flow
Header inline flow initializes `buffersCompletelySent_` and checks whether unsent buffers remain.

## State And Persistence Behavior
Owns only iovec descriptors, not the referenced bytes.

## Dependencies And Integration Points
Depends on platform headers for `iovec` and integrates with network output code.

## Risks And Edge Cases
Lifetime of referenced memory is the main contract risk.

## Test Signals
Socket/write tests should pair this with controlled partial-write fakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/network_address.h -->
# sources/distributed-fs/lizardfs/src/common/network_address.h

## Purpose
Defines a compact IP/port address value with serialization, hashing, formatting, and connection exception context. The source was read completely for this report.

## Important APIs, Types, And Functions
`NetworkAddress`, comparison/equality, `toString`, `serializedSize/serialize/deserialize`, `std::hash<NetworkAddress>`, and `ChunkserverConnectionException` are visible.

## Control Flow
Formatting converts numeric IP through `ipToString` and appends `:port` only for nonzero ports. Serialization writes ip then port.

## State And Persistence Behavior
State is just `uint32_t ip` and `uint16_t port`; no persistence except serialized protocol use.

## Dependencies And Integration Points
Used throughout chunkserver connection, stats, and read-plan code.

## Risks And Edge Cases
Hash is MooseFS-derived and may collide; IP byte order must match project conventions. Exception stores a copy of the server address.

## Test Signals
`network_address_unittest.cc` covers string formatting for port/no-port/zero address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/network_address.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/network_address_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/network_address_unittest.cc

## Purpose
Tests `NetworkAddress::toString` formatting. The source was read completely for this report.

## Important APIs, Types, And Functions
Constructs addresses with IP `0x0A00FF10`, port 9425/0, and zero IP/port.

## Control Flow
Straight-line expectations verify dotted-quad rendering and optional port suffix.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Depends on gtest and `network_address.h`.

## Risks And Edge Cases
Does not test serialization, hashing, comparisons, or exception text.

## Test Signals
Passing tests protect the display form used in errors/logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/network_address_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/output_packet.h -->
# sources/distributed-fs/lizardfs/src/common/output_packet.h

## Purpose
Defines a move-only outgoing packet container used by servers writing protocol messages to clients. The source was read completely for this report.

## Important APIs, Types, And Functions
`OutputPacket(PacketHeader)`, `OutputPacket(MessageBuffer)`, default constructor, move operations, deleted copy operations, `packet`, and `bytesSent` are the contract.

## Control Flow
The header constructor reserves header+payload size, serializes the header, and resizes the buffer to include payload space. MessageBuffer constructor takes ownership of an existing serialized message.

## State And Persistence Behavior
State is an owned message buffer and byte progress counter; no persistence.

## Dependencies And Integration Points
Depends on `protocol/packet.h` and serialization helpers. Used by network output queues.

## Risks And Edge Cases
Payload bytes after the header are uninitialized/resized placeholders until callers fill them. `bytesSent` must be maintained by send loops.

## Test Signals
Tests should cover move-only behavior, header serialization size, and partial-send progress handling in output queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/output_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/parser.cc -->
# sources/distributed-fs/lizardfs/src/common/parser.cc

## Purpose
Implements a small string parser with position tracking and consume-by-size/string/type-predicate operations. The source was read completely for this report.

## Important APIs, Types, And Functions
`Parser` constructor/destructor, `consume(size_t)`, `consume(std::string)`, `consume(TypeCheckFunction)`, `checkState`, and `getLastConsumedCharacterCount` are implemented.

## Control Flow
Consumes update `previousPosition_` and `position_` after validating availability and match. Predicate consume advances while the type-check function accepts characters and fails if no characters matched.

## State And Persistence Behavior
State is the input string and current/previous positions. No persistence.

## Dependencies And Integration Points
Used as a base helper for typed parsers; depends only on standard string utilities.

## Risks And Edge Cases
Predicate consume calls `data_.at(newPosition)` without checking `newPosition < size` inside the loop, so a predicate that stays true through the final character can throw out_of_range. Number helpers in the header check `number.at(0)` rather than the requested position.

## Test Signals
Needs tests for end-of-string predicate consumes, no-match cases, and numeric conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/parser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/parser.h -->
# sources/distributed-fs/lizardfs/src/common/parser.h

## Purpose
Declares the parser base class and protected numeric conversion helpers. The source was read completely for this report.

## Important APIs, Types, And Functions
`Parser::Status`, `consume` overloads, protected `data/position/previousPosition`, `getHexValue`, `getDecValue`, and private `intFromHexString/intFromDecString` define the API for derived parsers.

## Control Flow
Template conversion helpers parse the last consumed substring as signed/unsigned hex or decimal using `stoll/stoull`.

## State And Persistence Behavior
Parser state is per object: copied input string and cursor positions.

## Dependencies And Integration Points
Depends on `platform.h` for compatibility `std::stoull` and standard exceptions.

## Risks And Edge Cases
Hex length check uses `length/2 > sizeof(T)` and may not reject all odd-length overflows; signedness casts can wrap.

## Test Signals
Derived parser tests should include malformed numbers, negative values into unsigned types, and substring positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/pcqueue.cc -->
# sources/distributed-fs/lizardfs/src/common/pcqueue.cc

## Purpose
Implements a C-style pthread producer/consumer queue with optional byte-size capacity. The source was read completely for this report.

## Important APIs, Types, And Functions
`queue_new/delete/isempty/elements/isfull/sizeleft/put/tryput/get/tryget` manage `qentry` linked-list nodes under a mutex with wait-free and wait-full condition variables.

## Control Flow
Producers allocate an entry, block or fail if adding `leng` would exceed `maxsize`, append to the tail, and signal consumers. Consumers block or fail when empty, pop the head, update byte size, and signal producers.

## State And Persistence Behavior
Runtime heap state is the queue struct, linked entries, counters, mutex, and condition variables. Payload ownership is transferred to callers/deleter by convention.

## Dependencies And Integration Points
Depends on pthreads, project assert macros, and `TracePrinter`. Used by legacy threaded worker queues.

## Risks And Edge Cases
Waiter counters are manually maintained and can become inaccurate if pthread waits are interrupted unexpectedly. `queue_delete` asserts no waiters, so lifecycle must be externally quiesced. Blocking `queue_put` leaks the preallocated entry only if an assertion aborts.

## Test Signals
Needs multithreaded tests for blocking/full/empty behavior, try error codes, delete with queued payloads, and size accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/pcqueue.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/pcqueue.h -->
# sources/distributed-fs/lizardfs/src/common/pcqueue.h

## Purpose
Declares the opaque C queue API and payload deleter helpers. The source was read completely for this report.

## Important APIs, Types, And Functions
`queue_deleter_dummy`, `queue_deleter_delete<T>`, and all `queue_*` functions are exported using `void*` queue handles.

## Control Flow
Header flow is limited to inline deleters that either do nothing or delete a typed payload pointer cast from `uint8_t*`.

## State And Persistence Behavior
Queue state is opaque and owned by the `.cc` implementation.

## Dependencies And Integration Points
Used by C and C++ legacy threaded components.

## Risks And Edge Cases
The `uint8_t*` payload type is untyped; callers must pair allocation and deleter correctly.

## Test Signals
Compile and multithreaded integration tests should cover API misuse boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/pcqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/platform.h -->
# sources/distributed-fs/lizardfs/src/common/platform.h

## Purpose
Central compatibility header for generated config features, missing errno aliases, older standard-library functions, Judy width flags, and `thread_local` fallback. The source was read completely for this report.

## Important APIs, Types, And Functions
Defines FreeBSD `ENODATA`, fallback `std::to_string`, fallback `std::stoull`, `LIZARDFS_HAVE_64BIT_JUDY`, and fallback `thread_local __thread`.

## Control Flow
Preprocessor-only control flow selects definitions based on config/platform macros.

## State And Persistence Behavior
No runtime state or persistence.

## Dependencies And Integration Points
Included by almost every common source file; depends on generated `config.h`.

## Risks And Edge Cases
Global fallback definitions inside namespace `std` are compatibility hacks and can conflict with modern libraries if feature detection is wrong. `__thread` is not a full C++ `thread_local` replacement for non-trivial types.

## Test Signals
Build matrix coverage across Linux, FreeBSD, old GCC, Judy/non-Judy, and Windows-like targets is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/portable_endian.h -->
# sources/distributed-fs/lizardfs/src/common/portable_endian.h

## Purpose
Provides portable host/big/little-endian conversion macro definitions across Linux, Cygwin, Apple, BSD, OpenBSD, NetBSD, Windows, and Solaris-like systems. The source was read completely for this report.

## Important APIs, Types, And Functions
Exports `htobe16/32/64`, `htole16/32/64`, `be16toh`, `le16toh`, byte-order constants, and platform-specific aliases where missing.

## Control Flow
Preprocessor branches include native endian headers or define conversion macros from platform byte-swap APIs.

## State And Persistence Behavior
No runtime state or persistence.

## Dependencies And Integration Points
Used by serialization/protocol code needing explicit endian conversions.

## Risks And Edge Cases
Unsupported platforms hit preprocessor errors. Macro names can collide with system headers if include order differs.

## Test Signals
Build tests on each supported OS/compiler are required; runtime byte-swap vector tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/portable_endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/random.cc -->
# sources/distributed-fs/lizardfs/src/common/random.cc

## Purpose
Defines and seeds the project-global random engine. The source was read completely for this report.

## Important APIs, Types, And Functions
`RandomEngine kRandomEngine` and `rnd_init()` are implemented. `rnd_init` seeds the global `std::mt19937` from `std::random_device` and returns 0.

## Control Flow
Control flow is a single seed assignment.

## State And Persistence Behavior
Global mutable RNG state persists for the process lifetime; no disk persistence.

## Dependencies And Integration Points
Used by `random.h` helpers and tests/algorithms needing random values.

## Risks And Edge Cases
The global engine is not synchronized and deterministic tests must seed/initialize carefully. `random_device` quality varies by platform.

## Test Signals
Tests should seed deterministically when reproducibility matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/random.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/random.h -->
# sources/distributed-fs/lizardfs/src/common/random.h

## Purpose
Declares the project random engine and templated uniform integer helpers. The source was read completely for this report.

## Important APIs, Types, And Functions
`RandomEngine`, `kRandomEngine`, `rnd_init`, `rnd<T>`, and `rnd_ranged<T>` are public.

## Control Flow
`rnd` returns a value over the full distribution range; `rnd_ranged` asserts positive range and returns [0, range).

## State And Persistence Behavior
State is the extern global `std::mt19937`.

## Dependencies And Integration Points
Used by tests and utility algorithms.

## Risks And Edge Cases
Unsigned/signed template use follows `std::uniform_int_distribution` constraints; global engine is not thread-safe.

## Test Signals
Unit tests should cover range bounds and deterministic seeded behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_operation_executor.cc -->
# sources/distributed-fs/lizardfs/src/common/read_operation_executor.cc

## Purpose
Implements one chunkserver read operation state machine for a single chunk part and read-plan entry. The source was read completely for this report.

## Important APIs, Types, And Functions
`sendReadRequest`, `continueReading`, `readAll`, `processHeaderReceived`, `processReadDataMessageReceived`, `processReadStatusMessageReceived`, `processDataBlockReceived`, and `setState` are the key functions.

## Control Flow
It serializes the correct read packet based on chunkserver version, sends it, then receives packet headers, READ_DATA prefixes, fixed-size data blocks, and READ_STATUS messages. It validates chunk id, offsets, sizes, status, and optional CRC before marking finished.

## State And Persistence Behavior
Runtime state includes message buffer, packet header, target data buffer pointer, chunk metadata, fd, state enum, current destination/bytes-left, completed block count, and current block CRC.

## Dependencies And Integration Points
Depends on sockets, protocol cltocs/cstocl serializers, `lizardfs_version`, CRC, exceptions, and `NetworkAddress`. Used by `ReadPlanExecutor` for parallel reads.

## Risks And Edge Cases
Assumes READ_DATA blocks are exactly `MFSBLOCKSIZE`; partial final read semantics must be handled by plan/request size/status protocol. Network errors mark chunkservers defective upstream.

## Test Signals
Needs protocol-fake tests for legacy/XOR/EC serialization, malformed headers, wrong ids/offsets/sizes, CRC mismatch, status errors, EAGAIN, timeout, and connection reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_operation_executor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_operation_executor.h -->
# sources/distributed-fs/lizardfs/src/common/read_operation_executor.h

## Purpose
Declares the per-part read operation executor and its state machine fields. The source was read completely for this report.

## Important APIs, Types, And Functions
`ReadOperationExecutor` constructor, move-only semantics, `sendReadRequest`, `continueReading`, `readAll`, `isFinished`, `chunkType`, `server`, and the private `ReadOperationState` enum/state processors are visible internally.

## Control Flow
The header documents single-step `continueReading` versus blocking `readAll` flow.

## State And Persistence Behavior
Owns no socket lifetime by itself; it stores the fd and writes into caller-provided buffer memory.

## Dependencies And Integration Points
Integrated by `ReadPlanExecutor` and chunkserver connection pools.

## Risks And Edge Cases
Move operations are defaulted while containing raw pointers/fd ids, so container moves must preserve external ownership expectations.

## Test Signals
Compile tests plus executor integration tests protect constructor and state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_operation_executor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan.h -->
# sources/distributed-fs/lizardfs/src/common/read_plan.h

## Purpose
Defines the abstract read-plan model for complex reads involving waves, redundant chunk parts, recovery, and post-processing. The source was read completely for this report.

## Important APIs, Types, And Functions
`ReadPlan`, `PartsContainer`, `ReadOperation`, `readOffset`, `readBufferSize`, `fullBufferSize`, pure virtual `isReadingFinished`, `isFinishingPossible`, `postProcessRead`, virtual `postProcessData`, and `to_string` are the core API.

## Control Flow
Read operations specify request offset/size, destination buffer offset, and wave. `postProcessData` lays out post-process buffers before the read buffer, runs `postProcessRead`, then walks configured post-process operations backward toward the final output buffer.

## State And Persistence Behavior
State is plan-owned vectors of read operations and post-process functions plus buffer sizes/prefetch flag. No persistence.

## Dependencies And Integration Points
Implemented by XOR/EC/simple read plan classes elsewhere and executed by `ReadPlanExecutor`.

## Risks And Edge Cases
Buffer layout is delicate: post-process sizes and function contracts must match exactly. Debug-only bounds asserts catch overlap/layout errors only in non-release builds.

## Test Signals
Tests should use concrete plan implementations to cover finish predicates, recovery post-processing, and buffer layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan_executor.cc -->
# sources/distributed-fs/lizardfs/src/common/read_plan_executor.cc

## Purpose
Implements execution of a `ReadPlan` across chunkserver connections, waves, prefetches, failures, and final post-processing. The source was read completely for this report.

## Important APIs, Types, And Functions
`startReadOperation`, `startPrefetchOperation`, `startReadsForWave`, `startPrefetchForWave`, `waitForData`, `readSomeData`, `executeReadOperations`, `checkPlan`, and `executePlan` are implemented. Static atomic execution counters are defined.

## Control Flow
Execution resizes the output buffer to the full plan size, starts wave 0 reads, prefetches next waves, polls active fds, advances per-fd executors, marks available/failed parts, starts later waves on timeout/failure, and stops when the plan says enough parts are available. Then it runs post-processing and shrinks the buffer to final size.

## State And Persistence Behavior
State includes active fd-to-executor map, available parts, networking failures, last failed server, stats counters, and the owned plan.

## Dependencies And Integration Points
Depends on chunk connector/pool, stats, sockets, protocol serializers, read operation executor, block/xor and exception types. Integrates client reads with chunkserver health tracking.

## Risks And Edge Cases
Cleanup on non-`Exception` throws may skip buffer rollback because catch catches `Exception&` only. Prefetch failures are ignored by design. Poll/wave timing controls read latency and redundancy load.

## Test Signals
Needs integration tests with fake connectors for wave progression, failure recovery, timeout, prefetch behavior, stats updates, buffer rollback, and post-processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan_executor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan_executor.h -->
# sources/distributed-fs/lizardfs/src/common/read_plan_executor.h

## Purpose
Declares the coordinator that executes a complete read plan against located chunk parts. The source was read completely for this report.

## Important APIs, Types, And Functions
`ReadPlanExecutor`, `ChunkTypeLocations`, constructor, `executePlan`, `partsFailed`, static counters, and protected execution helper declarations define the API.

## Control Flow
Header flow is declarative; implementation owns orchestration.

## State And Persistence Behavior
Holds references/ids/owned plan plus execution maps and part containers for the last run.

## Dependencies And Integration Points
Used by client read paths after planners produce `ReadPlan` objects and chunk locations.

## Risks And Edge Cases
The executor is stateful across calls and not documented as thread-safe. `partsFailed` reports last execution only.

## Test Signals
Compile and integration tests should cover repeated `executePlan` calls and failed-part reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan_executor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/reed_solomon.h -->
# sources/distributed-fs/lizardfs/src/common/reed_solomon.h

## Purpose
Implements templated Reed-Solomon encoding/recovery over GF(2^8), using ISA-L when available or the project Galois fallback. The source was read completely for this report.

## Important APIs, Types, And Functions
`ReedSolomon<MAXK,MAXM>`, matrix/table typedefs, `encode`, `recover`, `createRSMatrix`, `createEncodingMatrix`, `createRecoveryMatrix`, `selectRows`, `selectColumns`, and `matrixMultiply` are the important APIs.

## Control Flow
Construction creates an RS/Cauchy matrix for k,m. Encode selects parity rows and non-zero data columns, initializes GF tables, and computes parity. Recover selects available rows, inverts a decode matrix when needed, builds a recovery matrix for missing data/parity, caches GF tables by erased/needed/non-zero sets, and calls `ec_encode_data`.

## State And Persistence Behavior
State is cached GF tables, RS matrix, cached erased/needed/non-zero bitsets, and current k/m. No persistence.

## Dependencies And Integration Points
Used by erasure-coded chunk read/write paths; depends on ISA-L or `galois_field.h` and slice traits/tests.

## Risks And Edge Cases
The `gf_invert_matrix` failure path constructs `std::runtime_error` but does not throw it, so inversion failure would continue with invalid data. Assertions enforce counts and non-zero inputs only in debug builds.

## Test Signals
`reed_solomon_unittest.cc` covers parity encode/recover, zero inputs, benchmarks, and matrix invertibility across supported k/m combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/reed_solomon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/reed_solomon_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/reed_solomon_unittest.cc

## Purpose
Tests Reed-Solomon encoding/recovery correctness, zero-input optimization, performance benchmarks, and matrix invertibility. The source was read completely for this report.

## Important APIs, Types, And Functions
Helpers generate deterministic pseudo-random data, encode parity, recover erased parts, benchmark throughput, and test matrix invertibility through `gf_invert_matrix`.

## Control Flow
Correctness tests erase data and parity combinations and compare recovered buffers to originals. Benchmark tests run small and large encodes. Matrix tests enumerate erasure combinations for m=1..4 within supported ranges.

## State And Persistence Behavior
No persistence; tests allocate large in-memory buffers, including 64 MiB benchmark data.

## Dependencies And Integration Points
Depends on gtest, `reed_solomon.h`, `slice_traits.h`, and `time_utils.h`.

## Risks And Edge Cases
Benchmark tests can be heavy for regular unit runs. Matrix tests skip m=4 for k>20 in the RS matrix branch.

## Test Signals
Passing tests are strong signals for normal EC recovery and generator-matrix invertibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/reed_solomon_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/richacl.cc -->
# sources/distributed-fs/lizardfs/src/common/richacl.cc

## Purpose
Implements RichACL mode conversion, effective mask computation, inheritance, POSIX-mode equivalence, inode inheritance, and explicit inheritance expansion. The source was read completely for this report.

## Important APIs, Types, And Functions
`RichACL::isSameMode`, `setMode`, `getMode`, `createFromMode`, `allowedToWho`, `groupClassAllowed`, `computeMaxMasks`, `removeInheritOnly`, `checkInheritFlags`, `inherit`, `equivMode`, `inheritInode`, and `createExplicitInheritance` are implemented.

## Control Flow
Mode conversion maps POSIX mode bits to ACL masks, optionally removes delete-child on files, and builds allow/deny ACE sequences. Mask computation walks ACEs in reverse to derive owner/group/other maxima. Inheritance copies directory ACEs to child ACLs according to directory/file/no-propagate/inherit-only flags, then applies auto-inherit/protected behavior. POSIX equivalence attempts to collapse ACLs back to mode bits.

## State And Persistence Behavior
State mutated is the ACL object: flags, owner/group/other masks, and ACE list. Persistence occurs only when ACLs are serialized by higher layers.

## Dependencies And Integration Points
Depends on `richacl.h` definitions for ACE flags/masks and is used by ACL converters, metadata, and permission handling.

## Risks And Edge Cases
ACL semantics are order-sensitive and easy to regress. `equivMode` rejects unsupported ACE flags and non-special entries. File-vs-directory delete-child handling must remain consistent with permission checks.

## Test Signals
Needs broad ACL tests for POSIX-equivalent ACLs, named/group ACEs, inheritance flags, auto-inherit/protected transitions, mask computation, and mode round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/richacl.cc -->

# subset-b-007058 EOS namespace utilities, QuarkDB metadata protos, placement benchmarks, and MGM tests research

Grouped source research for EOS namespace helper headers, QuarkDB namespace metadata protobufs, placement/locking microbenchmarks, and MGM unit tests. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Etag.hh -->
# sources/distributed-fs/eos/namespace/utils/Etag.hh

## Purpose
Declares namespace ETag calculation helpers for EOS file and container metadata. The API centralizes how namespace-visible ETags are derived from `IFileMD`, `IContainerMD`, QuarkDB `FileMdProto`, and FST-side file metadata so HTTP/WebDAV-style consumers and MGM/FST paths can share the same identity semantics.

## Important APIs, types, and functions
The exported overloads are `calculateEtag(const IFileMD*, std::string&)`, `calculateEtag(const eos::ns::FileMdProto&, std::string&)`, `calculateEtag(IContainerMD*, std::string&)`, and FST variants taking `fst::FmdBase`. Specialized helpers `calculateEtagInodeAndChecksum()` and `calculateEtagInodeAndMtime()` expose the two main strategies: inode plus checksum when checksum metadata is available, or inode plus modification time as a fallback.

## Control flow
This header only declares the operations. Callers provide metadata and a mutable output string; implementations decide whether to inspect checksum, inode, and timestamps. The `useChecksum` overload makes that choice explicit for FST metadata.

## State and persistence
No state is stored here, but the produced ETag is externally observable and may be cached by clients. Any change in the implementation affects HTTP cache validators and object identity expectations.

## Dependencies and integration points
Depends on EOS namespace interfaces, FST metadata, and generated `proto/FileMd.pb.h`. It integrates namespace metadata services, FST metadata reporting, and MGM frontends that need stable ETags.

## Risks and test signals
Risk centers on compatibility: changing checksum-vs-mtime fallback changes client cache behavior. Tests should cover files with and without checksums, directories, QuarkDB proto input, FST `FmdBase` input, and stable output across equivalent metadata representations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Etag.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/FileListRandomPicker.cc -->
# sources/distributed-fs/eos/namespace/utils/FileListRandomPicker.cc

## Purpose
Implements random selection of a file id from an `IFsView::FileList`, which is an unordered bucketed container used by namespace filesystem views. It is a small utility for choosing an arbitrary file without materializing or indexing the whole list.

## Important APIs, types, and functions
`pickRandomFile(const IFsView::FileList& filelist, eos::IFileMD::id_t& retval)` returns `false` for an empty file list and otherwise writes a selected file id to `retval`. It uses `filelist.bucket_count()`, bucket iterators, and `eos::common::getRandom<uint64_t>()`.

## Control flow
The function first checks `empty()`. For non-empty lists it loops indefinitely, chooses a random bucket index in `[0, bucket_count - 1]`, obtains the bucket begin iterator, and returns the first element if the bucket is non-empty. Empty buckets cause another random draw.

## State and persistence
No durable state is modified. The only output is the selected file id. Randomness comes from EOS common random utilities.

## Dependencies and integration points
Includes `namespace/interface/IFsView.hh`, its matching header, and `common/utils/RandUtils.hh`. It is likely used by balancer, recycler, or policy code that samples file ids from filesystem views.

## Risks and test signals
The retry loop assumes non-empty lists have at least one non-empty bucket and that bucket count is non-zero. Sparse hash tables can make selection inefficient, and selecting the first element of a random bucket is not uniformly random over files. Tests should cover empty lists, single-element lists, sparse bucket distributions, and repeated sampling bias if fairness matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/FileListRandomPicker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/FileListRandomPicker.hh -->
# sources/distributed-fs/eos/namespace/utils/FileListRandomPicker.hh

## Purpose
Declares the random file picker helper used against namespace filesystem-view file lists. It gives callers a narrow function-level API without exposing the implementation's bucket sampling strategy.

## Important APIs, types, and functions
The single API is `bool pickRandomFile(const IFsView::FileList& filelist, eos::IFileMD::id_t& retval)`. It returns success/failure separately from the selected id, allowing callers to handle empty views without sentinel file ids.

## Control flow
The header has no control flow beyond namespace wrapping. The implementation in the `.cc` file performs empty-list handling and random bucket probing.

## State and persistence
No state is declared. Output is delivered through the `retval` reference.

## Dependencies and integration points
Includes `namespace/Namespace.hh` for the EOS namespace macros and relies on `IFsView::FileList` and `IFileMD::id_t` being available through namespace headers. Consumers include namespace-view utilities and MGM components that need random file sampling.

## Risks and test signals
The declaration hides distribution guarantees, so callers may incorrectly assume uniform random file selection. Tests should pair this header with implementation tests for empty lists, non-empty sampling, and build coverage that ensures all consumers see the required `IFsView` declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/FileListRandomPicker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/LocalityHint.hh -->
# sources/distributed-fs/eos/namespace/utils/LocalityHint.hh

## Purpose
Provides a compact locality hint string for namespace entries by combining a parent container identifier with the child name. The binary prefix keeps hints sortable or shardable by parent before the human-readable name suffix.

## Important APIs, types, and functions
`LocalityHint::build(ContainerIdentifier parent, const std::string& name)` returns an eight-byte big-endian representation of the parent id, a colon, and the entry name. Private helpers convert a `uint64_t` to big-endian bytes with `htobe64()` and `memcpy()`.

## Control flow
Construction is linear: convert parent id to binary, append `:`, append name, and return the resulting string. The binary prefix may contain null bytes, so consumers must treat the return value as a length-aware `std::string`, not a C string.

## State and persistence
No mutable state is kept. If locality hints are persisted or used as database keys, byte order and delimiter placement become part of that storage contract.

## Dependencies and integration points
Depends on namespace identifiers and EOS namespace macros. It likely integrates with QuarkDB key layout, cache locality, or metadata grouping where parent-child proximity matters.

## Risks and test signals
Main risks are binary-string misuse, platform availability of `htobe64`, and ambiguity if consumers expect printable keys. Tests should validate exact byte layout, embedded zero handling, stable ordering for parent ids, empty names, and names containing colons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/LocalityHint.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Mode.hh -->
# sources/distributed-fs/eos/namespace/utils/Mode.hh

## Purpose
Implements POSIX mode rendering helpers for EOS namespace metadata. It maps `mode_t` file-type and permission bits to the ten-character listing string used by Unix-style directory listings, with EOS-specific xattr indication.

## Important APIs, types, and functions
`S_XATTR` is an EOS marker bit used to display extended ACL/xattr presence. `modeToFileTypeChar(mode_t)` maps `S_IFIFO`, `S_IFCHR`, `S_IFDIR`, `S_IFBLK`, `S_IFREG`, `S_IFLNK`, and `S_IFSOCK` to `p`, `c`, `d`, `b`, `-`, `l`, and `s`. `modeToBuffer(mode_t, char*)` fills a caller-provided buffer with a mode string like `drwxr-xr-x`.

## Control flow
`modeToBuffer()` initializes the buffer to `"----------"`, sets the file type, applies user/group/other permission bits, then overlays sticky-bit, xattr, setuid, and setgid indicators. Unknown file types are logged critically and rendered as regular files.

## State and persistence
No state is retained. The output buffer must be large enough for ten characters plus null terminator. Display semantics are user-visible and affect command output compatibility.

## Dependencies and integration points
Depends on `<sys/stat.h>` and EOS static logging. It is used by namespace stat/listing helpers and metadata-to-text conversions.

## Risks and test signals
Setuid/setgid handling always writes `s` and does not distinguish no-execute uppercase `S`, while sticky/xattr compete for the last character. Tests should cover every file type, all permission classes, xattr-only, sticky-plus-xattr, setuid/setgid without execute, unknown types, and buffer sizing at callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Mode.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/PathProcessor.hh -->
# sources/distributed-fs/eos/namespace/utils/PathProcessor.hh

## Purpose
Collects path-splitting and absolute-path normalization helpers used by EOS namespace implementations. It bridges newer `StringSplit`-based path parsing with an older in-place splitter still used by the in-memory namespace backend.

## Important APIs, types, and functions
`insertChunksIntoDeque(std::string_view)` returns a deque of path components. The overload taking an existing deque prepends new path chunks while preserving component order. `splitPath(std::vector<char*>&, char*)` destructively splits a mutable C buffer by replacing slashes with null terminators. `absPath(std::string&)` normalizes `.` and `..` components into an absolute path.

## Control flow
Modern split helpers delegate to `eos::common::SplitPath`. The destructive splitter walks each character and records non-empty component starts. `absPath()` scans components from right to left, counts `..` skips, drops `.`, rebuilds with leading slashes, and returns `/` when all components collapse.

## State and persistence
No state is stored. `splitPath()` mutates its input buffer, so callers lose the original path string.

## Dependencies and integration points
Uses `common/StringSplit.hh` and standard containers. It is used by namespace views, path traversal, and legacy in-memory namespace code.

## Risks and test signals
Normalization does not preserve leading `..` above root, intentionally collapsing to root. Tests should cover repeated slashes, relative inputs, empty strings, trailing slashes, `.` and `..` combinations, destructive splitting side effects, and prepend order when an existing deque is non-empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/PathProcessor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/RenameSafetyCheck.hh -->
# sources/distributed-fs/eos/namespace/utils/RenameSafetyCheck.hh

## Purpose
Defines `isSafeToRename()`, a namespace consistency guard that prevents moving a directory under itself or under one of its descendants. It is a critical check for directory rename operations.

## Important APIs, types, and functions
`bool isSafeToRename(IView* view, IContainerMD* source, IContainerMD* target)` walks target ancestry through `IContainerMDSvc`. It uses `getContainerMDSvc()`, `getContainerMD(parentId)`, container id comparisons, and `throw_mdexception(EFAULT, msg)` on suspected namespace corruption.

## Control flow
The function rejects `source == target`, then starts at the target's parent and walks upward until root id `1`. If it sees the exact source object or a different object with the same id, it rejects the rename. A hard cap of 1024 iterations logs and throws for potential parent loops.

## State and persistence
No metadata is modified. The function assumes source/target or the global view mutex are at least read-locked by the caller, so correctness depends on external locking while parent links are inspected.

## Dependencies and integration points
Integrates with `IView`, `IContainerMD`, `IContainerMDSvc`, namespace exceptions, and EOS logging. It is used by namespace rename paths before committing parent-child changes.

## Risks and test signals
Null service returns, missing parents, and concurrent parent changes could crash or misclassify without caller locking. Tests should cover root, self-renames, moving into descendants, safe sibling moves, duplicate id object detection, and artificial parent loops exceeding 1024 iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/RenameSafetyCheck.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/RmrfHelper.hh -->
# sources/distributed-fs/eos/namespace/utils/RmrfHelper.hh

## Purpose
Implements a non-atomic recursive directory deletion helper for namespace paths. It is intended for controlled cleanup scenarios where all files and subcontainers under a path should be removed.

## Important APIs, types, and functions
`RmrfHelper::nukeDirectory(eos::IView* view, const std::string& path)` obtains the target container, removes every direct file through `IFileMDSvc::removeFile()`, collects child container paths with `ContainerMapIterator`, recursively deletes children, then removes the container itself through `view->removeContainer(path)`.

## Control flow
The function deletes files first, records subcontainer paths before recursing, recursively processes each child path, and finally removes the current directory. Child paths are built by appending a slash when needed and the child key.

## State and persistence
This mutates namespace metadata through file and container services. It is explicitly non-atomic: partial deletion is possible if an exception, service failure, or crash occurs mid-recursion.

## Dependencies and integration points
Depends on namespace metadata interfaces and container/file map iterators. It integrates with administrative cleanup paths and test utilities that need recursive deletion.

## Risks and test signals
Risks include deleting the wrong subtree, partial state after failure, deep recursion stack growth, races with concurrent creates, and unchecked null container lookups. Tests should cover empty directories, nested trees, paths with/without trailing slash, missing paths, service exceptions, and concurrent mutation policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/RmrfHelper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Stat.hh -->
# sources/distributed-fs/eos/namespace/utils/Stat.hh

## Purpose
Provides helpers to derive POSIX-like `mode_t` values from EOS namespace metadata entries. It bridges internal file/container metadata into stat/listing semantics.

## Important APIs, types, and functions
`modeFromMetadataEntry(const std::shared_ptr<IContainerMD>&)` returns the container mode and adds `S_XATTR` when `sys.acl` or `user.acl` exists. `modeFromMetadataEntry(const std::shared_ptr<IFileMD>&)` returns symlink mode for links, otherwise regular-file mode plus either explicit file flags or default `0444` plus owner write. It adds `EOS_TAPE_MODE_T` for files with a tape location.

## Control flow
Container handling is a simple mode read and xattr check. File handling first checks `isLink()`, then starts from `S_IFREG`, chooses explicit flags when non-zero or a default mode otherwise, and applies the tape bit if the file has `EOS_TAPE_FSID`.

## State and persistence
No state is modified. The computed mode is transient but user-visible through stat and listing operations.

## Dependencies and integration points
Depends on `common/FileSystem.hh`, namespace file/container interfaces, and `Mode.hh`. It integrates namespace metadata, ACL display, symlink handling, and tape-resident file presentation.

## Risks and test signals
The default permission branch for zero flags is policy-sensitive. Tests should cover directories with ACL xattrs, files with zero and non-zero flags, symlinks, tape locations, and interactions with `modeToBuffer()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Stat.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/StringConvertion.hh -->
# sources/distributed-fs/eos/namespace/utils/StringConvertion.hh

## Purpose
Defines a small namespace utility for fast conversion of arbitrary values to strings. The filename preserves a historical misspelling, while the API offers a concise wrapper around `fmt`.

## Important APIs, types, and functions
`template <typename T> std::string stringify(const T& elem)` returns `fmt::to_string(elem)`. It is generic and header-only.

## Control flow
There is no branching. Callers instantiate the template for types supported by `fmt::to_string`.

## State and persistence
No state is kept and no persistence is involved. Output formatting follows the linked `fmt` version and available formatters.

## Dependencies and integration points
Includes `namespace/Namespace.hh` for namespace macros and `fmt/format.h`. It is a convenience adapter for namespace code that wants a uniform string conversion spelling.

## Risks and test signals
Risk is low, but template instantiation failures surface at compile time for unsupported types. Formatting may differ from `std::to_string` for some values. Tests should cover integer, floating-point, string-like, and custom formatter-supported types if callers rely on exact text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/StringConvertion.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/proto/namespace/ns_quarkdb/ChangelogEntry.proto -->
# sources/distributed-fs/eos/proto/namespace/ns_quarkdb/ChangelogEntry.proto

## Purpose
Defines protobuf messages for recording MGM configuration changes. It is part of the QuarkDB-backed namespace/configuration metadata contract.

## Important APIs, types, and functions
Package `eos.mgm` contains `ConfigModification` with `key`, `previous_value`, and `new_value`, plus `ConfigChangelogEntry` with repeated modifications, an `int64 timestamp`, and a free-form `comment`.

## Control flow
The file has no executable control flow. Generated protobuf code serializes, deserializes, and mutates changelog entries for callers.

## State and persistence
Field numbers are persistent wire-format state. `modifications = 1`, `timestamp = 2`, and `comment = 3` must remain compatible with stored changelog entries. The schema records configuration deltas rather than full snapshots.

## Dependencies and integration points
Uses proto3 and integrates with MGM configuration engines, QuarkDB persistence, and admin/audit tooling that displays configuration history.

## Risks and test signals
Changing field numbers or package names would break existing data. Tests should cover round-trip serialization, multiple modifications per entry, empty comments, timestamp interpretation, and compatibility with previously stored changelog records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/proto/namespace/ns_quarkdb/ChangelogEntry.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/proto/namespace/ns_quarkdb/ContainerMd.proto -->
# sources/distributed-fs/eos/proto/namespace/ns_quarkdb/ContainerMd.proto

## Purpose
Defines the QuarkDB protobuf representation of EOS container metadata. It is a persistent schema for directories in the namespace.

## Important APIs, types, and functions
`ContainerMdProto` includes ids, owner uid/gid, `tree_size`, `mode`, `flags`, binary `name`, binary ctime/mtime/stime fields, string-to-bytes xattrs, recursive tree counters for containers and files, plus high-number transient `cloneid` and `clonefst` fields.

## Control flow
No executable flow is present. Generated protobuf accessors are used by namespace storage and migration code.

## State and persistence
Fields 1-14 are durable metadata. The transient clone fields use ids 256 and 257, signaling a separate compatibility surface. Binary time fields imply callers serialize native or EOS-specific time structures into bytes.

## Dependencies and integration points
Package `eos.ns` integrates with QuarkDB namespace services, container metadata classes, views, and tools that inspect or migrate namespace records.

## Risks and test signals
Wire compatibility is the main risk. Tests should cover old-record decoding, xattr map preservation, binary name handling, tree counter consistency, mode/flag round trips, and clone field treatment as transient rather than authoritative persisted namespace state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/proto/namespace/ns_quarkdb/ContainerMd.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/proto/namespace/ns_quarkdb/FileMd.proto -->
# sources/distributed-fs/eos/proto/namespace/ns_quarkdb/FileMd.proto

## Purpose
Defines the QuarkDB protobuf representation of EOS file metadata. It is the durable wire schema for file identity, ownership, layout, checksums, locations, xattrs, and timestamps.

## Important APIs, types, and functions
`FileMdProto` includes `id`, parent container id, uid/gid, size, layout id, flags, binary name and link target, ctime/mtime/stime/atime byte fields, primary checksum, replica `locations`, `unlink_locations`, string-to-bytes xattrs, alternative checksums keyed by algorithm id, and transient clone fields 256/257.

## Control flow
There is no executable logic. Generated code supplies accessors and serialization for namespace services.

## State and persistence
Field numbering is storage compatibility. Locations and unlink locations encode replica lifecycle, while checksum and layout fields feed data-integrity and placement logic. Binary timestamp/name fields require length-safe handling.

## Dependencies and integration points
Package `eos.ns` integrates with QuarkDB namespace file metadata, fsck, FST reconciliation, conversion, recycle, and stat/listing code.

## Risks and test signals
Risks include incompatible schema changes, inconsistent location/unlink state, checksum length mismatch for layout, and transient clone leakage into durable decisions. Tests should round-trip all fields, decode legacy records, preserve map fields, and verify namespace code handles absent optional proto3 fields correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/proto/namespace/ns_quarkdb/FileMd.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/test/microbenchmarks/mgm/BM_FlatScheduler.cc -->
# sources/distributed-fs/eos/test/microbenchmarks/mgm/BM_FlatScheduler.cc

## Purpose
Benchmarks EOS MGM flat placement scheduler strategies under varying group counts, replica counts, and thread counts. It measures scheduling throughput for round-robin, thread-local round-robin, random, fid-seeded random, weighted random, and weighted round-robin placement.

## Important APIs, types, and functions
Benchmark functions build `eos::mgm::placement::ClusterMgr` data with root/group buckets and `Disk` entries, instantiate `FlatScheduler` with a `PlacementStrategyT`, then call `schedule()`. Weighted variants use `eos::common::pickIndexRR()` and `PlacementArguments` with incrementing fids.

## Control flow
Each benchmark constructs a synthetic cluster once, then in the benchmark loop obtains immutable cluster data and calls the scheduler with the requested replica/stripe count. Google Benchmark registrations run 1, 8, 64, 128, and 256 threads across group counts 32-512 and placement widths 2, 3, and 6.

## State and persistence
State is in-memory synthetic cluster topology and scheduler counters. No persistent metadata is modified.

## Dependencies and integration points
Depends on Google Benchmark, placement `ClusterMap`, `PlacementStrategy`, `FlatScheduler`, and common container utilities. It tracks performance for code used by production file placement.

## Risks and test signals
This is a performance signal, not a correctness test. Risks include unrealistic topology, shared scheduler state under high thread counts, and excessive benchmark runtime. Useful signals are throughput regressions, scalability differences between global and thread-local seeds, and weighted placement overhead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/test/microbenchmarks/mgm/BM_FlatScheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/test/microbenchmarks/mgm/BM_RRSeed.cc -->
# sources/distributed-fs/eos/test/microbenchmarks/mgm/BM_RRSeed.cc

## Purpose
Benchmarks the basic round-robin seed generator against the thread-local variant used by placement scheduling. It isolates seed generation overhead from full scheduler topology traversal.

## Important APIs, types, and functions
`BM_RRSeed` constructs `eos::mgm::placement::RRSeed seed(10)` and repeatedly calls `seed.get(1, 0)`. `BM_ThreadLocalRRSeed` initializes `ThreadLocalRRSeed::init(10)` and calls `ThreadLocalRRSeed::get(1, 0)`. Both use Google Benchmark counters.

## Control flow
Each benchmark iteration performs ten seed reads and reports operation rate as `iterations * 10`. Registrations use `ThreadRange(1, 64)` and real time to observe contention effects.

## State and persistence
State is transient seed state. `ThreadLocalRRSeed` has static/thread-local state initialized before the loop. No persistent data is touched.

## Dependencies and integration points
Depends on Google Benchmark and MGM placement seed classes. It supports performance decisions for scheduler round-robin state management.

## Risks and test signals
Signals are throughput and contention differences. Risks include benchmark sensitivity to static initialization, insufficient coverage of multiple bucket keys, and not validating sequence correctness. Correctness tests should separately cover wraparound and concurrent uniqueness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/test/microbenchmarks/mgm/BM_RRSeed.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/test/microbenchmarks/namespace/ns_quarkdb/BM_NSLocking.cc -->
# sources/distributed-fs/eos/test/microbenchmarks/namespace/ns_quarkdb/BM_NSLocking.cc

## Purpose
Benchmarks namespace metadata locking paths for QuarkDB-backed namespace objects. It compares a single container write lock against bulk write locking of multiple namespace objects.

## Important APIs, types, and functions
The fixture creates `eos::ns::testing::NsTests`, namespace containers/files, `MDLocking::ContainerWriteLock`, and `MDLocking::BulkMDWriteLock`. `simulateWork()` burns CPU while locks are held to mimic protected work.

## Control flow
For each benchmark, thread 0 initializes global test namespace objects. `ContainerMDLock` repeatedly locks one container, changes an attribute, and updates the container store. `BulkNSObjectLocker` adds two containers and one file to a bulk locker, acquires all locks, and simulates work. Both run over `ThreadRange(1, 5000)`.

## State and persistence
State is an in-memory/test QuarkDB namespace fixture and global shared object pointers. The benchmark mutates test metadata attributes but not production state.

## Dependencies and integration points
Depends on Google Benchmark, namespace locking APIs, bulk locker, QuarkDB namespace test harness, and hierarchical view classes.

## Risks and test signals
Global fixture pointers and thread-0 setup can race if other threads enter before initialization is visible. Signals include lock contention scalability and bulk-lock overhead. Tests/benchmarks should watch for deadlocks, lock ordering regressions, update-store cost, and unrealistic CPU work dominating lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/test/microbenchmarks/namespace/ns_quarkdb/BM_NSLocking.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/AccessTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/AccessTests.cc

## Purpose
Tests MGM access-control primitives: stall-rule state, POSIX mode checks, ACL overrides, prepare permissions, deletion/rename permissions, sticky-bit behavior, and access rule key normalization.

## Important APIs, types, and functions
The file exercises `mgm::Access::SetStallRule`, `AccessChecker::checkContainer`, `AccessChecker::checkFile`, `mgm::Acl`, `ProcessRuleKey`, Quark namespace metadata stand-ins, and `VirtualIdentity`. Helpers create fake containers/files with uid/gid/mode and identities.

## Control flow
Tests construct metadata and identities, then assert allow/deny outcomes for user/group/other permission bits, ACL user/group entries, prepare flag `P_OK`, deletion flag `D_OK`, and sticky directory semantics. Rename/delete tests combine container and file checks to model operation-level authorization.

## State and persistence
`Access_SetRule` mutates static global stall maps and restores previous state. Other tests use transient metadata objects and ACL strings. No persistent namespace state is written.

## Dependencies and integration points
Uses Google Test, MGM access/ACL/admin command code, `AccessChecker`, common identity definitions, QuarkDB metadata classes, and mapping fixture setup.

## Risks and test signals
This file is a strong behavioral oracle for authorization edge cases. Risks include global stall state leakage across tests, ACL identity-context subtleties, sticky-bit owner rules, and default file mode interpretation. Missing signals include root/admin bypass behavior and multiple supplementary groups beyond simple allowed-gid cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/AccessTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/AclCmdTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/AclCmdTests.cc

## Purpose
Tests user-facing ACL command helper logic for parsing ACL strings into ordered rule maps, locating/inserting rules, moving existing rules, and validating requested insertion positions.

## Important APIs, types, and functions
The tests cover `AclCmd::GenerateRuleMap`, `key_position`, `insert_or_assign`, `get_iterator`, and `AclCmd::GetRulePosition`. `RuleMap` is treated as an ordered vector-like structure of ACL keys and bitmasks.

## Control flow
The parsing test converts a compound ACL string with grant/deny modifiers into expected bitmasks. Position tests build a map, insert new keys, update existing keys, verify move semantics with lvalue/rvalue keys, and exercise repositioning when `move_existing` is true.

## State and persistence
All state is local to tests. The output bitmasks and ordering are command semantics that influence persisted ACL xattr strings when admin/user ACL commands update namespace metadata.

## Dependencies and integration points
Depends on Google Test and `mgm/proc/user/AclCmd.hh`. It is tied to MGM proc/user ACL command behavior and ACL serialization order.

## Risks and test signals
The tests catch ordering regressions that plain maps would hide. Risks include brittle binary literals, unclear move expectations, and incomplete coverage of malformed ACL tokens. Additional tests should cover duplicate group/user keys in parsed strings, invalid permission characters, empty rule maps, and position arguments from real command parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/AclCmdTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/CapsTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/CapsTests.cc

## Purpose
Tests FUSEX capability tracking in the MGM `Caps` class, including storage, updates, expiration, deletion, broadcast selection, implied capabilities, and concurrent delete/imply behavior.

## Important APIs, types, and functions
The fixture builds a fake `XrdMgmOfs`, configures environment variables to avoid service startup, and uses `Caps::Store`, `Get`, `HasCap`, `pop`, `expire`, `dropCaps`, `Remove`, `Delete`, `BroadcastCap`, `GetBroadcastCapsTS`, `GetAllCaps`, `GetInodeCapAuthIds`, and `Imply`. Helpers create `eos::fusex::cap` and `VirtualIdentity` values.

## Control flow
Tests insert capabilities keyed by auth id, update client id or inode id, inspect the three internal views (`GetCaps`, client caps, client/inode caps), expire time-ordered entries, drop by client UUID, remove by iterator, delete by inode, and select broadcast targets while excluding a caller's own UUID. The final test runs delete and imply loops concurrently.

## State and persistence
State is in-memory capability maps and time-ordered expiration structures. No durable data is written, but the fake global `gOFS` and environment are shared across the fixture suite.

## Dependencies and integration points
Depends on FUSE server capability code, XRootD MGM OFS, ZMQ teardown behavior, fusex protobuf messages, and Google Test.

## Risks and test signals
Signals are rich for index consistency and expiration semantics. Risks include static fixture global leakage, real-time sleeps making tests slow/flaky, and expected `ncaps()` divergence from `GetCaps().size()` after updates. Concurrency coverage is useful but nondeterministic and should be complemented with thread-sanitizer runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/CapsTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/CommitHelperTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/CommitHelperTests.cc

## Purpose
Tests version-file timestamp increment logic in `CommitHelper`. This supports commit/versioning code that encodes timestamps into file names.

## Important APIs, types, and functions
The test includes `mgm/ofs/fsctl/CommitHelper.hh` under `IN_TEST_HARNESS` and exercises `CommitHelper::IncrementTsForVersionFn(std::string)`.

## Control flow
It passes valid version names like `1724758410.00001111` and expects the seconds component to increment while preserving the suffix. Invalid inputs with missing separators, nonnumeric seconds, or empty suffix are expected to round-trip unchanged.

## State and persistence
No state is stored. The function output may become a persisted version-file name in real commit paths.

## Dependencies and integration points
Depends on Google Test and MGM OFS fsctl commit helper internals. It integrates with versioned file creation and commit workflows.

## Risks and test signals
The test covers basic parse/fallback behavior but not overflow, negative timestamps, multiple dots, or very large suffixes. Regression risk is high for users relying on stable version filename format, so additional tests should cover boundary timestamps and real version-path generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/CommitHelperTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/ConversionInfoTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/ConversionInfoTests.cc

## Purpose
Tests parsing and serialization of MGM conversion job descriptors. Conversion strings encode file id, target scheduling group, layout id, placement policy, app tag, and ctime-update behavior.

## Important APIs, types, and functions
The tests use `eos::mgm::ConversionInfo::parseConversionString()`, `ConversionInfo::ToString()`, `GroupLocator::parseGroup()`, and fields such as `mLid`, `mAppTag`, `mPlctPolicy`, and `mUpdateCtime`.

## Control flow
Construction tests parse valid strings with gathered/scattered/hybrid placement policy tails, optional app tags delimited by carets, and trailing `+` ctime flags. Invalid strings assert null parse results. Optional-member tests verify canonical `ToString()` ordering when app tag appears before or after placement policy.

## State and persistence
State is the parsed conversion object. The string representation is persisted or queued in proc paths, so canonicalization affects job identity and compatibility.

## Dependencies and integration points
Depends on Google Test, MGM conversion code, namespace exceptions, `GroupLocator`, and XRootD string utilities for URL/proc path construction.

## Risks and test signals
The tests protect delimiter grammar and canonical output. Risks include reserved-character handling, layout id numeric base assumptions, and URL/proc path escaping. Additional signals should cover empty policy tags, app tags containing carets, and invalid group locators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/ConversionInfoTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/CtaUtilsTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/CtaUtilsTests.cc

## Purpose
Tests CTA/tape garbage collection utility helpers for numeric parsing, integer division rounding, binary time conversion, and bounded file descriptor reads.

## Important APIs, types, and functions
The file exercises `CtaUtils::toUint64`, `divideAndRoundToNearest`, `divideAndRoundUp`, `bufToTimespec`, and `readFdIntoStr`. It expects custom exceptions such as `EmptyString`, `NonNumericChar`, `ParsedValueOutOfRange`, and `BufSizeMismatch`.

## Control flow
Tests validate successful and failing integer parse inputs, exhaustive small-number rounding cases, binary serialization/deserialization of `timespec`, pipe-based reads with exact, truncated, and shorter-than-limit data, and a too-large max string length throwing `std::out_of_range`.

## State and persistence
All state is local to the test process. Pipe file descriptors are created for read tests; production callers may use the same helper to read proc or command output.

## Dependencies and integration points
Depends on MGM `CtaUtils.hh`, Google Test, `<limits>`, and POSIX `pipe`/`write`. It supports tape GC and CTA integration code.

## Risks and test signals
The tests cover many boundaries but do not close pipe fds explicitly, which is acceptable for short tests but not a production pattern. Additional tests should cover interrupted reads, nonblocking fds, negative divisors if allowed by type, and platform differences in `timespec` binary layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/CtaUtilsTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/EgroupTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/EgroupTests.cc

## Purpose
Tests CERN e-group membership lookup and caching behavior used by MGM authorization. It covers both a live functional LDAP-style lookup and deterministic injected cache behavior.

## Important APIs, types, and functions
The tests use `eos::mgm::Egroup`, `SteadyClock`, `Egroup::Member`, `inject`, `DumpMember`, `DumpMembers`, `refresh`, and `getPendingQueueSize`.

## Control flow
The functional test calls real membership checks for known CERN users/groups. Cache tests inject membership statuses, advance a fake clock through lifetimes, wait for pending asynchronous refresh queues to drain, and verify stale-to-refreshed membership transitions. Explicit refresh bypasses normal expiration delay.

## State and persistence
State is in-memory membership cache with expiration lifetimes and asynchronous refresh queue. No durable state is persisted.

## Dependencies and integration points
Depends on MGM e-group code, common steady clock abstraction, and Google Test. The live test integrates with CERN external directory infrastructure.

## Risks and test signals
The live functional test is environment-dependent and may fail outside CERN network or when directory data changes. Deterministic tests strongly cover cache lifetime semantics but spin-wait on queue size. Additional tests should cover lookup failures, negative-cache expiration, and shutdown of pending refresh threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/EgroupTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/FileSystemRegistryTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/FileSystemRegistryTests.cc

## Purpose
Tests `FileSystemRegistry`, the MGM utility that maps filesystems by id, pointer, and queue path. It verifies duplicate prevention and cleanup of all lookup indexes.

## Important APIs, types, and functions
The tests use `FileSystemRegistry::registerFileSystem`, `lookupByID`, `lookupByPtr`, `lookupByQueuePath`, `eraseById`, `eraseByPtr`, `clear`, and `size`, with `FileSystemLocator` values and dummy `FileSystem*` pointers.

## Control flow
The basic test registers a locator/id/pointer triple, rejects duplicates by locator/id/pointer combinations, validates each lookup path, erases entries by id and pointer, and clears the registry. The queue-path collision test ensures one queue path cannot be registered twice under different ids.

## State and persistence
All registry state is in-memory. The registry mirrors production MGM filesystem inventory and must keep multiple indexes consistent.

## Dependencies and integration points
Depends on Google Test, `mgm/utils/FileSystemRegistry.hh`, and common filesystem locator formatting. It integrates with FsView/filesystem management code.

## Risks and test signals
Tests provide good index-consistency signals. Risks not covered include concurrent registration/erase, null pointer registration policy beyond lookup, and filesystem locator normalization differences. Queue path formatting is part of the compatibility surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/FileSystemRegistryTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/FsViewTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/FsViewTests.cc

## Purpose
Tests MGM filesystem view support classes: geo-tree iteration, FsView reset cleanup, filesystem UUID mapping, filesystem config parsing/joining/relocation, balancer stats, and random vector iterator selection.

## Important APIs, types, and functions
Coverage includes `GeoTree`, `FsView::Reset`, `FsNode::sNumInstances`, `FilesystemUuidMapper`, `ConfigParsing::parseFilesystemConfig`, config join/relocate helpers, `FsBalancerStats::UpdateInfo`, `FsView::GetUnbalancedGroups`, and `FsBalancer::GetRandomIter`.

## Control flow
Tests populate trees and maps, assert duplicate rejection and iterator boundary behavior, directly inject `FsNode` pointers into `mNodeView` to verify reset deletes nodes, parse realistic filesystem config strings, relocate filesystem queue/path entries, and build synthetic balancing groups to validate unbalanced group counts under threshold changes.

## State and persistence
State is local test data plus static `InstanceName` and `FsNode::sNumInstances`. Config parsing outputs are transient but model persisted MGM configuration entries.

## Dependencies and integration points
Depends on Google Test/Mock, FsView, balancer classes included under `IN_TEST_HARNESS`, filesystem UUID mapper, config parsing, and string utilities.

## Risks and test signals
The reset leak regression is a strong lifecycle signal. Risks include direct access to internals, manual deletion of synthetic groups, and random iterator tests that cannot guarantee full distribution. Additional tests should cover concurrent FsView reset and malformed config strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/FsViewTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/FsckEntryTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/FsckEntryTests.cc

## Purpose
Tests MGM fsck entry repair logic for metadata/checksum/size mismatches and replica-set inconsistencies. It validates when repairs mutate MGM metadata, when repair jobs are launched, and when repair fails.

## Important APIs, types, and functions
The fixture constructs `eos::mgm::FsckEntry`, populates MGM `FileMdProto` and FST `FmdBase` metadata, and replaces `mRepairFactory` with a `MockRepairJob`. Tests exercise `FsckEntry::Repair()` across `FsckErr` values including `MgmXsDiff`, `MgmSzDiff`, `FstSzDiff`, `FstXsDiff`, `UnregRepl`, `DiffRepl`, and `MissRepl`.

## Control flow
Setup creates a two-replica file with matching MGM/FST size and checksum. Each test corrupts one dimension, marks an error type, calls `Repair()`, and asserts metadata correction, failure, replica removal/addition, or mock repair-job invocation. Replica tests model unregistered, over-replicated, under-replicated, and missing-on-disk states.

## State and persistence
State is in-memory proto metadata and maps of FST file info. Production equivalents are durable namespace metadata and physical replica records.

## Dependencies and integration points
Depends on Google Test/Mock, layout id helpers, fsck repair internals, string checksum conversion, and FST file metadata structures.

## Risks and test signals
This is a high-value repair oracle. Risks include access to internals under `IN_TEST_HARNESS`, mock factory always reusing one job, and limited layout/checksum variety. Additional tests should cover erasure-coded layouts, excluded source/destination sets, no-contact combinations, and failed repair-job statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/FsckEntryTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/FusexCastBatchTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/FusexCastBatchTests.cc

## Purpose
Tests basic batching and execution of deferred FUSEX cast callbacks. It verifies callback registration count and execution behavior for captured-by-value and captured-by-reference lambdas.

## Important APIs, types, and functions
The test uses `eos::mgm::FusexCastBatch::Register`, `GetSize`, and `Execute`.

## Control flow
It first registers two mutable lambdas that capture `value` by copy, executes them, and asserts the outer value is unchanged. It then registers three reference-capturing lambdas, executes them, and asserts the accumulated side effect is six.

## State and persistence
State is the batch's in-memory callback list. The test implies `Execute()` clears or replaces previous callbacks because `GetSize()` after the second registration sequence is expected to be three rather than five.

## Dependencies and integration points
Depends on Google Test and MGM FUSE server cast batching. It supports FUSEX notification batching paths.

## Risks and test signals
The test covers basic semantics but not exception behavior, execution order, callback removal, repeated `Execute()`, or thread safety. Those areas matter if batches are used across asynchronous FUSE broadcast paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/FusexCastBatchTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/HttpTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/HttpTests.cc

## Purpose
Tests HTTP client distinguished-name normalization in the MGM HTTP server. It verifies that old slash-separated and newer comma-separated certificate DN formats converge to the canonical slash-separated form.

## Important APIs, types, and functions
The test includes `mgm/http/HttpServer.hh` under `IN_TEST_HARNESS` and calls `eos::mgm::HttpServer::ProcessClientDN()`.

## Control flow
It constructs an `HttpServer`, passes an already canonical DN, then passes a reversed comma-separated DN, and asserts both produce the same canonical string.

## State and persistence
No persistent state is involved. DN normalization affects request identity presentation and authorization/accounting inputs.

## Dependencies and integration points
Depends on Google Test and MGM HTTP server internals. It integrates with TLS/X.509 client identity handling.

## Risks and test signals
The test protects one common DN shape but not escaping, commas inside attribute values, whitespace, lowercase attribute names, multi-valued RDNs, or malformed DNs. Because identity strings feed authorization, parser hardening tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/HttpTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/IdTrackerTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/IdTrackerTests.cc

## Purpose
Tests `IdTrackerWithValidity`, a time-based tracker for MGM ids such as drain candidates. It verifies insertion, lookup, expiration, removal, custom validity, and clearing.

## Important APIs, types, and functions
The test uses `IdTrackerWithValidity<uint64_t>`, `TrackerType::Drain`, `GetClock`, `AddEntry`, `HasEntry`, `DoCleanup`, `RemoveEntry`, and `Clear`.

## Control flow
It constructs a tracker with fake-clock mode, inserts ids at five-second intervals, advances time to expire the first and then all entries, removes an explicit entry, adds entries with custom expiration times based on the id, and clears all tracker state.

## State and persistence
State is in-memory id-to-expiration tracking. No durable state is written. The fake clock makes expiration deterministic.

## Dependencies and integration points
Depends on Google Test and MGM misc id tracker code. It integrates with background MGM workflows that need temporary suppression or validity windows.

## Risks and test signals
Good signals exist for cleanup boundaries. Missing coverage includes multiple `TrackerType` namespaces, duplicate inserts, non-fake real clock behavior, and concurrent access if the tracker is shared across threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/IdTrackerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/IostatTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/IostatTests.cc

## Purpose
Tests MGM IO statistics collection configuration, UDP popularity target encoding, rolling transfer-period buffers, percentile transfer duration calculation, and sequential transfer accounting.

## Important APIs, types, and functions
Coverage includes `Iostat`, `StartCollection`, `StopCollection`, `StoreIostatConfig`, `ApplyConfig`, `AddUdpTarget`, `RemoveUdpTarget`, `EncodeUdpPopularityTargets`, and `IostatPeriods` methods such as `Add`, `GetDataInPeriod`, `StampBufferZero`, `UpdateTransferSampleInfo`, `GetTimeToPercComplete`, `GetLongestTransferTime`, and `GetTotalSum`.

## Control flow
Fixture tests verify initial config keys, start/stop state, mock FsView config storage/application, and UDP target list mutation. Period tests add long transfers, query many rolling windows, stamp bins to zero, test integer and fractional per-bin accumulation, update percentile summaries, and generate random sequential transfers.

## State and persistence
`Iostat` stores in-memory running/config state and persists config through `FsView` global config in production. `IostatPeriods` maintains rolling time-bin buffers and percentile summaries.

## Dependencies and integration points
Depends on Google Test, MGM iostat internals, FsView, maps, and common random utilities. It feeds MGM monitoring/reporting and popularity logic.

## Risks and test signals
The period test is broad but loop-heavy. Random sequential transfer lengths introduce slight nondeterminism. Important risks include off-by-one bin boundaries, ceil rounding, config key drift, and UDP target serialization compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/IostatTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/LRUTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/LRUTests.cc

## Purpose
Tests parsing of MGM LRU expiration policies. These policies combine filename patterns, age thresholds, and optional size comparisons for cleanup decisions.

## Important APIs, types, and functions
The tests cover `LRU::parseExpireMatchPolicy`, `LRU::extractTimeSizeCriterias`, `LRU::parseExpireSizeMatchPolicy`, and `LRU::PolicyRule` equality. Units include days, weeks, and months, and size suffixes include SI-style K/M/G values.

## Control flow
Single and multiple pattern tests parse simple `pattern:age` rules. Time/size extraction tests validate empty/invalid strings, plain seconds, month age, greater-than and less-than size filters. Full policy tests iterate expected valid strings and invalid strings.

## State and persistence
State is parsed into maps or ordered policy-rule vectors. Production policy strings are persisted as namespace/MGM configuration values.

## Dependencies and integration points
Depends on Google Test and `mgm/lru/LRU.hh`. It integrates with LRU cleanup and policy enforcement code.

## Risks and test signals
Tests protect grammar and rule ordering, including trailing/duplicate commas. Risks include unit interpretation (`1mo` fixed at 31 days), SI vs binary size assumptions, wildcard matching semantics not covered here, and missing tests for huge values or whitespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/LRUTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/LockTrackerTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/LockTrackerTests.cc

## Purpose
Tests MGM FUSE byte-range lock tracking. It validates range overlap math, range subtraction, lock coalescing by pid, lock-set conflict detection, and POSIX-style read/write/unlock behavior through `flock` inputs.

## Important APIs, types, and functions
Coverage includes `ByteRange::overlap`, `overlapOrTouch`, `absorb`, `contains`, `minus`; `Lock::absorb`; `LockSet::add`, `remove`, `overlap`, `conflict`, `nlocks`; and `LockTracker::setlk`.

## Control flow
Byte-range tests enumerate touching, infinite-length, middle/start/end subtraction, and whole-range removal cases. Lock-set tests add overlapping locks from different pids, remove subranges, and verify conflicts. `LockTracker` tests model write lock acquisition, failed competing lock, unlock splitting, read-lock conversion, shared read locks, and write upgrade when only one reader remains.

## State and persistence
State is in-memory lock ranges keyed by owners/pids. No persistence is involved, but correctness affects live FUSE file locking semantics.

## Dependencies and integration points
Depends on Google Test, `mgm/fuse-locks/LockTracker.hh`, and POSIX `fcntl.h` lock constants.

## Risks and test signals
The test suite is strong for boundary arithmetic. Risks include integer overflow on large offsets, owner-string semantics, process death cleanup, and multithreaded access not covered by these single-threaded tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/LockTrackerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/PolicyTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/PolicyTests.cc

## Purpose
Tests MGM policy key construction for read/write traffic policy lookups. It ensures user, group, app, and generic policy keys are generated in the expected priority/order.

## Important APIs, types, and functions
The tests cover `Policy::GetConfigKeys`, `Policy::RWParams`, `RWParams::getKey`, and `RWParams::getKeys`. Constants such as `Policy::gBasePolicyKeys` and read/write markers `:r`/`:w` are verified.

## Control flow
Tests construct `RWParams` with user/group/app and write/read booleans, assert individual derived keys, and verify ordered lookup keys for a base policy such as `policy:bandwidth`.

## State and persistence
No mutable state is kept. The generated keys address MGM configuration entries, so formatting and ordering are compatibility-sensitive.

## Dependencies and integration points
Depends on Google Test, `mgm/policy/Policy.hh`, and MGM constants. It integrates with policy lookup for bandwidth and likely other per-user/group/app controls.

## Risks and test signals
The tests protect key spelling and lookup order. Missing coverage includes empty user/group/app combinations in `getKeys`, escaping of names containing separators, and interactions with real config maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/PolicyTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/ProcFsTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/ProcFsTests.cc

## Purpose
Tests classification helpers for MGM proc filesystem commands that operate on filesystems, scheduling groups, and spaces. It verifies entity type detection and move operation classification.

## Important APIs, types, and functions
The tests call `get_entity_type()` and `get_operation_type()` from `mgm/proc/proc_fs.hh`, expecting `EntityType::{FS,GROUP,SPACE,UNKNOWN}` and `MvOpType::{FS_2_GROUP,FS_2_SPACE,GRP_2_SPACE,SPC_2_SPACE,UNKNOWN}`.

## Control flow
Entity tests pass numeric fs ids, `space.group` strings, simple spaces, and malformed combinations. Move tests pass source/destination strings and verify only supported movement directions are classified.

## State and persistence
No state is modified. Classification results drive command behavior and error paths in proc_fs operations.

## Dependencies and integration points
Depends on Google Test, proc filesystem command helpers, and XRootD `XrdOucString` output/error buffers.

## Risks and test signals
The tests protect common grammar but not whitespace, negative ids, huge numeric ids, or names containing dots. Misclassification could move or configure the wrong scope, so parser edge coverage is important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/ProcFsTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/QuarkDBConfigTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/QuarkDBConfigTests.cc

## Purpose
Tests cleanup behavior in the QuarkDB-backed MGM configuration engine. It verifies when unused node configuration entries should or should not be removed.

## Important APIs, types, and functions
The test includes `QuarkDBConfigEngine` under `IN_TEST_HARNESS`, mutates `sConfigDefinitions`, sets `EOS_MGM_CONFIG_CLEANUP`, and calls `RemoveUnusedNodes()`.

## Control flow
It starts with empty and space-only config maps, then adds node status/stat entries. A node with status `on` is retained, a node with status `off` and no filesystems is removed, and a node with filesystem config entries is retained even if off. Extra space config entries do not trigger node removal.

## State and persistence
State is the in-memory config definition map, modeling QuarkDB-stored config keys. The test mutates process environment and unsets it at the end.

## Dependencies and integration points
Depends on Google Test and MGM QuarkDB config engine internals. It integrates with configuration maintenance and stale node cleanup.

## Risks and test signals
The test protects cleanup gating but mutates environment globally. Missing coverage includes multiple nodes, malformed fs keys, cleanup disabled behavior after unset, and verifying exact keys removed rather than only boolean return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/QuarkDBConfigTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/RecyclePolicyTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/RecyclePolicyTests.cc

## Purpose
Tests recycle-bin policy enforcement and configuration parsing. It validates watermark derivation from quota stats, within-limit checks, and accepted/rejected policy config values.

## Important APIs, types, and functions
The tests use a `MockRecyclePolicy` overriding `GetQuotaStats()` and `StoreConfig()`. Covered members include `RefreshWatermarks`, `IsWithinLimits`, `Config`, `mEnforced`, `mLowInodeWatermark`, `mLowSpaceWatermark`, `mSpaceKeepRatio`, `mKeepTimeSec`, `mCollectInterval`, `mRemoveInterval`, and `mDryRun`.

## Control flow
No-limit and quota-limit tests feed quota maps using `SpaceQuota` keys and assert derived low watermarks and limit status. Config tests toggle enforcement, keep time, ratio, collection/removal intervals, dry-run mode, invalid values, and reset behavior.

## State and persistence
State is in-memory atomic policy fields. `StoreConfig()` is mocked; production policy changes persist to MGM configuration.

## Dependencies and integration points
Depends on Google Test/Mock, recycle policy internals, quota key constants, and maps. It integrates with recycle cleanup scheduling and quota-aware retention.

## Risks and test signals
The tests cover important policy toggles. Risks include floating-point ratio comparisons, enforcement state interactions after invalid config, quota maps missing some keys, and mocked persistence hiding storage failures beyond `StoreConfig()` returning false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/RecyclePolicyTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/RecycleTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/RecycleTests.cc

## Purpose
Tests recycle-bin date cutoff calculation and recycled-path demangling. It verifies user-visible recycle cleanup date strings and conversion from mangled recycle names back to original paths.

## Important APIs, types, and functions
The tests use `Recycle`, its fake/test clock, `Recycle::GetCutOffDate()`, policy field `mKeepTimeSec`, and static `Recycle::DemanglePath()`.

## Control flow
The cutoff test advances the clock to a fixed September 2025 timestamp, sets keep times for six months, one month, and one week, and asserts expected `YYYY/MM/DD` strings. Demangle tests reject empty or slash-containing recycle names, and decode `#:#` separators plus trailing file ids into original paths.

## State and persistence
State is test-clock time and policy keep duration. Production recycle paths are persisted in recycle namespace layouts, so demangling compatibility matters.

## Dependencies and integration points
Depends on Google Test/Mock and recycle internals. It integrates with recycle cleanup and restore/listing behavior.

## Risks and test signals
Date math uses fixed month approximations from policy seconds, not calendar-month semantics. Tests should also cover timezone boundaries, leap days, malformed suffix ids, names containing literal `#`, and demangling of file vs directory names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/RecycleTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/RoutingTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/RoutingTests.cc

## Purpose
Tests MGM path routing and route endpoint parsing. It validates route registration/removal, protocol-specific rerouting ports, offline endpoint stall behavior, and path normalization for special `.`/`..` components.

## Important APIs, types, and functions
The tests use `RouteEndpoint::ParseFromString`, endpoint equality, `PathRouting::Add`, `Remove`, `Clear`, `Reroute`, `GetListing`, and status values `NOROUTING`, `REROUTE`, and `STALL`.

## Control flow
Construction tests reject malformed endpoint strings and duplicate route additions. Functionality tests add routes for `/eos/dirN/`, check no-route cases, reroute HTTP/HTTPS to the third endpoint field, reroute XRootD to the endpoint service port, handle multi-endpoint offline stall, then prefer an online master endpoint. Special-path tests assert longest-prefix routing after normalization of trailing `.`, embedded `.`, and `..`.

## State and persistence
State is an in-memory route table and endpoint online/master flags. Production route tables may be configured dynamically and affect client redirection.

## Dependencies and integration points
Depends on Google Test, route endpoint, path routing, and `VirtualIdentity` protocol fields.

## Risks and test signals
The tests protect parsing and normalization. Risks include endpoint health races, async update intervals disabled in tests, path traversal normalization surprises, and route ordering for overlapping prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/RoutingTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/TrafficShapingTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/TrafficShapingTests.cc

## Purpose
Tests the MGM traffic shaping engine and manager. Coverage spans config propagation, detail-level stats, report aggregation, policy persistence boundaries, garbage collection, reservation-controller decisions, delay calculation, ephemeral controller limits, and delay publication gates.

## Important APIs, types, and functions
The tests exercise `TrafficShapingEngine` methods for detail, limits, reservations, GC idle seconds, and active-node-rate threshold; `TrafficShapingManager` methods for report processing, estimator updates, policy loading/serialization, policy accessors, garbage collection, controller-limit expiration, reserved-app pressure, default reservation controller, delay calculation, and `ShouldEmitDelayForPolicy`. They also use `eos::traffic_shaping::FstIoReport` and `AppState`.

## Control flow
Engine tests apply config under FsView write lock and verify values propagate to the manager. Manager tests synthesize FST IO reports, update estimators, inspect global/disk/detailed/projection cardinality, load JSON policies, apply controller-only updates without persistence, and expire ephemeral limits after five minutes. Delay tests call pure calculation helpers across idle, above-limit, near-target, global-vs-node, and reference-rate cases. Reservation-controller tests mutate `AppState` vectors and assert when competitor limits are set or cleared.

## State and persistence
State includes in-memory policy maps, cumulative stats, EMA rates, controller-limit timestamps, reservation flags, and detail toggles. Persistent policy JSON is distinguished from ephemeral controller-only limits; serialization is expected to omit ephemeral-only updates.

## Dependencies and integration points
Depends on Google Test, traffic shaping internals under `IN_TEST_HARNESS`, FsView lock, common constants, and protobuf FST IO reports. It integrates MGM control-plane policy with FST rate/delay publication.

## Risks and test signals
This is a broad regression suite for new shaping behavior. Risks include floating-point tolerance, clock/timestamp expiry boundaries, JSON policy compatibility, stale controller limits, map cardinality leaks, and incorrect throttling under reservation pressure. Missing signals include multi-threaded report ingestion and full engine-to-FST publication integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/TrafficShapingTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsFileTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsFileTests.cc

## Purpose
Tests selected `XrdMgmOfsFile` helpers for open opaque parsing and client application-name selection. These helpers affect placement exclusions and policy/accounting labels for XRootD client operations.

## Important APIs, types, and functions
The tests cover `XrdMgmOfsFile::GetExcludedFsids()` and static `XrdMgmOfsFile::GetClientApplicationName(XrdOucEnv*, XrdSecEntity*)`. They use `XrdOucEnv`, `XrdSecEntity`, and entity attributes such as `xrd.appname`.

## Control flow
The excluded-fsid test creates open opaque data with `eos.excludefsid=2,4,6,8,10,144`, assigns it to a file object, and verifies all ids are parsed. The app-name test checks null inputs, no app tags, XRootD entity app tag fallback, and `eos.app` opaque override even without a client entity.

## State and persistence
State is per-file open opaque data and security entity attributes. No durable state is written, but parsed values influence runtime scheduling and traffic policy behavior.

## Dependencies and integration points
Depends on namespace file metadata, XRootD security/entity APIs, XrdOucEnv, MGM OFS file internals, and Google Test.

## Risks and test signals
Tests cover happy paths but not malformed fsid lists, duplicates, whitespace, nonnumeric entries, memory ownership of `openOpaque`, or precedence when both tags are empty/malformed. Exclusion parsing is placement-sensitive and should fail conservatively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsFileTests.cc -->

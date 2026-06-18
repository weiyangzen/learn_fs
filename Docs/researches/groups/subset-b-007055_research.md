# subset-b-007055 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Inspector.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Inspector.cc

## Purpose
This file implements the QuarkDB namespace inspector command backend. It talks directly to `qclient::QClient` and provides read-only scans, consistency checks, metadata dumps, and dangerous repair operations for EOS namespace state stored in QuarkDB. It is not part of the normal metadata service hot path; it is an administrative/debugging tool that bypasses high-level service abstractions and builds `RedisRequest` batches directly when repairs are requested.

## Important APIs, Types, and Functions
`Inspector::checkConnection()` validates QDB reachability with `PING`. `loadConfiguration()` reads `eos-config:default` and extracts valid filesystem ids from `fs:*` config entries for unknown-fsid scans. `scan()` and `dump()` use `NamespaceExplorer` to traverse reachable namespace paths from a root path. `scanDirs()`, `scanFileMetadata()`, and `scanDeathrow()` use `ContainerScanner` and `FileScanner` to scan raw metadata, including unreachable entries.

The consistency-check group includes `checkNamingConflicts()`, `checkCursedNames()`, `checkOrphans()`, `checkFsViewMissing()`, `checkFsViewExtra()`, `checkShadowDirectories()`, and `checkSimulatedHardlinks()`. Layout-focused scanners are `oneReplicaLayout()` and `stripediff()`. Repair and mutation APIs include `overwriteContainerMD()`, `fixDetachedParentContainer()`, `fixDetachedParentFile()`, `fixShadowFile()`, `dropFromDeathrow()`, `dropEmptyCid()`, `changeFid()`, `renameCid()`, and `renameFid()`. `printFileMD()` and `printContainerMD()` emit complete protobuf and map details for one object. `executeRequestBatch()` centralizes dry-run logging, QDB command execution, and cache invalidation notification.

Important helper types include `CacheNotifications`, `ExpansionTrim`, `ConflictSet`, `PendingFile`, `PendingContainer`, `FsViewItemExists`, `FsViewExpectInLocations`, `NextGuard`, `HardlinkInfo`, and `InodeUseCount`.

## Control Flow
Traversal commands construct scanner/explorer objects, loop while valid, fetch protobuf records, optionally resolve full paths, filter by user flags, and print through `OutputSink` or explicit streams. `scan()` uses `NamespaceExplorer` with a `folly::IOThreadPoolExecutor`, optional depth limit, and optional regex-based expansion trimming. `dump()` emits simple path/checksum/size/mtime rows and can query one xattr.

The checker flows compare independently stored indexes. Naming conflicts rely on scanners sorted by parent id and name, grouping files and containers by parent and entry name. Orphan checks enqueue asynchronous `doesContainerMdExist()` futures and drain them opportunistically. `checkFsViewMissing()` starts `SISMEMBER` checks for every file location and unlink location. `checkFsViewExtra()` iterates all `fsview:*:*` keys with `FileSystemIterator` and `StreamingFileListIterator`, then fetches each `FileMdProto` and verifies that its locations match the fsview set being scanned. Hardlink checking groups files by container, interpreting `sys.eos.mdino` as simulated hardlink pointers and `sys.eos.nlink` as expected use counts.

Repair functions first fetch and print current metadata, perform sanity checks, construct updated `QuarkFileMD` or `QuarkContainerMD` objects, build Redis requests with `RequestBuilder`, optionally delete old parent map entries, add new parent map entries, and call `executeRequestBatch()`. `executeRequestBatch()` prints all commands, builds cache invalidation publish requests for affected fids/cids, returns early for dry runs, otherwise submits all commands and prints raw Redis replies.

## State and Persistence Behavior
Read paths inspect QDB keys for file/container protobufs, parent file maps, parent container maps, fsview sets, orphan/deathrow conventions, and MGM config. Mutation paths persist by writing or deleting protobuf keys and by editing parent map hashes (`<cid>:files`, `<cid>:dirs`) directly. Some repair paths also notify cache invalidation for affected file or container ids. The tool deliberately does not coordinate through normal metadata locks, so its mutations can race with active MGM operations if used online.

The state model assumes duplicated namespace indexes must agree: a `FileMdProto` parent id should match a file-map entry, a `ContainerMdProto` parent id should match a container-map entry, file locations/unlink locations should match fsview membership, and every non-root parent id should exist. The code treats `cont_id == 0` as deathrow/unlinked file state and `parent_id == 0` as detached/special container state.

## Dependencies and Integration Points
The file depends on `NamespaceExplorer`, `ContainerScanner`, `FileScanner`, `OutputSink`, `Printing`, `FileMetadataFilter`, `MetadataFetcher`, `FileSystemIterator`, `StreamingFileListIterator`, `RequestBuilder`, `QuarkFileMD`, `QuarkContainerMD`, QuarkDB constants, EOS checksum/layout helpers, `InodeTranslator`, config parsing, regex utilities, JSON/protobuf utilities, and qclient reply descriptions. Operationally it integrates with admin commands that expose namespace inspection and repair operations.

## Risks and Test Signals
Risks are high because repair methods bypass normal service transactions. `changeFid()` currently calls `executeRequestBatch()` once without notifications and then again with notifications for the same write request, which can duplicate writes and should be checked before relying on it. Several helpers move futures and then store resolved values back into future variables; tests should cover repeated count/path access. `scanDeathrow()` breaks on the first non-deathrow file, so it relies on scanner ordering. `checkNamingConflicts()` calls `getItem()` after advancing without checking the return in inner loops, so scanner boundary behavior matters. `checkSimulatedHardlinks()` does not run the final `crossCheckHardlinkMaps()` after the loop, leaving the last container group at risk of being skipped.

Good test signals include mocked qclient scans for empty namespace, malformed replies, duplicate file/container names, missing and extra fsview entries, orphan parent ids, cursed names with non-printable bytes, hardlink xattr edge cases, dry-run repair command lists, cache notification lists, and repair refusal when destination paths are files or too close to root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Inspector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Inspector.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Inspector.hh

## Purpose
This header declares the administrative `Inspector` facade for direct QuarkDB namespace inspection and repair. It collects many operational commands behind one object that owns no QDB connection itself, but references a `qclient::QClient` and an `OutputSink`.

## Important APIs, Types, and Functions
`CacheNotifications` groups fids and cids whose metadata caches should be invalidated after direct writes. `Inspector` exposes connectivity, traversal, dump, scan, consistency-check, layout-check, print, repair, mutation, configuration, and metadata-filter methods. Public mutators include `overwriteContainerMD`, `fixDetachedParentContainer`, `fixDetachedParentFile`, `fixShadowFile`, `dropFromDeathrow`, `dropEmptyCid`, `changeFid`, `renameCid`, and `renameFid`.

Private state includes `mgmConfiguration`, `validFsIds`, `mQcl`, `mOutputSink`, and optional `mMetadataFilter`. Private helpers `isDestinationPathSane()` and `executeRequestBatch()` enforce minimal repair destination checks and centralize direct QDB write execution.

## Control Flow
Callers construct `Inspector(qclient::QClient&, OutputSink&)`, optionally call `checkConnection()` and `loadConfiguration()`, then invoke one command method. Methods return errno-like integers: `0` on success and nonzero for command-level failure. Output goes through the injected sink for most scanner commands, while some repair/check methods receive explicit `out` and `err` streams.

## State and Persistence Behavior
The header makes it clear that the inspector can write persistent namespace metadata directly. It stores configuration-derived fs ids for filtering and an optional file metadata filter for raw file scans. It does not own cache, service, or transaction state; persistent effects are delegated to implementation methods that issue Redis requests.

## Dependencies and Integration Points
The declaration depends on EOS namespace macros, `RequestBuilder` request types, container protobufs, qclient forward declarations, scanners, output sink, and file metadata filters. It integrates with command-line/admin layers that need a single API for namespace inspection.

## Risks and Test Signals
The broad API mixes safe reads with dangerous repairs, so callers need explicit dry-run defaults and clear privilege boundaries. Tests should verify each public method returns stable nonzero errors on bad input, that `setMetadataFilter()` ownership is unique and honored by file scans, and that dry-run mutation calls never execute QDB writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Inspector.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/OutputSink.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/OutputSink.cc

## Purpose
This file implements output formatting for inspector metadata rows. It converts file and container protobuf fields into string maps, augments rows with resolved paths or child counts, and provides stream, JSON array, and JSON-lines sink implementations.

## Important APIs, Types, and Functions
`populateMetadata(ContainerMdProto, ContainerPrintingOptions, map&)` emits cid, parent id, uid/gid, tree size, mode, flags, name, ctime, mtime, stime, and xattrs according to options. `populateMetadata(FileMdProto, FilePrintingOptions, map&)` emits fid, parent/container id, uid/gid, size, layout, flags, name, link name, ctime, mtime, checksum, locations, unlink locations, xattrs, stime, and atime. `populateFullPath()` waits on scanner-provided full-path futures and suppresses path output on exceptions. `countAsString()` waits on count futures and emits `N/A` on failure.

`OutputSink::print()` overloads dispatch protobufs to maps. `printWithCustomPath()` adds a supplied path. `printWithAdditionalFields()` merges caller-provided fields with file metadata. `StreamSink::print()` emits escaped `key=value` pairs. `JsonStreamSink` wraps records in one JSON array. `JsonLinedStreamSink` emits one compact JSON object per line and overrides JSON-value printing.

## Control Flow
The common flow is: create a `std::map`, populate selected metadata fields, optionally wait for async path/count futures, then call the virtual map `print()` method. Stream output iterates the map in key order. JSON array output prints an opening bracket at construction, inserts commas between records, and prints a closing bracket in the destructor. JSON-lines output uses `Json::StreamWriter` with empty indentation.

## State and Persistence Behavior
This file manages no persistent namespace state. It consumes protobuf state and scanner futures. Its main stateful behavior is output framing in `JsonStreamSink::mFirst` and the JSON-lines writer object. Moving scanner futures while resolving paths/counts means the associated scanner item should not be reused for another path/count read afterward.

## Dependencies and Integration Points
It depends on `FileScanner::Item`, `ContainerScanner::Item`, `Printing`, EOS checksum serialization, protobuf types, folly futures, and jsoncpp. It is the formatting layer used by `Inspector` scans and layout checks.

## Risks and Test Signals
There are option-gating mistakes worth testing: container `flags` is guarded by `showMode`, and file `unlink_locations` is guarded by `showLocations` rather than `showUnlinkLocations`. Futures are waited synchronously, so slow path resolution or count queries can stall output. Tests should cover escaping, JSON array destructor framing, JSON-lines custom JSON values, failed path futures, failed count futures, all print option combinations, and deterministic key ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/OutputSink.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/OutputSink.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/OutputSink.hh

## Purpose
This header defines the abstract inspector output interface and concrete stream-oriented sinks. It separates inspector command logic from textual and JSON formatting.

## Important APIs, Types, and Functions
`OutputSink` stores `mOut` and `mErr` references, requires subclasses to implement `print(const std::map<std::string,std::string>&)`, and provides default string, JSON, error, file-protobuf, and container-protobuf print overloads. `StreamSink` prints key-value records. `JsonStreamSink` prints one JSON array over its lifetime. `JsonLinedStreamSink` prints newline-delimited JSON and overrides direct `Json::Value` printing.

## Control Flow
Inspectors call a high-level `print()` overload with protobufs or maps. The base class builds map rows in the implementation file and calls the virtual map function. Direct string output is escaped and newline-terminated. Direct JSON output defaults to jsoncpp stream formatting unless overridden by JSON-lines.

## State and Persistence Behavior
The header owns no namespace state. It defines output stream references and, for JSON sinks, framing/writer state. Because `JsonStreamSink` closes the JSON array in its destructor, object lifetime is part of the emitted format contract.

## Dependencies and Integration Points
It includes scanners, printing options, protobuf declarations, jsoncpp, and EOS namespace macros. It is injected into `Inspector`, allowing command code to stay independent of output format.

## Risks and Test Signals
Subclasses must be kept alive until all output is complete, especially `JsonStreamSink`. Tests should verify polymorphic dispatch for map rows, default string escaping, direct JSON printing behavior for both JSON sink types, and valid array output when zero or many records are printed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/OutputSink.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Printing.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Printing.cc

## Purpose
This file implements reusable formatting helpers for namespace file and container protobufs. It is used by inspector commands that need full multi-line diagnostic output rather than compact key-value rows.

## Important APIs, Types, and Functions
`Printing::escapeNonPrintable()` turns non-printable bytes into `\xNN` sequences and handles NUL as `\x00`. `timespecToTimestamp()` formats seconds and nanoseconds as `sec.nsec`. `timespecToFileinfo()` combines `ctime_r()` output with the timestamp form. `printMultiline(ContainerMdProto)` prints ids, name, ownership, ctime/mtime/stime, tree size, mode, flags, and xattrs. `printMultiline(FileMdProto)` prints ids, name/link, ownership, size, times, octal flags, checksum, expected stripes, ETag, locations, unlink locations, and xattrs.

## Control Flow
The functions are direct serializers. Protobuf byte fields containing `timespec` are parsed by `Printing::parseTimespec()` from the header. File checksum strings are generated with `appendChecksumOnStringProtobuf()`, expected stripe count comes from `LayoutId::GetStripeNumber() + 1`, and ETags come from `calculateEtag()`.

## State and Persistence Behavior
No state is persisted or cached. The code only observes protobuf fields. It assumes serialized time byte strings are either empty or large enough to hold `struct timespec`; that assumption comes from the metadata serialization contract.

## Dependencies and Integration Points
It depends on layout id helpers, checksum helpers, ETag generation, string conversion, file metadata interfaces, and protobuf types. It is used by `Inspector` repair previews and per-object print commands.

## Risks and Test Signals
`parseTimespec()` copies `sizeof(timespec)` whenever the field is non-empty, so malformed short time fields could cause out-of-bounds reads. `timespecToFileinfo()` seeks back one byte after `ctime_r()` to remove the newline; stream state should be tested. Tests should cover empty and valid time fields, non-printable names/xattrs, checksum rendering, ETag rendering, octal flags, and location vector formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Printing.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Printing.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Printing.hh

## Purpose
This header declares formatting options and helper methods for inspector metadata output. It defines which fields are shown by default for file and container records and exposes static formatting functions.

## Important APIs, Types, and Functions
`FilePrintingOptions` contains booleans for id, parent/container id, uid/gid, size, layout id, flags, name, link name, ctime, mtime, checksum, locations, unlink locations, xattrs, stime, and atime. `ContainerPrintingOptions` controls id, parent, uid/gid, tree size, mode, flags, name, ctime, mtime, stime, and xattrs. `Printing` declares multi-line file/container print methods, time conversion methods, `escapeNonPrintable()`, and templated `parseTimespec()`.

## Control Flow
The header has no complex runtime flow. `parseTimespec()` conditionally copies raw bytes into a local `timespec` and returns it; all other behavior is implemented in `Printing.cc`.

## State and Persistence Behavior
No state is stored. The option structs are value configuration objects for output functions. The time parser reflects the persistent metadata encoding of timestamps as raw `timespec` bytes in protobuf fields.

## Dependencies and Integration Points
It includes EOS namespace macros plus file and container protobuf headers. It is consumed by `OutputSink`, `Inspector`, and any code needing inspector-compatible metadata formatting.

## Risks and Test Signals
The raw-byte timestamp parser needs tests for empty and correctly sized fields. Option defaults should be snapshot-tested because inspector CLI output depends on them. Compile tests should ensure the header can be included without pulling scanner or qclient dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Printing.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/ContainerMDSvc.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/ContainerMDSvc.cc

## Purpose
This file implements `QuarkContainerMDSvc`, the EOS `IContainerMDSvc` backend backed by QuarkDB. It creates, fetches, updates, removes, counts, and notifies changes for container metadata objects while delegating asynchronous retrieval and caching to `MetadataProvider`.

## Important APIs, Types, and Functions
The constructor stores non-owning qclient/flusher pointers and initializes counters. `configure()` initializes the metainfo hash and applies container cache size when available. `initialize()` validates dependencies, applies delayed cache sizing, runs `SafetyCheck()`, and loads `mNumConts` using `RequestBuilder::getNumberOfContainers()`. `SafetyCheck()` probes sparse ids above the first free id and aborts if any container exists beyond the recorded maximum.

`getContainerMDFut()` rejects container id 0 and delegates to `mMetadataProvider->retrieveContainerMD()`. `getContainerMD()` blocks on the future and optionally returns the metadata clock. `createContainer()` reserves or blacklists an inode id, constructs `QuarkContainerMD`, increments the count, and inserts it into the metadata cache. `updateStore()` writes the container protobuf through `MetadataFlusher` unless the name is empty. `removeContainer()` refuses non-empty containers, deletes the protobuf, removes the meta map for root deletion, tombstones the object, and decrements the counter. `getLostFound()` and `getLostFoundContainer()` lazily create recovery containers. Listener, cache-stat, and blacklist methods implement the interface glue.

## Control Flow
Service setup is two-phase: file service configuration creates the shared `MetadataProvider` and inode provider, then container service `initialize()` verifies both pointers before use. Normal reads go through the cache-backed provider. Creates allocate ids before constructing in-memory objects and cache them immediately. Updates and deletes are asynchronous flusher submissions. Lost+found lookup first tries root id 1, creates root if missing, then finds or creates child containers by name.

## State and Persistence Behavior
Persistent state lives in QuarkDB container protobuf keys, parent maps maintained by `QuarkContainerMD` operations, and the namespace meta hash. The service maintains an atomic container count from QuarkDB's count request and updates it on create/delete. It also uses the shared `UnifiedInodeProvider` for first-free id state and blacklist handling. Deletions mark in-memory objects as deleted tombstones so cache consumers can see ENOENT behavior.

## Dependencies and Integration Points
It depends on `MetadataFetcher`, `QuarkContainerMD`, `QuarkFileMD`, `MetadataProvider`, `RequestBuilder`, `ConfigurationParser`, `MetadataFlusher`, namespace interfaces, logging, stacktraces, and inode providers. It integrates with `QuarkFileMDSvc`, quota stats, container change listeners, and cache-stat reporting.

## Risks and Test Signals
`createInParent()` increments `mNumConts` even though `createContainer()` already increments it, so container counts can be double-incremented for that path. Empty-name updates currently log and return instead of throwing, which can silently drop persistence. `SafetyCheck()` samples only selected offsets, so it is a guard rather than a proof. Tests should cover initialization dependency errors, id 0 lookup, explicit-id blacklist, lost+found creation, empty container deletion refusal, root deletion meta-map cleanup, cache insertion/tombstone behavior, and counter correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/ContainerMDSvc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/ContainerMDSvc.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/ContainerMDSvc.hh

## Purpose
This header declares the QuarkDB implementation of the EOS container metadata service. It adapts `IContainerMDSvc` to QuarkDB persistence, cache-backed retrieval, inode allocation, quota integration, and listener notification.

## Important APIs, Types, and Functions
`QuarkContainerMDSvc` overrides lifecycle, retrieval, creation, update, deletion, counting, listener, lost+found, cache-stat, and id-blacklist methods. It exposes setters for file metadata service, metadata provider, inode provider, and quota stats. `getContainerMDFut()` is the asynchronous API; `getContainerMD()` is the blocking interface-compatible wrapper. `createInParent()` and `getLostFoundContainer()` are higher-level convenience methods.

Private state includes listener list, quota stats pointer, file service pointer, qclient pointer, flusher pointer, metadata hash, provider pointer, unified inode provider pointer, atomic container count, and delayed cache-size string. `SafetyCheck()` and `notifyListeners()` are private implementation hooks.

## Control Flow
Callers must wire `setFileMDService()`, `setMetadataProvider()`, and `setInodeProvider()` before `initialize()`. The file metadata service is responsible for creating and sharing the metadata provider and inode provider. After initialization, normal interface calls use the provider and flusher.

## State and Persistence Behavior
The class represents persistent container metadata but stores only service-local counters and pointers. QuarkDB persistence is performed by implementation methods using request builders and flusher. Cache capacity configuration can be received before the provider pointer exists and applied later from `mCacheNum`.

## Dependencies and Integration Points
It includes container interfaces, QuarkDB constants, quota stats, metadata flusher, inode providers, and qclient hash structures. It is a friend of `QuarkContainerMD`, allowing metadata objects to call service internals as needed.

## Risks and Test Signals
The class relies on non-owning raw pointers, so initialization order and lifetime are critical. Tests should verify failures when dependencies are missing, delayed cache configuration, listener notification ordering, and that service methods do not dereference unset provider/inode pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/ContainerMDSvc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileMDSvc.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileMDSvc.cc

## Purpose
This file implements `QuarkFileMDSvc`, the QuarkDB-backed EOS file metadata service. It manages file metadata retrieval, creation, update, deletion, cache integration, listener notification, and shared setup of the metadata provider and unified inode provider.

## Important APIs, Types, and Functions
`configure()` parses QDB contact details when `qdb_flusher_md` is present, configures the meta hash and inode provider, creates `MetadataProvider`, and injects it plus the inode provider into `QuarkContainerMDSvc`. It can refresh inode state and set file cache size. `initialize()` checks the container service and qclient/flusher, runs `SafetyCheck()`, and initializes `mNumFiles`.

`SafetyCheck()` probes sparse ids above `getFirstFreeId()` using `MetadataFetcher::getFileFromId()`. `getFileMDFut()` and `getFileMD()` retrieve through `MetadataProvider`. `hasFileMD()` checks existence. `createFile()` reserves or blacklists ids, constructs `QuarkFileMD`, inserts it into cache, emits a Created event, and increments count. `updateStore()` writes the file protobuf and adds detached files (`cont_id == 0`) to the orphan set. `removeFile()` deletes the protobuf, removes the orphan-set entry, emits a Deleted event, tombstones the object, and decrements count. `setContMDService()` enforces the concrete Quark container service type.

## Control Flow
The file service is the owner of `MetadataProvider`; provider construction creates its own qclients and shards. During configuration it wires the provider and inode provider into the container service. Normal reads return futures or block on them. Creates notify listeners before persistence, while updates and deletes enqueue writes through the flusher. The destructor synchronizes the flusher if present.

## State and Persistence Behavior
Persistent state includes file protobufs, namespace metainfo, max inode values, and the orphan file set. In-memory state includes listener list, quota pointer, container service pointer, flusher/qclient pointers, metainfo hash, atomic count, metadata provider, and unified inode provider. Newly created or fetched metadata objects are cached in `MetadataProvider`; removed objects are marked deleted to act as cache tombstones.

## Dependencies and Integration Points
It depends on QuarkDB configuration parsing, constants, `QuarkFileMD`, `QdbContactDetails`, quota stats, metadata flusher, container service, metadata fetcher/provider, request builder, and string conversion. It implements `IFileMDSvc` for the namespace stack and coordinates with `QuarkContainerMDSvc`.

## Risks and Test Signals
`configure()` assumes `pContSvc` is already set and that it is a `QuarkContainerMDSvc`; misordered configuration can crash or throw. File cache size updates assume `mMetadataProvider` already exists. Empty-name updates log and return, risking silent lost writes. Creates notify listeners before durable write. Tests should cover configuration ordering, explicit-id blacklist, first-free id refresh, missing dependency errors, orphan-set updates, listener events, tombstone behavior, cache stats, and safety-check failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileMDSvc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileMDSvc.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileMDSvc.hh

## Purpose
This header declares the QuarkDB implementation of `IFileMDSvc`. It is the service facade used by EOS namespace code to access file metadata while hiding QuarkDB persistence and cache-provider details.

## Important APIs, Types, and Functions
`QuarkFileMDSvc` overrides lifecycle, asynchronous and blocking file retrieval, existence checks, cache dropping, creation, update, deletion, counting, listener notification, container-service wiring, quota stats wiring, visitor hook, id retrieval, cache stats, id blacklist, and provider access. `sFlushInterval` is declared as the backend flush interval. Private `SafetyCheck()` verifies recorded max file id consistency at startup.

Private state includes listener list, quota stats pointer, container service pointer, metadata flusher pointer, qclient pointer, metainfo hash, atomic file count, owning `MetadataProvider`, and `UnifiedInodeProvider`.

## Control Flow
Clients must set the container service before configuration creates the provider and before initialization. After setup, interface calls use the metadata provider for cached reads and the flusher/request builder for persistence.

## State and Persistence Behavior
The class is the service-level owner of file metadata cache/provider state and unified inode allocation state. It does not store file metadata itself except through provider caches; durable state remains in QuarkDB.

## Dependencies and Integration Points
It includes `IFileMDSvc`, inode providers, qclient hash structures, and forward declarations for quota, flusher, and metadata provider. It integrates with `QuarkContainerMDSvc`, metadata listeners, and namespace accounting/quota views.

## Risks and Test Signals
Raw non-owning pointers make lifecycle tests important. `visit()` is a no-op, so callers expecting visitor traversal need separate coverage. Tests should verify that `getMetadataProvider()` is null before configuration and valid after configuration, and that all interface methods fail predictably when called too early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileMDSvc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileSystemIterator.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileSystemIterator.cc

## Purpose
This file implements a small iterator over QuarkDB fsview keys. It discovers filesystem ids represented by keys matching `fsview:*:*` and classifies each key as the normal file view or unlinked-file view.

## Important APIs, Types, and Functions
The constructor initializes `qclient::QScanner` with pattern `fsview:*:*` and advances until it finds a parseable key. `getFileSystemID()`, `getRedisKey()`, `isUnlinked()`, and `valid()` expose parsed state. `next()` advances and skips malformed keys. `parseScannerKey()` logs malformed keys, while `rawParseScannerKey()` splits the key on `:` and accepts only `fsview:<id>:files` or `fsview:<id>:unlinked`.

## Control Flow
Iteration is scanner-driven. Both construction and `next()` loop until either the scanner is invalid or the current key parses. Parse failures are logged as critical and skipped.

## State and Persistence Behavior
The iterator stores the current raw Redis key, parsed filesystem id, and unlinked flag. It does not modify QuarkDB; it observes fsview set keys that are maintained elsewhere by namespace accounting.

## Dependencies and Integration Points
It depends on `QScanner`, `StringTokenizer`, logging, and file metadata location types. `Inspector::checkFsViewExtra()` uses it to scan every filesystem view and compare set membership against file metadata locations.

## Risks and Test Signals
`std::stoull(parts[1])` can throw on malformed numeric fields, and `parseScannerKey()` does not catch it. Tests should cover valid `files` and `unlinked` keys, bad prefixes, wrong part counts, bad suffixes, nonnumeric ids, skip behavior, and raw key reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileSystemIterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileSystemIterator.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileSystemIterator.hh

## Purpose
This header declares `FileSystemIterator`, an iterator abstraction for fsview keys in QuarkDB. It lets callers enumerate known filesystem views without exposing qclient scanner parsing details.

## Important APIs, Types, and Functions
The constructor takes a `qclient::QClient&`. Public methods return the parsed filesystem id, whether the current key is an unlinked view, the raw Redis key, validity, and advance operation. Private parsing methods split and validate scanner keys.

## Control Flow
The class follows a simple valid/current/next iterator model. Construction positions the iterator at the first valid fsview key, and `next()` moves to the next valid key.

## State and Persistence Behavior
It stores only scanner state and the parsed current key. It has no persistence behavior and no ownership of the qclient.

## Dependencies and Integration Points
It includes EOS namespace macros, `IFileMD` for location type, and `QScanner`. It is a utility for fsview consistency checks and any code that needs raw fsview set keys.

## Risks and Test Signals
The API exposes parsed values only when `valid()` is true; callers should not read them after invalidation. Tests should verify constructor skip behavior and that `getRedisKey()` remains aligned with the parsed id/unlinked state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileSystemIterator.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataFetcher.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataFetcher.cc

## Purpose
This file implements stateless, no-cache metadata retrieval helpers for QuarkDB. It fetches file/container protobufs, parent maps, id lookups, fsview membership, full-path resolution, reverse path resolution, and directory content counts. Higher-level services and inspectors use it as the direct backend access layer.

## Important APIs, Types, and Functions
Reply validators `ensureStringReply()`, `ensureBoolReply()`, and `ensureUInt64Reply()` normalize Redis reply errors into `MDStatus`. `MapFetcher<Trait>` is a self-deleting qclient callback that HSCANs a container file map or container map in batches (`COUNT 250000`) and fulfills a `folly::Promise` with `IContainerMD::FileMap` or `ContainerMap`.

`getFileFromId()` and `getContainerFromId()` fetch protobufs and deserialize them. `doesFileMdExist()` and `doesContainerMdExist()` distinguish ENOENT from backend/deserialization errors. `getFileMap()` and `getContainerMap()` create map fetchers. `getFilesFromFilemap()` and `getContainersFromContainerMap()` sort by name before issuing metadata fetches. `getFileIDFromName()` and `getContainerIDFromName()` read parent hashes and deserialize ids. Name-based protobuf fetchers chain id lookup and id fetch. `locationExistsInFsView()` checks `SISMEMBER` in `fsview:<location>:files` or `fsview:<location>:unlinked`. `resolveFullPath()` uses `FullPathResolver`; `resolvePathToID()` uses `ReversePathResolver`; `countContents()` issues two `HLEN` calls.

## Control Flow
Most methods return futures by chaining `qcl.follyExec()` with parsing callbacks. `MapFetcher` starts an HSCAN, validates the two-element cursor/result reply, inserts filename/id pairs into a sparse-hash-style map, recursively issues the next HSCAN until cursor `0`, then sets the promise and deletes itself. Its comments correctly note that members must not be accessed after `execCB()` because the callback may already have completed and deleted the object.

`FullPathResolver` walks parent containers by repeatedly reading container protobufs and pushing names to the front of a deque until parent id 1, then emits a slash-terminated path. It short-circuits container id 1 to `/`. `ReversePathResolver` tokenizes a path, starts at container id 1, resolves each component as a container, and if resolving the final component as a container fails it tries a file lookup. It self-deletes after setting a value or exception.

## State and Persistence Behavior
The fetcher does not mutate persistent state. It reads protobuf keys, parent map hashes, fsview sets, and hash lengths. It constructs transient protobufs, maps, and futures. Its returned map contents represent persistent parent index state at scan time, not an atomic snapshot across multiple HSCAN batches or chained fetches.

## Dependencies and Integration Points
It depends on namespace interfaces, QuarkDB services, serialization, request builders, path processing, qclient async APIs, folly futures/promises, Redis reply types, and QuarkDB constants. It is used by `MetadataProviderShard` for cache misses, by `Inspector` for direct checks/repairs, and by scanner/explorer code for path and child metadata resolution.

## Risks and Test Signals
The self-deleting callback/resolver pattern is fragile: every error and success path must set exactly one promise outcome and then delete once. HSCAN does not provide an atomic view if parent maps change mid-scan. `FullPathResolver` does not guard against cycles or parent id 0 beyond eventual fetch failure, so detached/cyclic containers can hang or fail late. `ReversePathResolver` intentionally lacks symlink support. Tests should cover nil, empty, wrong-type, and malformed Redis replies; multi-batch HSCAN; deserialization errors; missing final path component as file vs container; root path resolution; detached parent errors; fsview boolean validation; and count reply validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataFetcher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataFetcher.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataFetcher.hh

## Purpose
This header declares `MetadataFetcher`, a static utility class for direct QuarkDB metadata reads without caching. It exposes future-returning APIs for file/container protobufs, parent maps, path resolution, fsview membership, and content counts.

## Important APIs, Types, and Functions
The API includes `getFileFromId`, `getContainerFromId`, existence checks, file/container map fetches, map-to-metadata fetch expansion, fetches by parent/name, path-to-id and container full-path resolution, fsview membership checks, and `countContents()`. Private helpers construct parent hash keys for files and subcontainers.

## Control Flow
All public methods are static and either return a `folly::Future`, a vector of futures, or a pair of futures. Callers compose or block on these futures depending on their own threading model.

## State and Persistence Behavior
The class stores no state and performs no writes. It reads durable QuarkDB namespace structures and returns protobuf/map snapshots from the time of query.

## Dependencies and Integration Points
It includes identifier types, metadata interfaces, namespace macros, file/container protobufs, `std::future`, and folly futures. It is the low-level read layer for both cache-backed services and the inspector.

## Risks and Test Signals
Because the class returns many independent futures, callers need to handle partial failures explicitly. Tests should verify API behavior for missing ids, missing names, bad maps, detached paths, root path, file-vs-container final component, and fsview membership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataFetcher.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProvider.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProvider.cc

## Purpose
This file implements the sharded, cache-backed metadata provider used by QuarkDB file and container services. It distributes metadata ids over 16 shards, each with its own qclient and `MetadataProviderShard`, and aggregates cache controls/statistics.

## Important APIs, Types, and Functions
The constructor creates a `folly::IOThreadPoolExecutor(16)`, then builds `kShards` qclients from `QdbContactDetails` and one shard per qclient. `retrieveContainerMD()`, `retrieveFileMD()`, cache drops, existence checks, and cache insertions delegate to `pickShard(id)`. `setFileMDCacheNum()` and `setContainerMDCacheNum()` divide global capacity by shard count, preserving `UINT64_MAX` as unlimited. `aggregateStatistics()` sums cache stats. `getFileMDCacheStats()` and `getContainerMDCacheStats()` aggregate shard stats and mark the result enabled. `pickShard()` uses id modulo `kShards`.

## Control Flow
The provider is a thin dispatcher. Every operation computes the target shard from the id and forwards. Cache size changes iterate all shards. Statistics iterate all shards and sum their counters.

## State and Persistence Behavior
The provider owns the executor, qclients, and shards. It does not persist metadata directly; shards fetch from QuarkDB and cache objects. Member declaration order intentionally keeps the executor before qclients so continuations cannot outlive their executor during destruction.

## Dependencies and Integration Points
It depends on `MetadataProviderShard`, `QdbContactDetails`, qclient construction options, and folly executors. It is owned by `QuarkFileMDSvc` and shared with `QuarkContainerMDSvc`.

## Risks and Test Signals
Capacity division truncates remainders, so small global limits below 16 become zero per shard. Modulo sharding assumes stable id distribution and fixed shard count. Tests should cover construction with contact details, forwarding to expected shards, unlimited cache size, small cache sizes, aggregated statistics including in-flight counts, and destruction ordering under pending futures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProvider.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProvider.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProvider.hh

## Purpose
This header declares `MetadataProvider`, the sharded asynchronous metadata retrieval and cache coordinator for QuarkDB namespace services.

## Important APIs, Types, and Functions
The public API retrieves container and file metadata, drops cached ids, checks file existence, inserts newly created file/container objects into caches, changes file/container cache capacities, and returns cache statistics. Private `pickShard()` overloads map file and container identifiers to one of `kShards == 16`.

Important members are `mExecutor`, `mQcl`, and `mShards`. The comment documents a lifetime invariant: the folly executor must outlive qclient futures and therefore is declared before qclient storage.

## Control Flow
Users construct the provider with QDB contact details and service pointers, then call asynchronous retrieval APIs. All calls are forwarded to a selected `MetadataProviderShard`.

## State and Persistence Behavior
The provider owns cache shards and qclients but no durable metadata. It coordinates in-memory cache state for persistent protobuf objects fetched from QuarkDB.

## Dependencies and Integration Points
It depends on identifier types, metadata interfaces, `MetadataProviderShard`, namespace macros, folly futures and splitters, and QDB contact details. It integrates with `QuarkFileMDSvc` and `QuarkContainerMDSvc`.

## Risks and Test Signals
Service pointers are non-owning and passed down to shards for object construction, so their lifetimes must exceed provider operations. Tests should target pointer lifetime assumptions, shard selection consistency, and executor/qclient teardown while futures are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProvider.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProviderShard.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProviderShard.cc

## Purpose
This file implements one shard of the QuarkDB metadata provider. A shard owns LRU caches for file and container metadata, coalesces concurrent cache misses with `folly::FutureSplitter`, fetches from QDB through `MetadataFetcher`, and turns protobuf/map results into `QuarkFileMD` and `QuarkContainerMD` objects.

## Important APIs, Types, and Functions
The constructor stores non-owning qclient/service/executor pointers and initializes default cache sizes: 312,500 containers and 2,500,000 files per shard. `retrieveContainerMD()` checks the LRU, checks in-flight fetches under `mMutex`, fetches container protobuf, file map, and container map concurrently, combines them with `folly::collect`, processes the result on the executor, and clears in-flight state on errors. `retrieveFileMD()` follows the same pattern for file protobufs and explicitly rejects fid 0. `dropCachedFileID()` and `dropCachedContainerID()` remove LRU entries. `hasFileMD()` delegates existence checks. Insert and cache-size methods update LRU state under the mutex.

`processIncomingContainerMD()` validates id, constructs a `QuarkContainerMD`, initializes it from protobuf plus maps, erases the in-flight splitter, inserts the object into the cache, and returns the pointer. `processIncomingFileMdProto()` does the same for `QuarkFileMD`. Cache-stat methods report enabled state, occupancy, max, request/hit counters, and in-flight size.

## Control Flow
Each retrieve method uses double-checked cache lookup: a fast unlocked LRU get, then a locked in-flight/cache check. Cache hits returning deleted tombstone objects are converted to ENOENT futures. Cache misses insert a `FutureSplitter` before returning so later callers receive the same eventual object. Error continuations remove the in-flight entry and propagate the exception.

## State and Persistence Behavior
The shard stores in-memory LRU caches and in-flight maps. It reads persistent metadata from QuarkDB via `MetadataFetcher` but does not write persistent state. Newly created metadata objects can be inserted directly by services before they are fetched from QDB. Deleted objects may remain as tombstones, causing future retrievals to return ENOENT until dropped or evicted.

## Dependencies and Integration Points
It depends on folly futures/executors, `MetadataFetcher`, `QuarkFileMD`, `QuarkContainerMD`, `MDException`, EOS assertions, `LRU`, qclient, and namespace service interfaces. It is used exclusively by `MetadataProvider`.

## Risks and Test Signals
Race behavior is central. Tests should verify concurrent callers for the same id share one backend fetch, in-flight entries are erased on both success and failure, tombstone cache hits return ENOENT, fid 0 does not contact QDB, cache drops work while objects are in flight, cache stats include in-flight counts, and malformed fetched protobuf ids trip assertions. Object initialization runs under `mMutex`, so expensive initialization could block unrelated ids in the same shard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProviderShard.cc -->

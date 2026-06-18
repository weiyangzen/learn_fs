# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.22.0.xml lines 17751-18589

## Chunk Scope

This chunk is the final span of the Hadoop HDFS 0.22.0 JDiff XML API snapshot. It starts in the tail of `org.apache.hadoop.hdfs.tools.DelegationTokenFetcher`, covers HDFS command-line/admin tools, offline fsimage viewer entry points, and HDFS utility collection/throttling types, then closes the XML document.

The file is API metadata, not executable Java source. It records public type signatures, inheritance, implemented interfaces, constructors, methods, fields, exceptions, synchronization flags, deprecation status, and Javadoc CDATA used for compatibility comparison.

## Purpose and Major Areas

The span documents three broad API surfaces:

- HDFS operational tools in `org.apache.hadoop.hdfs.tools`: delegation-token fetching/renewal/cancellation, administrative NameNode commands, filesystem checking, concatenation, and JMX inspection.
- Offline image viewer entry points in `org.apache.hadoop.hdfs.tools.offlineImageViewer`: visitors and CLI plumbing for reading fsimage files without a live NameNode.
- Low-level HDFS utilities in `org.apache.hadoop.hdfs.util`: byte-array key wrapping, transfer throttling, and memory-sensitive set implementations used by HDFS internals.

## Important APIs and Types

### `org.apache.hadoop.hdfs.tools`

`DelegationTokenFetcher` is a command-line helper for obtaining and managing HDFS delegation tokens. This chunk includes `main(String[])`, static `getDTfromRemote(String nnAddr, String renewer)`, static `renewDelegationToken(String nnAddr, Token tok)`, and static `cancelDelegationToken(String nnAddr, Token tok)`. The renew API returns the next token expiration timestamp as a `long`; both renew and cancel document the NameNode address and token parameters and throw `IOException`.

`DFSAdmin` extends `org.apache.hadoop.fs.FsShell` and provides public constructors with and without `Configuration`. Its public administrative methods map command-line subcommands to NameNode operations:

- `report()` prints filesystem status.
- `setSafeMode(String[] argv, int idx)` handles `-safemode enter|leave|get`.
- `saveNamespace()` asks the NameNode to persist the namespace via `ClientProtocol#saveNamespace()`.
- `restoreFaileStorage(String arg)` controls or checks failed-storage restoration. The method name is misspelled in the published API, so compatibility users must preserve that spelling.
- `refreshNodes()` reloads include/exclude host files.
- `finalizeUpgrade()` finalizes a completed upgrade.
- `upgradeProgress(String[] argv, int idx)` reports, details, or forces distributed-upgrade progress.
- `metaSave(String[] argv, int idx)` writes NameNode metadata structures to a named file.
- `printTopology()` prints rack-to-node topology as seen by the NameNode.
- `refreshServiceAcl()`, `refreshUserToGroupsMappings()`, and `refreshSuperUserGroupsConfiguration()` refresh NameNode authorization and identity/group mapping state.
- `run(String[] argv)` implements `Tool`-style dispatch and `main(String[])` is the process entry point.

`DFSck` extends `Configured` and implements `Tool`. Constructors accept `Configuration` and optionally a `PrintStream`, both throwing `IOException`. `run(String[] args)` performs fsck command execution and `main(String[])` is the CLI entry point. The class documentation describes scans from a chosen root path, detection of missing blocks, under-replication, over-replication, detailed DFS statistics, optional block-location and replication-factor output, and optional filtering of open files. For corrupted files, the documented actions are none, move salvageable block chains to `/lost+found`, or delete, corresponding to `NamenodeFsck` fix constants.

`HDFSConcat` is a thin public tool class with a default constructor and `main(String[] args)` throwing `IOException`. The XML does not include detailed command semantics in this span, but the name and placement indicate CLI exposure for HDFS file concatenation.

`JMXGet` is a command-line utility for reading Hadoop MBeans from NameNode or DataNode processes. It exposes mutable target configuration through `setService(String)`, `setPort(String)`, `setServer(String)`, and `setLocalVMUrl(String)`. `init()` initializes the MBean server connection, `printAllValues()` emits all attributes, `getValue(String key)` returns one attribute as a string, and `main(String[])` drives CLI usage. The documented MBean examples include NameNode `FSNamesystemState`, `NameNodeActivity`, NameNode RPC activity, DataNode RPC activity, `FSDatasetState`, and `DataNodeActivity`. Logging is intentionally sent to `System.err` because this is a command-line tool.

### `org.apache.hadoop.hdfs.tools.offlineImageViewer`

`NameDistributionVisitor` extends `TextWriterImageVisitor`. Its constructor accepts an output target string and a boolean flag, and throws `IOException`. The visitor analyzes file names in an fsimage and prints unique filename count, ranges of duplicate-name usage, and estimated heap saved if filename objects are reused.

`OfflineImageViewer` is the main fsimage inspection utility. Its constructor accepts an input image filename, an `ImageVisitor`, and a boolean option. `go()` processes the image file, `buildOptions()` creates Apache Commons CLI `Options`, and `main(String[])` parses CLI arguments, selects an output visitor, processes the fsimage, and exits cleanly or reports errors. The documentation explicitly positions it as both a command-line and programmatic entry point for dumping Hadoop image files to XML or console-oriented formats.

### `org.apache.hadoop.hdfs.util`

`ByteArray` wraps a `byte[]` so arrays can be used as `HashMap` keys. It exposes `getBytes()`, `hashCode()`, and `equals(Object)`. Correctness depends on value-based equality/hash semantics rather than Java array identity.

`DataTransferThrottler` provides thread-safe bandwidth limiting for HDFS data transfers. Constructors accept `bandwidthPerSec` alone or an enforcement `period` plus bandwidth. `getBandwidth()` and `setBandwidth(long)` are synchronized; `setBandwidth` takes effect no later than the end of the current period. `throttle(long numOfBytes)` is synchronized and sleeps the calling thread when aggregate I/O rate exceeds the configured bytes-per-second budget. The docs say the configured bandwidth is shared by all threads using the same throttler instance.

`GSet` is a generic set-like interface extending `Iterable` with map-style lookup. It exposes `size()`, `contains(Object key)`, `get(Object key)`, `put(Object element)`, and `remove(Object key)`. Unlike `Set#add`, `put` replaces an equal existing element and returns the previous stored element. Null keys/elements are unsupported and documented as throwing `NullPointerException`. The generic contract is key type `K` and element type `E`, where `E` is a subclass of `K`.

`GSetByHashMap` implements `GSet` on top of `HashMap`. Its constructor takes initial capacity and load factor. It exposes the full `GSet` surface plus `iterator()`, serving as the straightforward collection-backed implementation.

`LightWeightGSet` implements `GSet` with lower memory overhead. The constructor takes a recommended internal array length. It exposes `size`, `get`, `contains`, `put`, `remove`, `iterator`, `toString`, and `printDetails(PrintStream)`, plus a public static final `LOG` field. The class stores elements in a fixed array and resolves collisions with linked lists. It never rehashes or resizes, rejects null elements, and is explicitly not thread safe. Elements must implement the nested `LightWeightGSet.LinkedElement` interface.

`LightWeightGSet.LinkedElement` is a public static nested interface with `setNext(LightWeightGSet.LinkedElement)` and `getNext()`. It lets the set maintain collision chains without allocating separate wrapper nodes, which is the core memory-saving design point.

## Control Flow and Lifecycle

Tool classes follow the Hadoop CLI pattern: parse arguments in `main` or `run`, build or read configuration, connect to NameNode/DataNode/JMX or local fsimage state, then return an exit code or throw an exception. `DFSAdmin.run` is the central command dispatcher for administrative subcommands. Individual methods perform focused RPC-like operations such as save namespace, refresh nodes, or change safemode. `DFSck.run` drives a scan through the NameNode-side fsck implementation and reports findings/actions through the configured output stream.

Delegation-token flow is remote and token-centered: `getDTfromRemote` obtains credentials from a named NameNode address for a renewer; `renewDelegationToken` sends the token back to the NameNode and returns the updated expiration; `cancelDelegationToken` invalidates it. Callers must handle `IOException` from RPC, address resolution, and token service errors.

Offline image viewing is file-oriented rather than cluster-oriented. `OfflineImageViewer.main` builds CLI options, chooses an `ImageVisitor`, constructs the viewer, and calls `go()`. Visitors such as `NameDistributionVisitor` receive parsed fsimage events and write derived reports.

`DataTransferThrottler` control flow is per-transfer accounting: callers report bytes transferred to `throttle`; the synchronized method compares accumulated bytes over the current period against the configured bandwidth and sleeps if necessary. Shared use across transfer threads intentionally enforces a group bandwidth budget.

`GSet` implementations center on key-equivalent element lookup. `GSetByHashMap` delegates lifecycle to Java collection storage. `LightWeightGSet` uses caller-owned element link pointers, so `put` and `remove` mutate the element chain through `LinkedElement.setNext` and depend on stable `hashCode`/`equals` behavior.

## State and Persistence Behavior

The JDiff XML itself preserves API compatibility state for Hadoop 0.22.0. Within the APIs it describes, persistent or externally visible state includes delegation tokens and `Credentials`, NameNode namespace images, host include/exclude files, upgrade state, metadata dump files from `metaSave`, fsck repair output under `/lost+found`, and offline fsimage input/output reports.

`DFSAdmin.saveNamespace` triggers NameNode persistence of filesystem namespace state. `finalizeUpgrade` and `upgradeProgress` interact with upgrade lifecycle state that must remain consistent across NameNode/DataNode processes. Refresh commands update live in-memory policy, group mapping, superuser proxy configuration, or datanode membership state from external configuration files.

`JMXGet` keeps connection target state in service, port, server, or local VM URL fields until `init` connects. It reads live process metrics but does not define a durable format in this span.

`ByteArray` stores a raw byte-array reference; if callers mutate that array after inserting the wrapper into a hash map, hash/equality behavior can become inconsistent. `DataTransferThrottler` stores synchronized mutable bandwidth and per-period accounting. `LightWeightGSet` stores entries in a fixed-size array and in each element's next pointer, so set membership is embedded partly in the elements themselves.

## Dependencies and Integration Points

These APIs depend on Hadoop core and HDFS types including `Configuration`, `FsShell`, `Configured`, `Tool`, `Credentials`, `Token`, `NameNode`, `ClientProtocol`, `NamenodeFsck`, `ImageVisitor`, and `TextWriterImageVisitor`. They also use Java I/O (`IOException`, `PrintStream`), Java collections/iteration, Apache Commons CLI `Options`, Apache Commons Logging `Log`, and Java MBean/JMX infrastructure through the `JMXGet` tool.

External integration points are operationally significant: NameNode administrative RPCs, DataNode/NameNode JMX MBeans, delegation-token services, fsimage files, Hadoop security authorization policy files, user/group mapping providers, include/exclude hosts files, upgrade-finalization state, and filesystem repair paths such as `/lost+found`.

The utility collection types integrate with HDFS in-memory metadata structures. `LightWeightGSet` is especially tied to high-cardinality metadata use cases where avoiding per-entry wrapper allocation matters, such as block or inode lookup tables in older HDFS internals.

## Risks and Edge Cases

- The published `DFSAdmin.restoreFaileStorage` spelling is part of the public API in this snapshot; correcting it without a compatibility bridge would break callers using the JDiff-defined method.
- Administrative commands mutate live cluster state. Safemode transitions, namespace saves, upgrade finalization, and failed-storage restoration need authorization checks and should be tested against NameNode state transitions, not just CLI parsing.
- Refresh commands are only as correct as their backing configuration sources. Bad hosts files, service ACLs, or group mapping data can immediately affect cluster access and datanode participation.
- Fsck repair modes can delete data or move partial block chains to `/lost+found`; tests need to distinguish reporting-only scans from mutating repair modes.
- Delegation token renew/cancel operations are security-sensitive. Wrong NameNode address, renewer identity, expired tokens, or token service mismatch should fail clearly and avoid leaking credentials.
- JMX MBean names include service, port, and sometimes storage-id-derived names. Hard-coded MBean strings can be brittle across process roles, ports, and versions.
- `ByteArray` is safe as a map key only if the wrapped bytes are treated as immutable while stored in hash-based collections.
- `DataTransferThrottler` is synchronized and may become a contention point when shared by many transfer threads. Bandwidth changes are period-delayed by design.
- `LightWeightGSet` never rehashes, so a poor recommended length or skewed hash distribution can cause long chains and degraded lookup performance. It is not thread safe and corrupts membership if elements' next pointers are reused elsewhere.
- `LightWeightGSet` depends on element implementations of `LinkedElement`, `equals`, and `hashCode`; mutable key fields can make entries unreachable or removable only by traversal accidents.

## Test Signals

Useful validation around code represented by this API snapshot would include:

- JDiff/schema checks asserting that the public classes, methods, exceptions, synchronization flags, and field visibility in this line span remain stable for the 0.22.0 snapshot.
- CLI dispatch tests for `DFSAdmin.run` covering `-safemode`, `-saveNamespace`, `-restoreFailedStorage`, `-refreshNodes`, `-finalizeUpgrade`, `-upgradeProgress`, `-metasave`, topology printing, and refresh commands, including argument-index validation and non-zero exit codes.
- NameNode integration tests for namespace save, hosts refresh, service ACL refresh, group mapping refresh, superuser proxy refresh, safemode transitions, upgrade progress, and upgrade finalization.
- Delegation token tests for fetch, renew, cancel, expired-token handling, wrong renewer, wrong NameNode address, and credential serialization around `getDTfromRemote`.
- Fsck tests for healthy files, missing blocks, under-replicated blocks, over-replicated blocks, open-file filtering, detailed block-location output, delete repair, and move-to-`/lost+found` repair.
- JMX tests with mock or in-process MBean servers verifying server/port/service/local-VM configuration, `init`, `getValue`, missing attributes, and `printAllValues`.
- Offline image viewer tests for option construction, invalid CLI arguments, visitor selection, `go()` error handling, and `NameDistributionVisitor` duplicate-name/heap-savings reporting against small fsimage fixtures.
- `ByteArray` equality/hash tests for same contents, different contents, and mutation-after-insert behavior documentation.
- `DataTransferThrottler` tests using controlled clocks or bounded sleeps for bandwidth enforcement, dynamic `setBandwidth`, shared-thread throttling, and synchronized access.
- `GSet` contract tests shared across `GSetByHashMap` and `LightWeightGSet`: null rejection, `put` replacement semantics, `get` by equal key, `remove`, iteration, and size tracking.
- `LightWeightGSet` stress tests for collision chains, fixed-capacity behavior, iterator consistency after removal, `printDetails`, and non-thread-safe behavior guarded by higher-level synchronization in callers.

## Cross-Chunk Notes

The chunk starts after the beginning of `DelegationTokenFetcher`; adjacent upstream lines contain earlier package context and the start of that class. This chunk ends at `</api>`, so it completes the `hadoop-hdfs_0.22.0.xml` source file. Merge/reconciliation should treat this as a chunk report for the tail of the file, not as a complete source-file report by itself.

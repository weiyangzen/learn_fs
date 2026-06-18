# subset-b-007365 grouped research

This grouped report covers Hadoop Common network topology/socket support, ONC RPC protocol support, ONC RPC security flavors, and the requested portmap entry points. Each section title preserves the source path and is wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetworkTopology.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetworkTopology.java

Purpose: `NetworkTopology` models a Hadoop cluster as a hierarchical tree of `InnerNode` switches/racks and leaf `Node` data nodes. It is used by HDFS and MapReduce to reason about rack locality, replica distance, random target selection, and sorting candidate nodes by network distance.

Important APIs/types/functions: `getInstance(Configuration)` reflects `net.topology.impl`; `add`, `remove`, `contains`, `getNode`, `getDatanodesInRack`, `getDistance`, `getDistanceByPath`, `isOnSameRack`, `chooseRandom`, `countNumOfAvailableNodes`, `getLeaves`, `sortByDistance`, `sortByDistanceUsingNetworkLocation`, `shuffle`, `decommissionNode`, `recommissionNode`, and `getNumOfNonEmptyRacks`. `InvalidTopologyException` protects against mixed leaf depths.

Control flow: writes acquire `netlock.writeLock`, reject inner-node additions/removals, enforce a consistent leaf depth, update rack counters, and delegate structural mutation to `clusterMap`. Reads use `readLock`. Random selection normalizes include/exclude scopes, subtracts excluded subtrees and excluded nodes, then chooses uniformly among valid leaves. Sorting groups active nodes by distance weight, shuffles each weight bucket, optionally applies a secondary sort, and rewrites the active prefix.

State and persistence: state is in-memory only: `clusterMap`, `depthOfAllLeaves`, rack counts, `rackMap`, `decommissionNodes`, and `clusterEverBeenMultiRack`. No disk persistence exists; callers rebuild topology from membership events and DNS-to-switch mappings.

Dependencies and integration: depends on `Node`, `NodeBase`, `InnerNode`, `InnerNodeImpl`, Hadoop `Configuration`, `CommonConfigurationKeysPublic.NET_TOPOLOGY_IMPL_KEY`, and `ReflectionUtils`. Consumers include block placement, read replica ordering, and topology-aware schedulers.

Risks: scope logic is path-string sensitive; wrong normalization changes random selection and available-node counts. `isChildScope` naming is unintuitive because it checks prefix containment after appending slashes. Empty-rack accounting relies on node names and can drift if callers mutate `Node` names/locations after insertion. `getDistance` depends on parent references belonging to this topology, while path-based distance does not. `RANDOM_REF` is static test state.

Test signals: `TestClusterTopology` and related topology tests exercise add/remove, rack counts, distances, random selection, sorting, and decommission/recommission behavior. Useful additional coverage is deterministic random selection with excluded inner scopes and empty rack transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetworkTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetworkTopologyWithNodeGroup.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetworkTopologyWithNodeGroup.java

Purpose: extends `NetworkTopology` for a four-level topology with node groups between racks and leaves, used for virtualization-aware placement where hosts sharing a hypervisor should be closer than same-rack but not identical.

Important APIs/types/functions: `DEFAULT_NODEGROUP`, `getNodeForNetworkLocation`, `getRack`, `getNodeGroup`, `isOnSameRack`, `isOnSameNodeGroup`, `isNodeGroupAware`, `add`, `remove`, `getWeight`, `sortByDistance`, and nested `InnerNodeWithNodeGroup`.

Control flow: default-rack leaves are rewritten to `/default-rack/default-nodegroup`. `add` validates that the implied rack is an inner node with a parent, then adds the leaf and increments rack count only when a new rack appears. Same-rack compares parents of node-group parents; same-node-group compares direct parents. Sorting substitutes an out-of-tree reader with an existing sibling leaf from the same node group when possible, then delegates to base sorting.

State and persistence: in-memory topology state inherited from `NetworkTopology`, but the constructor replaces `clusterMap` with `InnerNodeWithNodeGroup`. It does not update the base class empty-rack tracking on add/remove, so nodegroup-aware users primarily rely on rack counts and distance sorting.

Dependencies and integration: integrates with `InnerNodeImpl` and base topology APIs. HDFS block placement can query `isNodeGroupAware` and `isOnSameNodeGroup` to avoid colocating replicas on the same physical host.

Risks: `getNodeGroup` only recognizes `InnerNodeWithNodeGroup`; leaf lookup paths fall through as not handled. The rack/nodegroup classification in `InnerNodeWithNodeGroup` inspects the first child, assuming homogeneous subtree shape. The constructor sets `clusterMap` directly and leaves `factory` as the base default factory, so removal fallback uses `factory.newInnerNode` rather than the nodegroup subclass.

Test signals: `TestNetworkTopologyWithNodeGroup` covers node group identity, rack identity, add/remove, distance sorting, and default nodegroup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetworkTopologyWithNodeGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/Node.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/Node.java

Purpose: defines the minimal contract for entries in Hadoop's network topology tree. Leaves usually represent data nodes, while inner-node implementations represent data centers, racks, or node groups.

Important APIs/types/functions: `getNetworkLocation`, `setNetworkLocation`, `getName`, `getParent`, `setParent`, `getLevel`, and `setLevel`.

Control flow: this is an interface only. Tree mutations are driven by `InnerNode`/`NetworkTopology` implementations, which set parent and level while adding or removing nodes.

State and persistence: no state directly. Implementations are mutable, so callers must treat network location, parent, and level as topology-managed fields once inserted.

Dependencies and integration: implemented by `NodeBase` and inner-node classes. Used pervasively in topology distance, scope, sorting, and rack membership code.

Risks: because setters are public, external mutation can invalidate `NetworkTopology` invariants, cached map keys, and parent/level-based distance calculations.

Test signals: indirectly covered by `NodeBase`, `NetworkTopology`, and nodegroup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/Node.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NodeBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NodeBase.java

Purpose: base mutable implementation of `Node` that stores a node name, normalized network location, tree parent, and tree level. It also provides path utility functions used by topology code.

Important APIs/types/functions: constructors from full path or name/location, `normalize`, `getPath`, `getPathComponents`, `locationToDepth`, getters/setters, `equals`, `hashCode`, and `toString`.

Control flow: constructors call `normalize` and split paths on the last slash. `normalize` rejects null and relative locations, collapses duplicate slashes, strips a trailing slash, and maps empty input to root. Equality and hash code are path based.

State and persistence: in-memory fields `name`, `location`, `level`, and `parent`; no persistence. `name` must not contain `/`; null names become empty strings.

Dependencies and integration: used by `NetworkTopology`, `InnerNodeImpl`, block placement helpers, and tests as the canonical path formatter/normalizer.

Risks: `setNetworkLocation` does not normalize, so callers can bypass constructor invariants. `getPathComponents` uses Java `split("/")`, so leading slash creates an initial empty component; distance code depends on that behavior. Mutating location/name after insertion changes equality and hash code.

Test signals: topology tests validate normalization, path identity, and level/depth behavior through higher-level APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NodeBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ScriptBasedMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ScriptBasedMapping.java

Purpose: implements DNS-to-rack mapping by invoking an administrator-configured script and caching results through `CachedDNSToSwitchMapping`.

Important APIs/types/functions: constructors, `setConf`, `getConf`, `toString`, nested `RawScriptBasedMapping.resolve`, `runResolveCommand`, `isSingleSwitch`, and reload no-ops on the raw mapper.

Control flow: outer class delegates to the raw mapper and cache. The raw mapper reads script path and max argument count from configuration. `resolve` returns default rack for all names when no script is configured. With a script, it invokes the script in chunks of `maxArgs`, tokenizes whitespace output, and requires exactly one returned switch path per input name.

State and persistence: stores `scriptName` and `maxArgs`; the outer superclass stores the cache. No mapping state is persisted. Script execution occurs in `user.dir` if set.

Dependencies and integration: depends on `ShellCommandExecutor`, `CommonConfigurationKeys`, `DNSToSwitchMapping`, and topology default rack constants. Used by Hadoop network topology mapping configuration.

Risks: script output count mismatch returns null, signaling resolution failure. Invalid `maxArgs` disables resolution. Script execution inherits current working directory and environment, so deployment configuration matters. `isSingleSwitch` returns true only when no script is configured.

Test signals: `TestScriptBasedMapping` covers no-script fallback, argument chunking, bad output count, reload behavior, and configuration changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ScriptBasedMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ScriptBasedMappingWithDependency.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ScriptBasedMappingWithDependency.java

Purpose: extends script-based rack mapping with a dependency script, allowing callers to ask what hosts depend on a given host.

Important APIs/types/functions: `DEPENDENCY_SCRIPT_FILENAME_KEY`, `getDependency`, `setConf`, nested `RawScriptBasedMappingWithDependency.getDependency`, and inherited rack-resolution APIs.

Control flow: `getDependency` normalizes the host name through `NetUtils.normalizeHostName`, checks a concurrent cache, and on miss invokes the raw dependency script with the single normalized name. The raw mapper returns an empty list for null names or no configured dependency script, tokenizes script output on whitespace, and returns null on script execution failure.

State and persistence: dependency results are cached in a `ConcurrentHashMap`; no eviction and no persistent storage. Configuration stores the dependency script path in the raw mapper.

Dependencies and integration: implements `DNSToSwitchMappingWithDependency`, reuses `ScriptBasedMapping.RawScriptBasedMapping.runResolveCommand`, and depends on `CommonConfigurationKeys.NET_DEPENDENCY_SCRIPT_FILE_NAME_KEY`.

Risks: cache never invalidates on `setConf` or reload, so dependency script changes may not affect already-resolved names. Null from a failed script is not cached and may surprise callers expecting a list. Host normalization can collapse aliases before lookup.

Test signals: `TestScriptBasedMappingWithDependency` covers dependency script execution, default empty results, and cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ScriptBasedMappingWithDependency.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketIOWithTimeout.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketIOWithTimeout.java

Purpose: package-private base for Hadoop socket input/output streams that implement read, write, connect, and readiness waits with explicit timeouts over nonblocking `SelectableChannel`s.

Important APIs/types/functions: constructor, `checkChannelValidity`, abstract `performIO`, `doIO`, static `connect`, `waitForIO`, `setTimeout`, `timeoutExceptionString`, and nested `SelectorPool`.

Control flow: channels are forced to nonblocking mode. `doIO` tries immediate I/O; if zero bytes are transferred, it waits on a pooled selector for the requested operation, throws `SocketTimeoutException` on timeout, and treats close/error as closed. `connect` temporarily sets nonblocking mode, loops on `finishConnect`, closes the channel on failure, and restores blocking mode if needed. `SelectorPool` leases selectors by provider, cancels keys after use, clears cancelled keys with `selectNow`, and trims idle selectors.

State and persistence: per-wrapper state is channel, timeout, and closed flag. Static selector pools are process-local and idle-trimmed after 10 seconds.

Dependencies and integration: used by `SocketInputStream` and `SocketOutputStream`; depends on Java NIO selectors and Hadoop `Time`.

Risks: one thread is intended per wrapper; concurrent use can conflict on channel registration. Negative timeouts are not explicitly rejected. Selector trimming uses static shared state and must avoid returning broken selectors after exceptions.

Test signals: `TestSocketIOWithTimeout` covers timeout behavior, readiness waits, connect timeouts, and selector cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketIOWithTimeout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketInputStream.java

Purpose: `InputStream` and `ReadableByteChannel` wrapper that reads from a selectable socket channel with Hadoop-managed timeouts.

Important APIs/types/functions: constructors from `ReadableByteChannel` or `Socket`, `read()`, `read(byte[], int, int)`, `read(ByteBuffer)`, `close`, `getChannel`, `isOpen`, `waitForReadable`, and `setTimeout`.

Control flow: a nested `Reader` implements `SocketIOWithTimeout.performIO` by calling `ReadableByteChannel.read`. All channel reads pass through `reader.doIO(..., OP_READ)`. Closing closes the underlying channel and marks the reader closed.

State and persistence: holds only the `Reader`; no persistence. Constructing the wrapper makes the socket channel nonblocking, which changes behavior of standard socket streams.

Dependencies and integration: used by `NetUtils.getInputStream` and by `SocketInputWrapper` for sockets with channels. Pairs with `SocketOutputStream`.

Risks: sockets created without a channel fail construction. Single-byte reads allocate a new byte array. Consumers must avoid mixing this wrapper with the original blocking socket streams after nonblocking mode is set.

Test signals: `TestSocketIOWithTimeout` exercises reads, EOF, timeout, close, and channel validity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketInputWrapper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketInputWrapper.java

Purpose: filter stream wrapper that gives callers a consistent read-timeout API whether a socket has an NIO channel or only classic blocking streams.

Important APIs/types/functions: package-private constructor, `setTimeout`, and `getReadableByteChannel`.

Control flow: construction records whether `Socket.getChannel()` is present and asserts that channel-backed sockets use a `SocketInputStream`. `setTimeout` delegates to `SocketInputStream.setTimeout` for channel sockets or to `Socket.setSoTimeout` for non-channel sockets. `getReadableByteChannel` is allowed only for channel-backed sockets.

State and persistence: holds the socket, wrapped input stream, and `hasChannel` flag; no persistence.

Dependencies and integration: used by socket utility code that must support both NIO and classic sockets.

Risks: for non-channel sockets, timeout changes affect all readers of that socket, not only this wrapper. Long timeout values are cast to `int` in the non-channel path. Creating multiple wrappers on one socket can produce inconsistent timeout expectations.

Test signals: covered indirectly by socket utility and timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketInputWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketOutputStream.java

Purpose: `OutputStream` and `WritableByteChannel` wrapper that writes to selectable socket channels with explicit timeouts and supports zero-copy file transfer.

Important APIs/types/functions: constructors, `write(int)`, `write(byte[], int, int)`, `write(ByteBuffer)`, `close`, `getChannel`, `isOpen`, `waitForWritable`, `transferToFully`, and `setTimeout`.

Control flow: nested `Writer.performIO` delegates to `WritableByteChannel.write`. Byte-array writes loop until the buffer drains; if an exception occurs after a partial write, the writer is marked closed because `OutputStream` cannot report partial progress. `transferToFully` waits for writability, calls `FileChannel.transferTo`, advances position/count, and records wait and transfer timings.

State and persistence: holds a `Writer`; no persistence. Construction puts the channel in nonblocking mode.

Dependencies and integration: used by HDFS data transfer paths and `NetUtils.getOutputStream`. Integrates with `LongWritable` timing counters.

Risks: transfer count is `int`, limiting single call size. EOF detection depends on file size when `transferTo` returns zero. Mixing original blocking socket streams with this wrapper is unsafe after nonblocking mode.

Test signals: `TestSocketIOWithTimeout` covers writes, timeouts, and close behavior; data-transfer tests usually exercise `transferToFully`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocksSocketFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocksSocketFactory.java

Purpose: Hadoop-configurable `SocketFactory` that creates sockets through a SOCKS proxy.

Important APIs/types/functions: constructors, all `createSocket` overloads, `setConf`, `getConf`, equality/hash code, and private `setProxy`.

Control flow: the default proxy is `Proxy.NO_PROXY`. `setConf` reads `hadoop.socks.server` and parses `host:port` into an unresolved SOCKS proxy. Socket overloads create a proxy-backed socket, optionally bind a local address, and connect to the remote endpoint.

State and persistence: stores `Configuration` and `Proxy`; no persistence.

Dependencies and integration: used by Hadoop networking code when a socket factory class is configured. Depends on `CommonConfigurationKeysPublic.HADOOP_SOCKS_SERVER_KEY`.

Risks: malformed proxy strings throw runtime exceptions, and non-numeric ports throw `NumberFormatException`. `setConf(null)` would dereference null. Equality is proxy-based, so factories with equivalent proxy settings compare equal.

Test signals: usually covered through socket factory and `NetUtils` tests; additional tests should cover malformed proxy configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocksSocketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/StandardSocketFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/StandardSocketFactory.java

Purpose: standard Hadoop `SocketFactory` that creates NIO-backed sockets so Hadoop can wrap them with timeout-aware channel streams.

Important APIs/types/functions: constructor, all `createSocket` overloads, `equals`, and `hashCode`.

Control flow: `createSocket()` opens a `SocketChannel` and returns its socket. Other overloads bind and/or connect the created socket.

State and persistence: stateless; equality is class-based.

Dependencies and integration: used by `NetUtils` and default Hadoop networking. Its sockets should be consumed with `NetUtils.getInputStream` and `NetUtils.getOutputStream`, not raw socket streams, because channel mode interactions can block in surprising ways.

Risks: the class comment says SOCKS proxy but implementation is standard NIO sockets. Users that call `Socket.getInputStream()`/`getOutputStream()` directly can hit blocking-mode issues after Hadoop wrappers configure nonblocking mode.

Test signals: covered indirectly by `NetUtils` and socket timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/StandardSocketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/TableMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/TableMapping.java

Purpose: DNS-to-rack mapping implementation backed by a two-column UTF-8 text file configured via `net.topology.table.file.name`.

Important APIs/types/functions: constructor, `getConf`, `setConf`, `reloadCachedMappings`, nested `RawTableMapping.load`, `resolve`, and reload overloads.

Control flow: `resolve` lazily loads the file into a map, falling back to an empty map and default rack on load failure. `load` trims lines, skips blanks and comments, accepts exactly two whitespace-separated columns, and logs ignored malformed lines. Reload attempts a fresh full-table load and only swaps the map on success.

State and persistence: in-memory `map` cache in `RawTableMapping`; source of truth is the external table file. Outer class adds `CachedDNSToSwitchMapping` caching.

Dependencies and integration: depends on Hadoop `Configuration`, `Configured`, `NET_TOPOLOGY_TABLE_MAPPING_FILE_KEY`, and topology default rack. Used as an alternative to script-based mapping.

Risks: malformed or unreadable files silently degrade to default rack on initial load. Reload failure preserves stale mappings. Per-name reload reloads the whole file. Lookups are exact; host normalization is not done here.

Test signals: `TestTableMapping` covers parsing, fallback, reload, comments, and malformed lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/TableMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/package-info.java

Purpose: package-level metadata declaring `org.apache.hadoop.net` as the network-related Hadoop package.

Important APIs/types/functions: package annotation `@InterfaceAudience.Public`.

Control flow: no runtime control flow.

State and persistence: none.

Dependencies and integration: depends on Hadoop classification annotations and documents package audience for generated Javadocs.

Risks: minimal. Incorrect audience annotations can mislead downstream API consumers about compatibility expectations.

Test signals: no direct tests required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/unix/DomainSocket.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/unix/DomainSocket.java

Purpose: Java wrapper around native UNIX domain socket operations, including bind/listen, accept, connect, socketpair, socket attributes, shutdown/close, stream I/O, readable channel I/O, and file descriptor passing.

Important APIs/types/functions: static native loader and `getLoadingFailureReason`, `disableBindPathValidation`, `getEffectivePath`, `bindAndListen`, `socketpair`, `connect`, `accept`, `setAttribute`, `getAttribute`, `close(boolean)`, `shutdown`, `sendFileDescriptors`, `recvFileInputStreams`, nested `DomainInputStream`, `DomainOutputStream`, and `DomainChannel`.

Control flow: static initialization verifies non-Windows native support. Public operations acquire `CloseableReferenceCount` references before using `fd` and unreference in finally blocks. `close(false)` marks closed, calls shutdown to interrupt blocking operations, waits for references to drain, then closes the fd. `close(true)` skips the drain wait after shutdown. Descriptor receive wraps native descriptors in `FileInputStream`s and cleans partial resources on failure.

State and persistence: per-socket immutable `fd` and `path`, refcount/closed state, and stream/channel wrapper instances. No persistence beyond OS socket files created by native bind.

Dependencies and integration: depends on libhadoop native methods, `NativeCodeLoader`, `CloseableReferenceCount`, and `DomainSocketWatcher`. Used by HDFS short-circuit local reads and peer transport.

Risks: native availability and path-security validation are deployment-sensitive. Reference count bugs can leak or prematurely close descriptors. `DomainChannel` only supports direct or array-backed buffers. `close(true)` can be necessary for server accept but changes lifecycle guarantees.

Test signals: `TestDomainSocket` covers socketpair, bind/connect, streams, attributes, descriptor passing, path validation, and close behavior, usually gated by native availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/unix/DomainSocket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/unix/DomainSocketWatcher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/unix/DomainSocketWatcher.java

Purpose: watches a set of `DomainSocket` file descriptors for readability or close events using native polling, then invokes registered handlers.

Important APIs/types/functions: `Handler`, constructor, `close`, `isClosed`, `add`, `remove`, `kick`, `sendCallback`, watcher thread loop, nested `FdSet`, and native `doPoll0`.

Control flow: constructor verifies native support, creates a notification socketpair, and starts a daemon watcher thread. `add` references the socket, queues it, kicks the thread, and waits until processed. `remove` queues by fd and waits until callback/removal. The watcher drains readable fds, processes additions/removals under a lock, checks close/interruption, then polls. `kick` writes one byte to the notification socket and coalesces wakeups to avoid deadlock. Shutdown closes notification socket 0 and joins the thread.

State and persistence: in-memory lock-protected queues `toAdd` and `toRemove`, `closed`, `kicked`, notification sockets, and the thread-local fd set. No persistence.

Dependencies and integration: depends on `DomainSocket`, native libhadoop polling, `IOUtils`, `SubjectInheritingThread`, and Netty-free callback consumers such as HDFS short-circuit cache components.

Risks: handler callbacks run while the watcher lock is held, so slow or reentrant handlers can block add/remove progress. Incorrect fd lifecycle causes native poll on closed descriptors. The final cleanup path must unreference sockets added but never processed.

Test signals: `TestDomainSocketWatcher` covers add/remove, readable callbacks, close cleanup, notification wakeups, and native-availability gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/unix/DomainSocketWatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RegistrationClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RegistrationClient.java

Purpose: TCP client specialization for registering or unregistering an RPC program with portmap/rpcbind and validating the reply.

Important APIs/types/functions: constructor and nested `RegistrationClientHandler.channelRead`, `validMessageLength`, `handle(RpcDeniedReply)`, and `handle(RpcAcceptedReply, XDR)`.

Control flow: inherits connection setup from `SimpleTcpClient`. On read, the handler validates a minimum response size, parses the TCP record mark, copies the reply payload into an XDR buffer, reads an `RpcReply`, handles denied vs accepted replies, expects `SUCCESS`, reads the boolean answer, logs result, and closes the channel.

State and persistence: stateless beyond request inherited from `SimpleTcpClient`; no persistence.

Dependencies and integration: used by ONC RPC registration paths. Depends on `RpcReply`, `RpcAcceptedReply`, `RpcDeniedReply`, `XDR`, Netty `ByteBuf`, and `SimpleTcpClientHandler`.

Risks: uses assertions for fragment size and success state; assertions may be disabled. It assumes array-backed `ByteBuf`. It logs failures but does not surface a boolean result to callers.

Test signals: portmap and registration integration tests should cover accepted, denied, and malformed short responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RegistrationClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcAcceptedReply.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcAcceptedReply.java

Purpose: represents the accepted branch of an ONC RPC reply body.

Important APIs/types/functions: `AcceptState` enum, `getAcceptInstance`, `getInstance`, static `read`, `getAcceptState`, and `write`.

Control flow: read consumes a verifier and accept-state integer from XDR. Write emits xid, message type, reply state, verifier, and accept state. `getAcceptInstance` is a convenience for `SUCCESS`.

State and persistence: immutable fields inherited from `RpcReply` plus `acceptState`; no persistence.

Dependencies and integration: used by `RpcProgram`, `PortmapResponse`, and tests to build success and program/procedure error replies. Depends on `Verifier`.

Risks: enum `fromValue` uses ordinal indexing without bounds checks, so malformed wire values throw array exceptions. Program mismatch replies require callers to append version bounds after this object writes its common body.

Test signals: `TestRpcAcceptedReply` validates serialization and parse round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcAcceptedReply.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcCall.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcCall.java

Purpose: models an ONC RPC call header as defined by RFC 1831, including xid, program, version, procedure, credentials, and verifier.

Important APIs/types/functions: `RPC_VERSION`, static `read`, `getInstance`, constructor validation, getters, `write`, and `toString`.

Control flow: `read` consumes header fields and delegates credential/verifier decoding. Constructor validates message type is `RPC_CALL` and RPC version is 2. `write` emits the fixed header then credential and verifier auth blocks.

State and persistence: immutable per-call fields; no persistence.

Dependencies and integration: central input object for `RpcUtil.RpcMessageParserStage`, `RpcProgram`, security handlers, and portmap requests. Depends on `Credentials` and `Verifier`.

Risks: malformed auth flavors throw during parse. `toString` assumes credential and verifier are non-null. Validation currently only checks type and RPC version, not program/version/procedure ranges.

Test signals: `TestRpcCall` covers XDR serialization, invalid versions/types, and credential/verifier handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcCall.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcCallCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcCallCache.java

Purpose: duplicate suppression cache for non-idempotent RPC calls, keyed by client address and xid.

Important APIs/types/functions: `CacheEntry`, `ClientRequest`, constructor with max entries, `checkOrAddToCache`, `callCompleted`, `size`, `iterator`, and `getProgram`.

Control flow: `checkOrAddToCache` synchronizes on the map, returns an existing entry or inserts a new in-progress entry and returns null. `callCompleted` locates the entry and stores the response. The backing `LinkedHashMap` evicts the eldest entry when size exceeds the configured maximum.

State and persistence: in-memory bounded map only; cache entries transition from in-progress (`response == null`) to completed (`response != null`).

Dependencies and integration: used by RPC services that need retransmission handling for non-idempotent procedures. Stores `RpcResponse` for replay.

Risks: `callCompleted` assumes a prior cache entry and will null-dereference if called without `checkOrAddToCache`. `size` and `iterator` are not synchronized, so test/introspection callers can observe concurrent modification. Eviction is insertion-order, not access-order.

Test signals: `TestRpcCallCache` covers duplicate detection, completion, eviction, equality, and invalid sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcCallCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcDeniedReply.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcDeniedReply.java

Purpose: represents the denied branch of an ONC RPC reply.

Important APIs/types/functions: `RejectState`, constructor, static `read`, `getRejectState`, `toString`, and `write`.

Control flow: read consumes a verifier and reject-state integer. Write emits xid, message type, reply state, verifier, and reject state.

State and persistence: immutable reply fields; no persistence.

Dependencies and integration: produced by `RpcProgram.sendRejectedReply` and parsed by clients such as `RegistrationClient`.

Risks: enum parsing uses ordinal indexing without validation. `toString` concatenates fields without separators in some places, which is harmless for logs but less readable.

Test signals: `TestRpcDeniedReply` covers read/write behavior and state access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcDeniedReply.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcInfo.java

Purpose: immutable carrier for a parsed RPC request plus Netty channel and remote-address context.

Important APIs/types/functions: constructor, `header`, `data`, `channel`, and `remoteAddress`.

Control flow: no logic beyond storing references. Created by `RpcUtil.RpcMessageParserStage` and consumed by `RpcProgram` or `RpcProgramPortmap`.

State and persistence: holds a `RpcMessage`, request `ByteBuf`, Netty `Channel`, and remote `SocketAddress`; no persistence. ByteBuf lifetime is managed by downstream handlers.

Dependencies and integration: links protocol parsing to Netty server handlers.

Risks: constructor accepts a `ChannelHandlerContext` parameter but does not store it. Consumers must release `data` exactly once; `RpcProgram` does so in finally, but custom handlers must be careful.

Test signals: covered by parser and server tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcMessage.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcMessage.java

Purpose: abstract base for ONC RPC call and reply messages, carrying xid and message type.

Important APIs/types/functions: `Type` enum, constructor, abstract `write`, `getXid`, `getMessageType`, and `validateMessageType`.

Control flow: constructor rejects any type except `RPC_CALL` or `RPC_REPLY`. `Type.fromValue` returns null for out-of-range values.

State and persistence: immutable `xid` and `messageType`; no persistence.

Dependencies and integration: extended by `RpcCall` and `RpcReply`; used by parser and response code.

Risks: invalid wire type becomes null, then subclass validation throws. Type ordinal order is protocol significant and must not be reordered.

Test signals: `TestRpcMessage` covers type mapping and validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcProgram.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcProgram.java

Purpose: abstract Netty handler base for ONC RPC server programs. It validates program/version, handles portmap registration, sends standard errors, and delegates valid calls to subclass logic.

Important APIs/types/functions: constructors, `register`, `unregister`, protected `register(PortmapMapping, boolean)`, `startDaemons`, `stopDaemons`, `channelRead`, `doPortMonitoring`, `sendRejectedReply`, abstract `handleInternal`, abstract `isIdempotent`, `getPort`, and `getPortmapUdpTimeoutMillis`.

Control flow: `register`/`unregister` build a `PortmapMapping` for every supported version and send UDP portmap requests. `channelRead` casts to `RpcInfo`, releases request data in finally, validates program number and version, sends accepted error replies for mismatch, then calls `handleInternal`. `doPortMonitoring` rejects unprivileged client ports unless allowed.

State and persistence: stores program metadata, configured/current port, version range, registration socket, timeout, and insecure-port policy; no durable state.

Dependencies and integration: used by RPC services and `SimpleTcpServer`. Depends on Netty, portmap helpers, `RpcAcceptedReply`, `RpcDeniedReply`, `RpcUtil`, and `VerifierNone`.

Risks: registration failures throw runtime exceptions. Port monitoring must be called by subclasses; base validation does not enforce it automatically. `channelRead` assumes parser produced `RpcInfo`.

Test signals: server and portmap tests cover mismatch replies, registration request construction, and insecure-port logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcProgram.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcReply.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcReply.java

Purpose: abstract base for ONC RPC replies, carrying accepted/denied state and verifier.

Important APIs/types/functions: `ReplyState`, constructor, `getVerifier`, static `read`, and `getState`.

Control flow: `read` consumes xid, validates message type is `RPC_REPLY`, reads reply state, and dispatches to `RpcAcceptedReply.read` or `RpcDeniedReply.read`.

State and persistence: immutable reply state and verifier; no persistence.

Dependencies and integration: used by clients, portmap registration, and tests to parse server replies.

Risks: `ReplyState.fromValue` does not bounds-check. A malformed XDR stream can throw unchecked exceptions. `getVerifier` returns `RpcAuthInfo` even though field type is `Verifier`.

Test signals: `TestRpcReply` covers read dispatch and reply-state handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcReply.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcResponse.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcResponse.java

Purpose: Netty addressed envelope for outbound RPC response bytes.

Important APIs/types/functions: constructors, `data`, and `remoteAddress`.

Control flow: delegates all envelope behavior to `DefaultAddressedEnvelope`; TCP and UDP response stages consume it differently.

State and persistence: wraps a `ByteBuf`, recipient, and optional sender; no persistence.

Dependencies and integration: emitted by `RpcProgram`, `RpcProgramPortmap`, and cache replay code; consumed by `RpcUtil` response stages.

Risks: ByteBuf reference ownership must be consistent. UDP response code assumes recipient is an `InetSocketAddress`.

Test signals: covered indirectly by RPC utility, server, and portmap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcUtil.java

Purpose: utility and sharable Netty stages for ONC RPC xid generation, TCP fragment decoding, RPC message parsing, and TCP/UDP response encoding.

Important APIs/types/functions: `getNewXid`, `sendRpcResponse`, `constructRpcFrameDecoder`, constants `STAGE_RPC_MESSAGE_PARSER`, `STAGE_RPC_TCP_RESPONSE`, `STAGE_RPC_UDP_RESPONSE`, nested `RpcFrameDecoder`, `RpcMessageParserStage`, `RpcTcpResponseStage`, and `RpcUdpResponseStage`.

Control flow: TCP frame decoder waits for a 4-byte record mark and full fragment, then retains and emits the fragment. Parser handles both `DatagramPacket` and TCP `ByteBuf`, builds an XDR read view, parses `RpcCall`, slices remaining bytes as procedure data, and releases malformed buffers. TCP response prepends a last-fragment record mark; UDP response wraps bytes in a datagram to the recipient.

State and persistence: static xid seed initialized from current time; frame decoder tracks `isLast`. No persistence.

Dependencies and integration: central to `SimpleTcpServer`, `SimpleUdpServer`, `Portmap`, and `SimpleTcpClient`. Depends on Netty and `XDR`.

Risks: `getNewXid` is not synchronized/atomic. `RpcFrameDecoder` does not assemble multi-fragment messages into one buffer despite tracking last-fragment state. Parser data slice lifetime depends on downstream retention/release discipline.

Test signals: `TestFrameDecoder` and RPC parser/server tests cover record marks, incomplete frames, malformed calls, and response stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpClient.java

Purpose: minimal Netty TCP client that connects to an RPC server and sends one XDR request.

Important APIs/types/functions: constructors, `setChannelHandler`, `run`, and `stop`.

Control flow: `run` creates a `NioEventLoopGroup`, configures `Bootstrap` with `NioSocketChannel`, installs frame decoder and `SimpleTcpClientHandler`, connects synchronously, and if `oneShot` waits for close and shuts down. `stop` waits on `closeFuture` then shuts down the worker group.

State and persistence: stores host, port, request, one-shot flag, worker group, and connection future; no persistence.

Dependencies and integration: base for `RegistrationClient`; used in tests and simple RPC flows.

Risks: interrupted exceptions are printed to stderr rather than logged or propagated. If `run` fails before creating `workerGroup`, `stop` may null-dereference in unusual paths. Long-lived non-one-shot users must call `stop`.

Test signals: integration tests cover simple client/server request flow and registration subclass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpClientHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpClientHandler.java

Purpose: default Netty handler for `SimpleTcpClient`, responsible for sending the XDR request on connection.

Important APIs/types/functions: constructor, `channelActive`, `channelRead`, and `exceptionCaught`.

Control flow: on active connection it writes the request using TCP record-mark framing. Default `channelRead` closes after any response, allowing subclasses to parse before close. Exceptions log a warning and close the channel.

State and persistence: stores the request; no persistence.

Dependencies and integration: used by `SimpleTcpClient`; subclassed by `RegistrationClientHandler`.

Risks: log message has a typo (`PRC`). `exceptionCaught` logs `cause.getCause()`, which can hide the actual exception when cause has no nested cause. Default handler discards response content.

Test signals: covered by simple TCP and registration client tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpClientHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpServer.java

Purpose: small Netty TCP server wrapper for ONC RPC programs.

Important APIs/types/functions: constructor, `run`, `getBoundPort`, and `shutdown`.

Control flow: `run` creates boss and worker event loop groups, configures `ServerBootstrap`, installs pipeline stages for RPC frame decoding, message parsing, RPC program handling, and TCP response framing, binds the requested port, and stores the actual bound port. `shutdown` closes the server channel and shuts down both groups.

State and persistence: stores configured and bound port, handler, channel, event loop groups, and worker count; no persistence.

Dependencies and integration: used to host `RpcProgram` implementations. Depends on `RpcUtil` stages and Netty server channels.

Risks: class comment says UDP server though implementation is TCP. Worker group uses `Executors.newCachedThreadPool`, so sizing must be controlled by Netty worker count. `shutdownGracefully` is not awaited.

Test signals: simple server and portmap/NFS-related integration tests cover binding and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleUdpClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleUdpClient.java

Purpose: blocking UDP client for sending a single XDR RPC request and validating an accepted reply.

Important APIs/types/functions: constructors and `run`.

Control flow: resolves host, serializes request bytes, uses a provided `DatagramSocket` or creates one, sends a packet, sets receive timeout, receives up to 65535 bytes, parses an `RpcReply`, and throws if reply state is not accepted. It closes only sockets it created.

State and persistence: stores host, port, request, one-shot flag, optional socket, and timeout; no persistence. `oneShot` is stored but not used in control flow.

Dependencies and integration: used by `RpcProgram` to register/unregister with local portmap.

Risks: timeout applies to the shared caller-provided socket too. It only checks reply state, not xid or accept state. Large UDP responses above buffer size would truncate at datagram level.

Test signals: portmap registration and UDP server tests cover request/response behavior and timeout configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleUdpClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleUdpServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleUdpServer.java

Purpose: small Netty UDP server wrapper for ONC RPC handlers.

Important APIs/types/functions: constructor, `run`, `getBoundPort`, and `shutdown`.

Control flow: `run` creates a worker event loop group, configures a `Bootstrap` with `NioDatagramChannel`, buffer sizes, broadcast and reuse options, installs parser/program/UDP-response stages, binds the port, and records the actual bound port. `shutdown` closes the channel and group.

State and persistence: stores configured port, handler, worker count, bound port, bootstrap, channel, and worker group; no persistence.

Dependencies and integration: used for UDP RPC services and portmap-like handlers. Depends on `RpcUtil` stages and Netty datagram channels.

Risks: response stage assumes `InetSocketAddress` recipients. `shutdownGracefully` is not awaited. Broadcast is enabled for all uses, which may be broader than needed.

Test signals: portmap and simple UDP integration tests cover binding, request parsing, response sending, and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleUdpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/XDR.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/XDR.java

Purpose: utility buffer for encoding and decoding External Data Representation messages per RFC 4506, plus ONC RPC TCP record-mark helpers.

Important APIs/types/functions: constructors, `State`, `asReadOnlyWrap`, `buffer`, `size`, primitive read/write methods, fixed/variable opaque read/write, string read/write, `verifyLength`, `recordMark`, `writeMessageTcp`, `writeMessageUdp`, `fragmentSize`, `isLastFragment`, and test-only `getBytes`.

Control flow: read methods assert `READING`; write methods ensure capacity and append big-endian values. Opaque reads/writes align to four-byte boundaries. `ensureFreeSpace` doubles buffer capacity until enough space remains. TCP message writing flips a duplicate of the write buffer and prepends a record mark; UDP writing copies a read-state buffer.

State and persistence: owns a mutable `ByteBuffer` and immutable read/write state; no persistence.

Dependencies and integration: foundational for all RPC, security, and portmap serialization. Uses Netty `ByteBuf` wrappers for transport.

Risks: state misuse throws precondition failures. `writeMessageUdp` requires reading state, while most writers produce writing state, so callers must wrap appropriately. `ensureFreeSpace` capacity math is unusual and should remain covered by growth tests. `readFixedOpaque` allocates exact-size arrays from wire lengths.

Test signals: `TestXDR` covers alignment, primitive/string/opaque round trips, record marks, fragment parsing, and capacity expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/XDR.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/package-info.java

Purpose: package-level documentation for Hadoop's ONC RPC implementation and simple UDP/TCP clients and servers.

Important APIs/types/functions: package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Evolving`.

Control flow: no runtime control flow.

State and persistence: none.

Dependencies and integration: participates in Javadocs and API audience metadata.

Risks: minimal; annotation changes affect downstream expectations.

Test signals: no direct tests required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/Credentials.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/Credentials.java

Purpose: abstract base and factory for ONC RPC credential auth blocks.

Important APIs/types/functions: `readFlavorAndCredentials`, `writeFlavorAndCredentials`, constructor, `mCredentialsLength`, and test-only `getCredentialLength`.

Control flow: factory reads an auth flavor integer and instantiates `CredentialsNone`, `CredentialsSys`, or `CredentialsGSS`, then delegates body parsing. Writer emits the flavor matching the runtime type and delegates body writing.

State and persistence: subclass instances track credential-body length; no persistence.

Dependencies and integration: used by `RpcCall` for request header parsing/writing and by security handlers.

Risks: unsupported flavors throw. Runtime-type dispatch means custom credential subclasses are not serializable without modifying this base. Error message for unrecognized credential says verifier.

Test signals: `TestCredentialsSys`, `TestRpcAuthInfo`, and `TestRpcCall` cover auth flavor parsing and writing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/Credentials.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsGSS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsGSS.java

Purpose: placeholder credential type for RPCSEC_GSS auth flavor.

Important APIs/types/functions: constructor, `read`, and `write`.

Control flow: constructor sets flavor to `RPCSEC_GSS`; read/write are currently empty TODO stubs.

State and persistence: no body fields are stored; inherited length is not updated.

Dependencies and integration: selected by `Credentials.readFlavorAndCredentials` when the wire flavor is `RPCSEC_GSS`.

Risks: this does not actually parse or emit RPCSEC_GSS credential bodies, so GSS-protected traffic needs higher-level handling elsewhere or will leave bytes unread/missing. Tests should pin this limitation to avoid assuming complete GSS support.

Test signals: auth-info tests can verify flavor recognition, but full GSS credential behavior is unimplemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsGSS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsNone.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsNone.java

Purpose: credential implementation for `AUTH_NONE`.

Important APIs/types/functions: constructor, `read`, and `write`.

Control flow: constructor sets credential length to zero. `read` consumes and validates a zero length. `write` emits zero length.

State and persistence: inherited length field only; no persistence.

Dependencies and integration: used by null-auth RPC calls such as portmap registration.

Risks: malformed nonzero length triggers precondition failure. No body bytes are skipped if length is invalid.

Test signals: RPC call and auth-info tests cover zero-length behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsNone.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsSys.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsSys.java

Purpose: credential implementation for ONC RPC `AUTH_SYS`, carrying host, uid, gid, auxiliary gids, and stamp.

Important APIs/types/functions: constructor, getters/setters for uid/gid/stamp/host, `read`, and `write`.

Control flow: static initialization captures local host name. `read` consumes credential length, stamp, hostname string, uid, gid, aux group count, and each aux gid. `write` computes padded credential length, writes stamp, hostname, uid, gid, aux group count, and aux gid list.

State and persistence: mutable credential fields in memory; no persistence.

Dependencies and integration: consumed by `SysSecurityHandler` and request parsing. Uses `XDR` string alignment and UTF-8 hostname bytes.

Risks: static host lookup failure throws at class load. `read` trusts aux group count and can allocate large arrays from malformed input. Credential length is computed but not validated against bytes read. Hostname setter is test-visible only.

Test signals: `TestCredentialsSys` covers length calculation, host/stamp fields, uid/gid/aux groups, and round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsSys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/RpcAuthInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/RpcAuthInfo.java

Purpose: abstract base for ONC RPC auth credential and verifier objects.

Important APIs/types/functions: `AuthFlavor` enum, `fromValue`, constructor, abstract `read`/`write`, `getFlavor`, and `toString`.

Control flow: `AuthFlavor.fromValue` scans enum constants by protocol value and throws for unknown values.

State and persistence: immutable auth flavor; no persistence.

Dependencies and integration: parent of `Credentials` and `Verifier`; used by RPC call/reply serialization.

Risks: supported enum includes flavors that not all subclasses implement. Protocol numeric values are explicit and must remain stable.

Test signals: `TestRpcAuthInfo` covers flavor value mapping and invalid flavor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/RpcAuthInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/SecurityHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/SecurityHandler.java

Purpose: abstract per-request security adapter used by ONC RPC services to map credentials to users, decide drops, produce verifiers, and optionally wrap/unwrap GSS payloads.

Important APIs/types/functions: abstract `getUser`, `shouldSilentlyDrop`, `getVerifer`; defaults `isUnwrapRequired`, `isWrapRequired`, `unwrap`, `wrap`, `getUid`, `getGid`, and `getAuxGids`.

Control flow: base defaults indicate no wrapping and throw `UnsupportedOperationException` for GSS and AUTH_SYS-specific operations unless overridden.

State and persistence: no fields; subclasses provide state.

Dependencies and integration: used by NFS/ONC RPC service implementations. Depends on `RpcCall`, `Verifier`, and `XDR`.

Risks: method name `getVerifer` is misspelled and is part of the API. Callers must check `isWrapRequired`/`isUnwrapRequired` before invoking default throwing methods. AUTH_SYS getters throw unless subclass is `SysSecurityHandler`.

Test signals: subclass tests and service tests should verify user mapping, verifier creation, and drop/wrap decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/SecurityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/SysSecurityHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/SysSecurityHandler.java

Purpose: `SecurityHandler` implementation for `AUTH_SYS` credentials.

Important APIs/types/functions: constructor, `getUser`, `shouldSilentlyDrop`, `getVerifer`, `getUid`, `getGid`, and `getAuxGids`.

Control flow: maps uid to a username via `IdMappingServiceProvider`, returns false for silent drop, returns a new `VerifierNone`, and exposes uid/gid/aux gids from `CredentialsSys`.

State and persistence: stores credential object and ID mapping provider references; no persistence in this class.

Dependencies and integration: used by NFS/ONC RPC services that accept AUTH_SYS. Depends on Hadoop security ID mapping.

Risks: user identity depends on external id mapping configuration and cache. The handler does not authorize by itself; it only exposes identity attributes. Returns a new verifier each call rather than singleton.

Test signals: service security tests should cover uid-to-user fallback and gid/aux gid propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/SysSecurityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/Verifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/Verifier.java

Purpose: abstract base and factory for ONC RPC verifier auth blocks.

Important APIs/types/functions: constructor, `readFlavorAndVerifier`, and `writeFlavorAndVerifier`.

Control flow: factory reads flavor, maps `AUTH_NONE` to `VerifierNone`, treats `AUTH_SYS` verifier flavor as `VerifierNone` for compatibility, maps `RPCSEC_GSS` to `VerifierGSS`, then delegates body read. Writer supports `VerifierNone` and `VerifierGSS`.

State and persistence: only inherited flavor; no persistence.

Dependencies and integration: used by `RpcCall`, `RpcReply`, and security handlers.

Risks: unsupported verifier flavors throw. Mapping AUTH_SYS to VerifierNone still calls `VerifierNone.read`, expecting zero length after the AUTH_SYS flavor. Runtime-type dispatch blocks custom verifier subclasses.

Test signals: `TestRpcAuthInfo`, `TestRpcReply`, and call/reply tests cover flavor parsing and writer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/Verifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/VerifierGSS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/VerifierGSS.java

Purpose: placeholder verifier type for RPCSEC_GSS.

Important APIs/types/functions: constructor, `read`, and `write`.

Control flow: constructor sets flavor to `RPCSEC_GSS`; read/write are empty TODO stubs.

State and persistence: no verifier body state; no persistence.

Dependencies and integration: selected by `Verifier.readFlavorAndVerifier` and emitted by `Verifier.writeFlavorAndVerifier`.

Risks: does not parse or serialize GSS verifier payloads, so using it without additional wrapping logic can leave wire bytes unread or responses incomplete.

Test signals: auth flavor recognition can be tested, but full GSS verifier behavior is unimplemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/VerifierGSS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/VerifierNone.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/VerifierNone.java

Purpose: verifier implementation for `AUTH_NONE`.

Important APIs/types/functions: singleton `INSTANCE`, constructor, `read`, and `write`.

Control flow: `read` consumes a length and requires zero. `write` emits zero length.

State and persistence: no body state; no persistence.

Dependencies and integration: used in most portmap and accepted/denied replies, and by `SysSecurityHandler`.

Risks: public constructor allows multiple instances despite singleton. Malformed nonzero length throws precondition failure.

Test signals: reply and auth-info tests cover zero-length read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/VerifierNone.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/package-info.java

Purpose: package-level documentation for ONC RPC security implementation.

Important APIs/types/functions: package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Evolving`.

Control flow: no runtime control flow.

State and persistence: none.

Dependencies and integration: used by Javadocs and API metadata.

Risks: minimal; annotations set consumer expectations.

Test signals: no direct tests required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/Portmap.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/Portmap.java

Purpose: standalone portmap/rpcbind service entry point for binding RPC program/version/transport tuples to ports.

Important APIs/types/functions: `main`, `start`, `shutdown`, test-visible address getters, and `getHandler`.

Control flow: `main` starts TCP and UDP listeners on port 111. `start` creates Netty boss/worker/UDP groups, configures a TCP pipeline with RPC frame decoder, parser, idle handler, portmap handler, and TCP response stage, configures a UDP pipeline with logging, parser, handler, and UDP response stage, binds both addresses, stores channels, and adds them to a channel group. `shutdown` closes all channels and shuts down groups.

State and persistence: process-local Netty bootstraps, channel group, channels, event loops, and one `RpcProgramPortmap` handler. Port mappings live in the handler only and are not persisted.

Dependencies and integration: depends on `RpcUtil`, `RpcProgramPortmap`, Netty, and `RpcProgram.RPCB_PORT`. Used by tests and can run as a daemon.

Risks: class is package-private final. Shutdown assumes groups were initialized. Binding privileged port 111 requires appropriate permissions. UDP and TCP maps are shared through one handler.

Test signals: `TestPortmap` covers startup on test ports, handler access, set/unset/get/dump behavior, and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/Portmap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapMapping.java

Purpose: immutable value object for one portmap mapping tuple: program, version, transport, and port.

Important APIs/types/functions: constants `TRANSPORT_TCP` and `TRANSPORT_UDP`, constructor, `serialize`, static `deserialize`, `getPort`, static `key`, and `toString`.

Control flow: serialization writes four integers to XDR; deserialization reads four integers. `key` joins program, version, and transport, intentionally excluding port so set/unset/getport address the mapping identity.

State and persistence: immutable fields; no persistence. Instances are stored in `RpcProgramPortmap`'s in-memory map.

Dependencies and integration: used by `PortmapRequest`, `PortmapResponse`, `RpcProgram`, and `RpcProgramPortmap`.

Risks: no validation of transport, version, program, or port ranges. No equals/hashCode, so map identity uses string keys rather than object keys.

Test signals: portmap tests cover serialization, key behavior, and getport values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapRequest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapRequest.java

Purpose: helper for parsing and constructing portmap SET/UNSET requests.

Important APIs/types/functions: static `mapping` and `create`.

Control flow: `mapping` deserializes a `PortmapMapping` from the current XDR position. `create` builds an `RpcCall` with a new xid, portmap program/version, `PMAPPROC_SET` or `PMAPPROC_UNSET`, null credentials and verifier, writes it to XDR, then serializes the mapping body.

State and persistence: stateless utility; no persistence.

Dependencies and integration: used by `RpcProgram.register`/`unregister` and `RpcProgramPortmap` request handling. Depends on `RpcUtil.getNewXid`, `CredentialsNone`, and `VerifierNone`.

Risks: only supports SET/UNSET creation. Xid generation is inherited from non-atomic `RpcUtil`. Caller must send over the correct transport.

Test signals: portmap and RPC call tests cover request encoding and mapping parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapResponse.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapResponse.java

Purpose: helper for writing accepted portmap responses with typed result payloads.

Important APIs/types/functions: `voidReply`, `intReply`, `booleanReply`, and `pmapList`.

Control flow: each method writes a successful `RpcAcceptedReply` with `VerifierNone`, then appends the requested payload. `pmapList` writes a linked-list style sequence of boolean-present markers plus serialized mappings, terminated by false.

State and persistence: stateless utility; no persistence.

Dependencies and integration: used by `RpcProgramPortmap` procedures to build XDR responses.

Risks: always emits success; callers must choose other reply paths for procedure unavailable or errors. `pmapList` order follows array order from the caller, which for concurrent map values is not deterministic.

Test signals: `TestPortmap` and XDR tests cover reply encoding and list termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsck.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsck.java

## Purpose
`RouterFsck` exposes a federated FSCK wrapper. Instead of checking local namespace state, it discovers active NameNodes from the federation state store and proxies the incoming `/fsck` query to each active NameNode web endpoint, streaming their output back to the caller.

## Important APIs, Types, and Functions
The constructor captures the `Router`, query parameter map, response `PrintWriter`, and remote address. `fsck` is the public execution method. `remoteFsck` builds the downstream URL from `MembershipState.getWebScheme`, `getWebAddress`, and `getURLArguments`, then copies UTF-8 lines from the downstream response. `getURLArguments` serializes the first value for each query key.

## Control Flow
`fsck` logs and prints an unstable-feature warning and start banner, obtains `MembershipStore` from the router state store, reads all Namenode registrations, sorts them, and invokes `remoteFsck` only for `ACTIVE` memberships. Per-namenode IO failures are printed and do not abort the whole run. Top-level exceptions produce an end banner and error text, and the writer is always closed.

## State and Persistence Behavior
This class stores no durable data. It reads live membership records from the state store and streams remote HTTP data. It does not cache membership or FSCK responses.

## Dependencies and Integration Points
It integrates with `StateStoreService`, `MembershipStore`, `GetNamenodeRegistrations*`, `MembershipState`, `FederationNamenodeServiceState`, NameNode web `/fsck`, and the servlet wrapper that supplies the authenticated user context.

## Risks
`getURLArguments` does not URL-encode keys or values and only uses `value[0]`, which can mis-handle special characters or repeated parameters. FSCK output is streamed serially, so a slow NameNode delays the whole response. There is no explicit connection/read timeout here. The writer is closed by this helper, which is suitable for servlet ownership but important for callers. The feature is explicitly logged as unstable.

## Test Signals
Tests should exercise active-only filtering, membership sorting, downstream URL construction including schemes and query arguments, handling of individual NameNode IO failures, top-level exception reporting, writer closure, and behavior for empty membership sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsck.java -->

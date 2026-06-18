<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetUtils.java

## Purpose
`NetUtils` is Hadoop's broad network utility class for socket factories, address parsing/canonicalization, static host overrides, socket I/O wrappers, connect behavior, hostname normalization, exception diagnostics, subnet matching, and free-port helpers.

## Important APIs and Types
Major APIs include `getSocketFactory`, `getDefaultSocketFactory`, `getSocketFactoryFromProperty`, `createSocketAddr` variants, `createSocketAddrUnresolved`, `createSocketAddrForHost`, `getCanonicalUri`, static resolution getters/setters, `getConnectAddress`, socket input/output stream wrappers, `connect`, hostname/IP normalization, `verifyHostnames`, host/port formatting, local-address checks, `wrapException`, `addNodeNameToIOException`, subnet helpers, `getFreeSocketPort(s)`, and `bindToLocalAddress`.

## Control Flow
Address creation trims input, wraps bare `host:port` with a dummy URI scheme, validates host/port/path, uses an optional short-lived URI cache, and either resolves through `SecurityUtil.getByName` or creates an unresolved socket address. `connect` optionally binds a local address, uses normal socket connect or Hadoop `SocketIOWithTimeout` for channels, converts connect timeouts, maps unresolved addresses to `UnknownHostException`, and rejects accidental loopback self-connections. `wrapException` detects common socket/ACL exception types and creates same-type exceptions with richer diagnostics and wiki links when possible.

## State and Persistence
Static state includes host-to-static-resolution mappings, a bounded expiring URI cache, and a concurrent canonicalized hostname cache. No durable persistence exists.

## Dependencies and Integration Points
This class is central to Hadoop RPC, IPC server clients, metrics sinks such as StatsD, filesystem URI handling, security-aware resolution, and test port allocation. It integrates with `SocketInputStream`, `SocketOutputStream`, `SocketIOWithTimeout`, `SecurityUtil`, Apache Commons `SubnetUtils`, Guava cache, and dynamic constructors.

## Risks and Test Signals
`getPortFromHostPortString` and IP regex helpers are IPv4/simple-host oriented and can mishandle IPv6. Static and canonical host caches can become stale. Free-port helpers are inherently race-prone. Tests should cover URI forms with and without schemes, unresolved address creation, static host aliases, canonical URI defaults, socket channel and plain-socket connect paths, loopback self-connect detection, exception wrapping by type, hostname verification, subnet matching including subinterfaces, free-port bounds, and wildcard bind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetUtils.java -->

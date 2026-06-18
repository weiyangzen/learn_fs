# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestNetUtils.java

## Purpose
Broad unit coverage for `NetUtils`: loopback connection prevention, invalid host handling, socket read timeouts, local address detection, hostname verification, exception wrapping, socket address parsing, static resolution, resolver search-order behavior, canonical URI generation, host normalization, host/port parsing, local binding, and IOException message decoration.

## Important APIs, Types, And Functions
Uses `NetUtils.connect()`, `getInputStream()`, `getLocalInetAddress()`, `verifyHostnames()`, `isLocalAddress()`, `wrapException()`, `createSocketAddr()`, `createSocketAddrForHost()`, `getConnectAddress()`, `getCanonicalUri()`, `normalizeHostNames()`, `getHostNameOfIP()`, `getPortFromHostPortString()`, `bindToLocalAddress()`, and `addNodeNameToIOException()`. Test DNS behavior is driven by `NetUtilsTestResolver.install()`.

## Control Flow
The file first tests real socket behavior and timeout wrappers, then validates exception-message enrichment for multiple `IOException` subclasses. Resolver tests install a custom resolver globally, reset it before each test, and inspect the exact search suffix sequence for qualified/unqualified names. Later tests verify canonical URI host/port rewriting, hostname normalization, and exception cloning/decorating behavior.

## State And Persistence Behavior
Global state includes installed `NetUtilsTestResolver`, static host resolutions, and cached URI/host behavior. Socket tests create and close real sockets. Configuration is reset before each resolver test.

## Dependencies And Integration Points
Integrates with Java sockets, DNS resolution, Hadoop configuration, security exception types, shell Java-version checks, and URI normalization used by Hadoop clients.

## Risks
Environment-sensitive areas include local network interfaces, external DNS for `1.kanyezone.appspot.com`, Java-version-specific unresolved-host exception text, and timing thresholds. Custom resolver installation is global and must be reset. Exception wrapping depends on reflective constructors and class accessibility.

## Test Signals
Signals include loopback self-connect rejection, read timeouts within `TIME_FUDGE_MILLIS`, wrapped messages containing wiki/local/remote details, exact resolver search arrays, canonical URIs using `host.a.b`, normalized `localhost` to `127.0.0.1`, and inaccessible private exception classes returning the original exception.

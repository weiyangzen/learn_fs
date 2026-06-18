# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/FederationUtil.java

## Purpose
`FederationUtil` is a static utility holder for Router-Based Federation support code. It centralizes JMX retrieval from NameNode web endpoints, build/version reporting, reflective construction of configurable federation components, mount-point `HdfsFileStatus` rewriting, fairness-controller construction, and parsing configured nameservices from `dfs.federation.router.monitor.namenode`.

## Important APIs, Types, And Functions
- `getJmx(String, String, URLConnectionFactory, String)` builds `/jmx?qry=...` URLs, opens secure-aware HTTP(S) connections, reads JSON, and returns the `beans` array.
- `newFileSubclusterResolver`, `newActiveNamenodeResolver`, `newSecretManager`, and `newFairnessPolicyController` load configured classes from `RBFConfigKeys` and instantiate them reflectively.
- Private `newInstance` supports no-arg, `Configuration`, and `(Configuration, context)` constructors.
- `updateMountPointStatus` rebuilds an `HdfsFileStatus` while replacing the child count.
- `getAllConfiguredNS` extracts nameservice IDs from `ns` or `ns.nn` monitor entries and rejects malformed dotted names.

## Control Flow
JMX calls parse host and optional port, create a `URL`, open a connection using security mode, enforce 5 second connect/read timeouts, buffer all response text, and parse it through Jettison JSON. Reflective factory methods read class keys, call `newInstance`, and return null on reflective failure after logging. `getAllConfiguredNS` iterates configured monitor entries and normalizes each entry to a nameservice identifier.

## State And Persistence
The class owns no durable state. All returned objects are newly constructed or derived from inputs. JMX data is transient. Errors are logged and usually converted to `null`, so callers must handle absent utility results.

## Dependencies And Integration Points
It integrates with `Router`, `StateStoreService`, `FileSubclusterResolver`, `ActiveNamenodeResolver`, delegation token secret managers, `RouterRpcFairnessPolicyController`, `HdfsFileStatus`, and `RBFConfigKeys`. `NamenodeHeartbeatService` uses `getJmx` for NameNode metrics, while `Router` uses the resolver factories during initialization.

## Risks And Edge Cases
`getJmx` has broad exception handling and returns null on network, parsing, or unexpected errors, so downstream metric population must tolerate stale or absent arrays. `webAddress.split(":")` assumes simple host:port input and is not IPv6-safe. Reflective construction hides type-constructor mismatches as null, which can delay failure until router initialization checks. `getAllConfiguredNS` throws on names with more than one dot, which is correct for the configured `ns.nn` syntax but strict for accidental FQDN-like values.

## Test Signals
Fairness controller factory behavior is exercised by fairness tests such as `TestRouterRpcFairnessPolicyController`, `TestProportionRouterRpcFairnessPolicyController`, and async fairness tests. `getAllConfiguredNS` behavior is indirectly covered by router heartbeat/monitoring tests that configure `DFS_ROUTER_MONITOR_NAMENODE`. JMX behavior is indirectly covered through `TestRouterNamenodeHeartbeat` and web-scheme tests.

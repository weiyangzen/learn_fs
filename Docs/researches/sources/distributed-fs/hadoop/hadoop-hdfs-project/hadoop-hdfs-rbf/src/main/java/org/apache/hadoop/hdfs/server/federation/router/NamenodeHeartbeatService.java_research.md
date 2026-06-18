# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NamenodeHeartbeatService.java

## Purpose
`NamenodeHeartbeatService` periodically probes one NameNode and registers its namespace, address, HA state, safemode state, storage, datanode, and corruption metrics with the active NameNode resolver/state store. Routers use these records to choose active NameNodes and expose federation health.

## Important APIs, Types, And Functions
- Constructors identify a nameservice and optional NameNode ID; the resolved-host constructor creates a synthetic NameNode ID for DNS-expanded monitor targets.
- `serviceInit` resolves RPC, service RPC, lifeline, and web addresses, creates an `NNHAServiceTarget` for HA NameNodes, sets heartbeat and JMX intervals, and initializes URL connection factory/scheme.
- `periodicInvoke` runs `updateState` as the login user.
- `getNamenodeStatusReport` builds a `NamenodeStatusReport` and populates namespace info, safemode, JMX metrics, and HA status.
- `updateNameSpaceInfoParameters`, `updateSafeModeParameters`, `updateJMXParameters`, and `updateHAStatusParameters` isolate the individual probes.

## Control Flow
Each tick creates a report, calls the NameNode protocol `versionRequest` first, and stops early if namespace registration is invalid. Safemode is fetched through `ClientProtocol`, JMX is refreshed only when enabled and the configured interval has elapsed, and HA state is fetched through a cached health monitor proxy. If a HA-enabled target cannot report HA state, the service leaves the current resolver state unchanged; otherwise it registers the report through `ActiveNamenodeResolver.registerNamenode`.

## State And Persistence
The service caches RPC protocol proxies, JMX arrays, last JMX update attempt time, address strings, and health-monitor timeout. Proxies are reset to null on their respective failures so future ticks recreate them. Durable federation state is written indirectly through the resolver/state store registration path.

## Dependencies And Integration Points
It integrates with `PeriodicService`, `ActiveNamenodeResolver`, `NamenodeStatusReport`, `NameNodeProxies`, `NamenodeProtocol`, `ClientProtocol`, `NNHAServiceTarget`, `HAServiceProtocol`, `FederationUtil.getJmx`, `DFSUtil`, `DFSHAAdmin`, `URLConnectionFactory`, and router monitor configuration keys. `Router.createNamenodeHeartbeatServices` owns service creation.

## Risks And Edge Cases
Address fallback is important: absent service RPC falls back to client RPC, absent lifeline falls back to service RPC. DNS resolution mode clones a configured NameNode across resolved hosts and rewrites ports from configured addresses. JMX failures are logged but stale cached metrics may continue to populate reports. `updateHAStatusParameters` calls `e.getMessage().startsWith(...)`; a throwable with null message could fail this branch. Health-monitor timeout is coerced to zero for negative config values.

## Test Signals
`TestRouterNamenodeHeartbeat` covers lifecycle, local NameNode discovery, HA failover reporting, HA service/lifeline address selection, DNS resolution, and security-enabled heartbeat registration. `TestRouterNamenodeMonitoring` and `TestRouterNamenodeWebScheme` provide additional monitor and HTTP/HTTPS scheme coverage.

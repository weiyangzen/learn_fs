# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterWebHdfsMethods.java

## Purpose
`RouterWebHdfsMethods` adapts WebHDFS REST requests for the Router. It reuses `NamenodeWebHdfsMethods` for many metadata operations while adding Router-specific Datanode redirects for data-transfer operations such as create, append, open, and checksum.

## Important APIs and Types
The class extends `NamenodeWebHdfsMethods`, is rooted at JAX-RS `@Path("")`, and overrides `init`, `getRpcClientProtocol`, `queueExternalCall`, `put`, `post`, `get`, and `createCredentials`. Router-specific helpers include `redirectURI`, `chooseDatanode`, `getNsFromDataNodeNetworkLocation`, and `getRandomDatanode`.

## Control Flow
The constructor captures HTTP method, query, servlet path, and remote address. `getRpcClientProtocol` returns the Router RPC server or throws `RetriableException` during startup. `put`, `post`, and `get` whitelist supported WebHDFS operations. `CREATE`, `APPEND`, `OPEN`, and `GETFILECHECKSUM` build a redirect URI to a selected Datanode unless `noredirect` requests a JSON location. `chooseDatanode` reads the cached live Datanode report from `RouterRpcServer`, determines the target namespace for create using `getCreateLocation` (sync or async via `syncReturn`), excludes caller-provided Datanodes and non-target namespaces, and for read/append/checksum prefers a Datanode from the file's located blocks. Otherwise it chooses a random non-excluded Datanode.

## State and Persistence
It stores per-request fields for remote address and request metadata. It does not persist state. Token credentials are generated through `RouterSecurityManager.createCredentials`.

## Dependencies and Integration Points
It integrates servlet/JAX-RS request handling, `NamenodeWebHdfsMethods`, `Router`, `RouterRpcServer`, `ClientProtocol`, `RouterSecurityManager`, `JsonUtil`, WebHDFS resource params, cached Datanode reports, and HDFS block location APIs.

## Risks
Datanode namespace filtering relies on `RouterRpcServer.updateDnMap` prefixing network locations as `/ns/rack`; malformed or stale locations make `getNsFromDataNodeNetworkLocation` return empty and can misroute create redirects. `getRandomDatanode` instantiates `Random` in a loop and returns null if all nodes are excluded. `reset()` clears only `remoteAddr`; other captured request fields are unused but stale if instances are reused. Redirect security depends on correct delegation-token handling for secure and insecure clusters.

## Test Signals
Tests should cover supported/unsupported WebHDFS operation whitelists, `noredirect` JSON location responses, secure vs insecure delegation query construction, create redirects constrained to resolved namespace, open offset validation, excludeDatanodes filtering, network-location namespace parsing, and startup-mode `RetriableException`.

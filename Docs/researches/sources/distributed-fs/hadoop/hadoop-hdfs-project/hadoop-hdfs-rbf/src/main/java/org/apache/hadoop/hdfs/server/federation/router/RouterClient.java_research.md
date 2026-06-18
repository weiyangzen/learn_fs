# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClient.java

## Purpose
`RouterClient` is a closeable admin-protocol client for connecting to a router's admin RPC server. It is used by router internals and tools to access mount table, router state, nameservice, and generic admin managers.

## Important APIs, Types, And Functions
- `createRouterProxy` configures protobuf RPC engine, creates a `RouterAdminProtocolPB` proxy, and wraps it in `RouterAdminProtocolTranslatorPB`.
- The constructor captures the current UGI and creates the proxy for a given admin address.
- `getMountTableManager`, `getRouterStateManager`, `getNameserviceManager`, and `getRouterGenericManager` expose the translator through narrower interfaces.
- `close` stops the RPC proxy.

## Control Flow
Construction sets protocol engine and gets a versioned protocol proxy using the configured socket factory and RPC timeout. Manager getters simply return the translator. Close is synchronized and calls `RPC.stopProxy`.

## State And Persistence
The client stores a translator proxy and the current user. It owns no persistent state. Remote calls persist data through `RouterAdminServer` and state-store-backed managers.

## Dependencies And Integration Points
It depends on Hadoop IPC, `RouterAdminProtocolPB`, `RouterAdminProtocolTranslatorPB`, `MountTableManager`, `RouterStateManager`, `NameserviceManager`, `RouterGenericManager`, `NetUtils`, and `UserGroupInformation`. `MountTableRefresherService` caches `RouterClient` instances for remote cache refreshes.

## Risks And Edge Cases
The captured `ugi` is used at proxy creation time; long-lived cached clients in secure clusters depend on the refresher service recreating clients after expiration and relogin. `fallbackToSimpleAuth` is local to proxy creation and not exposed. Calling getters after `close` returns a stopped proxy reference, so owners must manage lifecycle.

## Test Signals
Admin CLI tests, router admin tests, disabled nameservice tests, and mount-table cache refresh tests cover proxy usage. Secure cache refresh tests are especially relevant because this client is cached and closed by `MountTableRefresherService`.

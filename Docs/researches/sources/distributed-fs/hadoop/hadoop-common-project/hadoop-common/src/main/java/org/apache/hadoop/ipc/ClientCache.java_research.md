# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ClientCache.java

## Purpose

`ClientCache` provides shared `Client` instances keyed by `SocketFactory` for Hadoop RPC engines. It avoids creating independent connection pools for every proxy while reference counting users.

## Important APIs, control flow, and state

The cache stores `Map<SocketFactory, Client>`. `getClient(conf, factory, valueClass)` is synchronized: it creates a `Client` if absent or increments the existing client's ref count, then returns it. Convenience overloads use the default socket factory and `ObjectWritable` response class. `stopClient(Client)` decrements the client ref count under the cache lock, removes it when count reaches zero, and then calls `client.stop()` outside the lock. `clearCache()` stops all cached clients and clears the map for tests.

## Dependencies and integration points

`ProtobufRpcEngine` and `ProtobufRpcEngine2` use this cache for client reuse. It depends on `Client`, `SocketFactory`, `ObjectWritable`, `Writable`, and Hadoop configuration.

## Risks and test signals

The key excludes `Configuration` and response `valueClass`, so the first client created for a socket factory controls timeouts and value class for later users. The comment calls out the tradeoff: reuse connection pools while accepting global-ish IPC configuration. Clear-cache is unsynchronized, so it should remain test-only or externally serialized. RPC engine lifecycle tests and client reference count tests are the primary signals.

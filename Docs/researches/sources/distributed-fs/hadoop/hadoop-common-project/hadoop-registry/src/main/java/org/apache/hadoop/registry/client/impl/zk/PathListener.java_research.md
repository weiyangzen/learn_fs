# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/PathListener.java

## Purpose
`PathListener` is a tiny callback interface for components interested in registry path changes detected through the Curator cache.

## Important APIs and types
It declares `nodeAdded(String path)` and `nodeRemoved(String path)`, both throwing `IOException`. Paths passed by `CuratorService.registerPathListener()` are absolute ZooKeeper paths from Curator event data, not necessarily registry-root-relative paths.

## Control flow
Implementations are invoked from Curator cache create/change and delete callbacks. The main implementation in this subset is the anonymous listener in `RegistryDNSServer.manageRegistryDNS()`, which resolves new records and removes DNS records when znodes disappear.

## State and persistence behavior
The interface has no state. Its persistence effect depends entirely on implementations; in `RegistryDNSServer`, it causes DNS zone mutations based on ZooKeeper registry content.

## Dependencies and integration points
It depends only on `java.io.IOException`. It connects the ZooKeeper client layer to server-side consumers without coupling `CuratorService` to DNS or registry administration logic.

## Risks and test signals
Because callbacks can throw `IOException`, caller code must decide whether to swallow, wrap, or propagate failures. Tests should assert that listener implementers receive both create/update and delete events with expected path form, and that exceptions do not silently corrupt downstream caches.

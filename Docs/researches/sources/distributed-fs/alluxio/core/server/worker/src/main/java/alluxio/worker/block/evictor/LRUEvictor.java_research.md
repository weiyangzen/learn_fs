# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/LRUEvictor.java

Purpose: Deprecated LRU evictor implementation backed by an access-ordered `LinkedHashMap`.

Important APIs: Constructor preloads evictable existing blocks; `getBlockIterator` returns a snapshot in LRU order; event callbacks update or remove IDs from the LRU map.

Control flow: Access and local commit insert into the access-ordered map, moving entries to the tail. Remove and lost events delete entries. `AbstractEvictor` consumes the snapshot iterator from least to most recently used.

State and persistence: Maintains a synchronized access-ordered map in memory. The map is rebuilt from metadata when the evictor is constructed.

Dependencies and integration: Extends `AbstractEvictor`, consumes storage evictor views, and can be wrapped by `EmulatingBlockIterator`.

Risks and test signals: Snapshot iteration may lag concurrent events, and the implementation is marked not thread-safe despite a synchronized map. Tests should cover preload filtering, event updates, remove callbacks, and order after repeated accesses.

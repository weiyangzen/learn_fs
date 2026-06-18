# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/BlockStreamTracker.java

Purpose: Static event hub for block reader and writer open/close events.

Important APIs: `registerListener`, `unregisterListener`, `readerOpened`, `readerClosed`, `writerOpened`, and `writerClosed`.

Control flow: Store reader and writer wrappers call the open/close methods, which synchronously notify all registered `BlockClientListener`s.

State and persistence: Holds a static `CopyOnWriteArrayList` of listeners. No persisted state.

Dependencies and integration: Feeds `DefaultStoreLoadTracker`, which uses stream activity to pause background management transfers.

Risks and test signals: Listener callbacks run inline and can delay close/open paths if expensive. Tests should cover registration removal, multiple listeners, open/close symmetry, and no concurrent modification failures.

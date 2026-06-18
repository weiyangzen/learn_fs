# sources/distributed-fs/beegfs/meta/source/app/App.cpp

Purpose: `App.cpp` implements the BeeGFS metadata daemon lifecycle. It owns startup, configuration, storage initialization, node registration, management-state download, component creation, shutdown, session persistence, and signal handling.

Important APIs/functions: `run()` constructs `Config` and maps exceptions to app result codes. `runNormal()` sequences the daemon: optional NUMA bind, `preinitStorage()`, logging, UUID check, local node ID loading, data object creation, network setup, metadata layout creation, root/disposal dir loading or creation, signal registration, daemonization, RDMA discovery, mgmtd wait/preregistration, local node setup, management info download, optional `FileEventLogger`, session restore, component startup/join, session store, and final client sync. Initialization helpers create node stores, target mappers, state stores, capacity pools, queues, `MetaStore`, hashed metadata directories, and listeners/workers/syncers. Shutdown helpers stop and join components in dependency order.

Control flow: Startup is deliberately staged so disk locks happen before logging, RDMA device opening happens after daemon fork, mgmtd registration precedes state downloads, and worker shutdown follows modification-event and resync shutdown. `stopComponents()` avoids blocking because it may run from a signal handler.

State and persistence behavior: Persistent state includes the metadata directory, storage format file, node number ID file, registration token, root/disposal inodes, session backup files, optional event queue, and filesystem UUID check. It writes session files on clean shutdown and removes restored session files after startup.

Dependencies/integration: The app integrates common networking, `NetMessageFactory`, `MetaStore`, `SessionStore`, `InternodeSyncer`, `DatagramListener`, stream listeners, workers, `BuddyResyncer`, `ChunkBalancerJob`, timers, and file-event logging. Risks include startup ordering regressions, double deletion (`timerQueue` is deleted through `SAFE_DELETE` and later raw `delete timerQueue` in the destructor), partial shutdown from signal context, stale session-file handling, and mismatched target UUID or storage format.

Test signals: Direct tests are not in this file. Coverage comes from component tests, config tests, serialization tests, and integration/runtime behavior.

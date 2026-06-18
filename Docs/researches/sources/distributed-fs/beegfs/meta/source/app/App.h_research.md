# sources/distributed-fs/beegfs/meta/source/app/App.h

Purpose: `App.h` declares the metadata daemon's central application object and exposes accessors used by nearly every metadata component.

Important APIs/types: `App` derives from `AbstractApp` and overrides `run()`, `stopComponents()`, component exception handling, network-interface failure handling, and `getStreamListenerByFD()`. It defines result codes, worker/listener container typedefs, and a large object graph: config/logging, local node, node stores, root info, capacity pools, target and buddy mappers, state stores, storage pools, work queues, message factory, metadata store, root/disposal dirs, sessions, acknowledgments, stats, metadata path objects, datagram/stream listeners, syncers, timers, workers, buddy resyncer, chunk balancer, quota stores, and file-event logger.

Control flow contract: Private methods are grouped by lifecycle phase: init logging/data/network/storage/components, start/stop/join/delete workers and listeners, mgmtd registration/download, daemonization, signal handling, and session restore/store/delete. Public getters make these shared objects globally available through `Program::getApp()`.

State and persistence behavior: The header documents ownership of persistent metadata paths (`inodes`, `dentries`, buddy-mirror variants), root/disposal inodes, session stores, and file-event logger state. Most members are raw pointers with destructor-managed ownership; `storagePoolStore` and `fileEventLogger` are `unique_ptr`s.

Dependencies/integration: Because many components reach into `App`, this header is a high-coupling integration point. It mediates access to network filters, node stores, target states, queues, and timers.

Risks and test signals: Raw-pointer ownership and broad public access increase lifetime and ordering risk. `getStreamListenerByFD()` assumes `numStreamListeners > 0` and a populated vector. Tests need integration coverage because many invariants are cross-member rather than local.

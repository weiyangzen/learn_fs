# sources/distributed-fs/beegfs/client_module/source/components/InternodeSyncer.c

## Purpose
Implements the main client background synchronization thread for management discovery, registration, topology refresh, target states, delayed remote cleanup, NIC changes, and idle connection cleanup.

## Important APIs and control flow
Startup initializes app stores, delayed queues, force-state mutex, and target-state timeout. `__InternodeSyncer_run` performs management init, enters the periodic request loop, signals init completion on exit, and unregisters if registered. `_InternodeSyncer_requestLoop` runs timed tasks: retry management init, check network changes and force reregistration, reregister heartbeats, download/sync nodes and target mappings, update metadata/storage states and buddy groups, retry delayed close/unlock queues, and drop idle connections. Management init waits for heartbeat via UDP, downloads topology/state, registers over request/response, and repeats downloads to avoid notification races. Registration updates local numeric node ID, management gRPC port, and fs UUID.

## State, dependencies, integration
State includes management/meta/storage node stores, datagram listener, `mgmtInitDone` condition, `nodeRegistered`, forced target-state update flag, last successful state update time, and three delayed operation queues. It integrates with `NodesTk`, `MessagingTk`, `DatagramListener`, `TargetMapper`, `TargetStateStore`, `MirrorBuddyGroupMapper`, `FhgfsOpsRemoting`, and `NodeConnPool`.

## Risks and test signals
Target-state failure transitions all states to probably-offline, then offline after configured timeout. Delayed queues copy `EntryInfo` and file handle IDs and retry only communication errors. Tests should cover management absent/present, hostname resolution failure, registration response with zero ID, NIC list change, forced state update, state sync timeout, delayed close/unlock retry/removal, and shutdown deregistration failure logging.

# sources/distributed-fs/lizardfs/src/chunkserver/network_main_thread.cc

## Purpose
`network_main_thread.cc` owns the chunkserver listening socket and dispatches accepted client/peer connections to worker threads. It also reloads listener and replication/read-ahead settings and starts/stops `NetworkWorkerThread` instances.

## Important APIs, Types, and Functions
Public functions are `mainNetworkThreadInit`, `mainNetworkThreadInitThreads`, `mainNetworkThreadGetListenIp`, and `mainNetworkThreadGetListenPort`. Internal functions include `mainNetworkThreadReload`, `mainNetworkThreadDesc`, `mainNetworkThreadServe`, `mainNetworkThreadTerm`, `chunkReplicatorReload`, and `replicationBandwidthLimitReload`. Global state tracks `lsock`, listener poll position, worker thread/object lists, round-robin iterator, listen IP/port, and worker/job/read-ahead configuration.

## Control Flow
`mainNetworkThreadInit` reads listen host/port and worker counts, configures read-ahead, creates a nonblocking TCP listening socket, resolves/listens, registers event-loop poll/reload/destructor hooks, initializes replication bandwidth limiting, and reloads chunk replicator timeouts. The poll descriptor callback adds the listen socket. The serve callback accepts one pending connection, checks the next worker's job queue, either closes on saturation or hands the socket to that worker, and advances round-robin.

`mainNetworkThreadInitThreads` constructs configured `NetworkWorkerThread` objects and starts one `std::thread` per object. Reload can replace the listening socket if address changes, update bandwidth/read-ahead/replicator settings, and warn that worker-count settings require restart.

## State and Persistence Behavior
This module is runtime-only. It does not persist data, but accepted sockets drive persistent chunk operations in workers. Reload changes the active listen socket without restarting the process. Destruction closes the listener, frees config strings, asks all workers to terminate, and joins their threads.

## Dependencies and Integration Points
It depends on bgjobs, HDD readahead, network stats, worker thread definitions, chunk replicator globals, config/event-loop helpers, and socket wrappers. `masterconn.cc` queries listen IP/port during registration. `init.h` requires this module to initialize before master connection.

## Risks and Edge Cases
Reload swaps `lsock` while the event loop is active, so descriptor registration must see the new value next poll cycle. Only one accept is attempted per serve call, which can throttle bursts. Worker selection uses job-pool occupancy as admission control; a worker with many idle connections but low jobs can still receive more sockets. Worker-count changes are not applied live.

## Test Signals
Integration tests should cover listen creation, address reload success/failure rollback, connection round-robin, saturation close behavior, clean worker termination, and master registration using the resolved listen address. Config reload tests should verify read-ahead and replication limits update live.

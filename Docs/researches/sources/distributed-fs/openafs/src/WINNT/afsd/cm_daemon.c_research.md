# sources/distributed-fs/openafs/src/WINNT/afsd/cm_daemon.c

## Purpose
`cm_daemon.c` implements Windows cache manager background threads: periodic maintenance, lock checking, IP-address change monitoring, and asynchronous fetch/store queues. It keeps server/volume/callback/token state fresh and decouples expensive cache I/O work from foreground SMB/redirector operations.

## Important APIs and Types
Global intervals include down/up server checks, volume refresh, callback expiration, lock checks, token cache checks, offline-volume checks, server ranking, redirector extent shaking, hook reloads, and access-cache cleanup. `daemon_state_t` owns one queue, lock, counters, and head/tail pointers for background requests. Public APIs are `cm_InitDaemon`, `cm_DaemonShutdown`, and `cm_QueueBKGRequest`; worker functions include `cm_IpAddrDaemon`, `cm_BkgDaemon`, `cm_LockDaemon`, and `cm_Daemon`.

## Control Flow
`cm_InitDaemon` clamps daemon count to an even value, starts detached IP, maintenance, lock, and per-queue background worker threads, and initializes queue locks. `cm_QueueBKGRequest` chooses a queue by FID hash and read/write operation class, suppresses duplicate fetch/store requests, holds scache/user refs, and wakes a worker. `cm_BkgDaemon` chooses a non-blocking, server-available request from the tail, invokes its procedure, and requeues transient retryable failures. `cm_Daemon` loops every 500 ms and performs scheduled checks for server reachability, volume refresh, callback expiration, token cache cleanup, offline volumes, server ranking, firewall configuration, network-address changes, redirector extents, performance tuning, and optional hook DLL callbacks.

## State and Persistence
Daemon state is in memory only: queues, counters, shutdown events, interval globals, and `daemon_ShutdownFlag`. Intervals are initialized from registry values in `cm_DaemonCheckInit`; no daemon queue contents persist across process restart.

## Dependencies and Integration Points
The file integrates with Rx client thread startup, pthreads, Windows events/services/firewall APIs, IP helper `NotifyAddrChange`, SMB listener and VC handling, redirector buffer management, server/volume/callback/token modules, power-suspend state, and optional `afsdhook` DLLs.

## Risks and Test Signals
Risk areas include queue starvation, requeue loops on persistent failures, duplicate suppression correctness, shutdown waiting, firewall side effects, and address-change timing. Tests should cover even daemon count clamping, fetch/store queue partitioning, transient error requeue, deleted scache handling, suspend behavior, registry interval overrides, and daemon-triggered callback expiration.

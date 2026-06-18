# sources/distributed-fs/openafs/src/WINNT/afsd/cm_daemon.h

## Purpose
`cm_daemon.h` declares the public daemon controls and background request contract for the Windows cache manager. It exposes maintenance intervals, daemon count, shutdown/init entry points, and the structure used to queue asynchronous scache work.

## Important APIs and Types
Extern interval variables configure server down/up checks, volume checks, callback checks, lock checks, and token checks. `cm_bkgProc_t` is the callback signature for background jobs and must free its rock according to the header comment. `cm_bkgRequest_t` stores queue linkage, procedure, opaque rock, scache/user references, and a copied `cm_req_t`. Public entry points are `cm_InitDaemon`, `cm_DaemonShutdown`, and `cm_QueueBKGRequest`. `CM_MIN_DAEMONS` and `CM_MAX_DAEMONS` bound worker count and require an even daemon count.

## Control Flow
Foreground cache operations allocate a rock and call `cm_QueueBKGRequest`; daemon workers later invoke the `cm_bkgProc_t` against the held scache/user/request. Startup calls `cm_InitDaemon`, and service shutdown calls `cm_DaemonShutdown` to wake and wait for workers.

## State and Persistence
The header exposes in-process state only. Queued requests, interval variables, and daemon count do not persist; the implementation may initialize intervals from registry settings.

## Dependencies and Integration Points
The types depend on `osi_queue_t`, `cm_scache_t`, `cm_user_t`, and `cm_req_t`. The queue is used by background store, direct write, redirector fetch, and prefetch paths declared elsewhere.

## Risks and Test Signals
Tests should confirm rock ownership, reference ownership, daemon-count bounds, duplicate request behavior in the implementation, and that background procedure failures are correctly requeued or released.

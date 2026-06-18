# sources/distributed-fs/coda/coda-src/venus/hdb_daemon.cc

Purpose: implements the HDB daemon that serializes hoard pioctl requests and runs periodic hoard walks.

Important APIs and flow: `HDBD_Init` starts a priority-adjusted `HDBDaemon` vproc. `HDBD_GetNextHoardWalkTime` reports seconds until the next periodic walk. `HDBDaemon` registers a five-minute wake interval, skips the initial startup walk, handles queued requests before periodic work, runs `HDB->Walk` every ten minutes when `PeriodicWalksAllowed` is set, handles requests again afterward, logs elapsed time, and advances its sequence number. `HDBD_Request` enforces `AuthorizedUser`, builds a stack `hdbd_msg`, appends it to `hdbd_msgq`, signals the daemon, waits on the message wait block, and returns the result. `HDBD_HandleRequests` drains the queue and dispatches to the corresponding `HDB` method.

State and persistence: the daemon state is transient: last walk time, synchronization byte, and in-memory request queue. Persistence is delegated to `hdb` methods, which open their own recovery transactions where needed.

Dependencies and integration: depends on `vproc` scheduling, LWP priorities, user authorization, HDB command APIs, and the global periodic-walk flag defined in `hdb.cc`.

Risks and test signals: risks include stack-address request messages that require synchronous completion, no explicit queue lock beyond cooperative vproc assumptions, long blocking hoard walks delaying request replies, root/authorized user policy changes, and inaccurate next-walk reporting before daemon initialization. Tests should cover unauthorized requests, each dispatch type, request/walk interleaving, periodic enable/disable, and daemon wake-up behavior while a demand walk is running.

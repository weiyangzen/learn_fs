# sources/distributed-fs/ceph-client/net/9p/trans_xen.c

Purpose: implements the Xen frontend transport for 9P by negotiating Xenstore state with a backend and exchanging 9P frames over grant-table-backed flexible rings and event channels.

Important APIs, types, and functions: `struct xen_9pfs_front_priv` stores one share, its tag, Xenbus device, attached client, and ring array. `struct xen_9pfs_dataring` stores the shared data interface, grant refs, event channel/IRQ, ring buffers, wait queue, lock, and response work. Transport functions are `p9_xen_create`, `p9_xen_request`, `p9_xen_close`, and `p9_xen_cancel`. Frontend lifecycle is handled by `xen_9pfs_front_init`, `xen_9pfs_front_alloc_dataring`, `xen_9pfs_front_changed`, `xen_9pfs_front_remove`, and `xen_9pfs_front_free`.

Control flow: module init registers the 9P transport only in Xen domains and registers a Xenbus frontend. When the backend reaches `InitWait`, frontend init validates protocol version 1, allocates two data rings, grants the interface and ring pages, allocates event channels, writes grant refs/event channels/tag into Xenstore, and adds the share to `xen_9pfs_devs`. Mount creation matches the source tag and attaches the client. Requests choose a ring by tag modulo two, wait for output space, copy the 9P packet into the ring, update producer index with memory barriers, notify the backend, and drop the request reference. IRQ schedules response work, which reads headers, looks up tags, copies full replies, advances consumer index, and calls `p9_client_cb`.

State and persistence: global share list is protected by `xen_9pfs_lock`. Per-ring indexes live in shared memory; grant references and event channels persist for the lifetime of the Xen frontend device. No filesystem-level persistent state exists.

Dependencies and integration points: depends on Xenbus, Xen events, grant tables, Xen 9pfs interface helpers, workqueues, wait queues, and net/9p transport registration.

Risks: cancellation is unsupported. `p9_xen_create` attaches without setting `client->status`, relying on upper-level expectations. The request path assumes the client remains attached while scanning the global list. Ring size negotiation mutates global `p9_xen_trans.maxsize`, affecting all shares. Suspend/resume is explicitly unsupported.

Test signals: Xenstore negotiation failures, backend version/max-ring constraints, tag matching, full-ring wait/retry, malformed response lengths/tags, backend close/removal during I/O, IRQ storms/spurious interrupts, share removal while mounted, and non-Xen module load returning `-ENODEV`.

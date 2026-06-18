# sources/distributed-fs/ceph-client/include/rdma/restrack.h

Purpose: Declares RDMA resource tracking metadata used to expose kernel and user RDMA resources through nldev/netlink and to coordinate resource lifetime.

Important APIs/types/functions: `enum rdma_restrack_type` names tracked objects such as PD, CQ, QP, CM_ID, MR, CTX, COUNTER, SRQ, and DMAH. `struct rdma_restrack_entry` stores validity, no-track state, kref/completion, owner task or kernel name, resource type, user/kernel ownership, and exported ID. APIs include `rdma_restrack_count()`, `rdma_restrack_get()`, `rdma_restrack_put()`, `rdma_restrack_get_byid()`, `rdma_restrack_no_track()`, `rdma_restrack_is_tracked()`, and netlink driver-attribute emitters.

Control flow and state: Entries are filled during add and may be concurrently observed until delete completes. The kref plus completion protect object destruction while netlink dump or lookup users hold references. `no_track` suppresses database exposure but leaves the resource usable internally. `user` distinguishes process-owned objects from kernel-created objects.

Dependencies and integration: Depends on `ib_device`, netlink SKBs, Linux kref/completion/task/xarray, and UAPI RDMA netlink identifiers. Drivers integrate by embedding an entry in RDMA objects and publishing optional driver-specific attributes.

Risks and test signals: Risks include leaking task references, marking objects untracked without review, exposing stale IDs, and missing get/put pairs during nldev dumps. Tests should cover resource create/destroy races while dumping `rdma resource`, no-track resources, driver detail attributes, and module unload with active references.

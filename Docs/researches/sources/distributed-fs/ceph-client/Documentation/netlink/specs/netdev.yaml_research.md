# sources/distributed-fs/ceph-client/Documentation/netlink/specs/netdev.yaml

Purpose: describes the Generic Netlink `netdev` configuration and introspection API for network devices, page pools, queues, NAPI instances, queue statistics, DMA buffer binding, and dynamic queue creation.

Important APIs/types/functions: definitions include XDP action/features, XDP RX metadata flags, XSK flags, queue type, queue-stat scope, and NAPI threaded state. Attribute sets include `dev`, `io-uring-provider-info`, `page-pool`, `page-pool-info`, `page-pool-stats`, `napi`, `xsk-info`, `queue`, `qstats`, `queue-id`, `lease`, and `dmabuf`. Device replies report ifindex and XDP/XSK capability bitmaps. Page-pool attributes expose ids, ifindex, NAPI id, inflight pages/bytes, detach time, dmabuf id, and io_uring provider info. Queue/NAPI/qstats sets describe queue ids/types, NAPI affinity and tunables, per-queue counters, leases, and dmabuf bindings.

Control flow: `dev-get`, `page-pool-get`, `queue-get`, `napi-get`, and `page-pool-stats-get` are query/dump paths. Device and page-pool add/delete/change notifications reuse get schemas. `qstats-get` is dump-only and filters by ifindex/scope. Mutating paths are `bind-rx` for RX dmabuf binding, `bind-tx` for TX binding, `napi-set` for NAPI tunables, and `queue-create` for driver-supported queue creation; most write paths require `admin-perm`, while `bind-tx` notably has no explicit flag in the schema.

State and persistence: the API exposes live netdevice capabilities, page-pool lifecycle, queue configuration, NAPI runtime settings, dmabuf leases, and counters. Some settings mutate driver/runtime state; counters and pool statistics are transient.

Dependencies and integration points: integrates with network core, XDP/XSK, page_pool, NAPI, io_uring provider plumbing, dmabuf-backed networking, and netdev queue management. User tools can discover capabilities, then bind memory or allocate queues based on driver support.

Risks: several attributes use symbolic min/max checks such as `u32-max` and `s32-max`, so generator support is required. Queue and page-pool ids are live objects that can disappear between dump and action. Dmabuf binding crosses fd, namespace, and hardware ownership boundaries. `bind-tx` lacking an explicit admin flag should be checked against kernel implementation expectations. Statistics coverage depends on driver support.

Test signals: parse/generation tests for nested queue/dmabuf/lease schemas, notification tests for device and page-pool lifecycle, qstats dumps on devices with and without per-queue counters, NAPI set/get round trips, dmabuf fd validation, and queue-create failure paths on unsupported drivers.

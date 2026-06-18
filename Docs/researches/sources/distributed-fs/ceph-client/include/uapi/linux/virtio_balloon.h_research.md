# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_balloon.h

Purpose: defines the virtio memory balloon device ABI for guest memory inflation/deflation, statistics, free-page hinting/reporting, page poisoning, and page reporting.

Important APIs/types/functions: feature bits include `VIRTIO_BALLOON_F_MUST_TELL_HOST`, `STATS_VQ`, `DEFLATE_ON_OOM`, `FREE_PAGE_HINT`, `PAGE_POISON`, and `REPORTING`. `virtio_balloon_config` carries host-requested page count, actual ballooned pages, free-page hint/report command id, and poison value. Statistic tags range from swap/fault/memory totals through hugepage and reclaim counters, with `VIRTIO_BALLOON_S_NAMES` name macros. `virtio_balloon_stat` is the packed tag/value pair sent on the stats virtqueue.

Control flow: the host updates `num_pages`; the guest inflates or deflates by sending PFNs over balloon queues and updates `actual`. Optional stats queues send arrays of `virtio_balloon_stat`. Free-page hint/reporting uses command IDs `STOP` and `DONE` to coordinate reporting batches. Page poisoning communicates the poison value when negotiated.

State and persistence: device config tracks desired and actual balloon size plus hint/report command state. The guest owns transient PFN lists and stat arrays. Ballooned pages persist as unavailable guest memory until deflated; stats are sampled, not durable.

Dependencies and integration: includes Linux integer types and common virtio type/id/config headers. It integrates with guest memory management, host memory overcommit, OOM behavior, page reporting, and VMM memory accounting.

Risks: the PFN interface assumes `VIRTIO_BALLOON_PFN_SHIFT` of 12, so page size assumptions must be managed. Packed `virtio_balloon_stat` is kept for compatibility but can generate inefficient accesses. Incorrect command ID handling can race free-page reporting. Misreported `actual` breaks host memory accounting.

Test signals: virtio-balloon inflate/deflate tests, stats virtqueue tests, OOM deflate behavior, free-page hint/reporting command tests, page poisoning negotiation tests, and ABI layout checks for the packed stat structure.

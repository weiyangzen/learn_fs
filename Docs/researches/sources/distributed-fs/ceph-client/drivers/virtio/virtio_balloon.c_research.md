# sources/distributed-fs/ceph-client/drivers/virtio/virtio_balloon.c

## Purpose
`virtio_balloon.c` implements the virtio memory balloon driver. It lets the host reclaim or return guest memory, reports memory statistics, supports free-page hinting and page reporting, handles OOM deflation, and participates in PM freeze/restore.

## Important APIs, types, and functions
The central type is `struct virtio_balloon`, holding virtqueues, work items, balloon page accounting, free-page hint state, stats, shrinker, OOM notifier, page-reporting device, locks, and wakeup state. Important functions include `virtballoon_probe`, `virtballoon_remove`, `virtballoon_changed`, `fill_balloon`, `leak_balloon`, `tell_host`, `update_balloon_size_func`, `stats_request`, `stats_handle_request`, `init_vqs`, `virtio_balloon_report_free_page`, `report_free_page_func`, `virtballoon_free_page_report`, `virtio_balloon_oom_notify`, `virtballoon_validate`, and PM `virtballoon_freeze`/`virtballoon_restore`.

## Control flow
Probe validates config access, allocates state, initializes work/locks, creates virtqueues based on negotiated features, registers optional shrinker/OOM/page-reporting hooks, sets page-poison config, marks the device ready, and schedules adjustment if the host target differs. Config changes queue freezable work that reads the target, inflates by allocating balloon pages and sending PFNs on the inflate queue, or deflates by dequeuing pages and sending PFNs on the deflate queue. Stats are host-request driven through a primed stats queue. Free-page hinting sends command IDs and page blocks on a dedicated queue; page reporting uses the generic page-reporting callback.

## State and persistence
State is runtime only: `num_pages`, `vb_dev_info` page list, PFN buffer, stats buffer, free-page list and command IDs, workqueue state, and negotiated feature hooks. Host-visible config fields include actual balloon size and page poison value. No storage persistence exists.

## Dependencies and integration points
It depends on virtio config/queues, balloon core, MM/page allocation, page reporting, OOM notifier, shrinker API, PM wakeup sources, and optional balloon migration. It integrates with host memory management and guest reclaim paths.

## Risks and test signals
Risks include deadlocks around `balloon_lock`, host notification ordering with `MUST_TELL_HOST`, stalled waits for virtqueue acknowledgements, races with removal/freeze via `stop_update`, free-page hint command ID transitions, shrinker accounting, OOM notifier side effects, page poisoning/reporting compatibility, and feature validation clearing `ACCESS_PLATFORM`. Test signals include target inflate/deflate loops, OOM deflation, stats queue requests, free-page hint start/stop/done, page reporting capacity checks, PM freeze/restore, migration of balloon pages, removal with nonzero balloon, and host feature combinations.

# sources/distributed-fs/ceph-client/net/9p/trans_virtio.c

Purpose: implements the default virtio 9P transport, discovering virtio 9P channels, matching mounts by mount tag, and sending 9P requests through a single virtqueue with optional zero-copy user data.

Important APIs, types, and functions: `struct virtio_chan` stores channel in-use state, virtqueue, client, tag, wait queue, scatterlist array, and zero-copy page limit. `p9_virtio_probe` and `p9_virtio_remove` handle virtio device lifecycle; `p9_virtio_create` and `p9_virtio_close` attach/detach mounts; `p9_virtio_request` sends normal requests; `p9_virtio_zc_request`, `p9_get_mapped_pages`, `pack_sg_list`, and `pack_sg_list_p` implement scatter-gather and zero-copy.

Control flow: probe requires the `VIRTIO_9P_MOUNT_TAG` feature, reads the tag from config space, creates a `mount_tag` sysfs attribute, initializes the channel wait queue and scatterlist, and adds the channel to a global list. Mount creation locks the list, finds an unused tag match, marks it in use, and attaches the client. Requests pack outgoing and incoming buffers into scatterlists, call `virtqueue_add_sgs`, wait and retry on `-ENOSPC`, and kick the queue. `req_done` drains completed buffers, sets response length, invokes `p9_client_cb`, and wakes waiters for ring space.

State and persistence: global state includes `virtio_chan_list`, `virtio_9p_lock`, and `vp_pinned`. Per-channel `ring_bufs_avail` gates waiters. Zero-copy pins pages up to `p9_max_pages`, then unpins and wakes global waiters after completion or failure. No state persists beyond the virtio device/module lifetime.

Dependencies and integration points: depends on virtio core, virtio 9P config, scatterlist, page pinning/iov iter helpers, sysfs, and net/9p. It registers both a `virtio_driver` and `p9_trans_module`; the mount tag sysfs file is intended for udev rules.

Risks: no request cancel is supported; cancelled zero-copy requests must drop references correctly. Page pin accounting is global and can become a denial-of-service boundary. `handle_rerror` copies error payload out of user pages into static response data and truncates long errors. Remove waits indefinitely for `inuse` to clear, only logging periodically.

Test signals: virtio probe without config access or mount-tag feature, duplicate tag mount attempts, virtqueue full retries, zero-copy read/write with user and kernel iovecs, interrupted waits, RERROR on zero-copy reads, page pin limit pressure, hot-remove while mounted, and sysfs `mount_tag` visibility.

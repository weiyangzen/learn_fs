<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_main.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_main.c

Purpose: Handles UDL device initialization, vendor-descriptor parsing, channel selection, reusable USB URB pool allocation/completion/submission/synchronization, and USB resource teardown.

Important APIs/types/functions: `udl_parse_vendor_descriptor()` reads descriptor `0x5f` and extracts SKU pixel limit key `0x0200`. `udl_select_std_channel()` sends the fixed standard-channel vendor command. `udl_alloc_urb_list()` allocates coherent bulk URBs, shrinking buffer size on failure. `udl_get_urb()` waits for an available URB. `udl_submit_urb()` submits a payload and requeues on error. `udl_sync_pending_urbs()` waits for all URBs to return. `udl_init()` sets DMA device, descriptor defaults, channel, URBs, and modeset. `udl_drop_usb()` frees URBs.

Control flow: Init sets a default FullHD-ish pixel limit, optionally overrides from firmware descriptor, selects the channel, builds a pool of 20 URBs up to `MAX_TRANSFER`, and initializes KMS. Completion returns URBs to the free list under spinlock and wakes waiters. Free waits for all URBs to be available before releasing coherent buffers and URB nodes.

State and persistence: Runtime state is the SKU pixel limit and URB pool (`count`, `available`, `size`, free list, waitqueue). No durable persistence exists.

Dependencies and integration points: Uses USB descriptors/control/bulk URBs, DRM logging, DMA-device setup for buffer sharing, and `udl_modeset_init()`.

Risks and test signals: Risks include URB pool deadlock on disconnect, timeout under heavy damage upload, descriptor parsing accepting bogus lengths, and fallback buffer sizing. Test descriptor variants, allocation pressure, USB submit errors, sync timeout, suspend/resume, and teardown with in-flight URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/udlfb.h -->
# sources/distributed-fs/ceph-client/include/video/udlfb.h

## Purpose
This header defines the DisplayLink USB framebuffer driver's private state, deprecated damage/EDID ioctls, URB pool structures, compression thresholds, transfer limits, and deferred I/O timing.

## Important APIs, Types, And Functions
- `DLFB_IOCTL_RETURN_EDID` and `DLFB_IOCTL_REPORT_DAMAGE` support existing DisplayLink X server behavior.
- `struct dloarea` reports damaged rectangles.
- `struct urb_node` and `struct urb_list` manage USB URBs with list, lock, semaphore limit, availability/count, and transfer size.
- `struct dlfb_data` stores USB device, fb info, URB pool, backing buffer, virtual/active/lost-pixels state, EDID, SKU limits, palettes, blank mode, render mutex, damage rectangle/lock/work item, fb ops, mmap count, render metrics, current mode, and deferred-free list.
- Transfer constants define request IDs, `BULK_SIZE`, `MAX_TRANSFER`, `WRITES_IN_FLIGHT`, vendor descriptor size, URB timeouts, bpp, pixel command limits, RLX/RLE/RAW minimum sizes, and deferred I/O delays.

## Control Flow
Framebuffer writes mark damaged areas, workqueue processing compares against the backing buffer, compresses changed pixels into DisplayLink commands, obtains URBs from `urb_list`, submits USB bulk transfers, updates metrics, and tracks failures through `lost_pixels`. Ioctls return EDID or report explicit damage.

## State And Persistence
Runtime state is extensive in `dlfb_data`: backing framebuffer copy, damage bounds, EDID, current mode, URB availability, USB activity, blank state, mmap count, deferred frees, and sysfs metrics. Device persistence is limited to USB device state and monitor EDID.

## Dependencies And Integration Points
It integrates with USB core, fbdev, workqueues, mutex/spinlock/semaphore/atomic primitives, deferred I/O, sysfs metrics, EDID handling, and existing DisplayLink userspace.

## Risks And Edge Cases
Damage bounds are shared between rendering and ioctl paths and must be protected by `damage_lock`. USB disconnect uses `virtualized` and `usb_active`; code must update the backing buffer without submitting URBs when inactive. Compression thresholds and transfer limits must avoid overrun while keeping URBs full enough for performance.

## Test Signals
Signals include correct EDID return, damage ioctl refresh, no lost pixels under heavy mmap/fb writes, bounded URB in-flight counts, stable disconnect/reconnect handling, accurate byte/cpu metrics, and deferred I/O behavior at both normal and disabled delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/udlfb.h -->

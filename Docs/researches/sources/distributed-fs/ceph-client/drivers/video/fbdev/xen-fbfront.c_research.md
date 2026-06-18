# sources/distributed-fs/ceph-client/drivers/video/fbdev/xen-fbfront.c

Purpose: Xen paravirtual framebuffer frontend. It exposes a sysmem fbdev framebuffer to Linux guests and communicates memory pages, display updates, and optional resize requests to a Xen backend through xenbus, shared pages, event channels, and the Xen framebuffer ring protocol.

Important APIs, types, and functions: `struct xenfb_info` tracks vmalloc framebuffer memory, `fb_info`, dirty rectangle, resize request, shared page, GFNs, event IRQ, feature flags, and xenbus device. Core functions include `xenfb_send_event`, `xenfb_refresh`, `xenfb_deferred_io`, `xenfb_setcolreg`, `xenfb_check_var`, `xenfb_set_par`, `xenfb_event_handler`, `xenfb_probe`, `xenfb_remove`, `xenfb_resume`, `xenfb_init_shared_page`, `xenfb_connect_backend`, `xenfb_disconnect_backend`, and `xenfb_backend_changed`.

Control flow: module init only registers the frontend when running as a non-dom0 Xen PV-capable guest. Probe reads backend video limits from xenstore, allocates vmalloc framebuffer memory and GFNs, allocates a shared `xenfb_page`, creates `fb_info`, sets 32-bpp truecolor defaults, initializes deferred I/O, fills the shared page with GFN directory and mode metadata, binds an event channel IRQ, writes `page-ref`, `event-channel`, protocol, and update feature to xenstore, registers the framebuffer, and makes tty0 preferred if no console was selected. Deferred I/O and damage callbacks coalesce dirty rectangles and send `XENFB_TYPE_UPDATE` when requested. Resize changes are staged in `xenfb_set_par` and emitted before updates if backend resize is supported.

State and persistence: all state is per xenbus frontend and volatile. The guest framebuffer is vmalloc memory; the shared page and GFN directory persist while the device is connected. Dirty and resize state are protected by spinlocks. Xenstore values and ring producer/consumer indexes are integration state with the backend.

Dependencies and integration points: depends on Xen hypervisor detection, xenbus, event channels, Xen page/GFN helpers, fbdev deferred I/O, vmalloc, console registration, and protocol definitions in `xen/interface/io/fbif.h`.

Risks: framebuffer sharing uses GFNs rather than grant tables, as noted in the TODO. Ring-full conditions defer dirty rectangles and rely on later IRQ/update flushes. Resize is limited to initial memory bounds and backend feature support. The module parameter array is global, so multiple vfb devices would share sizing state. Damage-range handling refreshes the whole current mode. Backend input events are ignored.

Test signals: boot a Xen PV guest with vfb; vary `video=` memory/width/height and xenstore limits; verify fbcon, mmap/write damage, deferred I/O updates, backend `request-update`, resize with and without `feature-resize`, resume reconnect, ring-full dirty coalescing, and frontend close state transitions.

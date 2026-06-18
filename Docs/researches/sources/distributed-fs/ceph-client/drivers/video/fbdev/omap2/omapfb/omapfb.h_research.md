## sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb.h

Purpose: this internal header defines the shared OMAP fbdev data model, debug macro, locking helpers, and cross-file function prototypes used by the main, sysfs, ioctl, and VRFB-related code.

Important APIs/types/functions: `FB2OFB()` converts `fb_info->par` to `struct omapfb_info`. `struct omapfb2_mem_region` holds DMA/VRFB memory state, address fields, allocation flags, map count, and rwsem/lock count. `struct omapfb_info` is appended to each `fb_info` and records framebuffer id, memory region, overlay list, owning `omapfb2_device`, rotation type, per-overlay rotations, and mirror state. `struct omapfb_display_data` tracks a DSS display, bpp override, update mode, and delayed auto-update work. `struct omapfb2_device` is the driver root object containing displays, overlays, managers, framebuffer array, regions, pseudo palette, mutex, and workqueue. Inline helpers include `fb2display()`, `get_display_data()`, `omapfb_lock()`, `omapfb_unlock()`, `omapfb_overlay_enable()`, `omapfb_get_mem_region()`, and `omapfb_put_mem_region()`.

Control flow: the header does not execute standalone, but it defines the locking and ownership conventions. Callers use `omapfb_get_mem_region()`/`omapfb_put_mem_region()` around region-sensitive operations, causing read locking and `lock_count` accounting. `fb2display()` resolves the display through the first attached overlay. `get_display_data()` linearly searches the driver display array and `BUG()`s if the display is unknown.

State and persistence behavior: all structures are volatile kernel runtime state. The fixed-size arrays support up to 10 framebuffers/regions/displays/overlays/managers and up to 3 overlays per framebuffer. No persistent storage is defined; module parameters and detected DSS topology populate these structures at probe time.

Dependencies and integration points: includes Linux rwsem and DMA mapping APIs plus OMAP DSS headers. Prototypes link to `omapfb-main.c`, `omapfb-sysfs.c`, ioctl/update-mode implementation files, and auto-update helpers. The memory region embeds `struct vrfb` from `<video/omapvrfb.h>` through transitive includes in source users.

Risks: array sizes are fixed and rely on probe code not exceeding them when enumerating DSS devices/overlays/managers. `get_display_data()` fails with `BUG()` rather than a recoverable error, so callers must only pass known DSS devices. `fb2display()` assumes the first overlay is representative, which can be limiting when a framebuffer drives multiple overlays. Lock-count is diagnostic/guard state and must stay paired with rwsem operations.

Test signals: build coverage across all OMAPFB compilation units, lockdep during sysfs and fbdev mode changes, enumeration with multiple displays/overlays, no-overlay framebuffers returning `NULL` display, and stress around memory-region map/reallocation lock pairing.

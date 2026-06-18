# sources/distributed-fs/ceph-client/include/video/mmp_disp.h

## Purpose
`mmp_disp.h` defines the common display-controller interface for Marvell MMP display paths, overlays, panels, modes, and platform data. It gives buffer, controller, and panel drivers a shared object model and callback surface.

## Important APIs, Types, and Functions
Pixel formats include packed/planar YUV, RGB565/1555/888, RGBA/BGRA, RGB666, and pseudocolor; `pixfmt_to_stride()` returns bytes per pixel or luma-plane stride unit. Core structs include `mmp_win`, `mmp_addr`, `mmp_mode`, `mmp_overlay_ops`, `mmp_overlay`, `mmp_panel`, `mmp_path_ops`, `mmp_path`, `mmp_path_info`, `mmp_buffer_driver_mach_info`, `mmp_mach_path_config`, `mmp_mach_plat_info`, and `mmp_mach_panel_info`. Public APIs register and look up paths/panels and inline helpers dispatch mode, on/off, modelist, overlay, fetch, window, and address operations.

## Control Flow
Controller drivers register paths with overlay ops and path callbacks. Panel drivers register panels matched by path name. Buffer/fb drivers look up a path, get an overlay, set fetch ID, window geometry, DMA addresses, and enable status. Path mode and power callbacks propagate to controller-specific hardware code and panel callbacks.

## State and Persistence Behavior
Runtime state is in path and overlay objects: open counts, status, mode, current window, DMA addresses, panel attachment, and mutexes. Registration lists persist for device lifetime only; no persistent storage exists.

## Dependencies and Integration Points
The header depends on Linux kthreads indirectly, devices, list heads, mutexes, and flexible array support. It integrates MMP display controllers, panels, fb/buffer drivers, DMA fetch IDs, platform machine data, and output types such as parallel, DSI, and HDMI.

## Risks and Test Signals
Risks include missing null checks on callback pointers despite inline object checks, incorrect stride for planar formats, open-count/status races, overlay flexible-array allocation errors, and path/panel name mismatches. Test signals include path/panel registration and unregister, modelist propagation, overlay window/address programming for each format class, concurrent open/close, DSI/HDMI/parallel output selection, and invalid pixfmt stride behavior.

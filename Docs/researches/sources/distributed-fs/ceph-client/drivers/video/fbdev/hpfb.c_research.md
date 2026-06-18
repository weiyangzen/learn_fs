<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hpfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/hpfb.c

Purpose: implements fbdev support for HP300 Topcat and Catseye framebuffers on internal HP300 and DIO/DIO-II buses.

Important APIs, types, and functions: global `fb_info`, `fb_regs`, and `fb_bitmask` represent the single device. `hpfb_setcolreg()` programs the color map through HP registers. `hpfb_blank()` controls `TC_NBLANK`. `topcat_blit()` programs the block mover; `hpfb_copyarea()`, `hpfb_fillrect()`, and `hpfb_sync()` use it for acceleration and synchronization. `hpfb_init_one()` reads framebuffer geometry from registers, initializes Catseye-specific magic registers, maps framebuffer memory, detects bit planes, enables planes, clears the screen, allocates cmap, and registers fbdev. `hpfb_dio_probe()` handles DIO devices; `hpfb_init()` also checks the internal framebuffer address.

Control flow: module init requires HP300 architecture and no disabled options, registers the DIO driver, then probes the internal Topcat address. DIO probe reserves device memory, maps DIO-II resources if needed, and calls common initialization. Remove unregisters, unmaps resources, releases memory, and frees the colormap.

State and persistence: one global framebuffer state is used. Hardware geometry and color depth are read from device registers at init. `fb_bitmask` captures the writable planes and is used for blanking and blitter enable masks.

Dependencies and integration points: depends on m68k HP300/DIO bus APIs, big-endian register accessors, fbdev, and Topcat/Catseye register conventions. It integrates with DIO device IDs and a special internal framebuffer physical/virtual address.

Risks: global state limits multiple-device handling. Internal framebuffer resource handling in `hpfb_init()` can return errors after registering the DIO driver without unregistering it. Busy waits on colormap and blitter registers have no timeout. Catseye initialization uses hardware magic from the HP X server. The cleanup module only unregisters the DIO driver; internal device cleanup relies on global fb state but is not fully symmetrical here.

Test signals: HP300-only init rejection on other architectures, DIO probe/remove for each supported secondary ID, internal Topcat detection, color map writes under busy conditions, blitter fill/copy/sync behavior, blank/unblank, and failure injection after DIO driver registration and internal resource request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hpfb.c -->

# sources/distributed-fs/ceph-client/drivers/video/fbdev/fsl-diu-fb.c

## Purpose
`fsl-diu-fb.c` is the Freescale Display Interface Unit framebuffer driver. It exposes five fbdev AOIs, manages DIU descriptors, modes, gamma/cursor memory, open counts, IRQ workarounds, monitor-port routing, and platform-specific DIU operations.

## APIs And Control Flow
`struct fsl_diu_data` contains five `fb_info` objects, AOI metadata, DIU registers, descriptors, gamma table, cursor buffers, dummy AOI, EDID data, IRQ, and monitor port. `struct mfb_info` tracks each AOI's descriptor, alpha, count, display offset, and parent. Key routines include `fsl_diu_check_var()`, `fsl_diu_set_par()`, `fsl_diu_pan_display()`, `fsl_diu_ioctl()`, `fsl_diu_open()`, `fsl_diu_release()`, `fsl_diu_cursor()`, `install_fb()`, `fsl_diu_probe()`, `fsl_diu_remove()`, and `fsl_diu_isr()`. Probe allocates coherent shared state, initializes descriptors/AOIs, reads EDID, maps registers, requests IRQ, installs all fbdevs, and creates the `monitor` sysfs file.

## State, Dependencies, Integration, Risks
Shared state across five fbdevs is guarded by a global spinlock for open/release descriptor linking. Dependencies include OF, `diu_ops`, DMA coherent memory, big-endian MMIO, `linux/fsl-diu-fb.h`, EDID helpers, and optional MPC512x gamma ioctls. Risks include descriptor-chain ordering, low-memory assumptions in framebuffer allocation, cursor image 32-bit reads, and partial probe unwind. Tests should cover EDID fallback, all bpp modes, AOI clamping/linking, ioctls, IRQ underrun reset, suspend/resume, sysfs monitor changes, and non-coherent cache builds.

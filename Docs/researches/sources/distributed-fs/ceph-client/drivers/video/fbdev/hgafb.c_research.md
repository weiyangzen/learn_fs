<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hgafb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/hgafb.c

Purpose: implements a platform fbdev driver for Hercules Graphics Adapter compatible hardware at legacy memory and I/O ports.

Important APIs, types, and functions: global state tracks `hga_vram`, `hga_vram_len`, current `hga_mode`, detected card type/name, and I/O release flags. Low-level helpers program HGA registers via `outb_p`, test register writability, clear VRAM, switch text/graphics modes, pan by CRTC start address, and blank video. `hga_card_detect()` reserves 0xb0000 VRAM, maps it, optionally claims I/O ports, tests memory/registers, detects vsync toggling, and classifies card type. Fbdev callbacks include open/release mode switching, `hgafb_pan_display()`, `hgafb_blank()`, and custom monochrome fill/copy/imageblit operations using HGA row addressing. `hgafb_probe()` detects hardware, allocates/registers fbdev; init registers both platform driver and a simple platform device.

Control flow: module init registers a synthetic platform device. Probe performs legacy hardware detection, fills fixed 720x348 1bpp fbdev state, and registers. Opening the framebuffer switches to graphics and clears; release switches back to text and clears. Remove restores text mode, clears, unregisters, unmaps, and releases I/O regions.

State and persistence: most hardware state is global rather than per-device because the driver supports one fixed legacy device. The framebuffer maps fixed physical memory. `nologo` is a module parameter. Current mode is tracked under `hga_reg_lock`.

Dependencies and integration points: depends on legacy VGA/HGA I/O ports, platform-device scaffolding, fbdev IOMEM helpers, and spinlock serialization around register programming.

Risks: port claims are best-effort; if `request_region()` fails, the driver can continue and later may not own the ports it touches. Detection writes to legacy video memory and CRTC registers. Accel callbacks assume byte-aligned widths and HGA memory layout. `hga_fix.smem_start` is assigned the mapped virtual address rather than the physical base, matching legacy style but risky for mmap/userspace expectations.

Test signals: detection with no card, MDA-only, Hercules/HerculesPlus/HerculesColor signatures, open/release mode transitions, pan validation with y offsets multiple of 8, blank/unblank, fill/copy/imageblit alignment behavior, and cleanup after partial port reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hgafb.c -->

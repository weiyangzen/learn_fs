# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/bochs.c

Purpose: This PCI DRM driver supports the Bochs/QEMU stdvga DISPI interface and Simics-compatible variants. It offers one virtual connector/CRTC/primary plane, copies shadow GEM framebuffer damage into the linear framebuffer BAR, and programs VBE DISPI plus VGA registers for display modes and blanking.

Important APIs, types, and functions: `struct bochs_device` stores MMIO or I/O-port access, framebuffer mapping/base/size, QEMU extension size, current mode fields, and DRM objects. `bochs_uses_mmio()`, `bochs_vga_readb()`/`writeb()`, and `bochs_dispi_read()`/`write()` abstract MMIO versus port I/O. `bochs_hw_init()` discovers BAR2 MMIO/ports, validates DISPI ID, maps framebuffer BAR0, and enables native endian extension registers. `bochs_primary_plane_helper_atomic_update()` copies damaged rectangles using `drm_fb_memcpy()` and exposes a panic scanout buffer through `get_scanout_buffer`.

Control flow: Probe removes conflicting apertures, allocates a managed DRM device, enables PCI, stores drvdata, initializes hardware, builds KMS objects, registers DRM, and starts the DRM client. Mode setting writes DISPI x/y/bpp/virtual size/offset registers and enables LFB mode. Plane atomic updates iterate damage, copy shadow data to write-combined VRAM, reset scanout base to offset zero, and adjust endian format. Connector mode probing reads EDID from the MMIO aperture if present, otherwise creates no-EDID modes with module-param defaults.

State and persistence: The driver caches current resolution, bpp, stride, virtual height, framebuffer mapping, and extension size. Hardware persistence includes DISPI registers, VGA blanking attribute writes, QEMU endian register 0x604, and LFB content. There is no persistent software backing store beyond GEM shadow buffers owned by DRM helpers.

Dependencies and integration points: Uses PCI IDs for QEMU stdvga and Simics, `aperture_remove_conflicting_pci_devices()`, optional I/O port support, DRM shmem helpers, shadow-plane helpers, fbdev shmem, vblank timer helpers, EDID helpers, and DRM panic scanout. Module parameters `modeset`, `defx`, and `defy` control binding/default modes.

Risks: If I/O ports are unavailable and the device lacks MMIO register BARs, probe fails. EDID reads are limited to the area before VGA registers and silently fall back to synthetic modes. Framebuffer memory size mismatches are clamped after warning. Endian switching is format-dependent and relies on QEMU extension behavior. The plane update copies only reported damage, so incorrect damage clips can leave stale VRAM.

Test signals: Validate QEMU stdvga boot, Simics ID match, EDID and no-EDID mode paths, XRGB8888 and BGRX8888 endian output, mode rejection when framebuffer memory is insufficient, suspend/resume through mode config helpers, panic framebuffer readout, and removal/unplug racing with atomic commits through `drm_dev_enter()` guards.

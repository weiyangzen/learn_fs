# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/cirrus-qemu.c

Purpose: This is a DRM driver for QEMU/Xen emulated Cirrus Logic GD5446 VGA hardware. It is intentionally minimal for virtual hardware: one virtual connector, one CRTC, one primary plane, shmem shadow framebuffers, and direct writes to VGA/Cirrus sequencer/CRTC/graphics registers plus VRAM.

Important APIs, types, and functions: `struct cirrus_device` owns DRM objects plus VRAM and MMIO mappings. Register helpers `rreg_seq()`, `wreg_seq()`, `rreg_crt()`, `wreg_crt()`, `wreg_gfx()`, and `wreg_hdr()` access the Cirrus register windows. `cirrus_mode_set()` programs horizontal/vertical timing registers and overflow bits. `cirrus_format_set()` selects C8/RGB565/RGB888/XRGB8888 hardware modes. `cirrus_pitch_set()` programs CRTC offset and extended pitch bits. Plane check enforces `CIRRUS_MAX_PITCH` and 4 MiB VRAM limits.

Control flow: PCI probe removes conflicting framebuffer apertures, enables the device, requests all BARs, allocates DRM state, maps VRAM BAR0 and MMIO BAR1, initializes fixed mode limits, creates the primary plane/CRTC/encoder/connector, registers the device, and launches fbdev/client setup. Atomic CRTC enable programs the display mode, unblanks VGA attribute output when I/O ports exist, and enables vblank timer accounting. Plane atomic update detects format/pitch changes, programs registers as needed, and copies damaged shadow framebuffer rectangles into VRAM.

State and persistence: The software state is small: DRM object state plus BAR mappings. Hardware state includes VGA/Cirrus CRTC timing, sequencer format bits, graphics mode, DAC header, pitch, start address, and VRAM contents. No explicit suspend/resume PM callbacks are present; normal remove/shutdown calls atomic shutdown.

Dependencies and integration points: Binds only to Cirrus GD5446 PCI IDs for Red Hat Qumranet/QEMU and Xen. Uses aperture conflict removal, `pcim_*` PCI management, DRM shmem/fbdev helpers, shadow-plane helpers, damage clips, vblank timer helpers, and `video/cirrus.h`/`video/vga.h` constants.

Risks: The file comments state the programming is only sufficient for emulated hardware and may not correctly drive real devices. The maximum mode dimensions are constrained by pitch and fixed VRAM size; bad pitch or height combinations are rejected. Register programming is unguarded beyond `drm_dev_enter()` in update/enable. There is no EDID path, so userspace sees synthetic modes with a 1024x768 preference.

Test signals: Exercise QEMU and Xen binding, all advertised formats, pitch rejection above `0x1ff << 3`, VRAM-size mode rejection, damage-only updates, format/pitch change commits, shutdown/remove atomic cleanup, and visual output for 16/24/32-bpp modes.

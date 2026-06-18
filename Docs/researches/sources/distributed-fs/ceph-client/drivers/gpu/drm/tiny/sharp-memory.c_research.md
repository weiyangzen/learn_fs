# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/sharp-memory.c

Purpose: This SPI DRM driver supports multiple Sharp Memory LCD panels. It exposes fixed model modes, converts XRGB8888 framebuffer lines to monochrome, sends Sharp memory-display update/clear/maintain messages, and supports software, external, or PWM VCOM generation.

Important APIs, types, and functions: `struct sharp_memory_device` owns DRM objects, SPI handle, mode, optional enable GPIO, VCOM state, optional software kthread or PWM, tx buffer metadata, and a mutex for SPI/tx-buffer synchronization. `sharp_memory_spi_write()` reverses bit order in-place before `spi_write()`, matching the panel protocol. `sharp_memory_update_display()`, `sharp_memory_maintain_display()`, and `sharp_memory_clear_display()` build command buffers. `sharp_memory_fb_dirty()` expands any dirty rectangle to full lines. `sharp_memory_sw_vcom_signal_thread()` toggles the VCOM bit once per second in software mode.

Control flow: Probe sets up SPI, coerces 32-bit DMA if needed, allocates DRM state, stores drvdata, initializes mode config, gets optional enable GPIO, selects mode from SPI/OF match data, computes pitch and tx buffer size, initializes the mutex, parses required `sharp,vcom-mode`, starts a software VCOM kthread or PWM if requested, sets exact mode bounds, initializes plane/CRTC/encoder/SPI connector, enables damage clips, registers DRM, and starts client setup. CRTC enable clears display and asserts enable GPIO; disable clears and deasserts. Plane update merges damage and sends line updates only while CRTC is active. Remove unplugs/shuts down DRM and stops VCOM generation.

State and persistence: Persistent software state includes selected mode, VCOM mode, current VCOM bit, tx buffer contents, mutex, optional kthread/PWM, and enable GPIO. Hardware state includes display memory, VCOM drive, and panel enable. Because `sharp_memory_spi_write()` bit-reverses the buffer in-place, callers repopulate command/data before each transfer.

Dependencies and integration points: Binds to many Sharp `ls*` SPI IDs and OF compatibles. Uses SPI, GPIO, PWM, kthread, bit reversal, DRM GEM DMA vmap/fbdev helpers, shadow-plane helpers, mono conversion helpers, fixed connector modes, and the `sharp,vcom-mode` DT property.

Risks: Missing or invalid `sharp,vcom-mode` fails probe. Software VCOM thread starts before DRM registration and must be stopped on remove; failed `kthread_run()` is not explicitly checked as an error pointer. In-place bit reversal means tx buffer data cannot be reused after write without repopulation. Dirty updates always cover full lines, not arbitrary rectangles. PWM disable is manual on remove.

Test signals: Validate every model match-data mode, software/external/PWM VCOM paths, kthread stop on remove, line-damage expansion, bit-reversed SPI command bytes, clear on enable/disable, enable GPIO polarity, and XRGB8888-to-mono conversion for full and partial-line updates.

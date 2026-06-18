# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/pixpaper.c

Purpose: This custom SPI DRM driver supports the Mayqueen PIXPAPER color e-ink panel. It exposes a fixed 122x250 XRGB8888 DRM display while programming a 128-pixel-wide e-paper controller buffer and converting each visible pixel into a 2-bit white/black/yellow/red packed format.

Important APIs, types, and functions: `struct pixpaper_panel` owns DRM objects, SPI device, and reset/busy/dc GPIOs. `pixpaper_wait_for_panel()` polls the busy GPIO with a 10-second timeout. `pixpaper_send_cmd()` and `pixpaper_send_data()` send one-byte SPI transactions with D/C GPIO control and an error accumulator. `pixpaper_panel_hw_init()` resets the panel and writes a long sequence of documented and reverse-engineered registers. `pack_pixels_to_byte()` thresholds XRGB8888 pixels into four 2-bit panel pixels per byte. `pixpaper_plane_atomic_update()` streams the packed frame and triggers power-on/display refresh.

Control flow: Probe allocates DRM state, forces SPI mode 0 and 8 bits per word, applies a default SPI speed if DT omitted it, sets a 32-bit DMA mask, gets reset/busy/dc GPIOs, performs hardware init immediately, initializes DRM mode config, creates a shadow primary plane for XRGB8888, CRTC, encoder, SPI connector, registers DRM, and starts client setup. CRTC enable sends power-on and waits. CRTC disable sends power-off. Plane update enters the DRM device, validates framebuffer visibility, sends data-start, loops over all 250 rows and 32 bytes per row, sends packed bytes with busy waits, powers on, and sends display-refresh with AC VCOM.

State and persistence: Software state is mostly DRM state plus GPIO/SPI handles; there is no cached previous frame or partial update tracking. Hardware state includes the many power/PLL/resolution/VCOM/timing/unknown registers, panel power state, and e-paper image memory. Error propagation is stored in a small `pixpaper_error_ctx` during command sequences.

Dependencies and integration points: Binds to `mayqueen,pixpaper` or `pixpaper`. Uses SPI, GPIO reset/busy/dc, DRM shmem helpers, shadow-plane helpers, fixed connector modes, fbdev shmem, and DMA mask setup. The driver imports the DMA_BUF namespace.

Risks: Several register values are explicitly undocumented and derived from userspace examples; changing them can destabilize or damage panels. Busy-wait timeout only warns in `pixpaper_wait_for_panel()` and then continues. Color thresholds are simplistic and map unknown colors to white. Plane update performs full-frame synchronous SPI transfer for every damage event. Initialization occurs at probe, so failed panel hardware blocks DRM registration.

Test signals: Validate hardware init sequence on real panel, busy timeout diagnostics, full-frame update timing, color threshold mapping for black/white/red/yellow, fixed 122x250 mode with 128-byte row padding, power on/off commits, default SPI speed fallback, and remove with active display.

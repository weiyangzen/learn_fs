## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_crtc.c

Purpose: implements the ASPEED GFX simple display pipe: mode timing programming, framebuffer base updates, controller enable/disable, and vblank interrupt control.

Important functions are `aspeed_gfx_set_pixel_fmt`, `aspeed_gfx_crtc_mode_set_nofb`, `aspeed_gfx_pipe_enable`, `aspeed_gfx_pipe_disable`, `aspeed_gfx_pipe_update`, `aspeed_gfx_enable_vblank`, `aspeed_gfx_disable_vblank`, and `aspeed_gfx_create_pipe`. Supported formats are `DRM_FORMAT_XRGB8888` and `DRM_FORMAT_RGB565`.

Control flow: pipe enable programs pixel format, sync polarities, interlace bit, horizontal/vertical totals/display/sync ranges, line offset/terminal count, FIFO thresholds, then switches the SCU DAC source and CRT/DAC enable bits. Pipe update handles pending vblank events under `event_lock`, obtains the DMA GEM address, and writes `CRT_ADDR`. Vblank callbacks set/clear interrupt enable/status bits in `CRT_CTRL1`.

State persists in CRT MMIO registers, SCU DAC mux bits, vblank event state, and the active framebuffer DMA address. Dependencies are DRM simple KMS, GEM DMA helpers, regmap, clock/reset initialized by probe, and display modes constrained elsewhere. Risks include returning early from `mode_set_nofb` on unsupported format without failing the atomic commit, fixed pixel clock limitations, terminal-count math tied to `scan_line_max`, and missing GEM object handling. Test signals are visible scanout after enable, page flips updating `CRT_ADDR`, vblank event delivery, format switching, and clean disable of CRT/DAC.

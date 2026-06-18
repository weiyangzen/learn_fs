# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_gdp.c

Purpose: Implements GDP graphics display planes for framebuffer scanout and overlays. GDP planes use DMA command nodes chained through `GAM_GDP_NVN` and synchronized with VTG field events.

Important APIs/functions: `sti_gdp_create()` allocates/registers a DRM universal plane, initializes DMA node banks, clocks, and VTG notifier. `sti_gdp_atomic_check()` validates format, DMA GEM backing, destination/source bounds, and sets GDP pixel-clock parent/rate when available. `sti_gdp_atomic_update()` builds top/bottom field nodes, calculates PML/PMP/size/VTG positions, handles progressive/interlaced NVN update rules, and posts the next node. `sti_gdp_field_cb()` tracks current top/bottom field and finalizes flushing disables. `sti_gdp_disable()` marks nodes ignored, unregisters VTG, disables clock, and marks the plane disabled.

Control flow: Two node banks avoid overwriting the node currently consumed by hardware. Atomic update chooses a free bank, fills top/bottom nodes, and either directly writes NVN or patches the current node chain depending on current hardware state and interlace field. CRTC flush enables the plane at the mixer after update.

State/persistence: `struct sti_gdp` persists register base, optional GDP pixel clock and parent clocks, two DMA node banks, current-field flag, VTG pointer, and embedded `sti_plane` status/FPS.

Dependencies/integration: Uses DRM atomic plane helpers, DMA GEM helpers, VTG coordinate helpers, compositor VTG lookup, mixer z-order/status programming, and debugfs node/register dumps.

Risks/test signals: Scaling is not supported; larger destinations are clamped and smaller are cropped with debug warnings. DMA node allocation has alignment checks but no cleanup path on partial failure. Test all supported formats, interlaced vs progressive updates, repeated atomic no-op detection, disable synchronization, GDP debugfs node addresses, and underflow status.

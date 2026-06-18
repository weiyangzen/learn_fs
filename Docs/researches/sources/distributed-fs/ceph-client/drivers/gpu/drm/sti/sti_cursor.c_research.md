# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_cursor.c

Purpose: Implements the STI hardware cursor as a DRM universal cursor plane. Hardware accepts CLUT8 cursor data, so the driver exposes ARGB8888 and converts into a DMA pixmap plus generated CLUT.

Important APIs/functions: `sti_cursor_create()` allocates `struct sti_cursor`, allocates a 256-entry CLUT with `dma_alloc_wc()`, initializes the CLUT, registers a DRM cursor plane, and installs atomic helpers. `sti_cursor_atomic_check()` validates 1..128 source size, reallocates the pixmap when dimensions change, and verifies a DMA GEM object exists. `sti_cursor_atomic_update()` converts ARGB8888 to CLUT8, writes active-window, pixmap address, pitch/size, position, CLUT address, and sets `CUR_CTL_CLUT_UPDATE`. `sti_cursor_atomic_disable()` marks the STI plane disabling.

Control flow: The atomic check owns pixmap allocation because cursor size drives buffer size. Atomic update is purely register programming and status transition to `STI_PLANE_UPDATED`; the CRTC flush later enables it in the mixer. Cursor disable is finalized immediately by CRTC flush because cursor does not require GDP/HQVDP DMA retirement.

State/persistence: Cursor keeps current width/height, CLUT virtual/physical address, and DMA pixmap metadata. Plane status and FPS counters live in embedded `struct sti_plane`.

Dependencies/integration: Uses DRM plane helpers, DMA GEM framebuffer helpers, write-combined DMA allocation, VTG coordinate helpers, mixer/CRTC path through common plane status, and debugfs for register inspection.

Risks/test signals: No explicit destroy-time freeing is installed for pixmap/CLUT beyond partial create failure; devm lifetime and plane cleanup must match device teardown. Conversion assumes GEM CPU virtual address is valid. Test cursor size limits, repeated resize, negative/offscreen coordinates clamped by DRM state, debugfs CLUT/pixmap addresses, and cursor enable/disable over atomic commits.

## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_plane.c

Purpose: shared Armada plane helper plus primary plane implementation. It translates DRM atomic plane state into Armada source/destination register fields, DMA addresses, pitches, interlace bookkeeping, and primary graphics-layer register updates.

Important functions are `armada_drm_plane_calc`, `armada_drm_plane_atomic_check`, `armada_drm_primary_plane_atomic_update`, `armada_drm_primary_plane_atomic_disable`, `armada_plane_reset`, `armada_plane_duplicate_state`, and `armada_drm_primary_plane_init`. Supported primary formats include packed YUV and common RGB formats.

Control flow: atomic check validates scaling/clipping, enforces even destination y coordinates for interlaced modes, computes packed height/width fields, and calculates two field addresses for interlace. Primary update then queues changed geometry, start-address, pitch, format, modifier, palette, frame-toggle, enable, and smoothing writes. Disable clears `CFG_GRA_ENA` and powers down cursor/palette/slave/graphics FIFO SRAM blocks.

State lives in `struct armada_plane_state` and hardware registers queued through `armada_reg_queue_*`. Dependencies are DRM atomic helpers, Armada framebuffer/GEM helpers, CRTC register queue state, and `armada_hw.h` bit definitions. Risks include address truncation into 32-bit registers, interlace field-address assumptions, pitch width limits, and stale register state if mode-change checks miss a needed write. Test signals are primary scanout in every listed format, page flips with unchanged pitch, interlaced mode validation, scaled versus unscaled smoothing bit transitions, and no graphics FIFO underflow.

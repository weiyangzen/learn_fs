# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dpu.c

Purpose: Unisoc display processing unit DRM CRTC and plane implementation. It programs layer registers, DPI/eDPI timing, interrupts, vblank, and component binding.

Important APIs and types: `struct sprd_plane` wraps `drm_plane`; `struct sprd_dpu` and `struct dpu_context` are declared in the header. Format/rotation/blend conversion helpers map DRM plane state to DPU register bits. `sprd_dpu_run()` and `sprd_dpu_stop()` are exported to the DSI encoder. Component bind creates six planes and one CRTC.

Control flow: master component bind calls `sprd_dpu_bind()`, which creates planes, initializes the CRTC, maps registers, requests IRQ, and initializes wait queues. During atomic mode set, `sprd_crtc_mode_set_nofb()` converts DRM mode to videomode and chooses DPI versus EDPI based on the connected DSI slave's video flag. Plane updates program layer addresses, pitch, position, crop, alpha, format, blend, and rotation. CRTC flush triggers register update or run; IRQ signals update/stop events and vblank.

State and persistence: `dpu_context` holds MMIO base, IRQ, interface type, current videomode, stopped flag, wait queue, and event flags. Hardware layer registers persist until disabled or overwritten.

Dependencies and integration: depends on DRM atomic helpers, DMA GEM framebuffer addresses, OF graph, component framework, DSI state, wait queues, IRQ handling, and memory-mapped registers.

Risks: plane creation uses a hard-coded CRTC mask of `1` and six layers. `sprd_plane_atomic_disable()` assumes `old_state->crtc` is valid. DPU waits are interruptible but treat any nonzero return as success, so interrupted waits may look successful. Address programming uses 32-bit DMA addresses, which may not be enough on all DMA configurations. No explicit runtime PM calls are present in the DPU file despite master commit tail using RPM.

Test signals: multi-plane composition, each supported pixel format, alpha/blend/rotation properties, EDPI stop/update timing, IRQ/vblank, underflow warning handling, and OF graph CRTC discovery.

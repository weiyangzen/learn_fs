# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dpu.h

Purpose: DPU internal definitions for the SPRD DRM driver.

Important APIs and types: defines interface enum values `SPRD_DPU_IF_DPI` and `SPRD_DPU_IF_EDPI`, `struct dpu_context`, `struct sprd_dpu`, cast helper `to_sprd_crtc()`, MMIO helpers `dpu_reg_set()`/`dpu_reg_clr()`, layer register helpers, and public `sprd_dpu_run()`/`sprd_dpu_stop()`.

Control flow: DPU and DSI sources share this header so the DSI encoder can start/stop the DPU around PHY/host enable/disable.

State and persistence: `dpu_context` documents the persistent hardware and synchronization state: base, IRQ, interface type, videomode, stopped flag, wait queue, and event booleans.

Dependencies and integration: includes Linux platform/device/videomode headers and DRM CRTC/fourcc/vblank APIs.

Risks: inline register helpers do relaxed read-modify-write without locking, so callers must serialize register programming through atomic commit/enable paths. Layer offset math assumes fixed `DPU_LAY_REG_OFFSET`.

Test signals: compile integration with both DPU and DSI, plus register programming tests for set/clear/layer index offsets.

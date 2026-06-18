
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_encoder.h

## Purpose
Defines Nouveau's encoder wrapper and DisplayPort/MST state shared by the display implementation. It bridges DRM encoder objects, NVIF output objects, BIOS DCB data, connector association, DP training state, audio flags, and display-specific callbacks.

## Important APIs, Types, and Functions
Primary types are `struct nouveau_encoder` and `struct nv50_mstm`. Helpers include `nouveau_encoder()`, `to_drm_encoder()`, and the external `find_encoder()`. The header declares DP functions from `nouveau_dp.c`: `nouveau_dp_detect()`, `nouveau_dp_train()`, `nouveau_dp_power_down()`, `nouveau_dp_link_check()`, `nouveau_dp_irq()`, and `nv50_dp_mode_valid()`. It also declares connector lookup helpers and MST functions `nv50_mstm_detect()`, `nv50_mstm_remove()`, and `nv50_mstm_service()`.

## Control Flow
Display code stores hardware programming callbacks in each encoder and uses the inline wrappers to move between DRM and Nouveau encoder types. DP detection/training/control paths update and consume the nested `dp` state. MST state is managed through `struct nv50_mstm`, whose flags are protected by the encoder's `dp.hpd_irq_lock`.

## State and Persistence
`struct nouveau_encoder` persists per output. It holds DCB output data, NVIF output handle, output resource index, bound connector, optional I2C adapter, currently programmed CRTC and mode, audio enable flag, HDMI enable flag, DP caps/DPCD/rates/lane/bandwidth/training state/downstream descriptor/sink count, interlace capability, and save/restore/update callbacks. `struct nv50_mstm` persists MST topology state, including topology manager, `can_mst`, `is_mst`, `suspended`, `modified`, `disabled`, and link count.

## Dependencies and Integration Points
The header depends on NVIF output definitions, BIOS DCB definitions, DRM DP and MST helpers, and legacy display encoder wrappers. It is consumed by DP, connector, and NV50 display code.

## Risks and Test Signals
Risks include stale cached DP state, lock ordering around HPD IRQ service, MST suspend/resume transitions, and callback assumptions about programmed CRTC versus DRM's proposed state. Test signals include encoder enumeration, DP hotplug, MST topology changes, display suspend/resume, audio enable transitions, and link training/state cache resets.

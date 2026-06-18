# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drm.c

Purpose: implements the in-kernel VSP1 interface used by the Renesas DU DRM/KMS driver. It configures internal display pipelines, maps DRM plane state onto RPF/BRx/WPF/LIF entities, handles CRC/writeback, and exports DU-facing symbols.

Important APIs and functions: exported functions include `vsp1_du_init()`, `vsp1_du_setup_lif()`, `vsp1_du_atomic_begin()`, `vsp1_du_atomic_update()`, `vsp1_du_atomic_flush()`, `vsp1_du_map_sg()`, and `vsp1_du_unmap_sg()`. Internal helpers set up RPF inputs, arbitrate BRU/BRS, insert UIF for CRC, set output formats, configure entities, and signal DU completion.

Control flow: `vsp1_drm_init()` creates one pipeline per LIF and permanently attaches WPF and LIF. `vsp1_du_setup_lif()` enables or disables a CRTC pipeline; enable sets dimensions, configures input/output formats, resumes the device, commits an initial display list, and starts the pipeline. Atomic update stores per-RPF memory, format, crop, compose, zpos, alpha, and color range. Atomic flush optionally configures writeback, re-sorts inputs by z-order, reconfigures BRx/UIF/RPF links, and commits a new display list.

State and persistence: `struct vsp1_drm` stores pipeline state, global lock, and per-RPF input rectangles/color metadata. `force_brx_release` plus wait queues coordinate sharing BRU/BRS between two display pipelines. Display-list managers persist active hardware configuration until replaced at frame end.

Dependencies and integration: depends on `include/media/vsp1.h` DU API, V4L2 subdev pad operations, DMA mapping through the VSP/FCP bus master, VSP1 entity/display-list/pipeline helpers, and UIF CRC support.

Risks and test signals: risks include BRx arbitration timeouts, stale disabled RPFs remaining in hardware routes, format propagation failures, writeback flag lifetime, and non-coherent DMA assumptions. Test atomic modesets, plane enable/disable/z-order changes, dual-pipeline BRU/BRS contention, CRC source selection, writeback capture, and suspend/resume with active display.

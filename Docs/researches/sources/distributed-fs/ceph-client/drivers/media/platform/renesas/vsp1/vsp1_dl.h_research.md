# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_dl.h

Purpose: public-private interface for VSP1 display-list management used by all VSP1 entities, pipelines, video paths, and DRM integration.

Important APIs and types: declares opaque `vsp1_dl_body`, `vsp1_dl_body_pool`, `vsp1_dl_list`, and `vsp1_dl_manager`; frame-end flags `VSP1_DL_FRAME_END_COMPLETED`, `VSP1_DL_FRAME_END_WRITEBACK`, and `VSP1_DL_FRAME_END_INTERNAL`; and `struct vsp1_dl_ext_cmd` for extended display-list command payloads. Function prototypes cover manager setup/create/reset/destroy, body pool lifecycle, body writes, list acquisition, chaining, and commit.

Control flow role: callers acquire a list from a manager, obtain body0, write register/data pairs through `vsp1_dl_body_write()`, optionally attach extra bodies or chains, and commit with frame-end flags. IRQ code calls `vsp1_dlm_irq_frame_end()` to retire or promote list state.

State and persistence: the header abstracts DMA-backed persistent list state while hiding implementation details. The frame-end flags intentionally mirror external DU status bits, making this header part of the DRM notification contract.

Dependencies and integration: includes Linux types and uses `list_head`, DMA addresses, and VSP1 device types indirectly. It is included by almost every entity implementation.

Risks and test signals: changing flag values can break DU status synchronization. Prototype changes affect many objects. Compile all VSP1 sources and run streaming tests that cover single-shot, continuous, chained, extended-DL, and writeback paths.

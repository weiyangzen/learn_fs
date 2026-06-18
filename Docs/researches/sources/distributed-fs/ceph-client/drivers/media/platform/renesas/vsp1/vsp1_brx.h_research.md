# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_brx.h

Purpose: declares the VSP1 BRU/BRS blend entity state and constructor. It is the shared contract between entity creation, DRM pipeline setup, and BRx stream configuration.

Important APIs and types: `BRX_PAD_SINK(n)` maps input pad indexes. `struct vsp1_brx` embeds `struct vsp1_entity`, the register `base`, a V4L2 control handler, `inputs[VSP1_MAX_RPF]` linking BRx pads to active RPFs, and `bgcolor`. `to_brx()` converts from subdev to container, and `vsp1_brx_create()` constructs either `VSP1_ENTITY_BRU` or `VSP1_ENTITY_BRS`.

Control flow role: `vsp1_drv.c` calls `vsp1_brx_create()` based on feature flags. `vsp1_drm.c` uses `to_brx()` and `inputs[]` to sort and attach RPF layers. `vsp1_brx.c` uses the same structure for V4L2 controls and display-list register generation.

State and persistence: `inputs[]` is transient pipeline state but persists across atomic DRM setup until reconfigured. `bgcolor` persists as a V4L2 control-backed value. The embedded entity owns pad state, routing, pipe membership, and media links.

Dependencies and integration: includes media entity, V4L2 controls/subdev, and `vsp1_entity.h`; forward-declares `vsp1_device` and `vsp1_rwpf`.

Risks and test signals: array sizing must remain compatible with maximum RPF and BRU pad counts. Test compile with variants that expose BRU only, BRS only, and both, and exercise DRM layer count transitions above and below two inputs.

# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-comp.h

## Purpose
This header defines the MDP3 component model used by MediaTek's image processor driver. It names every public hardware component, classifies components by functional type, and provides command-queue register/event helper macros used by the component operation implementations.

## Important APIs, Types, And Functions
The register macros wrap `cmdq_pkt_write[_mask]`, `cmdq_pkt_wfe`, `cmdq_pkt_clear_event`, `cmdq_pkt_set_event`, and `cmdq_pkt_poll[_mask]`. `enum mtk_mdp_comp_id` is the stable component namespace, while `enum mdp_comp_type` groups components into RDMA, RSZ, WROT, WDMA, path, color, HDR, merge, dummy, and external/direct-link classes. `struct mdp_comp_data` binds match data, clock/register offsets, and blend metadata. `struct mdp_comp` is the runtime component object. `struct mdp_comp_ctx` binds a component to firmware parameters and frame input/output arrays. `struct mdp_comp_ops` defines the per-component command-building callbacks.

## Control Flow
The header does not execute control flow directly. It defines the callback phases used by command construction: flag derivation, component init, frame config, subframe config, event wait, subframe advance, and post-processing. Runtime code builds `mdp_comp_ctx` objects from firmware component parameters, then dispatches these callbacks while emitting CMDQ packets.

## State, Persistence, And Dependencies
State is runtime-only: MMIO bases, GCE events, clocks, component IDs, and operation tables are kept in `struct mdp_comp`. It depends on `mtk-mdp3-cmdq.h`, V4L2 geometry types through users, and firmware image parameter structs.

## Integration Points
`mtk-mdp3-core.c` allocates and destroys components through `mdp_comp_config()` and `mdp_comp_destroy()`. `mtk-mdp3-m2m.c` and the CMDQ path consume component contexts after VPU path planning. Platform data in `mtk-mdp3-cfg.h` supplies `mdp_comp_data`.

## Risks
The component ID order is a firmware/platform contract; reordering breaks table indexes. The mask macros assume a matching `ofst##_MASK` symbol. Clock count and DTS register offsets must match device tree data.

## Test Signals
Useful signals are successful probe with all components configured, correct CMDQ packets for each pipeline component, no missing clocks/events in device tree, and image transforms completing without GCE timeout.

## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_drv.h

### Purpose

`mtk_disp_drv.h` declares cross-component MediaTek display-block functions used to populate DDP component function tables.

### Important APIs, types, and functions

The header declares clock/config/start/stop and feature callbacks for AAL, CCORR, COLOR, DITHER, DPI, DSI, GAMMA, MERGE, OVL, OVL adaptor, RDMA, MDP RDMA, and PADDING. It also declares plane-layer operations, vblank callback registration, format/blend/AFBC queries, color management operations, mutex connection helpers, mode validation, and CMDQ-aware start/stop/config variants for some blocks.

### Control flow

There is no runtime flow in the header. `mtk_ddp_comp.c` binds these declarations into per-component callback tables, and `mtk_crtc.c` invokes them indirectly through DDP wrappers.

### State and persistence behavior

The header owns no state. State is stored in each display block driver and in DDP component structures.

### Dependencies

It includes CMDQ, MMSYS, mutex, MDP RDMA, and plane headers because declarations reference those types. It also relies on DRM mode/color types being visible through included headers and consumers.

### Integration points

This is the broad internal ABI for the MediaTek display pipeline. It connects the DDP registry to implementation files for display processing blocks, encoders, and plane-capable components.

### Risks

The header is wide and tightly couples many display blocks. Signature changes require coordinated edits across the registry and drivers. Optional features are represented by missing function-table callbacks, so declarations alone do not imply a component supports the operation.

### Test signals

Build coverage of the full `mediatek-drm` aggregate, plus runtime modeset, vblank, plane, color-management, route, and output tests, validate this internal contract.

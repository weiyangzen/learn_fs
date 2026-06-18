## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ovl_adaptor.c

### Purpose

`mtk_disp_ovl_adaptor.c` implements a pseudo overlay component for newer MediaTek display systems where overlay behavior is assembled from ETHDR, multiple MDP RDMA blocks, MERGE blocks, and padding blocks. It lets the rest of the DRM pipeline treat that collection as one DDP component.

### Important APIs, types, and functions

The key types are `enum mtk_ovl_adaptor_comp_type`, `enum mtk_ovl_adaptor_comp_id`, `struct ovl_adaptor_comp_match`, and `struct mtk_disp_ovl_adaptor`. `comp_matches[]` maps adaptor-local component slots to DDP component IDs, alias IDs, and function tables. Public hooks include layer/config/start/stop, power and clock control, mode validation, format/blend queries, DMA device lookup, vblank forwarding, mutex add/remove, connect/disconnect, and presence detection.

Important functions are `mtk_ovl_adaptor_layer_config()`, `mtk_ovl_adaptor_power_on/off()`, `mtk_ovl_adaptor_clk_enable/disable()`, `mtk_ovl_adaptor_add_comp/remove_comp()`, `mtk_ovl_adaptor_connect/disconnect()`, `mtk_ovl_adaptor_is_comp_present()`, `ovl_adaptor_comp_init()`, and the component/master bind callbacks.

### Control flow

Probe allocates adaptor state, scans the parent display node for compatible ETHDR, MDP RDMA, MERGE, and padding child devices, maps them into adaptor slots by alias ID, adds component matches, stores the MMSYS device passed as platform data, registers a component master, enables runtime PM, and registers the pseudo component. Master bind calls `component_bind_all()` on children and then marks `children_bound`; the component bind defers until that is true.

Layer configuration maps each logical layer to two MDP RDMA engines and one MERGE. Disabled or zero-sized layers stop both RDMAs and merge then update ETHDR layer state. Enabled layers align width down to two pixels for the 1T2P ETHDR domain, split over two pipes if the aligned width exceeds 1920, programs MERGE dimensions and MMSYS async merge, configures left and optional right MDP RDMA, starts/stops the relevant engines, and finally programs ETHDR layer blending.

### State and persistence behavior

The adaptor itself stores only child device pointers, MMSYS device, and bind state. Persistent hardware state lives in child components: MDP RDMA memory fetch configuration, MERGE sizes and enable bits, ETHDR layer state, padding state, MMSYS routing, and mutex membership. Power and clock helpers explicitly walk children because the pseudo device has no independent hardware power domain.

### Dependencies

It depends on DRM format and OF component matching, MediaTek MMSYS and mutex APIs, CMDQ, MDP RDMA, MERGE, ETHDR, padding, and DDP component function tables. It is tightly coupled to device-tree aliases such as `vdo1-rdma`, `merge`, `ethdr`, and `padding`.

### Integration points

`mtk_drm_drv.c` detects adaptor-exclusive child nodes and inserts `DDP_COMPONENT_DRM_OVL_ADAPTOR` into graph-built paths. The CRTC/plane path calls the adaptor just like OVL for layer count, format list, blend modes, vblank, and DMA device. MMSYS route connection wires MDP RDMA to MERGE and MERGE to ETHDR, then ETHDR to the next display component.

### Risks

The error unwind in `mtk_ovl_adaptor_clk_enable()` uses the current `comp` variable while walking prior indices, which is a bug risk because it may call `clk_disable()` with the wrong device pointer. `mtk_ovl_adaptor_clk_disable()` additionally calls `pm_runtime_put()` for indices before MERGE even though power-on is handled separately, so ordering must match child PM expectations. Width is aligned down, so odd-width layer handling relies on the pipeline accepting the dropped pixel or upstream alignment. Device-tree alias mismatches cause components to be skipped. Connect/disconnect currently wires only a fixed subset of MDP RDMA paths.

### Test signals

Use MT8195/MT8188 graph-built pipelines with OVL adaptor, multi-layer composition, layers wider than 1920 that require dual pipe, odd widths, disable/enable layer transitions, vblank through ETHDR, mutex route programming, suspend/resume power sequencing, clock error injection, and mode validation through the MERGE child.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_0_sc8280xp.h

Purpose: this header defines the DPU 8.0 SC8280XP catalog through `dpu_sc8280xp_cfg`. It describes a large laptop-class display block with many DP interfaces and multiple DSC engines.

Important data: capabilities include source split, dim layer, idle PC, 3D merge, 5120 max line width, and eleven blend stages. The catalog lists six CTLs, four VIG plus four DMA SSPPs, six paired LMs, four DSPPs, six pingpongs, three 3D merge blocks, and six DSC slices arranged as three DCE bases with paired sub-blocks. The interface table is the distinguishing feature: DP `intf_0`, DSI `intf_1`/`intf_2`, and DP `intf_3` through `intf_8`, with comments documenting MST pairings.

Integration points: resource-manager code uses the larger interface set to support multi-DP/MST topologies. `dpu_encoder_update_topology()` and `dpu_crtc_get_topology()` depend on DSC count, interface count, and 3D merge availability for LM/DSC allocation. Interrupt indices in CTL, pingpong, DSI tear, and interface entries are consumed by the central IRQ layer and physical encoders.

State and persistence: there is no mutable state. The catalog persists as read-only kernel data and determines hardware block availability for the device lifetime.

Risks: the many DP interface/controller mappings are easy to misroute, particularly MST companion comments. There is no WB entry in this catalog, so writeback assumptions copied from adjacent SoCs would be wrong. The performance section has TODO/FIXME notes for QoS table accuracy and shares some SC7180/SC8180X tables, making underrun and bandwidth validation important.

Test signals: boot and modeset on SC8280XP, all DP controller mappings, MST pairing, dual-DSI if present, DSC modes using more than four slices, high-resolution LM split, vblank/underrun IRQs across all interfaces, and bandwidth/clock validation near `max_bw_high`.

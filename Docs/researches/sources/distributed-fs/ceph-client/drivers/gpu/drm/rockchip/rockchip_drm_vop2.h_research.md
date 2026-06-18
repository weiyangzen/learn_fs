# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop2.h

## Purpose

`rockchip_drm_vop2.h` defines the public and internal data model for VOP2 hardware: version constants, feature flags, output-interface helpers, window register indices, SoC data structures, runtime structs, interrupt bits, register offsets/fields, layer IDs, regmap accessors, and cfg-done helper.

## Important APIs, Types, and Functions

- `VOP2_VERSION` and `VOP_VERSION_RK*` identify supported VOP2 IP revisions.
- `enum vop2_win_regs` names per-window regmap fields consumed by plane update.
- `struct vop2_win_data`, `vop2_video_port_data`, and `vop2_data` are SoC descriptor contracts.
- `struct vop2_win`, `vop2_video_port`, and `vop2` are runtime window, CRTC/video-port, and global controller objects.
- `struct vop2_ops` provides SoC-specific hooks for interface muxing, background delay, and overlay setup.
- Inline helpers wrap regmap operations, window writes, container conversions, cluster-window detection, and `vop2_cfg_done`.

## Control Flow

VOP2 code writes window fields through `vop2_win_write`, VP-relative registers through `vop2_vp_write`, and commits delayed state with `vop2_cfg_done`, which sets global cfg-done enable plus the VP-specific cfg-done bit and write mask.

## State and Persistence Behavior

Descriptor structs are static per SoC, while runtime structs persist for the component lifetime. `vop2` owns shared clocks, syscon maps, regmap, enable count, old overlay selections, and windows. `vop2_video_port` owns per-CRTC clock/event/layer state.

## Dependencies and Integration Points

The header depends on Linux regmap, DRM modes, VOP helper definitions, Rockchip DRM state, and device-tree endpoint IDs from `dt-bindings/soc/rockchip,vop2.h`. It is consumed by VOP2 implementation and SoC register tables.

## Risks and Edge Cases

Register offsets and bitfields are SoC-critical across RK3568, RK3588, RK3528, RK3562, and RK3576. The cfg-done helper notes write-mask differences. `ROCKCHIP_VOP2_PHY_ID_INVALID = -1` should be handled carefully with unsigned fields. Endpoint helper predicates must stay synchronized with bindings.

## Test Signals

Build every VOP2 SoC table, then validate cfg-done commits, interface mux selection, per-window regmap fields, power-domain bits, interrupts, and debugfs register dumps on target hardware.

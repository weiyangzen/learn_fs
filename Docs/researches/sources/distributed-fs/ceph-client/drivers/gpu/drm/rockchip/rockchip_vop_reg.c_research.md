## sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop_reg.c

### Purpose

`rockchip_vop_reg.c` is the platform data table for the earlier Rockchip VOP display controller family. It maps generic VOP concepts such as windows, scaling, alpha, interrupts, modeset timing, output pins, AFBC, YUV conversion, LUTs, and common control bits to concrete register offsets/masks for RK3036, RK3126, PX30, RK3066, RK3188, RK3288, RK3366, RK3368, RK3399, RK3228, RK3328, RK3506, and RV1126.

### Important APIs, Types, and Functions

`_VOP_REG()`, `VOP_REG()`, `VOP_REG_SYNC()`, and `VOP_REG_MASK_SYNC()` create `struct vop_reg` descriptors with offset, mask, shift, write-mask behavior, and relaxed/non-relaxed write semantics. The core data structures are `struct vop_scl_regs`, `struct vop_scl_extension`, `struct vop_win_phy`, `struct vop_win_data`, `struct vop_intr`, `struct vop_modeset`, `struct vop_output`, `struct vop_common`, `struct vop_misc`, `struct vop_yuv2yuv_phy`, `struct vop_win_yuv2yuv_data`, `struct vop_afbc`, and `struct vop_data`.

The only executable functions are `vop_probe()`, which rejects devices without an OF node and registers `vop_component_ops`, and `vop_remove()`, which unregisters the component. `vop_driver_dt_match` binds compatible strings to a specific `struct vop_data`; `vop_platform_driver` exposes the platform driver.

### Control Flow

The platform driver is selected by OF compatible. Probe does not parse hardware itself; it lets the common VOP component code retrieve `of_device_id.data` and use the static table for later atomic modesets. During normal display operation, common code iterates windows, programs fields through `struct vop_reg` descriptors, enables interrupts, applies timing and output configuration, sets cfg-done, and uses optional AFBC/YUV2YUV/LUT descriptors when present.

The data is layered from reusable register blocks. For example, RK3288-style full windows are reused by RK3368/RK3399/RK3228/RK3328 with base offsets or slight output/common overrides; PX30-style windows are reused by RV1126 and RK3506 variants. Interrupt arrays map logical `DSP_HOLD_VALID_INTR`, `FS_INTR`, `LINE_FLAG_INTR`, and `BUS_ERROR_INTR` positions to differing status/enable/clear layouts.

### State and Persistence Behavior

This file owns no mutable runtime state beyond component registration. Its descriptors drive persistent hardware register writes made by the common VOP driver. Per-SoC `vop_data` persists for the device lifetime and defines maximum output size, LUT size, supported modifiers, VOP version, feature flags, and number/type of DRM planes.

### Dependencies and Integration Points

It depends on `rockchip_drm_vop.h` for the descriptor types, `rockchip_vop_reg.h` for raw register offsets, DRM fourcc/plane constants, the Rockchip AFBC modifier, and the Linux component/platform/OF module APIs. It is integrated with the Rockchip DRM driver registration code and common VOP atomic plane/CRTC implementation.

### Risks and Edge Cases

The table is a hardware contract; wrong masks or base offsets can program unrelated registers. Reusing descriptors across related SoCs reduces duplication but can hide subtle register-layout differences. Some compatible strings represent "big" and "lit" variants with different max output, LUT size, and plane layout; matching the wrong compatible can expose unsupported planes or resolutions. `vop_probe()` rejects missing OF nodes, so non-DT instantiation is unsupported. Modifier lists must be accurate, especially RK3399 primary-plane AFBC. Cursor windows are sometimes substituted with overlay windows because dedicated cursor alpha support is incomplete.

### Test Signals

Build coverage should include Rockchip DRM with all listed compatibles. Runtime testing should cover probe from DT, plane enumeration, primary/overlay/cursor use, full and lite VOP variants, interrupt handling, line flag/vblank delivery, scaling limits, YUV formats and 10-bit formats where advertised, AFBC scanout on RK3399, gamma LUT updates, output enable/polarity per encoder type, and suspend/resume cfg-done restoration.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sunxi_engine.h

## Purpose

`sunxi_engine.h` defines the common abstraction for sunxi display engines used by the sun4i DRM driver. It describes optional/mandatory engine operations and provides inline wrappers for commit, layer initialization, color correction, and mode setting.

## Important APIs, Types, and Functions

- `struct sunxi_engine_ops`: callback table for `atomic_begin`, `atomic_check`, `commit`, mandatory `layers_init`, color correction enable/disable, `vblank_quirk`, and `mode_set`.
- `struct sunxi_engine`: common engine state with ops, OF node, regmap, numeric id, and list linkage.
- `sunxi_engine_commit()`: invokes optional commit callback.
- `sunxi_engine_layers_init()`: invokes mandatory layer creation callback or returns `ERR_PTR(-ENOSYS)`.
- `sunxi_engine_apply_color_correction()` / `disable_color_correction()`: optional RGB/YUV correction controls.
- `sunxi_engine_mode_set()`: optional per-mode update hook.

## Control Flow

CRTC and driver code hold a `struct sunxi_engine *` and call these inline wrappers instead of directly checking each callback. Optional hooks no-op when absent. Layer initialization is treated as required and returns an error pointer if missing. The engine list field supports discovery/association of engines elsewhere in the driver.

## State and Persistence Behavior

The engine object persists for the display engine lifetime. It references a device tree node and regmap owned elsewhere, carries a stable id, and participates in a list. The header itself does not implement locking or reference management; callers must coordinate lifecycle and list access.

## Dependencies and Integration Points

It forward-declares DRM types and depends on kernel list and error-pointer helpers being visible to including translation units. It integrates with sun4i CRTC atomic paths, mixer backends, TCON/TV output color correction, vblank handling, and layer construction.

## Risks and Edge Cases

- `layers_init` is documented mandatory but only enforced at runtime.
- Optional callbacks silently no-op, so missing ops can produce display behavior differences without obvious failures.
- The `vblank_quirk` callback runs in interrupt context per documentation; implementers must avoid sleeping.
- No locking contract is specified for `list` or mutable fields.

## Test Signals

Compile tests should cover all engine implementations. Integration tests should verify missing optional callbacks no-op safely, missing `layers_init` fails cleanly, color correction is applied/removed around TV encoder use, and vblank callbacks satisfy interrupt-context constraints.

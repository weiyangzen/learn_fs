# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_layer.h

## Purpose

`sun8i_vi_layer.h` defines VI layer register offsets, alpha/format/coarse-scaling fields, FCC global alpha definitions, forward declarations, and the VI plane constructor.

## Important APIs, Types, and Definitions

- `SUN8I_MIXER_CHAN_VI_LAYER_*()`: per-overlay attribute, size, coordinate, pitch, and low-address register offsets.
- `SUN8I_MIXER_CHAN_VI_OVL_SIZE()` and HDS/VDS macros: overlay size and coarse downscale registers.
- `SUN8I_MIXER_FCC_GLOBAL_ALPHA_REG`: global alpha register used by some DE2 FCC paths.
- Attribute bits: enable, RGB mode, framebuffer format field, DE3 alpha mode/value fields.
- `SUN8I_MIXER_CHAN_VI_DS_N()` and `DS_M()`: coarse scaling numerator/denominator encoding.
- `sun8i_vi_layer_init_one()`: public VI plane constructor.

## Control Flow and State

The macros compute register addresses from a channel base, overlay index, and plane index. The C implementation uses them during atomic updates to configure VI scanout and coarse scaling. No software state is stored in the header, but the macros define persistent hardware state layout.

## Dependencies and Integration Points

It includes DRM plane definitions and forward-declares sun8i types. It integrates with `sun8i_vi_layer.c`, `sun8i_mixer` channel base calculation, and hardware CSC/scaler programming.

## Risks and Edge Cases

- Register macros assume valid overlay and plane indices; invalid indices would compute unintended offsets.
- FCC global alpha is not per-plane in the macro, matching hardware global behavior and requiring higher-level constraints.
- High DMA address registers are not declared here, unlike the UI layer header.

## Test Signals

Register-trace tests should verify per-plane pitch/address offsets, coarse downscale register encodings, RGB/YUV mode bit behavior, and DE3 alpha field programming.

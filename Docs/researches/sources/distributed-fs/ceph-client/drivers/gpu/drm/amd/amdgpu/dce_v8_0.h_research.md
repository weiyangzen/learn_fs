# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.h

## Purpose

This header publishes the DCE 8.x IP block descriptors and the one externally callable helper for disabling the DCE engine. It is the public include boundary for other AMDGPU source files that need to register or quiesce this display generation without depending on the large implementation file.

## Important APIs and Types

- `extern const struct amdgpu_ip_block_version dce_v8_0_ip_block`
- `extern const struct amdgpu_ip_block_version dce_v8_1_ip_block`
- `extern const struct amdgpu_ip_block_version dce_v8_2_ip_block`
- `extern const struct amdgpu_ip_block_version dce_v8_3_ip_block`
- `extern const struct amdgpu_ip_block_version dce_v8_5_ip_block`
- `void dce_v8_0_disable_dce(struct amdgpu_device *adev)`

The declarations assume consumers already have visibility of `struct amdgpu_device` and `struct amdgpu_ip_block_version` through normal AMDGPU include ordering.

## Control Flow and State

The header carries no runtime state. Its declarations let ASIC discovery tables bind a DCE revision to the common DCE8 implementation, and let early ASIC code call `dce_v8_0_disable_dce()` before or outside normal DRM modeset setup.

## Dependencies and Integration Points

The guard macro `__DCE_V8_0_H__` protects inclusion. Integration is with AMDGPU IP block assembly and legacy display initialization. The implementation side is `dce_v8_0.c`.

## Risks and Test Signals

The main risk is declaration drift: any change to IP block symbol names or the disable helper signature must remain synchronized with users and `dce_v8_0.c`. Build coverage across DCE 8.0, 8.1, 8.2, 8.3, and 8.5 ASIC tables is the primary signal.

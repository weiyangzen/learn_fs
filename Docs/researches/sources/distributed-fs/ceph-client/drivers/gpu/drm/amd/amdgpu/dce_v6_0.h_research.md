# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.h

## Purpose

`dce_v6_0.h` is the public interface for the DCE6 AMDGPU display backend. It exposes the IP block descriptors for DCE 6.0 and 6.4 hardware and declares the early display-engine disable helper.

## Important APIs and Types

- Include guard: `__DCE_V6_0_H__`.
- `extern const struct amdgpu_ip_block_version dce_v6_0_ip_block;` declares the DCE 6.0 IP descriptor implemented in `dce_v6_0.c`.
- `extern const struct amdgpu_ip_block_version dce_v6_4_ip_block;` declares the DCE 6.4 descriptor, which uses the same function table as DCE 6.0 in the implementation.
- `void dce_v6_0_disable_dce(struct amdgpu_device *adev);` declares the helper that disables VGA render and active CRTC masters when ATOM BIOS reports DCE engine information.

## Control Flow and Integration

There is no executable logic in the header. Other AMDGPU source files include it to select DCE6/DCE6.4 IP blocks during ASIC setup or to call `dce_v6_0_disable_dce()` during low-level display quiescing. The implementation behind the descriptors installs the DCE6 `amd_ip_funcs` table and its DRM display callbacks.

## State and Persistence Behavior

The header owns no runtime state. The declared IP block descriptors are immutable constants in the C file. The declared disable function mutates device registers and depends on `struct amdgpu_device` state, but those side effects are in the implementation.

## Dependencies

The header assumes includers already have declarations for `struct amdgpu_ip_block_version` and `struct amdgpu_device`. It deliberately avoids local includes and exists as a narrow linkage boundary between ASIC setup code and the DCE6 display implementation.

## Risks and Test Signals

The risk surface is small and mostly compile/link oriented: declarations must stay synchronized with implementation symbols, and ASIC setup code must use the correct DCE6 or DCE6.4 descriptor. Test signals are build coverage for both descriptors and boot/probe validation on hardware paths that select DCE6.x, including any path that calls the disable helper before full mode-setting initialization.

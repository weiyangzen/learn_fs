# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.h

## Purpose

`dce_v10_0.h` is the public interface for the DCE10 AMDGPU display backend. It exposes the IP block descriptors used by device discovery/ASIC setup code and the early DCE disable helper used to quiesce display hardware before or during driver initialization.

## Important APIs and Types

- Include guard: `__DCE_V10_0_H__`.
- `extern const struct amdgpu_ip_block_version dce_v10_0_ip_block;` declares the DCE 10.0 IP descriptor implemented in `dce_v10_0.c`.
- `extern const struct amdgpu_ip_block_version dce_v10_1_ip_block;` declares the DCE 10.1 IP descriptor. In the implementation it shares the same function table as DCE 10.0 while advertising minor version 1.
- `void dce_v10_0_disable_dce(struct amdgpu_device *adev);` declares the display-engine disable routine that disables VGA render and active CRTC masters when the ATOM BIOS DCE engine info table is present.

## Control Flow and Integration

The header has no executable control flow; it allows other AMDGPU compilation units to reference DCE10 IP block versions and call the disable helper without including the full implementation. The concrete IP block functions are installed through `dce_v10_0_ip_block`/`dce_v10_1_ip_block`, whose `.funcs` member points to the DCE10 `amd_ip_funcs` table in the C file.

## State and Persistence Behavior

The header owns no state. The declared IP block objects are immutable `const` descriptors in the C file. The declared disable function mutates hardware display registers and depends on `amdgpu_device` runtime state, but those side effects are outside this header.

## Dependencies

This header intentionally relies on forward-visible AMDGPU core type declarations from includers: `struct amdgpu_ip_block_version` and `struct amdgpu_device`. It does not include other headers itself, keeping it lightweight but requiring callers to include AMDGPU core definitions in the right order.

## Risks and Test Signals

The main risk is interface drift: any change to the implementation exports, IP block naming, or disable-helper signature must be reflected here or callers will fail to compile. Test signals are build coverage for ASIC tables that reference DCE10/DCE10.1, plus boot validation that the selected IP block calls the DCE10 init/fini hooks and that any pre-init disable path links and executes correctly.

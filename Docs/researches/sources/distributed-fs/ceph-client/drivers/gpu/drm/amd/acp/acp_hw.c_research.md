# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/acp_hw.c

## Purpose
`acp_hw.c` provides a small hardware initialization gate for AMD ACP support inside amdgpu. It checks whether the ACP block is configured for I2S mode and rejects unsupported Azalia mode for the relevant hardware version.

## Important APIs, types, and functions
The exported-to-amdgpu function is `amd_acp_hw_init(struct cgs_device *cgs_device, unsigned acp_version_major, unsigned acp_version_minor)`. It reads `mmACP_AZALIA_I2S_SELECT` through `cgs_read_register()` for ACP version 2.2 and compares against `ACP_MODE_I2S`.

## Control flow
Initialization defaults `acp_mode` to I2S. For ACP 2.2, it reads the hardware select register. If the resulting mode is not I2S, it returns `-ENODEV`; otherwise it returns success. Other versions are accepted without a register read in this file.

## State and persistence behavior
The file stores no persistent or long-lived runtime state. It only reads an MMIO-backed register through the CGS device abstraction.

## Dependencies and integration points
It depends on `acp_gfx_if.h`, `cgs_common.h`, and the amdgpu CGS register access interface. It is pulled into `amdgpu.o` when `DRM_AMD_ACP` is enabled and is expected to be called by amdgpu ACP integration code before exposing ACP audio functionality.

## Risks and edge cases
The version check is narrow: only 2.2 reads the mode register, so behavior for later versions relies on external code or defaults. A stale or inaccessible CGS device would make the register read path unsafe if callers do not ensure initialization. Returning `-ENODEV` for non-I2S mode is correct for I2S audio but must not be treated as a fatal GPU probe error by callers.

## Test signals
Unit or hardware tests should cover ACP 2.2 with I2S and Azalia register values, other version numbers, invalid CGS/register access paths, and amdgpu probe behavior when ACP init returns `-ENODEV`.

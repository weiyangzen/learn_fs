# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/Makefile

## Purpose
Builds the AMDGPU Display Manager subcomponent when Display Core is enabled.

## Important APIs, Types, And Functions
When `CONFIG_DRM_AMD_DC` is set, `AMDGPUDM` includes core DM objects such as `amdgpu_dm.o`, plane/CRTC/IRQ/MST/color/services/helpers/SMU/PSR/replay/quirks/writeback/colorop/ISM support. `dc_fpu.o` is added when `CONFIG_DRM_AMD_DC_FP` is set. HDCP support adds `amdgpu_dm_hdcp.o`. Debugfs builds add CRC and debugfs objects. The file adds the DC include path and appends prefixed objects to `AMD_DISPLAY_FILES`.

## Control Flow
Kbuild conditionals decide which object names are appended. The parent display Makefile includes this file as part of the DAL build.

## State And Persistence
No runtime state. It controls compile-time inclusion of DM code.

## Dependencies And Integration Points
Depends on `CONFIG_DRM_AMD_DC`, optional `CONFIG_DRM_AMD_DC_FP`, optional `CONFIG_DEBUG_FS`, `AMDDALPATH`, and `FULL_AMD_DISPLAY_PATH`. It contributes objects consumed by the parent amdgpu display build.

## Risks
Object lists must stay synchronized with source files and feature gates. FPU-sensitive code must remain behind `CONFIG_DRM_AMD_DC_FP`. Debugfs-only CRC/debug objects should not be built without debugfs. HDCP is unconditionally added within DC, so missing HDCP source/dependency handling would break DC builds.

## Test Signals
Build with DC disabled, DC enabled without FP, DC enabled with FP, and DC plus DEBUG_FS. Confirm expected object inclusion and no unresolved symbols from optional DM features.

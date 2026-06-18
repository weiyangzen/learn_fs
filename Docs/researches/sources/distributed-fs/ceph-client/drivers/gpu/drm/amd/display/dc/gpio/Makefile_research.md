# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/Makefile

## Purpose

`dc/gpio/Makefile` assembles AMD Display Core GPIO support. It adds common GPIO service/base/pin/translate objects and generation-specific hardware factory/translate objects for DCE and DCN families.

## Important APIs, Types, And Functions

It defines common `GPIO`, `AMD_DAL_GPIO`, and per-generation variables for DCE60, DCE80, DCE110, DCE120, DCN10, DCN20, DCN21, DCN30, DCN315, DCN32, DCN401, and DCN42. Each generation appends paths to `AMD_DISPLAY_FILES`; DCE60 is gated by `CONFIG_DRM_AMD_DC_SI`.

## Control Flow

This is make-time flow only. The common GPIO objects are always appended, SI-era DCE60 objects are conditional, and later generations are unconditionally added under the AMD display build.

## State, Dependencies, Risks, And Test Signals

It changes build variables only and has no runtime state. It depends on `AMDDALPATH`, `AMD_DISPLAY_FILES`, and Kconfig. Risks include stale generation lists, duplicate or missing object inclusion, and path drift. Build tests across supported ASIC Kconfigs should catch unresolved factory/translator symbols.

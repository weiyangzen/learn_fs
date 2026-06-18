# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/Makefile

## Purpose
Top-level AMD Display Core Kbuild file. It establishes include paths, feature defines, and includes subcomponent Makefiles for DAL/DC, modules, DMUB, and HDCP.

## Important APIs, Types, And Functions
Defines `AMDDALPATH = $(RELATIVE_AMD_DISPLAY_PATH)`. Adds many `subdir-ccflags-y` include directories under `dc`, `modules`, and `dmub`. Defines `BUILD_FEATURE_TIMING_SYNC=0`. `DAL_LIBS` lists `amdgpu_dm`, `dc`, FreeSync, color, info packet, power, `dmub/src`, and HDCP. `AMD_DAL` turns those into Makefile paths and includes them.

## Control Flow
Kbuild includes this file from the amdgpu display build. This file includes each subcomponent Makefile, which appends objects into aggregate variables such as `AMD_DISPLAY_FILES`.

## State And Persistence
No runtime state. It controls compile-time object lists, include search paths, and feature macros.

## Dependencies And Integration Points
Depends on parent variables `RELATIVE_AMD_DISPLAY_PATH` and `FULL_AMD_DISPLAY_PATH`. Integrates all display subdirectories into the amdgpu driver build and provides include paths used by those sources.

## Risks
Include path order is broad and can hide accidental header coupling. `BUILD_FEATURE_TIMING_SYNC=0` is a compile-time feature gate marked temporary. Any missing subcomponent Makefile breaks display builds. Adding a new display module requires updating `DAL_LIBS` or a subcomponent Makefile.

## Test Signals
Build AMDGPU with DC enabled, confirm `AMD_DISPLAY_FILES` includes expected DM/DC/module/DMUB/HDCP objects, and verify no include path regressions with W=1 or sparse-style checks.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/Makefile

## Purpose
Adds the DCN1.0 display-core objects for input pixel processing, hardware-state debug dumping, and common color-management helpers to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN10 = dcn10_ipp.o dcn10_hw_sequencer_debug.o dcn10_cm_common.o`, wraps it into `AMD_DAL_DCN10` with `$(AMDDALPATH)/dc/dcn10/`, and appends to `AMD_DISPLAY_FILES`.

## Control Flow
There is no runtime flow. Build flow expands object names to source-tree paths and includes them in the aggregate AMD display object list.

## State And Persistence
No runtime state. Build state is represented by make variables.

## Dependencies And Integration Points
This file integrates the DCN10 subdirectory into the parent AMDGPU display make system. Other DCN10 files may be referenced from later-generation code, but only these three objects are compiled from this local Makefile.

## Risks
Omitting a required object from this list causes unresolved symbols or disabled functionality. Adding objects here without matching source files breaks builds. Because `dcn10_dwb.c` exists but is not listed here, its compilation is controlled elsewhere or intentionally excluded for this snapshot.

## Test Signals
Kernel/module build should show these object files compiled and linked through `AMD_DISPLAY_FILES`; missing-symbol failures around `dcn10_ipp_construct`, `dcn10_get_hw_state`, or color helper functions indicate build-list drift.

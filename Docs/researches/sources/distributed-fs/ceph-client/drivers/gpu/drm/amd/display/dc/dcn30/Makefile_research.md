# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/Makefile

## Purpose
Adds selected DCN3.0 objects to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN30 := dcn30_vpg.o dcn30_afmt.o dcn30_cm_common.o dcn30_mmhubbub.o`, wraps with `AMD_DAL_DCN30`, and appends to `AMD_DISPLAY_FILES`.

## Control Flow
Build-time object-list expansion only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrates video packet generator, audio formatter, color-management helpers, and MMHUBBUB/MCIF writeback memory client into the display build.

## Risks
The report set does not include `dcn30_vpg.c`, but the build list does; missing or stale source for that object would fail builds. Omitting `dcn30_cm_common.o` or `dcn30_mmhubbub.o` breaks symbols used by DCN3 resource code.

## Test Signals
Kernel/module build for DCN3 configs, link-time resolution of AFMT/CM/MMHUBBUB symbols, and object inclusion in `AMD_DISPLAY_FILES`.

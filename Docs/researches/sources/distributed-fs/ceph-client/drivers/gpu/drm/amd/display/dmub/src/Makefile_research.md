# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/Makefile

## Purpose

This Makefile fragment enumerates DMUB service and generation-specific source objects and appends them to the AMD display build. It is the build integration point for the DMUB service layer and hardware-family implementations.

## Important APIs, Types, And Functions

The `DMUB` variable starts with common service objects (`dmub_srv.o`, `dmub_srv_stat.o`, `dmub_reg.o`) and then appends generation objects from DCN20 through DCN42: `dmub_dcn20.o`, `dmub_dcn21.o`, `dmub_dcn30.o`, `dmub_dcn301.o`, `dmub_dcn302.o`, `dmub_dcn303.o`, `dmub_dcn31.o`, `dmub_dcn314.o`, `dmub_dcn315.o`, `dmub_dcn316.o`, `dmub_dcn32.o`, `dmub_dcn35.o`, `dmub_dcn351.o`, `dmub_dcn36.o`, `dmub_dcn401.o`, and `dmub_dcn42.o`.

`AMD_DAL_DMUB` prefixes those object names with `$(AMDDALPATH)/dmub/src/`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DMUB)` adds them to the overall display driver compilation list.

## Control Flow And Data Flow

There is no runtime control flow. Build-time flow is variable assembly: object names are collected, path-prefixed, and handed to the parent AMD display make infrastructure.

## State And Persistence Behavior

The file persists build membership only. Adding or removing a DMUB generation source changes which register tables and hardware function implementations are linked into the display driver.

## Dependencies And Integration Points

The fragment depends on parent make variables `AMDDALPATH` and `AMD_DISPLAY_FILES`. It integrates all DMUB source files with the broader AMDGPU display build. The generation objects correspond to ASIC-specific function tables selected by service creation code elsewhere.

## Risks And Edge Cases

If a new DMUB generation source is added but not listed here, it will not be compiled into the driver. If an object is listed without its source or with missing generated register headers, the AMD display build fails. Ordering is mostly not runtime-significant, but common service objects must be compiled and linked along with generation implementations.

## Test Signals

Primary signals are successful kernel/module builds, presence of the expected DMUB objects in the build log, and successful linking of symbols such as generation register tables and hardware functions. Runtime validation is indirect: ASIC-specific DMUB initialization must find the expected function implementation after build.

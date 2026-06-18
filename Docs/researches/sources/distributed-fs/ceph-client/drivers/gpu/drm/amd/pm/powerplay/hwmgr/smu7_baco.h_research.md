# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.h

## Purpose

This header declares the SMU7 BACO support, state query, and state transition functions.

## Important APIs, Types, and Functions

It exports `smu7_get_bamaco_support()`, `smu7_baco_get_state()`, and `smu7_baco_set_state()`. The state API uses `enum BACO_STATE` from `common_baco.h`.

## Control Flow and State

There is no logic or state in the header. It defines the BACO integration surface for SMU7 hwmgr code.

## Dependencies and Integration

The header includes `hwmgr.h` and `common_baco.h`, tying the API to the PowerPlay manager and shared BACO state definitions. ASIC-specific hwmgr files can include it to advertise or invoke BACO support.

## Risks and Test Signals

The API assumes callers pass valid `pp_hwmgr` and state pointers. Compile coverage verifies signatures; runtime signals are successful capability checks and BACO state transitions through the selected ASIC implementation.

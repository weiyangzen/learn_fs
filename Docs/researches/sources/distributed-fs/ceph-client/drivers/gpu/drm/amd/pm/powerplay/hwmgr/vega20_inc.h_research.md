# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_inc.h

## Purpose
`vega20_inc.h` is a thin register include aggregator for Vega20 PowerPlay code. It pulls in SOC15 offset and mask definitions for thermal (`thm_11_0_2`), MP (`mp_9_0`), and NBIO (`nbio_7_4`) blocks.

## Important APIs, Types, and Functions
The file exports no functions or types of its own. Its important API is the set of included register constants and field masks consumed by `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD` users in hwmgr and thermal code.

## Control Flow
There is no control flow. Inclusion makes register names such as thermal fan-control registers and NBIO/MP masks available to implementation files.

## State and Persistence
No state is defined. It only names hardware register addresses and bitfields through included generated headers.

## Dependencies and Integration Points
It integrates generated ASIC register headers with Vega20-specific PM files, particularly fan control, temperature reads, interrupt setup, and low-level power-management register access.

## Risks
Incorrect include selection would make the driver program the wrong SOC15 block layout. Because these are compile-time constants, errors generally surface as build failures or runtime hardware misprogramming rather than local validation failures.

## Test Signals
Build success verifies names exist. Runtime fan/thermal/PCIe register behavior on Vega20 hardware validates that the selected offset/mask headers match the ASIC revision.

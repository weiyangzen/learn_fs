# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/amd_powerplay.h

## Purpose
`amd_powerplay.h` is a lightweight umbrella header for AMD PowerPlay code. It centralizes common kernel, amdgpu, CGS, display-manager PP, and KGD PP interface includes.

## Important APIs, Types, and Functions
This header declares no new functions or data structures. Its exported surface is the transitive availability of `seq_file`, Linux integer/error types, `amd_shared.h`, `cgs_common.h`, `dm_pp_interface.h`, `kgd_pp_interface.h`, and `amdgpu.h`.

## Control Flow
There is no control flow. Including it gives implementation files access to common PowerPlay-facing interfaces and amdgpu device types.

## State and Persistence
No state is defined.

## Dependencies and Integration Points
It is used by files such as `vega20_hwmgr.c` that need broad PowerPlay and amdgpu type visibility. It sits near the top of the include graph for this legacy PM stack.

## Risks
Umbrella headers can hide true dependencies and increase compile coupling. Any change to included headers may affect many PowerPlay translation units.

## Test Signals
Compile success across PowerPlay users validates that included interface dependencies remain sufficient and non-conflicting.

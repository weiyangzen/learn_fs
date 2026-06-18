# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/Makefile

## Purpose

`rascore/Makefile` lists the generic RAS core object files and appends them to the AMDGPU RAS object list.

## Important APIs, Types, And Functions

`RAS_CORE_FILES` includes rascore modules for core lifecycle, MP1, ACA, EEPROM, UMC, command handling, GFX, process queue, NBIO, log ring, CPER, PSP, and firmware EEPROM support. `RAS_CORE` prefixes the files with `$(AMD_GPU_RAS_PATH)/rascore/`, then appends to `AMD_GPU_RAS_FILES`.

## Control Flow, State, And Persistence

There is no runtime behavior. The Makefile controls whether the generic rascore implementation is linked into AMDGPU.

## Dependencies And Integration Points

It depends on outer Kbuild variables and is included by the top-level RAS Makefile. Its object set backs the manager's `ras_core_context` lifecycle and command/ACA/UMC/EEPROM/PSP features.

## Risks And Test Signals

Risks are missing objects for declared APIs, stale file names, and accidental omission of paired versioned modules. Test signals include full build, modpost unresolved symbol checks, and feature-specific link coverage for ACA, CPER, firmware EEPROM, and UMC paths.

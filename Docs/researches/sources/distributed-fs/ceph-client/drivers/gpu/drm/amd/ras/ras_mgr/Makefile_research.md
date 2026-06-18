# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/Makefile

## Purpose

`ras_mgr/Makefile` lists the AMDGPU-facing unified RAS manager objects and appends them to the global `AMD_GPU_RAS_FILES` build list.

## Important APIs, Types, And Functions

The object list includes `amdgpu_ras_sys.o`, `amdgpu_ras_mgr.o`, `amdgpu_ras_eeprom_i2c.o`, `amdgpu_ras_mp1_v13_0.o`, `amdgpu_ras_cmd.o`, `amdgpu_virt_ras_cmd.o`, `amdgpu_ras_process.o`, and `amdgpu_ras_nbio_v7_9.o`. `RAS_MGR` prefixes those names with `$(AMD_GPU_RAS_PATH)/ras_mgr/`.

## Control Flow, State, And Persistence

There is no runtime behavior. Build state is accumulated by appending `RAS_MGR` into `AMD_GPU_RAS_FILES`, which makes the manager, virtualization bridge, system callback table, EEPROM adapter, MP1/NBIO adapters, command handlers, and event processing compile into AMDGPU.

## Dependencies And Integration Points

It depends on the top-level RAS Makefile and parent AMDGPU Kbuild variables. It integrates with `rascore` headers and objects, the AMDGPU IP block list, SR-IOV support, SMU/MP1 firmware messaging, NBIO interrupt registration, and EEPROM I2C support through the objects it selects.

## Risks And Test Signals

Risks are omitting a required object after adding a header or exported function, stale object names after file moves, and manager/core object order assumptions. Test signals include full AMDGPU build, modpost unresolved-symbol checks, and link coverage for VF and non-VF RAS paths.

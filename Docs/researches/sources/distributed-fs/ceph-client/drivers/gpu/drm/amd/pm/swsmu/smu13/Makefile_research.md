# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/Makefile

## Purpose

This Makefile fragment wires SMU13 SWSMU manager objects into the AMDGPU PowerPlay build. It includes the common SMU13 helper plus multiple ASIC-specific PPT policy implementations.

## Important APIs, Types, and Functions

`SMU13_MGR` lists `smu_v13_0.o`, `aldebaran_ppt.o`, `yellow_carp_ppt.o`, `smu_v13_0_0_ppt.o`, `smu_v13_0_4_ppt.o`, `smu_v13_0_5_ppt.o`, `smu_v13_0_7_ppt.o`, `smu_v13_0_6_ppt.o`, and `smu_v13_0_12_ppt.o`. `AMD_SWSMU_SMU13MGR` prefixes them with `$(AMD_SWSMU_PATH)/smu13/`, and `AMD_POWERPLAY_FILES` is extended with that list.

## Control Flow

There is no runtime control flow. Kbuild evaluates the variables and includes the objects in the AMDGPU powerplay link.

## State and Persistence Behavior

The Makefile has no runtime state. Its build-state effect is inclusion of SMU13 common and ASIC-specific power-management code.

## Dependencies

It depends on the parent AMDGPU Makefile defining `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`, and on the listed sources being present and buildable.

## Integration Points

The build output provides SMU13 policy entry points such as `aldebaran_set_ppt_funcs` and common SMU13 helpers to the AMDGPU driver.

## Risks and Edge Cases

Object-list drift causes missing symbols or stale policy code in AMDGPU builds. Since the list includes many ASICs unconditionally in this fragment, compile errors in one policy file can break all SWSMU SMU13 builds.

## Test Signals

Kernel build and link coverage for AMDGPU with SWSMU enabled validates the fragment. Missing callback symbols or unreferenced object changes point to Makefile integration issues.

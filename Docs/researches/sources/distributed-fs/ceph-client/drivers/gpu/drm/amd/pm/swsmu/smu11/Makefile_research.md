<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/Makefile

## Purpose

`smu11/Makefile` wires SMU11 platform manager objects into the AMDGPU powerplay build. It names the SMU11 PPT implementations and common SMU11 implementation object, prefixes them with `$(AMD_SWSMU_PATH)/smu11/`, and appends the result to `AMD_POWERPLAY_FILES`.

## Important APIs, Types, and Functions

The file defines `SMU11_MGR` with `arcturus_ppt.o`, `navi10_ppt.o`, `sienna_cichlid_ppt.o`, `vangogh_ppt.o`, `cyan_skillfish_ppt.o`, and `smu_v11_0.o`; defines `AMD_SWSMU_SMU11MGR` via `$(addprefix ...)`; and appends to `AMD_POWERPLAY_FILES`.

## Control Flow

Build-system flow is linear: Kbuild includes this makefile, expands the object list, prefixes paths, and links the selected objects into the AMDGPU driver according to the surrounding build configuration.

## State and Persistence Behavior

There is no runtime state. The persistent effect is build composition: removing an object drops that platform's PPT function installer/common implementation from the driver image.

## Dependencies

It depends on the parent AMDGPU makefiles defining `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`. The listed object names must correspond to C files in the same directory.

## Integration Points

This is the build integration point for all SMU11 platform files, including the Arcturus and Cyan Skillfish sources in this work item. Higher-level AMDGPU build rules consume `AMD_POWERPLAY_FILES`.

## Risks and Edge Cases

A missing object breaks platform support at link or runtime dispatch time. Adding a new SMU11 platform requires updating this list. Renames must keep path prefixing consistent with `AMD_SWSMU_PATH`.

## Test Signals

Kernel build of AMDGPU with powerplay enabled, link success, and boot probing on SMU11 ASICs confirm the makefile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/Makefile -->

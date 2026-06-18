# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/Makefile

## Purpose
The PM `Makefile` wires AMDGPU power-management sources into the kernel build. It establishes include search paths for common AMD headers, SMU firmware interfaces, SW SMU generations, PowerPlay managers, and legacy DPM code, then includes the sub-Makefiles for the PM libraries and adds the top-level PM manager objects to `AMD_POWERPLAY_FILES`.

## Important Build Variables
`subdir-ccflags-y` appends include directories rooted at `$(FULL_AMD_PATH)`, covering `include/asic_reg`, `include`, `pm/inc`, `pm/swsmu`, `pm/swsmu/inc`, `pm/swsmu/inc/pmfw_if`, SMU generation folders `smu11` through `smu15`, PowerPlay include/SMU/HW manager folders, and `pm/legacy-dpm`. `AMD_PM_PATH` is `../pm`. `PM_LIBS` is `swsmu powerplay legacy-dpm`. `AMD_PM` expands those library paths to included Makefiles. `PM_MGR` lists `amdgpu_dpm.o`, `amdgpu_pm.o`, and `amdgpu_dpm_internal.o`, and `AMD_PM_POWER` prefixes them with `$(AMD_PM_PATH)`.

## Control Flow and State
Build control flow is declarative: include flags are accumulated, subordinate Makefiles are included through `include $(AMD_PM)`, and object names are appended to `AMD_POWERPLAY_FILES`. Persistent state is the Kbuild variable graph; no runtime state is created.

## Dependencies and Integration Points
This file depends on the parent AMDGPU build defining `FULL_AMD_PATH` and consuming `AMD_POWERPLAY_FILES`. It integrates the SW SMU, PowerPlay, and legacy DPM subtrees into a single power-management build surface. Source files in this directory rely on the include flags to find `hwmgr.h`, `amdgpu_smu.h`, PM firmware interfaces, and ASIC register headers.

## Risks
Include path ordering can affect which generation-specific headers are found. Adding a new SMU generation or PM subtree requires updating these flags and `PM_LIBS` consistently. Removing legacy paths can break older ASIC support. Because the file includes nested Makefiles, missing or misspelled paths can fail builds far from the edit location.

## Test Signals
The direct signal is a successful kernel or module build with AMDGPU PM enabled across configurations that include SW SMU, PowerPlay, and legacy DPM. Incremental build tests should verify that `amdgpu_dpm.o`, `amdgpu_pm.o`, and `amdgpu_dpm_internal.o` are included exactly once. Cross-ASIC build coverage is important because different PM subtrees consume different include directories.

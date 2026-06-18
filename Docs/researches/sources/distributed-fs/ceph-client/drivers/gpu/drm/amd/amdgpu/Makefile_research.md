# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/Makefile

Purpose: composes the large `amdgpu.o` DRM driver from core KMS, memory-management, ASIC, display, media, power, reset, RAS, compute, ACP, ISP, and compatibility objects.

Important APIs/types/functions: sets AMD include paths, `GCOV_PROFILE`, local warning suppressions, optional `-Werror`, and appends hundreds of objects to `amdgpu-y`, including core amdgpu files, ASIC families, DF/GMC/UMC/IH/PSP/DCE/GFX/SDMA/MES/UVD/VCE/VCN/JPEG/VPE/UMSCH/ATHUB/SMUIO/reset/MCA/KFD bridge objects, CGS, scheduler jobs, optional ACP/ISP, compat, ACPI, HMM, powerplay, display core, and RAS.

Control flow: Kbuild conditionally includes older SI/CIK objects, KFD files via the amdkfd Makefile, ACP via `AMDACPPATH` and the ACP Makefile, DC display via the display Makefile, and RAS/powerplay file lists. `obj-$(CONFIG_DRM_AMDGPU) += amdgpu.o` emits the module or built-in object.

State/persistence: build-time variable state only; runtime state is in the compiled subsystems.

Dependencies/integration: integrates AMD shared headers, ASIC register headers, power management, display core, KFD, RAS, ACP, ISP, DRM helpers, TTM, HMM, ACPI, and compat ioctl support.

Risks: object ordering, include path order, and conditional file-list includes are fragile; missing objects may fail only for narrow ASIC/config combinations. GCOV and Werror significantly alter build behavior.

Test signals: allmodconfig, amdgpu built-in/module, SI/CIK toggles, KFD/DC/ACP/ISP enabled and disabled, ACPI/compat/HMM configs, RAS/powerplay linkage, GCOV, Werror, and representative ASIC boot smoke tests.

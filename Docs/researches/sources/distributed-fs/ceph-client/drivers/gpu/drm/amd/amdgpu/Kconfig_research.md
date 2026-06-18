# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/Kconfig

Purpose: defines the AMDGPU DRM driver and feature switches for older ASIC support, userptr/HMM behavior, AMD ISP support, warning policy, GCOV profiling, ACP, display, and KFD configuration.

Important APIs/types/functions: key symbols are `DRM_AMDGPU`, `DRM_AMDGPU_SI`, `DRM_AMDGPU_CIK`, `DRM_AMDGPU_USERPTR`, `DRM_AMD_ISP`, `DRM_AMDGPU_WERROR`, and `GCOV_PROFILE_AMDGPU`. `DRM_AMDGPU` selects firmware loading, DRM helpers, scheduler, TTM, power/hwmon/I2C/backlight support, interval trees, DRM buddy, suballocator, exec helper, panel quirks, and ACPI video/input dependencies.

Control flow: selecting `DRM_AMDGPU` exposes the PCI AMD GPU driver. SI/CIK toggles control older GCN families that overlap with radeon. Userptr selects HMM/MMU notifier support. Sourced Kconfigs expose ACP, display, and KFD options.

State/persistence: config choices persist in `.config`.

Dependencies/integration: integrates amdgpu with PCI, DRM core/helpers, TTM, scheduler, GPU buddy, ACPI, HMM, AMD display, KFD, ACP, and ISP support.

Risks: SI/CIK ownership is shared with radeon and depends on module parameters; broad selects can force dependencies unexpectedly; GCOV and Werror change build size and failure behavior.

Test signals: amdgpu built-in/module, SI/CIK combinations, userptr/HMM, ACPI/non-ACPI, ISP/ACP toggles, GCOV, Werror, and radeon coexistence configs.

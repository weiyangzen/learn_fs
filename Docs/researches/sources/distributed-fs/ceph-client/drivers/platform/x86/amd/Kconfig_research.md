# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/Kconfig

Purpose: this Kconfig file is the top-level AMD platform-x86 menu. It includes HSMP, PMF, PMC, and HFI submenus and defines build options for 3D V-Cache optimization, WBRF, and the AMD ISP4 platform driver.

Important APIs, types, and functions: there are no C APIs, but key symbols are `AMD_3D_VCACHE`, `AMD_WBRF`, and `AMD_ISP_PLATFORM`. The file also sources `amd/hsmp/Kconfig`, `amd/pmf/Kconfig`, `amd/pmc/Kconfig`, and `amd/hfi/Kconfig`.

Control flow: kernel configuration flows from this file into subdirectory-specific symbols. `AMD_3D_VCACHE` depends on `X86_64 && ACPI`; `AMD_WBRF` depends on ACPI; `AMD_ISP_PLATFORM` depends on I2C, x86_64, and ACPI.

State and persistence: configuration choices persist in the kernel `.config`; no runtime state exists here.

Dependencies and integration points: the symbols map directly to object inclusion in the sibling `Makefile`. Help text documents module names and user-facing scope, including `amd_isp4` as the ISP4 module.

Risks: dependency mistakes can expose drivers on unsupported architectures or omit required subsystem dependencies. Because sourced submenus are unconditional in this file, their own dependencies must protect unsupported builds.

Test signals: `make menuconfig` visibility, generated `.config` symbol values, and object inclusion in `drivers/platform/x86/amd/Makefile` are the main validation signals.

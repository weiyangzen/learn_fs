# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/Kconfig

Purpose: this Kconfig file defines AMD Host System Management Port support, split into shared common code plus ACPI and legacy platform front ends.

Important APIs, types, and functions: `AMD_HSMP` is a hidden tristate selected by `AMD_HSMP_ACPI` or `AMD_HSMP_PLAT`. `AMD_HSMP_ACPI` depends on ACPI and optionally hwmon. `AMD_HSMP_PLAT` is the platform-device probing path for systems without the ACPI object.

Control flow: selecting either front end selects the common HSMP core. The menu is visible only when `AMD_NODE` or `COMPILE_TEST` is set.

State and persistence: only kernel configuration state exists.

Dependencies and integration points: HSMP relies on AMD node/SMN support, optional hwmon, ACPI for modern probing, and platform-device probing for older systems. Help text documents user-space monitoring and management use on EPYC and MI300A server CPUs.

Risks: enabling both ACPI and platform paths requires runtime code to avoid duplicate binding. Optional hwmon support must compile both with and without `CONFIG_HWMON`.

Test signals: config combinations for ACPI-only, platform-only, both, and no hwmon; module names `hsmp_acpi` and `amd_hsmp`; and common object selection through `AMD_HSMP`.

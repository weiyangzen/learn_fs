# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/Makefile

Purpose: this Makefile builds the HSMP common layer and its ACPI/platform front ends.

Important APIs, types, and functions: `hsmp_common.o` is built from `hsmp.o` and optionally `hwmon.o`. `amd_hsmp.o` is built from `plat.o`; `hsmp_acpi.o` is built from `acpi.o`.

Control flow: kbuild includes common code when `CONFIG_AMD_HSMP` is selected, the platform front end for `CONFIG_AMD_HSMP_PLAT`, and the ACPI front end for `CONFIG_AMD_HSMP_ACPI`.

State and persistence: build-only state.

Dependencies and integration points: object names match exported namespace use in front ends and optional hwmon integration.

Risks: omitting `hsmp_common` would break symbol imports for front ends. Optional hwmon inclusion must stay aligned with the inline fallback in `hsmp.h`.

Test signals: compile/link for all three config combinations and namespace import/export resolution for `AMD_HSMP`.

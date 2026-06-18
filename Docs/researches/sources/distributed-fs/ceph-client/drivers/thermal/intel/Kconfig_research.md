# sources/distributed-fs/ceph-client/drivers/thermal/intel/Kconfig

## Purpose
Top-level Kconfig entries for Intel thermal drivers. It defines Intel x86 thermal feature symbols, includes the INT340x ACPI submenu, and describes dependencies for package DTS, SoC DTS, Quark DTS, PMIC, PCH, TCC cooling, PowerClamp, and HFI thermal support.

## Important APIs, Types, and Functions
No runtime APIs. Key symbols include `INTEL_POWERCLAMP`, `X86_THERMAL_VECTOR`, `INTEL_TCC`, `X86_PKG_TEMP_THERMAL`, `INTEL_SOC_DTS_IOSF_CORE`, `INTEL_SOC_DTS_THERMAL`, `INTEL_QUARK_DTS_THERMAL`, `INTEL_BXT_PMIC_THERMAL`, `INTEL_PCH_THERMAL`, `INTEL_TCC_COOLING`, and `INTEL_HFI_THERMAL`.

## Control Flow
Kconfig dependency resolution selects helper libraries and exposes user-selectable drivers. The file enters an `ACPI INT340X thermal drivers` menu and sources `drivers/thermal/intel/int340x_thermal/Kconfig`.

## State and Persistence
No runtime state. Symbol selections persist in kernel config.

## Dependencies and Integration Points
Integrates with x86 CPU vendor support, local APIC thermal vectors, PCI, ACPI, NET/THERMAL_NETLINK, IOSF, powercap/RAPL, ACPI thermal libraries, and Intel TCC helper code.

## Risks and Edge Cases
Wrong dependencies can expose drivers on platforms without required firmware interfaces. Several symbols select helper subsystems, so dependency changes affect build footprint.

## Test Signals
Kconfig/build testing should cover x86 and COMPILE_TEST-style matrices where applicable, allmodconfig, module/built-in combinations, and submenu symbol propagation to Makefile targets.

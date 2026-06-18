## sources/distributed-fs/ceph-client/drivers/acpi/processor_perflib.c

### Purpose
`processor_perflib.c` implements ACPI processor performance-state support for x86. It parses `_PCT`, `_PSS`, `_PPC`, and `_PSD`, coordinates shared P-state domains, and exposes registration hooks used by cpufreq drivers.

### Important APIs, Types, And Functions
Exports include `acpi_processor_get_performance_info()`, `acpi_processor_get_bios_limit()`, `acpi_processor_notify_smm()`, `acpi_processor_get_psd()`, `acpi_processor_preregister_performance()`, `acpi_processor_register_performance()`, and `acpi_processor_unregister_performance()`. `_PPC` integration is handled by `acpi_processor_ppc_init()`, `acpi_processor_ppc_exit()`, and `acpi_processor_ppc_has_changed()`.

### Control Flow
Cpufreq policy creation adds per-processor max-frequency QoS requests and evaluates `_PPC` if enabled. Performance registration assigns a caller-provided `struct acpi_processor_performance`, parses `_PCT` control/status registers, extracts `_PSS` state packages, applies AMD frequency fixups for older families, validates frequency values, and updates the platform limit. Preregistration parses `_PSD` for all processors, validates domain membership and coordination type, builds shared CPU maps, then clears temporary `pr->performance` assignments until real registration. SMM notification writes FADT `pstate_control` to `smi_command` once and pins the caller module if `_PPC` is in use.

### State, Persistence, And Dependencies
State lives in per-processor performance structures, `performance_platform_limit`, per-CPU cpufreq QoS requests, `ignore_ppc`, `acpi_processor_ppc_in_use`, and the `performance_mutex`. Dependencies include ACPICA package extraction, cpufreq policy constraints, x86 CPUID/MSR helpers, FADT SMI control, and ACPI `_OST`.

### Integration Points
`processor_driver.c` invokes `_PPC` updates on ACPI notify and hooks policy create/remove. cpufreq drivers call the exported register and preregister functions to consume ACPI P-state data and shared-domain maps.

### Risks
Firmware package validation is strict but still accepts adjusted lists after invalid frequency entries. `_PPC` is ignored until cpufreq initialization unless overridden. Module reference handling in `acpi_processor_notify_smm()` intentionally prevents unloading in `_PPC` cases. Shared-domain errors degrade all CPUs to no coordination. x86-only code is conditionally compiled.

### Test Signals
Cover valid and malformed `_PCT`, `_PSS`, `_PPC`, and `_PSD`, invalid or overflowing frequencies, AMD fixup cases, cpufreq policy create/remove, `_PPC` notify with `_OST`, shared-domain mismatches, FADT SMI success/failure, and `ignore_ppc` settings.

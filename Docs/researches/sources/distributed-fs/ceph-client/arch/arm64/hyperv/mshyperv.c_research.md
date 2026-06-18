## sources/distributed-fs/ceph-client/arch/arm64/hyperv/mshyperv.c

### Purpose
Detects Hyper-V on ARM64, initializes common Hyper-V guest state, publishes feature flags, and tracks initialization completion.

### Important APIs, Types, And Functions
Exports `hv_get_hypervisor_version` and `hv_is_hyperv_initialized`. Internal functions are `hyperv_detect_via_acpi`, `hyperv_detect_via_smccc`, and `hyperv_init`. File-local state is `hyperv_initialized`.

### Control Flow
Early init first detects Hyper-V via ACPI FADT hypervisor ID or SMCCC UUID. If not detected, it returns success without initialization. On Hyper-V, it sets the guest OS ID, reads privilege/features/hints VP registers, identifies partition type, runs `hv_common_init()`, installs CPU hotplug callbacks, optionally reads partition ID and VTL, runs late init, then marks initialization complete.

### State, Persistence, And Dependencies
Persistent kernel state includes `ms_hyperv` feature fields, common Hyper-V allocations, CPU hotplug state, partition ID/VTL, and `hyperv_initialized`. Dependencies include ACPI, SMCCC hypervisor UUID support, Linux version code, cpuhotplug, and common Hyper-V functions declared in `asm/mshyperv.h`.

### Integration Points
Runs as `early_initcall`, preparing Hyper-V services before dependent drivers initialize. It integrates ARM64 detection with generic Hyper-V guest infrastructure.

### Risks
Detection must avoid false positives on non-Hyper-V ACPI systems. Failure cleanup after CPU hotplug setup must free common resources. Feature field interpretation depends on `hv_core.c` VP register reads.

### Test Signals
Boot with and without Hyper-V, with ACPI enabled/disabled, validate SMCCC UUID detection, exercise CPU hotplug online/offline callbacks, inspect `ms_hyperv` feature logs, and verify `hv_is_hyperv_initialized()` behavior.

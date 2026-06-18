<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/platform.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/platform.c

### Purpose
`platform.c` provides LoongArch platform wake setup, cpufreq platform-device registration, and ACPI S3 suspend target discovery.

### Important APIs, Types, And Functions
Functions are `enable_gpe_wakeup()`, `enable_pci_wakeup()`, `loongson_cpufreq_init()`, `default_suspend_addr()`, and `loongson3_acpi_suspend_init()`. Static state includes `loongson3_cpufreq_device`.

### Control Flow
Wake helpers return early if ACPI is disabled or reduced-hardware mode is active. GPE wake enables all wake GPEs; PCI wake clears wake status and enables PCIe wake if the FADT advertises it. Cpufreq registration runs at arch init only if `cpu_has_scalefreq`. ACPI S3 init enables SCI, checks S3 support, evaluates `\SADR`, and stores either a default ACPI sleep function or the physical-to-virtual SADR target in `loongson_sysconf.suspend_addr`.

### State, Persistence, And Dependencies
State includes ACPI wake registers, registered platform device, and `loongson_sysconf.suspend_addr`. Dependencies include ACPI core, Loongson system config, boot CPU feature flags, and platform-device APIs.

### Integration Points
Suspend and hibernate call wake helpers. `suspend_asm.S` calls the firmware suspend address prepared here. Cpufreq driver probing depends on the platform device.

### Risks
ACPI reduced-hardware handling must avoid unsupported register accesses. A bad `\SADR` conversion sends suspend assembly to the wrong firmware entry. Wake bits must be set before entering S3/hibernate.

### Test Signals
Boot ACPI systems with/without S3, inspect `\SADR`, test suspend wake from GPE/PCIe, and validate cpufreq device registration on scalable-frequency CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/platform.c -->

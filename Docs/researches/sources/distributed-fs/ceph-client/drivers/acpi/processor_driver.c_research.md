## sources/distributed-fs/ceph-client/drivers/acpi/processor_driver.c

### Purpose
`processor_driver.c` is the ACPI processor driver module entry point. It registers the CPU-subsystem driver, wires ACPI processor notifications into cpufreq, cpuidle, throttling, and thermal subsystems, and manages CPU hotplug callbacks.

### Important APIs, Types, And Functions
The file defines `acpi_processor_driver`, `processor_device_ids`, `acpi_processor_notify()`, `__acpi_processor_start()`, `acpi_processor_stop()`, `acpi_soft_cpu_online()`, `acpi_soft_cpu_dead()`, and module init/exit routines. It exports the global state `acpi_processor_cpufreq_init` and weak `acpi_processor_init_invariance_cppc()`.

### Control Flow
Module init registers a cpufreq policy notifier, registers the ACPI idle driver, registers the CPU bus driver, installs CPU hotplug states, initializes throttling coordination, initializes CPPC frequency invariance, and rescans dead SMT siblings. Starting a processor probes CPPC, initializes idle power handling, initializes P-state/throttling data when `_PSS` support is configured, registers a thermal cooling device, and installs an ACPI notify handler. Notifications dispatch `_PPC`, C-state, T-state, and highest-performance-change events to the relevant subsystem and generate netlink events. Stop/remove unwinds notify, idle, CPPC, and thermal state.

### State, Persistence, And Dependencies
State is per-processor in `struct acpi_processor`, per-CPU `processors`, cpuhp state IDs, registered notifier blocks, and the `previously_online` and `acpi_processor_cpufreq_init` flags. Dependencies include CPU hotplug, cpufreq, cpuidle, ACPI scan/device APIs, CPPC, thermal cooling, and the ACPI processor internal interfaces.

### Integration Points
This file is the coordinator for `processor_idle.c`, `processor_perflib.c`, `processor_throttling.c`, and `processor_thermal.c`. It also provides ACPI event delivery to userspace through `acpi_bus_generate_netlink_event()`.

### Risks
Initialization ordering matters: thermal setup is unwound through power exit, cpufreq notifier registration controls whether `_PPC` is honored, and first physical hotplug differs from later soft online events. Notify handlers must tolerate stale or missing driver data. Exit removes dynamic cpuhp state and notifier state but only when ACPI is enabled.

### Test Signals
Test CPU online/offline cycles, first hotplug of a previously unseen CPU, module load with ACPI disabled, ACPI notifications `0x80`, `0x81`, `0x82`, and `0x85`, cpufreq policy create/remove, and failure paths in thermal registration or notify-handler installation.

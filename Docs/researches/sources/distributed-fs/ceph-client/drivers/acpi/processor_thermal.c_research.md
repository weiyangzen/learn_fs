## sources/distributed-fs/ceph-client/drivers/acpi/processor_thermal.c

### Purpose
`processor_thermal.c` exposes each ACPI processor as a thermal cooling device. It maps cooling states first to cpufreq max-frequency QoS reductions and then, if needed, to ACPI T-state throttling.

### Important APIs, Types, And Functions
Public hooks are `acpi_processor_thermal_init()`, `acpi_processor_thermal_exit()`, `acpi_thermal_cpufreq_init()`, and `acpi_thermal_cpufreq_exit()`. Cooling callbacks are collected in `processor_cooling_ops`, backed by `processor_get_max_state()`, `processor_get_cur_state()`, and `processor_set_cur_state()`.

### Control Flow
Thermal init registers a `Processor` cooling device and creates reciprocal sysfs links between the ACPI device and cooling device. Cpufreq policy init adds per-CPU max-frequency QoS requests and updates the cooling device. Setting a cooling state uses cpufreq reduction steps up to `cpufreq_thermal_max_step`; higher states clamp cpufreq at the maximum reduction and request ACPI throttling for the remaining state. Reductions are package-wide using the first online CPU in the physical package as storage.

### State, Persistence, And Dependencies
State includes per-package emulated `cpufreq_thermal_reduction_step`, global reduction parameters, per-processor `thermal_req` QoS requests, and `pr->cdev`. Dependencies include cpufreq, thermal cooling devices, CPU topology, ACPI processor throttling, sysfs, and architecture-provided thermal reduction percentage.

### Integration Points
The processor driver calls thermal init/exit during processor start/stop. Cpufreq policy notifier callbacks in `processor_driver.c` call the cpufreq init/exit helpers. Thermal governors drive the cooling-device callbacks.

### Risks
Package state is emulated with per-CPU storage and can be lost temporarily across hot-unplug. The code assumes `per_cpu(processors, i)` exists for online package CPUs before touching QoS state. Frequency reduction parameters must avoid reducing performance to zero. Sysfs link creation has two-step unwind requirements.

### Test Signals
Test with and without `CONFIG_CPU_FREQ`, policy create/remove, package-level multi-CPU policies, cooling states that stay within cpufreq and cross into T-states, hotplug during thermal state changes, sysfs link failure injection, and architecture-specific reduction percentages.

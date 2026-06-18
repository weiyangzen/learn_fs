# sources/distributed-fs/ceph-client/include/acpi/cppc_acpi.h

Purpose: Declares Linux CPPC library data structures and APIs used by CPU frequency and scheduler-performance code to read and program ACPI Collaborative Processor Performance Control registers.

Important APIs, types, and functions: Defines CPPC revision/count constants, PCC masks and commands, register indexes `enum cppc_regs`, packed `struct cpc_reg`, `struct cpc_register_resource`, `struct cpc_desc`, capability/control/feedback structs, and per-CPU `struct cppc_cpudata`. When `CONFIG_ACPI_CPPC_LIB` is enabled it declares getters/setters for performance caps, counters, desired/min/max/energy performance, EPP, auto-selection/action-window, perf-limited bits, FFH read/write, PSD mapping, fast-switch capability, and AMD preferred-core helpers; otherwise it returns `-EOPNOTSUPP`, `-ENODEV`, or false stubs.

Control flow: Consumers probe `_CPC`, classify each register as integer, system-memory, PCC, or FFH, then use the declared APIs to read feedback counters or write controls. PCC operations use command/status masks; FFH operations are delegated to arch support.

State and persistence: Per-CPU CPPC descriptors cache register resources, virtual mappings, PSD domains, and kobjects. Actual performance controls are hardware/firmware state exposed through ACPI registers and PCC shared memory.

Dependencies and integration points: Depends on Linux ACPI, cpufreq, CPPC/PCC, processor PSD structures, raw spinlocks, kobjects, cpumasks, and AMD-specific performance discovery. Integrates with `acpi-cpufreq`, `amd-pstate`, scheduler frequency invariance, thermal frequency limits, and platform firmware.

Risks and test signals: Risks include wrong register index ordering, unsafe RMW locking, PCC timeout/status handling, disabled-config callers, frequency/performance conversion errors, and AMD preferred-core misdetection. Test `_CPC` parsing, PCC and FFH register paths, concurrent cpufreq writes, EPP/autonomous mode toggles, suspend/resume, hotplug, and no-CPPC builds.

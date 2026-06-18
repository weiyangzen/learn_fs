# sources/distributed-fs/ceph-client/include/acpi/processor.h

Purpose: Defines ACPI processor driver data structures and APIs for CPU enumeration, idle states, performance states, throttling, thermal limits, CPPC probing, and CPU frequency/thermal integration.

Important APIs, types, and functions: Exports HIDs, power/performance/throttling constants, domain coordination constants, register structs for C/P/T state controls, `struct acpi_processor_cx`, `struct acpi_lpi_state`, `struct acpi_processor_power`, `struct acpi_psd_package`, `struct acpi_processor_px`, `struct acpi_processor_performance`, `struct acpi_tsd_package`, `struct acpi_processor_throttling`, `struct acpi_processor_limit`, `struct acpi_processor_flags`, and `struct acpi_processor`. Declares performance registration, `_PSD` parsing, SMM notification, P-state/CPPC/idle/throttling/thermal hooks, CPU id mapping helpers, per-CPU `processors`, and `call_on_cpu()`.

Control flow: Processor discovery maps ACPI ids to logical CPUs, parses `_CST`/LPI, `_PSS`/`_PCT`/`_PSD`, `_TSS`/`_PTC`/`_TSD`, and installs idle/cpufreq/thermal hooks depending on Kconfig. `call_on_cpu()` runs directly when already on the target CPU or dispatches through `work_on_cpu()`. Disabled configs return no-op or error stubs.

State and persistence: `struct acpi_processor` stores per-processor runtime state: ACPI handle, ids, power states, performance and throttling domains, limits, thermal cooling device, device pointer, and frequency QoS requests. Firmware ACPI methods and tables are the persistent source of capabilities.

Dependencies and integration points: Depends on CPU hotplug, cpufreq, PM QoS, scheduler, SMP, thermal framework, workqueues, asm ACPI id mapping, CPPC, and architecture FFH idle support. Integrates with ACPI processor core, idle driver, cpufreq perflib, thermal cooling, and CPU invariance.

Risks and test signals: Risks include bad CPU id mapping, domain coordination errors, unsafe CPU-affine execution, stale hotplug state, incorrect disabled-config behavior, and thermal/performance limit conflicts. Test CPU hotplug, `_PPC` notifications, C/P/T-state parsing, CPPC probe/exit, FFH idle entry, thermal throttling, no-cpufreq/no-idle builds, and suspend/resume.

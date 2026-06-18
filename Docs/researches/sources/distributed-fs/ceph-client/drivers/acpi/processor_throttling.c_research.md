## sources/distributed-fs/ceph-client/drivers/acpi/processor_throttling.c

### Purpose
`processor_throttling.c` implements ACPI processor T-state throttling. It supports modern `_PTC`/`_TSS`/`_TPC`/`_TSD` control and legacy FADT P_BLK duty-cycle throttling.

### Important APIs, Types, And Functions
Public functions are `acpi_processor_throttling_init()`, `acpi_processor_get_throttling_info()`, `acpi_processor_set_throttling()`, `acpi_processor_tstate_has_changed()`, and `acpi_processor_reevaluate_tstate()`. Internals parse `_PTC`, `_TSS`, `_TSD`, and `_TPC`, compute FADT states, read/write status and control registers, and coordinate domain-wide changes through `__acpi_processor_set_throttling()`.

### Control Flow
Discovery first attempts modern ACPI throttling packages; if any required modern method is missing or invalid, it falls back to FADT duty-cycle data. `_TSD` domain data is parsed per CPU and later reconciled globally by `acpi_processor_throttling_init()`. Setting a T-state clamps the requested state against thermal, user, and `_TPC` platform limits through a prechange notifier, runs control on the target CPU with `call_on_cpu()`, optionally updates every CPU in shared SW_ALL/HW_ALL domains, then posts final state updates. `_TPC` notifications force current states down or up to the new platform limit.

### State, Persistence, And Dependencies
State resides in `struct acpi_processor_throttling`, per-processor limit fields, shared CPU maps, `ignore_tpc`, and legacy I/O regions. Dependencies include ACPI package extraction, cpumasks, CPU online masks, x86 MSR helpers for fixed hardware throttling, FADT, and cpufreq/thermal limit integration.

### Integration Points
`processor_driver.c` initializes coordination and calls T-state reevaluation on CPU online/dead transitions and ACPI throttling notifications. `processor_thermal.c` calls `acpi_processor_set_throttling()` for cooling states beyond cpufreq reduction.

### Risks
Modern method parsing is all-or-fallback, so partial firmware support becomes legacy throttling if possible. Shared-domain transitions call target functions with CPU affinity and must handle offline CPUs. The FADT path writes raw I/O ports with interrupts disabled. `_TPC` can be disabled with `ignore_tpc`. In `acpi_get_throttling_value()`, the bounds check allows `state == state_count`, which would be out of range if reached; callers otherwise validate `state <= state_count - 1`.

### Test Signals
Cover modern and FADT throttling, malformed `_PTC` bit widths, `_TSS` zero percentages, invalid `_TSD` domains, `_TPC` notifications and ignored mode, CPU online/offline reevaluation, SW_ANY versus SW_ALL/HW_ALL coordination, thermal-driven throttling, and fixed-hardware MSR failures.

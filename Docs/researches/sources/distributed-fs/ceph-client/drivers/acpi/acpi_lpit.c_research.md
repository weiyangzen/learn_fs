# sources/distributed-fs/ceph-client/drivers/acpi/acpi_lpit.c

## Purpose
`acpi_lpit.c` parses the Low Power Idle Table and exposes low-power idle residency counters through CPU sysfs attributes.

## Important APIs, Types, And Functions
The central type is `struct lpit_residency_info`, with ACPI generic address, frequency, and optional mapped MMIO address. File state is split between `residency_info_mem` and `residency_info_ffh`. Important functions are `lpit_read_residency_counter_us()`, sysfs show functions for system and CPU residency, exported `lpit_read_residency_count_address()`, `lpit_update_residency()`, `lpit_process()`, and `acpi_init_lpit()`.

## Control Flow
`acpi_init_lpit()` obtains the LPIT table and passes its body to `lpit_process()`. The processor scans native LPIT entries with type and flags zero. The first system-memory residency counter is ioremapped and exposed as `cpuidle/low_power_idle_system_residency_us`; the first fixed-hardware counter is exposed as `cpuidle/low_power_idle_cpu_residency_us`. Sysfs reads fetch either MMIO or MSR/FFH counter values, apply bit masks/offsets for FFH, and convert ticks to microseconds using the table frequency or TSC-derived fallback.

## State And Persistence
The selected counter descriptors and MMIO mapping persist after ACPI initialization. Sysfs attributes are added under the CPU subsystem root's `cpuidle` group. No teardown is present.

## Dependencies And Integration Points
It depends on ACPI LPIT structures, CPU subsystem sysfs, `ioremap`, ACPI OS MMIO reads, x86 MSR reads, TSC frequency, and cpuidle attribute grouping. `lpit_read_residency_count_address()` exports the system-memory counter address to other kernel code.

## Risks
The LPIT entry loop increments by firmware-provided `header.length` without an explicit zero-length guard, so malformed tables could hang. The MMIO mapping length is `bit_width / 8`, which assumes byte-aligned widths. Missing cpuidle sysfs group is silently ignored. No unmap/removal path exists for the ioremapped counter.

## Test Signals
Tests should include absent LPIT, memory and FFH counters, zero frequency fallback, sysfs reads, exported address read, malformed entry lengths, unsupported address spaces, and systems without a CPU root device.

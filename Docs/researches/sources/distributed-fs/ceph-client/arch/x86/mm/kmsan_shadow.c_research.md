# sources/distributed-fs/ceph-client/arch/x86/mm/kmsan_shadow.c

## Purpose
This small file provides x86-specific KMSAN metadata storage for the CPU entry area, which lacks normal `struct page` backing.

## Important APIs, Types, and Functions
- `DEFINE_PER_CPU(char[CPU_ENTRY_AREA_SIZE], cpu_entry_area_shadow)` allocates per-CPU KMSAN shadow bytes for CPU entry area addresses.
- `DEFINE_PER_CPU(char[CPU_ENTRY_AREA_SIZE], cpu_entry_area_origin)` allocates per-CPU KMSAN origin bytes for the same region.

## Control Flow and State
There is no executable control flow in this file. It defines persistent per-CPU arrays. KMSAN's architecture helpers map addresses in each CPU's entry area to these arrays when normal page-backed metadata lookup cannot apply.

## Dependencies and Integration Points
The file depends on `asm/cpu_entry_area.h` for `CPU_ENTRY_AREA_SIZE` and on percpu definitions. It integrates with `arch_kmsan_get_meta_or_null()` declared elsewhere and with exception/entry-stack instrumentation.

## Risks
The arrays must stay exactly sized to the CPU entry area. If CPU entry area layout changes without matching metadata mapping logic, KMSAN can miss uninitialized accesses or compute invalid metadata addresses.

## Test Signals
KMSAN-enabled boot should handle exceptions, entry stacks, and CPU entry area accesses without metadata faults. Instrumentation tests that exercise interrupts, exceptions, and context switches are relevant.

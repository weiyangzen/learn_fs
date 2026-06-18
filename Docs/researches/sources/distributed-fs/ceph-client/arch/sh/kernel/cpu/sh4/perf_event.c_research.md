# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/perf_event.c

## Purpose
`perf_event.c` registers SH7750-style hardware performance counters with the generic SH perf infrastructure.

## Important APIs, Types, And Functions
It defines PMCR/PMCTR register macros, event maps `sh7750_general_events` and `sh7750_cache_events`, callbacks `sh7750_event_map()`, `sh7750_pmu_read()`, `sh7750_pmu_disable()`, `sh7750_pmu_enable()`, `*_all()`, `sh7750_pmu`, and `sh7750_pmu_init()`.

## Control Flow
At `early_initcall`, the file checks `boot_cpu_data.flags & CPU_HAS_PERF_COUNTER`. If present, it registers a two-counter `sh_pmu`. Perf core maps generic or cache events to PMCR PMM values, enables counters by clearing and programming PMCR, and reads a 48-bit count from high/low registers.

## State And Persistence
Hardware PMCR/PMCTR registers hold counter state. Software state is the static `sh_pmu` descriptor.

## Dependencies And Integration Points
It depends on `linux/perf_event.h`, raw MMIO, SH CPU feature probing, and `register_sh_pmu()`. The SH4 Makefile selects it for SH7750/SH7750S/SH7091 under perf events.

## Risks
Unsupported events use `-1` while zero-valued cache slots may mean unsupported or no event depending on core interpretation. Counter width composition and clear-on-enable behavior can affect sampling accuracy.

## Test Signals
`perf stat` for cycles/instructions/cache events, unsupported-event rejection, counter overflow behavior, and boot notice when counters are absent validate integration.

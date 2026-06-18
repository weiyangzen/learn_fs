<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_server.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_server.h

## Purpose
This header defines classic/server POWER PMU registration data, MMCR programming state, constraint semantics, BHRB support, and sysfs event attribute helpers.

## Important APIs, Types, And Functions
It defines `MAX_HWEVENTS`, `MAX_EVENT_ALTERNATIVES`, `MAX_LIMITED_HWCOUNTERS`, `struct mmcr_regs`, `struct power_pmu`, `PPMU_*` feature flags, alternative flags, `register_power_pmu()`, perf arch helpers, `read_bhrb()`, `power_events_sysfs_show()`, and macros `EVENT_ATTR`, `GENERIC_EVENT_ATTR`, `CACHE_EVENT_ATTR`, and `POWER_EVENT_ATTR`.

## Control Flow
PMU drivers register a `power_pmu`. Perf scheduling asks callbacks to compute MMCR registers, constraints, alternatives, memory data source/weight, BHRB filters, limited counter rules, and reserved event validation.

## State And Persistence Behavior
The registered PMU descriptor persists for the CPU family. `mmcr_regs` instances are transient computed programming state for event groups. Sysfs attribute groups expose persistent event aliases.

## Dependencies And Integration Points
It depends on perf UAPI, hardware IRQ helpers, device attributes, and POWER PMU implementations. It integrates with perf event scheduling, sampling, BHRB, memory profiling, and sysfs event discovery.

## Risks And Edge Cases
Constraint encoding is dense and easy to get wrong; limited PMCs and NAND/select/add fields determine whether event groups are schedulable. POWER10 and architecture-version flags alter extended register availability.

## Test Signals
Run perf event group scheduling, generic/cache/raw events, BHRB branch sampling, memory data source sampling, extended register sampling, sysfs alias inspection, and limited counter conflict tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_server.h -->

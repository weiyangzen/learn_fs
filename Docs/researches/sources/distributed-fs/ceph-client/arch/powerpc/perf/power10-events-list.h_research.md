# sources/distributed-fs/ceph-client/arch/powerpc/perf/power10-events-list.h

Purpose: X-macro event list of POWER10 raw PMU event encodings consumed by `power10-pmu.c` to generate enum constants and sysfs event attributes.

Important APIs/types/functions: `EVENT(name, code)` entries for cycles, dispatch/execute stalls, completed instructions, branch completion/misprediction, L1/L2/L3/cache/TLB events, alternate cycle/instruction encodings, and synthetic memory profiling aliases `MEM_LOADS`/`MEM_STORES`.

Control flow and state: no runtime control flow. The including file defines `EVENT` differently to create enum values and event attribute pointers.

State and persistence behavior: no state. The constants become raw event ABI exposed under `/sys/bus/event_source/devices/cpu/events` for POWER10/POWER11 style PMUs.

Dependencies and integration points: included by `power10-pmu.c`; event values must match the POWER10 PMU user guide and the raw format documented in that file. Memory access events rely on marked instruction completion plus sample and threshold fields encoded in the raw value.

Risks: event-code mistakes produce wrong counts while still compiling; comments include user-visible event intent and must remain synchronized; DD1 uses a restricted subset in `power10-pmu.c`, so adding events may require DD1 table decisions.

Test signals: compile `power10-pmu.c`, inspect generated sysfs event files, run generic and raw POWER10 events on hardware, and validate memory profiling aliases with `perf mem`/sample mode.

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-events-list.h

Purpose: compact X-macro list of POWER8 event encodings consumed by the POWER8 PMU implementation to define event constants and sysfs event attributes.

Important APIs/types/functions: `EVENT(name, code)` entries for cycles, stalls, completed instructions, branch events, L1/L2/L3/cache/TLB events, run-state alternates, marked events and their alternatives, dispatch/filter events, and `MEM_ACCESS`.

Control flow and state: no runtime control flow. The including POWER8 PMU file defines `EVENT` for enum and sysfs generation.

State and persistence behavior: no state. Event constants become kernel/user ABI through sysfs event names and raw config values.

Dependencies and integration points: included by the POWER8 PMU code, which shares ISA207 helpers. The alternate events listed here feed alternative scheduling and run-state equivalence logic in the POWER8 implementation.

Risks: event-code drift causes incorrect measurements; alternate pairs must remain synchronized with PMU alternative tables; `MEM_ACCESS` encodes marked-instruction random sampling assumptions and must match `isa207-common` format fields.

Test signals: compile the POWER8 PMU, verify sysfs event files, run generic/cache and alternate raw events on POWER8, and validate `MEM_ACCESS` sampling with perf memory workflows.

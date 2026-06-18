# sources/distributed-fs/ceph-client/arch/powerpc/perf/power7-events-list.h

Purpose: X-macro list of POWER7 event names and raw event codes used by `power7-pmu.c` to define enum constants, sysfs event attributes, and event pointers.

Important APIs/types/functions: hundreds of `EVENT(name, code)` entries covering completion, dispatch, stalls, branch prediction, LSU/cache/TLB, VSU/FPU, marked events, power/thermal events, nest pair events, and run-state counters.

Control flow and state: no runtime control flow. The including file controls expansion by defining `EVENT` as enum entry, `POWER_EVENT_ATTR`, or `POWER_EVENT_PTR`.

State and persistence behavior: no state. Event names and codes become static ABI exposed under POWER7 perf event sysfs.

Dependencies and integration points: included three times by `power7-pmu.c`. The list must remain sorted/consistent enough for generated attributes and for any events referenced by generic mappings or alternative tables.

Risks: wrong codes silently produce wrong counts; adding duplicate names can break enum or sysfs symbol generation; event availability may differ between POWER7 and POWER7+ even though the same list is used.

Test signals: compile `power7-pmu.c`, inspect sysfs events on POWER7/POWER7+, run representative raw events from major units, and compare counts against architectural expectations or vendor tables.

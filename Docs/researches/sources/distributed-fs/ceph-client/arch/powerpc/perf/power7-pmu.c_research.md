# sources/distributed-fs/ceph-client/arch/powerpc/perf/power7-pmu.c

Purpose: PMU backend for POWER7 and POWER7+ processors, including raw event encoding, constraint handling, alternatives, marked instruction detection, MMCR programming, sysfs event generation, generic/cache mappings, and registration.

Important APIs/types/functions: `power7_pmu`, `init_power7_pmu`, `power7_get_constraint`, `power7_compute_mmcr`, `power7_get_alternatives`, `power7_marked_instr_event`, `find_alternative_decode`, `power7_disable_pmc`, the included `power7-events-list.h`, and event/format attribute groups.

Control flow and state: constraints enforce fixed PMC uniqueness, PMC5/6 restrictions to run cycles/instructions, total PMC1-4 pressure, and shared L2 selector value. Alternatives include explicit tables, decode-event PMC swaps, and run-state substitutions. MMCR computation reserves fixed PMCs, assigns free PMC1-4 slots to unpinned events, writes MMCR1 unit/combine/L2SEL/PMCSEL fields, enables MMCRA sampling for marked instruction events, and sets MMCR0 counter-enable bits.

State and persistence behavior: no persistent state. Static PMU descriptor and sysfs attributes are registered for matching PVRs. POWER7+ adds `PPMU_SIAR_VALID`.

Dependencies and integration points: depends on `register_power_pmu`, PVR detection for `PVR_POWER7`/`PVR_POWER7p`, perf generic/cache events, generated event attributes from the event list, and common PowerPC MMCR definitions. Exposes `format/event` as `config:0-19`.

Risks: L2 events require a single shared L2SEL across a group; marked event detection is heuristic over PMCSEL/unit combinations; decode alternatives are limited to certain 4x patterns; POWER7+ behavior differs only by flag in this file.

Test signals: boot POWER7/POWER7+, verify PMU name/events/formats, run generic and selected raw events, schedule groups with conflicting L2SEL and PMC5/6 usage, test marked sampling, and check SIAR validity behavior on POWER7+.

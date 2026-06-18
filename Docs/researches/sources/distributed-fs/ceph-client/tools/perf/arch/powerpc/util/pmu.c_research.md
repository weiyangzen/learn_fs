# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/pmu.c

Purpose: Architecture PMU customization for perf, such as slots-per-cycle lookup or PMU capability initialization.

Important APIs/types/functions: `perf_pmu__arch_init`.

Control flow: Reads PMU sysfs capability files or sets architecture flags during PMU initialization.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf PMU registry and architecture PMU sysfs ABI.

Risks: Missing capability files must fall back cleanly; wrong defaults distort metrics.

Test signals: Metric calculations and PMU initialization on hardware with and without optional caps.

Source coverage: researched from the complete local file (13 lines, 227 bytes).

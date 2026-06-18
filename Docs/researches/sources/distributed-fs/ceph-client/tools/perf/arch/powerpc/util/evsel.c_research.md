# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/evsel.c

Purpose: PowerPC evsel hook that maps architecture sample weight fields.

Important APIs/types/functions: `arch_evsel__set_sample_weight`.

Control flow: Sets sample weight interpretation for PowerPC events before reporting.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on common evsel weight helpers.

Risks: Incorrect weight source skews reported memory/latency metrics.

Test signals: Perf report on weighted PowerPC samples.

Source coverage: researched from the complete local file (9 lines, 186 bytes).

# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/tsc.c

Purpose: ARM64 timestamp-counter helper used as a perf auxtrace reference clock.

Important APIs/types/functions: `rdtsc`.

Control flow: Reads the architectural virtual counter with inline assembly and returns it as `rdtsc()` equivalent.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on ARM64 counter availability and perf util TSC abstraction.

Risks: Counter frequency/availability assumptions affect trace correlation.

Test signals: Build on arm64 and compare monotonic behavior during auxtrace recording.

Source coverage: researched from the complete local file (22 lines, 498 bytes).

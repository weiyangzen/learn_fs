# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/cpuid-match.c

Purpose: ARM64 perf test for CPU ID matching logic used by PMU event maps.

Important APIs/types/functions: `test__cpuid_match`.

Control flow: Feeds MIDR strings into comparison helpers to verify wildcarding of variant/revision fields.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on arm64 header cpuid parsing helpers and perf test framework.

Risks: Incorrect masking rejects valid event-map matches or accepts wrong CPU models.

Test signals: Perf `cpuid match` test with variant/revision and base MIDR cases.

Source coverage: researched from the complete local file (38 lines, 1130 bytes).

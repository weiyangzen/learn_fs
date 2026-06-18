# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/arch-tests.c

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `test_suite`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (13 lines, 216 bytes).

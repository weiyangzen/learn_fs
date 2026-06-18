# sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/arch-tests.h

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `ARCH_TESTS_H`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (8 lines, 130 bytes).

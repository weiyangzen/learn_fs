# sources/distributed-fs/ceph-client/lib/test-kstrtox.c

## Purpose
Defines a load-time module selftest for kernel string-to-integer conversion APIs. It checks accepted values, rejected syntax, sign handling, base handling, newline rules, and overflow boundaries across unsigned and signed integer widths.

## APIs, Control Flow, and State
The module uses macros `TEST_OK()` and `TEST_FAIL()` over static `__initconst` tables. It tests `kstrtoull()`, `kstrtoll()`, `kstrtou64()`, `kstrtos64()`, `kstrtou32()`, `kstrtos32()`, `kstrtou16()`, `kstrtos16()`, `kstrtou8()`, and `kstrtos8()`. Each ok table records input string, base, and expected result; each fail table records strings expected to return a negative error. The init function invokes all test groups and returns `-EINVAL`, intentionally causing module load to fail after running the tests so the module does not remain resident.

State is limited to static test vectors and stack-local temporaries. Failures are reported through `WARN()`.

## Dependencies, Integration, Risks, and Tests
Depends on kernel module infrastructure, integer conversion helpers, limits constants, and warning output. Integration is with lib selftest builds and CI that loads test modules. Risks include missing base/autodetection combinations for narrower types, no aggregate pass/fail counter, warning-only failure reporting, and intentional init failure being misread as test failure by harnesses that do not know this convention. Test signals are the warnings emitted for mismatches, module load logs, and CI coverage across 32-bit and 64-bit builds to catch type-width assumptions.

# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mdwe_test.c

## Purpose

`mdwe_test.c` tests Memory Deny Write Execute prctl behavior. It validates prctl argument checks, monotonic flag changes, inheritance behavior across fork, and mmap/mprotect behavior when executable permission is gained.

## Important APIs, Types, and Functions

The file uses `PR_SET_MDWE`, `PR_GET_MDWE`, `PR_MDWE_REFUSE_EXEC_GAIN`, `PR_MDWE_NO_INHERIT`, `mmap()`, `mprotect()`, and kselftest harness fixtures. `FIXTURE_VARIANT(consecutive_prctl_flags)` covers repeated prctl combinations. `FIXTURE_VARIANT(mdwe)` covers stock, enabled, inherited, and no-inherit process states. `executable_map_should_fail()` centralizes expected denial rules.

## Control Flow

The standalone `prctl_flags` test asserts that invalid flag and nonzero unused arguments fail with `EINVAL`. The consecutive-prctl fixture checks that MDWE can be kept but not weakened or retroactively changed to add/remove `NO_INHERIT`. The `mdwe` fixture optionally enables MDWE, optionally forks, and then runs mapping tests. `mmap(PROT_READ|PROT_EXEC)` and staying executable are allowed; write+exec mappings and adding exec to a writable mapping are denied when MDWE applies. `MAP_FIXED` replacement is expected to work because it unmaps before mapping. The arm64 BTI test verifies `PROT_BTI` can be added to executable mappings when hardware supports it.

## State and Persistence Behavior

MDWE state is per-process prctl state and may be inherited by fork unless `PR_MDWE_NO_INHERIT` is set. Test VMAs are unmapped in fixture teardown. Parent processes in forked fixture variants exit with the child result.

## Dependencies and Integration Points

It depends on kernel MDWE prctl support in `linux/prctl.h`, architecture BTI support on arm64, and kselftest harness. It integrates with executable mapping policy, JIT hardening, and W^X enforcement paths.

## Risks and Edge Cases

Unsupported MDWE appears as fixture assertion failure rather than a broad up-front skip. Forked fixture control flow exits from the parent inside setup, which is intentional but unusual. BTI is architecture-conditional and skipped unless `HWCAP2_BTI` is present.

## Test Signals

Passes require exact `errno` for invalid prctl calls, exact `PR_GET_MDWE` flag values after valid calls, and expected mmap/mprotect success or denial for each fixture variant.

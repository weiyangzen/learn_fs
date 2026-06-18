# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.h

## Purpose
`ptrace-gpr.h` defines known GPR/FPR test values and inline validation helpers shared by GPR and transactional-memory GPR ptrace tests.

## Important APIs, Types, and Functions
It defines `GPR_1` through `GPR_4`, floating constants and their bit representations, plus `validate_gpr()`, `validate_fpr()`, and `validate_fpr_double()`.

## Control Flow and State
Validation helpers scan register arrays for expected values and return match status. No persistent state is held.

## Dependencies and Integration Points
The header is included by `ptrace-gpr.c`, `ptrace-tm-gpr.c`, and `ptrace-tm-spd-gpr.c` to keep register expectations consistent.

## Risks and Test Signals
Risks are floating representation assumptions and array-length mismatches. Test signals are all expected values found in ptrace-read register buffers.

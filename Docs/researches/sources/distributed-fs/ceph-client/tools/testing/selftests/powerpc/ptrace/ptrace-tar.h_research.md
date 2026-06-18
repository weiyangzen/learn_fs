# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tar.h

## Purpose
`ptrace-tar.h` provides known TAR, DSCR, and PPR constants plus validation logic for TAR-related ptrace tests.

## Important APIs, Types, and Functions
It defines `TAR_*`, `DSCR_*`, and `PPR_*` constants and the inline `validate_tar_registers()` helper.

## Control Flow and State
The validation helper compares a three-entry register buffer against expected TAR, PPR, and DSCR values and returns whether all fields match. No persistent state is held.

## Dependencies and Integration Points
It is included by `ptrace-tar.c` and related transactional-memory SPR tests to share constants.

## Risks and Test Signals
Risks are wrong register order assumptions and unsupported SPR state. Test signals are exact matches after ptrace reads and writes.

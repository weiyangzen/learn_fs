<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strrchr.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strrchr.S

## Purpose
`strrchr.S` implements search for the last occurrence of a character in a NUL-terminated string.

## Important APIs, Types, And Functions
The exported `strrchr` masks the search byte, scans from the start, keeps the most recent match in `a0`, and aliases `__pi_strrchr`.

## Control Flow
The loop loads the current byte, updates the saved result when it matches, advances, and stops after processing the NUL terminator. Searching for NUL therefore returns the terminator address.

## State And Persistence
No persistent state is used.

## Dependencies And Integration Points
It is used by kernel string callers when architecture string routines are selected.

## Risks
It assumes a valid terminated string. A typo in comments is non-functional; behavior must match C `strrchr`.

## Test Signals
String tests for multiple matches, absent character, first/last character, and NUL target are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strrchr.S -->

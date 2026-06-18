# sources/distributed-fs/ceph-client/arch/x86/include/asm/misc.h

## Purpose
Declares miscellaneous x86 helper `num_digits()`.

## Important APIs, Types, And Functions
The sole API is `int num_digits(int val)`, expected to return the decimal digit count for an integer value.

## Control Flow
No inline flow is present; callers link to the implementation elsewhere.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by x86 code needing compact numeric formatting without pulling in larger helpers.

## Risks And Edge Cases
Implementation behavior for zero and negative values must match callers' expectations. The header is intentionally minimal.

## Test Signals
Compile/link coverage and any formatting tests around integer digit counts are sufficient.

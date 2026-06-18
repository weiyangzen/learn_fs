# sources/distributed-fs/ceph-client/arch/s390/lib/test_modules_helpers.c

## Purpose
Defines and exports 10,000 helper functions used to stress s390 module relocation handling.

## Important APIs, Types, And Functions
`DEFINE_RETURN(i)` defines `test_modules_return_i()` returning `1 ## i - 10000` and exports it with `EXPORT_SYMBOL_GPL`. `REPEAT_10000(DEFINE_RETURN)` expands this for every generated suffix.

## Control Flow And State
Each generated function is trivial and stateless. The collective symbol set creates many relocations for the test module.

## Dependencies And Integration
Depends on `test_modules.h` for macro expansion and Linux export infrastructure. Built under `CONFIG_S390_MODULES_SANITY_TEST_HELPERS`, paired with the KUnit test module.

## Risks And Test Signals
Risks include huge object size, token-pasting surprises, export table stress, and expected-value mismatch. Signals include successful module/helper build, symbol exports, and `modules_test_s390` passing.

# sources/distributed-fs/ceph-client/net/wireless/tests/module.c

## Purpose
`module.c` supplies minimal module metadata for the cfg80211 KUnit test aggregate.

## Important APIs, Types, And Functions
It includes `<linux/module.h>` and declares `MODULE_LICENSE("GPL")` plus `MODULE_DESCRIPTION("tests for cfg80211")`.

## Control Flow
There is no executable test logic or init/exit code in this file.

## State And Persistence
No runtime state is maintained.

## Dependencies And Integration Points
The file is compiled with the other cfg80211 test objects into `cfg80211-tests.o`, giving the aggregate test object valid module metadata when built as a module.

## Risks And Edge Cases
The main risk is metadata omission: without a GPL-compatible license declaration, KUnit-only exported symbols or GPL-only symbols used by the tests could be unavailable or taint behavior could change.

## Test Signals
A successful `CONFIG_CFG80211_KUNIT_TEST=m` build and module load confirms this boilerplate is sufficient.

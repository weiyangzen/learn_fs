<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/poison.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/poison.h

## Purpose
This header defines poison pointer and byte patterns used to detect invalid list, timer, slab, page, and subsystem states.

## APIs And Flow
It exports `POISON_POINTER_DELTA`, `LIST_POISON1`, `LIST_POISON2`, `TIMER_ENTRY_STATIC`, `PAGE_POISON`, `TAIL_MAPPING`, `SLUB_RED_*`, `POISON_*`, `JBD*_POISON_FREE`, pool poison values, `ATM_POISON`, mutex debug values, and `KEY_DESTROY`. There is no control flow.

## State, Dependencies, Risks, Tests
Poison values become persistent in freed or invalidated data structures. It depends on `_AC`, optional `CONFIG_ILLEGAL_POINTER_VALUE`, and C/C++ differences where list poisons become `NULL` under C++. Risks include poisoned pointers becoming mappable on unusual systems, C++ behavior weakening detection, and consumers relying on exact byte values for diagnostics. Tests should delete list entries and confirm poison writes, validate configured pointer deltas, and compare constants with kernel expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/poison.h -->

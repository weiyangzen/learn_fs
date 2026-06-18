# sources/distributed-fs/ceph-client/include/linux/migrate_mode.h

## Purpose
Provides shared enums for migration blocking behavior and migration reason accounting.

## Important APIs/Types
`enum migrate_mode` defines `MIGRATE_ASYNC`, `MIGRATE_SYNC_LIGHT`, and `MIGRATE_SYNC`. `enum migrate_reason` lists compaction, memory failure, hotplug, syscall/cpuset, mempolicy mbind, NUMA misplaced, contiguous range, long-term pin, demotion, DAMON, and `MR_TYPES`.

## Control Flow
No executable flow. Callers pass modes to migration APIs and reasons to accounting/trace/stat paths.

## State And Persistence
No state is stored here. The enums influence runtime policy and accounting labels elsewhere.

## Dependencies And Integration Points
Included by migration and MM code that needs the vocabulary without pulling extra declarations.

## Risks
Changing enum order/count can break arrays such as `migrate_reason_names`. Misusing async mode in blocking paths creates latency issues.

## Test Signals
Build checks for reason-name array size, trace/stat reason correctness, and latency behavior under each migration mode.

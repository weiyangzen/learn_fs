# sources/distributed-fs/ceph-client/include/linux/dqblk_v1.h

## Purpose
This header records block allocation and rewrite cost constants for the old quota file format.

## Important APIs, types, and functions
It defines `V1_INIT_ALLOC`, `V1_INIT_REWRITE`, `V1_DEL_ALLOC`, and `V1_DEL_REWRITE`. There are no types or functions.

## Control flow, state, and persistence
No runtime logic is present. The constants inform quota code how many blocks may be allocated or rewritten for init and delete operations in v1 quota format.

## Dependencies and integration points
It has no include dependencies beyond its guard. It is integrated by quota format implementations that need to estimate journal credits or block reservations.

## Risks and test signals
The risk is underestimating update costs, which can cause journal reservation failures. Tests should exercise v1 quota creation and deletion under journaling and quota-file full conditions.

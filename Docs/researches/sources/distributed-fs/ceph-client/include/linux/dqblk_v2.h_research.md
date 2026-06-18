# sources/distributed-fs/ceph-client/include/linux/dqblk_v2.h

## Purpose
This header maps v2 quota format update-cost constants to the generic qtree quota constants.

## Important APIs, types, and functions
It includes `linux/dqblk_qtree.h` and defines `V2_INIT_ALLOC`, `V2_INIT_REWRITE`, `V2_DEL_ALLOC`, and `V2_DEL_REWRITE` as aliases of `QTREE_*` values.

## Control flow, state, and persistence
No runtime logic is present. It documents that v2 quota files use the qtree update model.

## Dependencies and integration points
Its only dependency is the qtree quota header. Quota code uses these constants for block and journal credit planning.

## Risks and test signals
Risks follow qtree behavior: if qtree costs change, v2 reservations change with them. Tests should verify v2 quota write/delete paths under journaling and compare block reservations against actual qtree mutations.

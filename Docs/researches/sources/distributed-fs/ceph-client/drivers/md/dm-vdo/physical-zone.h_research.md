# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/physical-zone.h

## Purpose
`physical-zone.h` defines physical-zone and PBN lock data structures plus APIs for physical block locking, allocation, and release.

## Important APIs, Types, and Functions
`enum pbn_lock_type` defines read, data write, and block-map write locks. `struct pbn_lock` stores implementation pointer, holder count, compressed fragment lock count, provisional-reference flag, read-lock increment limit, and atomic increment claims. `struct physical_zone` stores zone/thread IDs, active PBN operation map, lock pool, block allocator, and next zone. `struct physical_zones` owns the flexible zone array. The header declares lock type checks, downgrade/claim/provisional helpers, zone lifecycle, lock get/acquire/release, allocation, and dump functions.

## Control Flow
The header contract lets data/block-map paths acquire or observe PBN locks in the responsible physical zone, allocate new blocks from zones, share/downgrade locks, and release locks when operations complete.

## State and Persistence Behavior
Structs represent runtime locking and allocation coordination. Provisional-reference flags map to persistent reference-count obligations managed in the implementation.

## Dependencies and Integration Points
It includes Linux atomic operations and VDO types. It is used by data VIO, dedupe, block map, packer, and allocation paths.

## Risks and Edge Cases
Direct field access requires thread discipline. `holder_count`, `fragment_locks`, and `increments_claimed` enforce reference safety for compressed and dedupe flows; misuse can overflow references or release locks too early.

## Test Signals
Compile coverage plus physical-zone allocation, lock sharing, compressed-write lock sharing, and reference-count tests validate the header contract.

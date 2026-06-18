# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMap.c

## Purpose
Implements find, begin, and key comparison for maps of ack IDs to caller-owned `WaitAck` objects.

## Important APIs and control flow
`WaitAckMap_find` wraps generic RB-tree lookup. `WaitAckMap_begin` returns an iterator at the first ordered element using `rb_first`. `compareWaitAckMapElems` orders ack ID strings via `strcmp`.

## State, dependencies, integration
The map state is defined in the header as a generic RB tree. `AcknowledgmentStore` iterates wait maps during registration/unregistration and moves entries between wait and received maps.

## Risks and test signals
As with other string-key tree wrappers, key string lifetimes must outlive tree entries. Test ordered iteration, missing find, and behavior after moving an element between maps.

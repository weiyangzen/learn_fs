# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMap.c

## Purpose
Implements lookup and key comparison for the acknowledgment store map.

## Important APIs and control flow
`AckStoreMap_find` calls the generic `_PointerRBTree_findElem` with a string key and wraps the result in `AckStoreMapIter`. `compareAckStoreMapElems` delegates ordering to `strcmp`.

## State, dependencies, integration
The map itself is a `PointerRBTree` configured by `AckStoreMap_init` in the header. `AcknowledgmentStore` uses it to map ack IDs to `AckStoreEntry` records while threads wait for acknowledgments.

## Risks and test signals
Keys are raw string pointers and must remain valid while in the map. Test finding present/missing ack IDs and duplicate insertion behavior through the header API.

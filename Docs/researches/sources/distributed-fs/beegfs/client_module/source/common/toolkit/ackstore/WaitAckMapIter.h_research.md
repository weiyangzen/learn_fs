# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMapIter.h

## Purpose
Provides typed iterator access for `WaitAckMap`.

## Important APIs and control flow
`WaitAckMapIter_init` wraps `PointerRBTreeIter_init`. `WaitAckMapIter_next` advances to the next RB-tree element. `WaitAckMapIter_key` returns the current ack ID string, `value` returns the current `WaitAck*`, and `end` checks for null.

## State, dependencies, integration
Iterator state is embedded generic RB-tree iterator state. It is used heavily by `AcknowledgmentStore` for registration, unregistration, and ack movement.

## Risks and test signals
Iterators become invalid when their current element is erased unless callers advance or use map-specific patterns carefully. Tests should cover iteration while erasing through the owning map.

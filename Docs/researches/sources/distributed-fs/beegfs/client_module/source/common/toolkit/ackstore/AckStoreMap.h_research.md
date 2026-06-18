# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMap.h

## Purpose
Defines the ack ID to wait-state map used by `AcknowledgmentStore`.

## Important APIs and types
`AckStoreEntry` stores a borrowed `ackID`, pointers to the waiting and received `WaitAckMap`s, and a `WaitAckNotification`. Inline helpers initialize, allocate, and free entries. `AckStoreMap` wraps a generic `RBTree`; `AckStoreMap_insert`, `erase`, `find`, and lifecycle helpers provide string-key map behavior.

## State, dependencies, integration
State is an RB tree of `AckStoreEntry` pointers. The map does not own ack ID strings or `WaitAck` records; it only owns the small `AckStoreEntry` allocated for store indexing. It integrates directly with `AcknowledgmentStore_receivedAck`.

## Risks and test signals
`AckStoreEntry_construct` does not check allocation before initialization. Duplicate inserts leak the newly constructed entry unless the caller handles failed insert, and current registration code does not check insert results. Tests should cover duplicate ack IDs and unregister after partial registration.

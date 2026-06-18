# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AcknowledgmentStore.c

## Purpose
Implements a synchronized acknowledgment rendezvous store. Callers register ack IDs they are waiting for, incoming ack handlers mark arrivals, and waiters block until their wait map is empty or timeout expires.

## Important APIs and control flow
`AcknowledgmentStore_registerWaitAcks` locks the store and inserts one `AckStoreEntry` for each `WaitAck`. `unregisterWaitAcks` removes and frees store entries for outstanding wait IDs. `receivedAck` locks the store, finds an ack ID, locks the notifier mutex, moves the `WaitAck` from the wait map to the received map, broadcasts completion if the wait map becomes empty, then removes the store entry. `waitForAckCompletion` waits on the notifier condition if the wait map is non-empty and returns whether it drained.

## State, dependencies, integration
State is `storeMap` protected by `mutex`; each notifier has its own mutex/condition for wait and received maps. It depends on `AckStoreMap`, `WaitAckMap`, and BeeGFS threading primitives. Network ack handlers feed `receivedAck`; higher-level operations create wait/received maps.

## Risks and test signals
Duplicate ack IDs are not handled robustly. `unregisterWaitAcks` assumes each outstanding key exists in the store; missing entries could lead to value access on an end iterator. Tests should cover ack before timeout, timeout plus unregister, ack racing unregister, duplicate IDs, and lock ordering.

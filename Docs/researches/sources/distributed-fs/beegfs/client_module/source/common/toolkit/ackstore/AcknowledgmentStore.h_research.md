# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AcknowledgmentStore.h

## Purpose
Declares the synchronized acknowledgment store and lifecycle helpers.

## Important APIs and types
`AcknowledgmentStore` contains an `AckStoreMap` and store mutex. Inline lifecycle helpers initialize/construct/uninit/destruct the store. External operations register wait maps, unregister wait maps, mark received ack IDs, and wait for completion with timeout.

## State, dependencies, integration
The store tracks live wait registrations only in memory. It depends on `Mutex`, `Condition`, `AckStoreMap`, `WaitAckMap`, and typed iterators.

## Risks and test signals
The API requires callers not to access registered wait/received maps until unregister, except under the notifier mutex. Tests should verify lifecycle cleanup with still-registered waits and that no wait maps are touched without proper locking.

# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMap.h

## Purpose
Defines wait-ack records, completion notification state, and a string-key map wrapper.

## Important APIs and types
`WaitAckNotification` contains the mutex and condition that synchronize wait and received maps during a wait phase. `WaitAck` stores a borrowed `ackID` and caller private data. `WaitAckMap` wraps `PointerRBTree` with string keys. Inline functions initialize notifications, initialize wait records, manage map lifecycle, insert/erase, get length, and clear.

## State, dependencies, integration
Wait maps and received maps are caller-owned, while `AcknowledgmentStore` temporarily indexes the same `WaitAck` objects in its store map. No `WaitAck` payload data is freed by map clear.

## Risks and test signals
`WaitAckNotification_uninit` uninitializes only the mutex, not the condition, which may be intentional if `Condition` has no uninit requirement but should be checked. Insert failure on duplicate key is silent. Tests should cover map clear not freeing `WaitAck` values and notifier wait/broadcast behavior.

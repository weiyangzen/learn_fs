# sources/distributed-fs/beegfs/client_module/source/components/AckManager.h

## Purpose
Declares the ack manager thread and queue structures.

## Important APIs and types
`AckQueueEntry` stores creation time, metadata node ID, and copied ack ID. `AckManager` embeds `Thread`, app/config pointers, vmalloc message buffer, queue mutex/condition, and a `PointerList` queue. Exports lifecycle, request-loop, processing helpers, queue add, node-removal helper, entry-free helper, and queue-size getter.

## State, dependencies, integration
The queue is protected by `ackQueueMutex`; only the manager removes entries to preserve iterator assumptions. Integrated with metadata operations that require reliable ack transmission.

## Risks and test signals
The header includes itself (`<components/AckManager.h>`), relying on include guards to avoid recursion. Tests should verify queue ownership and that `ackID` is always copied/freed exactly once.

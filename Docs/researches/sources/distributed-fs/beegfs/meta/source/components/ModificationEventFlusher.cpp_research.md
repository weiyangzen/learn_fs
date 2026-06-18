# sources/distributed-fs/beegfs/meta/source/components/ModificationEventFlusher.cpp

Purpose: This file implements asynchronous fsck modification-event delivery over UDP with acknowledgments.

Important APIs/functions: The constructor initializes the thread, log context, datagram listener, worker list, dummy fsck node, local NIC capabilities, and missed-event flag. `run()` waits for buffered events and calls `sendToFsck()`. `add()` applies backpressure when the event list reaches `MODFLUSHER_MAXSIZE_EVENTLIST`, appends event type and entry ID, and wakes the flusher. `sendToFsck()` splices up to `MODFLUSHER_SEND_AT_ONCE` events into local lists, sends `FsckModificationEventMsg` with the missed-event flag, and disables logging locally if fsck does not acknowledge.

Control flow: The thread sleeps on `eventsAddedCond` with a two-second timeout while empty. Producers wait on `eventsFlushedCond` if the queue is full. Sending uses small UDP batches and waits up to `MODFLUSHER_WAIT_FOR_ACK_MS` with configured retries. Failed delivery sets `fsckMissedEvent` and stops further logging until re-enabled.

State and persistence behavior: State is in-memory only: event type list, entry ID list, logging flag, fsck node address, and missed-event marker. It does not persist missed events, so fsck must treat missed-event notification as a consistency signal.

Dependencies/integration: `App` creates and starts the flusher. Worker stalling in the header is used to synchronize logging-enable/disable visibility across workers.

Risks and test signals: Risks include producer blocking if fsck is unreachable, event loss on failed ACK, deadlocks if worker stalling is called from the wrong context, and UDP size constraints. No direct tests cover these concurrency paths.

# sources/distributed-fs/beegfs/meta/source/components/FileEventLogger.cpp

Purpose: This file implements persistent metadata file-event logging and a Unix-socket streaming protocol for downstream listeners.

Important APIs/types/functions: Public entry points are `createFileEventLogger()`, `destroyFileEventLogger()`, `logEvent()`, and `makeEventContext()`. Internally it defines `Timer`, `UnixAddr`, `SocketState`, packet types and close reasons, `PacketBuffer`, ring-style `PacketQueue`, `PacketWriter`/`PacketReader`, `MessageStream`, `Subscriber`, `EventLoggerShared`, `EventLoggerWorker`, `EventQ_Worker_Thread`, and serialized `FileEventLogItem`.

Control flow: Logger creation initializes a PMQ under `sysFileEventPersistDirectory` or `<storeMetaDirectory>/eventq`, starts an `EventQ-Worker`, and configures a Unix `SOCK_SEQPACKET` target. Producers call `logEvent()`, serialize a versioned event item, enqueue into PMQ, request periodic flush, and wake the reader. The worker waits for shutdown, flush deadlines, PMQ messages, and socket reconnect deadlines. It performs handshake response, processes subscriber requests for newest MSN, message range, stream start, and close, streams PMQ messages with MSNs, and resets the subscriber after termination.

State and persistence behavior: PMQ stores events durably up to configured size. `pmq_sync()` is performed by the worker or by producers when enqueue needs space. Event items include format version 2, flags, link count, event type/path fields, user ID, and nanosecond timestamp. Socket state reconnects indefinitely and logs repeated failures sparingly.

Dependencies/integration: `App` creates the logger when `sysFileEventLogTarget` is set and passes node/buddy IDs. Metadata operation handlers call `logEvent()`. Serialization tests indirectly protect the event item format.

Risks and test signals: Risks include blocking Unix `connect()`, one-subscriber limitation, packet-size truncation/`uint16_t` message size, PMQ corruption/out-of-bounds handling, producer stalls when PMQ is full, and protocol-version compatibility. No local tests in this subset exercise the protocol, PMQ persistence, reconnects, or shutdown.

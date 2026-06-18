# sources/distributed-fs/beegfs/meta/source/components/FileEventLogger.h

Purpose: This header defines the public file-event logging API used by metadata operations and `App`.

Important APIs/types: `EventContext` carries entry ID, parent ID, user ID, target parent ID, link count, timestamp, and bit flags for mirrored and secondary events. `makeEventContext()` constructs that context from `EntryInfo` and operation details. `FileEventLoggerIds` identifies the metadata node and buddy group to subscribers. `FileEventLoggerParams` configures the target address and IDs. `FileEventLogger` is opaque; callers use `createFileEventLogger()`, `destroyFileEventLogger()`, and `logEvent()`.

Control flow contract: Callers create one logger when configured, pass file events with context to `logEvent()`, and destroy the logger on shutdown. Opaqueness keeps PMQ/socket/thread internals out of operation code.

State and persistence behavior: The header exposes enough context for persistent event records. The timestamp is stored in the context rather than generated only at serialization time, preserving operation timing semantics.

Dependencies/integration: It includes `FileEvent` and `EntryInfo`. `App` owns the logger in a `unique_ptr` with `destroyFileEventLogger` deleter and exposes `getFileEventLogger()`.

Risks and test signals: The API accepts a raw `FileEventLogger*`; callers must handle a null logger when logging is disabled. Context correctness depends on operation code supplying parent/target/link details. Direct tests should validate flag construction and serialized event compatibility.

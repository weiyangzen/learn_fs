# sources/distributed-fs/lizardfs/src/common/exceptions.h

Purpose: declares common exception categories for configuration, filesystem, initialization, connections, reads, writes, CRC, and parsing.

Important APIs/types/functions: macro-created classes include `ConfigurationException`, `FilesystemException`, `InitializeException`, `ConnectionException`, read/write recoverable and unrecoverable variants, and no-valid-copies variants. `ChunkCrcException` adds server and `ChunkPartType` context. `ParseException` can prefix messages with a line number.

Control flow: exceptions are constructed with messages/statuses and thrown by subsystem code. `ChunkCrcException` embeds server text in the base message and retains structured fields.

State and persistence: exception objects only; no persistence.

Dependencies and integration: depends on chunk part types, network address, error status strings, and `Exception`. It is a shared error taxonomy for IO and configuration paths.

Risks: category hierarchy implies recoverability semantics; callers must catch the right layer. `ChunkCrcException` stores copies of address and chunk type, which is useful but can be overlooked if only `what()` is logged.

Test signals: no direct tests in subset.

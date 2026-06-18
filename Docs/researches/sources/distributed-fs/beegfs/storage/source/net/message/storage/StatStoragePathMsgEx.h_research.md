## sources/distributed-fs/beegfs/storage/source/net/message/storage/StatStoragePathMsgEx.h

### Purpose
`StatStoragePathMsgEx.h` declares the storage-side statfs target path handler.

### Important APIs, Types, And Functions
The class inherits `StatStoragePathMsg`, overrides `processIncoming(ResponseContext&)`, and declares private helper `statStoragePath()` for byte/inode outputs.

### Control Flow, State, And Persistence
The handler has no member state. It fills caller-provided output pointers during request handling.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common storage errors and stat request messages. Tests should validate helper result codes and response field population.

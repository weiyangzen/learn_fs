## sources/distributed-fs/beegfs/storage/source/net/message/session/FSyncLocalFileMsgEx.cpp

### Purpose
`FSyncLocalFileMsgEx.cpp` handles fsync requests for open local chunk file sessions. It optionally performs cache-loss session checks and supports buddy mirror target resolution.

### Important APIs, Types, And Functions
`processIncoming()` replies with `FSyncLocalFileRespMsg(fsync())`. `fsync()` resolves mirror buddy group targets when `FSYNCLOCALFILEMSG_FLAG_BUDDYMIRROR` is set, references or creates the client session, looks up `SessionLocalFile`, calls `MsgHelperIO::fsync()` unless `FSYNCLOCALFILEMSG_FLAG_NO_SYNC` is set, and returns storage-crash errors when session checks indicate lost state.

### Control Flow, State, And Persistence
Non-mirror messages can use `FSYNCLOCALFILEMSG_FLAG_SESSION_CHECK`; mirror sessions skip that check. Persistent effects are the filesystem sync of an open FD and possible session creation. Missing session is only an error when session check is enabled.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on sessions, mirror buddy mapper, `SessionLocalFileStore`, and `MsgHelperIO`. Risks include creating sessions for fsync-only requests, invalid mirror groups flowing to failed lookup, and treating closed/missing files as success without session check. Tests should cover normal fsync, no-sync flag, mirror primary/secondary resolution, missing session with/without session check, crashed sessions, and fsync failure.

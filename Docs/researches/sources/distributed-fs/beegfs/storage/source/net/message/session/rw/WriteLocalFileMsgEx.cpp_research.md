## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileMsgEx.cpp

### Purpose
`WriteLocalFileMsgEx.cpp` implements storage-side chunk writes. It receives client data incrementally, enforces quota, opens/creates chunk files, forwards mirrored writes to the secondary, writes locally, handles retries at safe points, and returns byte counts or negative BeeGFS errors.

### Important APIs, Types, And Functions
`WriteLocalFileMsgExBase::processIncoming()` validates the message, calls `write()`, sends a protocol-specific response, and updates write op stats. `write()` resolves mirror targets, manages `SessionLocalFile`, checks session-crash state, enforces quota, locks chunks during buddy resync, opens files through `openFile()`, prepares mirroring through `prepareMirroring()`, performs `incrementalRecvAndWriteStateful()`, and calls `finishMirroring()`. Helpers include `doWrite()`, `incrementalRecvPadding()`, `sendToMirror()`, and `doSessionCheck()`.

### Control Flow, State, And Persistence
Data is received in buffer-sized chunks, optionally forwarded to the mirror before local `pwrite()`, and then written at tracked offsets. On early errors, the handler drains the remaining client payload to keep the stream protocol aligned. Mirroring prepares a secondary write message and can retry only before any client payload is irrecoverably consumed. Persistent effects are chunk creation/writes, quota-aware creation, target buddy-needs-resync marking, and session offset/counter state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sessions, chunk locks, quota stores, storage targets, mirror mappers, target states, `MessagingTk`, sockets, and `MsgHelperIO`. Risks are high: mirror retry boundaries, partial writes, quota race/error mapping, chunk lock release, stream padding after failures, session-crash signaling, and `mirrorToSock` lifecycle. Tests should cover local writes, quota exceeded, missing/unknown targets, mirrored secondary online/offline/unclear, mirror partial write, socket exceptions, disabled IO, direct IO buffer sizing, short `pwrite()`, and payload draining.

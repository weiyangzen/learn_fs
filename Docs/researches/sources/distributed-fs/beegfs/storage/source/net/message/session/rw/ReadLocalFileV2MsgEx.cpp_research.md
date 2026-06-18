## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileV2MsgEx.cpp

### Purpose
`ReadLocalFileV2MsgEx.cpp` implements the storage-side chunk read protocol. It opens or reuses a session-local file, reads requested ranges incrementally, sends length-framed data, updates session offsets before client-visible completion, and optionally triggers read-ahead.

### Important APIs, Types, And Functions
`ReadLocalFileMsgExBase::processIncoming()` resolves mirror targets, manages sessions, opens the chunk through `openFile()`, and calls `incrementalReadStatefulAndSendV2()`. `ReadLocalFileV2MsgSender::getBuffers()` reserves protocol space around the worker buffer. `incrementalReadStatefulAndSendV2()` calculates buffer-limited read lengths, uses `MsgHelperIO::pread()` unless disabled, sends data through template hooks, updates read counters and stats, and handles EOF/error length markers. `checkAndStartReadAhead()` uses sequential read counters.

### Control Flow, State, And Persistence
Session state includes FD, current offset, direct I/O flag, read counter, and last read-ahead trigger. Mirrored reads on non-good targets or unknown mirror targets return communication-style errors so clients can retry elsewhere. Persistent filesystem state is read-only; runtime counters and op stats are updated.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sessions, mirror mappers, storage targets, `MsgHelperIO`, `StorageTkEx`, sockets, worker buffers, and optional RDMA linkage. Risks include offset races if updates happen after sends, protocol buffer size assumptions, handling `DISABLE_IO`, EOF framing, and read-ahead thresholds. Tests should cover existing/missing chunks, sequential and random reads, tiny buffers, EOF partial reads, disabled IO, direct IO, mirror target consistency failures, socket exceptions, and RDMA forced linkage builds.

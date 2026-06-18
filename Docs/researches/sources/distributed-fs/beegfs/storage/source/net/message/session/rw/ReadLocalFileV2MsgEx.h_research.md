## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileV2MsgEx.h

### Purpose
`ReadLocalFileV2MsgEx.h` declares the generic read state machine and the TCP V2 read protocol specialization.

### Important APIs, Types, And Functions
`ReadStateBase` stores log context, remaining bytes, session file pointer, and last read result. `ReadLocalFileMsgExBase<Msg, ReadState>` provides common `processIncoming()`, `openFile()`, read-ahead, and incremental read/send helpers, delegating protocol-specific hooks to `Msg`. `ReadLocalFileV2MsgSender` implements length-framed socket sending and buffer layout. The typedef `ReadLocalFileV2MsgEx` binds them.

### Control Flow, State, And Persistence
The CRTP-like design lets TCP V2 and RDMA variants share session and file I/O behavior while customizing data transport. The V2 protocol sends an int64 length before each chunk and a zero final length marker after the last chunk.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common read message definitions, `SessionLocalFileStore`, storage errors, and storage targets. Risks include template interface drift, inline delegation hiding compile errors until instantiation, and protocol framing assumptions. Tests should instantiate both TCP and RDMA variants where available, verify length framing, and exercise invalid message checks.

## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GenericDebugMsgEx.h

### Purpose
`GenericDebugMsgEx.h` declares the storage-side generic debug handler and its command-specific helper methods.

### Important APIs, Types, And Functions
The class derives from `GenericDebugMsg`, overrides `processIncoming()`, and declares private helpers for command dispatch, open-file listing, version, queue stats, quota exceeded, used quota, resync queue length, chunk lock store size/content, and rejection-rate setting.

### Control Flow, State, And Persistence
The handler stores no additional data. Each command uses inherited command string data and samples or mutates global app subsystems.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the common node debug message and is factory-created for `NETMSGTYPE_GenericDebug`. Risks are mostly in command surface growth and keeping helper declarations aligned with `.cpp` dispatch. Tests should validate command dispatch coverage and unknown command response.

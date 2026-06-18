## sources/distributed-fs/beegfs/storage/source/net/message/storage/TruncLocalFileMsgEx.h

### Purpose
`TruncLocalFileMsgEx.h` declares the storage-side truncation handler and helpers for mirrored forwarding, local truncation, and dynamic attribute responses.

### Important APIs, Types, And Functions
The class derives from `TruncLocalFileMsg` and overrides `processIncoming(ResponseContext&)`. `DynamicAttribs` initializes size, block count, timestamps, and storage version to zero. Helpers include `truncFile()`, `getTargetFD()`, `getDynamicAttribsByPath()`, `getFakeDynAttribs()`, and `forwardToSecondary()`.

### Control Flow, State, And Persistence
The header stores no request-independent state. Helper signatures show the operation's phases: target FD validation, local filesystem mutation, attribute collection, and mirror forwarding.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common truncation messages, storage errors, paths, and `StorageTarget`. Tests should validate each helper branch through the `.cpp`, especially response suppression and storage version generation.

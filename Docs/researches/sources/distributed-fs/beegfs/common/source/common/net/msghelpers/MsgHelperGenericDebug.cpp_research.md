<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.cpp

### Purpose
`MsgHelperGenericDebug.cpp` implements service debug operations for reading logs/config/load average, dropping caches, changing log levels, listing outbound connections, showing exceeded quota IDs, and listing target/storage-pool state.

### Important APIs, Types, And Functions
Public static handlers include `processOpVarLogMessages()`, `processOpVarLogKernLog()`, `processOpFhgfsLog()`, `processOpLoadAvg()`, `processOpDropCaches()`, `processOpGetLogLevel()`, `processOpSetLogLevel()`, `processOpCfgFile()`, `processOpNetOut()`, `processOpQuotaExceeded()`, `processOpListTargetStates()`, and `processOpListStoragePools()`. Helpers `loadTextFile()`, `writeTextFile()`, `printNodeStoreConns()`, and `printNodeConns()` do the concrete file and node formatting work.

### Control Flow
Most handlers parse arguments from an `istringstream`, perform a local operation, and return human-readable text. `loadTextFile()` stats the file, seeks to the last 100 KiB for large files, then reads bounded lines. `processOpSetLogLevel()` can update one log topic or all topics. Network output walks management/meta/storage node stores and prints connection counts plus first peer names. Quota output validates `uid/gid` and `size/inode` arguments before asking `ExceededQuotaStore`.

### State, Persistence, And Dependencies
This file can read sensitive local files and can write `/proc/sys/vm/drop_caches`. It mutates global logger levels and can trigger kernel cache dropping. Dependencies include `AbstractApp`, `PThread`, `System`, node stores, quota stores, `TargetStateStore`, `StoragePoolStore`, and `ZipIterator`.

### Integration Points
Generic debug messages call these handlers based on string operation names from `MsgHelperGenericDebug.h`. Admin/debug tooling receives the returned text.

### Risks
Debug operations are operationally powerful: reading logs/configs may expose sensitive data, setting log levels changes runtime behavior, and dropping caches requires privilege and affects performance. File reads are bounded but line truncation/read errors produce text responses rather than structured errors. Tests should cover argument parsing, bounded large-file reads, missing files, log-topic validation, quota argument validation, and connection formatting with zero/TCP/RDMA connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.cpp -->

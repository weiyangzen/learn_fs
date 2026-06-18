<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.h -->
## sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.h

### Purpose
`MsgHelperGenericDebug.h` declares operation-string constants and static helpers for generic debug commands exposed over BeeGFS messages.

### Important APIs, Types, And Functions
It defines operation names such as `varlogmessages`, `beegfslog`, `dropcaches`, `getloglevel`, `setloglevel`, `net`, `quotaexceeded`, target-state listing, storage-pool listing, and rejection-rate control. The `MsgHelperGenericDebug` class declares public processors plus `loadTextFile()` and `writeTextFile()`.

### Control Flow
Callers dispatch on the operation string and call the corresponding static function with an argument stream and relevant stores. Private helpers format node stores and node connection state.

### State, Persistence, And Dependencies
The header has no state but exposes functions that can mutate runtime logger state or system cache state in the implementation. It depends on `NodeStoreServers`, `ExceededQuotaStore`, and common storage/target types.

### Integration Points
Generic debug message handlers include this header to map command strings to implementation functions.

### Risks
The command surface is stringly typed and security-sensitive. Tests should cover every operation constant's dispatch path and ensure unavailable stores produce clear responses rather than crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.h -->

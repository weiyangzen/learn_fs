<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameRespMsg.h

### Purpose
`RenameRespMsg` returns the integer result of a metadata rename operation.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_RenameResp`. Unlike several neighboring response wrappers, it does not add a `getResult()` cast helper.

### Control Flow
Serialization is inherited single-integer behavior.

### State, Persistence, And Dependencies
The message has no persistent state. It depends on `SimpleIntMsg` and caller knowledge of the result-code convention.

### Integration Points
Rename callers consume this response after `RenameMsg`.

### Risks
Callers must use `getValue()` or inherited APIs and cast consistently to `FhgfsOpsErr`. Tests should cover representative success and failure result codes and ensure callers do not assume extra overwrite metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameRespMsg.h -->

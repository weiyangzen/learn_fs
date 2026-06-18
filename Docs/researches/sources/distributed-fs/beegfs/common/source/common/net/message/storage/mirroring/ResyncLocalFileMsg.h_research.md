<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileMsg.h

### Purpose
`ResyncLocalFileMsg` transfers chunk-file content and optional attributes during storage buddy resync or chunk balancing. It can also represent metadata-only operations through the `NODATA` feature flag.

### Important APIs, Types, And Functions
The message derives from `NetMessageSerdes<ResyncLocalFileMsg>` with `NETMSGTYPE_ResyncLocalFile`. Feature flags control attributes, no-data mode, truncation, sparse checking, buddy-mirror destination, secondary writes, and chunk-balance buddy writes. Serialization writes relative path, target ID, offset, count, optional `SettableFileAttribs`, then a raw data block of `count` bytes.

### Control Flow
Senders provide a non-owned data buffer plus path/target/offset/count and optionally copy chunk attributes. Receivers inspect header feature flags to decide whether attributes/data/truncation/sparse checks apply.

### State, Persistence, And Dependencies
The message is transient but causes persistent chunk data and file attributes to be updated on disk. It depends on `PathInfo`, `StorageDefinitions`, raw-block serialization, and `SettableFileAttribs`.

### Integration Points
Storage resync workers and chunk-balancing flows use it to repair or copy chunk files between primary and secondary targets.

### Risks
`NODATA` still serializes `rawBlock(dataBuf, count)`, so callers must keep count/data consistent with flag semantics or rely on count zero. `TRUNC` is documented as incompatible with `NODATA` but not enforced here. Sparse-check and buddy-mirror flags affect disk layout decisions outside the message. Tests should cover data writes, attribute-only updates, truncation, sparse data, invalid flag combinations, and large counts near payload limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileMsg.h -->

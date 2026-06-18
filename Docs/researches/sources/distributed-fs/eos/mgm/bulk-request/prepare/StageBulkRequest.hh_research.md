## sources/distributed-fs/eos/mgm/bulk-request/prepare/StageBulkRequest.hh

Purpose: declares the stage bulk-request subtype for files to retrieve/prepare. It records issuer identity and creation time in addition to base request ID/files.

Important APIs: constructors with current time or explicit creation time, `getType()` returning `PREPARE_STAGE`, `getIssuerVid()`, and `getCreationTime()`.

State/integration: issuer VID and creation time are immutable members persisted by `ProcDirectoryBulkRequestDAO` xattrs and reconstructed through `BulkRequestFactory`. Risks include only UID being persisted in DAO reconstruction in the read code, while the full `VirtualIdentity` is stored at creation time. Tests should verify creation-time persistence and clarify which identity fields are expected after reload.

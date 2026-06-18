<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/DynamicFileAttribs.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/DynamicFileAttribs.h

Purpose: Defines dynamic file attributes reported by storage targets for chunked files.

Important APIs/types: `DynamicFileAttribs` stores file size, allocated blocks, modification time, last access time, storage version, and complete chunk count. It has a static serdes method and vector typedefs.

Control flow/state/persistence: This is a serialized value object. It is persisted or sent as part of higher-level metadata structures such as `ChunkFileInfo`.

Dependencies/integration: Used by stripe/chunk metadata aggregation, stat refresh, and fsck/repair code.

Risks/test signals: Field order and signedness are important, particularly `int64_t` file size/times and `uint64_t` blocks/version. Tests should round-trip edge values and verify consumers handle unset or stale versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/DynamicFileAttribs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.h

Purpose: Represents one chunk file's storage version and dynamic attributes.

Important APIs/types: `ChunkFileInfo` stores `storageVersion` and `DynamicFileAttribs`. It serializes both, exposes file size, mtime, atime, complete chunk counts, block count, raw attribute access, and `updateDynAttribs`.

Control flow/state/persistence: `updateDynAttribs` selectively applies newer/larger dynamic attributes and reports whether state changed. Serialization makes this object suitable for metadata and network transport.

Dependencies/integration: Depends on `DynamicFileAttribs`, BeeGFS serialization, and chunk metadata consumers that aggregate file attributes across targets.

Risks/test signals: Attribute update semantics affect file-size and timestamp reconciliation. Tests should cover older/equal/newer storage versions, zero/negative file sizes, chunk-count math for incomplete chunks, and equality round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.h -->

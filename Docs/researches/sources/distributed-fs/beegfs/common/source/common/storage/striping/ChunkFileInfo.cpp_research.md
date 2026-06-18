<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.cpp

Purpose: Implements equality for chunk file dynamic metadata wrappers.

Important APIs/functions: `ChunkFileInfo::operator==` compares storage version and dynamic attributes.

Control flow/state/persistence: No control flow beyond value comparison. Persistence is handled by serialization in the header.

Dependencies/integration: Depends on `ChunkFileInfo.h` and `DynamicFileAttribs` equality. Used by metadata/storage update logic to detect changed chunk state.

Risks/test signals: Equality must stay aligned with serialization fields. Tests should compare all fields, especially storage version changes with identical dynamic attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.cpp -->

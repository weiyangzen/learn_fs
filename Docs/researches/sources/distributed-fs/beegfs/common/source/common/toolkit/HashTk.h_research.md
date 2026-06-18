<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.h

Purpose: Declares common hash functions.

Important APIs/types: Namespace `HashTk` exposes `hsieh32(const char*, int)` and `authHash(const unsigned char*, std::size_t)`.

Control flow/state/persistence: Stateless deterministic functions.

Dependencies/integration: Included by placement/authentication helpers requiring stable hash APIs.

Risks/test signals: Tests should ensure null/zero-length caller expectations are documented and hash outputs remain stable across platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.h -->

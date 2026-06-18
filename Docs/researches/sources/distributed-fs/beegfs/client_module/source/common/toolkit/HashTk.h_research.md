<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/HashTk.h -->
## sources/distributed-fs/beegfs/client_module/source/common/toolkit/HashTk.h

**Purpose:** Declares hash algorithms and hash/auth helper APIs. **APIs/types:** `HashTkHashTypes` includes Hsieh32 and half-MD4; `HashTk_hash32`, `HashTk_hash64`, inline `HashTk_hash`, `HashTk_sha256`, and `HashTk_authHash`. **Control flow/state:** inline `HashTk_hash` chooses 64-bit only when `hashSize == 64`, otherwise 32-bit. **Dependencies/integration:** consumers use it for stable BeeGFS hash partitioning and auth secret derivation. **Risks/tests:** callers passing unexpected `hashSize` silently get 32-bit; tests should include both algorithms and size dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/HashTk.h -->

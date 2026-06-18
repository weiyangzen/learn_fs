<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.cpp

Purpose: Implements hashing utilities used for placement or authentication-style checks.

Important APIs/functions: `HashTk::hsieh32` implements a 32-bit Hsieh/SuperFastHash-style function over byte data. `HashTk::authHash` produces a 64-bit hash over unsigned bytes.

Control flow/state/persistence: Pure deterministic hash computation, no state. Both process input buffers sequentially.

Dependencies/integration: Used wherever stable BeeGFS hashes are required for metadata placement, routing, or lightweight authentication/checking.

Risks/test signals: Hash output stability is compatibility-sensitive. Tests should use golden vectors for empty input, short tails, aligned/unaligned buffers, long buffers, and byte values over 127.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.cpp -->

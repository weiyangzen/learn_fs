# sources/distributed-fs/orangefs/src/common/hash/murmur3.h

Purpose: Declares MurmurHash3 hash functions.

Important APIs/functions: `MurmurHash3_x86_32()`, `MurmurHash3_x86_128()`, and `MurmurHash3_x64_128()` accept key pointer, byte length, 32-bit seed, and output buffer.

Control flow/state: Header only; all functions are stateless and write into caller-owned `out`.

Dependencies/integration: Includes `<stdint.h>`. Consumers must allocate appropriately sized output buffers: 4 bytes for x86_32 and 16 bytes for 128-bit variants.

Risks: The API does not encode output size in the type system, so undersized `out` buffers are caller bugs. No `extern "C"` guard for C++ consumers.

Test signals: Compile C and C++ consumers if needed, and validate output buffer sizes at call sites.

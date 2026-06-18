# File Research: sources/block-storage/mdadm/sha1.c

Purpose: GPL SHA1 implementation imported from GNU code, used by mdadm for stable UUID derivation and hashing.

API implemented:
- `sha1_init_ctx()`
- `sha1_read_ctx()`
- `sha1_finish_ctx()`
- `sha1_stream()`
- `sha1_buffer()`
- `sha1_process_bytes()`
- `sha1_process_block()`

Implementation details:
- Maintains five SHA1 state words, total byte count, buffered partial block, and 32-word internal buffer.
- Handles endian conversion through `SWAP`.
- Handles unaligned input conditionally using `_STRING_ARCH_unaligned` and an `alignof` fallback.
- `sha1_stream()` reads in 4096-byte blocks and handles partial reads/EOF carefully.
- Compression function unrolls all 80 SHA1 rounds using macros `F1` through `F4`, constants `K1` through `K4`, and ring-buffer message expansion.

Dependencies:
- Includes `sha1.h`, `<stddef.h>`, `<string.h>`, optional `unlocked-io.h`.

Notes:
- Comments in `sha1_read_ctx()` and `sha1_finish_ctx()` require result buffers to be aligned for 32-bit access on some systems.
- SHA1 is not collision-resistant for security use, but mdadm uses it here for compact deterministic identifiers, not cryptographic authentication.

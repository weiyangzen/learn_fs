# File Research: sources/block-storage/mdadm/md5.h

## Role

`md5.h` declares the MD5 digest API and context structure imported from GNU libc-style code. It provides mdadm with a local MD5 interface when not using libc-internal names.

## API Surface

The header declares:

- `struct md5_ctx`, containing MD5 state words `A` through `D`, total byte count, buffer length, and an aligned 128-byte staging buffer.
- `__md5_init_ctx()` to initialize state.
- `__md5_process_block()` for block-aligned input; length must be a multiple of 64 bytes.
- `__md5_process_bytes()` for arbitrary-length input.
- `__md5_finish_ctx()` to finalize and write a 16-byte digest.
- `__md5_read_ctx()` to read the current digest state.
- `__md5_stream()` for FILE input.
- `__md5_buffer()` for in-memory input.

Outside `_LIBC`, the `__md5_*` names are macro-aliased to public `md5_*` names.

## Portability Support

The file conditionally includes `inttypes.h` and `stdint.h`, defines `__GNUC_PREREQ`, `__THROW`, and `__attribute__` compatibility helpers, and uses `uint32_t` as `md5_uint32`.

## Important Invariants

- Digests are written in little-endian byte order.
- Some result buffers must be correctly aligned for 32-bit access.
- `__md5_process_block()` requires 64-byte-multiple input.
- The buffer is explicitly aligned to `md5_uint32`.

## Risks

MD5 is cryptographically broken for security use. In mdadm context this header should be treated as a compatibility/checksum facility, not as a secure hash primitive. Any new use for authentication or tamper resistance would be inappropriate.

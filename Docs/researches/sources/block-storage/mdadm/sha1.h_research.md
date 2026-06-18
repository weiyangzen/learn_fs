# File Research: sources/block-storage/mdadm/sha1.h

Purpose: declares the SHA1 context type and public SHA1 functions.

Key contents:
- Include guard `SHA1_H`.
- Determines a 32-bit unsigned integer type `sha1_uint32` using libc types or preprocessor checks against `INT_MAX`, `SHRT_MAX`, and `LONG_MAX`.
- Defines `struct sha1_ctx` with state words `A` through `E`, total byte counters, buffer length, and 32-word buffer.
- Declares block, byte, stream, buffer, finish, read, and init functions.
- Provides C++ `extern "C"` wrappers.

Notes:
- Comments state `sha1_process_block()` requires `LEN` to be a multiple of 64, while `sha1_process_bytes()` accepts arbitrary lengths.
- Public digest output size is 20 bytes.

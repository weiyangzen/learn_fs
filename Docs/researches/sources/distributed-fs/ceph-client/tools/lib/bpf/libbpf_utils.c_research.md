<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_utils.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_utils.c

## Purpose
This utility implementation provides libbpf error string conversion and an internal SHA-256 implementation used by libbpf components that need deterministic hashing without external crypto dependencies.

## APIs, Types, and Functions
Error APIs are `libbpf_strerror()` and internal `libbpf_errstr()`. Static data includes `libbpf_strerror_table[]` mapping custom `enum libbpf_errno` values to messages. SHA-256 support includes unaligned big-endian helpers `get_unaligned_be32()` and `put_unaligned_be32()`, compression constants `sha256_K[]`, boolean/rotation macros, `sha256_blocks()`, and public internal `libbpf_sha256()`.

## Control Flow, State, and Persistence
`libbpf_strerror()` validates the destination buffer, normalizes positive and negative errors, delegates ordinary errno values to `strerror_r()`, maps libbpf private errors through `libbpf_strerror_table`, and returns `-ERANGE` if the formatted message was truncated or `-ENOENT` for unknown libbpf error numbers. It always NUL-terminates nonempty output buffers. `libbpf_errstr()` returns constant strings for common negative errno values or a thread-local numeric buffer for unknown values. `libbpf_sha256()` initializes the SHA-256 state, processes whole 64-byte blocks, pads the final one or two blocks with the bit count, compresses them, and writes a 32-byte big-endian digest.

Persistent state is limited to the thread-local fallback buffer in `libbpf_errstr()`. SHA-256 state is stack-local and deterministic.

## Dependencies and Integration
The file depends on libc formatting/string errors, Linux endian/kernel macros such as `ARRAY_SIZE` and `roundup`, local public and internal libbpf headers, and `ror32()` from `libbpf_internal.h`. Error conversion backs public diagnostics and internal logging. SHA-256 is declared in the internal header and can be used by loader/linker code for stable content hashes.

## Risks and Test Signals
Risks include platform differences in `strerror_r()` return semantics, missing table entries for new `enum libbpf_errno` values, the small thread-local numeric buffer in `libbpf_errstr()`, pointer arithmetic on `const void *` relying on compiler extensions, and SHA-256 correctness for boundary lengths. Test signals should include ordinary errno and private errno conversion, truncation behavior, unknown error handling, thread-local fallback isolation, and SHA-256 known-answer vectors for empty input, one block, 55/56/57-byte padding boundaries, and multi-block input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_utils.c -->

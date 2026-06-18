# sources/cloud-native/composefs/libcomposefs/erofs_fs_wrapper.h

Purpose: userspace compatibility wrapper around Linux EROFS format definitions, providing endian helpers, alignment/bit macros, block constants, CRC32C, file type enum, and `ilog2` before including `erofs_fs.h`.

Important APIs/types/functions: `__packed`, `u8`, `cpu_to_le16/32/64`, `le16/32/64_to_cpu`, `round_up`, `round_down`, `ALIGN_TO`, `BIT`, `BUILD_BUG_ON`, `DIV_ROUND_UP`, `EROFS_BLKSIZ`, `erofs_crc32c`, EROFS file-type enum, and macro `ilog2`.

Control flow: inline endian conversion delegates to host byte-order functions; CRC32C iterates bytes/bits with the little-endian polynomial; `ilog2` is a long constant-expression ternary chain.

State/persistence: no runtime state, but constants and conversions define how persistent EROFS bytes are encoded.

Dependencies/integration: depends on `<linux/types.h>`, `<stdbool.h>`, host endian functions, and includes `erofs_fs.h`. It lets libcomposefs reuse kernel-style headers in userspace.

Risks/test signals: missing includes for endian functions must be supplied by translation units or platform headers. CRC32C implementation is simple but slow; correctness is validated indirectly by image checksums/fsck.

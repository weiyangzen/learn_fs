<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_integer.h -->
# sources/compression/xz/src/common/tuklib_integer.h

Purpose: portable integer, endian, unaligned/aligned access, byte-swap, and bit-scan helpers.

Important APIs/types/functions: `byteswap16/32/64`, `conv16/32/64{be,le}`, `read*/write*{ne,be,le}`, `aligned_read*/aligned_write*`, `bsr32`, `clz32`, `ctz32`, and `bsf32`.

Control flow: preprocessor selects compiler/system byte-swap intrinsics or fallback expressions, endian conversion macros, fast-unaligned `memcpy` or byte-by-byte implementations, aligned access with `__builtin_assume_aligned` when possible, and bit-scan implementations using compiler builtins, inline x86 assembly, MSVC intrinsics, or portable shifts.

State and persistence: stateless inline/macro operations.

Dependencies and integration: consumed throughout liblzma for parsing headers, CRC, range coding, and optimized data access.

Risks: macro arguments may be evaluated more than once for conversion/write macros. Optional unsafe type punning can violate strict aliasing. Bit-scan functions are undefined for zero input.

Test signals: unit tests on big/little-endian and strict-align architectures; sanitizer/UB builds without unsafe punning; compare read/write round trips for aligned and unaligned buffers.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_integer.h -->

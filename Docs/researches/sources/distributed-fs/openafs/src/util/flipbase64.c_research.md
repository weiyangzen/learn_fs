# sources/distributed-fs/openafs/src/util/flipbase64.c

Purpose: Implements "flipped" base64 conversion for 64-bit integers, encoding from low-order bits to high-order bits instead of the usual high-to-low direction.

Important APIs: `int64_to_flipbase64(lb64_string_t s, afs_uint64 a)` writes an encoded string into caller storage. `flipbase64_to_int64(char *s)` decodes a string back into an integer. The translation tables differ on Darwin versus other platforms.

Control flow and state: Encoding repeatedly masks the low 6 bits, emits one table character, shifts right by 6, and terminates with NUL. Zero maps to the first alphabet character. Decoding iterates over the input, looks up each character in `c_reverse`, ignores illegal values (`>= 64`), shifts by cumulative 6-bit offsets, and ORs into the result.

Dependencies and integration: Includes `afsutil.h` for typedefs like `lb64_string_t` and AFS integer types. The `util/test/fb64.c` command-line utility exercises conversion, round-trip checks, and range verification.

Risks and test signals: Invalid characters are silently skipped, which can hide corrupted input. The return type is signed `afs_int64` even though encoding takes `afs_uint64`, so values with the high bit set may need careful interpretation. The `fb64` test is the direct test signal.

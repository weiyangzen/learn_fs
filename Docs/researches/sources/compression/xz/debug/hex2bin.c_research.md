<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/hex2bin.c -->
# sources/compression/xz/debug/hex2bin.c

Purpose: command-line converter from textual hexadecimal pairs to raw binary bytes.

Important APIs/types/functions: `getbin(int)` maps ASCII hex digits to nibble values; `main` loops over `getchar`, `isxdigit`, `putchar`, and reports invalid odd/incomplete hex pairs.

Control flow: non-hex characters are skipped until a first hex digit is found. The next character must also be hex; the two nibbles are combined and emitted. EOF after non-hex separators exits successfully.

State and persistence: stateless streaming filter over stdin/stdout.

Dependencies and integration: depends on `sysdefs.h`, stdio, and ctype. It complements debug tools that print or consume byte-oriented test vectors.

Risks: `getbin` assumes callers passed hex digits; it treats any non-digit/non-uppercase input as lowercase hex. `putchar` errors are reported, but read errors are not distinguished from EOF.

Test signals: round trip known strings such as `00 ff 5D` to binary and inspect with `od`; malformed single trailing hex digit should return failure.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/hex2bin.c -->

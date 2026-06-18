# sources/compression/zlib/contrib/puff/bin-writer.c

## Purpose
`bin-writer.c` is a tiny test utility that converts textual hexadecimal byte pairs from standard input into binary bytes on standard output.

## Important APIs, Types, and Functions
The only function is `main()`. It uses `getchar()` to read two hex characters, `strtol(..., 16)` to convert them, and `fwrite()` to emit one byte.

## Control Flow
The loop reads a first character, reads the next character as the second hex digit, null-terminates a two-character buffer, converts it to a byte, writes the byte to stdout, then reads and discards one separator character. EOF on the separator read terminates the loop.

## State and Persistence
No files are opened and no persistent state is stored. The program streams stdin to stdout using a fixed three-byte local buffer and temporary conversion variables.

## Dependencies and Integration Points
Built by `contrib/puff/CMakeLists.txt` for tests. It depends only on the C standard library headers `stdio.h` and `stdlib.h`.

## Risks and Edge Cases
The program assumes every byte is represented by two consecutive hex characters and ignores `endptr`, so malformed input still writes a converted value. If EOF occurs while reading the second hex digit, that `EOF` value is cast to `char` and converted as part of the pair. It discards exactly one separator character, so inputs without separators are parsed incorrectly after the first byte. The comment says separators can be spaces, newlines, commas, etc., but the implementation does not skip arbitrary-length separators.

## Test Signals
Coverage and test scripts can use this utility to pipe hex fixture text into binary streams. There are no direct unit tests for malformed or separator-heavy input.

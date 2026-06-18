<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/extra/7z2lzma/7z2lzma.bash -->
# sources/compression/xz/extra/7z2lzma/7z2lzma.bash

Purpose: primitive converter from a simple `.7z` archive containing one default-parameter LZMA stream to legacy `.lzma` format.

Important APIs/types/functions: bash `int2bin` writes little-endian integers; `7za l -slt` extracts metadata; `sed` parses packed size, uncompressed size, and dictionary; `dd` copies compressed payload after a 32-byte archive header.

Control flow: validate two arguments, enable `pipefail`, collect 7z metadata, reject multiple blocks, parse sizes/method, write `.lzma` properties/dictionary/uncompressed-size header, then append compressed bytes from the archive.

State and persistence: writes the output file incrementally and may leave a corrupt/partial file on failure.

Dependencies and integration: depends on bash, GNU-ish tools, `7za`/p7zip, and assumptions about 7z layout.

Risks: explicitly does not verify CRC32 and assumes default lc/lp/pb. Archive parsing and fixed 32-byte skip are fragile; success does not guarantee valid output.

Test signals: decompress original `.7z` and generated `.lzma`, compare raw output byte-for-byte, and test rejection of multi-block archives.
<!-- END_FILE_RESEARCH: sources/compression/xz/extra/7z2lzma/7z2lzma.bash -->

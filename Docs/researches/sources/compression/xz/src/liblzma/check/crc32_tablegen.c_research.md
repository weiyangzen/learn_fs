# sources/compression/xz/src/liblzma/check/crc32_tablegen.c

Purpose: build/developer utility that generates `crc32_table_le.h`, `crc32_table_be.h`, and optionally `lz_encoder_hash_table.h` from the CRC32 polynomial.

Important APIs/types/functions: static `crc32_table[8][256]`, `init_crc32_table()`, `print_crc32_table()`, `print_lz_table()`, and `main()`. Build defines select `WORDS_BIGENDIAN` for byte-swapped output or `LZ_HASH_TABLE` for the LZ hash table.

Control flow: `main()` initializes all eight slices. For slice zero each byte is folded through eight right-shift/XOR polynomial steps; later slices start from the previous slice output and repeat the fold. Big-endian builds byte-swap all constants. The print routines emit SPDX text split across string literals, generated-file comments, and formatted hexadecimal constants.

State and persistence: transient generator state only. Persistent effects are the generated headers that are committed or included in the source tree.

Dependencies/integration: includes `tuklib_integer.h` for fixed-width integer helpers, byte swapping, and `PRIX32`. The generated tables are consumed by fast CRC and LZ hash code.

Risks: generator flags must match the target file; using little-endian output in a big-endian table or vice versa causes silent checksum failures. Output formatting is part of the checked-in artifact, so changing it creates large diffs.

Test signals: compare regenerated files to the checked-in headers and run known CRC32 vectors. The LZ hash-table mode should be verified against `src/liblzma/lz/lz_encoder_hash_table.h`.

# sources/compression/xz/src/liblzma/check/crc64_tablegen.c

Purpose: generator utility for the CRC64 fast lookup headers, producing little-endian or big-endian `lzma_crc64_table[4][256]` definitions.

Important APIs/types/functions: static `crc64_table[4][256]`, exported-to-file-scope `init_crc64_table()`, static `print_crc64_table()`, and `main()`.

Control flow: initialization loops over four slices and all byte values. Slice zero starts from the byte value; later slices start from the previous slice output. Each is folded eight times with reversed ECMA-182 polynomial `0xC96C5795D7870F42`. Big-endian generation byte-swaps every constant before printing. `main()` initializes and prints the table.

State and persistence: only transient generator state. Persistent output is the generated checked-in table header.

Dependencies/integration: includes `stdio.h` and `tuklib_integer.h` for `uint64_t`, byte swap helpers, and formatting macros. Its output is consumed by `crc64_fast.c`.

Risks: generator output is architecture-flag sensitive; invoking it with the wrong `WORDS_BIGENDIAN` setting produces a syntactically valid but incorrect header. Any polynomial change would require synchronized updates to small, fast, CLMUL, and assembly paths.

Test signals: regenerate headers and compare with source, run CRC64 vectors, and verify that little- and big-endian generated outputs differ only as expected by byte swapping.

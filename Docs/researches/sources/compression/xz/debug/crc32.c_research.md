<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/crc32.c -->
# sources/compression/xz/debug/crc32.c

Purpose: tiny stdin-to-stdout tool that computes liblzma CRC32 over input and prints the resulting value as four little-endian hex bytes.

Important APIs/types/functions: `main` reads `stdin` in `BUFSIZ` chunks and calls `lzma_crc32(buf, size, crc)`. It uses `uint32_t`, `uint8_t`, `PRIX32`, and stdio.

Control flow: initialize CRC to zero, repeatedly `fread`, update CRC even for the last partial read, stop on EOF or read error, then print low-to-high bytes.

State and persistence: state is process-local CRC accumulator and buffer; no files are opened beyond standard streams.

Dependencies and integration: includes `sysdefs.h` for portability and `lzma.h` for CRC API. Used as an ad hoc debugging/test utility for expected CRC values.

Risks: read errors only stop the loop; they do not change the exit status or report diagnostics. Output is not the conventional big-endian CRC string, intentionally favoring hex-editor workflows.

Test signals: compare output against `xz --check=crc32` metadata or an independent CRC32 implementation; pipe known byte sequences through the tool.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/crc32.c -->

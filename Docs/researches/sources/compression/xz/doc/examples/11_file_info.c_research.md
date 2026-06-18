<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/11_file_info.c -->
# sources/compression/xz/doc/examples/11_file_info.c

Purpose: documented sample for reading `.xz` index information and printing uncompressed sizes without full decompression.

Important APIs/types/functions: `print_file_size`, `lzma_file_info_decoder`, `lzma_code`, `LZMA_SEEK_NEEDED`, `strm->seek_pos`, `lzma_index_uncompressed_size`, and `lzma_index_end`.

Control flow: determine input file size with `fseek`/`ftell`, initialize file-info decoder, feed buffers until liblzma asks for seeks or returns stream end, then print decoded uncompressed size and filename.

State and persistence: stream object is reused across files; `lzma_index` is allocated per successful file and freed after reporting.

Dependencies and integration: demonstrates the random-access file-info decoder and caller-managed seeking.

Risks: if `fopen` fails, `main` still calls `print_file_size` with `NULL`, which would crash; sample code needs a `continue`. `ftell`/`long` is not large-file-safe on 32-bit systems, as the comments note.

Test signals: run on valid multi-stream `.xz`, corrupt headers, unsupported options, and failed open paths; validate reported size against `xz --list`.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/11_file_info.c -->

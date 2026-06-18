<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/02_decompress.c -->
# sources/compression/xz/doc/examples/02_decompress.c

Purpose: documented sample for decompressing one or more `.xz` files to stdout.

Important APIs/types/functions: `init_decoder`, `decompress`, `lzma_stream_decoder`, `LZMA_CONCATENATED`, `lzma_code`, `LZMA_FINISH`, and error handling for `LZMA_FORMAT_ERROR`, `OPTIONS_ERROR`, `DATA_ERROR`, and `BUF_ERROR`.

Control flow: loop over filename arguments, reinitialize the decoder for each file using the same stream object, read file data, call `lzma_code`, write decompressed output, and report per-file errors while continuing to later files when possible.

State and persistence: decoder state is reused across files and freed once at the end; output concatenates decompressed inputs.

Dependencies and integration: demonstrates the recommended `LZMA_CONCATENATED` flag for normal `.xz` files.

Risks: memory limit is `UINT64_MAX`, so malicious inputs can request large decoder memory. It targets clarity over sandboxing or robust CLI behavior.

Test signals: run on valid, concatenated, corrupt, truncated, and non-xz files and check diagnostics/exit status.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/02_decompress.c -->

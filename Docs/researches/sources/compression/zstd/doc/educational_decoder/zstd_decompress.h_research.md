# sources/compression/zstd/doc/educational_decoder/zstd_decompress.h

Purpose: public header for the educational decoder. It exposes a small API for whole-buffer decompression, optional parsed-dictionary decompression, decompressed-size discovery, and dictionary lifecycle management.

Important APIs/types: opaque `dictionary_t`; `ZSTD_decompress(dst, dst_len, src, src_len)`; `ZSTD_decompress_with_dict(dst, dst_len, src, src_len, parsed_dict)`; `ZSTD_get_decompressed_size(src, src_len)`; `create_dictionary()`; `parse_dictionary(dict, src, src_len)`; and `free_dictionary(dict)`.

Control flow/integration: callers create or parse dictionaries separately, allocate an output buffer large enough for the reconstructed frame, and call the decompression function. The implementation assumes a single frame and returns bytes written. The harness uses `ZSTD_get_decompressed_size()` first, then dictionary creation/parsing, then `ZSTD_decompress_with_dict()`.

State and persistence: the header hides dictionary internals, so table/content ownership is controlled by `create_dictionary` and `free_dictionary`. It does not define any global state or file persistence.

Dependencies: only includes `<stddef.h>` for `size_t`. It is intentionally independent of the production `zstd.h` API despite similar names.

Risks: no include guard is present in this header, so repeated inclusion could redeclare types/functions in unusual compile units. The API name overlaps production zstd symbols, so linking this educational decoder with libzstd can create symbol conflicts. Error behavior is not visible from the header: implementation exits instead of returning error codes.

Test signals: compile with multiple C files including the header, call dictionary and non-dictionary paths, verify returned decompressed sizes, and ensure consumers do not link both educational and production `ZSTD_decompress` symbols unintentionally.

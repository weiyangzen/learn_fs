<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/xpress_decompress.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/xpress_decompress.c

Purpose: implements the Huffman variant of XPRESS decompression used by NTFS system-compressed files.

Important APIs and functions: public functions are `xpress_allocate_decompressor`, `xpress_decompress`, and `xpress_free_decompressor`. `struct xpress_decompressor` stores one Huffman decode table, 512 symbol lengths, and working space for `make_huffman_decode_table`.

Control flow: decompression first reads 256 bytes of packed 4-bit codeword lengths for 512 symbols, builds the Huffman table, initializes a bitstream after the length header, and decodes until the caller-supplied output size is filled. Symbols below 256 emit literal bytes. Symbols 256 and above encode an LZ match: low bits supply a length header, high bits supply `log2_offset`, extra offset bits are read from the bitstream, extended length bytes/u16 may be consumed, bounds are checked, and `lz_copy` copies from prior output.

State and persistence behavior: no persistent state exists. The decompressor context is reusable scratch memory. The output size is authoritative; the function succeeds only after exactly filling it and returns `-1` for malformed data.

Dependencies and integration points: uses shared Huffman, bitstream, and LZ-copy helpers from `decompress_common.h` and is exposed through `lib.h`. Higher NTFS compression code chooses XPRESS for the relevant system-compression format.

Risks: XPRESS input has compact headers, so truncated headers, invalid code-length sets, length extensions, and offset calculations are the main validation points. The code relies on caller-provided output size and validates only match bounds, not trailing compressed-data consumption. Return values are format-style `-1`, so callers must translate or handle consistently.

Test signals: known XPRESS-Huffman samples, literals-only and matches-only streams, long length extension paths, maximum `log2_offset`, offset-before-start rejection, output-overrun rejection, truncated length table, invalid Huffman lengths, and fuzzing with sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/xpress_decompress.c -->

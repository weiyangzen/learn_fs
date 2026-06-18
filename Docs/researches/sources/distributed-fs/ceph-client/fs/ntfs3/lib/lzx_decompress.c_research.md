<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/lzx_decompress.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/lzx_decompress.c

Purpose: implements an LZX decompressor for NTFS system-compressed files, specialized for the 32 KiB window size used by this driver. It decodes verbatim, aligned-offset, and uncompressed LZX blocks and applies the x86 E8 postprocessing transform.

Important APIs and functions: public functions are `lzx_allocate_decompressor`, `lzx_decompress`, and `lzx_free_decompressor`. Internal helpers include `lzx_postprocess`, `undo_e8_translation`, Huffman readers for pre/main/length/aligned codes, `lzx_read_codeword_lens`, `lzx_read_block_header`, and `lzx_decompress_block`. `struct lzx_decompressor` holds decode tables, length arrays, precode/aligned-code state, and working space.

Control flow: `lzx_decompress` initializes the bitstream, clears delta-coded main and length code lengths, and loops over blocks until the expected output size is produced. Each block header selects block type and size; compressed blocks rebuild Huffman tables and decode literals or matches; uncompressed blocks align the bitstream, read recent offsets, and copy bytes directly. Match symbols decode length headers, optional length symbols, repeat or explicit offsets, aligned low bits when needed, recent-offset queue updates, bound checks, and `lz_copy`. After output completion, E8 postprocessing runs if literals indicate possible `0xe8` bytes or if an uncompressed block was present.

State and persistence behavior: all decompression state is in the caller-provided context, stack recent-offset queue, input bitstream, and output buffer. Codeword lengths persist across LZX blocks within one compressed buffer because the format delta-encodes them. There is no filesystem persistence in this file.

Dependencies and integration points: uses `decompress_common.h` bitstream, Huffman, and LZ-copy helpers plus prototypes from `lib.h`. It is used by NTFS3 compressed-read support for WOF/system compression.

Risks: malformed streams can target many edge cases: invalid block types, bad Huffman tables, zero recent offsets, block sizes larger than remaining output, offset slots beyond tables, matches before output start, and codeword-length RLE overruns. E8 postprocessing temporarily overwrites the last six output bytes and must restore them. The implementation assumes fixed LZX constants for system compression rather than arbitrary cabinet-style windows.

Test signals: known LZX system-compressed files, blocks of each type, aligned offset blocks with low-bit Huffman decoding, repeat-offset behavior, E8 translation cases near buffer tails and small buffers, invalid/truncated block headers, invalid offsets/lengths, and fuzzing with expected `-1` failures rather than memory errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/lzx_decompress.c -->

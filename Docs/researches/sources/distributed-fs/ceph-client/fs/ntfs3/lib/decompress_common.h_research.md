<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.h -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.h

Purpose: defines shared inline primitives for XPRESS and LZX decompression: endian-safe bitstream reading, Huffman symbol decoding, unaligned word helpers, byte repetition, and LZ77 match copying.

Important APIs and types: defines `struct input_bitstream`, `init_input_bitstream`, `bitstream_ensure_bits`, peek/remove/pop/read bit helpers, literal byte/u16/u32/bytes readers, `bitstream_align`, `read_huffsym`, and `lz_copy`. It declares `make_huffman_decode_table`. `FAST_UNALIGNED_ACCESS` enables word-at-a-time copying on architectures where it is expected to be safe and fast.

Control flow: decompressor callers initialize a bitstream over compressed bytes, ensure enough bits before peeking/removing them, read Huffman symbols through a direct table lookup or slow tree traversal, and copy LZ matches from already-written output via `lz_copy`. `lz_copy` takes fast paths for non-overlapping word copies and offset-one run filling, otherwise falls back to bytewise overlapping copy.

State and persistence behavior: state is per-bitstream and per-output-buffer only. Missing literal bytes or integers return zero in several helpers, while higher-level decompressor validation is responsible for rejecting invalid streams. `lz_copy` assumes the caller has already validated match bounds and does not persist anything.

Dependencies and integration points: uses Linux compiler/type/string/slab/unaligned helpers and is included by `xpress_decompress.c`, `lzx_decompress.c`, and `decompress_common.c`. It is part of NTFS system-compression support and indirectly participates in compressed file reads.

Risks: bit-buffer semantics are specialized: bits are read from little-endian 16-bit units but ordered high-to-low in `bitbuf`. Callers can overrun logical input if they do not separately validate compressed-stream structure. `lz_copy` can intentionally overcopy up to a word within the output buffer slack, so its bound checks and `bufend` contract are critical. Architecture-specific unaligned access assumptions need build coverage.

Test signals: decode known XPRESS/LZX data on x86 and non-fast-unaligned architectures, fuzz truncated bitstreams, validate overlapping copies for offsets 1 through word size, verify output-tail overcopy never crosses `bufend`, and compare against a reference decompressor for random valid streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.h -->

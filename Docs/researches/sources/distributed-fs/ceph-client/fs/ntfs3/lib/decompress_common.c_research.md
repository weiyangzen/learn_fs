<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.c

Purpose: provides the shared canonical Huffman decode-table builder used by the NTFS3 XPRESS and LZX decompressors. It translates arrays of codeword lengths into compact direct-lookup and binary-tree tables consumed by `read_huffsym()`.

Important APIs and functions: the file implements `make_huffman_decode_table(u16 decode_table[], u32 num_syms, u32 table_bits, const u8 lens[], u32 max_codeword_len, u16 working_space[])`. The table format stores direct entries as `(codeword_len << 11) | symbol`; entries with high bits `0xC000` point to binary-tree child nodes for codewords longer than `table_bits`.

Control flow: the builder counts symbols per codeword length, verifies the prefix code is neither oversubscribed nor incomplete except for the explicitly allowed empty code, sorts symbols by canonical order using offset buckets, fills direct lookup entries for codewords up to `table_bits`, then allocates tree nodes for longer codewords. Empty codes zero the direct table so accidental decode attempts do not read uninitialized entries.

State and persistence behavior: no persistent state is stored. The caller owns `decode_table` and `working_space`, usually inside a reusable decompressor object. The function mutates only those buffers and returns `0` for valid tables or `-1` for invalid code-length sets.

Dependencies and integration points: included by XPRESS and LZX decompressor code under `fs/ntfs3/lib`. It relies on kernel `memset` and integer types, and its output is interpreted by inline bitstream/Huffman routines in `decompress_common.h`.

Risks: bounds are contractual: callers must supply a large enough decode table and working space, and all lengths must be <= `max_codeword_len`. A bad prefix-code validation bug can turn malformed compressed input into out-of-bounds table traversal. The long-codeword tree encoding shares the `u16` value space with symbols and length-tagged entries, so constants must stay consistent with symbol limits.

Test signals: valid XPRESS and LZX compressed samples, empty-code tables, oversubscribed and incomplete code-length arrays, maximum-length codewords that force tree allocation, short-code fast path coverage, and fuzzed compressed streams under KASAN/UBSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.c -->

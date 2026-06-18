# sources/distributed-fs/ceph-client/lib/inflate.c

## Purpose
`inflate.c` is the kernel boot-time gzip/deflate decompressor derived from early gzip inflate code. It parses a gzip wrapper, inflates deflate blocks using stored, fixed-Huffman, and dynamic-Huffman modes, maintains CRC32, and validates the gzip trailer.

## Important APIs, Types, and Functions
The key type is `struct huft`, a Huffman decode table entry with operation bits, consumed bits, and either a literal/base value or next-table pointer. Core routines are `huft_build()`, `huft_free()`, `inflate_codes()`, `inflate_stored()`, `inflate_fixed()`, `inflate_dynamic()`, `inflate_block()`, `inflate()`, `makecrc()`, and `gunzip()`. Static tables include literal length bases/extras, distance bases/extras, bit-length-code order, and bit masks. The file expects environment-provided gzip/unzip symbols such as `get_byte()`, `flush_window()`, `window`, `outcnt`, `bytes_out`, `inptr`, `free_mem_ptr`, `free_mem_end_ptr`, `memzero()`, and `error()`.

## Control Flow, State, and Persistence
`gunzip()` reads and validates gzip magic, method, flags, optional extra/name/comment fields, then calls `inflate()`. `inflate()` initializes the sliding window and bit buffer, loops over deflate blocks until the last-block bit, services an optional decompression watchdog, backs up excess byte lookahead, flushes output, and returns an error code. Block dispatch in `inflate_block()` reads the block type and calls stored, fixed, or dynamic handlers. Dynamic blocks read code-length metadata, build an intermediate bit-length tree, expand literal/distance lengths, build actual Huffman tables, then decode with `inflate_codes()`. Global/static state includes the bit buffer `bb`, bit count `bk`, Huffman allocation counter `hufts`, CRC table, CRC accumulator, and the sliding window position alias `wp`.

## Dependencies and Integration Points
It includes `"gzip.h"` when not built `STATIC`, relies on Linux boot decompressor conventions, and can use either a small bump allocator over `free_mem_ptr` or `kmalloc/kfree` under `NO_INFLATE_MALLOC`. It integrates with architecture decompression code and optional `ARCH_HAS_DECOMP_WDOG`.

## Risks and Test Signals
Risks include malformed Huffman tables, incomplete input underruns, memory exhaustion in table construction, overlapping sliding-window copies, CRC/length trailer mismatches, unsupported gzip flags, and reliance on global decompressor state. Tests should cover valid gzip streams using stored/fixed/dynamic blocks, optional gzip fields, truncated input at every stage, invalid block types, invalid length complements, oversubscribed and incomplete Huffman trees, CRC and length failures, allocator exhaustion, and boot decompressor smoke tests on architectures using this path.

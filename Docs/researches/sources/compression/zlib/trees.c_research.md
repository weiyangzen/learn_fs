# sources/compression/zlib/trees.c

`trees.c` implements deflate-side Huffman coding and block emission. It builds static and dynamic trees, chooses stored/static/dynamic block encodings, emits block headers and symbols, manages the bit buffer, and tallies literal/match frequencies for `deflate.c`.

Internal entry points are `_tr_init()`, `_tr_stored_block()`, `_tr_flush_bits()`, `_tr_align()`, `_tr_flush_block()`, and `_tr_tally()`. Important local routines include `bi_reverse()`, `bi_flush()`, `bi_windup()`, `gen_codes()`, `tr_static_init()`, `init_block()`, `pqdownheap()`, `gen_bitlen()`, `build_tree()`, `scan_tree()`, `send_tree()`, `build_bl_tree()`, `send_all_trees()`, `compress_block()`, and `detect_data_type()`.

Control flow starts with `_tr_init()` attaching descriptors and clearing bit state. `_tr_tally()` records literals/matches and updates frequencies. `_tr_flush_block()` builds trees, computes dynamic/static/stored costs, emits the selected representation, resets the block, and winds up bits for the last block. State lives in `deflate_state`: trees, heap/depth arrays, bit-length counts, symbol buffers, pending output, bit buffer, counters, strategy, level, and debug stats. Static table state comes from `trees.h` or one-time runtime generation.

Dependencies include `deflate.h`, `trees.h`, zutil macros, and RFC 1951 bitstream semantics expected by inflate. Risks are high: bit-order mistakes, heap errors, table drift, pending-buffer overlay, and conditional variants can corrupt output. Test signals include round trips through `example.c`/`minigzip.c`, debug assertions, interoperability with independent decompressors, and regenerated `trees.h` matching the checked-in tables.

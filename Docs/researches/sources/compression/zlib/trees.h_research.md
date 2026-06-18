# sources/compression/zlib/trees.h

`trees.h` is a generated header with precomputed deflate Huffman tables. It avoids runtime generation of static literal/length and distance trees in normal ANSI builds.

It defines `static_ltree`, `static_dtree`, `_dist_code`, `_length_code`, `base_length`, and `base_dist` using internal zlib types. `trees.c` indexes these arrays to map normalized match lengths and distances to deflate code numbers and extra-bit bases.

The file has no executable control flow and no mutable runtime state; its data is compiled into the library. It depends on constants and types already available from `deflate.h` when included by `trees.c`. Risks are table drift or manual edits, since one wrong value can create invalid compressed streams. Test signals are static-block round trips, debug checks in `trees.c`, and clean regeneration via `-DGEN_TREES_H`.

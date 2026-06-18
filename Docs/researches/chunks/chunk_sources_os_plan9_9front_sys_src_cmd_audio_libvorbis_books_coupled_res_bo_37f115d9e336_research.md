# Chunk Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_51.h lines 7053-12273

## Scope

This chunk is within subset A because `Docs/research_subset_a.md` includes `sources/os/plan9/9front`. The covered line range is a generated/static Vorbis residue codebook section from 9front's imported `audio/libvorbis` tree. It contains data declarations only: no executable functions, no macros, and no direct filesystem or kernel logic.

## APIs and Symbols

The public surface visible in this chunk is a set of file-local `static const` arrays and `static const static_codebook` descriptors. These are not exported APIs; they are included by libvorbis setup code elsewhere in the same header/translation unit.

Primary codebook descriptors in this chunk:

- Partial continuation of `_44p6` plus `_44p6_p5_0` at line 7186, `_44p6_p5_1` at 7208, `_44p6_p6_0` at 7241, `_44p6_p6_1` at 7274, `_44p6_p7_0` at 7307, `_44p6_p7_1` at 7340, `_44p6_p7_2` at 7381, `_44p6_p7_3` at 7422, and `_huff_book__44p6_short` at 7437.
- Full `_44p7` family: LFE/long Huffman books and vector quantization books from `_44p7_l0_0` at 7475 through `_huff_book__44p7_short` at 8572.
- Full `_44p8` family: `_44p8_l0_0` at 8610 through `_huff_book__44p8_short` at 9889.
- Full `_44p9` family: `_44p9_l0_0` at 9927 through `_huff_book__44p9_short` at 11382.
- Beginning and most of `_44pn1` family: `_44pn1_l0_0` at 11420 through `_huff_book__44pn1_short` at 12266.

Each VQ book follows the same pattern: `_vq_quantlist__...` arrays hold quantization values, `_vq_lengthlist__...` arrays hold codeword lengths, and `static_codebook` initializers bind dimensions, entry counts, map type, quant metadata, and quant-list pointers. Huffman-only books use `_huff_lengthlist__...` plus `static_codebook` descriptors with map type `0` and `NULL` quant lists.

## Control Flow

There is no local control flow. Runtime behavior is entirely data-driven by libvorbis code that consumes `static_codebook` structures. The effective flow is: higher-level setup tables select a family such as `_44p7`, `_44p8`, `_44p9`, or `_44pn1`; decoder/encoder setup passes the selected book to Vorbis codebook initialization; that layer interprets canonical code lengths and quantization metadata.

## State and Data Model

All state is immutable static storage. VQ descriptors are mostly dimension `5` with `243` or `3125` entries; scalar selector books use dimension `1` with `7` or `25` entries; low-frequency setup books use dimension `2` with `169`, `25`, `9`, or similar entry counts. Several `_44pn1` length lists are sparse and use `0` to mark disabled codebook entries.

## Dependencies

This chunk depends on the `static_codebook` definition, `NULL`, and Vorbis codebook initialization/lookup routines that understand map type `0`, map type `1`, length lists, packed quantization fields, and quant lists. It has no direct dependency on Plan 9 syscalls, filesystems, VFS objects, storage devices, or kernel APIs.

## Cross-Chunk References

- The chunk starts mid-declaration: lines 7053-7185 are the tail of `_vq_lengthlist__44p6_p5_0`, whose declaration begins in the previous chunk. Its `static_codebook _44p6_p5_0` is completed at line 7186.
- Families `_44p6`, `_44p7`, `_44p8`, `_44p9`, and `_44pn1` are likely referenced by aggregate residue book arrays later in this header or companion generated headers.
- `_44pn1` continues only through `_huff_book__44pn1_short` in this range; any later related declarations are in the next chunk.

## Risks and Review Notes

Generated-data integrity is the main risk. A single changed integer can silently alter codec bitstream compatibility or audio quality. Entry counts in `static_codebook` initializers must match corresponding length-list sizes. The `char *` casts discard `const`, following older libvorbis style, and rely on consumers treating static tables as read-only. Sparse `_44pn1` books require consumers to interpret zero length as “unused,” not as a valid code.

## Filesystem Relevance

No filesystem implementation behavior is present in this chunk. Its subset A relevance is repository placement under `sources/os/plan9/9front`; functionally it is user-space audio codec static data.
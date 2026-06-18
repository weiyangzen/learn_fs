# Chunk Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_51.h lines 1-7052

## Scope

- Subset: `Docs/research_subset_a.md`, which includes `sources/os/plan9/9front`.
- File chunk read: `sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_51.h`, lines 1-7052.
- This is an oversized generated/static-data header for Ogg Vorbis 5.1 surround residue codebooks. This chunk report does not create or update the final per-file report.

## APIs And Symbols

- This chunk declares only `static const` data; it exports no functions, macros, or externally linked symbols.
- Symbols have internal linkage because the header defines `static const` objects intended to be included by libvorbis mode templates.
- Primary data type dependency is `static_codebook` from `codebook.h`, with fields for vector dimension, entry count, Huffman length list, map type, quantization parameters, quant list, and allocation flag.
- VQ codebook pattern: `_vq_quantlist__...[]`, `_vq_lengthlist__...[]`, and `_44p*_...` `static_codebook` descriptors.
- Huffman-only pattern: `_huff_lengthlist__...[]` and `_huff_book__...` descriptors with maptype `0` and `NULL` quantlist.

## Data Covered

- Header/license block: lines 1-15 identify this as Xiph.Org OggVorbis source, function "static codebooks for 5.1 surround".
- Complete book families in this chunk: `_44p0_*` through `_44p5_*`, including corresponding long/short/LFE Huffman books.
- Partial `_44p6_*` family:
  - Complete through `_44p6_p4_1`: lines 6313-6977.
  - `_vq_quantlist__44p6_p5_0`: lines 6979-6985 complete.
  - `_vq_lengthlist__44p6_p5_0`: starts at line 6987 and is incomplete at chunk end line 7052.
- The chunk contains 127 complete `static_codebook` definitions before the split and one incomplete array definition at the split boundary.

## Control Flow

- There is no direct runtime control flow in this chunk.
- Runtime use is indirect: `modes/residue_44p51.h` includes this header, its `static_bookblock` tables reference these codebooks, and `vorbis_encode_residue_setup()` installs selected `static_codebook` pointers into encoder setup state.

## State

- State is immutable compile-time data: codeword length arrays, quantization arrays, and `static_codebook` descriptors.
- Downstream mutable state is outside this file: residue `booklist`, `groupbook`, `secondstages`, and `codec_setup_info.book_param`.
- `allocedp` is initialized to `0`, indicating static backing arrays.

## Dependencies

- Requires `static_codebook` and `NULL` definitions from the surrounding libvorbis include chain.
- Consumed by `sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44p51.h`.
- Interpreted by libvorbis internals in `codebook.c`, `sharedbook.c`, and `vorbisenc.c`.

## Risks And Invariants

- Generated-data integrity is the main risk. Each `entries` count must match its `lengthlist`, and maptype 1 quant lists must match implied quant dimensions.
- Common dimensions/entry counts include `1x7`, `1x25`, `2x4`, `2x9`, `2x25`, `2x49`, `2x64`, `2x169`, `5x243`, and `5x3125`.
- Sparse books intentionally use many zero code lengths.
- Casts from const arrays to non-const `static_codebook` fields mirror libvorbis’ structure definition; consumers must treat the arrays as read-only.
- Chunk boundary risk: line 7052 cuts through `_vq_lengthlist__44p6_p5_0`.

## Cross-Chunk References

- Next chunk must continue `_vq_lengthlist__44p6_p5_0` from line 7053, close it, and define `_44p6_p5_0`.
- Later `_44p6` symbols expected by `residue_44p51.h` include `_44p6_p5_1`, `_44p6_p6_0`, `_44p6_p6_1`, `_44p6_p7_0`, `_44p6_p7_1`, `_44p6_p7_2`, `_44p6_p7_3`, and `_huff_book__44p6_short`.
- Later chunks also contain `_44p7`, `_44p8`, `_44p9`, and `_44pn1` families referenced by the same residue template header.
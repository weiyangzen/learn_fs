# Chunk Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_stereo.h lines 13304-15782

## Scope

This report covers only `sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_stereo.h` lines 13304-15782 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declaration at the start of the chunk, the file end, the `static_codebook` type, and downstream residue-template references. The chunk is generated/static Ogg Vorbis residue codebook data, not executable OS/filesystem logic.

## APIs And Exported Data

The declarations are all `static const` header-scope objects. They are not exported linker symbols, but because `res_books_stereo.h` is included by `modes/residue_44.h`, they become compile-unit-local inputs to the 44.1 kHz stereo residue templates.

This chunk contributes these codebook families:

- `_44c1_sm_*`: completes the tail of `_vq_lengthlist__44c1_sm_p1_0` that began before this chunk, then defines `_44c1_sm_p1_0` and the short-mask VQ books `_44c1_sm_p2_0` through `_44c1_sm_p8_2`, plus `_huff_book__44c1_sm_short`.
- `_44cn1_s_*`: defines the uncoupled/noise-class stereo long/short huffman books and VQ books `_44cn1_s_p1_0` through `_44cn1_s_p8_2`.
- `_44cn1_sm_*`: defines the stereo-mask variant long/short huffman books and VQ books `_44cn1_sm_p1_0` through `_44cn1_sm_p8_2`.

## Control Flow

There are no functions, branches, loops, synchronization points, allocation sites, or runtime initialization side effects in this chunk. Runtime behavior is indirect through libvorbis codebook packing, encode/decode initialization, and maptype-1 unquantization.

## State And Dependencies

All state in the chunk is immutable compiled data. The large zero-heavy `char` lengthlists encode sparse canonical codeword lengths; nonzero entries define usable codewords and zeros mark unused entries. Quantlists are small symmetric integer columns interpreted by libvorbis maptype-1 unquantization.

Direct dependencies include `static_codebook` from `libvorbis/codebook.h`, `NULL`, `sharedbook.c`, `codebook.c`, and `modes/residue_44.h`, which references these symbols in `_resbook_44sm_1`, `_resbook_44s_n1`, `_resbook_44sm_n1`, and `_res_44s_*` templates.

## Risks

The main risk is data integrity. A single changed integer can alter entropy coding, quantized residue vectors, or the set of unused entries, causing incompatible Vorbis setup packets or degraded/corrupt audio.

Array length consistency is also critical. For each `static_codebook`, `entries` must match the corresponding lengthlist size, and maptype-1 quantlist length must match `_book_maptype1_quantvals(entries, dim)`. The header also casts const arrays to non-const struct fields; consumers should still treat this data as read-only.

## Cross-Chunk References

The first line in this chunk is inside `_vq_lengthlist__44c1_sm_p1_0`, whose declaration and earlier entries begin before line 13304. The previous chunk must be merged to reconstruct `_44c1_sm_p1_0` fully.

This chunk reaches the physical end of `res_books_stereo.h` at line 15782. There is no next chunk for this file.
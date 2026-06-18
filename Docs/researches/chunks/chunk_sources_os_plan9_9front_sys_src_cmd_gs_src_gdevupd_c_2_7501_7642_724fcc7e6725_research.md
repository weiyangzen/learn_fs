# Chunk Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevupd.c lines 7501-7642

## Scope

This report covers only `sources/os/plan9/9front/sys/src/cmd/gs/src/gdevupd.c` lines 7501-7642 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context to identify the reverse-pixel setup routine, the `upd_pxlget` function-pointer API, and the rendering/compression consumers. The chunk is Ghostscript UPD printer-driver pixel-reader code embedded in 9front's vendored `gs` tree.

## APIs

The chunk defines private `uint32_t name(upd_p upd)` pixel getter routines selected through `upd->pxlget` and invoked via the `upd_pxlget(UPD)` macro:

- `upd_pxlget1r1` through `upd_pxlget1r8`: reverse readers for 1-bit pixels packed most-significant-bit first in each source byte. Each function returns `0` or `1`, then rewires `upd->pxlget` to the previous bit-position function for the next pixel.
- `upd_pxlget2r1` through `upd_pxlget2r4`: reverse readers for 2-bit packed pixels. They mask and shift `0xC0`, `0x30`, `0x0C`, or `0x03` and rotate the function pointer backward through the four pixel slots.
- `upd_pxlget4r1` and `upd_pxlget4r2`: reverse readers for 4-bit packed pixels. They return the high or low nibble and toggle the getter state between the two nibbles.
- `upd_pxlget8r`, `upd_pxlget16r`, `upd_pxlget24r`, `upd_pxlget32r`: reverse readers for byte-aligned 8/16/24/32-bit pixels. They assemble a `uint32_t` from `upd->pxlptr` while walking the byte pointer backward.

All routines depend on the local `upd_proc_pxlget` signature macro and mutate fields of `struct upd_s`: `byte *pxlptr` and `uint32_t (*pxlget)(upd_p)`.

## Control Flow

The control flow is a hand-written finite-state machine encoded as self-modifying function-pointer state. For sub-byte depths, each call both returns the current packed pixel and installs the getter for the next reverse pixel position.

The decrement of `upd->pxlptr` happens only when crossing a source-byte boundary: `upd_pxlget1r1`, `upd_pxlget2r1`, and `upd_pxlget4r1` consume the high-order slot and then move to the preceding byte. The remaining sub-byte functions inspect the current byte without moving the pointer.

For 8-bit and wider depths, every pixel is byte-aligned, so each function decrements `pxlptr` for every source byte consumed. Multi-byte reverse readers assemble the returned integer little-endian relative to the backward walk: the byte at the current pointer becomes the low-order byte, then earlier addresses are shifted by 8, 16, and 24 bits.

Adjacent setup in `upd_pxlrev` positions `upd->pxlptr` at the last printable/source pixel and selects the correct initial function based on `IA_COLOR_INFO.data[1]` depth and bit offset. Consumers in the Floyd-Steinberg render paths call `upd_pxlget(upd)` repeatedly while trimming whitespace and processing pixels.

## State And Dependencies

This chunk has no global storage of its own, no allocation, no I/O, and no external library calls. Its runtime state is entirely carried in the mutable `upd` object:

- `upd->pxlptr` must already point into `upd->gsscan` at the byte and byte-offset chosen for a reverse scan.
- `upd->pxlget` is both the dispatch target and the continuation state for the next pixel.
- `upd->int_a[IA_COLOR_INFO].data[1]`, `upd->pwidth`, `upd->gswidth`, and `upd->gsscan` are consumed by the adjacent initializer, not directly by this chunk.

The chunk depends on C integer promotion behavior for `byte` values, explicit casts to `uint32_t` before multi-byte shifts, and the invariant that caller-visible scan widths keep `pxlptr` within the raster buffer while walking backward.

## Risks

Pointer safety is the main risk. None of these getters check bounds or null pointers; `upd_pxlrev` handles a null `gsscan`, but after initialization the render loops assume the selected width and source buffer are consistent. An off-by-one in width, depth, or initial offset would under-read before `gsscan`.

The sub-byte readers are fragile because pointer movement is tied to specific state functions. Changing the state transitions or moving the `pxlptr--` to the wrong function would duplicate or skip packed pixels. This also affects whitespace-trimming code that snapshots both `upd->pxlget` and `upd->pxlptr` to roll back to the last non-white position.

The 16/24/32-bit reverse readers intentionally return a value with the rightmost scanned byte in the low-order bits. Any caller or future maintainer expecting the same byte order as the forward readers would misinterpret color component extraction.

## Cross-Chunk References

The previous chunk contains the declarations for these functions, the forward pixel readers, `upd_pxlgetnix`, and `upd_pxlrev`. In particular, lines 7437-7499 initialize this chunk's reverse-reader state machine by computing the initial byte/bit offset and, for 16/24/32-bit depths, advancing `pxlptr` to the last byte of the pixel before the first reverse read.

Earlier render/compression code around `upd_fscomp` and its 4-component variant uses `upd_pxlfwd`, `upd_pxlrev`, and `upd_pxlget` to trim leading/trailing white pixels and then read one source pixel per output step. Later chunks are not needed for this chunk's local behavior; this section ends at `upd_pxlget32r`.
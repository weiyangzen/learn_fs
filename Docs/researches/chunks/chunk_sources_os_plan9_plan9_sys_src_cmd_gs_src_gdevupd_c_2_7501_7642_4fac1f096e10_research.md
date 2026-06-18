# Chunk Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevupd.c lines 7501-7642

## Scope

This chunk is the reverse-direction half of Ghostscript `upd` pixel-reader helpers in Plan 9's vendored `gs` tree, within `Docs/research_subset_a.md` Plan 9 OS source scope. It defines private `uint32_t` readers for 1, 2, 4, 8, 16, 24, and 32 bits per source pixel when the raster stream is consumed right-to-left/backward.

## APIs and Entry Points

- `upd_pxlget1r1()` through `upd_pxlget1r8()` read one 1-bit pixel from bit masks `0x80` through `0x01`, returning `0` or `1`.
- `upd_pxlget2r1()` through `upd_pxlget2r4()` read one 2-bit pixel from masks `0xC0`, `0x30`, `0x0C`, and `0x03`, returning the field shifted to bit 0 where needed.
- `upd_pxlget4r1()` and `upd_pxlget4r2()` read high and low nibbles.
- `upd_pxlget8r()`, `upd_pxlget16r()`, `upd_pxlget24r()`, and `upd_pxlget32r()` read whole-byte pixels and combine multibyte color indexes into `uint32_t`.
- These helpers are called indirectly through `upd_pxlget(UPD)`, which expands to the `upd->pxlget` function pointer.

## Control Flow

Each sub-byte reader is a tiny state machine: it returns the current bit field and rewrites `upd->pxlget` to the helper that should read the next pixel position. In reverse mode, the first sub-byte helper for a byte decrements `upd->pxlptr` after reading that byte, then later helpers continue using the decremented pointer until the cycle wraps to the next previous byte.

For 1-bit pixels, the cycle moves `1r8 -> 1r7 -> ... -> 1r1 -> 1r8`, with `1r1` consuming the high bit and post-decrementing the byte pointer. For 2-bit pixels, `2r4 -> 2r3 -> 2r2 -> 2r1 -> 2r4`, with `2r1` post-decrementing. For 4-bit pixels, `4r2 -> 4r1 -> 4r2`, with `4r1` post-decrementing.

Whole-byte readers do not change `upd->pxlget`; they only step `upd->pxlptr` backward by the pixel width. Multibyte reverse readers assemble values little-endian from the reverse traversal point: 16-bit reads current byte as low 8 bits and previous byte as high 8 bits, 24-bit reads low/mid/high bytes, and 32-bit reads four bytes into bits 0, 8, 16, and 24.

## State, Dependencies, Risks

State touched is limited to `upd->pxlptr` and, for sub-byte formats, `upd->pxlget`. Both fields live in `struct upd_s`; `pxlptr` is the current source cursor and `pxlget` is the active pixel-reader callback.

The immediate dependency is `upd_pxlrev()` immediately before this chunk, which initializes `upd->pxlptr` from `upd->gsscan`, positions it at the last pixel for the active width/depth, and selects the correct reverse helper based on `IA_COLOR_INFO.data[1]`. Earlier prototypes declare all helpers through `upd_proc_pxlget(name)`, and rendering paths call them through `upd_pxlget(upd)` while scanning or trimming white pixels.

The main risks are pointer-boundary correctness and state-machine alignment. These helpers assume `upd_pxlrev()` has selected an entry function matching the ending bit offset and that callers will not read past the beginning of `gsscan`. A bad depth, width, or offset would make the post-decrement operations underflow the source scanline. Because the function pointer is mutated on every sub-byte read, any caller that snapshots/restores `upd->pxlget` must also keep `upd->pxlptr` synchronized; nearby render code does this while skipping leading whitespace.

## Cross-Chunk References

- Lines 7207-7253 contain the private prototypes for all forward and reverse pixel readers.
- Lines 7255-7424 define the forward-direction setup and forward pixel readers mirrored by this chunk.
- Lines 7432-7499 define the dummy reader and `upd_pxlrev()`, which dispatches into this chunk.
- Lines 3608-3692 and 3998-4075 show render paths selecting forward/reverse readers, trimming whitespace, restoring `pxlget`/`pxlptr`, and consuming pixels through `upd_pxlget(upd)`.
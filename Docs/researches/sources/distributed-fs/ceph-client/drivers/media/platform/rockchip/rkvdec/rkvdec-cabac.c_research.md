# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-cabac.c

## Purpose
This file is a data-only CABAC initialization provider for Rockchip's RKVDEC stateless H.264 and HEVC decoder backends. It defines the H.264 `(m, n)` context initialization table and the HEVC hardware CABAC byte table copied into per-context coherent auxiliary buffers before decoding starts.

## Important APIs, Types, And Data
- `CABAC_ENTRY(ctxidx, ...)` expands one H.264 context index into four initialization-class entries: cabac_init_idc 0, 1, 2, and intra.
- `const s8 rkvdec_h264_cabac_table[4][464][2]` is the exported H.264 table. It is organized by initialization set, context index, then `{m, n}` pair.
- `const u8 rkvdec_hevc_cabac_table[RKV_HEVC_CABAC_TABLE_SIZE]` is the exported HEVC table. The declared size comes from `rkvdec-cabac.h` and is expected to match the hardware table layout exactly.

## Control Flow
There is no executable control flow. Consumers copy the tables into DMA-visible private tables during codec `start()`: `rkvdec-h264.c` copies the H.264 table, while `rkvdec-hevc.c` and VDPU-specific HEVC backends copy the HEVC table. Hardware receives the coherent table base through `regs->common.cabactbl_base`.

## State And Persistence
The file contributes immutable global kernel data. Runtime persistence is per decoder context only after the backend copies the table into its coherent auxiliary allocation. No mutable state is stored in this file.

## Dependencies And Integration Points
The file includes only `rkvdec-cabac.h`. It is tightly coupled to hardware ABI sizes in the H.264/HEVC private table definitions and to the CABAC base register programmed by the backend.

## Risks
- The HEVC byte table has no local compile-time initializer-count assertion beyond the declared array size; accidental short initializers would zero-fill.
- H.264 context data is manually transcribed from spec tables plus undocumented later indices, so mistakes would appear as decode corruption.
- The layout is hardware ABI and should only change with conformance coverage.

## Test Signals
Successful H.264 and HEVC stateless decode across CABAC-coded bitstreams, including H.264 cabac_init_idc variants and HEVC supported bit depths. Failures usually appear as block corruption, decode timeout, or mismatch against software-decoded reference frames.

# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-cabac.h

## Purpose
This header declares the shared CABAC tables used by the Rockchip RKVDEC H.264 and HEVC backends. It gives codec implementations a single ABI for copying entropy-decoder initialization data into hardware-visible private tables.

## Important APIs, Types, And Data
- `RKV_HEVC_CABAC_TABLE_SIZE` is fixed at `27456` bytes and drives both the exported HEVC table declaration and backend private-table member sizes.
- `extern const s8 rkvdec_h264_cabac_table[4][464][2]` exposes H.264 CABAC `(m, n)` initialization pairs.
- `extern const u8 rkvdec_hevc_cabac_table[RKV_HEVC_CABAC_TABLE_SIZE]` exposes the raw HEVC hardware initialization table.

## Control Flow
The header has no runtime flow. It is included by `rkvdec-cabac.c` for definitions and by codec backends that need the table symbols.

## State And Persistence
All declared objects are immutable `const` data owned by `rkvdec-cabac.c`. Runtime copies live in per-codec coherent auxiliary buffers allocated by backend `start()` callbacks.

## Dependencies And Integration Points
The header depends on `<linux/types.h>` for `s8` and `u8`. It integrates with H.264, HEVC, VDPU381, and VDPU383 backends that populate their `cabac_table` fields and program `cabactbl_base`.

## Risks
- `RKV_HEVC_CABAC_TABLE_SIZE` is a hardware contract. If a backend private table or source initializer diverges from this value, hardware reads may address wrong data.
- The header provides declarations only; it does not enforce table semantic correctness.

## Test Signals
Build coverage catches symbol and type mismatches. Runtime decode testing with HEVC and H.264 CABAC streams validates that copied table sizes and hardware offsets remain correct.

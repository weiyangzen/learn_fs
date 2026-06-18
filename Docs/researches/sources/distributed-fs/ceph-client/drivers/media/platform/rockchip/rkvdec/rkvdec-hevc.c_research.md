# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc.c

## Purpose
This file implements the base Rockchip RKVDEC HEVC stateless decoder backend. It packs HEVC SPS/PPS and per-slice RPS data into coherent hardware packets, programs RKVDEC registers, and exposes `rkvdec_hevc_fmt_ops`.

## Important APIs, Types, And Functions
- `struct rkvdec_hevc_priv_tbl` contains the HEVC CABAC table, scaling-list blob, PPS packets, and per-slice RPS packets.
- `struct rkvdec_hevc_ctx` stores the private table, scaling-matrix cache, and register shadow.
- `set_ps_field()`, `assemble_hw_pps()`, `assemble_sw_rps()`, and `config_registers()` handle packet and register packing.
- `rkvdec_hevc_validate_sps()`, `rkvdec_hevc_start()`, `rkvdec_hevc_run()`, `rkvdec_hevc_stop()`, and `rkvdec_hevc_try_ctrl()` implement the codec lifecycle.

## Control Flow
`start()` allocates context and coherent private-table memory, copies the global HEVC CABAC table, and stores `ctx->priv`. Each `run()` snapshots controls, updates scaling-list hardware data when needed, assembles PPS and per-slice RPS packets, configures registers, runs the generic postamble, schedules the watchdog, primes caches, optionally disables QoS for variants with that quirk, and starts decode. `stop()` frees the coherent table and context.

## State And Persistence
Persistent state is the per-context `rkvdec_hevc_ctx`. Its scaling-matrix cache suppresses repeated scaling-list translations. The coherent private table persists across frames and is overwritten by packet assembly. Register shadow state is rebuilt for each frame. Reference addresses come from active DPB entries through `get_ref_buf()` and fall back to the destination buffer.

## Dependencies And Integration Points
The backend integrates with `rkvdec.c` format descriptors and V4L2 HEVC controls, `rkvdec-regs.h`, common HEVC helpers, `rkvdec-cabac.h`, DMA-contig VB2 buffers, and variant quirks.

## Risks
- `start()` relies on V4L2 `try_ctrl` paths for SPS validation rather than validating directly.
- `assemble_sw_rps()` indexes `priv_tbl->rps[j]` for `run->num_slices` without an explicit local bound against `RKV_RPS_LEN`.
- Register setup iterates 15 reference slots, matching hardware but requiring DPB assumptions to stay aligned.
- Stream length is programmed as `round_up(payload, 16) + 64`, so edge payload sizes need coverage.
- Invalid PPS tile arrays would directly affect hardware packet contents.

## Test Signals
Run HEVC decode with I/P/B slices, multiple slices, tiles on/off, weighted prediction flags, SAO/PCM flags, scaling-list changes, long and short reference lists, 8-bit and 10-bit streams, monochrome and 4:2:0 content, timeout/watchdog paths, and QoS-quirk variants.

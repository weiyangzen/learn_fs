# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264.c

## Purpose
This file implements the base Rockchip RKVDEC H.264 stateless decoder backend. It marshals V4L2 H.264 controls into a coherent private hardware table, programs RKVDEC registers, starts decoding, and provides the H.264 `rkvdec_coded_fmt_ops` callbacks.

## Important APIs, Types, And Functions
- `struct rkvdec_h264_priv_tbl` is the coherent hardware table containing CABAC data, scaling lists, RPS, SPS/PPS packets, and error info.
- `struct rkvdec_h264_ctx` stores the private table, cached reference lists, and a register shadow.
- `set_ps_field()`, `assemble_hw_pps()`, `set_poc_reg()`, and `config_registers()` handle packet and register packing.
- `rkvdec_h264_start()`, `rkvdec_h264_run()`, `rkvdec_h264_stop()`, `rkvdec_h264_try_ctrl()`, and `rkvdec_h264_fmt_ops` implement the backend lifecycle.

## Control Flow
`start()` validates SPS, allocates context/private DMA memory, and seeds CABAC data. Each `run()` snapshots controls, builds V4L2 reference lists, assembles scaling/PPS/RPS data, programs registers, runs the common postamble, schedules a watchdog, primes luma/chroma caches, and starts decode. `stop()` releases the coherent table and context.

## State And Persistence
Persistent per-open-codec state is `struct rkvdec_h264_ctx` in `ctx->priv`. Its coherent `priv_tbl` persists across frames and is overwritten per decode. Register state is rebuilt from scratch for each run. Reference addresses come from current DPB resolution or fall back to the destination buffer for invalid entries.

## Dependencies And Integration Points
The backend depends on `rkvdec.h`, `rkvdec-regs.h`, common H.264 helpers, V4L2 stateless H.264 controls, V4L2 H.264 reference-list builders, DMA-contig VB2 buffers, and CABAC tables. It is selected from `rkvdec.c` through `rkvdec_h264_fmt_ops`.

## Risks
- Signed V4L2 fields are written through an unsigned bitfield helper, relying on correct two's-complement field widths.
- Register programming assumes one contiguous capture plane and correct negotiated strides.
- Missing DPB buffers fall back to the destination buffer, avoiding faults but hiding userspace reference errors as corruption.
- `run()` assumes required controls were established by the V4L2 framework.

## Test Signals
Test unsupported SPS rejection, I/P/B decode, field-coded streams, long-term references, scaling matrices, 8-bit and 10-bit streams, stride/crop variants, timeout handling, and register traces for correct base addresses and POC placement.

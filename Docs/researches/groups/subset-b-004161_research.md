# Research: subset-b-004161

Grouped research for the Rockchip RKVDEC H.264/HEVC backend sources under `sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-cabac.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-cabac.c

## Purpose
This file is a data-only CABAC initialization provider for Rockchip's RKVDEC stateless H.264 and HEVC decoder backends. It defines the H.264 `(m, n)` context initialization table and the HEVC hardware CABAC byte table copied into per-context coherent auxiliary buffers before decoding starts.

## Important APIs, Types, And Data
- `CABAC_ENTRY(ctxidx, ...)` expands one H.264 context index into four initialization-class entries: cabac_init_idc 0, 1, 2, and intra.
- `const s8 rkvdec_h264_cabac_table[4][464][2]` is the exported H.264 table. It is organized by initialization set, context index, then `{m, n}` pair.
- `const u8 rkvdec_hevc_cabac_table[RKV_HEVC_CABAC_TABLE_SIZE]` is the exported HEVC table. The declared size comes from `rkvdec-cabac.h` and is expected to match the hardware table layout exactly.

## Control Flow
There is no executable control flow. Consumers copy the tables into DMA-visible private tables during codec `start()`:
- `rkvdec-h264.c` copies `rkvdec_h264_cabac_table` into `struct rkvdec_h264_priv_tbl::cabac_table`.
- `rkvdec-hevc.c` and the newer VDPU-specific HEVC backends copy `rkvdec_hevc_cabac_table` into their private CABAC table area.
The hardware later receives the coherent table base through `regs->common.cabactbl_base`.

## State And Persistence
The file contributes immutable global kernel data. Runtime persistence is per decoder context only after the backend copies the table into its coherent auxiliary allocation. No mutable state is stored in this file.

## Dependencies And Integration Points
The file includes only `rkvdec-cabac.h` for declarations and Linux integer types. It is tightly coupled to hardware ABI sizes in the H.264/HEVC private table definitions and to the CABAC base register programmed by the backend.

## Risks
- The HEVC byte table has no local compile-time initializer-count assertion beyond the declared array size; any accidental data churn could still compile if the initializer is shorter and zero-filled.
- H.264 context coverage is manually transcribed from spec tables plus undocumented indices 399-459; table-entry mistakes would manifest as decode corruption rather than obvious driver errors.
- The table layout is hardware ABI, so formatting-only edits are low risk but semantic edits need bitstream conformance testing.

## Test Signals
Useful signals are successful H.264 and HEVC stateless decode across CABAC-coded bitstreams, including H.264 I/P/B slices with cabac_init_idc 0-2 and HEVC clips at supported bit depths. Failures usually appear as block corruption, decode timeout, or mismatch against software-decoded reference frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-cabac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-cabac.h -->
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
- `RKV_HEVC_CABAC_TABLE_SIZE` is a hardware contract. If a backend private table or the source initializer diverges from this value, hardware reads may address wrong data.
- The header provides declarations only; it does not enforce table semantic correctness.

## Test Signals
Build coverage catches symbol and type mismatches. Runtime decode testing with HEVC and H.264 CABAC streams validates that copied table sizes and hardware offsets remain correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-cabac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264-common.c

## Purpose
This file contains H.264 helpers shared by the base RKVDEC backend and VDPU-specific H.264 backends. It translates V4L2 stateless H.264 controls into hardware reference-picture-set data, scaling-list data, decoded format metadata, SPS validation, and per-run control pointers.

## Important APIs, Types, And Functions
- `lookup_ref_buf_idx()` resolves active DPB `reference_ts` values to capture-queue `vb2_buffer` objects and stores them in `run->ref_buf[]`.
- `assemble_hw_rps()` builds the packed H.264 RPS structure consumed by hardware from V4L2 reference lists and the resolved DPB buffers.
- `assemble_hw_scaling_list()` copies V4L2 4x4 and 8x8 scaling matrices into the hardware private table when the PPS says a scaling matrix is present.
- `rkvdec_h264_adjust_fmt()` forces one capture plane and defaults `sizeimage` to width * height * 2 bytes.
- `rkvdec_h264_get_image_fmt()` maps SPS bit depth and chroma format to the driver's `enum rkvdec_image_fmt`.
- `rkvdec_h264_validate_sps()` rejects unsupported chroma formats, bit-depth mismatch, unsupported bit depth, and coded dimensions larger than the configured coded format.
- `rkvdec_h264_run_preamble()` snapshots current H.264 V4L2 controls into `struct rkvdec_h264_run` and then calls the generic `rkvdec_run_preamble()`.

## Control Flow
The normal per-frame H.264 path calls `rkvdec_h264_run_preamble()`, builds V4L2 P/B reference lists, calls `assemble_hw_scaling_list()`, resolves DPB buffers through `lookup_ref_buf_idx()`, and packs RPS entries with `assemble_hw_rps()`. `set_dpb_info()` is a local bitfield helper that places one reference-list entry into the correct packed slot for three reference lists.

## State And Persistence
The helpers do not allocate persistent state. They fill caller-owned per-run or per-context structures. `run->ref_buf[]` is rebuilt every decode from current DPB timestamps. Scaling-list and RPS outputs persist only in the backend's coherent private table until overwritten by later frames or freed during codec stop.

## Dependencies And Integration Points
The file depends on V4L2 stateless H.264 controls, `v4l2_h264_reflist_builder`, V4L2 mem2mem queues, videobuf2 buffer lookup, and `rkvdec.h` context/run structures. It is used by `rkvdec-h264.c`, `rkvdec-vdpu381-h264.c`, and `rkvdec-vdpu383-h264.c`.

## Risks
- Missing reference buffers are tolerated and encoded as invalid DPB entries, but bad userspace timestamps can still degrade prediction or cause corruption.
- `assemble_hw_scaling_list()` leaves the previous scaling table untouched when the PPS scaling flag is absent; hardware should ignore it, but stale data becomes risky if register flags are wrong.
- RPS packing relies on V4L2 reference indices staying within DPB bounds; `WARN_ON()` catches out-of-range references but continues.
- SPS validation allows chroma format 2 for H.264, so downstream backends and register programming must agree on 4:2:2 support.

## Test Signals
Exercise H.264 I/P/B frame decode, field references, inactive DPB slots, long-term references, scaling matrices, 8-bit and 10-bit streams, 4:2:0 and 4:2:2 streams, and coded-size rejection via `VIDIOC_S_EXT_CTRLS` or decode start failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264-common.h

## Purpose
This header defines the shared H.264 hardware-facing data structures and helper prototypes for Rockchip RKVDEC H.264 backends.

## Important APIs, Types, And Data
- `struct rkvdec_h264_scaling_list` mirrors the hardware 4x4/8x8 scaling-list blob and includes padding for the private-table layout.
- `struct rkvdec_h264_reflists` stores V4L2 P, B0, and B1 reference lists.
- `struct rkvdec_h264_run` extends `struct rkvdec_run` with current H.264 decode controls and resolved DPB buffers.
- `struct rkvdec_rps_entry` and `struct rkvdec_rps` define packed hardware RPS memory, including frame numbers and three reference-list entry groups.
- Prototypes export reference lookup, RPS assembly, scaling-list assembly, format adjustment, image-format detection, SPS validation, and run preamble.

## Control Flow
The header wires shared helpers into each H.264 backend. Backends allocate a private table containing these structures, call the helpers during each `run()`, then program register addresses pointing to the filled table.

## State And Persistence
The structs describe caller-owned state. `rkvdec_h264_run` is per decode invocation. `rkvdec_rps` and `rkvdec_h264_scaling_list` usually live inside a coherent per-context private table until stop.

## Dependencies And Integration Points
The header includes V4L2 H.264 and mem2mem headers plus `rkvdec.h`. It is part of the ABI between common H.264 logic and hardware-specific RKVDEC/VDPU backends.

## Risks
- Packed bitfield layout is compiler- and ABI-sensitive; the Linux kernel build environment is assumed by the driver.
- Changing padding or field widths changes hardware memory layout.
- `struct rkvdec_h264_run` carries raw pointers to V4L2 controls; users must populate it with `rkvdec_h264_run_preamble()` before helper use.

## Test Signals
Compile-time users catch prototype and layout references. Runtime signals include correct RPS behavior for P/B slices, field pictures, and long-term references across all H.264 backend variants that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264.c

## Purpose
This file implements the base Rockchip RKVDEC H.264 stateless decoder backend. It marshals V4L2 H.264 controls into a coherent private hardware table, programs RKVDEC registers, starts decoding, and provides the H.264 `rkvdec_coded_fmt_ops` callbacks.

## Important APIs, Types, And Functions
- `struct rkvdec_h264_priv_tbl` is the coherent hardware table containing CABAC data, scaling lists, RPS, SPS/PPS packets, and error info.
- `struct rkvdec_h264_ctx` stores the private table, cached reference lists, and a register shadow.
- `set_ps_field()` writes variable-length fields into the SPS/PPS hardware packet.
- `assemble_hw_pps()` packs SPS/PPS fields, scaling-list DMA address, and long-term DPB flags into the PPS-indexed packet.
- `set_poc_reg()` maps top/bottom POC values into the split RKVDEC POC register layout.
- `config_registers()` fills stream, output, stride, CABAC, reference, POC, PPS, RPS, and error-info registers, then copies the register shadow to MMIO.
- `rkvdec_h264_start()` validates SPS, allocates context/private DMA memory, copies the CABAC table, and stores `ctx->priv`.
- `rkvdec_h264_run()` performs one decode submission and starts hardware.
- `rkvdec_h264_stop()`, `rkvdec_h264_try_ctrl()`, and `rkvdec_h264_fmt_ops` complete the backend interface.

## Control Flow
`start()` requires an H.264 SPS control, validates it, allocates zeroed software context memory, allocates coherent hardware memory, and seeds CABAC data. Each `run()` snapshots controls, builds V4L2 reference lists, assembles scaling/PPS/RPS data, programs registers, runs the common postamble, schedules a watchdog, primes luma/chroma caches, and writes the interrupt/config register to start decode. `stop()` releases the coherent table and context.

## State And Persistence
Persistent per-open-codec state is `struct rkvdec_h264_ctx` in `ctx->priv`. Its coherent `priv_tbl` persists across frames and is overwritten per decode. Register state is rebuilt from scratch into `h264_ctx->regs` for each run. Source and destination buffer addresses come from current VB2 buffers; reference addresses come from current DPB resolution or fall back to the destination buffer for invalid entries.

## Dependencies And Integration Points
The backend depends on `rkvdec.h` core scheduling/postamble behavior, `rkvdec-regs.h` register layout, common H.264 helpers, V4L2 stateless H.264 controls, V4L2 H.264 reference-list builders, DMA-contig VB2 buffers, and the CABAC table declarations. It is selected from `rkvdec.c` through `rkvdec_h264_fmt_ops` for the base RKVDEC variant.

## Risks
- `assemble_hw_pps()` writes signed V4L2 fields through an unsigned bitfield helper; this relies on the source values fitting the hardware two's-complement field widths.
- Register programming assumes one contiguous capture plane and correct bytesperline/height; bad format negotiation would directly affect hardware strides.
- Missing DPB buffers are replaced with the destination buffer to keep hardware addresses valid, which avoids faults but can hide userspace reference-management errors as visual corruption.
- The error-info buffer is large and coherent; allocation failures are handled, but memory pressure can prevent codec start.
- `run()` assumes required controls were established by the V4L2 framework; null control pointers would crash if the control setup contract is broken.

## Test Signals
Test startup validation for unsupported SPS values, successful decode of I/P/B frames, field-coded streams, long-term references, scaling matrices, 8-bit and 10-bit streams, stride/crop variants, timeout handling, and MMIO register traces for correct base addresses and POC placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc-common.c

## Purpose
This file provides shared HEVC helpers for Rockchip RKVDEC and VDPU HEVC backends. It computes tile dimensions, translates scaling matrices into hardware layout, derives SPS short/long-term reference-picture-set tables, resolves reference buffers, adjusts decoded formats, maps SPS image formats, and snapshots HEVC stateless controls.

## Important APIs, Types, And Functions
- `compute_tiles_uniform()` and `compute_tiles_non_uniform()` derive CTB tile column/row sizes from PPS parameters.
- `struct calculated_rps_st_set` is an internal representation of derived short-term RPS values.
- `rkvdec_hevc_assemble_hw_scaling_list()` updates a hardware `struct scaling_factor` only when the V4L2 scaling matrix differs from the cache.
- `rkvdec_hevc_assemble_hw_rps()` assembles long-term and short-term SPS RPS data for backends that store hardware RPS tables.
- `get_ref_buf()` maps an HEVC DPB index to a capture buffer by timestamp, falling back to the destination buffer if unavailable.
- `rkvdec_hevc_adjust_fmt()`, `rkvdec_hevc_get_image_fmt()`, and `rkvdec_hevc_run_preamble()` provide common format and run setup behavior.

## Control Flow
Scaling-list assembly compares the current matrix to a caller-provided cache, translates 4x4/8x8/16x16/32x32 matrices through `variant->ops->flatten_matrices()`, writes DC coefficients, and refreshes the cache. RPS assembly optionally reads extended SPS ST/LT RPS controls, derives predicted or explicit short-term sets according to HEVC spec equations, writes packed hardware fields, and fills long-term POC/used flags. The run preamble retrieves required HEVC controls plus optional extended RPS controls when `ctx->has_sps_st_rps` or `ctx->has_sps_lt_rps` is set.

## State And Persistence
This file owns no persistent allocations except temporary ST-RPS calculation memory during RPS preparation. Caches are caller-owned, commonly in per-codec context. `get_ref_buf()` is per-run and does not retain buffer references; it returns the destination buffer as a safe fallback address.

## Dependencies And Integration Points
The helpers depend on V4L2 stateless HEVC controls, V4L2 mem2mem queues, videobuf2 timestamp lookup, `rkvdec_variant` matrix-flattening callbacks, and shared RKVDEC context state. RPS helpers are used by VDPU381/VDPU383 HEVC paths; the base `rkvdec-hevc.c` builds a per-slice software RPS packet instead.

## Risks
- `rkvdec_hevc_prepare_hw_st_rps()` allocates temporary calculation memory but does not check `kzalloc()` failure before use.
- The ST-RPS cache comparison/copy uses `sizeof(struct v4l2_ctrl_hevc_ext_sps_st_rps)`, which covers one element, while the control can contain multiple sets; this can miss changes beyond the first element in backends that use the cache.
- Scaling-list cache correctness depends on the caller initializing the cache and passing the same cache across frames.
- Fallback to the destination buffer prevents invalid DMA addresses but can hide missing-reference bugs.
- Tile helpers trust PPS tile counts and arrays from validated controls; malformed control data could produce bad dimensions if upstream validation is insufficient.

## Test Signals
Use HEVC streams with uniform and non-uniform tiles, scaling-list changes across frames, explicit and predicted short-term RPS, long-term RPS, missing/invalid reference timestamps, 8-bit and 10-bit 4:2:0/monochrome formats, and optional extended SPS RPS controls on VDPU variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc-common.h

## Purpose
This header defines shared HEVC hardware-table structures and helper prototypes for Rockchip RKVDEC-family HEVC decoder backends.

## Important APIs, Types, And Data
- `struct rkvdec_rps_refs` describes one packed long-term RPS reference.
- `struct rkvdec_rps_short_term_ref_set` stores up to 15 delta POCs and used flags in the hardware bitfield layout.
- `struct rkvdec_rps` combines long-term references and up to 64 short-term reference sets.
- `struct rkvdec_hevc_run` extends `struct rkvdec_run` with HEVC slice, decode, SPS, PPS, scaling, extended RPS controls, and `num_slices`.
- `struct scaling_factor` defines the hardware scaling-list layout used by HEVC backends.
- Function prototypes expose tile calculation, RPS/scaling assembly, reference-buffer lookup, format adjustment, image-format mapping, and run preamble.

## Control Flow
Backends include this header, allocate private tables containing `struct scaling_factor` and sometimes `struct rkvdec_rps`, populate a per-frame `rkvdec_hevc_run`, then call these helpers before MMIO register programming.

## State And Persistence
The structs are data contracts. `rkvdec_hevc_run` is per decode submission. `scaling_factor` and `rkvdec_rps` usually persist in coherent per-context private tables and are updated when controls change.

## Dependencies And Integration Points
The header depends on Linux integer types, V4L2 mem2mem types, and `rkvdec.h`. It is shared by the base HEVC backend and VDPU381/VDPU383 HEVC variants, and its structure layouts must match hardware expectations.

## Risks
- Packed bitfields encode a hardware ABI; field-width or ordering changes can silently break decoding.
- The header exposes raw V4L2 control pointers in `rkvdec_hevc_run`; callers must establish valid controls before invoking helpers.
- `struct scaling_factor` sizes and comments are hardware-specific and must remain aligned with backend private-table offsets.

## Test Signals
Build coverage across all HEVC backends catches prototype drift. Runtime coverage should include tile, scaling-list, RPS, reference-buffer, and bit-depth combinations on each backend variant using these structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc.c

## Purpose
This file implements the base Rockchip RKVDEC HEVC stateless decoder backend. It packs HEVC SPS/PPS and per-slice RPS data into coherent hardware packets, programs RKVDEC registers, and exposes `rkvdec_hevc_fmt_ops`.

## Important APIs, Types, And Functions
- `struct rkvdec_hevc_priv_tbl` contains the HEVC CABAC table, scaling-list blob, PPS packets, and per-slice RPS packets.
- `struct rkvdec_hevc_ctx` stores the private table, scaling-matrix cache, and register shadow.
- `set_ps_field()` packs arbitrary bitfield values into hardware packet words.
- `assemble_hw_pps()` writes SPS/PPS fields, tile dimensions, and scaling-list DMA address to the PPS-indexed hardware packet.
- `assemble_sw_rps()` creates one hardware RPS packet per slice from V4L2 slice reference lists and decode parameters.
- `config_registers()` programs stream length/base, output base, strides, CABAC table, reference bases/POCs, current POC, PPS base, and RPS base.
- `rkvdec_hevc_validate_sps()`, `rkvdec_hevc_start()`, `rkvdec_hevc_run()`, `rkvdec_hevc_stop()`, and `rkvdec_hevc_try_ctrl()` implement the codec callback lifecycle.

## Control Flow
`start()` allocates zeroed HEVC context memory, coherent private-table memory, copies the global HEVC CABAC table, and stores `ctx->priv`. Each `run()` snapshots controls, updates scaling-list hardware data when needed, assembles the PPS packet, assembles per-slice RPS packets, configures registers, runs the generic postamble, schedules the watchdog, primes caches, optionally disables QoS for variants with that quirk, and starts decode through the interrupt/config register. `stop()` frees the coherent table and context.

## State And Persistence
Persistent state is the per-context `rkvdec_hevc_ctx`. Its scaling-matrix cache suppresses repeated scaling-list translations. The coherent private table persists across frames and is overwritten by `assemble_hw_pps()` and `assemble_sw_rps()`. Register shadow state is rebuilt for each frame. Reference addresses come from active DPB entries through `get_ref_buf()` and fall back to the destination buffer.

## Dependencies And Integration Points
The backend integrates with `rkvdec.c` format descriptors and V4L2 HEVC controls, `rkvdec-regs.h` register definitions, common HEVC helpers, `rkvdec-cabac.h`, DMA-contig VB2 buffers, and variant quirks. It is the base HEVC operation table, while newer VDPU variants reuse common helpers but have their own register/table layouts.

## Risks
- `rkvdec_hevc_start()` does not validate SPS immediately; validation is enforced via `try_ctrl`, so correctness depends on V4L2 control setup paths invoking it.
- `assemble_sw_rps()` indexes `priv_tbl->rps[j]` for `run->num_slices` without an explicit local bound against `RKV_RPS_LEN`.
- HEVC register setup only iterates 15 reference base slots; this matches the hardware layout but requires DPB/control assumptions to stay aligned.
- Stream length is programmed as `round_up(payload, 16) + 64`, so payload-size edge cases should be tested against hardware expectations.
- Tile programming writes PPS-provided width/height values when tiles are enabled and synthesized single-tile dimensions otherwise; invalid PPS tile arrays would affect hardware packet contents.

## Test Signals
Run HEVC decode with I/P/B slices, multiple slices, tiles on/off, weighted prediction flags, SAO/PCM flags, scaling-list changes, long and short reference lists, 8-bit and 10-bit streams, monochrome and 4:2:0 content, timeout/watchdog paths, and variants with `RKVDEC_QUIRK_DISABLE_QOS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc.c -->

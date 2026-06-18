# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_h265.c

Purpose: HEVC/H.265 stateless decode backend for Cedrus. It maps V4L2 HEVC controls into H265 engine registers/SRAM, supports tiles/WPP entry points, 8-bit and selected 10-bit capture sizing, per-buffer MV column buffers, and exports `cedrus_dec_ops_h265`.

Important APIs/functions: `cedrus_h265_2bit_size()` computes extra 2-bit plane size for 10-bit output packing. IRQ helpers inspect/clear/disable `VE_DEC_H265_*` status/control. SRAM helpers write frame info, DPB entries, reference lists, prediction weights, and scaling lists. `cedrus_h265_write_tiles()` configures tile start/end CTBs and entry point buffer contents. `cedrus_h265_setup()` validates entry point count, allocates per-output MV column buffer, enables engine, programs bitstream addresses/length, CTB address, tiles, SWDEC bit alignment, NAL/SPS/PPS/slice controls, picture size, scaling list, neighbor buffer, DPB/output frame info, ref lists, weighted prediction, 10-bit offset/stride, and IRQ mask. `cedrus_h265_start()` allocates neighbor info and coherent entry-point buffers; `cedrus_h265_stop()` frees them plus per-buffer MV columns; `extra_cap_size()` reports extra capture size for >8-bit.

Control flow: OUTPUT streamon allocates context buffers. Each job programs source slice data and all HEVC metadata, then trigger writes `VE_DEC_H265_TRIGGER_DEC_SLICE`. IRQ completion is handled by common `cedrus_irq()`.

State and persistence: context neighbor and entry-point buffers persist during streaming. Per-capture-buffer H265 MV column buffers are lazy and persist until streamoff. `ctx->bit_depth` is set by SPS control validation and affects capture format size and 10-bit programming.

Dependencies/integration: consumes V4L2 HEVC SPS/PPS/slice/decode/scaling/entry-point controls, common Cedrus helpers, vb2 timestamp buffer lookup, and register macros. Capability `CEDRUS_CAPABILITY_H265_10_DEC` gates bit depth in `cedrus.c`.

Risks: `cedrus_h265_irq_status()` does not return `CEDRUS_IRQ_NONE` when no status bits are set; with the common IRQ handler this can interpret an irrelevant/early interrupt as error after masking. Tile/entry-point buffer layout differs for WPP versus tiles and is sensitive to `num_entry_point_offsets`. Slice data with `data_byte_offset == 0` is unsupported. Padding parsing depends on hardware show/skip bits and returns `-EINVAL` if the inspected padding byte is zero. Neighbor buffer sizing is BSP-derived and comment notes H6 may need doubled size for 10-bit.

Test signals: HEVC I/P/B slices, tiles, WPP, weighted prediction, scaling lists, 8-bit and 10-bit H6 streams, mismatched entry-point control counts, `data_byte_offset` boundary cases, DPB timestamp misses, large resolution streams, and IRQ behavior under shared interrupt noise.

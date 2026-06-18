# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mcif_wb.h

## Purpose

`mcif_wb.h` defines the memory-controller interface for display writeback. It abstracts MCIF writeback enablement, buffer programming, arbitration, IRQ setup, warmup, and frame dumping for DWB output paths.

## Important APIs, Types, And Functions

`enum mmhubbub_wbif_mode` selects packed RGB/FP16 and planar 4:2:0 8/10 bpc modes. `mcif_arb_params` holds watermark, slice, timing, max scaled time, and DRAM speed-change duration settings. `mcif_irq_params` controls software, slice, overrun, and VCE interrupt enables. `mcif_wb_frame_dump_info` captures dump size, dimensions, pitches, and format. `struct mcif_wb` stores vtable, context, and instance. `mcif_wb_funcs` includes warmup, enable/disable, buffer config, arbitration config, IRQ config, and `dump_frame`.

## Control Flow

DWB users configure destination buffers and arbitration before enabling MCIF. IRQs may be configured to signal slices or overruns. `dump_frame` reads or transforms captured luma/chroma buffers into destination buffers according to output format and dimensions.

## State And Persistence Behavior

The object carries instance identity only. Runtime persistence is in MCIF/DWB registers and programmed frame buffers. Arbitration and watermark settings persist until rewritten, and dump metadata describes a captured frame rather than long-lived driver state.

## Dependencies And Integration Points

The header depends on `dc_hw_types.h` for DWB scaler, warmup, and buffer parameter types. It integrates with DWB resource blocks, MPC DWB muxing, memory hub arbitration, and debug/capture workflows that dump frames.

## Risks And Test Signals

Risks include incorrect pitch/format handling, stale buffer addresses, underflow/overrun IRQ configuration errors, and bad watermarks during p-state or DRAM changes. Test signals include DWB capture in packed and planar modes, overrun interrupt tests, frame dump integrity, and stress during clock or memory speed transitions.

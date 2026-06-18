# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 9822-12326

## Scope

This chunk is part of the generated AMD DCN 2.0.0 ASIC register mask/shift header. It covers lines 9822-12326 and contributes register field metadata for DC display hub pipe blocks, mostly pipes 0, 1, and 2. The chunk contains 2,104 `#define` entries: 1,052 `__SHIFT` constants and 1,052 `_MASK` constants. There are no C functions, structs, enums, or runtime control-flow constructs in this slice; the exported surface is preprocessor constants consumed by register accessor macros elsewhere in the AMDGPU display driver.

## Purpose

The purpose of this chunk is to define exact bit positions and bit masks for DCN 2.0.0 display front-end register fields. These definitions let the display core encode, update, poll, and decode fields inside memory-mapped hardware registers without hard-coded literal bit arithmetic in functional code.

The visible hardware domains are:

- Late `HUBPREQ0` request metadata fields for nominal timing, per-line delivery, cursor request adjustment, ref-clock-to-pixel-clock ratio, destination Y request limits, and HUBPREQ memory power control/status.
- `HUBPRET0`, `HUBPRET1`, and `HUBPRET2` return path fields for detile buffer routing, memory power, read-line windows, vblank/read-line interrupts, current read-line value, and read-line status.
- `CURSOR0_0`, `CURSOR0_1`, and `CURSOR0_2` fields for cursor enable/mode/pitch/position/hotspot/stereo, cursor memory power, and DMDATA address/QoS/status/software data.
- `DC_PERFMON7`, `DC_PERFMON8`, and the start of `DC_PERFMON9` performance monitor fields for counter selection, state, run/stop control, interrupt status/acknowledge, and counter readout.
- `HUBPXFC0` and `HUBPXFC1` fields for cross-fabric/XFC enablement, XBUF read base addresses, pitch, delay/precharge/prefetch margins, underflow status, slave VTG/scaler timing, and MPC destination placement.
- `HUBP1` and `HUBP2` pipe-local hub pixel processor fields for surface format, tiling, viewports, request sizes, hubp enable/blank/underflow/timeout, clock control/status, VMPG page size, debug, and measurement window controls.
- `HUBPREQ1` and `HUBPREQ2` request path fields for surface pitch, VMID, primary/secondary and chroma/luma surface addresses, DCC/TMZ surface control, flip control, queuing, pacing, in-use addresses, VM aperture/context controls, TTU/QoS timing, prefetch/vblank/flip/nominal timing parameters, cursor settings, and request-side memory power.

## Important API Surface

The API surface is macro naming, not callable symbols. Each hardware field follows the pattern:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Examples from the chunk include:

- `HUBP1_DCSURF_SURFACE_CONFIG__SURFACE_PIXEL_FORMAT__SHIFT` and `_MASK` for extracting or programming pipe 1 surface format.
- `HUBPREQ1_DCSURF_FLIP_CONTROL__SURFACE_UPDATE_LOCK__SHIFT` and `_MASK` for the pipe 1 surface update lock bit.
- `HUBPREQ1_DC_VM_CONTEXT0_CNTL__ENABLE_CONTEXT__SHIFT` and `_MASK` for display VM context enablement.
- `CURSOR0_1_CURSOR_CONTROL__CURSOR_ENABLE__SHIFT` and `_MASK` for enabling pipe 1 cursor composition.
- `HUBPRET2_HUBPRET_INTERRUPT__PIPE_VBLANK_INT_CLEAR__SHIFT` and `_MASK` for clearing pipe 2 return-path vblank interrupt state.
- `DC_PERFMON8_PERFCOUNTER_CNTL__PERFCOUNTER_EVENT_SEL__SHIFT` and `_MASK` for selecting pipe 1/DC perfmon events.
- `HUBPXFC1_HUBP_XFC_UNDERFLOW_STATUS__XFC_UNDERFLOW_CLR__SHIFT` and `_MASK` for acknowledging XFC underflow state.

The constants are intended to be included by higher-level display code using register helper macros such as `HUBP_SF`, `IPP_SF`, `TF_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and register table initializers. Inclusion sites found for this DCN 2.0.0 mask header include DC resource setup, IRQ service, clock manager, GPIO factory, DMUB DCN20 support, and GMC 10 code.

## Control Flow

There is no local control flow in this header chunk. Runtime control flow is external:

- Resource initialization code includes this header and expands mask/shift list macros into field tables. For DCN-style hubp code, `HUBP_MASK_SH_LIST_*(__SHIFT)` and `HUBP_MASK_SH_LIST_*(_MASK)` build `shift` and `mask` tables from these constants.
- Functional hubp/cursor/interrupt code calls register access helpers with symbolic field names. The helpers combine the register address, this chunk's mask, and this chunk's shift to write field values or decode register contents.
- IRQ code uses fields such as `HUBPRETn_HUBPRET_INTERRUPT` or surface flip interrupt fields to mask, clear, and query vblank/read-line/flip events.
- Power and validation paths can poll status fields such as `HUBP*_DCHUBP_CNTL__HUBP_NO_OUTSTANDING_REQ`, `*_UNDERFLOW_STATUS`, `*_MEM_PWR_STATUS`, and `*_CLOCK_ON` after programming the control fields.

The observable ordering contract is implicit: callers must program related fields in hardware-required order. This chunk only supplies bit locations and does not enforce ordering between surface address updates, update locks, VM context setup, clock enables, memory power transitions, or interrupt clears.

## State and Persistence

The file itself has no persistent software state. The macros map to persistent hardware state while the GPU is powered:

- Surface address, pitch, format, viewport, tiling, DCC, TMZ, VMID, and VM context fields determine which memory the display pipe fetches and how it interprets it.
- Flip, queue, pacing, in-use, and earliest-in-use fields expose or control surface update sequencing across frame boundaries.
- Prefetch, vblank, nominal, TTU, per-line delivery, and ref-clock conversion fields persist as timing parameters used by the HUBPREQ scheduler.
- Clock, blank, disable, timeout, underflow, memory power control, and status fields represent live pipe state and hardware health.
- Interrupt status/acknowledge/clear fields persist until software clears them or hardware transitions state.
- Perfmon counter registers hold selected measurement configuration and sampled/counted values.

Because these are memory-mapped hardware fields, stale or incorrect masks can produce persistent display corruption, faults, underflow state, or missed interrupt acknowledgements until the driver reprograms the block or the hardware is reset.

## Dependencies and Integration Points

This chunk depends on the generated register address header for matching register offsets, usually `dcn_2_0_0_offset.h`, and on AMD display helper macros that paste register and field names into `_MASK` and `__SHIFT` identifiers. The constants are tightly coupled to the DCN 2.0.0 hardware specification.

Important integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`, which includes this header for DCN 2.0 resource construction.
- `drivers/gpu/drm/amd/display/dc/hubp/dcn10` and `dcn20` hubp helpers, whose register and mask/shift list macros include many HUBP/HUBPREQ/CURSOR fields represented here.
- `drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`, which uses this generation family for interrupt source setup and clearing.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`, where generated DCN register metadata is shared with DMUB-facing display code.
- Cross-generation DCN headers such as `dcn_2_0_1_sh_mask.h`, `dcn_2_1_0_sh_mask.h`, and later `dcn_3_*`/`dcn_4_*` headers, which preserve many similarly named fields but may change masks, presence, or register coverage.

The pipe suffixes are part of the integration contract. This chunk covers pipe-specific copies such as `HUBPREQ1` and `HUBPREQ2`; generic driver code commonly uses macro indirection like `SRI(..., HUBPREQ, id)` and field-list macros based on the pipe instance.

## Risks

- A wrong shift/mask pair can silently write the wrong hardware bits. This is especially risky for surface addresses, VM aperture/context controls, DCC/TMZ flags, update-lock bits, interrupt acknowledgements, and memory power controls.
- Pipe instance copy/paste drift is a major risk. `HUBPREQ1` and `HUBPREQ2` blocks are nearly identical; a single mismatched field width or mask between instances could affect only one display pipe and be hard to reproduce.
- Address-high masks are typically 16-bit while address-low masks are 32-bit. Treating them uniformly would truncate or corrupt 48-bit surface, metadata, VM, or DMDATA addresses.
- Clear/ack fields share registers with status and mask/type bits. Incorrect use of `_MASK` constants in read-modify-write paths can clear interrupts unexpectedly or fail to clear sticky status.
- Timing fields have narrow widths, often 10-23 bits depending on the field. Overflow before masking can convert a calculated prefetch/vblank/nominal timing value into a low wrapped value and cause underflow or missed deadlines.
- Power and clock fields combine force, disable, low-power mode, and live status bits. Confusing control and status masks can leave memories or clocks gated while the pipe is expected to fetch.
- The chunk starts and ends mid-logical-region: it begins with the tail of `HUBPREQ0` and ends at the start of `DC_PERFMON9_PERFCOUNTER_STATE`. Whole-file reconciliation must merge adjacent chunks to describe the full DCN 2.0.0 register map.

## Test Signals

Useful validation signals for changes to this chunk are primarily build-time and hardware/display behavior:

- Full AMDGPU/display driver compilation should catch missing, renamed, or syntactically invalid macros in resource, hubp, irq, dmub, and clock manager code.
- Static comparison against the vendor register database or adjacent generated DCN headers can catch accidental mask/shift drift, especially across the repeated pipe 1 and pipe 2 blocks.
- Runtime display validation should exercise multi-pipe modes, cursor enable/position/hotspot changes, primary and secondary plane flips, DCC-enabled scanout, rotated/mirrored surfaces, VM-enabled display fetches, and secure/TMZ surfaces.
- Interrupt tests should verify vblank, read-line, and surface flip interrupt mask/status/clear behavior for the affected pipe instances.
- Stress signals include absence of HUBP/HUBPXFC underflow, timeout, VM fault, DMDATA underflow, and lost-command counters during mode set, page flip, cursor movement, suspend/resume, and memory power/clock gating transitions.
- Perfmon sanity checks should confirm `DC_PERFMON7/8/9` counter selection, run/stop, interrupt status/ack, and high/low readout behavior when using DC performance monitoring tooling.

## Chunk Notes

This is a generated constants-only slice. The substantive behavior lives in the display core code that consumes the constants and in the DCN 2.0.0 hardware. The key research value of this chunk is the exact register-field coverage and the high-risk domains represented by the masks: display memory fetch setup, VM/DCC/TMZ security and compression controls, flip synchronization, pipe timing, interrupts, power/clock status, cursor metadata, XFC underflow tracking, and performance monitor state.

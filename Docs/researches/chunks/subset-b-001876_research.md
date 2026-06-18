# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 27730-30207

## Scope

This chunk covers lines 27730-30207 of the generated AMD DCN 3.1.5 shift/mask header. It is preprocessor-only register metadata: 2,138 `#define` entries across 2,478 source lines, plus generated register and `addressBlock` comments. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts partway through `OTG0_OTG_CRC_CNTL`, after the first five CRC control shifts are defined by the previous chunk, and continues through the tail of OTG0 output timing generator fields, all OTG1 fields, all OTG2 fields, and most of OTG3 fields. It ends partway through `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK`, with the remaining shift/mask lines for that register and later OTG3 fields in the next chunk.

## Purpose

This header slice publishes exact bit positions and masks for DCN 3.1.5 OTG, or output timing generator, hardware registers. AMDGPU display code combines these macros with the matching DCN 3.1.5 offset header and register-helper macros to pack MMIO writes, decode MMIO reads, configure timing-generator behavior, and build IRQ/register tables without embedding raw bit numbers in driver logic.

The chunk is a generated hardware contract. Its correctness depends on each macro name and numeric value matching the ASIC register database for DCN 3.1.5. Runtime behavior is implemented by consumers such as OPTC and IRQ code; this file only supplies field layout.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within a 32-bit register value.
- `//<REGISTER>` comments group fields belonging to a logical register.
- `// addressBlock: ...` comments group per-instance OTG registers by decoded hardware block.

Major constant families in this chunk include:

- OTG CRC capture and readback fields for OTG0 through OTG3: `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window A/B start/end coordinates, CRC0/1/2/3 data readbacks, and CRC signal masks. These fields cover CRC enablement, continuous/one-shot behavior, capture-source selection, DSC/data-stream modes, window bounds, and 16-bit component results.
- Static-screen and stereo/3D fields: `OTG_STATIC_SCREEN_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_STEREO_CONTROL`, `OTG_STEREO_STATUS`, and `OTG_STEREO_FORCE_NEXT_EYE`, covering static-screen detection, CPU interrupt status/clear bits, 3D structure enable/update/reset state, stereo eye selection, DP stereo-output controls, and current-eye/status bits.
- Global synchronization, update, and lock fields: `OTG_VSTARTUP_PARAM`, `OTG_VUPDATE_PARAM`, `OTG_VREADY_PARAM`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_MASTER_UPDATE_LOCK`, `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL4`, `OTG_VUPDATE_KEEPOUT`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL`. These fields describe vstartup/vupdate/vready timing, interrupt enable/status/clear fields, master-update locks, pending double-buffer updates, global update lock windows, manual trigger/flow control, and keepout windows.
- Global swap lock and multi-OTG coordination fields: `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X`, `OTG_GSL_WINDOW_Y`, and `OTG_GSL_VSYNC_GAP`, covering GSL enable/master mode, delay/check controls, master-update-lock integration, GSL window coordinates, and vsync gap detection/status/clear fields.
- Timing and variable-refresh fields: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_TOTAL_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_VSYNC_NOM_INT_STATUS`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, and `OTG_DRR_CONTROL`.
- Trigger, force-count, flow-control, and status fields: `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_FLOW_CONTROL`, `OTG_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, pixel-data readback, `OTG_STATUS`, `OTG_STATUS_POSITION`, nominal/current counters, frame/VF/HV counters, count reset, manual force-vsync, and vertical sync control.
- Interrupt and pipe-update fields: `OTG_VERTICAL_INTERRUPT0/1/2_POSITION`, `OTG_VERTICAL_INTERRUPT0/1/2_CONTROL`, `OTG_PIPE_UPDATE_STATUS`, and `INTERRUPT_DEST`-related fields included near the per-instance OTG register blocks. These map line-triggered interrupt positions, enable/status/clear/type bits, and update-pending status fields used by IRQ and debug paths.
- DSC/output routing support fields: `OTG_DSC_START_POSITION`, `OTG_REQUEST_CONTROL`, `OTG_MASTER_EN`, `OTG_CLOCK_CONTROL`, `OTG_SPARE_REGISTER`, and output/control fields such as `OTG_OUT_MUX`, `OTG_MASTER_EN`, clock enable/on/gate-disable/busy, and soft reset.

The same logical layout is repeated by instance. OTG1 begins at the `dce_dc_optc_otg1_dispdec` address block, OTG2 begins at `dce_dc_optc_otg2_dispdec`, and OTG3 begins at `dce_dc_optc_otg3_dispdec`. OTG0 is already underway at the start of this chunk.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.5 display components include `dcn_3_1_5_sh_mask.h` and the matching offset header.
2. Register table macros such as `SRI(OTG_* , OTG, inst)` select instance-specific register addresses from the offset header.
3. Field macros such as `SF(OTG0_OTG_CRC_CNTL, OTG_CRC_EN, mask_sh)` resolve to the `__SHIFT` and `_MASK` values defined here.
4. Runtime helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and IRQ register descriptors use those resolved positions to perform MMIO writes, read-modify-write updates, polling, and field decoding.

The declaration order mirrors the hardware register map. OTG0 in this chunk covers CRC through spare/update state. OTG1 and OTG2 each present a full timing-generator instance from basic horizontal/vertical timing through CRC/static-screen/GSL/DRR/update fields. OTG3 starts with the same full timing, status, interrupt, and CRC layout, but this chunk stops before its static-screen and later fields are complete.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes bit locations for state held in DCN 3.1.5 display hardware registers.

Writable fields in this range can program timing totals and blank/sync ranges, vstartup/vupdate/vready positions, dynamic refresh bounds and trigger windows, CRC capture windows and modes, static-screen detection thresholds, GSL synchronization windows, master-update locking, double-buffer update behavior, stereo/3D behavior, flow-control sources, interrupt enables/types/clears, DSC start position, OTG clock enable/reset, and OTG master enablement.

Hardware-updated fields expose CRC result data, one-shot CRC pending state, static-screen status and interrupt status, 3D reset pending/count state, GSL gap status, global sync event/status fields, update-lock status, double-buffer pending bits, DRR timing events, force-count and forced-vsync events, flow-control input status, current master-enable state, interlace current/next field, pixel-data readback, live horizontal/vertical blank/active/sync state, counters, stereo current-eye/status, snapshot/update/pipe-update pending state, and vertical interrupt status bits.

Programmed values persist according to the underlying hardware power and reset domains. They may survive until rewritten, OTG clock/reset sequencing, display pipe reinitialization, suspend/resume restore, GPU reset, or ASIC reset. Status, pending, and counter fields can change asynchronously relative to the C code that includes this header.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 register offset header for register addresses. The shift/mask header identifies bit placement only; it does not say where a register is mapped.

Primary source consumers of this specific header include:

- `display/dmub/src/dmub_dcn315.c`, which includes the generated DCN 3.1.5 register metadata for DMUB-facing display support.
- `display/dc/irq/dcn315/irq_service_dcn315.c`, which uses generated OTG field names in IRQ descriptors for vupdate-no-lock, vblank/vstartup, and vertical-line interrupts.
- `display/dc/resource/dcn315/dcn315_resource.c`, which assembles DCN 3.1.5 resource/register tables.
- `display/dc/gpio/dcn315/hw_factory_dcn315.c` and `display/dc/gpio/dcn315/hw_translate_dcn315.c`, which share the generated register metadata for DCN 3.1.5 GPIO/display integration.

The OTG fields in this chunk align with the generic OPTC register abstractions in `display/dc/optc/dcn31/dcn31_optc.h` and related OPTC implementation files. Those files list OTG registers with `SRI`, list field masks/shifts with `SF`, and implement timing-generator operations such as enable/disable, update locks, DRR programming, CRC configuration/readback, state snapshots, and debug register-state reads.

Key integration areas are:

- Modeset and timing programming: horizontal/vertical totals, blanking, sync, interlace, master enable, clock control, and DSC start-position fields define the scanout timing that the rest of the pipe must match.
- Atomic update synchronization: vstartup/vupdate/vready, global update locks, master-update locks, double-buffer pending fields, keepout windows, and manual flow control coordinate when pending register changes become visible.
- Variable refresh and DRR: `OTG_V_TOTAL_*`, `OTG_DRR_*`, and `OTG_DOUBLE_BUFFER_CONTROL` fields support min/max/mid vtotal changes, trigger windows, timing interrupts, and last-used DRR vtotal readback.
- IRQ service: `OTG_GLOBAL_SYNC_STATUS` and `OTG_VERTICAL_INTERRUPT*` fields are used to enable, clear, and classify vblank/vstartup, vupdate-no-lock, and vertical-line interrupts.
- CRC and validation/debug: `OTG_CRC_*` fields configure CRC capture windows and modes, then expose component CRC results for display validation, debugfs-style CRC capture, and hardware diagnostics.
- Multi-pipe synchronization: GSL control/window/vsync-gap fields are used for synchronized updates across multiple OTGs, especially where master/slave timing generators must coordinate frame timing.
- Power and idle behavior: static-screen fields, clock control, and update-pending/status fields participate in idle detection, power-saving decisions, and safe sequencing around clock gating or reset.

The generated offset and shift/mask headers must come from the same DCN 3.1.5 register database. Mixing this file with a nearby ASIC generation is risky because OTG register names are highly similar while bit layouts, omitted fields, or instance counts can differ.

## Risks And Edge Cases

- The chunk starts mid-register. Lines 27725-27729 contain the first `OTG0_OTG_CRC_CNTL` shifts, but this work item begins at line 27730, so a chunk-only reader sees the rest of `OTG0_OTG_CRC_CNTL` without its earliest `OTG_CRC_EN`, dual-link, blank-only, and continuous-enable shift definitions.
- The chunk ends mid-register at `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK__OTG_CRC_SIG_BLUE_MASK__SHIFT`. The companion control-mask shift and both masks continue after line 30207.
- Repeated per-OTG layouts are copy-sensitive. OTG1, OTG2, and OTG3 are largely identical, so generator drift or manual edits can leave one instance with a subtly wrong field while the others still look correct.
- Many registers mix control, status, clear, pending, and interrupt type bits in the same 32-bit word. Consumers must respect hardware access semantics that are not encoded by the mask file, especially write-one-to-clear and status/pending bits.
- Several fields use high-bit or wide masks such as `0xFFFF0000L`, `0x7FFF0000L`, `0xFF000000L`, and `0x80000000L`. Incorrect integer width handling or signed assumptions can corrupt adjacent fields or misread status.
- Timing and synchronization masks are hardware-sensitive. Bad shifts in vtotal, vupdate, GSL, DRR, or master-update-lock fields can produce missed flips, visible glitches, stuck pending bits, interrupt storms, or hangs waiting for an update/lock condition.
- CRC fields are validation-sensitive. Wrong CRC window, component, DSC, or data-stream masks can make CRC diagnostics misleading even when the display appears functional.
- Clock/reset and master-enable fields can affect live display output. Misprogramming `OTG_CLOCK_CONTROL`, `OTG_CONTROL`, or `OTG_MASTER_EN` may blank a pipe, leave `OTG_BUSY` stuck, or break disable/enable sequencing.

## Test Signals

Useful validation is mostly build-time consistency plus DCN 3.1.5 hardware integration:

- Build AMDGPU display code for a DCN 3.1.5-enabled configuration to catch missing or renamed symbols used by `SRI`, `SF`, `IRQ_REG_ENTRY`, and `REG_*` helper expansion.
- Mechanically verify that each complete register in this line range has matching `__SHIFT` and `_MASK` symbols for every field, while accounting for the partial `OTG0_OTG_CRC_CNTL` start and partial `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK` end.
- Compare this slice against the authoritative DCN 3.1.5 register database and the matching offset header to ensure every per-instance OTG register comment maps to the intended address and every field has the intended bit layout.
- Exercise modeset, DP/eDP scanout, blank/unblank, suspend/resume, GPU reset recovery, and multi-display enable/disable paths on DCN 3.1.5 hardware while watching for timing-generator stuck states and unexpected blanking.
- Exercise atomic flips, cursor updates, vblank/vstartup interrupts, vupdate-no-lock interrupts, vertical-line interrupts, update locks, and pipe-update status readback.
- Exercise DRR/VRR paths using varying min/max/mid vtotal ranges, DRR trigger windows, and timing-update double-buffer modes; watch for stuck `OTG_DRR_*` events or incorrect last-used-vtotal readback.
- Exercise CRC capture with full-frame and windowed modes, DSC-related CRC modes, one-shot and continuous capture where supported, and compare stable reference patterns across OTG instances.
- Exercise multi-OTG synchronized updates/GSL where hardware and topology allow it, checking gap-detection status, master/slave update behavior, and absence of missed or delayed flips.
- Use debug state dumps that read `OTG_MASTER_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_DRR_*`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_VSYNC_GAP`, `OTG_STATIC_SCREEN_CONTROL`, and CRC/status registers to confirm decoded fields match observed hardware behavior.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `OTG0_OTG_CRC_CNTL` completely. It should combine this chunk with the next chunk to describe `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK` and the remainder of OTG3 completely. Whole-file analysis should reconcile this chunk with neighboring DCN 3.1.5 generated-header chunks before making final claims about the complete set of OTG0-OTG3 registers exposed by `dcn_3_1_5_sh_mask.h`.

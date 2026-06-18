# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 32325-34820

## Purpose

This chunk is a generated AMD DCE 12.0 register shift/mask section. It has no executable logic; it publishes C preprocessor constants that describe bit positions and masks for display-engine registers. Driver code combines these constants with DCE 12.0 register addresses and enum values to program AMDGPU display hardware through register read/write helpers.

The range begins inside `CRTCV0_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL`, then covers the tail of CRTC vertical pipe 0 external timing/static-screen/3D/GSL fields. It then defines complete field maps for pipe-1 display blocks: `UNP1` underlay/graphics fetch, `LBV1` line buffer, `SCLV1` scaler, `COL_MAN1` color management, `DCFEV1` display front-end control, `DC_PERFMON12` performance counters, `DMIFV_PG1` display memory-interface arbitration for DPGV0/DPGV1, `BLNDV1` blender, and the beginning of `CRTCV1` timing-generator fields through the first fields of external timing sync loss interrupt control.

Although this path lives under a `ceph-client` source mirror, the content is AMDGPU kernel display hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, networking, or storage persistence.

## Important APIs, Types, And Constants

There are no functions, structs, typedefs, global variables, or runtime APIs in this chunk. The public interface is a set of `#define` constants named in the generated pattern:

- `<REGISTER>__<FIELD>__SHIFT`: low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field after placement in the 32-bit register value.

Major register families in this range are:

- `CRTCV0_CRTCV_EXT_TIMING_SYNC_*`, `CRTCV0_CRTCV_STATIC_SCREEN_CONTROL`, `CRTCV0_CRTCV_3D_STRUCTURE_CONTROL`, and `CRTCV0_CRTCV_GSL_*`: late pipe-0 timing fields for external sync enable/status/clear/type, static-screen interrupts, stereo/3D frame structure, and global swap-lock vsync gap/window/check-line control.
- `UNP1_UNP_GRPH_*`: pipe-1 graphics/underlay enable, surface format, tiling geometry, endian/channel crossbar, luma/chroma primary/secondary and bottom-field surface addresses, high address bits, pitch, source offsets, start/end coordinates, update locking, outstanding-request limits, in-use address readback, DVMM PTE sizing/arbitration, page-flip interrupts, stereo/interlace surface flip tracking, CRC registers, line-buffer data gap, and hardware rotation.
- `LBV1_LBV_*`: pipe-1 line-buffer data format, memory size/partition configuration, desktop height, vline/vline2/vblank interrupt windows and status/ack bits, sync reset selection, black/keyer colors, request/data FIFO level status, urgency thresholds, empty/full status and a no-outstanding-request indicator.
- `SCLV1_SCLV_*`: pipe-1 scaler coefficient RAM selection and tap data, scaler mode/tap count/control, manual replication, automatic ratio calculation, horizontal/vertical luma and chroma ratios and initial phases, bottom-field phase values, rounding offsets, scaler update lock/status, viewport start/size for primary/secondary and chroma paths, overscan extents, and mode-change detection.
- `COL_MAN1_*`: pipe-1 color-management update locking, input/output CSC mode and A/B coefficient matrices, prescale controls, denorm/clamp ranges, floating-point converted-field access, regamma control/LUT/index/write-enable fields, regamma region definitions for CNTLA/CNTLB, FIFO error ack fields, input-gamma LUT autofill/read-write/data controls, black/white offsets, degamma control, and gamut-remap matrix fields.
- `DCFEV1_DCFEV_*`: pipe-1 display front-end clock gates, soft resets for UNP/SCLV/CRTC/PSCLV/COL_MAN, DMIFV clock and soft reset, DMIFV and block memory power force/disable/status controls, luma/chroma flush indicators, and miscellaneous self-refresh ECO enable.
- `DC_PERFMON12_*`: DCE display performance-counter event selection, counter value selection, run/interrupt/restart/off-mask control, counter state/status, performance-monitor mode/control, compare-value interrupt fields, and high/low counter readout registers.
- `DMIFV_PG1_DPGV0_*` and `DMIFV_PG1_DPGV1_*`: display memory-interface arbitration, urgency watermarks, DPM enable, stutter and non-latched stutter controls, northbridge P-state change controls, repeater programming, and DMIF buffer pre-check disable for two DPGV instances.
- `BLNDV1_BLNDV_*`: pipe-1 blender gain/mode/stereo/alpha/feedthrough controls, stereo-matrix controls, pixel transport and SuperAA degamma/regamma controls, update locks, underflow interrupt ack/mask/pipe-index fields, V-update lock aggregation, and register-update pending status for graphics, surface, cursor, scaler, and blender clients.
- `CRTCV1_CRTCV_*`: pipe-1 timing generator fields for horizontal/vertical totals, blanking and sync windows, polarity controls, vertical-total min/max and events, trigger A/B selection/status/clear, force-count/force-vsync controls, flow control, AV sync, master enable, blank/interlace/stereo controls, status/readback counters, snapshot controls, start-line and interrupt control, double-buffering, VGA capture, test pattern, master-update lock/mode, MVP in-band status, overscan/blank/black colors, vertical interrupt 0/1/2, CRC windows/data, and external timing sync control/window fields.

The chunk is boundary-split: it starts after the first fields of `CRTCV0_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` and ends after the first four `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` shift macros. Neighboring chunks are needed for the complete definitions of those two register groups.

## Control Flow

This header has no runtime control flow. Each line is a compile-time constant used by other AMDGPU display code.

Typical consumer control flow is:

1. Display code computes a software state such as mode timing, framebuffer address, tiling, scaling ratio, CSC matrix, gamma curve, power-management watermark, vblank interrupt policy, or CRC capture window.
2. The state is converted to field values, often using companion enum headers and block-specific programming helpers.
3. A register value is built by shifting values by the `__SHIFT` constants and constraining them with the matching `_MASK` constants.
4. The value is written through AMDGPU/DAL register helpers such as direct register macros or `REG_UPDATE`-style field update helpers.
5. Hardware latches the state immediately, at vertical update, after an update lock is released, after an interrupt ack/clear, or after a reset/power transition depending on the target register.

Several field groups represent synchronization points rather than simple configuration: `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `*_UPDATE_LOCK`, `*_ACK`, `*_CLEAR`, `*_OCCURED`, `*_INT_STATUS`, `*_FORCE`, and `*_STATE` fields are normally used in polling, interrupt handling, or sequenced modeset flows.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes state that lives in DCE 12.0 display hardware registers and in driver programming conventions.

Hardware state represented by this chunk includes:

- Scanout/underlay state: graphics enable, pixel depth/format, tiling layout, luma/chroma addresses, pitch, viewport coordinates, pending surface flips, stereo/interlace flip state, DVMM PTE behavior, and hardware rotation.
- Line-buffer state: pixel expansion/reduction/dither/prefetch policy, memory sizing, vertical line windows, vblank/vline interrupt flags, keyer colors, FIFO levels, urgency marks, and outstanding request completion.
- Scaler state: coefficient RAM selection/data, tap counts, luma/chroma scale ratios, initial phases for top/bottom fields, viewport and overscan extents, update lock state, and mode-change detection status.
- Color pipeline state: input/output CSC matrices, prescale and clamp values, degamma/regamma/gamut-remap modes, regamma LUT and region programming, input gamma LUT data and access mode, and FIFO underflow/overflow state.
- Front-end and memory-interface state: clock-gate disables, soft reset assertions, memory power force/disable/select/status bits, flush/deep-flush state, arbitration weights, DPM/stutter controls, self-refresh and NB P-state watermarks, and DMIF buffer checks.
- Blender and timing-generator state: alpha/stereo/feedthrough modes, update locks, underflow interrupts, CRTC horizontal/vertical timing, sync polarity, trigger inputs, AV sync counters, blanking/interlace/stereo flags, snapshot counters, vertical interrupt positions, CRC windows/data, test pattern controls, external timing sync windows, and static-screen/3D/GSL state inherited from the pipe-0 tail.

Persistence is register-specific. Many configuration bits persist until modeset, atomic commit, suspend/resume, GPU reset, display block reset, or runtime power management reprograms them. Status and interrupt fields are transient and may be level-sensitive, edge-latched, or write-one-to-clear depending on the register. Update-lock and double-buffer bits affect when pending writes become visible; power and reset bits can invalidate assumptions about downstream register contents.

## Dependencies And Integration Points

This file depends on AMD's generated ASIC register database. The constants in this chunk are meaningful only with the corresponding DCE 12.0 register address headers and enum headers in the same directory tree, especially generated `dce_12_0_*_d.h`, `dce_12_0_enum.h`, and adjacent sections of `dce_12_0_sh_mask.h`.

Important integration points include:

- AMDGPU Display Core and legacy DCE register programming paths that include generated shift/mask headers to implement modesets, page flips, color programming, interrupts, and power sequencing.
- DRM/KMS atomic state and framebuffer setup, where surface addresses, pitch, tiling, pixel format, viewport, scaler, color, and blender state are translated into `UNP1`, `LBV1`, `SCLV1`, `COL_MAN1`, and `BLNDV1` registers.
- Timing-generator and vblank handling code, where `CRTCV1` timing totals, blank/sync windows, status counters, vertical interrupts, snapshot, force-vsync, and update-lock fields drive CRTC enable/disable and event delivery.
- Display power-management and watermark calculations, where `DMIFV_PG1` arbitration, urgency, stutter, DPM, self-refresh, NB P-state, and `DCFEV1` memory-power fields are programmed from bandwidth and clock-state decisions.
- Color-management paths for CSC, degamma/regamma LUTs, gamut remap, clamp, and gamma LUT programming.
- Diagnostics and validation paths, including `UNP1` and `CRTCV1` CRC capture, `DC_PERFMON12` counters, test patterns, pixel readback, FIFO error status, and underflow interrupts.

The register fields also integrate with interrupt-service code. `UNP1_UNP_GRPH_INTERRUPT_*`, `LBV1_LBV_*_STATUS`, `BLNDV1_BLNDV_UNDERFLOW_INTERRUPT`, and `CRTCV1_CRTCV_*_INT*` fields provide mask, type, status, ack, and clear bits that must match the kernel's IRQ enable and acknowledgement ordering.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped integer macros; a wrong shift or mask can compile cleanly while corrupting a neighboring field or programming the wrong hardware behavior.

High-risk areas include:

- Surface address and layout fields. Incorrect address shifts, high-address masks, pitch, tiling, bank geometry, pipe config, array mode, endian swap, or luma/chroma split handling can cause blank scanout, corrupted images, channel swaps, page faults, or reads from the wrong framebuffer.
- Update synchronization. Misusing `*_UPDATE_LOCK`, `*_PENDING`, `*_TAKEN`, `*_DOUBLE_BUFFER`, and vertical-update lock fields can make atomic commits tear, remain pending indefinitely, or update only part of the pipe.
- Interrupt acknowledgement. `*_ACK`, `*_CLEAR`, `*_MASK`, `*_INT_STATUS`, and `*_INT_TYPE` fields are easy to confuse. Clearing before software samples status can lose vblank, vline, page-flip, underflow, trigger, snapshot, or external-sync events; failing to clear can flood IRQ handling.
- Watermark and memory-interface programming. Bad urgency, stutter, self-refresh, NB P-state, DPM, or arbitration values can produce display underflows, memory power transition failures, flicker during clock changes, or excessive power draw.
- Clock, reset, and memory-power controls. Asserting soft resets or forcing memory power states while a pipe is active can blank displays or leave dependent blocks in inconsistent state. Status fields must be polled or sequenced according to hardware rules not captured by this header.
- Color pipeline programming. CSC, regamma, input gamma, gamut remap, clamp, LUT index/data, and write-enable fields are dense and repetitive. Copy/paste or generation errors can produce wrong colors, banding, HDR/SDR range errors, or FIFO errors.
- CRTC timing fields. Off-by-one or mask-width mistakes in totals, blanking, sync, vertical interrupts, CRC windows, and external timing sync windows can break mode validation, vblank timing, CRC tests, stereo/interlace behavior, or synchronization to external sources.
- Chunk boundary splits. A reader looking only at this chunk will not see the complete `CRTCV0_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` or `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` definitions. The merge lane should reconcile those with adjacent chunks before making per-register conclusions.

## Test Signals

Useful validation signals are mostly compile-time, generated-header, and hardware-behavior oriented:

- Kernel build coverage for DCE 12.0 display code that includes this header; renamed or missing field macros should fail compilation.
- Generated-register-map comparison against AMD's authoritative DCE 12.0 register database, verifying every shift and mask in lines 32325-34820.
- Modeset tests across multiple resolutions, refresh rates, interlace/progressive modes, stereo modes, blanking/sync polarities, and vertical interrupt positions.
- Page-flip and atomic commit tests that check `UNP1` surface update pending/taken state, update locks, in-use addresses, and vblank event delivery.
- Framebuffer format and tiling tests covering luma/chroma planes, bottom-field addresses, endian/channel crossbar behavior, pitch, offsets, hardware rotation, and DVMM/PTE cases.
- Scaler and viewport tests covering luma/chroma ratios, taps, coefficient RAM programming, overscan, bottom-field initialization, mode-change detection, and coefficient update completion.
- Color-management tests for input/output CSC matrices, prescale, denorm/clamp, regamma LUT and region setup, input gamma LUT access/autofill, degamma, and gamut remap.
- Underflow and power-management tests that exercise `LBV1`, `BLNDV1`, `DCFEV1`, and `DMIFV_PG1` status fields under high bandwidth, clock changes, stutter/self-refresh, suspend/resume, and GPU reset.
- CRC and test-pattern diagnostics verifying `UNP1` CRC, `CRTCV1` CRC0/CRC1 windows/data, pixel readback, and test pattern color/dynamic-range fields.
- Interrupt tests for vblank, vline/vline2, page flip, snapshot, vertical interrupts 0/1/2, trigger A/B, force-vsync, underflow, and external timing sync loss/status.

Regression symptoms from incorrect constants include corrupted or blank scanout, wrong colors, missed or repeated vblank/page-flip events, stuck update locks, display underflows, failed CRC validation, bad scaling, failed suspend/resume recovery, excess power use, or unstable external synchronization.

## Cross-Chunk Notes

This is one chunk of the large generated `dce_12_0_sh_mask.h` register map. Earlier chunks define preceding DCE 12.0 register field maps and the beginning of pipe-0 CRTC external timing sync loss control. Later chunks complete `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` and continue the remaining pipe-1 CRTC and subsequent display blocks. The final per-file document should treat this as generated hardware ABI metadata, not as a standalone module with independent initialization or control flow.

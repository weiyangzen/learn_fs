# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 29826-32324

## Purpose

This chunk is a generated AMD DCE 12.0 shift/mask register header section. It contains C preprocessor constants only; there are no functions, structs, storage objects, or executable algorithms. The constants define bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-engine registers used by AMDGPU display programming.

The range starts at the tail of the `dce_dc_fmt5_dispdec` formatter block, then covers a full video/underlay display pipe path for instance 0: `UNP0`, `LBV0`, `SCLV0`, `COL_MAN0`, `DCFEV0`, `DC_PERFMON11`, `DMIFV_PG0`, `BLNDV0`, and the beginning of `CRTCV0`. These blocks describe how software programs surface fetch, line buffers, scaling, color management, clock/power/reset, performance monitoring, display memory interface watermarks, blending, timing generation, interrupts, CRC capture, and external timing synchronization.

The header is hardware ABI metadata. Consumer code combines these masks and shifts with the matching register offsets from `dce_12_0_offset.h` and enum values from related DCE headers, then reads or writes GPU registers through AMDGPU/DAL register helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public surface is a large set of `#define` names following this pattern:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same register field after shifting.

Major register families in this chunk are:

- `FMT5_FMT_*`: formatter instance 5 fields for bit-depth control, dither random seeds, clamp control, formatter CRC setup/signature registers, side-by-side stereo active width, and 4:2:0 horizontal blank early start. These fields participate late in the display pipe where pixels are clamped, dithered, optionally CRC-sampled, and formatted for output.
- `UNP0_UNP_GRPH_*`: underlay/graphics plane fields for enabling scanout, selecting graphics depth/format, tiling/banking, pipe configuration, endian and RGB crossbar swaps, luma/chroma primary and secondary surface addresses, bottom-field addresses, high address bits, pitch, source offsets, source rectangle start/end, update locking, in-use surface readback, stereo flip state, page-flip interrupt state, CRC capture, line-buffer gap, and hardware rotation.
- `UNP0_UNP_DVMM_*`: virtual-memory PTE behavior for luma and chroma planes, including single-PTE use, page width/height, minimum PTEs before flip, PTE buffer modes, PTE requests per chunk, and outstanding PTE request limits. These fields connect surface flip/display fetch to GPU memory translation.
- `LBV0_LBV_*`: line-buffer vertical block fields for pixel depth/expansion/reduction, interleave, dynamic pixel depth, dither, prefetch, request mode, alpha enable, memory control/size, desktop height, vertical line interrupt windows, vertical counters and snapshot counters, interrupt masks, vline/vblank status and ack bits, reset selection, black/keyer color controls, buffer level/urgency/status, and no-outstanding-request status.
- `SCLV0_SCLV_*`: scaler vertical block fields for coefficient RAM selection/data, scaler mode, tap counts, boundary/early-EOL/phase controls, manual and automatic replicate/ratio calculation, horizontal and vertical filter ratios and initial phases for luma and chroma, bottom-field initial phases, round offsets, update lock/taken/pending status, viewport start/size for primary/secondary and chroma planes, extended overscan, and mode-change detection/ack.
- `COL_MAN0_*`: color-management fields for update locking, input CSC mode/type/conversion, input and output CSC matrix coefficients for A/B banks, prescale mode and RGB bias/scale values, output CSC mode, denorm clamp, floating-point converted-field access, regamma control and LUT index/data/write masks, piecewise regamma regions for A/B banks, pack/output FIFO errors and acks, input gamma LUT autofill/index/data/color, input gamma control, black/white offsets, degamma mode, gamut-remap mode, and gamut-remap matrix coefficients.
- `DCFEV0_*`: front-end vertical block clock gating, block soft reset, DMIFV clock/reset/buffer mode, DMIFV and local memory power control/status, memory-power mode selection, luma/chroma flush status and clear bits, and miscellaneous self-refresh allowance.
- `DC_PERFMON11_*`: display performance monitor counter fields for event selection, current-value selection, increment/run/offset/restart/interrupt controls, counter state, performance monitor control, current-value interrupt thresholds/status/clear, and low/high counter value readback.
- `DMIFV_PG0_DPGV0_*` and `DMIFV_PG0_DPGV1_*`: display memory interface pipe-group fields for arbitration weights, watermark masks, urgency low/high watermarks, DPM enable, stutter/self-refresh controls, NB P-state change controls, non-latched stutter controls, repeater programming, and pre-processing buffer-check disable. Both DPGV0 and DPGV1 expose the same shape for two pipe-group instances.
- `BLNDV0_BLNDV_*`: blender vertical block fields for global gain/alpha, blend mode, stereo type/polarity, feedthrough, alpha mode, overlap-only and premultiplied behavior, stereo matrix control, pixel-through-insert/new-pixel controls, update locking, underflow interrupt status/ack/mask/pipe index, V-update locking across graphics/surface/cursor/scaler/blender clients, and aggregate register-update status.
- `CRTCV0_CRTCV_*`: beginning of timing-generator instance 0 fields for horizontal and vertical totals, blanking and sync windows, sync polarities, VBI end, dynamic vertical total min/max/control, vertical-total and nominal-vsync interrupt status, DTM test controls, trigger A/B controls and manual trigger, force-count-now, flow control, stereo force/AV-sync counters, CRTC enable/control/status, blank/interlace/field control, pixel readback, count/reset/snapshot/status readback, stereo control/status, update locks, test pattern programming, master update controls, MVP in-band control insertion, master enable, V-update interrupt status, overscan/blank/black colors including extension bits, vertical interrupt positions/controls, CRTC CRC setup/windows/data, and external timing sync control/window/loss interrupt fields.

## Control Flow

This header chunk has no runtime control flow. It contributes symbolic bit positions and masks that are consumed by display driver code.

A typical runtime use pattern outside this header is:

1. AMDGPU display code computes a modeset, plane, scaling, color, memory, or timing state from DRM state and hardware capabilities.
2. The driver selects the corresponding register address from `dce_12_0_offset.h`, such as `mmUNP0_UNP_GRPH_UPDATE`, `mmSCLV0_SCLV_UPDATE`, `mmCOL_MAN0_COL_MAN_UPDATE`, `mmCRTCV0_CRTCV_CONTROL`, or `mmDMIFV_PG0_DPGV0_PIPE_STUTTER_CONTROL`.
3. It inserts field values using the `__SHIFT` and `_MASK` constants in this header, often via `REG_UPDATE`, `REG_SET`, `dm_read_reg`, `dm_write_reg`, `RREG32`, or `WREG32` style helpers.
4. Hardware latches some values immediately and others only when update-lock and vertical-update rules are satisfied.
5. Status, pending, taken, interrupt, CRC, counter, and in-use fields are later read back through the same field definitions.

Several block families show explicit sequencing constraints through their field names:

- `*_UPDATE` registers have pending/taken/lock bits (`UNP0_UNP_GRPH_UPDATE`, `SCLV0_SCLV_UPDATE`, `COL_MAN0_COL_MAN_UPDATE`, `BLNDV0_BLNDV_UPDATE`). These imply that mode, surface, coefficient, color, and blender updates are intended to be staged and latched atomically.
- Interrupt/status registers pair event bits with clear or ack bits, such as `UNP0_UNP_GRPH_INTERRUPT_STATUS`, `LBV0_LBV_VLINE_STATUS`, `COL_MAN0_PACK_FIFO_ERROR`, `BLNDV0_BLNDV_UNDERFLOW_INTERRUPT`, `CRTCV0_CRTCV_V_TOTAL_INT_STATUS`, and `CRTCV0_CRTCV_VERTICAL_INTERRUPT*_CONTROL`.
- Memory and power control registers pair force/disable/select fields with status fields, such as `DCFEV0_DCFEV_DMIFV_MEM_PWR_CTRL` and `DCFEV0_DCFEV_DMIFV_MEM_PWR_STATUS`.
- CRC and performance monitor fields require enable/select programming followed by readback from result registers (`UNP0_UNP_CRC_*`, `FMT5_FMT_CRC_*`, `CRTCV0_CRTCV_CRC*`, `DC_PERFMON11_*`).

## State And Persistence Behavior

The header itself stores no state and persists nothing. The state described by these macros lives in GPU display registers and in the driver state that decides what to write.

Important hardware state represented by this chunk includes:

- Formatter output processing state: truncation, spatial/temporal dithering, random seeds, clamp enable and color format, formatter CRC enable/mode/window/signature state, stereo active width, and 4:2:0 blanking alignment.
- Plane fetch state: plane enable, pixel format/depth, tiling, bank geometry, pipe configuration, address translation, privileged access, endian/channel crossbar, surface addresses for luma/chroma primary/secondary/top/bottom fields, pitch, offsets, source rectangle, surface-update locks, in-use surface addresses, flip-pending state, page-flip interrupt state, and hardware rotation.
- Display virtual-memory fetch state: PTE page dimensions, PTE buffering, minimum PTEs before flip, request chunking, and outstanding PTE limits for luma and chroma.
- Line-buffer state: pixel format expansion/reduction, prefetch/request behavior, vertical counter snapshots, vline/vblank event state, buffer occupancy and urgency, black/keyer color values, reset selection, and outstanding request completion.
- Scaler state: coefficient RAM contents, selected filter type/phase/tap pair, tap counts, scale ratios, initial phases for luma/chroma and top/bottom fields, viewport geometry, overscan, update locks, and mode-change detection.
- Color state: CSC matrices, prescale values, denorm clamp, regamma LUT and piecewise region descriptors, input gamma LUT/control, black/white offsets, degamma/gamut-remap modes and coefficients, and FIFO error status.
- Front-end and memory-power state: clock gating, soft reset assertion, DMIFV clock/reset, buffer mode, memory power force/disable/mode selection, memory power status, and luma/chroma flush completion.
- Memory-interface state: pipe arbitration, urgency and stutter watermarks, DPM and self-refresh behavior, NB P-state change allowance, and DPG repeater/check behavior.
- Blender state: blend mode, alpha policy, stereo policy, feedthrough, super-AA degamma/regamma, underflow interrupt state, and cross-block V-update locks/status.
- Timing generator state: active timing totals and sync positions, dynamic refresh/vertical total controls, triggers, flow control, AV sync/stereo status, CRTC enable/blank/interlace/test pattern/master update state, scanout position counters, interrupt enables/clears, CRC windows/results, and external timing sync state.

Persistence is register-specific. Many fields persist until a modeset, plane update, color update, reset, suspend/resume, runtime power transition, or GPU reset changes them. Pending/status/interrupt/ack/clear fields are transient and may be consumed or cleared by hardware or interrupt handlers. In-use surface address and counter fields are readback snapshots of live hardware state rather than durable software state. LUT, coefficient, and matrix fields persist in display-block memory/registers while the block remains powered, but they can be lost or invalidated by display block reset or power-gating transitions.

## Dependencies And Integration Points

This chunk depends on the generated DCE 12.0 register contract. Its constants are meaningful only with sibling address and enum headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/`, especially:

- `dce_12_0_offset.h`, which provides `mm*` register addresses and base-index macros for the register names defined here.
- Other `dce_12_0_*` headers that provide related register definitions and any enum/value encodings used in these fields.
- Earlier and later sections of `dce_12_0_sh_mask.h`, because this chunk starts in the middle of `FMT5` and ends in the middle of `CRTCV0`; complete per-file research must merge this chunk with neighboring chunks.

Primary integration points are AMDGPU display and Display Core code paths that program DCE hardware:

- DRM plane and framebuffer setup maps DRM formats, tiling metadata, pitches, GPU addresses, source rectangles, and stereo/rotation state into `UNP0_UNP_GRPH_*`, `UNP0_UNP_DVMM_*`, and `LBV0_LBV_*` fields.
- Atomic update paths coordinate `UNP0`, `SCLV0`, `COL_MAN0`, `BLNDV0`, and `CRTCV0` update locks so visible state changes latch coherently on vblank/update boundaries.
- Scaling setup writes `SCLV0` taps, filter ratios, coefficient RAM, viewport geometry, chroma-specific geometry, and overscan.
- Color-management setup writes `COL_MAN0` CSC, prescale, clamp, degamma, regamma, input gamma, and gamut-remap fields.
- Display memory bandwidth and power-management code programs `DMIFV_PG0` arbitration/watermark/stutter/P-state fields and `DCFEV0` memory power/clock/reset fields.
- Interrupt handlers and vblank/event code interact with `LBV0`, `UNP0`, `BLNDV0`, and `CRTCV0` status/ack/clear fields.
- Debug and validation tooling uses CRC registers in `FMT5`, `UNP0`, and `CRTCV0`, performance monitor 11 registers, timing status counters, snapshot registers, test pattern registers, and pixel readback fields.

Although the path is under a `ceph-client` source mirror, this file is AMD GPU display hardware metadata. It does not implement Ceph filesystem behavior, network protocols, storage replication, distributed locking, or persistent filesystem state.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are plain integer macros; a wrong mask, wrong shift, stale generated value, or mismatched register address can compile successfully while causing display corruption, blank screens, hangs, lost interrupts, or power-management failures.

High-risk areas in this chunk include:

- Surface address and format programming. `UNP0_UNP_GRPH_*ADDRESS*`, pitch, tiling, pipe config, bank geometry, luma/chroma pairing, source offsets, and graphics format fields must match the actual framebuffer allocation and memory layout. Bad values can fetch the wrong memory, produce color/channel corruption, trigger memory faults, or underflow the display pipe.
- Virtual-memory display fetch. `UNP0_UNP_DVMM_*` PTE dimensions, minimum-PTE-before-flip, and outstanding request limits affect flip safety and memory-translation latency. Incorrect tuning can cause page flips before enough PTEs are ready, visible corruption, underflow, or faults during scanout.
- Update locking. `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `BLNDV0_BLNDV_V_UPDATE_LOCK`, and `CRTCV0_CRTCV_UPDATE_LOCK` fields are used to align multi-register updates with display timing. Missing or incorrectly ordered locks can expose partially updated surfaces, scaler ratios, color matrices, or timing state.
- Interrupt ack and clear bits. Fields named `ACK`, `CLEAR`, `INT_CLEAR`, or status masks may be write-one-to-clear or otherwise edge-sensitive depending on hardware semantics. A read-modify-write that preserves an ack bit accidentally, or clears before software records state, can lose vblank, vline, underflow, page-flip, vertical-total, external-sync, or FIFO error events.
- Color pipeline precision. CSC, prescale, denorm clamp, LUT, regamma region, degamma, and gamut-remap fields encode signed/fixed-point hardware formats. Off-by-one ranges, wrong coefficient bank, wrong write mask, or wrong LUT index sequencing can cause incorrect gamma, color-space conversion, clipping, banding, or invalid HDR/SDR presentation.
- Scaler coefficient and viewport programming. Coefficient RAM selection/data, tap counts, ratios, initial phases, chroma-specific ratios, and bottom-field phases must be consistent with source dimensions, interlace state, and 4:2:0 formats. Bad values can cause shimmering, line phase errors, chroma misalignment, or scaler mode-change events.
- Memory-interface watermarks. `DMIFV_PG0_DPGV*` urgency/stutter/NB P-state/self-refresh fields directly affect bandwidth and power behavior. Underestimated watermarks can cause underflow; overconservative values can block power savings or clock transitions.
- Clock, reset, and memory power controls. `DCFEV0` soft reset and power fields can invalidate state in dependent blocks. Programming these fields while a pipe is active, or failing to reinitialize LUT/coeff/state after reset or power gating, can break scanout.
- Timing generator programming. `CRTCV0` totals, blanking, sync, dynamic vertical total, trigger, flow control, stereo, interlace, and external timing sync fields are timing-sensitive. Invalid combinations can violate mode timings, break vblank accounting, interfere with variable refresh, or destabilize genlock/external sync.
- CRC and test/debug registers. CRC windows, select fields, continuous/one-shot modes, performance counters, test patterns, pixel readback, and DTM test fields can alter validation behavior and should not be left enabled unintentionally in normal modeset paths.

Generated-header maintenance is also risky. The same register names appear with addresses in `dce_12_0_offset.h`; masks here must remain synchronized with those addresses and with hardware documentation. Since the chunk starts after the beginning of `FMT5` and stops before the end of `CRTCV0`, reviewers need neighboring chunks before making whole-file conclusions.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for AMDGPU display code that includes DCE 12.0 headers, catching missing or renamed macros.
- Modeset tests across common RGB and YUV/4:2:0 formats, tiled and linear framebuffers, multiple pitches, primary/secondary surfaces, stereo/interlace paths, and hardware rotation.
- Plane update and page-flip tests that verify pending/taken bits drain and no partial updates appear during atomic commits.
- CRC-based display tests using `FMT5`, `UNP0`, or `CRTCV0` CRC registers to confirm deterministic output for known framebuffers and color/scaler settings.
- Color-management tests for CSC matrices, gamma/degamma/regamma LUT programming, gamut remap, clamp ranges, and 10/12-bit paths.
- Scaler tests covering up/downscale ratios, luma/chroma viewports, coefficient loading completion, interlaced bottom-field initialization, and overscan.
- Interrupt tests for vblank/vline/page-flip/underflow/vertical-total/external-sync events, including verifying ack/clear behavior and absence of interrupt storms.
- Memory-bandwidth and power tests that exercise DPM, stutter, self-refresh, NB P-state changes, and watermark programming under high-resolution/high-refresh modes.
- Suspend/resume, runtime power management, GPU reset, and display hotplug tests that verify clock/reset/memory-power state is restored and no stale LUT/coefficient/surface state remains.
- Debug/performance monitor tests that confirm performance counter start/stop/restart/threshold behavior and CRTC status counter readback under active scanout.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 22342-24835

## Purpose

This chunk is a generated AMDGPU DCE 12.0 display-engine shift/mask header section. It contains no executable C functions; it publishes compile-time `#define` constants that describe bit positions and bit masks for memory-mapped display controller registers. Driver code combines these field macros with address macros from `dce_12_0_offset.h` and generic register helpers to read, write, and update hardware fields safely.

The assigned range starts at the tail of the DCP3 cursor update field list, then covers several complete DCE pipe-3 register blocks: DCP3 color/cursor/CRC/DVMM/XDMA fields, line buffer `LB3`, display front-end `DCFE3`, performance monitor `DC_PERFMON6`, display memory interface `DMIF_PG3`, scaler `SCL3`, blender `BLND3`, CRTC timing generator `CRTC3`, formatter `FMT3`, and the beginning of DCP4 graphics-plane/color fields. The range ends mid-family after `DCP4_COMM_MATRIXB_TRANS_C13_C14__COMM_MATRIXB_TRANS_C13_MASK`; the continuation of DCP4 matrix B and later DCP4 fields belongs to the next chunk.

## Important APIs, Types, And Macros

The API surface is the macro namespace. Every field generally has a pair:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask in the 32-bit MMIO register value.

The chunk contains no structs, enums, functions, storage, or inline logic. Its value is in exact hardware ABI names and encodings. Important register families in this chunk are:

- `DCP3_CUR_*`: cursor request filtering and stereo offsets, plus inherited cursor update lock/pending/taken fields from the chunk boundary.
- `DCP3_DC_LUT_*` and `DCP3_REGAMMA_*`: input/display LUT programming, LUT read/write mode/index/data, 10-bit color packing, per-channel black/white offsets, autofill status, regamma LUT index/data/write-enable, and dual regamma region programming tables `CNTLA` and `CNTLB`.
- `DCP3_DCP_CRC_*`, `DCP3_GRPH_XDMA_*`, and `DCP3_GRPH_SURFACE_COUNTER_*`: DCP CRC controls/current/last values, XDMA underflow/timeout/average-delay diagnostics, recovery surface address, interrupt/ack bits, and graphics surface event counters.
- `DCP3_DVMM_*`, `DCP3_DCP_GSL_CONTROL`, `DCP3_GRPH_FLIP_RATE_CNTL`, `DCP3_GRPH_STEREOSYNC_FLIP`, `DCP3_HW_ROTATION`, and `DCP3_ALPHA_CONTROL`: virtual-memory PTE sizing/arbitration, genlock/swaplock synchronization, flip pacing, stereo flip pending state, hardware rotation, and cursor alpha blending.
- `LB3_*`: line-buffer pixel format/depth/alpha, memory size/configuration, vline/vblank interrupt masks and status/ack fields, sync reset selection, keyer colors, buffer level/urgency/empty/full status, no-outstanding-request status, and MVP/AFR flip controls.
- `DCFE3_*`: display front-end clock gating, soft reset, memory power control/status, and flush control, including many per-memory-bank power fields.
- `DC_PERFMON6_*`: eight performance-counter control/select/state fields, global performance monitor state, counter-off interrupt status/ack, counter value high/low reads, and per-counter interrupt status/ack fields.
- `DMIF_PG3_*`: DPG arbitration weights, watermark mask selection, urgent/stutter/self-refresh/P-state controls, repeater programming, preprocessor check disable, and DVMM forced-flip status/clear fields.
- `SCL3_*`: coefficient RAM selection/data, scaler mode/tap/bypass/replication/automatic-ratio controls, horizontal/vertical ratios and initial phases, round offsets, update lock/pending/taken fields, sharpening, ALU disable, coefficient conflict interrupt/ack, viewport/overscan geometry, and mode-change detection/masking.
- `BLND3_*`: blender global gain/alpha/mode/stereo controls, state-machine controls, pixel timing improvement and SuperAA controls, update lock/pending/taken fields, underflow interrupt fields, vertical update locks spanning DCP/SCL/BLND, and aggregate register-update status.
- `CRTC3_*`: timing totals, blank/sync windows, min/max vertical total and DRR support, triggers A/B, force-count-now, flow control, stereo/AV sync, CRTC enable/blank/interlace/status counters, snapshots, start-line and interrupt controls, update locks, double buffering, VGA parameter capture, test patterns, master update locks/modes, MVP in-band status, vupdate/vblank-like interrupt positions, colors, CRC windows/data, external timing sync, static screen status, 3D structure, GSL timing, range timing status, and DRR controls.
- `FMT3_*`: formatter clamp limits, dynamic expansion, pixel encoding/subsampling, 4:2:0 phase status/clear, truncation/spatial/temporal dithering, random seeds, clamp control, formatter CRC control/signatures/masks, side-by-side stereo width, and 4:2:0 hblank early-start.
- `DCP4_*`: first part of pipe-4 graphics plane programming, including enable/control/tiling/swizzle metadata, surface addresses and pitch, offsets and extents, input gamma, graphics update/flip controls, DFQ status/reset, page-flip interrupts, compression surface metadata, outstanding request limit, prescale, input/output CSC matrices, and the start of common color transformation matrices.

## Control Flow

There is no local runtime control flow. The control flow is imposed by consumers that include `dce_12_0_sh_mask.h` and use macros such as `FD(reg__field)` through register helpers. For example, DCE 12.0 timing code includes this file and `dce_12_0_offset.h`, then uses CRTC register update wrappers around `generic_reg_update_soc15()` and `generic_reg_set_soc15()`; resource code derives per-pipe offsets such as `mmCRTC3_CRTC_CONTROL - mmCRTC0_CRTC_CONTROL`; IRQ code builds interrupt register descriptors from address and mask macros.

Several macro groups encode hardware sequencing even though this header does not implement the sequence:

- Update paths use `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `*_UPDATE_LOCK`, `*_DISABLE_MULTIPLE_UPDATE`, master update locks, and vertical update lock fields. Consumers must program related registers while locked and then release/update in the right vertical timing window.
- Interrupt/status paths use `*_OCCURRED`, `*_STATUS`, `*_INT`, `*_MASK`, `*_CLEAR`, and `*_ACK` fields across CRTC, LB, BLND, FMT, DCP/XDMA, perfmon, and external timing sync. These fields are often sticky or write-one-to-clear at the hardware level.
- Memory and power paths use DMIF watermarks, stutter/self-refresh, P-state change, DVMM, DCFE memory power, line-buffer urgency, and DCP outstanding-request fields. Driver sequencing has to match display mode, memory clock, and surface layout.
- Color and scaling paths write LUTs, regamma regions, CSC matrices, scaler coefficients, formatter dither/clamp controls, and viewport geometry. Updates must be synchronized to avoid visible tearing, wrong color, or inconsistent scaler coefficients.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It is generated static metadata consumed at compile time.

The represented state lives in DCE 12.0 hardware registers after MMIO writes. Some fields are durable configuration until the next modeset, plane update, suspend/resume reprogramming, display pipe reset, or GPU reset. Examples include CRTC timings, scaler ratios, color matrices, LUT modes, DMIF watermarks, line-buffer memory layout, DCP surface format, and formatter dithering.

Other fields reflect transient or sticky hardware state: update pending/taken bits, vblank/vline/vertical interrupt occurrence, trigger occurrence, CRC data, current counters, underflow/timeout status, perfmon counter values, power status, buffer level/urgency status, and mode-change detection. Clear/ack fields are state-transition controls rather than persistent settings. The macros do not encode access type, reset value, polling requirements, or write-one-to-clear semantics; those are owned by the hardware specification and call-site logic.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCE 12.0 register-header contract. The practical pair is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`, where matching `mm...` address macros and base indices are defined. It is also tied to the generated enum/value headers and to SOC15 base-address definitions used by DCE 12.0 display code.

Direct source-tree include points for DCE 12.0 offset and shift/mask headers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

The functional integration surface is AMD display core for Vega/DCE 12.0-era hardware: mode set, page flip, cursor, scaler, color management, line-buffer programming, DMIF/watermark and low-power behavior, interrupts, CRC capture, underflow diagnostics, and pipe synchronization. The path is under a local `ceph-client` source mirror, but this chunk is AMDGPU display hardware metadata, not Ceph filesystem logic.

## Risks And Edge Cases

- Bit masks and shifts are hardware ABI. A single wrong value can compile cleanly while corrupting unrelated register fields or leaving the intended field unchanged.
- The range is highly repetitive across pipe instances. DCP3, LB3, SCL3, BLND3, CRTC3, FMT3, and DCP4 names differ mainly by block index, making generator or manual review mistakes hard to spot.
- The chunk begins and ends inside larger register families. The first lines continue `DCP3_CUR_UPDATE`, and the last lines stop in `DCP4_COMM_MATRIXB_TRANS_C13_C14`; per-file synthesis must merge adjacent chunks before treating the DCP3 cursor or DCP4 matrix coverage as complete.
- `*_MASK_MASK` identifiers are legitimate generated names for fields whose hardware name itself ends in `MASK`; they should not be simplified or deduplicated.
- Acknowledgement, clear, reset, and interrupt mask fields often have different polarity from ordinary enable fields. Misuse can leave interrupts stuck, drop vblank/vline events, fail to clear underflow/timeouts, or mask critical diagnostics.
- Update-lock misuse can produce partial plane, scaler, blender, or CRTC programming on a live scanout. Relevant fields include DCP graphics/cursor update locks, SCL update lock, BLND update lock, BLND vertical update lock, CRTC update/master update locks, and formatter or CRTC double-buffered state.
- DMIF, line-buffer, DCFE power, and DVMM fields are timing- and memory-sensitive. Bad watermarks, stutter/P-state settings, PTE parameters, or buffer limits can appear as underflow, flicker, page-flip delay, self-refresh instability, or resume failures.
- Color/scaler fields are packed signed/fixed-point or table-index values. Incorrect shifts for LUT deltas, regamma regions, CSC matrices, prescale bias/scale, scaler ratios, or dither controls can cause subtle image-quality regressions rather than obvious failures.
- CRTC timing and synchronization fields affect global display behavior. Wrong total/blank/sync, DRR, external timing sync, stereo, GSL, or trigger fields can break mode validation, genlock/swaplock, frame pacing, stereo output, or multi-display synchronization.

## Test Signals

Useful validation is mostly build-time plus hardware/display runtime behavior:

- Kernel or targeted AMDGPU display builds should compile all DCE 12.0 include users without missing macro names, duplicate definitions, or syntax issues.
- Generated-register validation can compare every `__SHIFT`/`_MASK` pair in this chunk against AMD's source register database and against the adjacent `dce_12_0_offset.h` address names.
- Modeset tests should cover pipe 3 and pipe 4 usage across common resolutions, interlaced/progressive modes, stereo/3D modes, DRR, external timing sync, and multi-display synchronization.
- Plane/page-flip tests should exercise DCP3/DCP4 graphics update locks, surface address changes, compression metadata, DFQ status, page-flip interrupts, XDMA flip timeout/average-delay diagnostics, and recovery surface behavior.
- Cursor tests should cover DCP3 cursor update locking, stereo offsets, request filtering, cursor alpha blending, and simultaneous cursor plus plane updates.
- Color tests should validate DC LUT, regamma LUT/regions, CSC/common matrices, prescale, formatter clamp, dynamic expansion, and dither/truncation paths with CRC or visual comparison.
- Scaler tests should cover coefficient RAM programming, horizontal/vertical ratios, viewport/overscan changes, update completion, coefficient conflict handling, mode-change detection, and bypass/replication modes.
- Memory and power tests should monitor DMIF watermarks, stutter/self-refresh, P-state change, DVMM forced-flip status, line-buffer urgency/empty/full status, DCFE memory power status, and display underflow during high bandwidth, low refresh, and suspend/resume scenarios.
- Interrupt and diagnostics tests should verify vblank/vline/vupdate, CRTC vertical interrupts, BLND underflow, FMT/CRTC/DCP CRC capture, perfmon counter-off interrupts, and all relevant ack/clear paths.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define the preceding DCP3 graphics, color, cursor, and possibly other DCE register fields. Later chunks continue DCP4 from the middle of `DCP4_COMM_MATRIXB_TRANS_C13_C14` into the remaining DCP4 color, clamp, keyer, gamma, cursor, LUT, CRC, DVMM, line-buffer, scaler, blender, CRTC, formatter, and following pipe blocks. The final merged per-file report should treat this file as generated AMDGPU DCE 12.0 shift/mask metadata and should avoid inferring algorithmic behavior from this chunk alone.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 17345-19846

## Scope And Purpose

This chunk is a generated AMDGPU DCE 12.0 display-engine register mask/shift slice. It contains no executable code; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for MMIO register fields. The assigned range has 2,130 `#define` entries: 1,065 shift constants and the matching 1,065 mask constants.

The range starts at the tail of the DCP1 display controller plane block, beginning with XDMA recovery/underflow and graphics surface counters. It then covers DCE pipe instance 1 support blocks: line buffer (`LB1`), DC front end (`DCFE1`), performance monitor 4, DMIF page 1 arbitration and power/stutter controls, scaler (`SCL1`), blender (`BLND1`), CRTC timing/status/CRC controls (`CRTC1`), and formatter (`FMT1`). The last section begins the DCP2 display controller plane block and runs through DCP2 regamma LUT write-enable masks. The chunk ends mid-DCP2 regamma family, so later chunks own the remaining DCP2 regamma region controls and subsequent blocks.

The file path is under a local `ceph-client` mirror, but this is AMDGPU Linux kernel display hardware metadata. It has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or local storage objects in this chunk. The public interface is the generated macro namespace. Consumers pair these field constants with the matching DCE 12.0 register-address definitions, usually through AMD display register helpers that compose read-modify-write operations.

The macro naming contract is:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the full bit mask for that field in the register.
- Prefixes such as `LB1_`, `SCL1_`, `CRTC1_`, `FMT1_`, and `DCP2_` identify display pipe or plane instances.
- `addressBlock` comments group adjacent registers by generated hardware block, such as `dce_dc_lb1_dispdec`, `dce_dc_scl1_dispdec`, `dce_dc_crtc1_dispdec`, and `dce_dc_dcp2_dispdec`.

Major register families in this slice:

- Late `DCP1` graphics-plane diagnostics: XDMA recovery address high bits, XDMA underflow count/status/interrupt acknowledgement, flip timeout status/mask/ack, average flip delay, and graphics surface min/max counters.
- `LB1` line-buffer configuration and status: pixel depth/expansion/reduction, prefill/prefetch/request mode, memory size/partitioning, desktop height, vline/vblank interrupt windows and acknowledgements, sync reset selection, black/keyer color values, buffer/FIFO level and urgency status, no-outstanding-request status, and MVP AFR flip helpers.
- `DCFE1`, `DC_PERFMON4`, and `DMIF_PG1`: front-end clock/reset/memory-power/flush bits, performance counter control/state/value fields, DMIF page arbitration, watermark mask selection, urgent/stutter/low-power controls, repeater programming, pre-processing checks, and DVMM status.
- `SCL1` scaler fields: coefficient RAM selection/tap data, scaler mode and tap counts, bypass/manual replication/automatic mode controls, horizontal and vertical filter setup, scale ratios/init phases, bottom-field init, rounding offsets, update lock/pending/taken state, sharpening/ALU controls, coefficient RAM conflict status, viewport start/size, overscan, and scaler mode-change detection/masking.
- `BLND1` blender fields: blend controls, shared-mode controls, update locks, underflow interrupt status/ack/mask, vertical update lock, and register update status.
- `CRTC1` timing generator fields: horizontal/vertical total, blanking, sync A/B positions and polarities, vertical total min/max and control, vertical total/vsync interrupts, trigger A/B, force count, flow control, stereo, AV sync counter, enable/blank/interlace/status/readback fields, frame/vblank counters, snapshot controls, interrupt controls, update locks, test patterns, master update state, MVP status, vertical interrupts 0-2, overscan/blank/black colors, CRC windows/data, external timing sync, static-screen control, 3D structure, GSL timing/control, range timing interrupt status, and DRR control.
- `FMT1` formatter fields: component clamps, dynamic expansion, pixel encoding/subsampling, spatial dither frame controls, 4:2:0 phase/early-start status, bit-depth/truncation/dithering controls, dither random seeds, clamp mode, CRC control/masks/signatures, and side-by-side stereo control.
- `DCP2` graphics-plane and color pipeline fields: graphics enable/control/swap/LUT bypass, primary/secondary surface addresses and in-use addresses, pitch/offset/window extents, gamma/update/flip controls, DFQ status, graphics interrupts, compressed surface metadata, outstanding request limits, prescale values, input/output CSC matrices, common matrix A/B transforms, denorm/round/clamp, keying ranges, degamma/gamut remap, spatial dither/random seeds, cursor surface/size/position/hotspot/colors/update/stereo, DC LUT programming/autofill/control/offsets, DCP CRC, DVMM PTE control/arbitration, flip-rate control, GSL/XDMA synchronization, line-buffer data gaps, stereo sync flip, hardware rotation, XDMA underflow counter control, and the start of regamma LUT access.

## Control Flow

This header slice has no runtime control flow. Every line is declarative metadata consumed by driver code when programming DCE 12.0 hardware registers.

The implied consumer flow is:

1. Select a register address macro from the paired DCE 12.0 address header for the relevant block and instance.
2. Use this chunk's `__SHIFT` and `_MASK` constants to pack, extract, or update a field value.
3. Read, write, or read-modify-write the MMIO register through AMDGPU/DC register helpers.
4. For stateful hardware operations, poll or acknowledge the status fields defined here, such as update-pending/taken bits, interrupt status/ack bits, CRC readbacks, coefficient RAM conflict status, underflow status, DVMM status, and vblank/vline/vsync events.

The header does not enforce sequencing. Correct ordering is owned by the display core: scaler coefficients must be selected and updated coherently, CRTC timing and formatter changes must obey update-lock/double-buffer rules, page flips and cursor updates must respect pending/taken state, and interrupt/ack fields must be handled with the polarity expected by the hardware.

## State And Persistence Behavior

The macros themselves have no mutable software state, allocation, locking, or persistence. They describe hardware-backed state in DCE 12.0 MMIO registers.

Hardware state represented by the chunk includes display pipe timing, line-buffer allocation, scaler and formatter programming, plane surface addresses, color matrices and LUTs, cursor state, CRC capture, performance counters, low-power and stutter controls, DVMM/PTE behavior, interrupt masks/status, update-lock state, and sticky diagnostics such as underflow and conflict indicators.

Persistence is register-specific and external to this header. Many control fields remain programmed until a later modeset, atomic commit, suspend/resume reprogramming, power-gating transition, or GPU reset. Status fields can be live, latched, sticky, write-one-to-clear, or self-clearing depending on the hardware block. The mask/shift header does not encode read-only/write-only semantics, reset defaults, volatile behavior, or required delays.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register contract for DCE 12.0. It is normally used with the companion address and enum headers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/`, especially the DCE 12.0 register address header and enum definitions. The numeric masks and shifts must match AMD's hardware register database.

Observed direct include points for `dce_12_0_sh_mask.h` in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

Practical integration surfaces are the AMD display core and AMDGPU memory/display initialization paths for DCE 12-era ASICs. These constants support mode set, vblank/vline/vsync IRQ service, CRTC timing, scaler setup, format conversion and dithering, plane flips, cursor updates, CRC testing, color-management programming, DMIF arbitration/watermark behavior, performance monitoring, and DVMM/PTE setup.

## Risks And Edge Cases

The primary risk is silent bitfield corruption. A wrong mask or shift can compile cleanly while programming the wrong bits in an MMIO register, leading to blank displays, bad timing, incorrect scaling, color errors, cursor corruption, failed flips, stuck interrupts, underflow, or power-management instability.

Instance repetition is a review hazard. This slice is mostly instance-1 display pipe metadata plus the start of DCP2, and many fields mirror equivalent DCP0/DCP1/LB0/SCL0/CRTC0/FMT0 definitions elsewhere in the file. A one-bit generator or copy error can affect only one display pipe, so single-display testing may miss it.

Status and acknowledgement fields need careful polarity handling. Names such as `*_ACK`, `*_MASK`, `*_INT`, `*_OCCURRED`, `*_PENDING`, `*_TAKEN`, `*_LOCK`, `*_CLEAR`, and `*_DISABLE` encode hardware conventions, not generic boolean API semantics. In particular, interrupt masks and write-one-to-clear acknowledgements are easy to misuse if callers infer behavior only from the suffix.

Timing and update-lock fields are high impact. CRTC timing, scaler ratio/init, formatter 4:2:0 phase, DCP surface address, LUT, CSC, cursor, and blender updates can be double-buffered or synchronized to vblank. Updating related fields without the right lock/pending/taken sequence can cause transient artifacts or missed flips.

Color pipeline fields are numerically dense. CSC matrices, gamut remap matrices, prescale values, clamp ranges, denorm/rounding, degamma/regamma LUT access, and dither controls use adjacent packed fields. Incorrect packing can produce subtle color regressions rather than obvious failures.

The requested range begins in the middle of a DCP1 register family and ends in the middle of the DCP2 regamma family. The final per-file synthesis should treat both as chunk-boundary artifacts and merge with neighboring chunk research before describing the full DCE 12.0 mask header.

## Test Signals

Useful validation is mostly build-time, generated-header comparison, and hardware/display behavior:

- Kernel or AMDGPU targeted builds should compile all DCE 12.0 users with no missing or duplicate macro names.
- Generated-register validation can compare every shift/mask pair against AMD's register database and ensure masks align with shifts and field widths.
- MMIO trace tests can verify that DCE 12.0 modeset, scaler, formatter, plane, cursor, and color-management paths write expected field values.
- Display mode tests should cover multiple pipes/connectors, common and high-refresh timings, interlace where supported, DRR, stereo/GSL paths, suspend/resume, and hotplug recovery.
- Page flip and cursor tests should watch update-pending/update-taken behavior, surface-address in-use registers, flip interrupts, and timeout/underflow diagnostics.
- CRC and formatter tests should exercise CRTC/FMT/DCP CRC controls and compare captured signatures across bit depths, pixel encodings, dithering modes, and 4:2:0 paths.
- IRQ tests should cover vblank, vline, vertical interrupt 0-2, underflow, range timing, external timing sync, and blender underflow acknowledgement/masking.
- Memory pressure and low-power tests should monitor DMIF urgency, stutter, DVMM/PTE status, line-buffer urgency, no-outstanding-request status, and XDMA/cache-underflow counters.

Regression symptoms from bad constants include blank or unstable output, wrong scanout dimensions, scaling artifacts, color shifts, broken cursor placement or format, persistent interrupt storms, missed vblank events, failed CRC validation, flicker around flips, underflow reports, and failures limited to the second or third display pipe.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define the prior DCP1 regamma and graphics-plane fields that this range continues. Later chunks complete the DCP2 regamma block and continue through the remaining DCE 12.0 display register mask/shift namespace. The merge lane should present the full file as generated AMDGPU register bitfield metadata rather than algorithmic driver code.

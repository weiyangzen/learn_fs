# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 12066-14850

## Purpose

This chunk is a generated AMD DCE 12.0 shift/mask header section. It contains no executable driver logic; it publishes preprocessor constants that describe bit positions and packed masks for display-controller MMIO registers. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` values with register offsets from the companion `dce_12_0_offset.h` file and with AMD display register helpers such as `REG_UPDATE`, `REG_SET`, and read/modify/write wrappers.

The range begins at a chunk boundary inside the `DPRX_DPHY_INT_RESET` register, carrying the final reset masks for `HEADERPARSE_RESET` and `SDOUT_RESET`. It then covers several DCE 12.0 display and audio hardware areas:

- DisplayPort receiver DPHY threshold/error/lock/align/deskw status fields.
- DCRX clock gating, soft reset, light sleep, test clock, clock enable, and a large reserved PHY macro range.
- I2S/SPDIF audio control, status, and CRC-test registers.
- Azalia/HD-audio stream, endpoint, and input-endpoint indexed register windows.
- The first DCP0 display controller pipe register block, including graphics surface format, tiling, addresses, update/flip, prescale, CSC, gamut, dithering, cursor, LUT, CRC, PTE, GSL, regamma, alpha, XDMA recovery/underflow, and surface counters.
- The beginning of the LB0 line-buffer block through buffer urgency control.

Although the repository path is under a `ceph-client` source tree mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph filesystem behavior, storage replication, network messaging, or distributed state management.

## Important APIs, Types, And Constants

There are no C functions, structs, enums, global variables, or runtime types in this chunk. The public API is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the already-shifted bit mask for that field.
- Names ending in `_MASK_MASK` are legitimate generated constants for hardware fields whose field name is `*_MASK`; they are not duplicate-mask typos.
- Full-register reserved/spare fields use `0xFFFFFFFFL` masks, for example `DPRX_DPHY_SPARE__DPHY_SPARE_MASK`, `DCRX_PHY_MACRO_CNTL_RESERVED*__DCRX_PHY_MACRO_CNTL_RESERVED_MASK`, and `ZCAL_MACRO_CNTL_RESERVED*__ZCAL_MACRO_CNTL_RESERVED_MASK`.

Important macro families in this range include:

- `DPRX_DPHY_*_STATUS`: status/ack/mask fields for BS interval error threshold, symbol error threshold, disparity error threshold, test-pattern error threshold, SR lock detection, loss of align, loss of deskew, excessive error, and deskew FIFO overflow. These follow a repeated flag/ack/mask layout, with `DETECT_SR_LOCK_STATUS` also exposing a type bit.
- `DCRX_*`: gate-disable fields for DCRX display and symbol clocks, soft-reset fields for display/symbol/ref/S clocks, light-sleep disable fields for AUX and DPRX, display-clock gate delay fields, the `DCRX_SYMCLK_RX_P_ENABLE` clock enable bit, test-clock select/invert fields, and hundreds of reserved PHY macro control slots.
- `I2S*` and `SPDIF*`: control and status fields for two I2S and two SPDIF paths, including word size, sample alignment/order, LRCLK polarity, word alignment, enable, FIFO start address, stream audio enable/idle/data-ready/sample-rate status, and CRC-test enable/reset/continuous/sample-count/data fields.
- `CRC_I2S_CONT_REPEAT_NUM` and `CRC_SPDIF_CONT_REPEAT_NUM`: repeat-count fields used by continuous CRC-test modes.
- `AZF0STREAM[0-15]_*`: indexed Azalia stream access windows with an 8-bit register index, a write-enable bit, and 32-bit data.
- `AZF0ENDPOINT[0-7]_*` and `AZF0INPUTENDPOINT[0-7]_*`: indexed Azalia codec endpoint and input-endpoint access windows with 14-bit index fields and 32-bit data fields.
- `DCP0_GRPH_*`: graphics enable, keyer alpha selection, scanout depth/format/tiling/swizzle, surface addresses and high address bits, pitch, viewport offsets/start/end, update locks, update pending/taken status, flip timing, DFQ controls/status, page-flip interrupts, compression surface metadata, outstanding request limits, XDMA flip and cache-underflow controls, and surface-counter fields.
- `DCP0_*COLOR*`, `DCP0_*CSC*`, `DCP0_*GAMMA*`, `DCP0_*LUT*`, and `DCP0_*DITHER*`: input/output color pipeline fields for prescale, input CSC, output CSC, common matrix transforms, denorm, output rounding/clamp, key ranges, degamma, gamut remap, spatial dithering, DC LUT access/autofill/control/offsets, DCP CRC, and A/B regamma curve programming.
- `DCP0_CUR_*`: cursor enable/mode/2x magnification, pitch, line-per-chunk, address, size, high address, position, hot spot, color, update lock/pending/taken flags, request filter, and stereo cursor controls.
- `DCP0_DVMM_PTE_*`: page-table/cache policy and arbitration fields for display virtual memory/PTE behavior.
- `DCP0_DCP_GSL_CONTROL`: global swap lock group, master, enable, reset-delay, and check-all-fields behavior.
- `LB0_LB_*`: line-buffer data format, memory sizing/partition/configuration, desktop height, vline/vline2 windows, vertical counters, vblank/vline interrupt masks and status/ack bits, sync reset selection/delay/duration, black/keyer colors, keyer replacement colors, buffer level status, and buffer urgency thresholds.

## Control Flow

This header has no runtime control flow. Every line is a compile-time `#define` mapping a hardware field name to a numeric bit shift or mask.

Runtime behavior appears in AMD display code that includes `dce_12_0_sh_mask.h`, especially the DCE 12.0 resource and timing-generator paths under `drivers/gpu/drm/amd/display/dc/dce120/`. A typical use sequence is:

1. A DCE 12.0 component selects a register offset from `dce_12_0_offset.h`, often through a generated register-list macro such as memory-input, transform, timing-generator, audio, AUX, or hardware-sequencer register tables.
2. The same component stores matching shift and mask values from this header in per-block tables, for example `MI_DCE12_MASK_SH_LIST(__SHIFT)`, `MI_DCE12_MASK_SH_LIST(_MASK)`, `XFM_COMMON_MASK_SH_LIST_SOC_BASE(__SHIFT)`, and `XFM_COMMON_MASK_SH_LIST_SOC_BASE(_MASK)`.
3. Driver code converts DRM/DC state into hardware field values, then uses register helpers to clear and insert only the relevant field bits.
4. Hardware latches the resulting register state immediately, at a display update boundary, on a page flip, after an ACK/clear write, or after block-specific reset/power sequencing.

Examples visible in the tree show this contract directly. `dce120_resource.c` builds DCE 12.0 shift/mask tables for transforms and memory inputs. `dce_transform.h` consumes fields from this chunk such as `LB0_LB_DATA_FORMAT`, `LB0_LB_MEMORY_CTRL`, clamp, dithering, gamut, output CSC, and regamma fields. `dce_mem_input.c` uses DCE 12.0 `DCP0_GRPH_CONTROL` masks to program GFX9 scanout swizzle, bank count, shader-engine count, pipe count, color expansion, and shader-engine enable.

Several register groups imply hardware control sequences even though this file does not implement them. Azalia stream/endpoint registers use an index/data access pattern. Audio CRC-test registers are configured, optionally reset, then observed through CRC data fields. Graphics updates can be locked, queued, taken on retrace, or forced immediate depending on `DCP0_GRPH_UPDATE` and `DCP0_GRPH_FLIP_CONTROL`. Cursor and LUT updates have pending/taken or indexed-write semantics. Interrupt/status registers expose occurrence/status, mask, ack, clear, or type bits that must be handled in the correct order by callers.

## State And Persistence Behavior

The macros do not store state and do not persist anything. They describe state held in DCE 12.0 hardware registers after other driver code writes those registers.

Hardware state represented by this chunk includes:

- DP receiver DPHY error, lock, alignment, deskew, excessive-error, FIFO-overflow, ack, and interrupt-mask state.
- DCRX power/clock/reset state, including clock-gate disable, light-sleep disable, soft reset, symbol-clock enable, test-clock routing, and reserved PHY macro configuration.
- Audio interface state for I2S/SPDIF formatting, enablement, FIFO placement, status, sample-rate observation, and CRC-test collection.
- Azalia stream/endpoint indexed register state for HDMI/DP audio codec programming.
- Display pipe scanout state: graphics enable, pixel depth/format, tiling/swizzle, surface addresses, pitch, viewport, compression metadata, update locks, flip controls, page-flip interrupt state, and outstanding request limits.
- Color pipeline state: prescale, input/output CSC matrices, common matrices, denorm, rounding, clamp, keying, degamma, gamut remap, spatial dithering, LUT contents/control, CRC configuration, regamma LUT/curve A and B programming, and alpha/cursor blending.
- Cursor state: surface address, format/mode, size, position, hot spot, colors, update synchronization, filter mode, and stereo behavior.
- Display VM/PTE arbitration and cache policy state.
- GSL synchronization state for coordinated flips or reset/update behavior.
- XDMA recovery, cache-underflow count/status/ack/mask, flip timeout, average delay, and graphics surface counter state.
- LB0 line-buffer configuration, interrupt masks/status, sync-reset controls, key colors, buffer levels, and urgency thresholds.

Persistence is register-specific. Control values generally remain until overwritten, reset, power-gated, or restored during modeset/suspend/resume/GPU-reset handling. Status and interrupt bits may be sticky until ACK or clear bits are written. Indexed data windows persist in their underlying audio/LUT/register files rather than in the index selector alone. Update-pending/taken and FIFO/reset-ack fields are transient reflections of hardware progress. This generated header does not encode read-only, write-one-to-clear, self-clearing, double-buffered, reserved, or power-domain semantics; consumers must know those rules from the ASIC programming model and existing AMD display code.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header ecosystem:

- The surrounding `dce_12_0_sh_mask.h` include guard and earlier/later field definitions in the same file.
- Register offsets and base indices in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`.
- DCE 12.0 display code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/`, including resource construction, timing generation, hardware sequencing, audio, AUX/I2C, transforms, and memory-input programming.
- Shared DCE display helper headers such as `dce_transform.h`, `dce_mem_input.c`, and related `REG_UPDATE`/field-table macros that expect each field to have both shift and mask constants.
- Vega-era display and graphics tiling conventions. The DCP0 graphics-control fields include GFX9-style swizzle, bank, shader-engine, pipe, and color-expansion fields, so they integrate with DC tiling information and framebuffer scanout setup.
- Audio-over-display paths. I2S/SPDIF and Azalia indexed fields feed HDMI/DisplayPort audio programming, status, and CRC diagnostics.
- Interrupt and validation paths for page flip, vline/vblank, DP receiver errors, line-buffer status, XDMA underflow/timeout, and CRC/test-pattern diagnostics.

The most direct source-tree consumers found for this DCE generation are the DCE 12.0 resource pool and timing-generator code. They include `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`, build register/shift/mask tables, and then hand those tables to common DCE components. The same audio mask-list convention is reused by newer DCN resource files for common audio fields, so some DCE 12.0 audio definitions serve as a shared compatibility contract beyond the original DCE 12.0 resource path.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are plain integers, so an incorrect shift or mask can compile cleanly and still corrupt an adjacent field, leave a field unchanged, or target the wrong hardware behavior.

Specific risk areas:

- The requested range begins mid-register. The first two macros are only the tail of `DPRX_DPHY_INT_RESET`; per-file reconciliation must combine them with the previous chunk before reasoning about the complete reset register.
- Status registers often combine occurrence/status, ACK, interrupt, type, clear, and mask bits. Confusing `*_ACK`, `*_CLEAR`, and `*_MASK` fields can lose events, leave interrupts storming, or hide important DP/graphics/LB/XDMA faults.
- Field names ending in `_MASK_MASK`, such as `DCP0_GRPH_XDMA_FLIP_TIMEOUT__GRPH_XDMA_FLIP_TIMEOUT_MASK_MASK`, represent the mask bit of a hardware field named `...MASK`. Scripts or reviewers should not collapse or rename them.
- Many masks use high bits, including `0x80000000L` and other upper-half values. Callers should compose values with unsigned 32-bit arithmetic to avoid sign-extension or overflow surprises.
- DCRX clock-gate, light-sleep, and soft-reset fields can disable or reset active display receiver clocks. Incorrect sequencing can break AUX/DPRX behavior, interrupt reporting, or link recovery.
- Reserved PHY/ZCAL macro control fields are wide writable-looking fields. Production code should not invent writes to these reserved locations without an AMD programming sequence or hardware documentation.
- DCP0 graphics-control fields are tightly tied to framebuffer layout. Bad depth, format, swizzle, bank, shader-engine, pipe, address-translation, privilege, pitch, or surface-address values can cause corrupted scanout, memory faults, display underflow, or blank output.
- Surface address fields are split between low and high registers, with low addresses shifted by 8 bits in several places. Consumers must preserve alignment and high-address handling for large GPU addresses.
- Update-lock, pending/taken, immediate flip, H-retrace, multiple-update-disable, and ignore-lock fields affect visible atomicity. Misuse can cause tearing, stale frames, missed flips, or updates that never take effect.
- Color pipeline fields are dense and repeated. Bad CSC, gamut, denorm, clamp, dither, LUT, or regamma masks can produce wrong colors, clipped output, broken HDR/gamma behavior, or failed CRC comparisons without crashing the driver.
- Cursor fields combine address, mode, expansion, color, position, hot spot, update, and stereo state. Incorrect mask layout can create misplaced cursors, wrong cursor colors, stale cursor updates, or stereo cursor mismatch.
- Azalia stream/endpoint windows are indexed. Writing data with the wrong index or write-enable bit can alter the wrong audio codec register while appearing as a valid MMIO write.
- Audio CRC and status fields are diagnostic-oriented and may be timing-sensitive. Resetting or enabling CRC collection at the wrong time can make test results unreliable.
- LB0 memory size, partitioning, pixel-depth, urgency, and interrupt fields interact with display bandwidth and underflow handling. Bad values can cause line-buffer underruns, vblank/vline interrupt loss, or unstable high-resolution modes.
- The chunk ends inside `LB0_LB_BUFFER_URGENCY_CTRL`; the following chunk owns the rest of the LB0 block. The final per-file report should avoid treating LB0 as fully covered by this chunk alone.

## Test Signals

Useful validation is mostly build-time, generated-header, and hardware-integration oriented:

- Kernel/AMDGPU builds for DCE 12.0 paths should compile with no missing field constants in `dce120_resource.c`, `dce120_timing_generator.c`, `dce120_hwseq.c`, memory-input, transform, audio, AUX, and shared DCE helper code.
- Generated-register validation should compare every field in lines 12066-14850 against AMD's authoritative DCE 12.0 register database and the matching offsets in `dce_12_0_offset.h`.
- Static checks can verify that each register field has matching `__SHIFT` and `_MASK` definitions, masks do not overlap unexpectedly within a register, full-register reserved fields remain full-width, and high-bit masks are represented with unsigned-safe 32-bit values.
- Display scanout tests should exercise DCP0 graphics enable, depth/format, tiling/swizzle, pitch, surface address high/low, viewport, compression metadata, and outstanding request programming across linear and tiled framebuffers.
- Page-flip and atomic-update tests should watch `DCP0_GRPH_UPDATE`, `DCP0_GRPH_FLIP_CONTROL`, page-flip interrupts, in-use address fields, immediate/H-retrace updates, lock/unlock paths, and multiple-update behavior.
- Color-management tests should cover prescale, input CSC, output CSC, gamut remap, degamma, LUT writes/autofill, regamma A/B regions, clamp, rounding, dithering, and DCP CRC output.
- Cursor tests should cover mode changes, 2x magnification, address high/low, size, position, hot spot, color, update locking, request filtering, and stereo controls.
- HDMI/DisplayPort audio tests should cover I2S/SPDIF enable/status, sample-rate reporting, CRC-test paths, and Azalia stream/endpoint indexed register access.
- DP receiver fault diagnostics should verify DPHY threshold, lock, align, deskew, excessive-error, FIFO-overflow, ack, and mask behavior during link bring-up and fault injection.
- Suspend/resume, runtime power-management, hotplug, and GPU-reset tests should verify that DCRX gate/reset/light-sleep state and DCP/LB/LUT/color state are restored or reinitialized correctly.
- Line-buffer tests should exercise LB0 pixel-depth/memory configuration, vblank/vline/vline2 interrupt masks and ACKs, sync-reset selection, key colors, buffer level reporting, urgency thresholds, and underflow recovery at bandwidth-stressing modes.
- XDMA diagnostics should observe cache-underflow count/status/ack/mask, flip timeout, average flip delay, recovery surface address, and surface counters on platforms or modes that use XDMA display paths.

Regression symptoms from bad constants include blank or corrupted displays, wrong colors or gamma, cursor artifacts, failed page flips, display underflows, lost vblank/vline/page-flip interrupts, failed EDID/audio behavior indirectly caused by receiver/audio misconfiguration, stuck Azalia indexed accesses, unreliable CRC diagnostics, broken suspend/resume recovery, or hardware faults when scanout addresses and tiling fields are misprogrammed.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define the preceding DCE 12.0 field namespace and the first part of `DPRX_DPHY_INT_RESET`. This chunk starts with only the last two masks from that register and then continues through DCRX, audio, Azalia, DCP0, and early LB0 fields.

Later chunks continue the LB0 line-buffer block and the rest of the generated DCE 12.0 shift/mask namespace. The final per-file research document should frame this source as a generated hardware bitfield contract paired with `dce_12_0_offset.h`, not as standalone algorithmic driver code.

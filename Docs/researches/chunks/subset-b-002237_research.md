# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 47435-49893

## Purpose

This chunk is generated AMD DCN 4.2.0 register-field metadata. It contains no executable C logic; its contract is a large set of C preprocessor constants that map hardware register fields to bit shifts and masks. AMDGPU display code combines these `_SHIFT` and `_MASK` macros with the matching register offsets in `dcn_4_2_0_offset.h` to program DisplayPort stream encoder state, Display Stream Compression (DSC) engines, DSC client-interface blocks, DSC compressor cores, and DC performance counters.

The range contains 2,139 `#define` entries across 275 register names: 1,067 `__SHIFT` definitions and 1,072 `_MASK` definitions. The first line is a chunk-boundary artifact inside `DP4_DP_MSO_CNTL1`: earlier fields for the same register are just above this range. The final line range ends inside the fourth DSC compressor instance, after `DSCC3_DSCC_PPS_CONFIG9`; the next chunk continues with `DSCC3_DSCC_PPS_CONFIG10` and later fields. Although this repository subtree is named `distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata, not Ceph or filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, heap allocations, includes, or direct MMIO accesses in this range. The public interface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field in a register value.

The chunk's main register groups are:

- `DP4_DP_*`: tail-end DisplayPort stream encoder 4 fields. These include multi-stream operation and secondary-data enablement, steering FIFO control, generic secondary packet send/pending/deadline/line-number controls for GSP1-GSP7 and GSP11/PPS, double-buffer state, MSA/VBID override fields, secondary metadata transmission state, ALPM/AUX-less ALPM timing, stream/link symbol counters, panel replay/SYM8 encoder control, and DPHY fast-training status.
- `DSC_TOP0` through `DSC_TOP3`: top-level DSC instance control and debug fields. These cover `DSC_CLOCK_EN`, display and DSC clock root-gate disables, fine-grain clock-gating repeat disable, dynamic DSC clock gating, debug enable, debug clock mux selection, spare debug, and top test-debug index/data registers.
- `DSCCIF0` through `DSCCIF3`: DSC client-interface configuration fields for input pixel format, bits per component, and double-buffer update-pending state.
- `DSCC0` through `DSCC3`: DSC compressor core fields. For instances 0-2, this chunk covers configuration, status, interrupt controls/status, PPS registers 0-22, memory power controls, squared-error counters, maximum absolute error, output/rate-buffer fullness, and test/debug buses. For instance 3, this chunk starts the same sequence but only reaches PPS config 9.
- `DC_PERFMON17` through `DC_PERFMON19`: performance-counter and performance-monitor control/state/value registers attached to DSC instances 0-2 in the address blocks. Fields include enable/reset/start/stop/clear/status controls, counter mode/selection, C-value interrupt/status/clear bits, and low/high counter value fields.

Representative field families include DSC PPS parameters (`DSC_VERSION`, `PPS_IDENTIFIER`, `BITS_PER_PIXEL`, `PIC_WIDTH`, `PIC_HEIGHT`, `SLICE_WIDTH`, `SLICE_HEIGHT`, delay/scale/BPG offsets, RC model size, RC buffer thresholds, and range QP/BPG table entries), compressor status and interrupt bits (`RATE_CONTROL_BUFFER_MODEL_OVERFLOW`, output overflow/underflow, end-of-frame-not-reached, and matching clear bits), memory low-power state controls, quality/error observation counters, and debug bus selection/index/data fields.

## Control Flow

This header has no runtime control flow. Its effect is compile-time token expansion:

1. DCN 4.2 display code includes generated offset and shift/mask headers for the target ASIC.
2. Register-table macros such as stream-encoder field macros and DSC field macros token-paste register and field names into generated register descriptors.
3. Runtime driver code uses those descriptors with `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or equivalent helpers to read or write MMIO fields.
4. Hardware state machines perform the real sequencing for secondary-data packet send, ALPM/panel replay, symbol counting, fast training, DSC clocking, DSC PPS programming, buffer/RC monitoring, memory power state, and debug/perf-counter capture.

The DP4 prefix binds this slice to the fifth DisplayPort stream encoder instance. The DSC and DSCC prefixes are instance-specific. Most DSC driver field tables are written against instance 0 names and then remapped by register lists; generated metadata for instances 1-3 must remain layout-compatible where the hardware instances are mirrored.

## State And Persistence Behavior

The chunk stores no software state and persists nothing directly. It defines encodings for hardware-visible state:

- DP secondary-data state: GSP enablement, send request bits, send-pending and deadline-missed status, line-number scheduling, "send any line" control, PPS routing via GSP11, double-buffer pending/taken flags, and active/idle send observation.
- DP low-power/replay state: ALPM enable/configuration, AUX-less ALPM PHY timing and debounce parameters, panel replay/SYM8 controls, symbol count start/clear/status fields, and link/stream symbol counters.
- DP link-training state: fast-training capability/configuration and status bits.
- DSC compressor state: top-level clock enable/gating bits, input format, bits per component, slices per line/vertical direction, ICH settings, rate-control buffer model size, PPS payload fields, double-buffer update-pending status, memory power state, and debug/test mux selection.
- DSC fault and observation state: interrupt enable/status/clear fields for rate-control model overflow, output-buffer overflow/underflow, and end-of-frame-not-reached; squared-error and maximum-absolute-error counters; output/rate-buffer fullness high-water marks; and performance-counter values.

Persistence is hardware-defined. Configuration fields generally survive until reprogrammed, reset, power-gated, or overwritten by a mode-set/link-training/compression programming path. Status, pending, taken, clear, counter, and debug-data fields may be read-only, sticky, write-one-to-clear, self-clearing, valid only while clocks are enabled, or valid only after a capture/control bit is asserted. The generated mask header does not encode access direction, reset value, timing, volatility, or side effects.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated register-header convention. The matching DCN 4.2.0 offset header provides register addresses and base indices, for example `regDP4_DP_SEC_CNTL2`, `regDP4_DP_AUXLESS_ALPM_CNTL1`, `regDSC_TOP0_DSC_TOP_CONTROL`, `regDSCC0_DSCC_PPS_CONFIG0`, `regDC_PERFMON17_PERFCOUNTER_CNTL`, and `regDSCC3_DSCC_PPS_CONFIG6` in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`.

Important consumers and integration points include:

- DisplayPort stream encoder code and field tables in `drivers/gpu/drm/amd/display/dc/dio/*`, including GSP/secondary-data controls for VSC, SPD, HDR metadata, adaptive sync, PPS, and immediate or line-scheduled packet sending.
- Link encoder and link training paths that use `DP_DPHY_FAST_TRAINING` and related fields for fast-training capability and behavior.
- Panel replay and ALPM paths in the display link code and DMUB-facing paths, with this chunk providing the DP4 hardware control fields that back those features.
- DSC code in `drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.h`, where `DSC_REG_LIST_SH_MASK_DCN401(mask_sh)` maps `DSC_TOP0`, `DSCC0`, and `DSCCIF0` field names into the driver's DSC register/shift/mask tables.
- DRM DSC parameter handling via `drm/display/drm_dsc.h` and AMD DSC types, which provide the software PPS/compression model that must be encoded into these hardware PPS registers.
- DC perfmon/debug infrastructure that reads the `DC_PERFMON17`-`DC_PERFMON19` counters and DSC debug buses for diagnostics and performance analysis.

Because this is generated silicon ABI metadata, edits must be synchronized with the authoritative AMD register database and with paired offset/base-index headers. A manual change can compile cleanly while making the driver program the wrong hardware bits.

## Risks And Edge Cases

- The macros are untyped. Incorrect shifts or masks compile but can corrupt adjacent hardware fields, especially in dense PPS, interrupt status, and packed QP/range table registers.
- The line range is not semantically aligned. `DP4_DP_MSO_CNTL1` begins before this chunk, and `DSCC3` continues after it; whole-register and whole-instance conclusions require adjacent chunks.
- Status and clear fields share similar names. Confusing `*_OCCURRED*`, `*_CLEAR*`, and `*_INT_EN*` fields can leave interrupts latched, mask real DSC faults, or clear diagnostics before software observes them.
- DSC PPS fields directly affect compressed stream generation. Wrong bit positions can cause blank displays, corrupted frames, downstream DSC decoder failures, link bandwidth miscalculation, or intermittent errors only on modes that require DSC.
- Instance symmetry matters. `DSCC0`, `DSCC1`, `DSCC2`, and `DSCC3` are expected to mirror many layouts, but this chunk only partially includes `DSCC3`; copy/paste or generated-name drift can break only one compressor instance.
- DP4-specific fields only affect one stream encoder. Bugs may appear only on a connector or pipeline assignment that maps to DP4, making regressions topology-dependent.
- ALPM, AUX-less ALPM, panel replay, and symbol counters are timing-sensitive. Misprogramming debounce, wake, counter start/clear, or training fields can create resume, replay, or low-power entry/exit failures that basic mode-set tests may miss.
- Debug and perfmon registers can have capture windows or clear-on-write behavior. Generic read/modify/write helpers must preserve unrelated fields and avoid clearing counters unintentionally.
- Reserved or spare debug fields expose full-width masks such as `0xFFFFFFFFL`; production code should not treat them as general-purpose policy fields unless the hardware programming guide requires it.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU display code that includes `dcn_4_2_0_sh_mask.h` with `dcn_4_2_0_offset.h`. Missing or renamed symbols should surface in stream-encoder, DSC, link-encoder, and perfmon field tables.
- Mechanically compare this range against AMD's authoritative DCN 4.2.0 register database, treating the first and last registers as partial-boundary cases.
- Check that every `__SHIFT` macro has a matching `_MASK` macro where the source database defines a normal field. This chunk has a small 1,067/1,072 shift-mask imbalance due to range boundaries or generated partial entries and should be reconciled with neighboring chunks.
- Validate mirrored DSC layouts across instances 0-3, especially PPS registers, interrupt status/clear fields, buffer fullness counters, memory power controls, and debug buses.
- Exercise DisplayPort output through a topology that uses DP4, including hotplug, mode-set, MST/MSO where applicable, HDR/VSC/SPD/adaptive-sync info packets, PPS metadata, and secondary packet scheduling.
- Test DSC-enabled modes across slice counts, bits per component, bits per pixel, RGB/YUV formats, and high-bandwidth modes. Watch for blanking, visual corruption, downstream DSC negotiation failures, and interrupt status for output-buffer overflow/underflow or RC model overflow.
- Cover panel replay and ALPM/AUX-less ALPM entry and exit, including idle, wake, selective update, suspend/resume, and link retraining.
- Use symbol-count and perfmon/debug paths during stress modes to confirm counters start, stop, clear, and report plausible values without stale or stuck status bits.

## Cross-Chunk Notes

The preceding chunk contains the beginning of `DP4_DP_MSO_CNTL1` and earlier DP4 stream-encoder fields. This chunk then covers the remainder of the DP4 secondary-data/low-power/replay/statistics area and most of DSC instances 0-2 plus the beginning of DSC instance 3. The following chunk is required to complete `DSCC3` PPS/configuration/debug coverage before a final per-file report can make complete claims about all DCN 4.2.0 DSC compressor metadata.

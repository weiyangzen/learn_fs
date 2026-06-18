# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 30309-32771

## Purpose

This chunk is generated AMD DCN 4.2.0 register-field metadata. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for several display color-management, performance-monitor, DisplayPort AUX, hotplug-detect, mux, formatter, display-pattern-generator, OPP buffer, OPP pipe, and pipe-CRC registers. AMDGPU Display Core pairs these definitions with `dcn_4_2_0_offset.h` and register-helper macros to pack, extract, and update individual MMIO fields.

The range contains 2,463 `#define` lines: 1,078 `__SHIFT` macros and 1,091 `_MASK` macros. It starts inside `CM3_CM_GAMCOR_RAMB_REGION_2_3`: the register comment and all shifts are included, but the previous chunk owns the preceding `REGION_0_1` register and line 30309 begins in the `REGION_2_3` definitions. It ends inside `DPG1_DPG_DIMENSIONS`: the active-height/width shifts and active-height mask are included, while the active-width mask and the rest of DPG1 continue after this chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, callbacks, or direct MMIO reads/writes in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, clearing, or writing that field.

Major register families in this chunk:

- `CM3_CM_GAMCOR_RAMB_*`, `CM3_CM_HDR_MULT_COEF`, `CM3_CM_MEM_PWR_*`, `CM3_CM_DEALPHA`, `CM3_CM_COEF_FORMAT`, `CM3_CM_TEST_DEBUG_*`, and `CM3_CM_HIST_*`: DPP3 color-management gamma-correction RAM-B region layout, HDR multiplier coefficient, color/histogram memory power controls and status, dealpha and coefficient-format controls, CM debug index/data, histogram source selection, coefficients, bias, lock/index/data/status, and histogram-ready interrupt control.
- `DC_PERFMON13_*`: DPP3 performance counter controls, counter state, perfmon control, comparison/increment interrupt configuration, and counter high/low value fields.
- `DP_AUX0_*` through `DP_AUX4_*`: five DisplayPort AUX channel instances. Each instance exposes AUX enable/reset, low-speed read control, HPD selection, impedance calibration/test mode, software transaction control, software/DMCU arbitration, interrupt enables and acknowledgements, software and low-speed status/error reporting, software and low-speed data/index fields, AUX DPHY TX/RX timing controls, TX/RX PHY status, and AUX PHY wake request/status fields.
- `HPD0_*` through `HPD4_*`: five hotplug-detect blocks. Each instance contains HPD interrupt and sense status, interrupt polarity/enable/ack, RX interrupt enable/ack, connection/RX timers, HPD enable, fast-train delays/enables, and connect/disconnect toggle filter delays.
- `DPIA_MUX0_*` through `DPIA_MUX5_*`: DPIA mux controls for HPD selection, AUX selection, link selection, USB4 DPALT disable, stream enable, and reserved-programming fields.
- `PHY_MUX0_*` through `PHY_MUX4_*`: PHY mux controls for PHY link selection, lane enables, lane-to-PHY mapping, and port type.
- `DCOH_TOP_*` and `DCOH_DCN_STATUS`: top-level DCOH clock, clock-on status, spare, and DCN status fields.
- `FMT0_*` and `FMT1_*`: formatter clamp components, dynamic expansion, pixel encoding, subsampling, dithering/truncation, dither seeds and offsets, clamp color format, side-by-side stereo active width, 4:2:0 memory power controls/status, and 4:2:2 edge pixel control.
- `DPG0_*` and partial `DPG1_*`: display pattern generator enable/mode/dynamic-range/bit-depth/resolution/field-polarity, ramp controls, active dimensions, colors, offset segment, and double-buffer status for instance 0; the chunk includes only DPG1 control, ramp control, and the beginning of dimensions.
- `OPPBUF0_*`, `OPP_PIPE0_OPP_PIPE_CONTROL`, and `OPP_PIPE_CRC0_*`: OPP buffer active width/segmentation/overlap/repetition/double-buffer and 3D dummy-data parameters, OPP pipe clock/digital-bypass control, and output-pipe CRC enable/mode/source/result fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 4.2.0 code includes `dcn_4_2_0_sh_mask.h` with the matching offset header.
2. Register tables and hardware-block constructors token-paste symbolic register and field names into mask/shift structures.
3. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, field-definition helpers, and related indexed/MMIO helpers to access hardware registers.
4. The numeric shift/mask values from this chunk determine which bits are touched when the driver handles color/histogram programming, perf counter setup, AUX transactions, HPD interrupts, USB4/DPIA/PHY mux routing, formatter output format, DPG test patterns, OPP buffering, OPP clocks, and pipe CRC capture.

The macros do not encode ordering constraints. Consumers must still follow hardware sequencing for AUX arbitration and transaction completion, HPD interrupt acknowledgement, mux ownership, formatter double-buffer updates, DPG programming, memory power transitions, CRC one-shot/continuous capture, and reads of status or sticky interrupt fields.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed DCN state:

- Color-management state includes gamma-correction RAM-B region segmentation, HDR multiplier, histogram configuration/data/status, debug index/data, dealpha mode, coefficient format, and CM memory power state.
- AUX state includes active transactions, request/done bits, arbitration ownership between software and DMCU/firmware, low-speed data snapshots, RX/TX status, PHY wake handshakes, error flags, reply byte counts, and interrupt acknowledgement bits.
- HPD state includes live sense, delayed sense, RX interrupt status, connection timers, filtering timers, polarity, enable, and acknowledgement fields.
- Mux state binds DPIA, AUX, HPD, link, PHY, lane, port-type, and stream-enable resources to display pipelines and physical outputs.
- Formatter and OPP state includes clamp ranges, pixel encoding and chroma subsampling, dithering/truncation behavior, dither seeds, map420 memory power state, DPG test-pattern configuration, OPP buffer geometry, OPP pipe clock/bypass state, and pipe CRC results.

Persistence is hardware-defined. Configuration fields usually survive until modeset, link reconfiguration, output reprogramming, power gating, suspend/resume, GPU reset, or driver reinitialization. Status, pending, ready, interrupt, acknowledgement, error, double-buffer, and one-shot fields may be transient, sticky, self-clearing, write-one-to-clear, read-only, or valid only while relevant clocks and power domains are active. This generated header does not express those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which provides matching register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, which includes the DCN 4.2.0 offset and shift/mask headers for DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, which includes these headers for DCN 4.2 interrupt service tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`, which include these headers for DCN 4.2 GPIO/HPD/AUX translation.
- OPP and formatter code that uses shared `FMT*`, `DPG*`, `OPPBUF*`, `OPP_PIPE*`, and `OPP_PIPE_CRC*` field names through ASIC-specific register lists.
- Link, AUX, HPD, USB4/DPIA, PHY mux, diagnostics, CRC, color, histogram, and perf-monitor code paths that rely on consistent field layouts across repeated instances.

The repeated AUX0-4, HPD0-4, DPIA_MUX0-5, PHY_MUX0-4, FMT0-1, and DPG0-1 patterns are integration contracts. Generic instance-indexed driver code can only be correct if each instance keeps the expected register layout and if the matching offset header maps the same symbolic registers to the correct hardware block.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while reading or writing the wrong hardware bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- The range is partial at both ends. Complete reasoning about `CM3_CM_GAMCOR_RAMB_REGION_2_3` should account for adjacent gamma-region definitions, and complete reasoning about `DPG1_DPG_DIMENSIONS` requires the following chunk for the active-width mask and later DPG1 fields.
- AUX status, interrupt, acknowledgement, arbitration, and data fields are sequencing-sensitive. Using the wrong mask can miss a HPD disconnect, miscount reply bytes, corrupt an AUX payload/index, or break software versus DMCU ownership handoff.
- HPD interrupt status/control fields have similar names across status, ack, polarity, enable, and RX interrupt paths. Confusing them can lose hotplug events, repeatedly signal stale interrupts, or invert expected polarity.
- Mux controls connect logical display resources to physical links, AUX channels, HPD pins, USB4/DPIA paths, and PHY lanes. Wrong fields can route a stream to the wrong connector or leave link training using the wrong AUX/HPD source.
- Formatter, DPG, and OPP fields are user-visible. Incorrect clamp, pixel-encoding, subsampling, dithering, test-pattern, buffer, or CRC masks can cause color shifts, bad 4:2:0/4:2:2 output, display artifacts, incorrect diagnostic CRCs, or blanking.
- Power/status fields for CM histogram memory and formatter 4:2:0 memory may be invalid during power gating or reset. Drivers need existing power-domain and double-buffer sequencing; the header alone cannot indicate safe access windows.
- Repeated instance layouts are copy-sensitive. Testing only AUX0/HPD0/FMT0/DPG0 may miss an instance-specific typo in AUX4, HPD4, FMT1, or DPG1.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.2.0 display behavior:

- Build AMDGPU display support with DCN 4.2.0 enabled. Missing or renamed macros should fail in DMUB, IRQ, GPIO, OPP, link, or resource register-table construction.
- Mechanically verify every field in this range has matching shift and mask definitions, while allowing boundary exceptions caused by the chunk split, including `DPG1_DPG_DIMENSIONS__DPG_ACTIVE_WIDTH_MASK` immediately after line 32771.
- Diff this slice against AMD's authoritative DCN 4.2.0 register database and the paired `dcn_4_2_0_offset.h`; repeated AUX/HPD/DPIA/PHY/FMT/DPG instances should have identical field layouts where the hardware schema expects them.
- Exercise DisplayPort AUX transactions on AUX0-4: DPCD reads/writes, I2C-over-AUX EDID reads, timeout/error handling, HPD disconnect during transaction, low-speed status updates, and firmware/software arbitration.
- Exercise HPD0-4 connect/disconnect and HPD RX IRQ paths, including debounce/toggle filtering, interrupt polarity, acknowledgement, fast-train delays, suspend/resume, and hotplug storms.
- Validate USB4/DPIA and PHY mux routing across all exposed ports, including link selection, AUX/HPD selection, stream enable, lane mapping, and port-type reporting.
- Run formatter and OPP output tests covering RGB/YCbCr pixel encoding, chroma subsampling, clamp ranges, truncation, spatial/temporal dithering, 4:2:0 memory power transitions, DPG patterns, OPP buffer segmentation, pipe clock gating, and pipe CRC one-shot/continuous reads.
- Use CM histogram/perfmon diagnostics to verify histogram ready/status/overflow behavior, memory power state reporting, perf counter event selection, counter high/low reads, interrupt enables, and counter restart/active states.
- Monitor kernel logs, display hotplug events, AUX transaction failures, link-training traces, CRC mismatches, color-format failures, blanking, and resume-only issues as high-signal indicators of bad mask/shift metadata.

## Cross-Chunk Notes

The previous chunk owns earlier CM3 gamma-correction RAM-B fields, including `CM3_CM_GAMCOR_RAMB_REGION_0_1`. This chunk owns the rest of CM3 gamma region pairs 2-33, CM histogram/perfmon, complete AUX0-4, HPD0-4, DPIA mux0-5, PHY mux0-4, DCOH top, complete FMT0, complete DPG0, OPPBUF0, OPP pipe0, OPP pipe CRC0, complete FMT1, and the opening DPG1 control/ramp/dimensions fields. The next chunk owns the remaining `DPG1_DPG_DIMENSIONS` mask and the rest of DPG1 and following generated register families. The final per-file research document should reconcile these adjacent chunks before making complete claims about all DCN 4.2.0 CM, OPP, AUX, HPD, mux, and DPG register coverage.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 11034-13252

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains C preprocessor constants for register bit positions and positioned masks, not executable logic. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with the matching DCN 3.5.0 offset header and AMD display register helper macros to read, write, or update memory-mapped display hardware fields.

The requested range contains 2,219 `#define` lines: 1,106 `__SHIFT` macros and 1,123 `_MASK` macros across 481 register groups. The imbalance is caused by chunk boundaries. The range starts inside `DC_PERFMON4_PERFCOUNTER_CNTL` after several earlier shift definitions, and it ends inside `HUBP1_DCSURF_ADDR_CONFIG` before the remaining masks for that register.

The substantive hardware covered here is a wide DCN display data path surface: DC performance monitors 4, 5, and 6; Azalia/HD-audio endpoint, stream, DMA, CRC, and memory-power fields; DCHUBBUB fabric, VM, arbitration, watermark, debug, CRC, clock, and timeout fields; DCN VM context and fault fields; HUBP0/HUBPREQ0/HUBPRET0 surface fetch, flip, TTU/QoS, memory-power, interrupt, cursor, and DMDATA fields; and the opening of the HUBP1 surface configuration.

## Important Constants And Register Areas

`DC_PERFMON4_*`, `DC_PERFMON5_*`, and `DC_PERFMON6_*` expose repeated performance-monitor field layouts. Each instance includes counter selection/control, counted value type and hardware stop selection, eight counter state readback selectors, perfmon run/control state, count-off interrupt control/status/ack fields, counter value interrupt status/ack bits, low/high value readback fields, and `PERFMON_READ_SEL`. `DC_PERFMON4_PERFCOUNTER_CNTL` is incomplete at the start of this slice, while `DC_PERFMON5` and `DC_PERFMON6` are complete within it.

The Azalia section covers display audio register layout. It includes output endpoints `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, input endpoints `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`, stream windows `AZF0STREAM8` through `AZF0STREAM15`, controller clock gating, audio DTO phase/module and force controls, SOCCLK deep-sleep exit behavior, underflow filler samples, data/BDL/CORB/RIRB/DP DMA snoop and isochronous controls, global capabilities, stream arbitration, CRC engines, memory power control/status, codec root/function parameters, power/reset/response controls, GTC group offsets, and audio port connectivity fields.

The DCHUBBUB section covers display hub fabric and memory arbitration. It includes SDPIF credit, response, snoop, and error controls; physical VM request mode; force-IO status capture; framebuffer, AGP, and local-HBM aperture fields; SDPIF and return-path memory power control; DCHUBBUB CRC source/value registers; DCC statistics; compbuf and DET sizing; memory power modes, latencies, and state; debug depth/stall controls; outstanding request limits; QoS force controls; DRAM state gating for self-refresh, p-state, c-state, and DCFCLK deep sleep; watermark sets A through D; HostVM controls; watermark change request/done controls; timeouts; VTG control; soft reset; clock and DCFCLK control; performance measurement windows; global timer; surface-check addresses; test debug index/data; and `FMON_CTRL`.

The DCN VM context section describes contexts 0 through 15. Each context has page-table depth and block-size fields plus high/low base, start, and end logical page number fields. The same section includes default address, fault control/status, and fault address fields. These macros describe how the display hub's VM view is programmed and how VM faults are reported.

The HUBP0 and HUBPREQ0 section covers surface fetch programming for pipe 0. It includes surface pixel format, rotation, mirror, alpha, address/tiling config, primary/secondary viewport start/dimensions for luma and chroma, request-size config, HUBP control and clock gating, VMPG config, DCFCLK/DPPCLK measurement windows, surface pitch, VMID, primary/secondary and metadata surface addresses, TMZ/DCC surface control, flip control, flip interrupts, in-use and earliest-in-use addresses, expansion mode, TTU/QoS watermarks, VM aperture and L1 TLB controls, blank/prefetch/flip/nominal timing parameters, per-line delivery parameters, cursor settings, and HUBPREQ memory power state.

`HUBPRET0_*` covers the return path: control fields, memory-power control/status, read-line programming and status, and interrupt mask/type/clear/status/overflow fields. `CURSOR0_0_*` covers cursor enable/mode/address/size/position/hot-spot/stereo control, memory power state, DMDATA address/control/QoS/status, and software DMDATA injection. The chunk ends with `HUBP1_DCSURF_SURFACE_CONFIG` and the first part of `HUBP1_DCSURF_ADDR_CONFIG`, establishing that the next chunk continues the repeated HUBP instance layout.

Common bitfield shapes in this chunk include full 32-bit value ports, 16-bit low/high address or data halves, 4-bit VMID selectors, status/clear/ack bit pairs, power force/disable/status fields, repeated instance suffixes, and repeated A/B/C/D watermark banks. Several registers contain side-effect fields such as interrupt clear, timeout clear, underflow clear, fault status clear, response status clear, soft reset, clock enable, and memory power force/disable.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. Its API surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask already shifted into register position.
- Repeated register prefixes such as `DC_PERFMON5`, `DCHUBBUB`, `DCN_VM_CONTEXT7`, `HUBPREQ0`, and `CURSOR0_0` encode hardware block and instance identity.

Consumers pair these definitions with register offsets from `dcn_3_5_0_offset.h`. The display stack commonly routes generated offsets, shifts, and masks into `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_SEQ`, and block-specific register field list macros. The DMUB DCN35 service also includes this header while initializing DCN35 register metadata. Semantic values, valid ranges, and sequencing rules are not defined here; they come from ASIC documentation, generated enum/value headers, and the higher-level DCN programming code.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior is implied by driver sequences that write and read the described registers.

Performance-monitor flows select events, counted value type, increment mode, run-enable start/stop sources, count-off behavior, and readback selectors, then read low/high counter values or acknowledge counter interrupts. Since perfmon instances 4, 5, and 6 use the same layout, callers can share programming logic across instances once the correct offsets are supplied.

Audio flows program Azalia endpoint and stream indexed data ports, configure audio DTO phase/module, choose DMA snooping and isochronous behavior, handle underflow filler behavior, configure CRC capture, expose codec capabilities, and control codec/function power state. Endpoint and stream register pairs have index/data access patterns, so ordering matters: the index field selects a register, and the data field transfers the payload.

DCHUBBUB and VM flows program memory apertures, page-table contexts, arbitration watermarks, request limits, HostVM behavior, fabric clock/deep-sleep policy, and timeout detection. The visible fields support both normal display timing setup and diagnostic/status paths: CRC values, DCC statistics, force-IO status, surface-check addresses, performance measurements, global timer snapshots, timeout interrupts, and FMON filtering.

HUBP/HUBPREQ/HUBPRET/CURSOR flows program a pipe's surface fetch state. A typical plane update writes surface format, tiling, request sizing, pitches, addresses, VMID, surface control, viewport geometry, prefetch/timing/TTU parameters, and flip controls, then observes flip-pending, in-use, earliest-in-use, underflow, timeout, and interrupt status. Cursor and DMDATA flows separately program cursor memory, position, stereo behavior, metadata payload address or software data, QoS, and underflow/done status.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state held in DCN 3.5.0 hardware registers.

Persistent hardware state represented in this chunk includes performance counter configuration and values, Azalia stream/endpoint/audio power state, DCHUBBUB memory aperture and VM context state, page-table base/start/end values, fabric arbitration and watermark state, memory power modes and statuses, HUBP surface format/address/tiling/viewport/flip state, TTU/QoS timing parameters, current in-use surface addresses, cursor memory and position state, DMDATA state, and interrupt/status latches. These values can persist across frames and until reset, modeset reprogramming, suspend/resume restore, or block power transitions.

Many fields are hardware-latched or side-effectful rather than ordinary storage. Examples include clear/ack bits, interrupt status, timeout status, underflow status, memory power state readbacks, current-size fields, no-outstanding-request flags, flip-pending and in-use address readbacks, CRC completion/results, VM fault status/address, and performance counter active/state fields. Callers should treat status fields as hardware observations and clear bits as commands.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.5.0 offset header and AMDGPU display register helper framework. Numeric masks are specific to the DCN 3.5.0 register database and should not be mixed with offsets from other ASIC generations unless explicitly validated.

Important integration points include:

- DCN35 DMUB register initialization, which includes `dcn_3_5_0_sh_mask.h` to populate register mask/shift metadata.
- HUBBUB memory arbitration, watermark, self-refresh, p-state, HostVM, timeout, CRC, and diagnostic code.
- HUBP/HUBPREQ/HUBPRET plane programming paths for surface address, tiling, flip, QoS, prefetch, VM, memory power, and cursor handling.
- Display audio/Azalia code that programs codec endpoints, streams, DTO, DMA policy, CRC, and audio memory power.
- Display VM and fault handling code that programs page-table contexts and decodes VM fault status/address.
- Performance-monitor and diagnostic paths that configure perf counters and read display fabric or pipe performance state.

The macros are intentionally low-level. They provide bit layout only; legal field values, ordering constraints, synchronization points, and read/write permissions are enforced, if at all, by higher-level DCN block code and hardware validation.

## Risks And Edge Cases

Generated-header drift is the primary risk. A wrong shift or mask can compile cleanly while corrupting unrelated bits in a display register, causing underflow, bad audio, wrong surface addressing, missed interrupts, incorrect VM translation, broken power management, or hard-to-debug display timing failures.

Chunk boundaries create local incompleteness. The opening `DC_PERFMON4_PERFCOUNTER_CNTL` group is missing earlier field definitions from the previous chunk, and the closing `HUBP1_DCSURF_ADDR_CONFIG` group is missing later masks from the next chunk. Whole-register validation for those two groups must include adjacent chunks.

Repeated-instance consistency matters. `DC_PERFMON5` and `DC_PERFMON6` should mirror the same field layout as the complete parts of `DC_PERFMON4`; `HUBP1` begins a layout that should match the full `HUBP0` register family where the hardware intentionally repeats instances. A one-instance generation error may only affect specific pipes or diagnostics.

Address, VM, and TMZ/DCC fields are high blast-radius. Wrong VMID, page-table, aperture, surface address, metadata address, DCC, or TMZ bits can point display fetches at the wrong memory, trigger VM faults, expose protected content incorrectly, or generate underflows. These fields should be programmed through established pipe update sequences, not open-coded writes.

Power, clock, and clear/ack fields are side-effect-prone. Memory power force/disable, clock gating, soft reset, underflow clear, timeout clear, interrupt clear, fault clear, and perf counter ack fields can change hardware state immediately. Register helpers should preserve unrelated fields and should use the documented write-one-to-clear or write-one-to-ack convention for each register.

Watermark and TTU fields are timing-sensitive. Incorrect urgency, self-refresh, p-state, prefetch, delivery, or QoS programming may pass compile tests but fail only under bandwidth pressure, high refresh, multi-plane, cursor, stereo, audio, or power-transition scenarios.

## Test And Validation Signals

Build validation should include DCN35 display and DMUB objects that include `dcn_3_5_0_sh_mask.h`. Missing or renamed macros usually fail at compile time; incorrect numeric values usually require generated-data comparison, register-database validation, or hardware testing.

Useful generated-data checks include:

- Compare this range against the authoritative DCN 3.5.0 register database.
- Verify non-overlapping masks and matching shifts for complete register groups, excluding the intentionally incomplete first and last groups.
- Diff repeated perfmon instances 4, 5, and 6 for structural consistency.
- Diff HUBP0/HUBPREQ0/HUBPRET0/CURSOR0 layout against other HUBP instances in adjacent chunks where repetition is expected.
- Cross-check DCN VM context 0 through 15 for identical context register layouts.
- Compare DCHUBBUB watermark banks A through D for consistent field widths and intended per-bank differences.

Runtime validation signals include successful DCN35 modesets, multi-plane flips without underflow or timeout interrupts, correct VM fault reporting and clearing, stable suspend/resume and runtime power transitions, correct cursor and DMDATA behavior, audio playback over display outputs, stable Azalia CRC/debug behavior where supported, correct perf counter readback/interrupt acknowledgment, and no regressions under bandwidth-heavy scenarios such as high refresh, multi-monitor, DCC-enabled surfaces, cursor movement, stereosync, and HostVM/system-memory display paths.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002061_research.md`. Whole-file research for `dcn_3_5_0_sh_mask.h` must merge adjacent chunks to complete the opening `DC_PERFMON4_PERFCOUNTER_CNTL` register group and the closing `HUBP1_DCSURF_ADDR_CONFIG` register group.

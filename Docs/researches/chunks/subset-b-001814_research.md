# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 30070-32536

## Scope

This chunk is a generated AMD Display Core Next 3.1.2 register-field mask slice. It contains C preprocessor constants only: `_SHIFT` macros for field bit positions, `_MASK` macros for the corresponding 32-bit register bitmasks, and comment markers that group those fields by register and address block. There are no functions, structs, enums, local variables, branches, loops, allocations, or direct MMIO accesses in this line range.

The range starts in the tail of the `OTG0` timing-generator register definitions, covers the complete `dce_dc_optc_otg1_dispdec` and `dce_dc_optc_otg2_dispdec` register-field surfaces, and then covers most of the `dce_dc_optc_otg3_dispdec` block through `OTG3_OTG_DRR_TIMING_INT_STATUS`. The requested line boundary stops at `OTG3_OTG_DRR_TIMING_INT_STATUS__OTG_DRR_V_TOTAL_REACH_OCCURRED_INT_MSK_MASK`; the final `OTG_DRR_V_TOTAL_REACH_OCCURRED_INT_TYPE_MASK` for that register appears on the next source line and is outside this chunk.

## Purpose And Hardware Surface

The purpose of this header section is to provide the bit layout ABI used by AMDGPU Display Core code when programming DCN 3.1.2 output timing generators. Companion generated headers provide register offsets; this mask header provides the field positions and masks that register helper macros use to encode, decode, and update individual hardware fields without scattering numeric bit positions through functional driver code.

Hardware areas represented in this chunk:

- `OTG0` tail definitions for manual flow control, dynamic refresh rate timing interrupt status, DRR vtotal reach/change/trigger/control fields, M/N constant DTO phase and modulo, request control, DSC start position, pipe update status, and spare register fields.
- Full `OTG1` and `OTG2` OPTC/OTG register sets for scanout timing, blanking, sync generation, trigger A/B control, forced count updates, flow control, stereo and interlace state, live status counters, snapshot capture, vertical interrupts, CRC capture, static screen detection, 3D structure control, global swap lock, master update locking, vstartup/vupdate/vready signaling, DRR, DSC start position, request control, pipe update status, and spare fields.
- The start-to-near-end of the `OTG3` register set through global update controls and the `OTG3_OTG_DRR_TIMING_INT_STATUS` fields included by the requested line range.

This is display-pipe register metadata. Its correctness affects modeset timing, vblank/vsync interrupt delivery, atomic update sequencing, variable refresh behavior, display CRC diagnostics, stereo/interlace output, Display Stream Compression positioning, global synchronization, and low-level pipe status reporting.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit index.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw mask within the 32-bit register.
- `// addressBlock: dce_dc_optc_otgN_dispdec` comments delimit per-OTG register blocks.
- `//OTGN_REGISTER_NAME` comments group the following field macros by hardware register.

Important field families in this chunk:

- Timing geometry: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN/MAX/MID`, `OTG_V_BLANK_START_END`, and `OTG_V_SYNC_A` define horizontal and vertical totals, blanking windows, sync ranges, polarity, and timing division controls. Most coordinate-like fields use 15-bit masks such as `0x00007FFFL` and `0x7FFF0000L`.
- DRR and vtotal control: `OTG_V_TOTAL_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, and `OTG_DRR_CONTROL` expose min/max/mid vtotal selection, event masks/acks, timing-update events, vtotal reach events, trigger windows, and last-used vtotal readback for variable refresh and frame pacing.
- Trigger and flow control: `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_FLOW_CONTROL`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL` define trigger source selection, pipe selection, polarity, edge detection, frequency selection, delays, clear bits, and manual/global update flow controls.
- Scanout status and counters: `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, and `OTG_COUNT_RESET` provide current timing-generator state, frame/field counters, h/v count readback, and counter reset/update controls.
- Stereo, interlace, and 3D output: `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, and `OTG_3D_STRUCTURE_CONTROL` expose current/next field, eye selection, stereo polarity, forced eye transitions, frame count reset/update state, interlace enable, and DP stereo/field output controls.
- Snapshot and interrupt controls: `OTG_SNAPSHOT_STATUS`, `OTG_SNAPSHOT_CONTROL`, `OTG_SNAPSHOT_POSITION`, `OTG_SNAPSHOT_FRAME`, `OTG_INTERRUPT_CONTROL`, and `OTG_VERTICAL_INTERRUPT{0,1,2}_{POSITION,CONTROL}` define snapshot request/clear/status fields and programmable vertical interrupt positions, sources, polarity, enables, clears, and status bits.
- Atomic update synchronization: `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_EN`, `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`, `OTG_VUPDATE_KEEPOUT`, and `OTG_GLOBAL_CONTROL0..4` define update locks, double-buffer enable/update-instantly behavior, master enable, master update lock status, global swap lock windows, vupdate keepout offsets, and global update lock selection.
- CRC and diagnostics: `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, `OTG_CRC0/1_WINDOW*`, `OTG_CRC0..3_DATA_*`, and CRC signature masks define capture enable, continuous/one-shot mode, stereo/interlace handling, capture windows, data readback, and mask controls for display CRC validation.
- Miscellaneous pipe fields: pixel readback, blank color not present in this chunk but nearby in the file, static screen frame counting, `OTG_CLOCK_CONTROL`, vstartup/vupdate/vready parameters, global sync status, DTO phase/modulo, request mode for horizontal duplicate handling, DSC start position, pipe update pending status, and full-width spare registers.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior is created when AMDGPU Display Core code combines these constants with matching register offsets and register access helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and table-driven field descriptors.

A typical runtime pattern is:

1. Driver code selects an OTG instance and matching register offset from generated DCN 3.1.2 register tables.
2. The code uses this chunk's `_SHIFT` and `_MASK` macros to pack or unpack a field value.
3. The display register abstraction performs an MMIO read, write, or read/modify/write.
4. Hardware stores configuration fields, exposes volatile status fields, or consumes side-effecting clear/ack/reset bits.

The state represented here is hardware register state rather than C heap or stack state:

- Timing configuration, sync polarity, update lock, DRR, CRC, stereo/interlace, GSL, vstartup/vupdate/vready, DTO, DSC start position, and request-control fields persist in hardware registers until reprogrammed, reset, or power-gated.
- Status, scan position, frame count, field count, stereo state, global sync status, pipe update pending, clock-on, busy, CRC data, and DRR last-used vtotal fields are volatile readbacks produced by display hardware.
- ACK, clear, reset, manual trigger, force-count, snapshot, and event-clear fields are side-effecting write paths. They should be treated as commands to a hardware state machine, not durable configuration storage.
- Double-buffered and master-update fields have sequencing constraints. The mask constants do not enforce that sequencing; callers must coordinate update locks and vupdate/vready timing to avoid partial pipe updates.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.2 register header family. It is normally consumed together with matching offset and register-list headers for `dcn_3_1_2`, ASIC-specific display resource tables, and the AMDGPU Display Core register helper layer.

Primary integration points include:

- OPTC/OTG timing code that programs scanout totals, blanking, sync, trigger behavior, count resets, and master enable state.
- Atomic modeset and plane-update paths that use update locks, double-buffer controls, master update locks, global update lock selection, vupdate keepout windows, and pipe update pending status.
- Vblank, vsync, vertical interrupt, vstartup, vupdate, vready, and DRR interrupt handlers that use status, clear/ack, mask, and type fields.
- VRR/DRR logic that manipulates vtotal min/max/mid, DRR trigger windows, vtotal reach ranges, vtotal change limits, and average frame settings.
- Display CRC and validation paths that configure CRC windows/selectors, trigger one-shot or continuous capture, and read CRC data registers.
- Stereo, interlace, and 3D display support that consumes field-number, eye-selection, forced next eye, stereo sync, and frame count fields.
- DSC and request scheduling paths that use `OTG_DSC_START_POSITION` and `OTG_REQUEST_CONTROL` fields.
- Power and clock sequencing paths that use `OTG_CLOCK_CONTROL` enable, gate-disable, soft-reset, clock-on, and busy fields before accessing dependent timing-generator state.

Because these are macros, invalid names usually fail at compile time only where referenced. Incorrect numeric values can compile cleanly and then misprogram MMIO registers at runtime.

## Risks And Maintenance Notes

- Numeric drift from the ASIC register specification is the main risk. A wrong mask or shift can write the wrong bit, corrupting timing, interrupts, update locking, DRR, CRC capture, or clock/reset behavior.
- The OTG1, OTG2, and OTG3 blocks are highly repetitive. Instance-prefix mistakes can route a modeset, interrupt clear, update lock, or CRC operation to the wrong display pipe.
- The requested chunk boundary cuts through the `OTG3_OTG_DRR_TIMING_INT_STATUS` macro group. Any reconciliation or review should account for the missing final `OTG_DRR_V_TOTAL_REACH_OCCURRED_INT_TYPE_MASK` on the next source line.
- Clear/ack/reset/manual-trigger fields have side effects. Generic read/modify/write helpers must avoid accidentally writing event clear bits while only intending to update masks or type fields.
- Update-lock, double-buffer, vupdate keepout, and GSL fields are timing-sensitive. Misuse can produce partially applied timing changes, stale pipe update state, missed vupdate events, or visible display glitches.
- DRR/vtotal fields influence frame pacing. Incorrect min/max/mid/range/window programming can create unstable VRR behavior, unexpected frame durations, or missed vtotal reach interrupts.
- Full-width fields such as DTO phase/modulo and spare registers provide no type or range checking. Callers must validate values against hardware semantics before packing them through the macros.
- Clock enable, gate-disable, soft-reset, clock-on, and busy fields interact with power management. Accessing the OTG while the block is gated, resetting, or busy can make status readbacks unreliable.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware/display behavior:

- Build AMDGPU/DCN 3.1.2 code and ensure referenced macro names from this range resolve.
- Run generated-header checks that each in-scope register field has the expected `_SHIFT`/`_MASK` pair, masks are 32-bit, and field masks do not overlap unexpectedly within a register.
- Compare the generated values against the authoritative DCN 3.1.2 register specification, especially repeated OTG1/OTG2/OTG3 blocks and the chunk boundary around `OTG3_OTG_DRR_TIMING_INT_STATUS`.
- Exercise modesets on pipes using OTG1 and OTG2, and on OTG3 for the fields included here, validating horizontal/vertical timing, sync polarity, master enable, clock state, and scan position readback.
- Test atomic updates with update locks, double-buffer controls, global update locks, GSL windows, vupdate keepout, and pipe update pending status.
- Exercise vblank/vsync/vertical interrupt paths and confirm status, mask, type, clear, and ack bits behave as expected.
- Run VRR/DRR tests that validate vtotal min/max/mid programming, DRR timing update interrupts, vtotal reach events, trigger windows, and last-used vtotal readback.
- Use display CRC tests to configure windows, enable one-shot and continuous capture, read CRC0-CRC3 data, and verify pending/status bits clear correctly.
- Test stereo/interlace modes where supported, checking field/eye status, forced next eye behavior, frame count reset/update, and 3D structure controls.
- Validate suspend/resume or runtime power transitions that toggle OTG clock, gate, reset, busy, vstartup, vupdate, and vready related fields.

## Chunk-Specific Summary

Lines 30070-32536 define a dense DCN 3.1.2 OTG mask/shift surface, not executable logic. The chunk's most important responsibilities are per-pipe timing programming for OTG1 and OTG2, the tail of OTG0 DRR/update/status metadata, and most of OTG3 up to the DRR timing interrupt status group. Correctness depends on exact generated bit positions and masks, instance-correct macro use, careful handling of side-effecting clear/ack/reset fields, and hardware tests that cover modeset timing, atomic update sequencing, interrupts, DRR/VRR, CRC, stereo/interlace, DSC start position, and OTG clock/reset behavior.

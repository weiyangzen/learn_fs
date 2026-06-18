# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 30060-32529

## Scope

This chunk is a generated DCN 3.1.6 register-field shift/mask slice. It contains C preprocessor constants only: every exported symbol is a `_SHIFT` or `_MASK` macro for a hardware register field, plus comments that identify register names and address-block boundaries. There are no C functions, structs, enums, allocations, loops, branches, or direct MMIO operations in this range.

The range starts at the tail of the `ODM3_OPTC_*` output data formatter fields, then covers the `dce_dc_optc_otg0_dispdec`, `dce_dc_optc_otg1_dispdec`, and `dce_dc_optc_otg2_dispdec` address blocks. The `OTG0`, `OTG1`, and `OTG2` blocks are highly repetitive and describe timing-generator fields for display timing, dynamic refresh, global synchronization, CRC capture, stereo/interlace state, interrupts, update locking, clocking, and status readback. The chunk ends at the `OTG2_OTG_SPARE_REGISTER` marker, before its field definitions appear in the next chunk.

## Purpose And Hardware Surface

This header provides the bit-layout ABI used by AMDGPU Display Core when programming DCN 3.1.6 output timing generators and the tail of an ODM/OPTC formatter block. Companion generated offset headers provide register addresses; this file supplies the masks and shifts that register-helper macros use to pack values into MMIO writes and decode MMIO reads.

Major hardware areas represented here:

- `ODM3_OPTC_*`: final fields for ODM/OPTC segment source selection, data format and DSC mode, DSC bytes-per-pixel, segment and DSC slice widths, input clock gating/enabling/status, memory selection/status, and spare input bits.
- `OTG0`, `OTG1`, and `OTG2` base timing: horizontal total, horizontal blanking, horizontal sync A, horizontal timing divider controls, vertical total/min/max/mid values, vertical blanking, vertical sync A, and vertical-total control fields for dynamic timing changes.
- Trigger and flow controls: trigger A/B source, pipe, polarity, edge detection, frequency, delay, manual trigger, force-count-now, manual flow control, and flow-control input status.
- Timing state readback: active/blank/sync/update status, current horizontal/vertical counters, nominal vertical counter, frame/VF/HV counters, pixel data readback, interlace state, stereo state, field selection, and snapshot registers.
- Interrupt and event fields: vertical-total event status, nominal-vsync status, vertical interrupt 0/1/2 position and control registers, trigger/force-count/snapshot/vsync/GSL interrupt masks and types, and global sync event state.
- CRC and validation registers: CRC control, DSC/data-format CRC mode, two programmable CRC windows, four CRC data result groups, and CRC signature masks.
- Update and synchronization controls: OTG update lock, double-buffer pending flags, master enable, static-screen detection, 3D structure control, global swap-lock (GSL) control and windows, master update lock, vupdate keepout, global update controls, and pipe update pending status.
- Dynamic refresh and clocking: DRR timing interrupt/status, DRR v-total reach range, v-total change limit, DRR trigger window, DRR average-frame/last-used-vtotal readback, m-constant DTO phase/modulo, clock enable/gate/reset/status, vstartup/vupdate/vready parameters, and DSC start position.

## Important Definitions

The generated interface follows the standard AMD display register naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for the field.
- `// addressBlock: ...` comments mark hardware instance blocks.
- `//<REGISTER>` comments group all following field macros for that register.

Important macro families in this chunk:

- `ODM3_OPTC_DATA_FORMAT_CONTROL`, `ODM3_OPTC_BYTES_PER_PIXEL`, and `ODM3_OPTC_WIDTH_CONTROL` define DSC/output-format packing fields such as `OPTC_DATA_FORMAT`, `OPTC_DSC_MODE`, `OPTC_DSC_BYTES_PER_PIXEL`, `OPTC_SEGMENT_WIDTH`, and `OPTC_DSC_SLICE_WIDTH`.
- `ODM3_OPTC_INPUT_CLOCK_CONTROL` and `ODM3_OPTC_MEMORY_CONFIG` expose input clock gate/enable/on status and OPTC memory selection/status for the ODM3 instance.
- `OTGx_OTG_H_*` and `OTGx_OTG_V_*` macros define the timing model: totals, blanking start/end, sync start/end, sync polarity/mode, timing divider mode, and DRR-oriented min/max/mid v-total controls.
- `OTGx_OTG_V_TOTAL_CONTROL`, `OTGx_OTG_DRR_*`, and `OTGx_OTG_M_CONST_DTO*` define variable-refresh and dynamic-refresh behavior: v-total source selection, min/max/mid replacement, forced lock events, event-active period, v-total reach interrupts, trigger windows, change limits, averaging, and DTO phase/modulo.
- `OTGx_OTG_TRIGA_*`, `OTGx_OTG_TRIGB_*`, `OTGx_OTG_FORCE_COUNT_NOW_CNTL`, `OTGx_OTG_TRIG_MANUAL_CONTROL`, and `OTGx_OTG_MANUAL_FLOW_CONTROL` define external/manual trigger, count-forcing, and flow-control bit positions.
- `OTGx_OTG_STATUS*`, `OTGx_OTG_COUNT_*`, `OTGx_OTG_PIXEL_DATA_READBACK*`, `OTGx_OTG_INTERLACE_*`, and `OTGx_OTG_STEREO_*` provide volatile readback fields for scanout state, counters, frame count, pixel sample data, interlace field state, stereo eye selection, and 3D structure status.
- `OTGx_OTG_VERTICAL_INTERRUPT*`, `OTGx_OTG_INTERRUPT_CONTROL`, `OTGx_OTG_V_TOTAL_INT_STATUS`, `OTGx_OTG_VSYNC_NOM_INT_STATUS`, and `OTGx_OTG_GLOBAL_SYNC_STATUS` define interrupt enable/status/clear/type fields for vstartup, vupdate, vready, vertical interrupts, nominal vsync, triggers, snapshots, force-count-now, and GSL-vsync-gap events.
- `OTGx_OTG_CRC_*` macros define CRC enable/mode/source/window fields and the readback data for CRC0 through CRC3. These fields are used for display validation and diagnostics rather than normal scanout programming.
- `OTGx_OTG_UPDATE_LOCK`, `OTGx_OTG_DOUBLE_BUFFER_CONTROL`, `OTGx_OTG_MASTER_UPDATE_LOCK`, `OTGx_OTG_VUPDATE_KEEPOUT`, and `OTGx_OTG_GLOBAL_CONTROL*` define double-buffer update locks, pending flags, global update lock selection, master update lock dead-band/keepout windows, DIG update positions, and field/eye update selection.
- `OTGx_OTG_CLOCK_CONTROL`, `OTGx_OTG_MASTER_EN`, `OTGx_OTG_CONTROL`, and `OTGx_OTG_PIPE_UPDATE_STATUS` expose OTG enable/gating/reset/busy state and pending flip, DC register, cursor, and vupdate-keepout state.

Here `x` is `0`, `1`, or `2`. The three OTG instances generally carry the same field layout, so instance-prefix correctness is part of the API contract.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when Display Core code combines these macros with generated register offsets and register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

Typical runtime flow:

1. Resource construction or an OPTC instance table selects an `OTG0`, `OTG1`, or `OTG2` register offset for the active pipe.
2. Shared OPTC code uses this header's field shifts and masks to program timing, enable the timing generator, lock double-buffered updates, configure vstartup/vupdate/vready windows, or decode status.
3. IRQ service code uses global-sync, vertical interrupt, vtotal, and vsync status masks to enable, clear, and classify display timing interrupts.
4. Debug, validation, or state-dump code reads CRC, counter, pipe-update, DRR, stereo/interlace, pixel-readback, and snapshot fields to report hardware state.

The state described by these macros is hardware register state, not persistent driver-owned memory:

- Persistent configuration includes programmed timing totals and blank/sync intervals, sync polarity, DRR min/max/mid and trigger parameters, global update lock settings, GSL windows, vupdate keepout windows, stereo/interlace mode, static-screen detection, CRC windows, interrupt masks/types, and clock/master-enable controls.
- Volatile readback includes current blank/active/sync/update state, counters, frame count, vupdate/vready/vstartup event status, update pending flags, lock status, clock-on/busy state, CRC result data, pixel readback, interlace/stereo current state, snapshot position/frame, and DRR last-used vtotal.
- Side-effecting fields include clear/ack bits for vtotal events, vertical interrupts, nominal vsync, global sync events, trigger occurrence, force-count-now, GSL-vsync-gap, snapshot clear/manual trigger, update lock toggles, count reset, manual trigger/flow-control controls, and soft reset bits.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.6 register header family. It is normally consumed together with the matching `dcn_3_1_6_offset.h` register address definitions and Display Core's register helper layer.

Important integration points include:

- OPTC timing-generator code under `drivers/gpu/drm/amd/display/dc/optc/`, especially DCN 3.x register tables such as `dcn31_optc.h`, `dcn314_optc.h`, and related implementation files. These tables use `SF(...)` and `SRI(...)` style macros to map `OTG0_*` mask/shift constants into per-instance `optc` register structures.
- IRQ service code under `drivers/gpu/drm/amd/display/dc/irq/`, where `OTG_GLOBAL_SYNC_STATUS`, `VSTARTUP_*`, `VUPDATE_*`, and `VUPDATE_NO_LOCK_*` fields are used to enable and clear timing interrupts.
- Resource code that instantiates timing generators and binds OTG register offsets/masks to display pipes. Instance alignment matters because this chunk exposes separate `OTG0`, `OTG1`, and `OTG2` names for equivalent hardware layouts.
- Display mode programming paths that set totals, blanking, sync, DSC/ODM formatting, DRR/vtotal behavior, vstartup/vupdate/vready timing, global update locks, and master enable state during modeset, fast update, and variable-refresh transitions.
- Diagnostic and validation paths that read OTG CRCs, counters, snapshots, pipe-update status, pixel readback, static-screen state, and interlace/stereo status. State capture code in DCN 3.1 reads registers such as `OTG_DRR_CONTROL`, `OTG_GLOBAL_SYNC_STATUS`, and `OTG_PIPE_UPDATE_STATUS`.
- DisplayPort/DSC and ODM paths, where the tail `ODM3_OPTC_*` fields describe segment source selection, data format, DSC byte rate, slice width, clocking, and memory selection feeding an output timing path.

Because this file only defines macros, missing symbols usually fail at compile time. Incorrect numeric masks or shifts can compile cleanly and only appear as runtime MMIO misprogramming.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.6 register specification is the primary risk. A wrong mask or shift can corrupt timing generator programming, interrupt handling, double-buffer updates, DRR behavior, CRC readout, or clock/reset control.
- The three OTG blocks are repetitive. Copy-generation mistakes can produce macros that are valid C symbols but point an `OTG1` or `OTG2` field at the wrong bit layout.
- Several fields are write-one-to-clear, trigger, ack, lock, or reset controls. Incorrect masks can clear latched diagnostics, retrigger manual actions, leave update locks asserted, or reset a timing generator unexpectedly.
- Timing fields are hardware-contract values. Incorrect horizontal/vertical totals, blanking, sync, vstartup, vupdate, or vready fields can cause modeset failures, flicker, missed flips, frame timing drift, or black screens.
- DRR and variable-refresh fields are sensitive to frame timing. Errors in vtotal min/max/mid, trigger windows, reach ranges, and change limits may only reproduce with FreeSync/VRR, low-refresh panels, or under compositor frame pacing.
- Global update lock, GSL, and vupdate keepout fields coordinate multiple pipes. Mistakes can cause unsynchronized pipe updates, stuck pending bits, or missed global-lock events in multi-display or ODM/MPO scenarios.
- CRC and pixel-readback fields are often used as test signals. Bad masks may hide real display corruption or produce false validation failures.
- The chunk starts inside the `ODM3_OPTC_DATA_SOURCE_SELECT` family and ends before the `OTG2_OTG_SPARE_REGISTER` fields, so final file-level reconciliation must merge neighboring chunks to describe those families completely.

## Test Signals

Useful validation combines generated-header checks, build coverage, and display hardware behavior:

- Build AMDGPU Display Core with DCN 3.1.6 support enabled and ensure all `OTG0`, `OTG1`, `OTG2`, and `ODM3_OPTC` field names referenced by OPTC, IRQ, resource, and diagnostic code resolve.
- Run generated-register consistency checks that every in-scope field has both `_SHIFT` and `_MASK`, masks fit in 32 bits, packed fields do not overlap unexpectedly, and repeated `OTG0`/`OTG1`/`OTG2` layouts match where the hardware spec says they should.
- Compare this range against the authoritative DCN 3.1.6 register specification, focusing on timing totals, interrupt clear bits, double-buffer pending flags, global update lock fields, DRR fields, and side-effecting trigger/reset bits.
- Exercise modesets on pipes backed by OTG0, OTG1, and OTG2, including common progressive modes, interlaced modes if supported, DSC modes, ODM/segment-width configurations, and stereo/3D paths if available.
- Test VRR/DRR paths by changing vtotal min/max/mid, trigger windows, reach-range interrupts, and average-frame settings while watching for missed flips, unstable refresh, or incorrect `OTG_V_TOTAL_LAST_USED_BY_DRR` readback.
- Validate vstartup, vupdate, vready, vtotal, vertical interrupt, nominal vsync, and no-lock interrupt handling through IRQ enable/clear/status paths.
- Verify update-lock and global-lock behavior with atomic commits, cursor updates, page flips, multi-plane updates, and multi-display synchronized updates; monitor `OTG_PIPE_UPDATE_STATUS` and double-buffer pending bits.
- Use CRC capture tests with both CRC windows and multiple source/data-format modes, confirming CRC0-CRC3 data readbacks and one-shot/continuous pending semantics.
- Run suspend/resume, runtime power, and display hotplug/modeset cycles to confirm clock gate, clock-on, busy, master-enable, memory-selection, and update-lock state recovers.
- Capture state dumps before and after modeset/flip/VRR events and confirm counters, snapshots, static-screen status, stereo/interlace state, global sync status, and pipe update pending fields decode correctly.

## Chunk-Specific Summary

Lines 30060-32529 define DCN 3.1.6 bit shifts and masks for the end of the `ODM3_OPTC` data-format/clock/memory block and most of the `OTG0`, `OTG1`, and `OTG2` output timing generator blocks. The content is generated register ABI, not executable logic. Correctness depends on exact mask/shift values, instance-correct macro use, careful treatment of side-effecting clear/trigger/reset bits, and hardware validation across modeset, IRQ, DRR/VRR, update-lock, CRC, multi-pipe sync, and suspend/resume paths.

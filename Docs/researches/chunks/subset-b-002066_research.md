# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h - subset-b-002066

## Scope

- Chunk id: `subset-b-002066`
- Source lines: 22127-24344
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h`
- Observed content: 2,218 source lines, all `#define` register field constants; 1,120 `__SHIFT` macros and 1,098 `_MASK` macros.

This chunk is generated AMD DCN 3.5.0 register field metadata. It does not define executable C, functions, structs, enums, or persistent software objects. Its interface is the preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants consumed by AMDGPU display register-access helpers.

## Purpose

The chunk publishes bit layouts for a contiguous display-controller register area that spans timing-generator state, global synchronization, memory power, performance monitoring, and DDC I2C control:

- The first region completes part of `OTG1` output timing generator field coverage, including CRC data/signature masks, static-screen control, 3D/stereo structure control, global sync lock/update status, master-update lock, GSL controls, vupdate keepout, global update controls, DRR timing, DTO, DSC start position, pipe update status, and spare register fields.
- `OTG2_*` and `OTG3_*` then define nearly complete repeated output timing generator layouts: horizontal and vertical timing totals, blanking/sync windows, triggers, count/reset controls, stereo state, snapshots, vertical interrupt controls, CRC windows/data, dynamic refresh rate fields, global update locking, clock control, vstartup/vupdate/vready status, GSL, DSC, and update-pending status.
- `GSL_SOURCE_SELECT` chooses ready and timing-sync sources for global-swap-lock coordination.
- `OPTC_CLOCK_CONTROL` and `OPTC_MISC_SPARE_REGISTER` describe shared OPTC clock/test-clock and spare-register fields.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` define ODM memory light-sleep or power-state control/status for eight memory slices.
- `DC_PERFMON15_*` defines a display performance-monitor instance with counter event selection, count modes, state readback, report count, counter-value interrupt status/clear masks, and 32-bit low/high counter values.
- `DC_I2C_*` begins shared display DDC hardware I2C field coverage: engine control, arbitration, interrupt/status handling, DDC1-DDC5 status/speed/setup fields, transaction descriptors, indexed data FIFO access, EDID detect control, and read-request interrupt bits through the visible DDC6 ACK shift.

The macros are paired by convention: `REGISTER__FIELD__SHIFT` is the least-significant bit position and `REGISTER__FIELD_MASK` is the already-shifted mask. Register addresses come from the matching DCN 3.5.0 offset/base-index headers.

## Important APIs, Types, and Macros

There are no normal C APIs or types in this range. Important exported macro groups are:

- OTG timing and scanout programming:
  - `OTG2_OTG_H_TOTAL`, `OTG2_OTG_H_BLANK_START_END`, `OTG2_OTG_H_SYNC_A`, `OTG2_OTG_V_TOTAL`, `OTG2_OTG_V_BLANK_START_END`, and `OTG2_OTG_V_SYNC_A` have the same layout repeated for `OTG3`. These fields describe mode timing values programmed during display mode set.
  - `OTG*_OTG_CONTROL`, `OTG*_OTG_MASTER_EN`, `OTG*_OTG_COUNT_CONTROL`, `OTG*_OTG_COUNT_RESET`, `OTG*_OTG_STATUS`, and frame/HV/VF count registers expose enablement, free-run/count behavior, reset, and live timing status.
  - `OTG*_OTG_CLOCK_CONTROL`, `OPTC_CLOCK_CONTROL`, and `OTG*_OTG_H_TIMING_CNTL` expose local timing-generator clock enable/gate/reset state, test-clock selection, and horizontal timing divider mode.
- Update, lock, and interrupt coordination:
  - `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_VUPDATE_KEEPOUT`, and `OTG*_OTG_GLOBAL_CONTROL0` through `GLOBAL_CONTROL4` define master/global update lock windows, DIG update positions, vupdate blocking, and double-buffer lock regions.
  - `OTG*_OTG_GLOBAL_SYNC_STATUS`, `OTG*_OTG_VSTARTUP_PARAM`, `OTG*_OTG_VUPDATE_PARAM`, and `OTG*_OTG_VREADY_PARAM` define vstartup/vupdate/vready event enable, type, status, clear, and position fields.
  - `OTG*_OTG_VERTICAL_INTERRUPT0/1/2_CONTROL`, `OTG*_OTG_VERTICAL_INTERRUPT*_POSITION`, `OTG*_OTG_INTERRUPT_CONTROL`, `OTG*_OTG_V_TOTAL_INT_STATUS`, `OTG*_OTG_VSYNC_NOM_INT_STATUS`, and `OTG*_OTG_DRR_TIMING_INT_STATUS` provide event and interrupt masks/acks for vertical positions, vtotal updates, nominal vsync, and DRR timing changes.
  - `OTG*_OTG_PIPE_UPDATE_STATUS` exposes pending flip, DC register update, cursor update, and vupdate-keepout status.
- Synchronization, stereo, CRC, and diagnostics:
  - `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X/Y`, `OTG*_OTG_GSL_VSYNC_GAP`, and `GSL_SOURCE_SELECT` define global-swap-lock enable, master mode, timing windows, gap detection, ready-source selection, and lock integration with master-update locks.
  - `OTG*_OTG_STEREO_CONTROL`, `OTG*_OTG_STEREO_STATUS`, `OTG*_OTG_STEREO_FORCE_NEXT_EYE`, and `OTG*_OTG_3D_STRUCTURE_CONTROL` define stereo enablement, eye select, polarity, frame count, and status.
  - `OTG*_OTG_CRC_CNTL`, CRC window registers, `OTG*_OTG_CRCn_DATA_RG/B`, and CRC signature mask registers expose scanout CRC capture, windowing, continuous/triggered behavior, and channel masks.
  - Snapshot, status-position, pixel-data-readback, spare-register, trigger A/B, and manual trigger fields support hardware diagnostics and bring-up.
- DRR, DSC, DTO, and request behavior:
  - `OTG*_OTG_V_TOTAL_MIN/MAX/MID`, `OTG*_OTG_V_TOTAL_CONTROL`, `OTG*_OTG_DRR_*`, and `OTG*_OTG_DRR_CONTROL` define dynamic refresh rate limits, trigger windows, reach ranges, and last-used vtotal readback.
  - `OTG*_OTG_M_CONST_DTO0/1` contains full-width phase/modulo fields for timing DTO programming.
  - `OTG*_OTG_DSC_START_POSITION` and `OTG*_OTG_REQUEST_CONTROL` define DSC start X/line and request mode for horizontal duplicate handling.
- Shared ODM/perfmon/I2C blocks:
  - `ODM_MEM_PWR_CTRL*` and `ODM_MEM_PWR_STATUS` expose force/disable/power-state fields for ODM memories 0-7 and unassigned/vblank power modes.
  - `DC_PERFMON15_PERFCOUNTER_CNTL`, `CNTL2`, `STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_LOW/HI`, and `PERFMON_CVALUE_LOW` configure event counting, run/stop/start selectors, counter states, report counts, interrupt clear/status, and count readback.
  - `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDCn_HW_STATUS`, `DC_I2C_DDCn_SPEED`, `DC_I2C_DDCn_SETUP`, `DC_I2C_TRANSACTION0-3`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, and `DC_I2C_READ_REQUEST_INTERRUPT` define hardware DDC I2C ownership, setup, command sequencing, byte access, EDID detection, and interrupt/status fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is implemented by display code that includes this generated header and uses register helper macros such as `REG_UPDATE`, `REG_GET`, `REG_SET`, `REG_WAIT`, and table-driven mask/shift structures.

The hardware flows implied by this chunk include:

1. Mode-set programming writes OTG horizontal/vertical totals, blanking and sync windows, polarity, divider mode, DTO/DSC fields, then enables the timing generator and watches clock/status fields.
2. Atomic updates and page flips use master/global update lock fields, vupdate keepout windows, vertical interrupt positions, and pipe update pending bits so plane/cursor/DIG updates land at the intended frame boundary.
3. DRR and variable-refresh flows adjust vtotal min/max/mid, DRR trigger windows, vtotal reach ranges, change limits, and timing-update interrupt fields.
4. Multi-pipe or synchronized-display flows configure GSL source selection, GSL windows, gap limits, master mode, and master-update-lock GSL integration across OTG instances.
5. CRC and diagnostics flows select CRC source/window behavior, trigger or continuously capture CRCs, then read CRC data/signature/status and snapshot/pixel-readback fields.
6. ODM power management forces or disables per-memory light-sleep/power modes and validates the resulting memory state before or after display pipe use.
7. Performance monitoring selects DC perf events and counter behavior, starts/stops perfmon capture, reads low/high counters, and acknowledges counter interrupts.
8. DDC I2C transactions acquire I2C register ownership, configure selected DDC speed/setup, program up to four transaction descriptors plus indexed data bytes, assert GO, poll or handle status/interrupts, process NACK/timeout/overflow/stop conditions, and release ownership.

## State and Persistence Behavior

The macros are stateless compile-time constants. They describe MMIO register fields whose state lives in display hardware:

- Persistent configuration until reset or reprogramming: timing totals, blank/sync windows, polarity, stereo control, GSL enable/window/source selection, master update lock windows, vstartup/vupdate/vready offsets, DRR limits, DSC start, clock gating disables, ODM memory power mode bits, perfmon event/counter selection, and I2C speed/setup values.
- Transient command or handshake fields: timing count reset, snapshot trigger/update lock, manual trigger fields, interrupt clear/ack bits, GSL gap clear, static-screen interrupt clear, 3D frame-count reset, DRR timing clear, perfmon counter interrupt clear/ack, I2C GO/soft reset/status reset/send reset, transaction START/STOP, data index write, EDID detect send reset, and read-request ACK bits.
- Status and observation fields: OTG busy/clock-on, frame/HV/VF counters, live vertical/horizontal positions, stereo/field status, trigger occurred/status bits, CRC data, vstartup/vupdate/vready event/status bits, vtotal and DRR event status, pipe update pending flags, ODM memory power states, perfcounter state/active/interrupt bits, I2C hardware/software status, timeout/NACK/overflow/stop, EDID detection, and read-request interrupt state.
- The full-width spare, DTO phase/modulo, perfmon low/high, and CRC data fields are opaque hardware values from the driver point of view and persist only according to the associated hardware domain reset and update rules.

## Dependencies

This chunk depends on the generated AMDGPU/DCN register infrastructure:

- Matching register offsets and base indices in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`.
- DC register-access helpers and generated field tables that expect the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.
- Output pixel processor/timing-generator code in the AMD display stack, especially OPTC/OTG implementations that map these fields into per-generation `dcn*_optc` register/mask/shift tables.
- Interrupt and flip/update code that uses vstartup, vupdate, vready, vertical interrupt, vtotal, DRR timing, and pipe-update status fields.
- CRC/debug and validation paths that depend on the OTG CRC, snapshot, status-position, pixel-readback, trigger, and spare-register fields.
- Display DDC I2C consumers, such as the DCE/DCN hardware I2C implementation, which use `DC_I2C_*` fields for EDID, DDC, and sink-management transactions.
- Performance monitoring and power-management code that uses `DC_PERFMON15_*` and `ODM_MEM_PWR_*` when those hardware blocks are present in the DCN 3.5.0 ASIC.

The path is inside a Ceph client source corpus, but the file content is Linux AMDGPU display-driver register metadata and is not Ceph-specific.

## Integration Points

Important integration points are:

- Kernel mode setting and atomic commit, where OTG timing fields, update locks, and interrupt positions coordinate visible scanout changes.
- Variable refresh rate and dynamic refresh rate, where vtotal min/max/mid and DRR status/trigger fields must align with the mode and stream timing model.
- Multi-display synchronization and multi-pipe composition, where GSL and global update lock fields coordinate multiple timing generators and DIG update points.
- Display diagnostics and automated validation, where CRC capture, frame counters, snapshots, pixel readback, trigger status, and perfmon counters provide hardware evidence.
- Display power management, where ODM memory power controls and OPTC/OTG clock fields interact with suspend/resume, idle, and low-power display paths.
- EDID/DDC and sink communication, where the shared `DC_I2C_*` definitions back hardware I2C transactions on DDC1-DDC5 and read-request interrupt handling across DDC channels.

## Risks and Edge Cases

- Generated mask/shift drift silently corrupts MMIO field access. Timing, update-lock, interrupt-clear, clock/reset, ODM power, and I2C ownership fields are especially sensitive because wrong bits can cause display hangs, missed vblank events, or failed EDID reads.
- `OTG2` and `OTG3` contain large repeated layouts. A generation or copy-index mismatch can compile cleanly while programming the wrong timing generator.
- The chunk starts in the middle of `OTG1` CRC field coverage and ends in the middle of `DC_I2C_READ_REQUEST_INTERRUPT`; adjacent chunks are required for complete per-file interpretation.
- ACK/clear/reset/GO fields likely have write-one or pulse semantics. Generic read-modify-write usage can drop events or retrigger hardware if callers do not follow the register protocol.
- Multi-bit timing and window fields, such as h/v totals, blank/sync starts and ends, GSL windows, global update positions, vupdate offsets, DRR limits, DSC start positions, perfmon selectors, I2C prescale/time limits, and transaction counts require range validation before field insertion.
- Master/global update lock windows can block register updates if programmed around the wrong scan position or never released.
- GSL master/source selection and vsync-gap fields affect synchronization across pipes; incorrect programming can produce frame slips or master/slave deadlocks.
- ODM memory power force/disable fields can make downstream register accesses unreliable if software does not wait for the expected `ODM_MEM*_PWR_STATE`.
- I2C arbitration and status bits represent shared ownership with hardware/firmware users. Failure to acquire or release ownership can starve firmware pollers or corrupt DDC transactions.
- Perfmon counter interrupt/status fields can be stale unless counters are reset, clock enabled, and interrupt status acknowledged in the expected order.

## Test Signals

Useful validation signals for code using this chunk:

- Build coverage for DCN 3.5.0 display code that includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`, catching missing, renamed, or misgenerated macros.
- Generated consistency checks that every visible field has coherent shift/mask pairs, masks match shifts and widths, and repeated `OTG2`/`OTG3` and `DC_I2C_DDC1-5` layouts remain equivalent where expected.
- Field insert/extract tests for h/v timing values, global update windows, vertical interrupt positions, DRR limits, GSL windows, CRC channel masks, ODM memory power fields, perfmon selectors/counters, I2C transaction counts, I2C data indexes, and EDID detect controls.
- Hardware smoke tests for mode set, vblank/vupdate/vready interrupt delivery, atomic page flips, cursor updates, VRR/DRR transitions, stereo/3D modes if supported, and multi-pipe GSL synchronization.
- CRC and diagnostic tests that program CRC windows, capture CRC data, use snapshot/status-position registers, and confirm pipe-update pending bits clear after flips and cursor updates.
- Suspend/resume and low-power display tests that exercise ODM memory power states and OTG/OPTC clock control without losing timing-generator state unexpectedly.
- DDC/EDID tests across DDC1-DDC5, including NACK, timeout, overflow, repeated-start transaction descriptors, EDID detect retries, and read-request interrupt ACK/mask handling.
- Perfmon validation that selected events count, counter low/high reads are stable enough for the caller's sampling model, and counter interrupt clear/status behavior matches the expected hardware semantics.

## Chunk Boundary Notes

The first visible line is `OTG1_OTG_CRC2_DATA_B__CRC2_C_MASK`, so earlier `OTG1` CRC2 shifts and masks are in the previous chunk. The final visible line is `DC_I2C_READ_REQUEST_INTERRUPT__DC_I2C_DDC6_READ_REQUEST_ACK__SHIFT`; the DDC6 read-request mask shift and all masks for this register continue after line 24344. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final per-file research document for `dcn_3_5_0_sh_mask.h`.

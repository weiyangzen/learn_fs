# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 25261-27727

## Purpose

This chunk is a generated AMDGPU DCN 3.2.0 register shift/mask header slice. It contains C preprocessor constants only; there are no functions, structs, enums, storage definitions, locks, allocations, or executable branches. The macros publish bit positions (`__SHIFT`) and masks (`_MASK`) for DCN 3.2 display timing-generator and OPTC-misc MMIO registers, and callers combine them with the matching DCN 3.2.0 offset header and AMD display register helpers.

The range starts in the tail of `OTG1_OTG_H_TIMING_CNTL`, covers the rest of the `OTG1` timing-generator block, covers complete `OTG2` and `OTG3` timing-generator blocks, then covers the `dcn_dc_optc_optc_misc_dispdec` block for GSL source selection, OPTC clock control, ODM memory power control/status, and an OPTC misc spare register. It ends at the beginning of the HPD0 DIO block with two shift constants for `HPD0_DC_HPD_INT_STATUS`. The chunk defines 2,141 macros: 1,070 shift constants and 1,071 mask constants.

Although this repository path is under `ceph-client`, this file is AMD Display Core hardware metadata, not distributed-filesystem logic.

## Important APIs, Types, And Macros

The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit index of a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for extracting or updating that field.
- `// addressBlock: ...`: generated grouping comments matching hardware register blocks.

There are no direct register-access APIs in this header. The macros become usable through AMD DC register-table builders such as `SF(...)`, `SRI(...)`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and IRQ register-entry helpers in the display code.

The covered register groups are:

- `OTG1` tail: vertical totals, vertical blank/sync, trigger A/B, force-count-now, flow control, stereo/interlace/readback/status, snapshots, vertical interrupts, CRC windows/results, static-screen/3D-structure controls, global sync/update-lock/GSL, DRR, M constant DTO, DSC start, pipe update status, and spare fields. The first three macros are only masks for `OTG1_OTG_H_TIMING_CNTL`; the shifts for that register live in the previous chunk.
- `OTG2` and `OTG3`: complete timing-generator instances with horizontal timing, vertical timing, master enable, stereo/interlace, status and counters, vertical interrupts, CRC diagnostics, global sync/update-lock, GSL windows, DRR, DSC start position, and update-pending status.
- `GSL_SOURCE_SELECT`: source selection for `GSL0`, `GSL1`, `GSL2`, and timing-sync source routing.
- `OPTC_CLOCK_CONTROL`: OPTC display-clock gating disable, clock-on status, test clock selection, and fine-grain clock-gating repeat disable.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`: power force/disable/state fields for ODM memory slices 0-7 plus unassigned/vblank memory power policies.
- `OPTC_MISC_SPARE_REGISTER`: low 8-bit spare field.
- `HPD0_DC_HPD_INT_STATUS`: only the `DC_HPD_INT_STATUS` and `DC_HPD_SENSE` shift constants appear in this chunk; masks and remaining fields are in the following chunk.

Important field families include:

- Timing geometry: `OTG_H_TOTAL`, horizontal/vertical blank start/end, sync start/end, sync polarity, vertical total/min/max/mid, `OTG_H_TIMING_DIV_MODE`, and DSC start position.
- Timing-generator enablement: `OTG_MASTER_EN`, disable/start point control, field-number control/polarity, output mux, current master-enable state, OTG clock enable/on/busy/gate-disable fields, and VTG-facing update timing.
- Dynamic refresh and manual triggers: `OTG_V_TOTAL_CONTROL`, `OTG_DRR_TRIGGER_WINDOW`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_CONTROL`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, and force-count-now fields.
- Interrupt and event status: vertical interrupt 0/1/2 position/control bits, `OTG_GLOBAL_SYNC_STATUS` VSTARTUP/VUPDATE/VREADY/no-lock enable/type/occurred/status/clear fields, `OTG_V_TOTAL_INT_STATUS`, and nominal vsync clear fields.
- Synchronization and update locking: `OTG_MASTER_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL4`, `OTG_VUPDATE_KEEPOUT`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`, and global `GSL_SOURCE_SELECT`.
- Diagnostics and readback: `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, pixel readback, snapshot status/control/position/frame, CRC control/window/data/signature fields, and pipe update pending bits.
- Low-power controls: `OPTC_CLOCK_CONTROL` and ODM memory power control/status fields.

## Control Flow

This chunk has no local runtime control flow. Runtime behavior is provided by display code that includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`, then token-pastes register and field names into per-ASIC tables.

The inferred programming sequence for the OTG/OPTC fields is:

1. A DCN 3.2 resource constructor builds timing-generator, IRQ, hardware-sequencer, and DMUB register tables from generated offset and shift/mask macros.
2. Timing-generator code programs horizontal and vertical totals, blanking, sync, polarity, stereo/interlace, DSC, ODM, and output mux fields before enabling the OTG.
3. Clock and enable paths use `OTG_CLOCK_CONTROL`, `OTG_CONTROL`, and related status fields to enable or disable timing generation and to wait for idle/busy transitions.
4. DRR and FAMS/manual-trigger paths update `OTG_V_TOTAL_MIN/MAX/MID`, `OTG_V_TOTAL_CONTROL`, trigger A/B, and DRR window/change/last-used fields.
5. Atomic updates and synchronized multi-pipe updates use update locks, double-buffer controls, global-control windows, GSL source selection/windows, and vupdate keepout fields.
6. IRQ service code enables and clears VSTARTUP, VUPDATE no-lock, and vertical-line interrupts through the generated global-sync and vertical-interrupt fields.
7. Diagnostics read status, counters, CRC results, snapshot positions, pipe pending state, and ODM memory power status; low-power init code can set ODM memory policies.

The generated constants do not encode ordering requirements, access type, volatility, write-one-to-clear behavior, reset timing, or polling delays. Those rules live in AMD DC/DMUB code and hardware specifications.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk, memory, or firmware. It describes MMIO-backed state in DCN 3.2 display hardware.

State described by this chunk includes:

- Programmed mode timing: totals, blanking, sync positions, polarities, horizontal div mode, vertical total min/max/mid, DSC start, and request behavior.
- Enable and clock state: OTG master enable, current enable state, OTG busy/clock-on, OPTC clock gating state, output mux, and VTG/OPTC integration fields.
- Frame/update state: update locks, double-buffer update pending, global-update lock selection, digital update positions, vupdate keepout, GSL readiness/windows, and pipe update pending bits.
- Event and interrupt state: VSTARTUP/VUPDATE/VREADY/no-lock event occurred/status/clear bits, vertical interrupt control/clear/status, DRR timing/reach events, vtotal-min events, and nominal vsync clear.
- Diagnostics: frame/vblank counters, current scan position, stereo/interlace state, snapshot data, pixel readback, CRC windows/results/signatures, static-screen counters, and pipe update state.
- Low-power policy/status: ODM memory force/disable controls, unassigned/vblank power modes, and per-memory-slice power states.

Persistence is hardware-defined. Programmed fields typically survive until modeset reprogramming, power gating, suspend/resume, GPU reset, or a new atomic update. Status and event bits may be read-only, sticky, self-clearing, write-one-to-clear, or latched at specific scanout/update boundaries. Trigger, clear, reset, and manual-force fields should be treated as side-effectful.

## Dependencies And Integration Points

This chunk depends on synchronized generated register metadata:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` supplies the matching `reg...` addresses and base indices for the register names in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.h` builds the DCN 3.2 timing-generator mask/shift table. It references many fields present in this chunk, including `OTG_V_TOTAL_CONTROL`, `OTG_TRIGA_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_GLOBAL_CONTROL*`, `OTG_GSL_*`, `OTG_DRR_*`, `OTG_CRC_*`, `OTG_PIPE_UPDATE_STATUS`, and `GSL_SOURCE_SELECT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.c` uses those fields to enable/disable CRTC timing, wait for OTG busy to clear, program ODM bypass, set horizontal timing division, and set DRR/manual-trigger behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c` uses `OTG_GLOBAL_SYNC_STATUS` fields for VSTARTUP and VUPDATE no-lock interrupt enable/clear entries, and vertical interrupt registers for vline interrupts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_hwseq.c` uses `ODM_MEM_PWR_CTRL3` to set default OPTC memory low-power behavior when enabled by debug policy.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` includes this generated header with the offset header to initialize DCN32 DMUB register metadata.

The instance naming is important. `OTG1`, `OTG2`, and `OTG3` fields are per-timing-generator instances, but DC register tables commonly define masks from `OTG0` field names and offsets from per-instance `SRI(...)` entries. The replicated layouts in this chunk must therefore remain identical where the register-table code assumes a shared instance layout.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Wrong masks or shifts compile cleanly but silently program the wrong MMIO bits.
- This chunk starts mid-register for `OTG1_OTG_H_TIMING_CNTL` and ends mid-register for `HPD0_DC_HPD_INT_STATUS`; adjacent chunks are required before making complete per-register claims for those two registers.
- Repeated OTG instance blocks are easy to miscompare. A generation error limited to `OTG2` or `OTG3` can produce connector-, pipe-, or ODM-topology-specific failures rather than global display failure.
- Trigger and clear bits are side-effectful. Broad read-modify-write operations over `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_GLOBAL_SYNC_STATUS`, vertical interrupt controls, DRR event status, or CRC controls can accidentally acknowledge events, fire triggers, or clear diagnostics.
- Timing fields are packed 15-bit or 16-bit values. Off-by-one conventions are handled by callers, so masks must match hardware width precisely or mode timings can be subtly wrong.
- DRR/FAMS fields affect visible refresh behavior. Incorrect `OTG_V_TOTAL_CONTROL`, manual trigger, DRR window, or vtotal-change masks can cause flicker, missed variable-refresh updates, bad vblank stretching, or clock-switch instability.
- Update-lock, GSL, and vupdate-keepout fields coordinate atomic updates across pipes. Bad masks can create underflow, tearing, update stalls, or deadlocks waiting for pending bits to clear.
- IRQ fields mix enable, type, occurred, status, and clear bits in the same register. Wrong bit definitions can cause missed vblank/vupdate interrupts, interrupt storms, or stuck event state.
- ODM memory power fields can affect low-power entry/exit and memory availability. Incorrect force/disable/status masks may cause power regressions, underflow during vblank, or inability to validate memory power state.
- `0xFFFFFFFFL` full-register masks such as DTO phase/modulo and spare fields should be treated carefully in signed contexts; AMD helpers generally operate on 32-bit register values.

## Test Signals

Useful validation should combine generated-header checks with DCN32 display behavior:

- Build AMDGPU display code with DCN32 enabled. Compile failures in `dcn32_optc.h`, `dcn32_optc.c`, `irq_service_dcn32.c`, `dcn32_hwseq.c`, or `dmub_dcn32.c` indicate offset/field-name drift.
- Mechanically verify that each field in the repeated `OTG1`, `OTG2`, and `OTG3` blocks has the expected `__SHIFT`/`_MASK` pair, except for known chunk-boundary partials.
- Diff the `OTG2` and `OTG3` layouts against `OTG1` and the authoritative DCN 3.2 register source to catch instance-specific generation mistakes.
- Exercise modesets across common and edge timings, interlace/stereo paths where supported, DSC/ODM topologies, horizontal timing division modes, and enable/disable sequences while watching for OTG busy waits and master-enable state transitions.
- Exercise DRR/FAMS/variable-refresh paths, including vertical total min/max/mid, manual trigger, trigger windows, vtotal-change limits, and vblank stretching.
- Run atomic update and multi-display synchronization tests that stress update locks, double-buffer pending bits, GSL windows, global-control windows, and vupdate keepout behavior.
- Verify vblank, vupdate no-lock, and vertical-line interrupts on all active OTG instances; watch for missed interrupts, stuck clear bits, and unexpected interrupt storms.
- Use CRC and readback diagnostics where available to confirm CRC enable/window/result fields, frame counters, scanout position, snapshot data, and pipe update pending states.
- Test suspend/resume, display hotplug, power-gating, and memory low-power policy with `enable_mem_low_power.bits.optc` enabled, checking ODM memory power status and underflow logs.

## Cross-Chunk Notes

This is partial-file research for `dcn_3_2_0_sh_mask.h`. The previous chunk is needed for the beginning of `OTG1_OTG_H_TIMING_CNTL` and earlier OTG1 fields. The next chunk is needed for the masks and remaining fields of `HPD0_DC_HPD_INT_STATUS` and subsequent HPD/DIO definitions. The final per-file document should merge this with all other chunks before summarizing the complete DCN 3.2.0 shift/mask namespace.

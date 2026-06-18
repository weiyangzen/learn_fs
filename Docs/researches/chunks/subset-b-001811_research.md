# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 22458-24978

## Scope

This chunk is a generated DCN 3.1.2 register-field shift/mask slice from `dcn_3_1_2_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` values for field low-bit positions, `_MASK` values for raw 32-bit register masks, and generated comments that group fields by register and address block. There are no C functions, structs, enums, branches, loops, local variables, allocation paths, or in-memory data structures in this range.

The chunk starts in the tail of `DC_PERFMON14_PERFCOUNTER_STATE`, completes the remaining `DC_PERFMON14` perfmon control/readback registers, covers `MPCC0` through `MPCC3`, covers shared MPC configuration/status/CRC/vupdate-lock registers, covers `DC_PERFMON15`, then defines the MPCC output-gamma and gamut-remap register fields for complete `MPCC_OGAM0`, `MPCC_OGAM1`, `MPCC_OGAM2`, and the beginning of `MPCC_OGAM3`.

## Purpose And Hardware Surface

The purpose of this range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.2 MPC/MPCC hardware. Companion generated offset headers provide register addresses; this header provides the field masks and shifts used by register helper macros to encode values, decode readbacks, and update MMIO registers without hard-coded bit arithmetic in functional driver code.

Major hardware areas represented here:

- `DC_PERFMON14` tail fields for MPC/MPCC perfmon state, report/count-off controls, clock/run start/stop selection, counter-value interrupt status/ack for counters 0-7, high/low counter readback, and read selection.
- `MPCC0` through `MPCC3` compositor slice controls: top/bottom input selection, OPP target selection, blend/alpha/gain mode, stereo/multi-plane control, update-lock source/status, top/bottom gain, background color components, output-gamma memory power control, and idle/busy/disabled status.
- Shared `MPC` configuration registers for clock control, soft reset of MPCC and MPC subblocks, CRC control/selection/results, perfmon event enable, bypass background color, host read rate, DPP/OPP/MPCC/DWB pending status, per-pipe vupdate lock sets, and DWB0 mux selection/status.
- `DC_PERFMON15` full perfmon block with counter event selection, counted value type, hardware stop/count-off selectors, per-counter states, perfmon state, interrupt controls, clock enable, and low/high readback.
- `MPCC_OGAM0`, `MPCC_OGAM1`, and `MPCC_OGAM2` complete output-gamma blocks: OGAM mode/select/current-state controls, LUT index/data/control, RAM A and RAM B piecewise-linear region definitions for RGB channels, offsets, region LUT offsets/segment counts, gamut-remap coefficient format/mode, and 3x4-style gamut-remap coefficient pairs for A and B coefficient banks.
- `MPCC_OGAM3` beginning: OGAM control, LUT access, RAM A start/end/offset fields, and RAM A region pairs through the chunk boundary at `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_16_17`.

## Important Definitions

The exported interface is the generated macro naming pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position where the field starts.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask within the 32-bit register.
- `// addressBlock: ...` comments identify the register aperture for following definitions.
- `//<REGISTER>` comments group the field definitions for each register.

Important field families in this chunk:

- Perfmon fields use `PERFCOUNTER_EVENT_SEL`, `PERFCOUNTER_CVALUE_SEL`, `PERFCOUNTER_INC_MODE`, `PERFCOUNTER_HW_CNTL_SEL`, `PERFCOUNTER_RUNEN_MODE`, `PERFCOUNTER_CNTOFF_*`, `PERFCOUNTER_RESTART_EN`, `PERFCOUNTER_INT_EN`, `PERFCOUNTER_ACTIVE`, and selector fields to configure event counting and readback multiplexing.
- Perfmon status/readback fields include per-counter 2-bit state fields, counter-state select bits, `PERFMON_STATE`, `PERFMON_RPT_COUNT`, counter-value interrupt status/ack bits for counters 0-7, high 16-bit readback, low 32-bit readback, and read selection.
- MPCC compositor fields use 4-bit selectors for top/bottom input and OPP ID, mode fields for blend and alpha behavior, 8-bit global alpha/gain fields, 19-bit gain fields, 12-bit background color components, and status bits for idle/busy/disabled.
- MPCC stereo/multi-plane fields include stereo/multi-plane enable, mode, frame/field alternation, forced next-frame/top polarity, and current frame polarity readback.
- MPCC update-lock fields select which lock source controls each compositor slice and expose locked-status bits. These interact with atomic display updates and vupdate locking.
- MPCC memory-power fields cover output-gamma memory power force, disable, low-power mode, and current power state for each MPCC instance.
- MPC soft-reset fields independently reset `MPCC0-3`, scalar/filter-like `MPC_SFR0-3` and `MPC_SFT0-3` subblocks, plus a global MPC soft reset.
- MPC CRC fields select enable/continuous/one-shot behavior, stereo/interlace mode, CRC source, update lock, DPP/OPP/DWB source selectors, mask bits, and result readbacks for AR, GB, and C channels.
- MPC pending-status fields expose surface/config/cursor update pending bits for DPP0-3, config update pending bits for OPP0-3 and MPCC0-3, and DWB0 pending state.
- Vupdate-lock set registers provide single-bit lock controls for address/config/cursor combinations, address/config-only combinations, address-only, config-only, and cursor-only domains for pipe sets 0-3.
- OGAM LUT fields provide a 9-bit LUT index, 18-bit LUT data, write color mask, read color selection, read debug, host selection, and configuration mode.
- OGAM piecewise-linear fields are replicated for RAM A and RAM B, RGB channels, and region pairs. Start/end/base/slope values are mostly 16-bit or 18-bit payloads, offsets are 19-bit, region LUT offsets are 9-bit, and region segment counts are 3-bit fields packed two regions per register.
- Gamut-remap fields provide coefficient format/mode/current mode and paired 16-bit coefficient fields for rows/columns `C11` through `C34` in A and B banks.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code combines these constants with matching register addresses and helper macros such as generated `REG_GET`, `REG_SET`, `REG_UPDATE`, or table-driven register accessors.

A typical runtime use is:

1. Select a DCN 3.1.2 register address from a companion offset/register header.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack a field value, unpack a readback, or generate a read/modify/write mask.
3. Perform MMIO access through the display register abstraction.
4. Let hardware retain, consume, report, or clear the associated state.

The persistent state represented here is hardware state, not software-owned data:

- MPCC selection, blending, background color, gain, OPP routing, output-gamma mode, LUT contents, PWL RAM region programming, and gamut-remap coefficients persist in display hardware until reprogrammed, reset, or power-gated.
- MPC clock, soft reset, memory-power, mux, vupdate-lock, and CRC controls are configuration state that affects live display pipeline behavior.
- Perfmon state, counter values, pending-status bits, lock-status bits, MPCC idle/busy/disabled bits, OGAM current-mode/current-select fields, CRC results, and memory-power states are volatile hardware readbacks.
- Interrupt status/ack fields in perfmon blocks are latched hardware event state. ACK fields are side-effecting write paths, not ordinary persistent configuration.
- LUT index/data/control registers are an indexed hardware access window. Correct behavior depends on setting index, color mask/read select, host/config mode, and data in the expected sequence.

Correct sequencing is imposed by hardware and the functional driver code, not by these macros. Driver paths must still hold appropriate update locks, avoid changing active compositor/gamma state at unsafe times, respect clock/reset/power ordering, program LUT/region data before enabling a mode that consumes it, and acknowledge perfmon interrupts without losing pending events.

## Dependencies And Integration Points

This chunk integrates with:

- The matching DCN 3.1.2 register offset/address headers for the same `dcn_3_1_2` ASIC register namespace.
- AMDGPU Display Core register tables and access helpers that map register names to instance-specific offsets and pair them with these shift/mask names.
- MPC/MPCC resource code that builds compositor trees, maps DPP inputs to MPCC top/bottom slots, routes MPCC output to OPP instances, controls blend/alpha/gain behavior, and checks MPCC busy/idle state.
- Atomic modeset and plane update paths that use MPCC update locks, MPC pending-status readbacks, and vupdate-lock set registers to coordinate surface/config/cursor updates.
- Color-management paths that program MPCC output gamma LUTs, PWL RAM A/B region descriptors, per-channel offsets, and gamut-remap matrices.
- CRC/debug code that enables MPC CRC capture, selects DPP/OPP/DWB sources, reads AR/GB/C result registers, and masks/locks CRC updates.
- Perfmon/debug tooling that configures `DC_PERFMON14` and `DC_PERFMON15`, selects events, controls start/stop/count-off behavior, reads low/high counter values, and services counter interrupts.
- Clock/reset/power-management paths that toggle MPC clock gating, soft reset, and MPCC OGAM memory power state.
- Display writeback paths using `MPC_DWB0_MUX` and pending status for DWB0 integration.

Because this is a generated preprocessor interface, name consistency is as important as numeric correctness. Missing or renamed macros fail at compile time where referenced; stale shifts or masks can compile cleanly and cause MMIO writes to the wrong bits.

## Risks And Maintenance Notes

- The main correctness risk is drift from the ASIC register specification. A wrong shift or mask can misprogram compositor routing, blending, color transforms, CRC, perfmon, reset, or power state.
- The range is heavily repetitive across MPCC0-3 and MPCC_OGAM0-3. Prefix mistakes can target the wrong compositor slice or gamma block while leaving code structurally valid.
- The chunk starts mid-`DC_PERFMON14_PERFCOUNTER_STATE` and ends mid-`MPCC_OGAM3` RAM A region definitions. Adjacent chunks are needed for complete per-register/per-block coverage.
- ACK and clear-like perfmon bits are side-effecting. Generic read/modify/write code must avoid accidentally acknowledging pending counter interrupts.
- MPCC update locks and MPC vupdate locks are sequencing-sensitive. Misuse can create partially applied plane, cursor, or configuration updates and visible display glitches.
- OGAM LUT and region programming is indexed and banked. Incorrect index progression, RAM A/B selection, color channel selection, or current-vs-target mode handling can produce wrong gamma curves.
- Gamut-remap coefficient fields are packed as 16-bit halves. A shift/mask error or signed/unsigned interpretation mismatch can distort color conversion without causing a build failure.
- Memory-power and soft-reset fields can make subsequent register accesses unreliable if toggled while dependent blocks are active.
- Pending-status fields are diagnostic/readback signals, not locks by themselves. Driver code must still enforce the update ordering around them.
- Full-width and wide payload fields, such as perfmon low values, PWL values, offsets, and CRC masks/results, provide no C type-level range checking. Callers must validate field width and hardware-defined fixed-point formats.

## Test Signals

Useful validation signals for this chunk are mostly compile-time generated-header checks plus hardware/display behavior tests:

- Build AMDGPU with DCN 3.1.2 support and ensure all referenced generated macro names resolve.
- Run generated-header consistency checks that each field has matching `_SHIFT` and `_MASK` definitions, masks fit in 32 bits, and field masks do not overlap unexpectedly within a register.
- Exercise plane composition across MPCC0-3, including top/bottom input routing, OPP routing, blend modes, global alpha/gain, background color, and MPCC idle/busy/disabled readback.
- Run atomic plane, cursor, and config update tests that observe `MPC_DPP_PENDING_STATUS`, `MPC_PENDING_STATUS_MISC`, MPCC update-lock status, and vupdate-lock set behavior.
- Program output gamma on MPCC_OGAM0-2 and the covered MPCC_OGAM3 RAM A portion, verifying LUT index/data access, RAM A/B region programming, offsets, segment counts, and current mode/select readbacks.
- Exercise gamut-remap enable/disable and coefficient-bank programming for MPCC_OGAM0-2, checking color accuracy or CRC output before and after matrix updates.
- Use display CRC diagnostics to configure MPC CRC source selection, update locking, one-shot/continuous modes, and read AR/GB/C result registers.
- Configure `DC_PERFMON14` and `DC_PERFMON15`, select events, start and stop counters, read high/low values, trigger counter interrupts, and verify status/ack bits clear without corrupting counter state.
- Test clock/reset/power transitions around suspend/resume, modeset, blank/unblank, and runtime power management, with attention to MPC soft reset and MPCC OGAM memory power fields.
- Validate DWB0 mux selection/status and DWB pending-state behavior when display writeback is enabled.

## Chunk-Specific Summary

Lines 22458-24978 define a dense generated DCN 3.1.2 MPC/MPCC register-field surface rather than executable code. The most important responsibilities in this slice are compositor routing/blending for MPCC0-3, MPC reset/CRC/pending/vupdate-lock controls, two perfmon register blocks, output-gamma LUT/PWL programming, and gamut-remap coefficient programming. Correctness depends on exact generated mask/shift values, instance-correct prefixes, and successful hardware behavior under modeset, atomic update, color-management, CRC, perfmon, reset, power-management, and display-writeback workloads.

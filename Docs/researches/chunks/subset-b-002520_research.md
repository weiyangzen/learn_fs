# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 40148-41664

## Scope

This chunk is the tail of a generated AMD GC 11.0.0 shift/mask register header. It contains only C preprocessor constants for register bit positions and masks, plus generated register/address-block comments. There are no functions, structs, enums, global variables, allocations, locks, loops, branches, or direct MMIO operations in this range.

The requested lines contain 1,251 `#define` statements: 618 `__SHIFT` macros and 633 `_MASK` macros. The chunk starts in the middle of the `HW_LUT_UPDATE_STATUS` register, covers the full `secacind` and `grtavfsind` address blocks visible here, enters the `sqind` address block, and ends at the header guard `#endif` after `SQ_WAVE_EXEC_HI`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata. It is unrelated to Ceph filesystem protocol, persistence, or distributed-storage behavior.

## Purpose

`gc_11_0_0_sh_mask.h` describes the bit layout of AMD Graphics Core 11.0.0 registers. Driver code combines these macros with matching register offsets from `gc_11_0_0_offset.h` and AMDGPU helper macros to construct, update, and decode 32-bit hardware register values without open-coded bit positions.

This chunk covers three broad hardware surfaces:

- Hardware LUT update status and shader-engine CAC selection/threshold fields.
- RTAVFS controls and status for adaptive voltage/frequency scaling, CPO/ripple-counter measurement, voltage-code PI control, power-state-monitor measurement, FSM timing, debug stops, retention save/restore, and override/readback paths.
- SQ indexed debug and wave-state registers used to inspect wave activity, wave execution mode/status, trap status, register/LDS allocation, instruction-buffer counters, program counter, scratch state, hardware identity, scheduling mode, temporary trap registers, M0, and EXEC masks.

## Important APIs, Types, And Macros

The generated macro namespace is the only interface:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- `// addressBlock: ...` comments mark generated register address spaces.
- `//<REGISTER>` comments mark generated register groups.

There are no callable APIs or C types here. Runtime users normally reach these constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indexed-register access helpers, and generation-specific GFX/KFD/power-management code that includes this header with the matching offset header.

Important register families in this chunk include:

- `HW_LUT_UPDATE_STATUS` fields for table 1 through table 5 completion, error, and error-step reporting. The chunk begins after the matching shift macros, so only masks are visible here.
- `SE_CAC_ID` and `SE_CAC_CNTL` in `secacind`, selecting CAC block/signal IDs and a 16-bit CAC threshold.
- `RTAVFS_REG0..4` zone start/stop counters for five AVFS zones, followed by `RTAVFS_REG5..14` zone enable bitmaps.
- `RTAVFS_REG15..18` voltage/frequency points, each splitting a frequency count and voltage code into 16-bit fields.
- `RTAVFS_REG19..24` guard-band and per-zone CPO average-divider controls, including final divider fields and reserved high bits.
- `RTAVFS_REG25..30` reserved and zone intercept registers.
- `RTAVFS_REG31..42` CPO clock divider and FSM timing counters for startup, idle, CPO reset/start/stop, ripple-counter start/done, final-result readiness, voltage-code readiness, target-voltage readiness, and wait-for-ack.
- `RTAVFS_REG43..48` PI-controller tuning: lookup-table `KP/KI` nibbles, binary-search and hardware-calibration selection, voltage-regulator enable/bleed/override controls, anti-windup, PI shift/error controls, PI min/max voltage-code bounds, loop iteration count, and error threshold.
- `RTAVFS_REG49..53` PSM controls and readbacks for VDD and VREG min/max and average measurement paths.
- `RTAVFS_REG54..117` CPO0 through CPO63 start/stop counters.
- `RTAVFS_REG118..120` CPO enable bitmaps and CPO average-divider controls.
- `RTAVFS_REG121` AVFS zone-in-use bits and a high-nibble error code.
- `RTAVFS_REG122..185` CPO0 through CPO63 ripple-count readbacks.
- `RTAVFS_REG186..187` target/current frequency-count overrides and override-select bits.
- `RTAVFS_REG188..194` reserved bits, PI/binary-search voltage-code readback, regulator status, RLC request ignore, ripple-counter output select, run-loop control, CPO weight save/restore, retention reset, FSM debug stop points, scaled/final CPO counts, FSM state, and full-width ripple-count read.
- `SQ_DEBUG_STS_LOCAL` and `SQ_DEBUG_CTRL_LOCAL` for SQ local busy state, wave level, sub-block busy flags, and a small debug-control payload.
- `SQ_WAVE_ACTIVE` and `SQ_WAVE_VALID_AND_IDLE` wave-slot bitmaps.
- `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, and `SQ_WAVE_TRAPSTS`, which expose wave floating-point mode, exception enables, trap-after-instruction behavior, wave end, FP16 overflow, performance disable, scalar condition code, priority, privilege, trap/thread-trace flags, export/exec/VCC zero state, barrier/thread-group state, halt/trap/valid/ECC/fatal/idle/scratch state, exception vectors, save-context, illegal instruction, out-of-bounds buffer, host trap, wave start/end, performance snapshot, and UTC error fields.
- `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, and `SQ_WAVE_IB_STS` for VGPR allocation, LDS/shared-VGPR allocation, and outstanding export/LGKM/VM/VS counters.
- `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_IB_DBG1`, `SQ_WAVE_FLUSH_IB`, `SQ_WAVE_FLAT_SCRATCH_LO/HI`, `SQ_WAVE_HW_ID1/2`, `SQ_WAVE_POPS_PACKER`, `SQ_WAVE_SCHED_MODE`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_SHADER_CYCLES`, `SQ_WAVE_TTMP0/1/3..15`, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI`.

## Control Flow

This header has no runtime control flow. It influences behavior only when compiled C code expands these constants while preparing or decoding register values.

The implied driver flow is:

1. A GC 11.0.0 consumer selects a register offset from the matching offset header.
2. It reads, writes, or read-modify-writes the register through SOC15/MMIO or indexed-register helpers.
3. It uses the `__SHIFT` and `_MASK` pair, often via `REG_SET_FIELD` or `REG_GET_FIELD`, to isolate or compose the target field.
4. GPU hardware, firmware, RLC/SMU/power-management logic, or SQ debug machinery performs the actual operation.

For RTAVFS, higher-level control paths configure zones, CPO enable masks, divider values, voltage/frequency points, PI-loop parameters, PSM measurement paths, overrides, and run/debug controls. Hardware state machines then update in-use/error/status fields and CPO/ripple-count readbacks. This header does not encode sequencing rules, stabilization delays, RLC ownership, SMU coordination, or register side effects.

For SQ wave inspection, debug code selects indexed SQ state and reads wave activity, mode/status/trap state, allocation counters, PC, scratch pointers, hardware IDs, temporary trap registers, M0, and EXEC masks. This chunk defines the decode layout but not how waves are selected, halted, flushed, resumed, or synchronized with traps and thread tracing.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent or volatile state exists only in GPU registers, indexed SQ state, firmware-managed control state, and hardware latches/counters.

RTAVFS-related hardware state includes zone start/stop counters, zone enable masks, voltage/frequency points, guard bands, CPO average dividers, FSM timing counters, PI coefficients and bounds, regulator/override enables, PSM measurement state, CPO start/stop windows, CPO enable bitmaps, ripple-count readbacks, error codes, target/current frequency overrides, control bits for running the loop and saving/restoring CPO weights, retention reset, debug stop points, FSM state, and final/scaled CPO count outputs. Some fields are configuration values, some are live status bits, and some are hardware-updated counters or readbacks.

SQ-related hardware state includes local busy indicators, active/idle wave-slot masks, per-wave mode/status/trap state, VGPR/LDS allocation, outstanding instruction-buffer counters, PC, flat scratch address, wave hardware identity, scheduling and POPS state, shader-cycle count, TTMP scratch registers, M0, and EXEC masks. These values are per-wave or per-SQ debug state and can change while shader execution is active.

This generated header does not identify reset values, write-one-to-clear fields, clear-on-read behavior, read-only versus writeable fields, locking requirements, power-gating persistence, or firmware ownership. Consumers must preserve reserved bits during read-modify-write unless hardware documentation or existing AMDGPU sequences explicitly say otherwise.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h` supplies matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h` supplies generated defaults where available.
- AMDGPU helper macros and SOC15 indexed/MMIO accessors provide the actual bitfield and register operations.
- GFX 11, KFD, RLC, debug, power-management, and SMU-adjacent code are the likely runtime consumers for these register layouts.
- Neighboring GC generation headers expose similar families, but field widths and positions are generation-specific and should not be assumed interchangeable.

Important integration surfaces are GPU power/voltage management, AVFS tuning and diagnostics, CPO/ripple-counter calibration, RLC/firmware interactions around AVFS ownership, GPU hang/debug tooling, wave trap handling, shader debugger support, thread tracing, register-dump decoding, and postmortem analysis of wave allocation/status.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong mask or shift can compile cleanly while reading or programming the wrong hardware bit.
- The chunk starts mid-register: `HW_LUT_UPDATE_STATUS` shift definitions and earlier table-zero context are in a previous chunk.
- RTAVFS has many repeated register families. Off-by-one mistakes across `RTAVFS_REG54..117` CPO start/stop counters or `RTAVFS_REG122..185` ripple counters would target the wrong CPO instance while looking mechanically valid.
- Several RTAVFS fields are control-sensitive: voltage overrides, regulator enables, low-power mode, PI disable/anti-windup, binary-search selection, run-loop, RLC request ignore, CPO weight save/restore, and retention reset. Misuse can destabilize clocks/voltage or break power-management handoff.
- Reserved masks are frequent. Full-register writes that do not preserve reserved fields can corrupt undocumented hardware state.
- Status/readback fields may be sampled while hardware is changing. Debug and diagnostics should account for transient in-use, busy, FSM, ripple-count, and wave-status values.
- SQ wave fields are highly execution-sensitive. Reading active wave status without proper halt/selection/synchronization can produce inconsistent PC, EXEC, trap, allocation, and counter values.
- Wave trap and exception fields overlap debugger, KFD, user-mode queue, thread-trace, and fault-reporting behavior. Incorrect decoding can misattribute illegal instructions, buffer out-of-bounds events, host traps, save-context events, UTC errors, or fatal halt conditions.
- `SQ_WAVE_TTMP2` is absent from the visible TTMP sequence, so consumers must not assume contiguous macros exist for every TTMP index in this chunk.
- The file ends at `#endif`; later chunk merging should treat this as the terminal chunk for this header, not a partial continuation.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware-level integration:

- Build AMDGPU/KFD configurations that include GC 11.0.0 support. Missing or malformed macros should surface as compile failures in GFX 11, KFD, debug, or power-management code.
- Compare every visible shift and mask against AMD's authoritative GC 11.0.0 register database.
- Cross-check that visible register groups have matching entries in `gc_11_0_0_offset.h` and, where applicable, `gc_11_0_0_default.h`.
- Run mechanical mask checks: masks should align with shifts, full-width data/readback fields should use `0xFFFFFFFFL`, 16-bit paired counters should split at bit 16, repeated CPO/ripple families should be structurally consistent, and reserved fields should not overlap named fields.
- Exercise AVFS/power-management flows on affected hardware: clock/voltage changes, low-power transitions, SMU/RLC handoff, CPO calibration, ripple-counter reads, override paths, retention save/restore, and debug stop/run-loop behavior.
- Inspect runtime logs and register dumps for `RTAVFS_REG121` error codes, FSM state, zone-in-use bits, target/current frequency override behavior, PSM min/max/average readbacks, and CPO/ripple counter plausibility.
- Exercise shader debugging and hang-diagnosis paths that read SQ wave active/idle masks, mode/status/trap state, allocation, PC, scratch, hardware ID, TTMP, M0, and EXEC registers.
- Validate trap and exception reporting with workloads that trigger illegal instruction, buffer out-of-bounds, host trap, save-context, performance snapshot, wave start/end, and UTC error paths where supported.
- Decode known-good GC 11.0.0 register dumps using these masks and compare against reference tools, especially for RTAVFS repeated arrays and SQ wave state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002520`. The final per-file research should merge it with neighboring chunks for complete `gc_11_0_0_sh_mask.h` coverage. The previous chunk owns the beginning of `HW_LUT_UPDATE_STATUS`; this chunk owns the terminal `secacind`, `grtavfsind`, and `sqind` tail through the header guard.

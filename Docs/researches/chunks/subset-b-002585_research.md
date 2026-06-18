# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 40042-40550

## Scope

This chunk is the final segment of the generated AMD GC 12.0.0 shift/mask register header. It contains preprocessor constants only. Each hardware field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no C functions, structs, enums, storage definitions, includes, locks, allocations, callbacks, or executable branches in this range.

The selected lines begin in the middle of `RTAVFS_REG188`, then cover `RTAVFS_REG189` through `RTAVFS_REG194`, the `dbgu_gfx_ports_blk` `PACKER_CONTROL` register, the `gfx_se_sqind` shader-queue indirect register fields for local debug and wave state, and the final `gfx_se_secacind` SE CAC indirect fields. The chunk ends with the file-level `#endif`.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. AMDGPU code combines these masks with addresses from the companion `gc_12_0_0_offset.h` header and with register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15`. This lets the driver pack, update, and decode individual hardware fields without embedding raw bit positions throughout engine setup, debug, reset, power, and wave-inspection code.

This specific chunk focuses on late debug and shader-engine metadata:

- RTAVFS control/status fields for debug-bus selection, voltage-code readback, VDD state, loop control, retention save/restore, FSM stop points, scaled/final CPO count reporting, FSM state, and ripple-counter readback.
- A 64-bit debug packer control register with presence, enable, stream ID, and reserved fields.
- Shader queue local status and control fields, including wave occupancy and busy bits for SQ, instruction-side, instruction buffer, arbiter, export, barrier-message, and VM activity.
- Per-wave execution state, including active/valid/idle slots, floating-point mode, scalar prefetch/performance flags, status bits, private wave state, GPR/LDS allocation, instruction-buffer counters, performance snapshot fields, exception flags, trap controls, scratch base, hardware ID, scheduling mode, shader cycle count, DVGPR allocation, PC, TTMP registers, `M0`, and `EXEC`.
- Shader-engine CAC selector/control fields for choosing a CAC block/signal and threshold.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the register value.
- Address symbols for the same registers are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h`, commonly as `ix...`, `mm...`, or `reg...` symbols depending on address space.
- AMDGPU callers usually consume these constants through register field helpers, direct MMIO helpers, SQ indirect read helpers, debugfs wave dump code, context save/restore paths, or command-packet construction.

The main macro families in this chunk are:

- `RTAVFS_REG188`: debug-bus enable and selection, using `RTAVFSRTAVFSDBGBUSEN`, `RTAVFSRTAVFSDBGBUSSELREG`, `RTAVFSUSEDBGBUSSELFROMREG`, `RTAVFSRTAVFSDBGSTREAMVALIDSEL`, `RTAVFSRTAVFSDBGSTREAMCLKDIV`, and `RTAVFSRTAVFSDBGSTREAMFSMBITSEL`.
- `RTAVFS_REG189`: AVFS voltage-code and VDD readback fields, including `RTAVFSVOLTCODEFROMPI`, `RTAVFSVOLTCODEFROMBINARYSEARCH`, `RTAVFSVDDREGON`, and `RTAVFSVDDABOVEVDDRET`.
- `RTAVFS_REG190`: AVFS loop and retention controls, including ignore-RLC request, ripple-counter output select, run loop, save/restore CPO weights, and reset retention registers.
- `RTAVFS_REG191`: stop-at-debug controls for AVFS FSM checkpoints such as startup, idle, reset CPO/ripple counters, start CPOs, start ripple counters, ripple counters done, final CPO result ready, voltage code ready, target voltage ready, stop CPOs, and wait for ACK.
- `RTAVFS_REG192` through `RTAVFS_REG194`: AVFS scaled/final CPO counts, FSM state, and 32-bit ripple-counter readback.
- `PACKER_CONTROL`: a 64-bit debug packer register with `PackerPresent`, `PackerEnable`, `StreamID`, and reserved-bit masks. Its mask constants use 64-bit-looking values, including `0xFFFFFFFFFFFFFF00L`.
- `SQ_DEBUG_STS_LOCAL` and `SQ_DEBUG_CTRL_LOCAL`: local SQ busy/wave-level status and a simple 8-bit unused control field.
- `SQ_WAVE_ACTIVE` and `SQ_WAVE_VALID_AND_IDLE`: 20-bit wave-slot bitmaps.
- `SQ_WAVE_MODE`: floating-point round/denorm mode plus `FP16_OVFL`, `SCALAR_PREFETCH_EN`, and `DISABLE_PERF`.
- `SQ_WAVE_STATUS`: per-wave status flags for privilege, trap enable, export readiness, `EXECZ`, `VCCZ`, in-workgroup, trap and trap-barrier state, valid/idle status, skip export, fatal halt, VGPR availability, LDS parameter readiness, GS/export obligations, wave64, DVGPR enable, and WGP takeover.
- `SQ_WAVE_STATE_PRIV`: private scheduler/debug state such as workgroup round-robin, sleep/wakeup, barrier completion, named barrier ID, `SCC`, priority, halt, poison error, conditional debug, scratch enable, performance enable, and thread trace enable.
- `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_DVGPR_ALLOC_LO`, and `SQ_WAVE_DVGPR_ALLOC_HI`: VGPR/LDS/DVGPR allocation packing.
- `SQ_WAVE_IB_STS`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_IB_DBG1`, and `SQ_WAVE_FLUSH_IB`: outstanding instruction-buffer and memory/export counter fields, forward progress, SPI thread-trace enable, idle/debug counters, and a full-width flush register.
- `SQ_PERF_SNAPSHOT_DATA`, `SQ_PERF_SNAPSHOT_DATA1`, `SQ_PERF_SNAPSHOT_DATA2`, `SQ_PERF_SNAPSHOT_PC_LO`, and `SQ_PERF_SNAPSHOT_PC_HI`: wave performance snapshot validity, issue/no-issue state, PC, wave count, issued/stalled arbiter states, and operation counters.
- `SQ_WAVE_EXCP_FLAG_PRIV`, `SQ_WAVE_EXCP_FLAG_USER`, and `SQ_WAVE_TRAP_CTRL`: privileged and user exception causes plus trap enable controls for ALU exceptions, address watch, wave end, trap-after-instruction, memory violation, context save, illegal instruction, host trap, XNACK error, and first memory-violation source.
- `SQ_WAVE_SCRATCH_BASE_LO` and `SQ_WAVE_SCRATCH_BASE_HI`: full 32-bit scratch base pieces.
- `SQ_WAVE_HW_ID1` and `SQ_WAVE_HW_ID2`: wave identity, SIMD/WGP/SA/SE placement, DP rate, queue/pipe/ME/state/workgroup/VM IDs.
- `SQ_WAVE_SCHED_MODE`, `SQ_SHADER_CYCLES_LO`, `SQ_SHADER_CYCLES_HI`, `SQ_WAVE_PC_LO`, `SQ_WAVE_PC_HI`, `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`, `SQ_WAVE_M0`, `SQ_WAVE_EXEC_LO`, and `SQ_WAVE_EXEC_HI`: scheduler mode, shader cycle counter, program counter, trap temporary registers, `M0`, and execution mask fields.
- `SE_CAC_ID` and `SE_CAC_CNTL`: CAC block/signal selection and 16-bit threshold.

## Control Flow

The header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied AMDGPU runtime flow is:

1. Select the GC 12.0.0 register headers for a matching ASIC.
2. Use the companion offset header to find the address or indirect index for a register.
3. Read a current register value, compose a new value, or collect a debug/status dump.
4. Use the `__SHIFT` and `__MASK` pair, either directly or through field helper macros, to pack or extract the field.
5. Submit the final value through MMIO, SQ indirect access, a command processor packet, debugfs readback, firmware interface, or a context save/restore table.

Concrete integration in this tree appears in `gfx_v12_0_read_wave_data()`: it selects SQ indirect addresses such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_HW_ID1`, `ixSQ_WAVE_HW_ID2`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_STS2`, `ixSQ_WAVE_IB_DBG1`, `ixSQ_WAVE_M0`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATE_PRIV`, `ixSQ_WAVE_EXCP_FLAG_PRIV`, `ixSQ_WAVE_EXCP_FLAG_USER`, `ixSQ_WAVE_TRAP_CTRL`, `ixSQ_WAVE_ACTIVE`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_DVGPR_ALLOC_LO`, `ixSQ_WAVE_DVGPR_ALLOC_HI`, and `ixSQ_WAVE_SCHED_MODE`. `amdgpu_debugfs_wave_read()` then exposes this GFX-version-specific wave status stream through debugfs after selecting the target SE/SH/CU/WGP/SIMD/wave.

The RTAVFS, packer, and SE CAC fields do not create control flow in this header. Their control-flow semantics are hardware-defined: writes can enable a debug bus, force AVFS debug stop points, start/stop loops, select counters, or change capture thresholds, while reads can observe volatile hardware state.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware register fields whose values are owned by GPU hardware, firmware, and AMDGPU runtime programming.

RTAVFS fields are power/voltage/frequency state and debug control. Voltage codes, VDD flags, FSM state, scaled CPO counts, final minimum CPO counts, and ripple-counter readback are volatile hardware observations. `RTAVFSRUNLOOP`, `RTAVFSSAVECPOWEIGHTS`, `RTAVFSRESTORECPOWEIGHTS`, and `RTAVFSRESETRETENTIONREGS` are active controls rather than passive state. The stop-at fields in `RTAVFS_REG191` can intentionally halt AVFS sequencing at internal milestones and should be treated as debug or bring-up controls.

`PACKER_CONTROL` configures a debug stream packer. Presence is likely read-only capability, while enable and stream ID affect debug stream routing. Reserved fields occupy most of the 64-bit value and should be preserved unless the authoritative hardware sequence says otherwise.

SQ wave registers describe live per-wave state. Active, valid/idle, status, mode, private state, allocation, outstanding-counter, exception, trap, PC, TTMP, M0, EXEC, cycle, and hardware-ID fields can change while waves execute, trap, halt, context-save, or retire. Reading them through SQ indirect access is a snapshot-like diagnostic operation, not persistent kernel state. The debugfs path protects selection with `adev->grbm_idx_mutex` and resets GRBM selection afterward, but the values remain race-prone with live GPU execution.

Exception and trap fields have both diagnostic and control implications. Privileged exception flags report causes such as address watch, memory violation, save-context, illegal instruction, host trap, wave start/end, performance snapshot, trap-after-instruction, and XNACK error. User exception flags report ALU and graphics/user events such as invalid operation, denorm input, divide by zero, overflow, underflow, inexact, integer divide by zero, buffer out-of-bounds, and LOD clamping. Trap-control bits determine which events can trap.

SE CAC fields configure or read counters in an indirect shader-engine counter block. `CAC_BLOCK_ID`, `CAC_SIGNAL_ID`, and `CAC_THRESHOLD` are small packed fields and likely depend on a block-specific selector protocol outside this header.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching addresses and indirect indices, including `ixRTAVFS_REG188` through `ixRTAVFS_REG194`, `ixPACKER_CONTROL`, `ixSQ_DEBUG_STS_LOCAL`, `ixSE_CAC_ID`, `ixSE_CAC_CNTL`, and the SQ wave indirect `ixSQ_WAVE_*` registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c` includes this header and uses the SQ indirect index macros in the GFX12 wave dump helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.c` exposes GFX wave state through debugfs and dispatches to the GFX-version-specific `read_wave_data` function.
- Other GC 12.0.0 include users in this tree include `soc24.c`, `sdma_v7_0.c`, `mes_v12_0.c`, `gfxhub_v12_0.c`, `imu_v12_0.c`, and `amdgpu_amdkfd_gfx_v12.c`; they rely on the same generated shift/mask contract for ASIC-specific register access even if not every field in this chunk is referenced directly.
- AMDGPU field helpers and SOC15 MMIO macros are the main consumers for packing/extracting these values.

Integration points are mostly diagnostics, debug, power, and shader-engine inspection:

- AVFS/power-management debug or firmware-facing sequences can use RTAVFS fields to observe voltage/frequency loop internals and retention behavior.
- Debug bus and packer controls feed hardware debug streaming.
- SQ wave readback supports debugfs, hang diagnostics, wave-state dumps, KFD/compute debugging, trap analysis, and low-level scheduler/occupancy inspection.
- Exception and trap masks tie into shader trap handling, memory fault diagnosis, user exception visibility, and context save/restore behavior.
- Cycle counters, performance snapshots, IB counters, and busy bits support performance diagnostics and hang triage.
- SE CAC selector/threshold fields support shader-engine activity or counter-threshold instrumentation.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can decode the wrong wave-state bit or program the wrong control bit.
- This chunk begins mid-register at `RTAVFS_REG188`; the first three shift macros for that register are in the previous chunk. File-level research must merge adjacent chunks before drawing complete conclusions about `RTAVFS_REG188`.
- `PACKER_CONTROL` uses masks wider than 32 bits. Callers must avoid truncating its reserved or stream fields through 32-bit-only helper assumptions when accessing the underlying register is truly 64-bit.
- RTAVFS controls are not ordinary status fields. Misprogramming run-loop, save/restore CPO weights, retention reset, ignore-RLC request, or stop-at bits can perturb voltage/frequency management and cause hangs, incorrect frequency decisions, or misleading power telemetry.
- SQ indirect wave state is volatile. Debugfs or hang-dump readers can observe partial progress, retired waves, or state that changes between consecutive indirect reads. Tests should not assume all fields form an atomic snapshot unless the surrounding hardware sequence freezes execution.
- `SQ_WAVE_STATUS` in GC 12.0.0 differs from older generations. For example, this layout has `IN_WG`, `OREO_CONFLICT`, `NO_VGPRS`, `LDS_PARAM_READY`, `MUST_GS_ALLOC`, `IDLE`, `WAVE64`, `DVGPR_EN`, and `WGP_TAKEOVER`, while older headers use other status names such as `HALT`, `ECC_ERR`, `ALLOW_REPLAY`, or `IN_TG`. Cross-generation debug decoders must use the correct ASIC layout.
- Exception and trap fields are security and correctness sensitive. Enabling or mis-decoding address watch, memory violation, host trap, save-context, XNACK, buffer OOB, or trap-after-instruction bits can confuse trap handlers or hide real faults.
- Allocation fields have compact widths. VGPR base/size, LDS base/size, VGPR shared size, and DVGPR segment fields must be interpreted in hardware units, not raw byte counts, unless a caller explicitly converts units.
- Split fields such as PC low/high, scratch base low/high, shader cycles low/high, and EXEC low/high need correct composition and ordering in debug decoders. A high/low mismatch can point to an impossible PC or execution mask.
- Reserved and `UNUSED` masks document occupied bits, but do not make those bits safe to set. Read-modify-write code should preserve reserved fields unless a documented sequence requires otherwise.
- SE CAC block and signal IDs are selector-dependent. A valid field encoding can still select an unsupported or meaningless signal on a particular ASIC stepping.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GFX12, MES, KFD, GFXHUB, IMU, SDMA, and SOC initialization paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 40042-40550.
- Cross-checks that all registers in this chunk have matching address or indirect-index macros in `gc_12_0_0_offset.h`.
- Static sanity checks that masks align with shifts, full-width data fields use `0xFFFFFFFFL`, `SQ_SHADER_CYCLES_HI` is limited to `0x0FFFFFFF`, 20-bit wave-slot masks stay at `0x000FFFFF`, and the DVGPR segment masks remain structurally consistent across segments 0-7.
- GFX12 debugfs wave-read tests that access `/sys/kernel/debug/dri/.../amdgpu_wave` or equivalent debugfs paths and verify the type-4 wave-data layout can be read without invalid GRBM selection or runtime-power failures.
- Hang-dump or shader-debug tests that decode `SQ_WAVE_STATUS`, PC, EXEC, HW IDs, allocation registers, exception flags, trap controls, and mode/private-state fields on a known workload.
- Trap and exception workloads that trigger representative ALU exceptions, buffer OOB, address-watch, host trap, save-context, wave-start/wave-end, and XNACK paths where hardware and firmware support them.
- Power/AVFS bring-up diagnostics that read RTAVFS voltage code, VDD state, CPO count, FSM state, and ripple-counter fields under controlled clock/voltage conditions.
- Debug-stream tests that validate packer presence/enable/stream-ID behavior without disturbing reserved bits.
- SE CAC tests that select known CAC block/signal IDs and confirm threshold programming or readback follows the hardware specification.
- Runtime warning signals include GFX12 wave dumps with impossible IDs or masks, broken debugfs reads, GPU hangs during wave/trap inspection, inconsistent power/AVFS telemetry, corrupted performance snapshots, or debug stream data loss after packer/control changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002585`. It covers lines 40042-40550 of `gc_12_0_0_sh_mask.h`, the tail of the file. The final per-file research should merge it with the previous chunk for the beginning of `RTAVFS_REG188` and with earlier chunks that define the rest of the GC 12.0.0 register map.

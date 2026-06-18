# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 7500-9967

## Scope

This chunk is a generated AMD GC 11.5.0 register-offset header slice. It contains C preprocessor constants only: register offset macros, matching `_BASE_IDX` macros, and generated comments that split the register namespace into address blocks. There are no functions, structs, enums, runtime branches, allocations, locks, or direct MMIO operations in this range.

The requested lines contain 2,404 `#define` statements: 2,083 `reg...` macros for directly addressed registers, 321 `ix...` macros for indexed address spaces, and 1,042 `_BASE_IDX` macros. The chunk starts in the middle of the GC performance-counter offset table at `regTCP_PERFCOUNTER1_LO_BASE_IDX`, covers multiple performance-select and control address blocks, and ends inside the `sqind` indexed shader-queue debug register group at `ixSQ_WAVE_LDS_ALLOC`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_11_5_0_offset.h` maps symbolic GC 11.5.0 register names to hardware register offsets. Driver code pairs these constants with generated bitfield definitions from companion shift/mask headers and uses SOC15/MMIO helper macros to access the right register for this ASIC generation.

This chunk covers late graphics-core performance monitoring and control surfaces:

- Performance counter data and selector registers for texture, cache, shader, geometry, color/depth, command processor, RLC, rasterization, primitive assembly, global data share, and UTCL1 blocks.
- GRTAVFS and RTAVFS target frequency/voltage, soft reset, clock, power-state, and indirect register windows.
- CP hypervisor-facing microcode and instruction/data cache base, bound, and control registers for PFP, ME, MEC, CPC, MES, and RS64 surfaces.
- RLC control/status, timers, interrupts, clock counts, doorbells, power-gating, safe-mode, microcontroller, save/restore, SPM, residency, interrupt-handler client, IMU boot, and SMU mailbox registers.
- Power decoder clock-gating and clock-control registers across shader, geometry, rasterization, cache, command processor, RLC, GDS, DB, CB, and UTCL1 units.
- Hypervisor, PSP, and GFX IMU mailboxes, scratch registers, interrupt controls, reset/power state, DPM, firmware timestamp, RAM windows, and security/access-control surfaces.
- Indexed CAC, RTAVFS, and SQ debug/wave register offsets.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace:

- `reg<NAME>` expands to the register offset used by AMDGPU register access helpers.
- `reg<NAME>_BASE_IDX` expands to a base-index selector, almost always `1` in this chunk, used by SOC15-style helpers to choose the MMIO base aperture.
- `ix<NAME>` expands to an index within an indirect register space rather than a normal direct MMIO offset.
- `// addressBlock: ...` and `// base address: ...` comments identify generated address-map regions.

Important direct-address macro families include:

- Performance counter data registers before `gc_perfsdec`: `TCP`, `GL2C`, `GL2A`, `GL1C`, `CHC`, `CB`, `DB`, `RLC`, `RMI`, `GCR`, `PA_PH`, `UTCL1`, `GL1A`, `GL1H`, `CHA`, `GDS`, `GE1`, `GE2`, `SPI`, `SQ`, `SQG`, `SX`, `GCEA`, `PC`, `PA_SC`, `PA_SU`, `GRBM`, `CPG`, `CPF`, and `CPC` `PERFCOUNTER*_LO/HI`, filter, and control registers.
- `gc_perfsdec` selector registers such as `*_PERFCOUNTER*_SELECT`, `*_SELECT1`, and `*_PERFCOUNTER*_CNTR` for the same broad graphics and cache blocks. These choose events for the counter data registers.
- `gc_grtavfs_grtavfs_dec` and `gc_grtavfsdec` macros for `GRTAVFS_RTAVFS_REG_ADDR`, write/read data, general, control/status, target frequency/voltage, soft reset, PSM, and clock control.
- `gc_cphypdec` CP microcode and cache registers including `CP_HYP_PFP_UCODE_*`, aliases such as `CP_PFP_UCODE_*`, ME RAM address/data aliases, `CP_HYP_ME_*`, `CP_HYP_MEC1/2_*`, `CP_PFP_IC_*`, `CP_ME_IC_*`, `CP_CPC_IC_*`, `CP_MES_IC_*`, `CP_MES_MI/MD*`, `CP_GFX_RS64_*`, and `CP_MEC_MI/MD*`.
- `gc_rlcdec` macros for `RLC_CNTL`, firmware version/status, reference and GPU clock timestamps, GPM timers and interrupts, microcode control, RLCG doorbells, power-gating controls and status, SRM index/control windows, save/restore lists, SPM setup, performance monitor selection, safe-mode/SMU command mailbox registers, IMU bootload address/size, and RLC interrupt/debug surfaces.
- `gc_rlcsdec` and `gc_pfvfdec_rlc` macros for RLC GPM status, safe mode, SPM interrupt state, CSIB address/length, CP scheduler hooks, EOF interrupts, and spare interrupt registers.
- `gc_pwrdec` macros for `CGTS_TCC_DISABLE`, per-block `GFX_ICG_*`, `CGTT_*`, `ICG_*`, `GL1*/GL2*`, `GCEA`, `RMI`, `GCR`, `DB`, `CB`, `CP`, `RLC`, and `UTCL1` clock controls.
- `gc_hypdec` macros for pipe priority, GRBM save/restore select/data, SE/SA/WGP/RB remapping, SDMA status, RLC hypervisor semaphores, busy/clock controls, IH cookie state, runlist and save/restore control, CP/GFX command status, address-window controls, and user shader rate configuration.
- `gc_pspdec` macros for MES debug-message index/data and GRBM hypervisor CAM address/data windows.
- `gc_gfx_imu_gfx_imudec` and `gc_gfx_imu_gfx_imu_pspdec` macros for GFX IMU C2P message registers, access controls, interrupt controls/status, RLC command/data/status mailboxes, scratch registers, firmware timestamps, GTS offsets, PIC/IH controls, doorbell control, DPM counters, RAM address/data windows, reset/power-good state, and IMU instruction/data RAM windows.

Important indexed macro families include:

- `gccacind`: `ixGC_CAC_ID`, `ixGC_CAC_CNTL`, `ixGC_CAC_STATUS`, multiple GC CAC weight/override/status registers, clock counter readouts, dynamic override/status registers, power/clock residency counters, accumulator controls, power-good/ready readouts, and LUT update status.
- `secacind`: `ixSE_CAC_ID` and `ixSE_CAC_CNTL`.
- `grtavfsind`: `ixRTAVFS_REG0` through `ixRTAVFS_REG194`, a dense RTAVFS indexed-register range.
- `sqind`: the first local SQ debug and wave state offsets in this chunk: `ixSQ_DEBUG_STS_LOCAL`, `ixSQ_DEBUG_CTRL_LOCAL`, `ixSQ_WAVE_ACTIVE`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_GPR_ALLOC`, and `ixSQ_WAVE_LDS_ALLOC`.

## Control Flow

This header has no executable control flow. It affects runtime behavior only through macro expansion in code that reads, writes, or read-modify-writes GC 11.5.0 registers.

The implied access flow is:

1. Driver code selects a symbolic register macro from this offset header.
2. For direct registers, AMDGPU SOC15/MMIO helpers combine the offset with the `_BASE_IDX` value and the GC instance to access the hardware aperture.
3. For indexed registers, driver code uses the corresponding indirect-index mechanism, such as an index/data window, and writes an `ix...` selector rather than a direct `reg...` offset.
4. Companion shift/mask definitions, where present, compose or decode bitfields at the chosen offset.
5. The actual sequencing is owned by higher-level AMDGPU components such as performance-counter setup, RLC/SMU/IMU initialization, CP firmware loading, clock-gating programming, reset, suspend/resume, and debug dump paths.

Performance monitoring usually programs event selector registers in `gc_perfsdec`, enables counting through the relevant control/filter registers, then samples low/high counter pairs from the earlier direct counter region. RLC, CP, IMU, PSP, and GRTAVFS paths often require ordered mailbox or index/data transactions, but this header records only numeric addresses and does not encode polling, acknowledgement, timeout, clear, or ownership rules.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists in GPU registers, firmware-owned SRAM/RAM windows, command processor state, RLC/IMU/SMU mailboxes, counter latches, doorbell capture registers, indexed CAC/RTAVFS/SQ spaces, and memory-backed save/restore areas.

State covered by this chunk includes:

- Performance counter selectors, filter controls, low/high counter data, and SPM/event-monitoring state.
- RLC firmware status, timers, interrupts, GPM state, power-gating controls, residency counters, safe-mode state, doorbell monitor data, IMU bootload metadata, and SMU command arguments/responses.
- CP firmware upload and instruction/data cache base/bound registers for multiple engines. Some entries are aliases at the same numeric offset, reflecting different consumer names for the same hardware window.
- Clock-gating and power control state for many graphics blocks. These settings persist until reprogrammed, reset, or power-management firmware changes them.
- Hypervisor and PSP-visible state such as GRBM save/restore windows, remap controls, semaphores, CAM windows, and user shader-rate configuration.
- GFX IMU firmware mailboxes, scratch space, interrupt controller state, DPM counters, reset/power-good bits, RAM windows, and IH gasket controls.
- Indexed CAC and RTAVFS telemetry/control state, plus local SQ wave/debug state for the selected shader context.

Some registers are configuration, some are live counters or status, some are firmware mailboxes, some are aliases, and some may be write-one-to-clear, self-clearing, or read-sensitive. This offset header does not encode access type or side-effect semantics; consumers must rely on the hardware register database and established driver sequences.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set staying synchronized:

- `gc_11_5_0_sh_mask.h` supplies matching field shifts and masks for registers that have named fields.
- `gc_11_5_0_default.h`, where present for this generation, supplies reset/default values for related registers.
- AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, `RREG32`, `WREG32`, `REG_SET_FIELD`, and indirect-register helper paths supply actual access behavior.
- Performance tooling and profiling paths rely on the counter and selector pairs remaining consistent.
- RLC, CP, PSP, SMU, IMU, reset, suspend/resume, power-management, clock-gating, GPU virtualization, SR-IOV, debugfs/register-dump, KFD, and hang-diagnosis paths can all consume these symbolic offsets.

The `reg..._BASE_IDX` values are part of the integration contract with SOC15-style address translation. The `ix...` values are part of a different contract: callers must route them through the proper indexed address block instead of treating them as ordinary MMIO offsets.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong offset or base index can compile cleanly while touching the wrong register.
- This chunk starts and ends mid-group. The previous chunk owns the beginning of the `TCP_PERFCOUNTER1` context, and the next chunk continues the `sqind` SQ wave/debug register table.
- Many performance counter families are repetitive but not interchangeable. Counter data, event selector, filter, and enable registers belong to different blocks and may have different widths, event encodings, and sampling rules.
- `_BASE_IDX` macros are mechanically paired with direct `reg...` macros. Missing or wrong base indices can break SOC15 register access even when the visible offset looks correct.
- `ix...` offsets have base address `0x0` in their generated blocks, but they are not normal direct MMIO offsets. Misrouting indexed CAC, RTAVFS, or SQ debug offsets through direct helpers can access unrelated hardware.
- Several CP and RLC macro names are aliases for the same numeric offsets, such as CP hypervisor and non-hypervisor microcode windows. Consumers must use the alias appropriate to the privilege and engine context.
- RLC, IMU, SMU, PSP, and GRTAVFS mailbox/register-window transactions are ordering- and timeout-sensitive. The offset table does not protect callers from missing a required poll, acknowledgement, mutex, safe-mode transition, or firmware ownership check.
- Clock-gating and power-control registers can destabilize active GPU blocks if modified outside the established bring-up, suspend/resume, or reset sequencing.
- Performance counters and residency counters may be split into low/high halves or latched by capture controls. Sampling without the expected latch order can produce torn values.
- Debug and wave-state indexed SQ registers are context-sensitive. Reads may depend on prior wave selection, debug halt state, shader engine selection, or GRBM indexing.
- Hypervisor, PSP, and security/access-control registers are isolation-sensitive. Incorrect offsets or access paths can break SR-IOV partitioning, firmware communication, or fault attribution.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include GC 11.5.0 support. Missing or renamed register macros should surface as compile failures in RLC, CP, power-management, debug, profiling, IMU, PSP, or KFD paths.
- Mechanically compare every offset and `_BASE_IDX` in this chunk against AMD's authoritative GC 11.5.0 register database.
- Check that each `reg...` macro has a matching `_BASE_IDX` macro and that direct-register names with fields also have corresponding shift/mask entries in `gc_11_5_0_sh_mask.h`.
- Validate that `ix...` macros are used only through indirect-index paths and not through direct SOC15 MMIO helpers.
- Exercise GPU performance counters and SPM sampling across TCP, cache, shader, geometry, DB/CB, RLC, UTCL1, and command processor blocks, checking selector-to-counter consistency and low/high sampling behavior.
- Exercise RLC initialization, safe mode, GPM timers/interrupts, RLCG/XT doorbells, power-gating transitions, residency counters, SMU mailbox commands, and IMU bootload handoff while monitoring for timeouts or stuck status bits.
- Exercise CP firmware loading and instruction/data cache base/bound setup for PFP, ME, MEC, CPC, MES, and RS64 paths where supported.
- Run suspend/resume, GPU reset, runtime power management, clock-gating enable/disable, SR-IOV or hypervisor paths, and PSP/IMU mailbox communication on GC 11.5.0 hardware.
- Decode register dumps with these offsets and compare against known-good dumps or vendor tooling, especially for RLC status, CP microcode windows, clock-gating controls, GFX IMU messages, CAC/RTAVFS indexed registers, and SQ wave debug state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002547`. The final per-file research should merge this with neighboring chunks for full `gc_11_5_0_offset.h` coverage. The previous chunk supplies the beginning of the performance-counter section, while the next chunk continues the `sqind` indexed SQ debug/wave register table after `ixSQ_WAVE_LDS_ALLOC`.

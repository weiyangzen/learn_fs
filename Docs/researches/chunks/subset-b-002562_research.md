# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 32528-35050

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains preprocessor constants only: hardware register fields are described as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for callers that need to pack or extract 32-bit register values.

The requested range contains 2,152 shift/mask `#define` entries. It begins in the middle of `GFX_ICG_GL2A_CTRL`: the earlier shift definitions for that register are in the previous chunk, while this chunk starts at `GFX_ICG_GL2A_CTRL__CLIENT15_OVERRIDE__SHIFT` and then carries all of the masks. It ends after `FIXED_PATTERN_PERF_COUNTER_7`; the next chunk continues with fixed-pattern counters 8-10 and LUT update status.

Although the file lives under a local `ceph-client` source mirror, this is AMDGPU DRM graphics-core metadata. It does not implement distributed filesystem or Ceph behavior.

## Purpose

`gc_11_5_0_sh_mask.h` supplies field layouts for GC 11.5.0 graphics hardware. Driver code pairs these field macros with register offsets from `gc_11_5_0_offset.h` and common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET`.

This chunk covers several large register families:

- Fine-grained and medium-grained clock-gating controls for CP, CPF, CPC, RLC, scan converter/PBB, GL2, TCP, UTCL1, CHC, LDS, CHA, GL1, GCR, RMI, GRBM, GCEA, and GC/SE CAC blocks.
- Hypervisor-visible GC registers in `gc_hypdec`, including graphics pipe priority, GRBM shader-array/instance indexing and remap controls, RLC SDMA busy/status, RLC hypervisor semaphores, RLC pace interrupt/cookie state, RLC/GPM/PACE microcode and scratch address/data windows, pipe steering, and user-visible shader-array/RB/TCC disable or redundancy configuration.
- PSP-facing GC debug and data-index windows in `gc_pspdec`, including MES, MEC, and GFX RS64 data-master index/data registers plus GRBM CAM and secure-control fields.
- GFX IMU host/RLC/SOC interface registers, including C2P mailboxes 0-47, mailbox access controls, power-management IRQ control, MP1/RLC mutexes, RLC command/data/status paths, SOC access request/address/data registers, VF control, scratch registers, timestamp/offset registers, PIC interrupt controller state, IH controls, clock/doorbell/RLC clock-gating/throttle controls, DPM counters, RLC RAM access, fence/control/status, reset/power-good status, and IMU instruction/data RAM windows.
- GC CAC indirect-register metadata in `gccacind`, including CAC identification/control, full-width accumulator counters for CP, EA, UTCL2 router/VML2/walker/ATCL2, GDS, GE, PMM, GL2C, PH, SDMA, CHC, and RLC blocks.
- Clock-state transition lookup tables and counters: release-to-stall, stall-to-release, stall-to-power-break, power-break-stall-to-release, power-break-release-to-stall LUT entries, and fixed-pattern performance counters 1-7.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or executable branches in this range. The API surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the register-value mask for that field.
- Matching register offsets are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`.
- Indirect CAC accumulator offsets use `ixGC_CAC_*` names in the offset header rather than direct `reg*` MMIO names.

Important field groups in this chunk include:

- `CGTT_CP_CLK_CTRL`, `CGTT_CPF_CLK_CTRL`, `CGTT_CPC_CLK_CTRL`, `CGTT_SC_CLK_CTRL3`, `CGTT_SC_CLK_CTRL4`, `GFX_ICG_*`, `GL1*`, `ICG_*`, and `GFX_ICG_UTCL1_CTRL`: clock-gating hysteresis, manual override, stall override, MGLS, and per-client/per-sub-block clock control fields.
- `GFX_PIPE_PRIORITY`, `GRBM_GFX_INDEX_SR_SELECT/DATA`, `GRBM_GFX_CNTL_SR_SELECT/DATA`, `GRBM_SE_REMAP_CNTL`, `GRBM_SA_REMAP_CNTL`, `GRBMH_WGP_REMAP_CNTL`, and `GRBMH_RB_REMAP_CNTL`: pipe priority, shader-array addressing, and physical-to-logical remap controls.
- `RLC_SDMA*_STATUS`, `RLC_SDMA*_BUSY_STATUS`, `RLC_HYP_SEMAPHORE_*`, `RLC_BUSY_CLK_CNTL`, `RLC_CLK_CNTL`, `RLC_PACE_*`, `RLC_IH_COOKIE*`, and RLC/GPM/PACE/RLCV/SRM address/data windows: RLC status, firmware windows, semaphore, interrupt-cookie, and pacing fields.
- `GL2_PIPE_STEER_*`, `GL1_PIPE_STEER`, `CH_PIPE_STEER`, `GC_USER_SHADER_ARRAY_CONFIG`, `GC_USER_PRIM_CONFIG`, `GC_USER_*_DISABLE`, `GC_USER_*_REDUNDANCY`, `CGTS_USER_TCC_DISABLE`, and `GC_USER_SHADER_RATE_CONFIG`: user-visible topology, disable, redundancy, and rate-configuration metadata.
- `CP_MES_DM_INDEX_*`, `CP_MEC_DM_INDEX_*`, `CP_GFX_RS64_DM_INDEX_*`, `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, `GRBM_SEC_CNTL`, and `GRBM*_CAM_*`: PSP/debug data windows and secure GRBM CAM access fields.
- `GFX_IMU_C2PMSG_*`, `GFX_IMU_MSG_FLAGS`, `GFX_IMU_*ACCESS_CTRL*`, `GFX_IMU_RLC_*`, `RLC_GFX_IMU_*`, `GFX_IMU_SOC_*`, `GFX_IMU_PIC_*`, `GFX_IMU_IH_*`, `GFX_IMU_DPM_*`, `GFX_IMU_RLC_RAM_*`, `GFX_IMU_CORE_CTRL`, `GFX_IMU_RESETn`, `GFX_IMU_GFX_RESET_CTRL`, `GFX_IMU_D_RAM_*`, and `GFX_IMU_I_RAM_*`: IMU mailbox, interrupt, firmware RAM, reset, DPM, and host/RLC/SOC handshake fields.
- `GC_CAC_ID`, `GC_CAC_CNTL`, and `GC_CAC_ACC_*`: CAC block identity/control and full-width 32-bit accumulator fields.
- `RELEASE_TO_STALL_LUT_*`, `STALL_TO_RELEASE_LUT_*`, `STALL_TO_PWRBRK_LUT_*`, `PWRBRK_*_LUT_*`, and `FIXED_PATTERN_PERF_COUNTER_*`: transition-pattern lookup-table fields and fixed-pattern performance counter fields.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select GC 11.5.0 register offsets and field definitions for an ASIC in the GC 11.5 family.
2. Build a register value with field masks/shifts, usually through `REG_SET_FIELD`, or decode a readback value with `REG_GET_FIELD`.
3. Access the target register through direct SOC15 MMIO helpers, indexed register windows, RLC-safe helpers, PSP/MES/MEC data-master windows, or indirect CAC index/data paths.
4. Use the value during graphics init, clock-gating setup, power-management handshakes, reset/recovery, topology enumeration, firmware mailbox exchange, virtualization/hypervisor operations, or diagnostics.

For clock-gating registers, higher-level code decides whether blocks should be auto-gated, forced on, stalled, or overridden; these macros only define the bit layout. For GRBM and pipe-steering registers, callers select shader engines, shader arrays, render backends, TCCs, or pipes before performing targeted programming or topology reporting. For IMU registers, code writes mailbox/request/status fields in a firmware-defined sequence; this chunk does not encode those wait loops or ordering rules. For GC CAC registers, software selects an indirect accumulator and reads or configures counter/control state through the CAC index/data aperture.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- Clock-gating and ICG/CGTT override fields persist in hardware registers until changed by driver init, power-management code, firmware, reset, suspend/resume restore, or ASIC reinitialization.
- GRBM index, remap, topology, and pipe-steering fields affect which shader-engine, shader-array, workgroup-processor, render-backend, cache, or pipe instances subsequent accesses target. Some fields are global broadcast selectors; others are per-topology configuration state.
- RLC status, busy, pace, cookie, semaphore, microcode, scratch, and RAM-window fields represent firmware-visible state. Address/data windows are stateful selectors, so incorrect sequencing can read or write the wrong internal RAM or scratch location.
- PSP, MES, MEC, and GFX RS64 data-master index/data windows are mailbox-like debug or firmware access mechanisms. The selected index and data value persist as register state and may have firmware side effects.
- GFX IMU C2P mailboxes, mutexes, command/status registers, DPM counters, interrupt-controller registers, RAM windows, reset controls, and power-good fields are shared between host driver, RLC, MP1/SMU, PSP-adjacent flows, and IMU firmware. Some are software-programmed controls, some are hardware/firmware-updated status, and some are side-effectful command windows.
- GC CAC accumulator registers are counter state for graphics-core activity or power/clock accounting. The `ACCUMULATOR_31_0` fields are full 32-bit values and may roll over or be sampled/reset by firmware or driver policy.
- Stall/release/power-break LUTs and fixed-pattern performance counters are hardware tuning/measurement state for clock/power transition logic.

Reserved fields and full-register masks appear throughout this range. Callers should preserve undocumented bits during read-modify-write unless the programming sequence explicitly owns the complete register value.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies the corresponding `reg*` and `ix*` offsets. The shift/mask header must remain synchronized with that offset header and AMD's source register database.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which directly includes both `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h`.
- Common AMDGPU register-helper infrastructure: `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, indexed MMIO helpers, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- `gfx_v11_0.c`, `gfx_v12_0.c`, `mes_v11_0.c`, `mes_v12_0.c`, and `amdgpu_amdkfd_gfx_v11.c` show the same architectural field families in use for GRBM indexing, RLC clock-gating overrides, IMU firmware access, MES/RLC setup, and KFD-specific indexed GRBM programming. GC 11.5-specific code may include fewer direct users in this mirror, but the register layouts align with those shared programming patterns.
- `imu_v11_0.c`, `imu_v11_0_3.c`, and `imu_v12_0.c` are relevant consumers for IMU mailbox/access-control/RLC-RAM patterns around registers represented in this chunk.
- PM/SMU code and firmware-interface headers expose feature flags and policy controls for GFX IMU, GC CAC, and clock/power management; this header supplies the low-level GC register field metadata those flows ultimately rely on.

## Risks And Edge Cases

- Generated-header drift is the main risk. An incorrect shift or mask will compile cleanly but program the wrong hardware bits.
- The range starts and ends mid-family. File-level research should merge adjacent chunks before making complete claims about `GFX_ICG_GL2A_CTRL` or the fixed-pattern counter and `HW_LUT_UPDATE_STATUS` families.
- Clock-gating override fields are power and liveness sensitive. Incorrect `SOFT_OVERRIDE`, `SOFT_STALL_OVERRIDE`, hysteresis, MGLS, or per-client override masks can cause hangs, clock domains stuck on/off, failed idle entry, or large power regressions.
- Repeated register families are copy-sensitive. Examples include PBB/SC clock fields, IMU C2P message registers, PIC priority registers, CAC accumulators, and transition LUT pattern slots; a one-register mismatch can affect only a narrow instance.
- GRBM index and remap fields affect addressing of per-SE/per-SA/per-instance registers. Bad masks can direct writes to the wrong shader array, accidentally broadcast writes, or misreport harvested/disabled topology.
- RLC, GPM, PACE, SRM, IMU, and PSP data windows are selector/data pairs. If field definitions or sequencing are wrong, firmware memory, scratch, or control windows can be corrupted without an obvious local failure.
- Mailbox, mutex, interrupt, and reset fields can be shared across host driver, firmware, and virtualization paths. Access-order, ownership, or stale-bit mistakes can deadlock firmware handshakes or lose interrupts.
- `GC_USER_*_DISABLE`, redundancy, pipe-steering, and shader-rate configuration fields describe hardware topology and policy. Wrong masks can expose nonexistent resources, hide available resources, or route traffic incorrectly.
- CAC accumulator and fixed-pattern counter fields may roll over, be sampled asynchronously, or have clear/update side effects outside this header. The macros do not document read-clear, latch, or sampling rules.
- LUT transition fields are compact bitfields with different widths across release/stall/power-break tables. Reusing the wrong table width can silently corrupt adjacent pattern entries.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware runtime signals:

- Build AMDGPU with GC 11.5 support. Include users such as `gfxhub_v11_5_0.c` should catch missing or renamed macros; broader GC 11 builds exercise the shared field-family conventions.
- Mechanically compare this range against the authoritative GC 11.5.0 register database. Check that masks align with shifts, full-width fields use `0xFFFFFFFFL`, and repeated families have consistent shapes.
- Cross-check every register family in this chunk against `gc_11_5_0_offset.h` for matching direct `reg*` offsets or indirect `ixGC_CAC_*` offsets.
- Run static sanity checks around boundary registers: `GFX_ICG_GL2A_CTRL` must be reconciled with the previous chunk, and fixed-pattern counters 8-10 plus `HW_LUT_UPDATE_STATUS` must be reconciled with the next chunk.
- Exercise graphics init, suspend/resume, GPU reset, and runtime power-management paths. Relevant signals are successful clock-gating enable/disable transitions, no RLC/IMU firmware timeouts, stable idle residency, and no unexpected power draw or hangs.
- Exercise GRBM-indexed register access across shader engines, shader arrays, WGPs, render backends, and harvested configurations. Expected signals include correct broadcast behavior and accurate topology reporting.
- Exercise IMU firmware loading, C2P mailbox traffic, RLC RAM access, DPM/ref-counter reads, interrupt delivery, reset sequencing, and doorbell control. Watch for mailbox timeouts, stale mutexes, missing IH/PIC interrupts, or reset failures.
- Exercise virtualization or hypervisor-facing flows where available: RLC hypervisor semaphores, secure GRBM CAM access, PSP debug windows, and user topology/remap fields.
- Read/sample GC CAC accumulators and fixed-pattern performance counters around known graphics/compute activity. Expected signals are monotonic or policy-expected counter movement, sensible rollover handling, and no access faults through the CAC indirect path.
- Run mixed graphics/compute workloads under power-management stress to expose clock-gating, pipe-steering, and transition-LUT issues that may appear only under load, idle, or rapid state transitions.

## Cross-Chunk Notes

The previous chunk owns most of `GFX_ICG_GL2A_CTRL`; this chunk begins with its final shift definition and all masks, then covers CGTT/ICG controls, GC hypervisor-visible controls, PSP windows, GFX IMU windows, CAC accumulators, transition LUTs, and fixed-pattern performance counters 1-7. The next chunk should continue fixed-pattern counters 8-10 and `HW_LUT_UPDATE_STATUS`. The final per-file document should reconcile these artificial line boundaries before describing the complete GC 11.5.0 shift/mask header.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 32559-35036

## Purpose

This chunk is generated AMD GC 10.3.0 register field metadata. It contains no executable C logic; it exports preprocessor constants for bit shifts and bit masks used to compose, read, and update fields inside Graphics Core MMIO registers. Consumers pair this file with the matching GC 10.3.0 offset header and AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

The requested range starts in the `RLC_PG_CNTL` field definitions and then covers a large RunList Controller / RunList Compute (`RLC`) region, two RLC decode address blocks (`gc_rlcrdec` and `gc_rlcsdec`), and the beginning of the GC power decoder (`gc_pwrdec`) clock-gating controls. Although the source tree path is under `ceph-client`, this file is AMDGPU hardware metadata, not distributed filesystem code.

Major hardware themes in this range are:

- RLC graphics power gating, clock gating, low-bandwidth power, SMU handshakes, GPM thread controls, and WGP status/request fields.
- RLC firmware-facing general-purpose, safe-mode, scheduler, scratch, semaphore, interrupt, doorbell, PACE timer, SPM, SPP, SRM, UTCL1, and prewalker controls.
- RLC RLCS decode/status registers for bootload status, power-state sequencing, load-balancing status, interrupt-handling metadata, GRBM idle/busy state, SDMA busy changes, virtualization/IOV status, UTCL2 overrides, SMU voltage-change handshakes, and KMD logging.
- GC power clock-gating controls for CGTS status and CGTT blocks including SPI, PC, BCI, VGT, IA, WD, GS/NGG, PA, and SC clock domains. The chunk ends inside `CGTT_SC_CLK_CTRL1`; the next chunk is needed for the rest of the power decoder block.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or local includes in this slice. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field inside a 32-bit register.
- `<REGISTER>__<FIELD>_MASK`: field mask for preserving, clearing, or extracting that field.

Important register families covered by the chunk:

- `RLC_PG_CNTL`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_PG_DELAY`, `RLC_STATIC_PG_STATUS`, `RLC_PG_DELAY_3`, `RLC_PG_ALWAYS_ON_WGP_MASK`, `RLC_MAX_PG_WGP`, `RLC_AUTO_PG_CTRL`, and `RLC_LB_*`: graphics and per-WGP power-gating policy, delays, masks, load-balancing parameters, and status.
- `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_CGCG_CGLS_CTRL_3D`, and `RLC_CGCG_RAMP_CTRL_3D`: coarse-grain clock gating and clock-gating light sleep enablement, idle thresholds, compensation delays, sleep modes, and ramp timing.
- `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, `RLC_GPM_GENERAL_0` through `RLC_GPM_GENERAL_16`, `RLC_GPM_INT_*`, and `RLC_GPM_LOG_*`: RLC GPM microcontroller thread enablement, priority, scratch/general registers, logging, interrupt masking, forcing, and status.
- `RLC_SPM_*`, `RLC_SPP_*`, and `RLC_SPM_THREAD_TRACE_CTRL`: streaming/performance monitor controls, memory-client attributes, sample counts, shader/power profiling, PVT counters, SSF capture, CAM access, and reset/status fields.
- `RLC_SRM_*`, `RLC_SRM_INDEX_CNTL_ADDR_*`, and `RLC_SRM_INDEX_CNTL_DATA_*`: SRM command queues, indexed control addresses/data, FIFO status, busy state, and abort fields.
- `RLC_RLCG_*`, `RLC_RLCV_*`, `RLC_RLCP_*`, and `RLC_XT_*` doorbell ranges, controls, status, and data registers: doorbell range bounds, mode selection, doorbell IDs, valid bits, and 64-bit data payload halves for several RLC clients.
- `RLC_GPM_UTCL1_*`, `RLC_SPM_UTCL1_*`, `RLC_PREWALKER_UTCL1_*`, `RLC_UTCL1_STATUS`, and UTCL1 error registers: translation retry timers, drop/bypass/invalidate controls, transaction-stall/busy status, prewalker trigger and address/size fields, and translated request error VMID/address reporting.
- `RLC_RLCS_*`: RLCS decode block fields for power, clock, boot, IOV, interrupt, GRBM idle/busy, CP/SPM interrupt info, IH packet metadata, WGP state, bootload ID loaded bits, power brake, UTCL2 overrides, and SMU/MP1 handshakes.
- `CGTS_*` and `CGTT_*`: power decoder readback, TCC disable/status, and clock-control fields. Common CGTT patterns include `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, `SOFT_OVERRIDE*`, `GRP*_OVERRIDE`, domain-specific core override bits, and `REG_OVERRIDE`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU graphics and power-management code:

1. GC 10.3 consumers include `gc_10_3_0_sh_mask.h` with `gc_10_3_0_offset.h`.
2. Driver code reads a GC register through the SOC15 helpers, clears or sets masks from this header, and writes the result back. Field helpers also use the `__SHIFT` and `_MASK` definitions to update individual fields.
3. Power-management paths program `RLC_PG_CNTL`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_CGLS_CTRL_3D` around power-gating and clock-gating transitions. The same mask names are used in nearby GC generations, and GC 10.x code uses this exact header for GC 10.3 hardware.
4. Firmware/load paths poll status fields such as `RLC_RLCS_BOOTLOAD_STATUS__BOOTLOAD_COMPLETE_MASK` after RLC firmware setup, and interrupt paths use the RLCS, SPM, GPM, PACE, and doorbell fields to report or acknowledge hardware events.
5. Golden-register programming and low-power setup code use the `CGTT_*` fields and whole-register masks to tune clock gating for individual graphics blocks.

The macros do not encode required ordering. Callers must still sequence firmware loading, safe mode, SMU handshakes, power-gating enables, idle waits, interrupt clear/ack operations, and suspend/resume restore ordering correctly.

## State And Persistence Behavior

This chunk stores no software state and performs no persistence. It describes MMIO-backed hardware state.

The represented state includes:

- Persistent configuration until reset or power transition: RLC power-gating policy, CGCG/CGLS enables and thresholds, thread enables/priorities, memory-client attributes, SRM controls, doorbell ranges, SPP/SPM profiling controls, UTCL1/UTCL2 behavior, and CGTT clock-gating override values.
- Volatile status and counters: WGP work pending and power status, load-balancing counters, RLC clock-valid/busy state, UTCL1 fault/retry/PRT and busy/stall bits, RLCS bootload status, GRBM/SDMA idle-busy status, PVT counters, GPU clock counters, and CGTS status/readback fields.
- Event and handshake state: spare interrupts, CP EOF interrupts, SPM/GPM/RLCS interrupt info and ack controls, PACE timers, doorbell valid/data fields, SMU message/argument/command fields, MP1/RLC doorbell control, SMUIO voltage-change request/ack fields, and power-brake status.

Some fields are likely read-only status bits, write-one-to-clear bits, sticky interrupt status, self-clearing command bits, or reserved fields. This header does not mark access direction or side effects; those semantics come from the ASIC register database and the consuming driver paths.

## Dependencies And Integration Points

This generated mask header must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which defines the corresponding `mm...` register offsets.
- SOC15 GC base-address tables and register-access helpers used by AMDGPU.
- AMDGPU graphics, SDMA, GFXHUB, KFD, and SMU code that includes `gc/gc_10_3_0_sh_mask.h`.

Observed direct include sites for the exact GC 10.3.0 mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`

Important cross-file consumers and patterns in the AMDGPU tree include GC 10.x graphics code that reads/writes `RLC_PG_CNTL`, sets `RLC_GPM_THREAD_ENABLE` bits, programs `RLC_CGCG_CGLS_CTRL` and `_3D`, polls `RLC_RLCS_BOOTLOAD_STATUS`, and applies golden values for `CGTT_*_CLK_CTRL` registers. Those consumers rely on this file's masks being bit-accurate for GC 10.3.0 silicon.

## Risks And Edge Cases

- Generated-mask drift is the main correctness risk. A wrong shift or mask compiles cleanly but can modify the wrong hardware field, especially where adjacent reserved bits surround power, interrupt, or command fields.
- Reserved bits must be preserved. Many registers expose large `RESERVED` masks; callers should read-modify-write targeted fields instead of writing arbitrary whole-register constants unless those constants are known golden settings.
- Power and clock controls are sequencing-sensitive. Misprogramming `RLC_PG_CNTL`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, or `CGTT_*_CLK_CTRL` fields can cause hangs, wake failures, excessive power draw, broken suspend/resume, or intermittent failures only under idle/load transitions.
- Doorbell, interrupt, and command fields can have side effects. Incorrect ack/clear/mode/data handling in `RLC_*_DOORBELL_*`, `RLC_RLCS_*_INT_*`, `RLC_SPM_INT_*`, `RLC_GPM_INT_*`, PACE timer, SMU command, and safe-mode registers can lose events or wedge firmware communication.
- Firmware and boot status fields are ABI-like. Polling the wrong `RLC_RLCS_BOOTLOAD_STATUS` bit or misinterpreting bootload ID status can make firmware initialization appear complete too early or time out even when hardware is healthy.
- Virtualization and address-translation fields are security-sensitive. `RLC_RLCS_IOV_*`, UTCL1 error address/VMID fields, `RLC_RLCS_UTCL2_CNTL` GPA/VF overrides, and IH VF metadata must remain matched to the hardware generation to avoid incorrect fault attribution or isolation behavior.
- The chunk boundary is artificial. It begins after the start of `RLC_PG_CNTL` and ends inside `CGTT_SC_CLK_CTRL1`; adjacent research chunks are required for full-file reasoning.

## Test Signals

Useful validation signals for code that consumes this chunk are hardware and integration oriented:

- Kernel build coverage for GC 10.3 AMDGPU paths confirms macro names still match consumers.
- GPU initialization logs should show successful RLC firmware load and no timeout polling `RLC_RLCS_BOOTLOAD_STATUS__BOOTLOAD_COMPLETE`.
- Suspend/resume, runtime power management, and idle-to-load transitions should complete without GC/RLC hangs, SMU handshake errors, or GRBM idle timeout messages.
- Stress tests for graphics, compute, SDMA, and KFD workloads should not report UTCL1/UTCL2 translation errors, CP status invalidation storms, or doorbell/interrupt loss.
- Power telemetry should show expected clock-gating and power-gating behavior when CGCG/CGLS and CGTT golden settings are applied.
- Debugfs or driver diagnostics reading RLC/SPM/SPP/GPM status should report coherent busy, interrupt, profile, and counter values rather than stuck or impossible bit combinations.

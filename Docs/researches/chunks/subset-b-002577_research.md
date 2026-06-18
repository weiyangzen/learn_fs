# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 20328-22793

## Scope

This chunk is a generated AMDGPU GC 12.0.0 register shift/mask header segment. It contains C preprocessor constants only: each hardware register field is exposed as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The matching register offsets live in `gc_12_0_0_offset.h`; default values, where present, live in the corresponding GC default header.

The range is centered on RLC and power-control register fields. It starts in the tail of `RLC_GPM_LEGACY_INT_DISABLE`, then covers RLC SRM/GPM command and status fields, UTCL1 and UTCL2 controls/errors, RLC clock/count capture, SPP/SPM profiling and residency counters, RLC interrupt-handler client status, LX6/Xtensa-style RLC core controls, doorbell capture, safe-mode and SMU command mailboxes, IMU bootload fields, the `gc_gfx_cpwd_cpwd_rlcsdec` RLCS decoder block, the `gc_gfx_cpwd_cpwd_pfvfdec_rlc` PF/VF RLC block, and the beginning of `gc_gfx_cpwd_cpwd_pwrdec` power/clock-gating fields through `GFX_ICG_GL2C_CTRL`.

## Purpose

The purpose of this header slice is to give GC 12 AMDGPU, KFD, MES, SDMA, GFXHUB, IMU, and SOC24 code stable symbolic bit definitions for low-level MMIO register programming. Driver code uses these masks with the matching offset macros through `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, golden-register helpers, and firmware-facing queue or initialization paths.

The fields in this chunk are mostly management-plane fields rather than shader execution fields. They describe how the RLC firmware complex coordinates GPU power transitions, register save/restore, bootload/autoload completion, interrupt delivery, profiling/sample collection, doorbells, IMU communication, memory sleep/deep-sleep behavior, and clock-gating overrides. Because the macros are pure constants, correctness depends on generated names, bit positions, masks, and register-family continuity matching the hardware register database.

## Register Families

`RLC_SRM_*` and `RLC_GPM_*` fields describe save/restore manager and graphics power-management control. The chunk includes SRM enable/reset/autoincrement, GPM command FIFO empty/full/overflow status, eight indexed SRM control address/data slots, `RLC_SRM_STAT`, GPM interrupt force/status/general scratch fields, SRM/GPM command encodings (`OP`, `INDEX_CNTL`, `INDEX_CNTL_NUM`, `SIZE`, `START_OFFSET`), and abort controls. These fields are the bit-level surface used when firmware or driver paths initiate or inspect register save/restore and GPM command activity.

`RLC_*_UTCL1_*` and `RLC_RLCS_UTCL2_*` fields cover translation/cache interface behavior and error reporting. The UTCL1 controls for GPM, SPM, SRM, and LX6 share the same shape: retry timer count, drop/bypass/invalidate, fragment-limit mode, force-snoop, and reserved fields. Error registers split translated request error type, VMID, high address bits, and low address bits. Status registers report faults, retries, PRT detection, busy status, stalls, and per-client IDs. The later RLCS UTCL2 controls add GPA/VF override, no-PTE memory type behavior, ignore-permission behavior, busy handshakes, and request/ack status.

`RLC_CGCG_CGLS_CTRL_3D`, `RLC_CGCG_RAMP_CTRL_3D`, `RLC_MEM_SLP_CNTL`, the RLCS deep-sleep controls, and the final `CGTT_*`/`GFX_ICG_*` block are power-management fields. They define clock-gating enables, ramp timing, sleep modes, memory light-sleep/deep-sleep enables and overrides for SRM/SPM/SPP/TC, SOC/GFX deep-sleep allow masks, GDFLL allow masks, shader-engine power/reset bits, GL2C disable masks, and per-block clock-gating delay/override bits for IA, WD, CP, CPF, CPC, RLC, GCR, EA/CPWD, GC CAC, GRBM, GL2A, and GL2C.

`RLC_SPP_*`, `RLC_SPM_*`, and residency-counter fields support profiling, power profiling, streaming performance monitor paths, and power residency instrumentation. The chunk includes SPP enable/pause/power-opt controls, shader-stage profiling enables and start conditions, SSF capture enables and thresholds, inflight readback address/data, profiling info, global shader IDs, SPP status and PVT counters, stall-state update, PBB override information, SPP reset bits, SPM delay/mask indirect address/data, SPM sample count, MC control attributes, interrupt control/status/info, and power/clock/DS/ULV/PCC/general residency counter reset/enable/ack/overflow plus event/reference counter data.

`RLC_GFX_IH_*`, `RLC_RLCS_*_INT_*`, `RLC_CP_EOF_INT*`, and spare interrupt fields describe interrupt plumbing. The RLC GFX IH control masks SE, SDMA, UTCL2, and PMM interrupt clients and has matching error-clear fields. Status registers report arbiter grants, per-SE0..SE7 buffer level/loading/protocol-error/overflow, per-SDMA0..SDMA3 status, and UTCL2/PMM status. RLCS CP, SPM, SDMA, GRBM idle/busy, GPM legacy, spare, and EOF interrupt fields provide ack/auto-ack, interrupt IDs, pending bits, status histories, and clear bits.

`RLC_LX6_*`, `RLC_XT_*`, `RLC_IMU_*`, and `RLC_RLCS_IMU_*` describe the embedded RLC/IMU control and messaging surfaces. They include LX6 reset/runstall/debug/status/firmware status/version, XT core status/interrupt/fault/alternate-vector fields, vector force/clear bits for interrupt sources, doorbell range/mode/status/data fields, IMU bootload address/size/misc/reset-vector fields, bidirectional IMU-RLC message data/control/toggle fields, telemetry current/voltage/temperature/rail fields, mutex control, IMU/RLC status, IMU RAM address/data handshakes, and a GFX doorbell fence.

`RLC_RLCS_*` fields define the RLCS decoder block. The chunk includes exception and auxiliary register address fields, CGCG request/status, SOC and GFX deep-sleep controls, GPM status mirrors, aborted power-down sequence, GRBM soft reset, power-gating change status/read, IH semaphores, bootload status, GRBM idle/busy status and interrupt controls, compute-idle hysteresis, general scratch registers, bootload ID loaded bitmaps for IDs 0..63, GCR data/status, perfmon clock state, GFX memory power control data registers, shader-engine power controls, and decoder block sentinels.

## Important APIs, Types, and Functions

This header defines no functions, structs, enums, or runtime storage. Its API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the masked bit range in the register word.
- Full-width payload fields use mask `0xFFFFFFFFL`; reserved fields are explicitly named so generated consumers can preserve or clear the correct bit ranges.

The main external helpers are `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and table macros such as SOC15 golden-register entries. Important in-tree GC 12 consumers include `amdgpu/gfx_v12_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v12.c`, `amdkfd/kfd_mqd_manager_v12.c`, `amdkfd/kfd_device_queue_manager_v12.c`, `amdgpu/mes_v12_0.c`, `amdgpu/sdma_v7_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/imu_v12_0.c`, and `amdgpu/soc24.c`, all of which include `gc_12_0_0_sh_mask.h` directly or use it alongside the matching offset header.

Concrete examples visible in this tree include `gfx_v12_0_wait_for_rlc_autoload_complete()`, which reads `regRLC_RLCS_BOOTLOAD_STATUS` and extracts `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`, and `gfx_v12_0_set_safe_mode()`, which builds a value with `RLC_SAFE_MODE__CMD_MASK` and `RLC_SAFE_MODE__MESSAGE__SHIFT`, writes `regRLC_SAFE_MODE`, and polls `RLC_SAFE_MODE.CMD`.

## Control Flow

There is no executable control flow in this header. Runtime control flow is imposed by register consumers:

- GC 12 RLC autoload waits read CP and RLC bootload status repeatedly until CP is idle and the RLCS bootload complete bit is set.
- Safe-mode entry writes the RLC safe-mode command/message bits and polls for command completion; safe-mode exit writes the command bit again with the exit message encoding.
- Power-management paths program clock-gating and memory sleep/deep-sleep fields during initialization, power-state transitions, suspend/resume, reset recovery, or firmware-managed transitions.
- RLC/IMU messaging uses data/control registers plus toggle, done, ack, mutex, and fence fields to handshake ownership and command completion.
- Interrupt paths mask, acknowledge, clear, or inspect RLC-facing interrupt clients, including SE, SDMA, UTCL2, PMM, CP, SPM, spare, EOF, and GRBM idle/busy sources.
- Profiling and telemetry paths enable SPP/SPM capture, configure thresholds or memory attributes, read sample/residency counters, and use status bits to detect overflow or completion.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware registers they describe are volatile GPU state, but many fields have effects that persist until reset, firmware action, or explicit driver writes.

RLC safe-mode, SMU message/argument, SRM/GPM command, IMU bootload, IMU-RLC mailbox, and doorbell fields represent command or handshake state. A stale toggle, ack, command, or doorbell-valid bit can make firmware and driver code disagree about ownership or completion.

Power and clock controls persist across the active power state of the GC block. Clock-gating override bits, memory light-sleep/deep-sleep enables, GFX/SOC deep-sleep allow masks, and shader-engine reset/clock-enable fields can change performance, power, idle detection, and reset behavior until reprogrammed by init, resume, or recovery code.

Status and counter registers are diagnostic state. Bootload status, GPM status, GRBM idle/busy state, UTCL1/UTCL2 fault or busy bits, residency event/reference counters, SPP/PVT counters, interrupt info, and SDMA/SE buffer status can be latched, accumulated, or cleared by side-effect depending on the hardware register semantics. Driver diagnostics and timeout paths depend on reading these fields with the exact masks defined here.

## Dependencies and Integration Points

This chunk depends on the broader generated GC 12 register set: `gc_12_0_0_offset.h` supplies the register addresses, this file supplies field positions, and driver helpers perform the read/modify/write and field extraction. It also depends on SOC24 register access plumbing, firmware loading policy, RLC/IMU firmware contracts, MES/KFD queue management, and GPU power-management policy.

Important integration points include:

- `amdgpu/gfx_v12_0.c` for RLC autoload completion, safe-mode entry/exit, firmware bring-up, reset, and GFX power behavior.
- `amdgpu/imu_v12_0.c` for IMU initialization and RLC/IMU coordination, using the same GC 12 register namespace.
- `amdgpu/mes_v12_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v12.c`, and KFD v12 queue managers for compute queue setup, command processor integration, and RLC-visible state around queue scheduling.
- `amdgpu/gfxhub_v12_0.c` and `amdgpu/sdma_v7_0.c`, which include this header for GC 12 field extraction and register programming adjacent to VM and DMA flows.
- Interrupt handling and diagnostics that read RLC GFX IH, CP/SPM/SDMA interrupt info, bootload status, idle/busy status, and fault information.
- Firmware and hardware-generation tooling: because this is generated, downstream code assumes macro spellings and field positions match the authoritative register database.

## Risks

The main risk is silent hardware misprogramming. These macros are constants; a wrong shift or mask can compile cleanly while causing driver code to set the wrong bits, preserve reserved bits incorrectly, or poll a field that never changes.

High-risk fields in this chunk include `RLC_SAFE_MODE`, `RLC_RLCS_BOOTLOAD_STATUS`, IMU bootload and IMU-RLC mailbox controls, SRM/GPM command/abort fields, `RLC_MEM_SLP_CNTL`, deep-sleep allow masks, clock-gating override controls, UTCL1/UTCL2 error/status fields, and interrupt ack/clear/status fields. Errors in these areas can produce initialization timeouts, failed RLC autoload, broken reset recovery, hangs during power transitions, lost interrupts, incorrect fault attribution, or performance/power regressions.

Reserved-bit masks are also important. Read/modify/write code must avoid accidentally setting reserved fields, while generated masks must still describe the reserved ranges accurately enough for table or diagnostic tooling to preserve them. The file should therefore be regenerated from hardware definitions rather than hand-edited.

## Test Signals

Compile-time signals include successful AMDGPU/KFD builds for GC 12 code that includes `gc_12_0_0_sh_mask.h`, especially `gfx_v12_0.c`, `amdgpu_amdkfd_gfx_v12.c`, `kfd_mqd_manager_v12.c`, `kfd_device_queue_manager_v12.c`, `mes_v12_0.c`, `sdma_v7_0.c`, `gfxhub_v12_0.c`, `imu_v12_0.c`, and `soc24.c`. Renamed or removed macros should fail quickly; wrong numeric values usually require runtime testing.

Runtime signals should focus on GC 12 hardware or emulation: successful GPU probe, RLC/IMU firmware loading, `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE` reaching completion before timeout, safe-mode entry/exit completing, suspend/resume, GPU reset recovery, MES startup, KFD process and queue creation, SDMA activity, and stable compute/graphics workloads.

Power and diagnostics signals include correct clock-gating and memory-sleep behavior, no unexpected hangs during GFXOFF/deep-sleep transitions, sane RLC GPM/GRBM idle-busy status, no persistent UTCL1/UTCL2 fault bits under normal workloads, working interrupt delivery and clearing for SE/SDMA/UTCL2/PMM/SPM/CP paths, valid SPP/SPM/residency counter behavior, and no firmware mailbox or doorbell handshakes stuck in pending states.

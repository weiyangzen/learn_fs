# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 131413-133888

## Scope

This chunk is part of AMDGPU's generated NBIO 6.1 register shift/mask header. It is not executable C; it exports preprocessor constants used by NBIO, PCIe, SR-IOV, HDP flush, doorbell, mailbox, and system-hub register access code.

The slice begins in the tail of the `BIF_BX_DEV0_EPF0_VF4` virtual-function register block, fully covers the repeated `BIF_BX_DEV0_EPF0_VF5` through `BIF_BX_DEV0_EPF0_VF15` blocks, then enters the `syshub_mmreg_ind_syshubind` address block. The final SYSHUB range defines clock/deep-sleep, QoS, reset, WRR arbitration, clock-gating, scratch/mask, idle-status, and NIC400 issue-override fields.

## Purpose

The definitions give field positions and masks for NBIO 6.1 hardware registers. Driver code pairs these constants with addresses from `nbio_6_1_offset.h` and access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `REG_GET_FIELD`, `REG_SET_FIELD`, and `WREG32_FIELD15`.

The VF blocks expose per-virtual-function hardware surfaces used by SR-IOV and virtualization-aware NBIO paths:

- Indexed MMIO access windows: `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- Bus-master and PCIe atomic error status: `BIF_BME_STATUS` and `BIF_ATOMIC_ERR_LOG`.
- Doorbell self-ring GPA aperture base/control: high base, low base, enable, mode, and size fields.
- HDP coherency flush controls and engine-specific GPU HDP flush request/done bits.
- BIF transaction pending state for master and slave paths.
- Four DWORD transmit and receive mailbox payload buffers, mailbox valid/ack control, interrupt enables, and compact VM/HV mailbox fields.

The SYSHUB block models lower-level system hub power and interconnect behavior:

- SOCCLK and SHUBCLK deep-sleep permission bits for host and DMA clients.
- Deep-sleep timers and bgen bypass/immediate-enable controls.
- DMA switch QoS control and class-level reset/QoS/WRR settings.
- Host class reset controls.
- SYSHUB clock-gating, transaction-idle, high-priority timer, scratch, and client-mask fields.
- NIC400 ASIB/AMIB read and write issue override bits.

## Important Definitions

The generated naming convention is consistent throughout the slice:

- `<REGISTER>__<FIELD>__SHIFT` is the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` is the raw bit mask for that field.
- `BIF_BX_DEV0_EPF0_VF<n>` names per-SR-IOV virtual-function register views.
- `SYSHUB_MMREG_IND_*` names registers reached through the SYSHUB indirect MMREG aperture.

Virtual-function register groups:

- VF4 tail: `MAILBOX_MSGBUF_TRN_DW0..DW3`, `MAILBOX_MSGBUF_RCV_DW0..DW3`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`.
- VF5 through VF15: each repeats the same core template: `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `DOORBELL_SELFRING_GPA_APER_BASE_HIGH/LOW/CNTL`, `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `BIF_TRANS_PENDING`, mailbox message buffers, mailbox control, mailbox interrupt control, and VM/HV mailbox.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` fields enumerate engines `CP0` through `CP9` plus `SDMA0` and `SDMA1`.
- `MAILBOX_CONTROL` fields use the standard transmit/receive handshake shape: `TRN_MSG_VALID`, `TRN_MSG_ACK`, `RCV_MSG_VALID`, and `RCV_MSG_ACK`.
- `BIF_VMHV_MAILBOX` packs interrupt enables, 4-bit transmit/receive message data, valid bits, and ack bits into one register.

SYSHUB register groups:

- `SYSHUB_DS_CTRL_SOCCLK` and `SYSHUB_DS_CTRL_SHUBCLK` define deep-sleep allow bits for `HST_CL0..CL7`, `DMA_CL0..CL7`, and the SYSHUB clock domain enable/allow bits.
- `SYSHUB_DS_CTRL2_SOCCLK` and `SYSHUB_DS_CTRL2_SHUBCLK` define 16-bit deep-sleep timer fields.
- `SYSHUB_BGEN_ENHANCEMENT_BYPASS_EN_*` and `SYSHUB_BGEN_ENHANCEMENT_IMM_EN_*` expose bgen bypass/immediate-enable controls for host and DMA switches.
- `DMA_CLK0_SW*_SYSHUB_QOS_CNTL` and `DMA_CLK1_SW*_SYSHUB_QOS_CNTL` define `QOS_CNTL_MODE`, `QOS_MAX_VALUE`, and `QOS_MIN_VALUE`.
- `DMA_CLK{0,1}_SW*_CL*_CNTL` records `FLR_ON_RS_RESET_EN`, `LKRST_ON_RS_RESET_EN`, `QOS_STATIC_OVERRIDE_EN`, `QOS_STATIC_OVERRIDE_VALUE`, `READ_WRR_WEIGHT`, and `WRITE_WRR_WEIGHT`.
- `HST_CLK0_SW*_CL*_CNTL` supplies host-client reset policy bits.
- `SYSHUB_CG_CNTL`, `SYSHUB_TRANS_IDLE`, `SYSHUB_HP_TIMER`, `SYSHUB_MGCG_CTRL_SOCCLK`, and `SYSHUB_MGCG_CTRL_SHUBCLK` expose clock gating, idle-status, and high-priority timing controls.
- `SYSHUB_SCRATCH` and `SYSHUB_CL_MASK` provide a scratch word and host/DMA client masking fields.
- `NIC400_*_FN_MOD*` fields expose `read_iss_override` and `write_iss_override` controls for selected NIC400 ASIB/AMIB ports.

## APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs defined in this chunk. The exported interface is the macro namespace consumed by AMDGPU code after including `nbio/nbio_6_1_sh_mask.h`.

The immediate NBIO 6.1 consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes:

- `nbio/nbio_6_1_default.h`
- `nbio/nbio_6_1_offset.h`
- `nbio/nbio_6_1_sh_mask.h`
- `nbio/nbio_6_1_smn.h`

That file demonstrates the expected helper style: it reads and writes NBIO registers with SOC15 helpers, uses `REG_SET_FIELD` for field updates, programs the PF0 doorbell self-ring aperture, exposes HDP flush request/done register offsets, and builds `struct nbio_hdp_flush_reg` masks from `*_GPU_HDP_FLUSH_DONE` definitions. The specific VF5-VF15 names in this chunk are more virtualization-specific than the PF0 names used by the bare-metal NBIO path, but they follow the same mask semantics.

Related search hits also show later NBIO/NBIF generations using equivalent `BIF_BX_PF*` doorbell self-ring and HDP flush fields, and `mxgpu_ai` using BIF mailbox control semantics for guest/host messaging. This makes the VF mailbox definitions in this chunk part of the same SR-IOV communication pattern even when exact VF macros are not directly referenced in the local C slice.

## Control Flow

This header has no branches, loops, calls, locking, or ordering of its own. The effective control flow is created by users of the macros:

1. Select a register address from the matching offset header.
2. Read the register through the AMDGPU MMIO/SMN/SOC15 access layer.
3. Extract or update fields using the `__MASK` and `__SHIFT` constants, often through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. Write the modified value back, or poll status bits until the hardware reaches the expected state.

Typical VF-side flows described by these fields include:

- Enabling a VF doorbell self-ring aperture by writing base-low/base-high and setting `DOORBELL_SELFRING_GPA_APER_EN`, `MODE`, and `SIZE`.
- Requesting HDP coherency flushes for CP or SDMA engines with `GPU_HDP_FLUSH_REQ`, then checking corresponding bits in `GPU_HDP_FLUSH_DONE`.
- Checking whether BIF master or slave transactions are still pending before reset, FLR, suspend, or virtualization teardown.
- Exchanging messages through transmit/receive mailbox DWORD buffers and valid/ack handshakes.
- Reporting and clearing DMA-on-BME-low and unsupported atomic request error conditions.

Typical SYSHUB flows include:

- Enabling or disabling deep-sleep participation for host/DMA clients in SOCCLK and SHUBCLK domains.
- Setting QoS min/max, static QoS override, and read/write WRR weights before latency-sensitive or reset-sensitive operation.
- Configuring medium-grain clock gating hysteresis and client disable masks.
- Reading aggregate transaction-idle bits before power, reset, or clock-gating transitions.
- Overriding NIC400 read/write issuing behavior for specific interconnect ports during bring-up, workarounds, or low-power sequences.

## State And Persistence

The macros are compile-time constants and do not store runtime state. The state they describe lives in NBIO/SYSHUB hardware registers.

VF state includes mailbox payloads and handshakes, transaction-pending status, atomic error latches, BME-low status, doorbell aperture configuration, HDP flush request/done bits, and MM index/data selector state. Many of these are transient hardware states that may change during command submission, guest/host communication, reset, FLR, and interrupt handling.

SYSHUB state includes power-management permissions, clock-gating configuration, QoS weights, reset response policy, transaction-idle indicators, scratch data, client masks, and NIC400 issue override policy. These values are hardware configuration, not kernel-persisted data. They may reset across GPU reset, FLR, BACO, suspend/resume, PCIe reset, or ASIC power transitions unless firmware or the AMDGPU resume/reset path reapplies them.

Care is required for fields whose names imply latch or clear behavior, such as `CLEAR_DMA_ON_BME_LOW` and `CLEAR_UR_ATOMIC_*`. They are not normal state variables; writes may clear hardware-recorded events.

## Dependencies And Integration Points

Direct dependencies:

- C preprocessor macro expansion.
- Matching register address definitions from `nbio_6_1_offset.h`.
- Optional default/reset values from `nbio_6_1_default.h`.
- SMN constants from `nbio_6_1_smn.h`.
- AMDGPU register helper macros that know how to combine register names, field names, masks, and shifts.

Functional integration points:

- `amdgpu/nbio_v6_1.c` for NBIO 6.1 include ordering and field access patterns.
- AMDGPU HDP flush infrastructure, where `*_GPU_HDP_FLUSH_DONE` masks become per-engine completion masks used by rings and memory coherency code.
- Doorbell aperture setup, especially self-ring doorbell programming, which shares the same base/control shape as the VF aperture registers in this chunk.
- SR-IOV/MxGPU code that uses BIF mailbox valid/ack and interrupt-enable semantics for guest-to-host or host-to-guest control messages.
- Reset and power-management code that relies on transaction-idle, pending-transaction, deep-sleep, clock-gating, and reset-response fields before changing hardware state.
- Interconnect/QoS tuning paths that may use SYSHUB QoS, WRR, and NIC400 issue-override fields for performance or workarounds.

The document should be merged later with other chunks for the same source file because this range is only one generated segment of a much larger ASIC register contract.

## Risks

- A wrong mask or shift can silently corrupt hardware programming. In this range the blast radius includes SR-IOV mailbox communication, doorbell routing, HDP flush completion, BIF reset sequencing, SYSHUB clock gating, QoS, and interconnect behavior.
- Repeated VF5-VF15 blocks invite copy or generation drift. The groups should remain structurally identical unless the hardware register database intentionally defines a VF-specific exception.
- The slice begins after the start of VF4. Merge tooling must preserve that the VF4 definitions here are a tail continuation, not a complete VF4 block.
- Mailbox handshakes are sensitive to valid/ack ordering. Treating `TRN_MSG_VALID`, `TRN_MSG_ACK`, `RCV_MSG_VALID`, and `RCV_MSG_ACK` as ordinary writable state can lose messages or wedge guest/host synchronization.
- Clear fields in `BIF_BME_STATUS` and `BIF_ATOMIC_ERR_LOG` may be write-one-to-clear or otherwise edge-sensitive. Generic read-modify-write sequences can accidentally acknowledge events.
- HDP flush request/done fields are part of memory coherency. Bad masks can cause stale data visibility, command processor hangs, or false completion.
- Doorbell self-ring aperture base and size fields affect MMIO routing. Bad programming can send doorbells to the wrong GPA range or disable expected VF signaling.
- SYSHUB deep-sleep and clock-gating fields can break low-power entry/exit if timers, client masks, idle checks, or hysteresis fields are wrong.
- NIC400 issue overrides can change interconnect ordering/issuing behavior. They should be treated as hardware-workaround fields, not casual tuning knobs.
- This file is generated. Manual edits should be avoided; review should focus on generated-register-database deltas and cross-file consistency with offsets/defaults.

## Test Signals

Useful validation is primarily compile-time, generated-header consistency, and hardware coverage:

- Build AMDGPU with NBIO 6.1 enabled to catch missing, renamed, or malformed macro definitions.
- Compare the regenerated `nbio_6_1_sh_mask.h` range against the matching `nbio_6_1_offset.h` address names and `nbio_6_1_default.h` defaults.
- Check VF5 through VF15 symmetry for register groups and field masks, with explicit review for any intentional exceptions.
- Exercise SR-IOV or MxGPU paths that use BIF mailbox valid/ack behavior, and monitor for lost mailbox interrupts, stalled valid bits, or guest/host timeout logs.
- Exercise doorbell allocation and self-ring signaling for PF/VF configurations, then verify command submission does not lose doorbells.
- Run workloads that stress CP and SDMA engines and check HDP flush completion behavior, GPU reset frequency, and memory coherency symptoms.
- Run suspend/resume, FLR, GPU reset, and PCIe reset tests while checking transaction-pending and SYSHUB transaction-idle behavior.
- Validate clock-gating and deep-sleep changes with power-management telemetry and kernel logs for wake failures, timeout messages, AER errors, or link instability.
- For SYSHUB QoS/NIC400 fields, use performance and stability tests under DMA-heavy, host-heavy, and mixed workloads to catch ordering, starvation, or latency regressions.

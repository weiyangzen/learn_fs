# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_5_sh_mask.h lines 1-2543

## Scope and Purpose

This chunk is the first 2543 lines of the generated AMD VCN 2.5 register shift/mask header. It contains no executable C control flow; its job is to publish bitfield `__SHIFT` and `__MASK` constants used by the amdgpu VCN/JPEG 2.5 driver code when composing, clearing, polling, or decoding memory-mapped hardware registers. In this range there are 2134 `#define` entries spanning 355 register names.

The file is paired with the matching register-address header for VCN 2.5 and is included directly by `amdgpu/vcn_v2_5.c` and `amdgpu/jpeg_v2_5.c`. Those drivers use these constants with MMIO helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and DPG-mode write helpers to manipulate video decode, JPEG decode/encode, interrupt, power, clock-gating, ring-buffer, and MMSCH virtualization registers.

## Address Blocks Covered

- Lines 25-417, `uvd0_mmsch_dec`: MMSCH microcontroller/scheduler masks for ucode and SRAM access, VF context/GPCOM memory windows, mailboxes, interrupts, scratch registers, GPU IOV command/status blocks, VFID FIFOs, and VM busy status.
- Lines 418-581, `uvd0_jpegnpdec`: JPEG decode front-end masks for control, ring buffer base/pointers/size, interrupt enable/status, pitch, GFX8/GFX10 tiling and address config, GPCOM command/data, scratch, and soft reset.
- Lines 582-630, `uvd0_uvd_jpeg_enc_dec`: JPEG encode interrupt, status, engine control, and scratch masks.
- Lines 631-698, `uvd0_uvd_jpeg_enc_sclk_dec`: JPEG encoder SCLK-side status, pitch/base addresses, GFX10 tiling/address config, GPCOM, clock-gating control, scratch, and soft reset.
- Lines 699-816, `uvd0_uvd_jrbc_dec`: JPEG decode ring-buffer controller masks for RB/IB pointers and size, urgent priority, conditional-read timers, status/error bits, preemption command/fence data, and scratch.
- Lines 817-934, `uvd0_uvd_jrbc_enc_dec`: Encoder-side JRBC equivalent of the previous block, including separate `UVD_JRBC_ENC_*` status, timer, preempt, and ring size masks.
- Lines 935-1255, `uvd0_uvd_jmi_dec`: JPEG memory interface and LMI/JMI masks for arbitration wait, burst size, swap mode, VMID assignment, perfmon, 64-bit BAR low/high address halves, preempt fence addresses, and decode/encode swap controls.
- Lines 1256-1341, `uvd0_uvd_jpeg_common_dec`: Common JPEG reset status, system interrupt enable/status/ack, master interrupt enable, IH control, and JRBBM arbitration masks.
- Lines 1342-1460, `uvd0_uvd_jpeg_common_sclk_dec`: JPEG common clock-gating and memory power-management masks, soft reset, and four performance counter banks.
- Lines 1461-1731, `uvd0_uvd_pg_dec`: UVD/JPEG power-gating FSM and status masks, DPG LMA indirect access, DPG pause/ack, scratch registers, VCPU cache BAR/offset/VMID, page-fault status/clear bits, address config, and general-purpose counters.
- Lines 1732-2543, start of `uvd0_uvddec`: Core UVD status/busy, soft reset, MMSCH reset, clock-gating, SUVD clock-gating, GPCOM command/data, VCPU and SYS interrupt enable/status/ack, job/context/ring metadata, multiple ring-buffer base/size/pointer sets, output ring-buffer registers, and the beginning of `UVD_RB_ARB_CTRL`.

## Important Macros and Register Families

The macros follow a stable generated naming contract: `REGISTER__FIELD__SHIFT` gives the field bit offset and `REGISTER__FIELD_MASK` gives the already-positioned bitmask. Driver code typically clears `FIELD_MASK`, then ORs a shifted value such as `value << FIELD__SHIFT`; single-bit control paths often OR or clear only the mask.

Key families in this chunk:

- `MMSCH_UCODE_*`, `MMSCH_SRAM_*`, `MMSCH_CTL`, `MMSCH_CNTL`, and `UVD_MMSCH_SOFT_RESET`: scheduler firmware/SRAM loading, run-stall/reset, clocking, timeout, NACK, and lock fields.
- `MMSCH_VF_*`, `MMSCH_GPUIOV_*`, `MMSCH_VFID_FIFO_*`, `MMSCH_VM_BUSY_STATUS_*`: SR-IOV and virtualization state for VF context buffers, GPCOM buffers, host/VF mailboxes, active function IDs, VM busy maps, and per-scheduler command/status blocks. The generated field names `FUNCTINO_ID` and `NEXT_FUNCTINO_ID` are misspelled in the header and therefore part of the ABI seen by C users.
- `UVD_JPEG_*`, `JPEG_DEC_*`, `UVD_JPEG_ENC_*`, `JPEG_ENC_*`: JPEG decode and encode control, command submission, address layout, pitch/base, soft reset, scratch, and engine idle/status masks.
- `UVD_JRBC_*` and `UVD_JRBC_ENC_*`: JPEG ring-buffer and indirect-buffer command processor controls, including read/write pointers, buffer-valid diagnostics, conditional read retry/timeout fields, illegal-command/memory-timeout/trap/preempt status bits, and preemption fence registers.
- `UVD_JMI_*`, `UVD_LMI_*`: memory-client setup for JPEG decode/encode, VMIDs, 64-bit BAR halves, endian/swap controls, arbitration and burst settings, and perfmon counters.
- `JPEG_SYS_INT_*`, `JPEG_MASTINT_EN`, `JPEG_IH_CTRL`: JPEG interrupt routing, status, acknowledgement, master enable, overrun reset/status, IH VMID/user data/ring ID, and arbitration drop controls. `jpeg_v2_5.c` uses `JPEG_SYS_INT_EN__DJRBC_MASK` for interrupt setup.
- `JPEG_CGC_*`, `JPEG_*_CGC_MEM_CTRL`, `UVD_CGC_*`, `UVD_SUVD_CGC_*`: clock-gating, dynamic clock mode, block active status, and memory light/deep/shutdown controls for JPEG, UVD, and SUVD sub-blocks.
- `UVD_PGFSM_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_DPG_*`: power-gating configuration/status, DPG-mode stalling, LMA SRAM indirect access, pause/ack sequencing, and DPG VCPU cache addressing. `vcn_v2_5.c` uses `UVD_POWER_STATUS__*` and `UVD_PGFSM_CONFIG__UVDM_UVDU_PWR_ON` around power transitions.
- `UVD_VCPU_INT_*`, `UVD_SYS_INT_*`, `UVD_MASTINT_EN`, `UVD_GPCOM_*`: firmware/system mailbox commands, interrupt enable/ack/status, interrupt routing, and master interrupt gating.
- `UVD_RB_BASE_*`, `UVD_RB_SIZE*`, `UVD_RB_RPTR*`, `UVD_RB_WPTR*`, `UVD_OUT_RB_*`: decode ring-buffer address and pointer fields, including four input rings and one output ring.

## Control Flow and State Behavior

There are no functions, branches, or data structures in this header. Runtime behavior emerges when the VCN 2.5 and JPEG 2.5 driver code applies these constants to hardware registers:

- Initialization and reset flows write soft-reset masks, clock-gating masks, power-gating FSM fields, and ring-buffer base/size/pointer fields.
- Command-submission flows update RB/IB write pointers and poll status/job-done bits exposed by `UVD_STATUS`, `UVD_JRBC_STATUS`, `UVD_JRBC_ENC_STATUS`, and related interrupt status registers.
- Power-management flows use `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_PGFSM_CONFIG`, `UVD_PGFSM_STATUS`, `UVD_DPG_PAUSE`, and DPG LMA/cache masks to enter/exit gated modes without racing active engines.
- Virtualization flows use MMSCH VF context address/size/VMID/mailbox fields and GPU IOV command/status fields. In `vcn_v2_5.c`, the driver programs `mmMMSCH_VF_CTX_ADDR_LO/HI`, `mmMMSCH_VF_VMID`, `mmMMSCH_VF_CTX_SIZE`, and mailbox registers using masks from this header.
- Interrupt flows enable, route, read, and acknowledge VCPU, SYS, JPEG SYS, JPEG master, and JPEG encoder interrupts. Incorrect pairing of enable/status/ack masks can leave interrupts stuck or dropped.

The state represented here is exclusively hardware state: MMIO register bits, SRAM indices/data ports, VMID bindings, physical/GPU address halves, ring pointers, busy/status bits, interrupt latches, and power/clock gating state. The header itself persists no state and allocates no memory.

## Dependencies and Integration Points

This header depends on the generated AMD register naming convention and on the companion VCN 2.5 address header (`vcn_2_5_offset.h`) for `mm*` register offsets. It is consumed by amdgpu ASIC-specific implementation files, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c`, which includes the header and uses masks for UVD clock gating, power gating, interrupts, ring arbitration, GPCOM registers, MMSCH initialization, and ring setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.c`, which includes the header and uses JPEG interrupt masks such as `JPEG_SYS_INT_EN__DJRBC_MASK`.
- Shared amdgpu MMIO and DPG helpers that expect masks to be already shifted and shifts to be raw bit positions.

The chunk also mirrors many register families present in other VCN generations. That makes it easy to compare with `vcn_4_*_sh_mask.h` or older UVD headers, but values must not be mechanically copied across ASIC generations because field positions and field availability vary.

## Risks and Edge Cases

- This is generated hardware-contract data. A single wrong mask or shift can silently program the wrong bit, causing hangs, power-transition failures, lost interrupts, page faults, or ring-buffer corruption.
- The chunk ends at line 2543 in the middle of `UVD_RB_ARB_CTRL`; later masks for that register are in the next chunk and must be merged before any full-file conclusion about that register.
- Some macro spellings appear generated from hardware descriptions, including `FUNCTINO_ID`. Callers must use the exact generated names; "fixing" the spelling in only one file would break builds.
- Address and size low fields are often aligned, for example ring/JPEG base lows use shifts such as 6 and masks ending in `C0`. Callers must pass appropriately aligned addresses or they will lose low bits.
- Several fields represent write-one-to-clear or acknowledgement semantics (`*_ACK`, `*_CLEAR`, page-fault clear bits, overrun reset). Generic read-modify-write without understanding register semantics can clear pending events.
- Power/clock-gating masks interact with busy/status bits. Clearing clock or power without observing busy/idle fields can strand firmware or engines in reset/gated states.
- VMID and BAR fields split 64-bit addresses and memory-domain identity across multiple registers. Misordered writes or stale high halves can redirect JPEG/JRBC/VCPU memory accesses.

## Test and Validation Signals

Useful validation is mostly build-time and hardware/driver runtime oriented:

- Compile coverage of `vcn_v2_5.c` and `jpeg_v2_5.c` catches missing or renamed macros.
- Static checks should verify each register field has consistent `__SHIFT` and `_MASK` pairs and that masks match the declared bit positions for generated data.
- Runtime smoke signals include successful VCN firmware boot, MMSCH mailbox response becoming nonzero during initialization, ring test jobs completing, JPEG decode/encode job-done interrupts firing and acknowledging, no persistent `*_ILLEGAL_CMD`, `*_MEM_*_TIMEOUT`, NACK, or page-fault status bits, and clean suspend/resume or DPG transitions.
- Power-management validation should poll the relevant `UVD_PGFSM_STATUS`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `JPEG_CGC_STATUS`, `UVD_CGC_STATUS`, and `UVD_SUVD_CGC_STATUS` fields before and after gating.
- Interrupt validation should pair enable/status/ack masks for VCPU, SYS, JPEG SYS, and JPEG encoder paths and confirm no overrun bits remain after acknowledgement.

## Unresolved Cross-Chunk References

This report covers only lines 1-2543. The next chunk is required to complete `UVD_RB_ARB_CTRL` and the remainder of the `uvd0_uvddec` block, including any additional ring, decode, memory, semaphore, or firmware interface masks that follow.

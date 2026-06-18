# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_3_0_0_sh_mask.h lines 1-2565

## Scope

This chunk covers the beginning of the generated AMD VCN 3.0.0 shift/mask header. It starts with the file license and include guard, then defines 32-bit bitfield constants for 11 address blocks:

- `uvd0_mmsch_dec`
- `uvd0_jpegnpdec`
- `uvd0_uvd_jpeg_enc_dec`
- `uvd0_uvd_jpeg_enc_sclk_dec`
- `uvd0_uvd_jrbc_dec`
- `uvd0_uvd_jrbc_enc_dec`
- `uvd0_uvd_jmi_dec`
- `uvd0_uvd_jpeg_common_dec`
- `uvd0_uvd_jpeg_common_sclk_dec`
- `uvd0_uvd_pg_dec`
- the start of `uvd0_uvddec`

The chunk ends inside the `UVD_SOFT_RESET` field list in `uvd0_uvddec`, after `UVD_SOFT_RESET__LBSI_VCLK_RESET_STATUS_MASK`; the remaining reset-status masks and later VCN decode/register blocks continue in the next chunk.

This file section is a generated hardware register ABI map. It defines preprocessor constants only. There are no C functions, structs, variables, allocations, locks, or executable control-flow statements in the covered lines.

## Purpose

The header provides bit positions and masks for VCN 3.0.0 UVD/JPEG/MMSCH registers used by AMDGPU. Each field follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in a 32-bit register value.

Consumers combine these macros with the matching VCN 3.0.0 offset/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The offset header supplies the register address; this header supplies the bit layout used to compose writes and decode reads.

## Important Macro Families

### MMSCH and Virtualization Scheduler

`uvd0_mmsch_dec` maps the multimedia scheduler control surface. It includes microcode and SRAM access registers (`MMSCH_UCODE_ADDR/DATA`, `MMSCH_SRAM_ADDR/DATA`), SRAM layout registers for VFs, doorbells, and context storage, and `MMSCH_CTL` runstall/reset/lock bits.

The same block exposes virtualization state:

- VF VMID and context/GPCOM address/size registers.
- Host and VF mailbox data/response registers.
- GPUIOV scheduler blocks 0 through 2 with command type, execute, interrupt-enable, active-function, busy-status, and data-word fields.
- Per-instance VFID FIFO head/tail fields, NACK status, scratch registers, and VM busy status fields.

These fields are integration points for SR-IOV or other GPU virtualization flows where a PF, VF, firmware scheduler, and host driver coordinate command dispatch and context ownership.

### JPEG Decode and Encode Engines

`uvd0_jpegnpdec` describes the JPEG decode engine. It covers request control, ring-buffer base/read/write/size fields, decode count, picture width/height, chroma format, timer control, interrupt enable/status bits, tier configuration, output buffer pointers, pitch fields, GFX10 tiling/address configuration, GPCOM command/data, indexed data access, scratch state, and decoder soft reset/status.

The JPEG encode blocks split across `uvd0_uvd_jpeg_enc_dec` and `uvd0_uvd_jpeg_enc_sclk_dec`. They cover:

- Encode byte count and interrupt enable/status bits for huff/scaler/fence/error events.
- Pixel padding, restart marker control, and engine enables for huffman, scalar, encode, compare, and restricted ECS writes.
- Scalar destination width/height, chroma offsets, scalar pitch, and scratch registers.
- Huffman and quantization table read/write controls and table data/index registers.
- Source picture dimensions, pitch, luma/chroma base addresses, GFX10 tiling/address mode, GPCOM command/data, clock-gating control, and encoder soft reset/status.

Together these macros define the software-visible register contract used to submit JPEG jobs, configure image layout, program tables, track completion/errors, and reset decode or encode subblocks.

### JRBC Command Processors

`uvd0_uvd_jrbc_dec` and `uvd0_uvd_jrbc_enc_dec` define matching ring-buffer command processor blocks for JPEG decode and JPEG encode. Each block has ring write/read pointers, ring control, indirect-buffer size and remaining-size fields, urgent read-priority controls, conditional-read retry timers, reference data, soft reset, status/error bits, ring/IB buffer status, preemption command bits, preemption fence data, ring size, and scratch state.

The status fields distinguish RB and IB job completion, illegal command, conditional register-read timeout, memory read/write timeout, trap status, preemption status, interrupt enable, and interrupt acknowledge. These masks are important for queue bring-up, hang detection, preemption, and interrupt handling.

### JMI, MCIF, Memory Protection, and VMID Mapping

`uvd0_uvd_jmi_dec` maps the JPEG memory interface. It includes urgent-control and arbitration fields for JPEG decode, JPEG encode, JRBC, encoder JRBC, EJPEG, and scaler paths; read/write maximum burst and swap controls; drop controls for JPEG/JRBC/EJPEG/scaler paths; and page-fault handling gates for decoder, encoder, and second decoder.

Security and isolation related fields in this block include:

- Memcheck clamping enables and safe-address registers.
- VMID assignment fields for JRBC RB/IB, JPEG read/write, encoder JRBC, encoder JPEG pixel/bitstream/scaler/fence, and preemption fence writes.
- Many 64-bit BAR low/high pairs for JPEG read/write, preemption fence, JRBC RB/IB, memory read/write, encoder pixel/bitstream/scaler paths, and atomic users.
- Decode and encode memory-swap controls.
- Atomic write arbitration, drop, clamping, urgent, gate, and byte-swap fields.

The block also exposes latency/performance counters and `UVD_JMI_CLEAN_STATUS`, which reports whether read/write paths are idle or pending. Driver code typically uses these fields during memory-interface setup, reset quiesce, virtualization setup, and diagnostics.

### JPEG Common Interrupts, Reset, Clock Gating, and Performance

`uvd0_uvd_jpeg_common_dec` defines shared JPEG reset-status fields, system interrupt enable/status/ack bits, memcheck system interrupt enable/status/ack bits, active PF/VF identification, master interrupt overrun fields, interrupt-handler metadata (`IH_VMID`, user data, ring id), and JRBBM arbitration drop controls.

`uvd0_uvd_jpeg_common_sclk_dec` defines clock and memory power controls for the JPEG complex: `JPEG_CGC_GATE`, `JPEG_CGC_CTRL`, `JPEG_CGC_STATUS`, common/JPEG/JPEG2/encoder CGC memory controls, a second soft reset bit for atomic, and four-bank performance counter selection/count registers.

These fields connect the JPEG subblocks to AMDGPU's interrupt, reset, clock-gating, and performance-monitoring paths.

### Power Gating, Firmware, Fault, and Feature Registers

`uvd0_uvd_pg_dec` maps VCN power-management and firmware-visible state. It includes power-gating FSM configuration/status for many UVD subblocks, global UVD/JPEG power status, JPEG memory-controller read/write space, DPG local-memory access control/data/mask, DPG pause request/ack fields, scratch registers, a free counter, DPG VCPU cache BAR/offset/VMID fields, and register filter/security privilege enables.

Fault and firmware reporting fields include VCPU error detection low/high bounds, error status/clear/detect/reset-on-fault bits, faulting instruction address, page-fault status/clear bits for JPEG, non-JPEG, encoder paths, atomic users, and JPEG2, firmware version, DPG clock-enable VCPU report, and security register violation reports.

The block also exposes non-cache/atomic memory spaces, GFX10 address configuration, general-purpose counters 2 and 3, VCLK/DCLK deep-sleep controls, timestamp counter lower/upper registers, `VCN_FEATURES` capability flags such as video decode/encode, MJPEG decode/encode, virtualization, VP9, AV1, EFC, dual MJPEG decode, and `UVD_GPUIOV_STATUS`.

### Start of Core UVD Decode Block

The start of `uvd0_uvddec` covers core VCN/UVD status and reset state. `UVD_STATUS` reports RBC busy, VCPU report bits, RBC GPCOM access, and system GPCOM request. `UVD_ENC_PIPE_BUSY` exposes many encoder pipeline busy bits for IME, SMP, SIT, SDB, entropy/header, LCM, MDM, MIF, BSP/BSD, and SAOE paths. `UVD_FW_POWER_STATUS` reports firmware power-off state for UVD subblocks. `UVD_CNTL` exposes selected control bits such as SUVD enable and safe-sync disable.

The chunk then begins `UVD_SOFT_RESET`, defining reset request bits for RBC, LBSI, LMI, VCPU, UDEC, CXW, TAP, MPC, EFC, IH, MPRD, IDCT, LMI UMC, SPH, MIF, LCM, and SUVD, plus the first reset-status masks. The rest of this register is outside the chunk.

## Control Flow and State Behavior

There is no runtime control flow in this header. Its behavior is compile-time substitution of constants into driver code that reads and writes memory-mapped hardware registers.

The state represented here is hardware and firmware-visible state, not software-owned state in the header. It includes scheduler SRAM, microcode access, VF mailbox/context state, JPEG ring buffers, JPEG encode/decode configuration, command processor queues, interrupt status/ack bits, page-fault and memcheck status, reset status, power-gating state, clock-gating state, performance counters, firmware reports, and feature flags.

Some fields are configuration fields expected to persist until reset or reprogramming, such as VMIDs, BAR high/low halves, tiling modes, address modes, pitch/base registers, power/clock gating settings, memcheck clamping, register filter privileges, and feature/control bits. Other fields are transient or command-like, such as write pointers, job-done bits, interrupt ack bits, soft reset bits, preemption commands, table write/read bits, page-fault clear bits, pause request/ack bits, and VCPU error clear bits. Correct sequencing, polling, write-one-to-clear behavior, and timeouts are defined by hardware documentation and consuming AMDGPU code, not by the masks alone.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `vcn_3_0_0_offset.h` supplies matching register offsets and base indices.
- `vcn_3_0_0_default.h`, where present, supplies reset/default values.
- AMDGPU SOC15 register access helpers and field helper macros consume the `__SHIFT` and `_MASK` constants.

Likely integration points in the source tree include:

- VCN 3.0 initialization, suspend/resume, power-gating, clock-gating, and reset code.
- JPEG decode/encode queue setup, ring pointer management, IB submission, preemption, and hang recovery.
- Firmware scheduler and GPUIOV/SR-IOV setup paths that configure MMSCH, VF context, mailboxes, VMIDs, and active function state.
- Interrupt handling for JPEG, JRBC, memcheck, page faults, VCPU events, and master interrupt overrun.
- Memory-interface setup that programs BAR low/high pairs, address modes, swap controls, tiling, VMIDs, atomic spaces, and safe-address clamping.
- Diagnostics and telemetry paths that read busy bits, clean status, latency/performance counters, timestamp counters, firmware version, power state, and feature flags.

The macros are ASIC-version specific. Mixing this mask header with a different VCN generation's offsets or defaults can silently write wrong bits.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can corrupt hardware programming, break JPEG jobs, mis-handle interrupts, or write reserved bits in reset/power/security registers.
- Virtualization fields are privilege-sensitive. Incorrect MMSCH, GPUIOV, VF mailbox, active-function, VMID, context, or BAR programming can break PF/VF isolation or scheduler ownership.
- Address and VMID fields are security-sensitive. Incorrect 64-bit BAR halves, safe-address registers, memcheck clamping, page-fault controls, atomic spaces, or register filters can cause memory corruption or expose protected surfaces.
- Reset and power-management fields require strict ordering. Misusing soft-reset bits, reset-status polling, DPG pause/ack, clean-status checks, or clock-gating controls can leave VCN/JPEG blocks hung or partially powered.
- Repetitive decode/encode and JRBC macro families are easy to copy incorrectly. Decode vs encode, JPEG vs JPEG2, DJRBC vs EJRBC, and low vs high BAR halves must not be crossed.
- This chunk stops mid-register at `UVD_SOFT_RESET`; any complete analysis or modification of that register must include the next chunk before drawing conclusions about all status masks.

## Test Signals

Useful validation signals for consumers of these macros include:

- Build coverage for files that include `vcn_3_0_0_sh_mask.h` with the matching VCN 3.0.0 offset/default headers.
- Successful VCN initialization and firmware load without register access violations.
- JPEG decode and encode ring bring-up, pointer movement, job completion interrupts, and correct fence signaling.
- Preemption and reset recovery tests that exercise JRBC status bits, soft reset, reset-status polling, and clean-status polling.
- SR-IOV/GPUIOV tests that verify VF mailbox exchange, active function selection, VMID routing, and memcheck behavior.
- Power-management tests across suspend/resume, DPG entry/exit, clock gating, and deep-sleep controls.
- Fault-injection or negative tests for page faults, memcheck high/low errors, VCPU error reporting, and interrupt ack/clear paths.

# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_3_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003452`: lines 1-2565, `Docs/researches/chunks/subset-b-003452_research.md`
- `subset-b-003453`: lines 2566-5084, `Docs/researches/chunks/subset-b-003453_research.md`
- `subset-b-003454`: lines 5085-5530, `Docs/researches/chunks/subset-b-003454_research.md`

## Chunk Research

### subset-b-003452: lines 1-2565

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

### subset-b-003453: lines 2566-5084

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_3_0_0_sh_mask.h lines 2566-5084

## Scope

This chunk covers the middle-to-late portion of the generated AMD VCN 3.0.0 shift/mask header. It starts at `UVD_SOFT_RESET2` immediately after the `UVD_SOFT_RESET` definitions from the previous chunk and runs through the `UVD_MEMCHECK_SYS_INT_STAT` low/high error status masks. The physical source file continues after this work item with `UVD_MEMCHECK_SYS_INT_ACK` and later register definitions, so this document intentionally describes only the line range mapped to `subset-b-003453`.

The file is a C preprocessor hardware register field map. It contains no executable functions, structs, enums, allocation, locking, or local storage. Its contract is the exact `__SHIFT` and `_MASK` macro values used with AMDGPU register helpers for VCN 3.0 decode, encode, firmware, memory-interface, clock-gating, reset, interrupt, and context-indirect registers.

## Purpose

`vcn_3_0_0_sh_mask.h` is the bitfield companion to `vcn_3_0_0_offset.h`. The offset header names the MMIO registers; this header names the bit positions and masks inside those registers. Runtime code in the VCN and JPEG 3.0 drivers combines both headers through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `WREG32_P`, `RREG32_SOC15`, `SOC15_REG_OFFSET`, `SOC15_WAIT_ON_RREG`, `WREG32_SOC15_DPG_MODE`, and SR-IOV MMSCH table builders.

This chunk is centered on VCN runtime control:

- soft-reset and clock-gating controls for VCN sub-blocks;
- general-purpose firmware command/data mailboxes;
- interrupt enable/status/ack fields for decoder, encoder, SUVD, and system interrupt paths;
- decode and encode ring-buffer base/size/read/write pointer registers;
- VCPU cache and non-cache window layout for firmware, stack, context, and shared memory;
- MPC, RBC, LMI, and context-indirect registers used to start, stop, pause, and resume VCN;
- memory deep-sleep/shutdown controls, software scratch registers, and memcheck interrupt status.

## Important Macro Families

The reset and clock-gating families at the start of the chunk define the basic control surface used during VCN start/stop:

- `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, and `UVD_WIG_CTRL` expose atomic, MMSCH, TAP, WIG, AVM, and ACAP reset bits plus reset status bits.
- `UVD_CGC_GATE`, `UVD_CGC_STATUS`, `UVD_CGC_CTRL`, and `UVD_CGC_UDEC_STATUS` describe clock gates, dynamic clock mode, gate/off delays, mode bits, and per-subblock status for SYS, UDEC, MPEG2, REGS, RBC, LMI, IDCT, MPRD, MPC, LBSI, LRBBM, WCB, VCPU, and MMSCH.
- `UVD_SUVD_CGC_GATE`, `UVD_SUVD_CGC_STATUS`, `UVD_SUVD_CGC_CTRL`, plus the later `UVD_SUVD_CGC_STATUS2` and `UVD_SUVD_CGC_GATE2` definitions cover scalable-video and codec-specific blocks including SRE, SIT, SMP, SCM, SDB, SCLR, ENT, IME, HEVC/VP9/AV1/FBC/EFC/SAOE paths, MPBE, and MPC1.

The firmware command and interrupt families define communication between host, VCN firmware, and interrupt handlers:

- `UVD_GPCOM_VCPU_CMD`, `UVD_GPCOM_VCPU_DATA0`, `UVD_GPCOM_VCPU_DATA1`, `UVD_GPCOM_SYS_CMD`, `UVD_GPCOM_SYS_DATA0`, and `UVD_GPCOM_SYS_DATA1` expose 32-bit firmware command/data payload fields.
- `UVD_VCPU_INT_EN`, `UVD_VCPU_INT_STATUS`, `UVD_VCPU_INT_ACK`, `UVD_VCPU_INT_ROUTE`, `UVD_SUVD_INT_*`, `UVD_ENC_VCPU_INT_*`, `UVD_MASTINT_EN`, `UVD_SYS_INT_*`, and the second SUVD interrupt bank provide bitfields for firmware-to-host, system-message, encoder, decoder, watchdog, and memory-fault signaling.
- `UVD_DRV_FW_MSG` and `UVD_FW_DRV_MSG_ACK` are simple message/acknowledgement payload registers.
- `UVD_JOB_DONE`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CONTEXT_ID2`, and `UVD_NO_OP` support ring commands and test/diagnostic command streams.

The ring-buffer families name the fields for decoder, encoder, output, and audio queues:

- `UVD_RB_BASE_LO/HI`, `UVD_RB_SIZE`, `UVD_RB_RPTR`, and `UVD_RB_WPTR`, repeated through queue 4, are the main encode ring register banks.
- `UVD_OUT_RB_*` and `UVD_AUDIO_RB_*` provide additional firmware output/audio queue windows.
- `UVD_RB_ARB_CTRL` controls arbitration and VCPU access behavior, including the `VCPU_DIS` bit used to block/unblock firmware register access.
- `UVD_IOV_ACTIVE_FCN_ID`, `UVD_IOV_MAILBOX`, and `UVD_IOV_MAILBOX_RESP` expose virtualization mailbox state for SR-IOV flows.

The `uvd0_ecpudec` block names the VCPU memory windows and controls:

- `UVD_VCPU_CACHE_OFFSET0..8` and `UVD_VCPU_CACHE_SIZE0..8` define cacheable firmware-visible windows.
- `UVD_VCPU_NONCACHE_OFFSET0/1` and `UVD_VCPU_NONCACHE_SIZE0/1` define non-cacheable firmware/shared-memory windows.
- `UVD_VCPU_CNTL`, `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, `UVD_VCPU_IND_INDEX`, and `UVD_VCPU_IND_DATA` provide clock/reset, timeout, processor identity, trace, and indirect-access fields.

The `uvd0_uvd_mpcdec` block defines media-pipeline composition controls:

- `UVD_MP_SWAP_CNTL` and `UVD_MP_SWAP_CNTL2` control endianness and swap behavior for multiple decode paths.
- `UVD_MPC_LUMA_*` and `UVD_MPC_CHROMA_*` expose search/hit/hit-pending state for luma and chroma paths.
- `UVD_MPC_CNTL`, `UVD_MPC_PITCH`, `UVD_MPC_SET_MUXA*`, `UVD_MPC_SET_MUXB*`, `UVD_MPC_SET_MUX`, and `UVD_MPC_SET_ALU` define replacement mode, pitch, mux selection, and ALU fields used during hardware initialization.
- `UVD_MPC_PERF0/1` and `UVD_MPC_IND_INDEX/DATA` expose performance and indirect register access.

The `uvd0_uvd_rbcdec` block defines the ring-buffer controller and semaphore interface:

- `UVD_RBC_IB_SIZE`, `UVD_RBC_IB_SIZE_UPDATE`, `UVD_RBC_RB_CNTL`, `UVD_RBC_RB_RPTR_ADDR`, `UVD_RBC_RB_RPTR`, `UVD_RBC_RB_WPTR`, `UVD_RBC_RB_WPTR_CNTL`, `UVD_RBC_WPTR_STATUS`, `UVD_RBC_WPTR_POLL_CNTL`, and `UVD_RBC_WPTR_POLL_ADDR` are used to put the decode ring into an idle/no-fetch state, program the ring buffer, and manage read/write pointer updates.
- `UVD_RBC_VCPU_ACCESS`, `UVD_FW_SEMAPHORE_CNTL`, `UVD_SEMA_*`, and semaphore timeout registers expose firmware semaphore command, address, signal/wait, timeout, and incomplete/fault status.
- `UVD_ENGINE_CNTL`, `UVD_JOB_START`, `UVD_RBC_BUF_STATUS`, and `UVD_RBC_SWAP_CNTL` provide engine control, job start, buffer status, and swap fields.

The `uvd0_lmi_adpdec` block dominates the latter half of the chunk. It defines low/high 64-bit BAR fields for many VCN memory clients: RE, IT, MP, CM, DB, DBW, IDCT, MPRD, MPC, RBC RB/IB, LBSI, VCPU cache/non-cache windows, CENC, SRE, MIF luma/chroma/ref/DBW/coloc/BSP/BSD/scaler/privacy/image-paste paths, MMSCH non-cache windows, and SPH. It also defines VMID, arbiter, latency, status, urgent, coherency, credit, prefetch, performance, and indirect-access registers such as `UVD_LMI_MMSCH_NC_VMID`, `UVD_LMI_MMSCH_CTRL`, `UVD_MMSCH_LMI_STATUS`, `UVD_ADP_ATOMIC_CONFIG`, `UVD_LMI_ARB_CTRL2`, `UVD_LMI_VCPU_CACHE_VMIDS_MULTI`, `UVD_LMI_VCPU_NC_VMIDS_MULTI`, `UVD_LMI_LAT_CTRL`, `UVD_LMI_CTRL2`, `UVD_LMI_URGENT_CTRL`, `UVD_LMI_CTRL`, `UVD_LMI_STATUS`, `UVD_LMI_PERFMON_*`, `UVD_LMI_ADP_SWAP_CNTL`, `UVD_LMI_RBC_RB_VMID`, `UVD_LMI_RBC_IB_VMID`, `UVD_LMI_MC_CREDITS`, `UVD_LMI_ADP_IND_*`, `UVD_LMI_ADP_PF_EN`, `UVD_LMI_ADP_CNN_CTRL`, and `UVD_LMI_PREF_CTRL`.

The final `uvdctxind` block in this chunk covers context-indirect state:

- `UVD_CGC_MEM_CTRL`, `UVD_CGC_CTRL2`, `UVD_CGC_MEM_DS_CTRL`, and `UVD_CGC_MEM_SD_CTRL` control memory clock gating, deep sleep, and shutdown for LMI, MPC, MPRD, WCB, UDEC, SYS, VCPU, MIF, LCM, MMSCH, and MPC1 memory slices.
- `UVD_SW_SCRATCH_00` through `UVD_SW_SCRATCH_15` are raw 32-bit software/firmware scratch registers.
- `UVD_MEMCHECK_SYS_INT_EN` exposes enables for low/high read/write and MIF client errors.
- `UVD_MEMCHECK_SYS_INT_STAT` begins the corresponding low/high status bitmap and is cut by this work item before the later acknowledgement definitions.

## Control Flow

There is no local control flow in the header. Runtime flow is in consumers, primarily `drivers/gpu/drm/amd/amdgpu/vcn_v3_0.c`, with `drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.c` also including this generated header for shared VCN/JPEG register definitions.

The main `vcn_v3_0.c` flow is:

1. Early/software init includes this header and `vcn_3_0_0_offset.h`, registers VCN hardware registers for debugfs/diagnostics, initializes rings, sets internal/external command offsets, and wires IRQ source IDs.
2. Firmware memory setup writes LMI BAR low/high registers and VCPU cache/non-cache offsets/sizes for firmware, stack, context, and `struct amdgpu_fw_shared`. This uses fields such as `UVD_VCPU_CACHE_OFFSET*`, `UVD_VCPU_CACHE_SIZE*`, and LMI BAR registers from this chunk.
3. Clock-gating setup reads and writes `mmUVD_CGC_CTRL`, `mmUVD_CGC_GATE`, `mmUVD_SUVD_CGC_GATE`, `mmUVD_SUVD_CGC_GATE2`, and `mmUVD_SUVD_CGC_CTRL` using the `UVD_CGC_*` and `UVD_SUVD_CGC_*` masks in this chunk. Disable paths clear mode/gate masks and wait for gates to open; enable paths set mode masks again before power gating.
4. Start paths program LMI coherency and stall controls, configure MPC replacement/mux fields, unblock VCPU register access through `UVD_RB_ARB_CTRL`, release VCPU reset via `UVD_VCPU_CNTL`, wait for firmware response in `UVD_STATUS`, enable `UVD_MASTINT_EN__VCPU_EN_MASK`, and initialize decode/encode rings through `UVD_RBC_RB_CNTL`, `UVD_RBC_RB_RPTR/WPTR`, `UVD_LMI_RBC_RB_64BIT_BAR_*`, and `UVD_RB_*`.
5. Dynamic power-gating start uses the same register fields through `WREG32_SOC15_DPG_MODE` and optional indirect SRAM programming. `vcn_v3_0_pause_dpg_mode()` later uses `UVD_DPG_PAUSE`, `UVD_POWER_STATUS`, and the ring-base/pointer fields from this chunk to pause, restore ring state, and unstall DPG.
6. SR-IOV start builds an MMSCH initialization table using direct write and direct read-modify-write packets. The table programs VCPU cache windows, encode/decode ring buffers, RBC control fields, and MMSCH mailbox/VMID state before waiting for an MMSCH mailbox response.
7. Stop paths wait for ring pointers and LMI clean status, stall the UMC arbiter, block VCPU register access, reset and clock-disable VCPU, assert LMI soft-reset bits, clear status, and re-enable clock/power gating.

The macros in this chunk are therefore part of several control paths: bare-metal bring-up, DPG bring-up, DPG pause/resume, SR-IOV guest/VF MMSCH initialization, normal stop, and debug/test ring operation.

## State and Persistence Behavior

The header itself stores no software state. It describes stateful hardware registers whose lifetime is controlled by VCN firmware, PSP firmware loading, power-gating domains, SR-IOV virtualization, GPU reset, and ring scheduling:

- Reset fields affect reset state for VCPU, LMI, UDEC, MPC, MPRD, IDCT, MIF, LCM, SUVD, MMSCH, and related sub-blocks. Status bits report whether some clock/reset domains are still asserted.
- Clock-gating fields persist in VCN hardware until rewritten by start/stop or power-management paths. The driver toggles these fields depending on `adev->cg_flags` and `adev->pg_flags`.
- Ring registers hold GPU addresses, sizes, read pointers, and write pointers for decoder and encoder queues. Software mirrors some of this state in `struct amdgpu_ring` and `struct amdgpu_fw_shared`, and must keep those mirrors synchronized with hardware.
- VCPU cache/non-cache and LMI BAR registers map firmware-visible GPU memory. They depend on whether firmware is loaded by PSP into TMR memory or from the driver-owned VCN BO.
- LMI coherency, urgent, credit, latency, prefetch, and VMID registers determine memory-interface behavior for active VCN clients. The header does not encode reset defaults or retention rules.
- Interrupt enable/status/ack registers are hardware-latched or firmware-driven. The header only provides bit positions; clear-on-write, write-one-to-clear, and routing semantics come from the programming model and consumer code.
- Scratch registers are 32-bit firmware/software mailboxes or diagnostics. The chunk does not define ownership of each scratch index.
- Memcheck status bits are hardware error state for internal clients. This chunk includes enable and status fields but not the ack fields that begin after the chunk boundary.

## Dependencies and Integration Points

Direct includes found in this tree:

- `drivers/gpu/drm/amd/amdgpu/vcn_v3_0.c`
- `drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.c`

The primary companion header is `drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_3_0_0_offset.h`, which supplies `mm...` register names and base indices. This chunk also shares naming and behavior patterns with VCN 2.x, 4.x, and 5.x generated headers, allowing common AMDGPU code to use stable field names where hardware kept compatible register layouts.

Key integration points:

- AMDGPU SOC15 register access: `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_WAIT_ON_RREG`.
- Bitfield helpers: `REG_SET_FIELD` and field-specific masks/shifts from this header.
- VCN firmware interface: `amdgpu_vcn_resume`, `amdgpu_vcn_setup_ucode`, `struct amdgpu_fw_shared`, firmware queue reset flags, firmware command/data registers, and VCPU cache windows.
- Ring scheduling: `struct amdgpu_ring`, decode ring `ring_dec`, encode rings `ring_enc[]`, doorbells, RBC read/write pointers, and VM hub selection.
- Power management: `amdgpu_dpm_enable_vcn`, `AMD_PG_SUPPORT_VCN`, `AMD_PG_SUPPORT_VCN_DPG`, `AMD_CG_SUPPORT_VCN_MGCG`, static power gating, dynamic power gating, and DPG SRAM programming.
- Interrupt handling: `amdgpu_irq_add_id`, VCN interrupt source IDs, master interrupt enable, VCPU/SUVD/encoder/system interrupt fields.
- SR-IOV: `amdgpu_sriov_vf`, MMSCH 3.0 command table structures/macros, MMSCH VF context address/size/mailbox registers, and guest-visible VCN ring setup.
- JPEG 3.0: the JPEG block includes the same generated VCN headers because JPEG registers and interrupt sources live under the VCN register namespace for this generation, though most chunk-specific fields are used by the VCN decode/encode path rather than JPEG decode setup.

## Risks

- Hardware ABI drift is the dominant risk. These generated constants must match VCN 3.0.0 exactly. A wrong mask or shift can silently write the wrong hardware bit, causing hangs, missed interrupts, memory corruption, or power-management failures.
- The chunk contains many full-width `0xFFFFFFFFL` data masks and many one-bit control masks. Mixing a field mask with a raw register value, or applying a mask from the wrong VCN generation, can clobber unrelated state.
- Clock-gating and power-gating fields are timing sensitive. `vcn_v3_0.c` waits for status changes and performs read-backs to order writes; missing those barriers in new consumers can produce intermittent bring-up, DPG pause, or shutdown failures.
- Ring pointer state is mirrored in both hardware and `fw_shared`. During DPG pause/resume or SR-IOV initialization, failing to reset queue mode flags around register writes can leave firmware observing inconsistent read/write pointers.
- Address fields are split into low/high 32-bit BARs and several offsets are in hardware-specific units. Incorrect low/high pairing, missing `upper_32_bits`, or wrong firmware-offset shifts can map VCPU firmware, stack, context, or shared memory incorrectly.
- SR-IOV MMSCH setup is indirect and mailbox-driven. If table offsets, table sizes, VMID fields, or mailbox response expectations are wrong, failures surface as initialization timeouts rather than compile errors.
- Some status/ack families are split across chunk boundaries. This chunk includes `UVD_MEMCHECK_SYS_INT_EN` and the beginning of `UVD_MEMCHECK_SYS_INT_STAT`; the associated `UVD_MEMCHECK_SYS_INT_ACK` definitions are outside this work item.
- Generated repetition is review-hostile. Suffix mistakes such as using queue 1 fields for queue 2, or confusing `UVD_RB_*` encode rings with `UVD_RBC_*` decode ring-controller fields, can compile cleanly while breaking only a specific queue or mode.

## Test Signals

Useful validation signals for code consuming this chunk include:

- Kernel build coverage for `vcn_v3_0.c` and `jpeg_v3_0.c` with `vcn_3_0_0_offset.h` and this shift/mask header.
- VCN firmware boot tests on VCN 3.0 hardware that verify VCPU reaches the expected ready status after cache/non-cache windows, LMI controls, MPC setup, and reset release are programmed.
- Decode and encode ring tests that submit jobs through decode and both encode queues, then verify `UVD_RBC_RB_RPTR/WPTR`, `UVD_RB_RPTR/WPTR`, job completion interrupts, and `fw_shared` queue state stay synchronized.
- Dynamic power-gating tests that start in DPG mode, pause/unpause, reset ring pointers, and confirm DPG pause acknowledgements plus `UVD_POWER_STATUS` transitions.
- Suspend/resume and GPU-reset tests that exercise stop/start sequencing, LMI clean waits, clock-gating re-enable, VCPU reset, and post-reset firmware/ring recovery.
- SR-IOV VF initialization tests that build the MMSCH table, program VCN cache/ring state through MMSCH, and receive the expected mailbox response before command submission.
- Interrupt tests that cover master VCPU interrupts, decoder system-message interrupts, encoder GP interrupts, SUVD interrupt banks, and acknowledgement paths.
- Register-readback diagnostics through AMDGPU debugfs/sysfs register lists for `UVD_CONTEXT_ID`, `UVD_GPCOM_*`, ring bases/sizes/pointers, `UVD_CGC_*`, `UVD_LMI_*`, and RBC control/status registers.
- Fault-injection or hardware diagnostics for memcheck status bits, ensuring enabled error sources surface through the expected `UVD_MEMCHECK_SYS_INT_STAT` low/high error fields and are reconciled with the ack definitions outside this chunk.

### subset-b-003454: lines 5085-5530

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_3_0_0_sh_mask.h lines 5085-5530

## Scope And Purpose

This chunk is the tail of the generated VCN 3.0.0 shift/mask header for the AMDGPU VCN/UVD block. It defines preprocessor constants for the low-level register bit layout of memory-check interrupt status/acknowledge registers and the final `UVD_IH_SEM_CTRL` register. The companion offset header maps the corresponding VCN 3.0 indirect register names to offsets `ixUVD_MEMCHECK_SYS_INT_EN` through `ixUVD_IH_SEM_CTRL` at `0x0014` through `0x001e`; this file supplies the bit positions and masks used to compose or decode the 32-bit register values.

There is no executable logic in this range. Its purpose is ABI-like: C code in the AMDGPU VCN 3.0 and JPEG 3.0 implementation can include `vcn_3_0_0_sh_mask.h` and use stable symbolic field names instead of hard-coded bit arithmetic when enabling memory-check interrupts, reading fault status, acknowledging latched faults, or configuring interrupt-handler/semaphore metadata.

The chunk begins in the middle of the `UVD_MEMCHECK_SYS_INT_STAT` mask block, then covers the full `UVD_MEMCHECK_SYS_INT_ACK`, `UVD_MEMCHECK_VCPU_INT_EN`, `UVD_MEMCHECK_VCPU_INT_STAT`, `UVD_MEMCHECK_VCPU_INT_ACK`, `UVD_MEMCHECK2_SYS_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_ACK`, `UVD_MEMCHECK2_VCPU_INT_STAT`, `UVD_MEMCHECK2_VCPU_INT_ACK`, and `UVD_IH_SEM_CTRL` definitions before closing the header guard.

## Register Field Groups

The first group maps legacy memory-check system interrupt status and acknowledge bits. `UVD_MEMCHECK_SYS_INT_STAT` and `UVD_MEMCHECK_SYS_INT_ACK` use the same low/high bit pairing for VCN client blocks such as `RE`, `IT`, `MP`, `DB`, `DBW`, `CM`, `MIF_REF`, `VCPU`, `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, and `IT_RD`. Each field has a `__SHIFT` value and a matching one-bit `*_MASK`; low/high status and ack fields occupy the same bit locations, including sparse high bits for `IT_RD` at bits 30 and 31.

`UVD_MEMCHECK_VCPU_INT_EN` is the enable register for routing memory-check events to the VCPU interrupt path. Unlike the status/ack registers, it uses one enable bit per error source rather than low/high pairs. It includes the base sources from the system register and adds read-side or second-set sources such as `CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, `LBSI_RD`, `RBC_RD`, `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, and `PREF`. Bits are sparse: for example `IT_RD_ERR_EN` is bit 15, `RBC_RD_ERR_EN` is bit 24, and `PREF_ERR_EN` is bit 29.

`UVD_MEMCHECK_VCPU_INT_STAT` and `UVD_MEMCHECK_VCPU_INT_ACK` mirror the first memory-check status/ack layout for VCPU-visible latched errors. They expose low/high error or acknowledge bits for `RE`, `IT`, `MP`, `DB`, `DBW`, `CM`, `MIF_REF`, `VCPU`, `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, and `IT_RD`.

The `UVD_MEMCHECK2_*` registers provide the second memory-check status/ack bank for additional read-side and extended memory interfaces. `UVD_MEMCHECK2_SYS_INT_STAT` and `UVD_MEMCHECK2_SYS_INT_ACK` cover `CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, `LBSI_RD`, `RBC_RD`, `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, and `PREF`. Their system-visible bit layout differs from the VCPU-visible layout: the system status/ack registers place `MIF_BSP2` and later fields at bits 22 through 31, while `UVD_MEMCHECK2_VCPU_INT_STAT` and `UVD_MEMCHECK2_VCPU_INT_ACK` place `MIF_BSP2` and later fields at bits 18 through 27. This is an important hardware contract and not a typo to normalize away.

`UVD_IH_SEM_CTRL` defines interrupt-handler and semaphore control fields. Single-bit controls are `IH_STALL_EN`, `SEM_STALL_EN`, `IH_STATUS_CLEAN`, and `SEM_STATUS_CLEAN`; packed metadata fields include `IH_VMID` at bits 4-7, `IH_USER_DATA` at bits 8-19, and `IH_RINGID` at bits 20-27. These masks allow the driver or firmware-facing code to describe how VCN interrupt/semaphore events should be identified and whether status should be cleaned.

## Important APIs, Types, And Functions

This chunk exports only C preprocessor macros. There are no C functions, structs, enums, static data objects, or inline helpers. The API surface consists of names following the generated register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift amount for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted 32-bit mask for the field.

Consumers normally combine these macros with the register offsets from `vcn_3_0_0_offset.h` and AMDGPU/SOC15 register helpers. For example, a write path can clear or set `UVD_MEMCHECK_VCPU_INT_EN__PREF_ERR_EN_MASK`, while a decode path can test `UVD_MEMCHECK2_SYS_INT_STAT__PREF_HI_ERR_MASK` after reading `ixUVD_MEMCHECK2_SYS_INT_STAT`.

## Control Flow

There is no runtime control flow in the header itself. Control flow is implicit in how downstream driver code uses these definitions:

1. Program the relevant memory-check interrupt-enable register using the `*_INT_EN` masks.
2. Hardware latches memory-check low/high or source-specific status bits in the `*_INT_STAT` registers.
3. Driver interrupt or diagnostic code reads the status register, decodes set bits using the matching masks, and chooses an error-handling path.
4. Driver code writes the corresponding `*_INT_ACK` mask bits to acknowledge or clear the latched status.
5. Interrupt-handler/semaphore behavior can be configured through `UVD_IH_SEM_CTRL` fields when the VCN block is initialized or reset.

Because the ack and status layouts are intentionally paired within each bank, any handler using this file should acknowledge exactly the bits it observed in the matching register bank rather than sharing masks between the `MEMCHECK` and `MEMCHECK2` banks blindly.

## State And Persistence Behavior

The macros do not store state, but they describe persistent hardware state in memory-mapped or indirect VCN registers. The status bits represent latched hardware error state until the appropriate acknowledge bits are written. The enable bits persist in the VCN block register file until reset, power-gating, firmware reinitialization, or explicit driver rewrite. `UVD_IH_SEM_CTRL` likewise reflects hardware register state and must be restored as part of VCN block initialization/resume if the block loses power.

The distinction between system interrupt state and VCPU interrupt state matters for persistence: a bit may be visible in a system status/ack register at one bit position and in a VCPU status/ack register at another, especially for the `MEMCHECK2` extended sources. State tracking in higher-level code should treat these as separate register layouts even when the field names refer to the same hardware source.

## Dependencies And Integration Points

The immediate dependency is the companion VCN 3.0 offset header, which defines register addresses for `ixUVD_MEMCHECK_SYS_INT_EN`, `ixUVD_MEMCHECK_SYS_INT_STAT`, `ixUVD_MEMCHECK_SYS_INT_ACK`, `ixUVD_MEMCHECK_VCPU_INT_EN`, `ixUVD_MEMCHECK_VCPU_INT_STAT`, `ixUVD_MEMCHECK_VCPU_INT_ACK`, `ixUVD_MEMCHECK2_SYS_INT_STAT`, `ixUVD_MEMCHECK2_SYS_INT_ACK`, `ixUVD_MEMCHECK2_VCPU_INT_STAT`, `ixUVD_MEMCHECK2_VCPU_INT_ACK`, and `ixUVD_IH_SEM_CTRL`.

The generated header is included by VCN 3.0 generation driver files such as `drivers/gpu/drm/amd/amdgpu/vcn_v3_0.c` and JPEG 3.0 code. Those files integrate the constants with AMDGPU register-access helpers, IP block initialization/reset, interrupt handling, power management, firmware bring-up, and debug paths.

The naming is also cross-generation aligned: similar `UVD_MEMCHECK*` and `UVD_IH_SEM_CTRL` fields appear in VCN 4.x and 5.x headers, sometimes with different offsets or enable-bit positions. This makes the file part of a generation-specific hardware description contract rather than a reusable generic definition.

## Risks And Edge Cases

The primary risk is incorrect bit mapping. These constants encode hardware ABI values; a one-bit shift error can enable the wrong error source, fail to report a real memory-check fault, or acknowledge the wrong latched status. The sparse fields at high bit positions and the differing `MEMCHECK2` system versus VCPU layouts are the most error-prone areas.

Another risk is over-generalizing across VCN generations. Later VCN headers share names but may place extended sources at different offsets or bits. Code should include the header for the active IP version and avoid mixing `vcn_3_0_0` masks with `vcn_4_*` or `vcn_5_*` offsets.

Generated-header churn is also a review risk. Since this file contains no type checking, duplicate-looking blocks can hide accidental copy/paste errors. Changes should be compared against AMD register specifications or an authoritative generated source, not inferred from neighboring masks alone.

For ack registers, callers must understand the hardware write semantics. These macros only name bits; they do not say whether a bit is write-one-to-clear, write-one-to-acknowledge, or has side effects. Incorrect read/modify/write logic could either lose events or leave interrupt status stuck.

## Test Signals

There are no direct unit tests for this header. Useful validation signals are integration and hardware-facing:

- A kernel build that includes `vcn_v3_0.c` and `jpeg_v3_0.c` catches missing or renamed macros.
- VCN firmware bring-up and reset tests should continue without interrupt storms or stuck memory-check status.
- Fault-injection or diagnostic paths that exercise VCN memory-check reporting should show expected low/high source bits in `UVD_MEMCHECK*_INT_STAT` and clear them through the matching `*_INT_ACK` masks.
- Suspend/resume, power-gating, and GPU reset tests should confirm VCN state is reprogrammed and no stale memory-check interrupt bits remain latched.
- Cross-generation review should verify VCN 3.0 code includes `vcn_3_0_0_offset.h` with `vcn_3_0_0_sh_mask.h`, not a sibling generation's mask header.

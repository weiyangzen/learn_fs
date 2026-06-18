# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h lines 2277-4738

## Scope And Purpose

This chunk is a large middle section of the generated AMD VCN 4.0.5 shift/mask header. It defines C preprocessor constants for the bit layout of VCN/UVD decode-side registers, beginning in the tail of `SAOE_SUVD_CGC_CTRL`, covering most of the core `uvd_uvddec`, `uvd_ecpudec`, `uvd_uvd_mpcdec`, `uvd_uvd_rbcdec`, and `uvd_lmi_adpdec` address blocks, and ending at the `UVD_LMI_PERFMON_COUNT_HI` register heading before that register's field definitions.

The file section is not executable code. Its purpose is to provide a generation-specific hardware ABI map: every `__SHIFT` macro gives a field bit offset, and every `_MASK` macro gives the already-shifted 32-bit field mask. AMDGPU VCN 4.0.5 driver code combines these constants with `vcn_4_0_5_offset.h` register offsets and SOC15 register helpers when programming the decode engine, video command processor, ring buffers, memory interface, interrupts, resets, and clock-gating state.

## Register Field Groups

The opening group covers SUVD clock-gating control registers. The chunk starts inside `SAOE_SUVD_CGC_CTRL`, then defines equivalent field layouts for `SCM_SUVD_CGC_CTRL`, `SDB_SUVD_CGC_CTRL`, `SIT0_NXT_SUVD_CGC_CTRL`, `SIT1_NXT_SUVD_CGC_CTRL`, `SIT2_NXT_SUVD_CGC_CTRL`, `SIT_SUVD_CGC_CTRL`, `SMPA_SUVD_CGC_CTRL`, `SMP_SUVD_CGC_CTRL`, `SRE_SUVD_CGC_CTRL`, `UVD_MPBE0_SUVD_CGC_CTRL`, `UVD_MPBE1_SUVD_CGC_CTRL`, and `UVD_SUVD_CGC_CTRL`. These fields gate or mode-control SUVD subblocks such as `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, `SCLR`, `UVD_SC`, entropy/header paths, `SAOE`, `MPBE0/1`, AV1 paths, `MPC1`, `AVM_0/1`, next-generation SIT common/decode/encode paths, `FBC_PCLK`, `FBC_CCLK`, and `CDEFE`.

Core UVD command and interrupt registers follow. `UVD_GPCOM_VCPU_DATA0/1`, `UVD_GPCOM_SYS_CMD`, and `UVD_GPCOM_SYS_DATA0/1` describe the general-purpose command mailbox between the host/system and VCPU. `UVD_VCPU_INT_EN`, `UVD_VCPU_INT_ACK`, `UVD_VCPU_INT_ROUTE`, `UVD_SUVD_INT_EN`, `UVD_SUVD_INT_STATUS`, `UVD_SUVD_INT_ACK`, `UVD_MASTINT_EN`, `UVD_SYS_INT_EN`, `UVD_SYS_INT_STATUS`, and `UVD_SYS_INT_ACK` define the interrupt enable/status/ack surface for page/interface faults, semaphore timeouts, software ring interrupts, LBSI/UDEC/LMI/SUVD/MPRD/IDCT events, job completion, GPCOM, clock switch, MIF hardware interrupts, and AVM events.

The ring and context group includes `UVD_JOB_DONE`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CONTEXT_ID2`, `UVD_NO_OP`, four input ring base/size triplets (`UVD_RB_BASE_LO/HI/SIZE` through `UVD_RB_BASE_LO4/HI4/SIZE4`), one output ring triplet, SR-IOV active-function and mailbox registers, `UVD_RB_ARB_CTRL`, indexed context access via `UVD_CTX_INDEX/DATA`, CXW write/interrupt IDs, MPEG2 decode state, pitch/width/height/picture-count placeholders, MPEG2 control, DXVA buffer sizing, scratch registers, audio ring base/size fields, and secondary SW ring interrupt bits for ring 6.

Status, control, reset, and clock-gating state is represented by `UVD_SUVD_CGC_STATUS2`, second-bank SUVD interrupts, `UVD_STATUS`, `UVD_CNTL`, `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, `UVD_WIG_CTRL`, `UVD_CGC_STATUS`, `UVD_CGC_UDEC_STATUS`, `UVD_SUVD_CGC_STATUS`, and `UVD_GPCOM_VCPU_CMD`. These registers expose busy/report bits, SUVD enable, reset request and reset-status bits for many UVD/SUVD subblocks, WIG buffer selection, clock-gating status for core and decode pipes, and VCPU-side GPCOM command state.

The `uvd_ecpudec` block maps VCPU cache and non-cache windows. `UVD_VCPU_CACHE_OFFSET0..8` and `UVD_VCPU_CACHE_SIZE0..8` define cached firmware memory windows; `UVD_VCPU_NONCACHE_OFFSET0/1` and `UVD_VCPU_NONCACHE_SIZE0/1` define uncached windows. `UVD_VCPU_CNTL` exposes VCPU error, reset, abort, clock, trace, JTAG, timeout, block reset, runstall, and SRE command-interface reset controls. `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, and indirect index/data registers support identification, trace, and indirect VCPU register access.

The `uvd_uvd_mpcdec` block describes the motion/picture cache or MPC programming surface. It includes byte-swap fields for 17 references, luma/chroma search and hit counters, MPC reset/performance/replacement/urgent controls, pitch, mux and ALU setup registers, performance latency counters, and indirect MPC access.

The `uvd_uvd_rbcdec` block defines the ring-buffer controller and semaphore control surface. `UVD_RBC_IB_SIZE`, `UVD_RBC_IB_SIZE_UPDATE`, and `UVD_RBC_RB_CNTL` describe indirect-buffer and ring-buffer sizing/fetch/update controls. `UVD_RBC_RB_RPTR_ADDR`, `UVD_RBC_VCPU_ACCESS`, urgent read priority, write-pointer status and polling registers, semaphore command/address/timeout/control registers, `UVD_ENGINE_CNTL`, `UVD_JOB_START`, `UVD_RBC_BUF_STATUS`, and `UVD_RBC_SWAP_CNTL` together define queue start, semaphore wait/signal behavior, timeout reporting, buffer validity, and endian/swap configuration.

The `uvd_lmi_adpdec` block is the memory-interface and adapter portion. Most of this group is low/high 64-bit BAR field pairs for VCN clients: RE, IT, MP, CM, DB, DBW, IDCT, MPRD S0/S1, MPC, RBC RB/IB, LBSI, VCPU NC0/NC1/cache/cache1-cache8, CENC, SRE, MIF GPGPU/current/ref/DBW/CM colocated/BSP/BSD/SCLR/image-paste/privacy paths, and SPH high bits. It also includes `UVD_LMI_ARB_CTRL2`, cache and non-cache VMID multi-registers, latency control and counters, SPH status, single cache VMID, `UVD_LMI_CTRL2`, urgent controls, `UVD_LMI_CTRL`, `UVD_LMI_STATUS`, `UVD_LMI_PERFMON_CTRL`, and `UVD_LMI_PERFMON_COUNT_LO`.

## Important APIs, Types, And Functions

This chunk exports only preprocessor macros. There are no functions, structs, enums, globals, locks, allocations, or inline helpers. The macro naming convention is the API:

- `<REGISTER>__<FIELD>__SHIFT` is the field shift count.
- `<REGISTER>__<FIELD>_MASK` is the mask at its final bit position.

Consumers normally use these constants through AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, and `SOC15_REG_OFFSET`. For this exact ASIC generation, `vcn_4_0_5_offset.h` supplies offsets such as `regUVD_CGC_CTRL3`, `regUVD_RBC_RB_CNTL`, `regUVD_LMI_CTRL2`, and `regUVD_LMI_PERFMON_COUNT_HI`; this header supplies their bit layouts.

Concrete in-tree consumers include `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c`, which uses `UVD_LMI_CTRL2__RE_OFLD_MIF_WR_REQ_NUM__SHIFT` to program RE offload request depth and `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK` to stall or unstall UMC arbitration during VCN setup and teardown. Cross-generation VCN files use the same macro families, but the VCN 4.0.5 offsets and masks must be treated as an ASIC-specific pair.

## Control Flow

The header itself has no runtime control flow; it is a table of constants expanded at compile time. The control flow it supports in driver code is hardware sequencing:

1. Initialize or resume the VCN block by programming clock-gating mode bits, soft-reset controls, VCPU cache windows, LMI BARs, VMIDs, and ring-buffer registers.
2. Start the command/ring path by configuring RBC ring sizing and polling behavior, enabling VCPU/RBC access as needed, and writing job or engine-start command bits.
3. Exchange mailbox commands through GPCOM data/command registers between host/system code and the VCPU firmware.
4. Route and service interrupts by enabling selected VCPU/SUVD/system bits, reading status registers, and acknowledging the matching status bits through the corresponding ack registers.
5. Quiesce or reset the block by stalling LMI arbitration, checking clean/idle/status bits, asserting soft-reset fields, and restoring persistent configuration after reset or power loss.

The field layout encourages paired usage: `*_INT_STATUS` fields should be decoded with their matching status masks and cleared through the corresponding `*_INT_ACK` masks; ring and LMI address halves must be programmed as matching low/high pairs; and reset-status bits should be polled with the masks from the same generation header.

## State And Persistence Behavior

The macros do not store state. They describe hardware register state in the VCN 4.0.5 register file. Configuration fields such as clock-gating modes, ring base/size registers, cache offsets/sizes, LMI BAR low/high pairs, VMIDs, byte-swap controls, urgent controls, and coherency settings persist until the block is reset, power-gated, firmware-reinitialized, or explicitly rewritten by the driver.

Other fields represent transient or latched state. Interrupt status and timeout status bits remain set until acknowledged through the appropriate ack or clear field. `UVD_STATUS`, clock-gating status, reset-status fields, LMI clean/idle state, buffer-valid counters, performance counters, latency counters, and GPCOM request bits are live hardware observations. Command-like fields such as `UVD_JOB_START`, `UVD_ENGINE_CNTL__ENGINE_START`, semaphore commands, reset bits, and interrupt ack bits can have side effects on write.

State split across registers needs careful persistence handling. Low/high BAR pairs are one 64-bit address split over two 32-bit registers; ring and audio ring base/size triplets must remain consistent; VCPU cache offsets/sizes define firmware-visible memory windows; and VMID registers tie those memory windows to GPU virtual-memory context. Suspend/resume, GPU reset, or dynamic power-gating paths must restore the same generation-specific configuration before accepting jobs.

## Dependencies And Integration Points

The immediate dependencies are the generated VCN 4.0.5 companion headers. `vcn_4_0_5_offset.h` maps the register names to addresses and base indices, while this file maps fields to bit positions. Default-value headers, when used by a caller, provide reset defaults. AMDGPU register helpers provide the typed usage pattern around these raw constants.

The primary integration point is the VCN 4.0.5 implementation under `drivers/gpu/drm/amd/amdgpu/`, especially initialization, firmware bring-up, clock/power gating, suspend/resume, reset recovery, ring setup, interrupt handling, and diagnostics. The RBC and LMI fields connect to AMDGPU ring allocation and command submission. GPCOM and VCPU fields connect to firmware command exchange. Interrupt masks connect to the DRM/AMDGPU interrupt handler path. BAR, VMID, coherency, and urgent-control fields connect the video block to GPU memory management and isolation.

This chunk is also part of a cross-generation register family. Similar names appear in VCN 2.x, 3.x, 4.0, and 5.x files, and some legacy UVD headers. That similarity is useful for code sharing, but it is also a risk: the active IP version's offset header and shift/mask header must be included together.

## Risks And Edge Cases

The highest risk is bitfield drift. These values are hardware ABI constants; an incorrect shift or mask can gate the wrong SUVD subblock, acknowledge the wrong interrupt, start or stop the wrong ring behavior, corrupt an LMI address, or leave VCN stuck in reset or arbitration stall.

The chunk boundaries matter. The requested range starts in the middle of `SAOE_SUVD_CGC_CTRL`, so a complete analysis of that register requires the previous chunk. It ends on the `UVD_LMI_PERFMON_COUNT_HI` heading before the `PERFMON_COUNT` field definitions, so complete perfmon high-counter handling requires the next chunk.

Several repeated macro families are easy to misuse. SUVD CGC control registers share similar fields but target different subblocks. `UVD_RB_BASE_LO/HI/SIZE` variants refer to different rings. LMI BAR pairs are numerous and client-specific; crossing low/high halves or programming a BAR for the wrong client can cause memory corruption or firmware faults. `UVD_VCPU_CACHE8` appears before cache2-7 in this chunk's BAR list, which should be preserved as generated rather than "normalized" by hand.

Interrupt and ack semantics are hardware-defined and not encoded in the macro names. Callers must know whether an ack bit is write-one-to-clear/write-one-to-acknowledge and avoid read/modify/write patterns that drop concurrent events. Similarly, reset and start bits may be edge-triggered or have sequencing constraints that are enforced only by the driver and hardware documentation.

Address, VMID, and virtualization fields are security-sensitive. Incorrect VMID or BAR programming can route VCN firmware, ring, or memory-interface traffic through the wrong GPU virtual address space. The SR-IOV active-function and mailbox fields should not be treated as ordinary scratch state.

## Test Signals

Useful validation signals are integration and hardware-facing rather than unit tests for this generated header:

- Kernel build coverage for `vcn_v4_0_5.c` and any files that include `vcn_4_0_5_offset.h` together with `vcn_4_0_5_sh_mask.h`.
- VCN 4.0.5 firmware load and ring bring-up with expected RBC read/write pointer movement and job completion.
- Decode workload tests that exercise the main rings, output ring, audio ring, GPCOM exchange, and interrupt ack paths without stuck status bits.
- Suspend/resume, dynamic power-gating, and GPU reset tests that verify clock-gating, soft-reset, LMI clean/idle, and VCPU cache/window state are restored.
- Fault-injection or negative tests for semaphore timeouts, page/interface faults, unsupported LMI AXI conditions, and system/VCPU/SUVD interrupt routing.
- Memory-management tests that verify LMI BAR low/high pairs, VMIDs, coherency fields, and urgent/stall controls do not cause page faults, data corruption, or isolation violations.
- Performance/diagnostic reads of MPC and LMI counters to ensure perf and latency fields decode as expected for this generation.

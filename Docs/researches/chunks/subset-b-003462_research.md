# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h lines 2276-4736

## Scope And Purpose

This chunk is a generated shift/mask description for the AMD VCN 4.0.3 UVD/VCN register blocks. It is not executable driver logic. Its job is to provide stable C preprocessor names for bit positions and already-shifted masks used by VCN 4.0.3 decode/encode, firmware, interrupt, ring-buffer, clock-gating, reset, and local-memory-interface programming code.

The range starts in the middle of the `SCM_SUVD_CGC_CTRL` field list, then covers the rest of the `aid_uvd0_uvddec` block through `UVD_GPCOM_VCPU_CMD`, the full `aid_uvd0_ecpudec` VCPU cache/control block, the `aid_uvd0_uvd_mpcdec` motion-prediction-cache block, the `aid_uvd0_uvd_rbcdec` ring-buffer-controller/semaphore block, and the start of the `aid_uvd0_lmi_adpdec` local-memory-interface/address-programming block. It ends inside `UVD_LMI_VCPU_CACHE_VMIDS_MULTI`, after the shift fields and the first VMID mask.

The source file pairs with `vcn_4_0_3_offset.h`: the offset header names register addresses such as `regUVD_RB_BASE_LO`, while this header names fields such as `UVD_RB_BASE_LO__RB_BASE_LO_MASK`. VCN 4.0.3 code includes both headers and uses AMDGPU register helpers to compose and decode hardware register values.

## Register Field Groups

The opening CGC control section describes submodule clock-gating mode bits for the secondary UVD path. The repeated `*_SUVD_CGC_CTRL` registers cover blocks including `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, `UVD_MPBE0`, `UVD_MPBE1`, and `UVD_SUVD`. Most share the same field layout: one-bit mode fields for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, `EFC`, `SAOE`, `SMPA`, `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, and `MPC1`, plus newer `AVM_0`, `AVM_1`, and `SIT_NXT_*` fields where applicable. `FBC_PCLK`, `FBC_CCLK`, and `CDEFE_MODE` occupy high bits. `UVD_MPBE0_SUVD_CGC_CTRL` and `UVD_MPBE1_SUVD_CGC_CTRL` are narrower than the fully populated groups and omit some later AVM/SIT_NXT fields.

`UVD_CGC_CTRL3` adds global clock-gating delay and mode controls for `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, and `PPU`. `UVD_CGC_STATUS`, `UVD_CGC_UDEC_STATUS`, `UVD_SUVD_CGC_STATUS`, and `UVD_SUVD_CGC_STATUS2` later expose clock-active/status bits for SYS/UDEC/MPEG2/REGS/RBC/LMI/IDCT/MPRD/MPC/LBSI/LRBBM/WCB/VCPU/MMSCH plus codec-specific SUVD paths such as H.264, HEVC, VP9, AV1, FBC, SMPA, CDEFE, and SIT0-2.

The GPCOM and firmware-message registers describe mailbox-style communication between host/system code and the VCPU firmware. `UVD_GPCOM_VCPU_DATA0/1` and `UVD_GPCOM_SYS_DATA0/1` are full 32-bit payload fields. `UVD_GPCOM_SYS_CMD` and `UVD_GPCOM_VCPU_CMD` split command words into `CMD_SEND`, a 30-bit `CMD`, and `CMD_SOURCE`. `UVD_DRV_FW_MSG`, `UVD_FW_DRV_MSG_ACK`, and `UVD_VCPU_INT_ROUTE` define driver/firmware message and acknowledgement routing bits.

The interrupt fields cover VCPU, SUVD, encoder, master, and system interrupt paths. `UVD_VCPU_INT_EN`, `UVD_VCPU_INT_STATUS`, and `UVD_VCPU_INT_ACK` use matching low/high layouts for errors and events such as PIF address errors, semaphore timeouts, software ring-buffer interrupts, RBC privilege faults, LBSI/UDEC/SUVD events, read-pointer writes, job start, nested page faults, IDCT/MPRD/AVM/clock-switch/MIF hardware interrupts, and driver/firmware request/ack events. `UVD_VCPU_INT_STATUS` includes `GPCOM_INT` at bit 20, while the enable and ack registers do not expose a matching enable/ack field in this first bank. `UVD_VCPU_INT_STATUS2`, `UVD_VCPU_INT_ACK2`, and `UVD_VCPU_INT_EN2` add `SW_RB6` and `RASCNTL_VCPU_VCODEC`; note that `RASCNTL_VCPU_VCODEC` appears at different bit positions in status, ack, and enable.

`UVD_SUVD_INT_EN`, `UVD_SUVD_INT_STATUS`, and `UVD_SUVD_INT_ACK` define packed function-interrupt fields and one-bit error fields for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, and `FBC`. The `*_INT_*2` bank extends this for `SMPA` and `SDB_AV1`. `UVD_ENC_VCPU_INT_EN/STATUS/ACK` defines three scan-in buffer-manager interrupt bits. `UVD_MASTINT_EN` gates VCPU and system interrupts and reports interrupt overrun state, while `UVD_SYS_INT_EN/STATUS/ACK` mirrors many VCPU interrupt sources for the system path and adds `CXW_WR`, `JOB_DONE`, `GPCOM`, and `RASCNTL_VCPU_VCODEC` handling.

The ring and context section defines software-visible job identity, no-op, and ring-buffer programming fields. `UVD_JOB_DONE`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CONTEXT_ID2`, and `UVD_NO_OP` are simple payload/status registers. `UVD_RB_BASE_LO/HI`, `UVD_RB_SIZE`, and their `2`, `3`, and `4` variants define four input ring buffers; low base fields are aligned at bit 6 and size fields at bit 4. `UVD_OUT_RB_*` and `UVD_AUDIO_RB_*` use the same base/size pattern. `UVD_RB_ARB_CTRL` controls whether SRBM, VCPU, RBC, and firmware-offload paths drop or disable access, and includes fast-path/debug bits. `UVD_CTX_INDEX/DATA`, `UVD_CXW_WR`, `UVD_CXW_WR_INT_ID`, `UVD_CXW_WR_INT_CTX_ID`, and `UVD_CXW_INT_ID` provide indexed context and CXW interrupt metadata.

The decode/control diagnostics include MPEG2 and picture-buffer fields. `UVD_MPEG2_ERROR`, `UVD_YBASE`, `UVD_UVBASE`, `UVD_PITCH`, `UVD_WIDTH`, `UVD_HEIGHT`, `UVD_PICCOUNT`, `UVD_MB_CTL_BUF_BASE`, `UVD_PIC_CTL_BUF_BASE`, and `UVD_SCRATCH_NP` are full-width payload registers. `UVD_MPRD_INITIAL_XY`, `UVD_MPEG2_CTRL`, and `UVD_DXVA_BUF_SIZE` pack screen coordinates, enable/trick-mode/job size, and picture/macroblock buffer sizes. `UVD_CLK_SWT_HANDSHAKE` names clock-switch type and domain bits. `UVD_GP_SCRATCH0` through `UVD_GP_SCRATCH23` are full-width general scratch registers.

The power/reset/status group defines block state and reset controls. `UVD_STATUS` reports RBC busy, VCPU report, RBC GPCOM access, DRM busy, and system GPCOM request. `UVD_ENC_PIPE_BUSY` exposes many encoder datapath busy bits, including IME/SMP/SIT/SDB/ENT/LCM/MDM/EFC/CDEFE/MIF/BSP/BSD/SAOE. `UVD_FW_POWER_STATUS` reports VCPU power state, read/write values, software data, and handshake bits. `UVD_CNTL` holds multiple clock-enable flags, timeout controls, dynamic clock gating and mem power controls, stall bits, and soft-disconnect controls. `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, and `UVD_WIG_CTRL` define reset request and reset-status bits for RBC, LBSI, LMI, VCPU, UDEC, CXW, TAP, MPC, EFC, IH, MPRD, IDCT, UMC, SPH, MIF, LCM, SUVD, atomic/PPU/MMSCH, AVM/ACAP/WIG, and related clock domains.

The `aid_uvd0_ecpudec` block describes VCPU memory windows and VCPU control. `UVD_VCPU_CACHE_OFFSET0..8` and `UVD_VCPU_CACHE_SIZE0..8` use 21-bit fields. `UVD_VCPU_NONCACHE_OFFSET0/1` use 25-bit offsets and `UVD_VCPU_NONCACHE_SIZE0/1` use 21-bit sizes. `UVD_VCPU_CNTL` defines IRQ error, burst, PMB, reset, abort, clock, trace, debug, JTAG, timeout, block reset, runstall, and SRE command-interface reset fields. `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, `UVD_VCPU_IND_INDEX`, and `UVD_VCPU_IND_DATA` provide processor identity, trace, and indirect-index/data access fields.

The `aid_uvd0_uvd_mpcdec` block describes motion-prediction-cache control and instrumentation. `UVD_MP_SWAP_CNTL` provides two-bit MC swap selectors for reference slots 0-15 and `UVD_MP_SWAP_CNTL2` adds reference slot 16. Luma/chroma search, hit, and hit-pending counters are full-width. `UVD_MPC_CNTL` includes block reset, performance selection/reset, replacement mode, debug mux, averaging weight, urgency, speed-up, and test mode fields. The mux/ALU registers (`UVD_MPC_SET_MUXA0/1`, `UVD_MPC_SET_MUXB0/1`, `UVD_MPC_SET_MUX`, `UVD_MPC_SET_ALU`) pack small selector/function fields, and `UVD_MPC_PERF0/1` expose max/average latency fields. `UVD_MPC_IND_INDEX/DATA` implement indirect access.

The `aid_uvd0_uvd_rbcdec` block defines ring-buffer-controller and semaphore fields. `UVD_RBC_IB_SIZE` and `UVD_RBC_IB_SIZE_UPDATE` encode indirect-buffer sizes at bit 4. `UVD_RBC_RB_CNTL` sets ring-buffer size, block size, no-fetch, write-pointer polling, no-update, read-pointer-write enable, and block reset. The remaining RBC fields provide read-pointer address, VCPU access enable, firmware semaphore status, urgent read priority, write-pointer prewrite timing, write-pointer status, write-pointer polling frequency/address, job start, buffer-valid/read/write address status, and MC swap fields. The semaphore registers split request command, write phase, mode, VMID enable/VMID, low/high address pieces, timeout status/clear, semaphore enable, and timeout counter/resend timer fields.

The `aid_uvd0_lmi_adpdec` block begins a long sequence of 64-bit base-address registers. Each low register exposes `BITS_31_0` and each high register exposes `BITS_63_32`, normally with full 32-bit masks. Covered clients include RE, IT, MP, CM, DB, DBW, IDCT, MPRD S0/S1/DBW, MPC, RBC RB/IB, LBSI, VCPU non-cache and cache windows, CENC, SRE, MIF GPGPU, current luma/chroma, references, DBW, CM coloc, BSP0-3, BSD0-4, VCPU cache1-8, SCLR/SCLR2, SPH high, imagepaste luma/chroma, and privacy luma/chroma. `UVD_ADP_ATOMIC_CONFIG` then defines four 4-bit atomic write-cache user fields and a 4-bit atomic read urgency field. `UVD_LMI_ARB_CTRL2` defines wait-enable, max-burst, and read/write request-return limits. The chunk ends at `UVD_LMI_VCPU_CACHE_VMIDS_MULTI`, which packs 4-bit VMIDs for VCPU cache windows 1-8 but only includes the first mask before the line-range boundary.

## Important APIs, Types, And Functions

This chunk exports only C preprocessor constants. There are no C functions, structs, enums, inline helpers, global variables, locks, or allocation paths. The API surface follows the generated AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` is the bit offset to use when inserting or extracting a field.
- `<REGISTER>__<FIELD>_MASK` is the already-positioned 32-bit mask used by `REG_SET_FIELD`, `REG_GET_FIELD`, direct bit tests, or masked writes.

The primary consumers are VCN 4.0.3 driver files that include both `vcn/vcn_4_0_3_offset.h` and `vcn/vcn_4_0_3_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.c`. That implementation lists many of the registers in `vcn_reg_list_4_0_3`, programs VCPU cache/LMI base registers during firmware setup, handles IRQ registration, and uses SOC15 register helpers such as `WREG32_SOC15`, `RREG32_SOC15`, and DPG-mode variants. `jpeg_v4_0_3.c` includes the same generated VCN header set for generation-consistent masks and offsets, although its main register use is in JPEG-specific blocks.

## Control Flow

There is no runtime control flow inside the header. The driver control flow implied by these definitions is hardware-programming flow:

1. During VCN initialization or resume, driver code programs clocks, resets, VCPU cache windows, non-cache windows, LMI BARs, ring-buffer bases/sizes, ring-control bits, and interrupt enables using the masks in this chunk.
2. Firmware and hardware exchange messages through GPCOM and driver/firmware message registers; the command/data masks define how the 32-bit words are packed and decoded.
3. During command submission, ring-buffer base, size, pointer, and RBC control fields define how VCPU/RBC fetch work from GPU memory.
4. During interrupts, hardware latches bits in VCPU, system, SUVD, encoder, and second-bank status registers; handlers decode those status registers and write matching ack masks where the hardware expects acknowledgement.
5. During reset, power-gating, DPG, suspend/resume, or error recovery, reset/status/clock-gating fields are polled or rewritten to return VCN blocks to a known state.

The important control-flow constraint is that similarly named enable/status/ack registers are not universally interchangeable. Several banks intentionally have different field coverage or bit positions, for example `GPCOM_INT` exists in status without a first-bank enable/ack field, and `RASCNTL_VCPU_VCODEC` differs across `UVD_VCPU_INT_STATUS2`, `UVD_VCPU_INT_ACK2`, and `UVD_VCPU_INT_EN2`.

## State And Persistence Behavior

The macros themselves hold no state. They describe persistent hardware register state in the VCN block. Ring-buffer base/size registers, VCPU cache and non-cache window registers, LMI 64-bit BARs, clock-gating controls, interrupt enables, reset controls, semaphore controls, and arbitration controls remain programmed until reset, power loss, power-gating, firmware reinitialization, or an explicit driver rewrite.

Status and interrupt registers describe latched or live hardware state. Busy/status fields such as `UVD_STATUS`, `UVD_ENC_PIPE_BUSY`, `UVD_CGC_STATUS`, and `UVD_SUVD_CGC_STATUS*` reflect current hardware activity or clock state. Interrupt status fields can remain asserted until cleared through matching ack bits. Timeout status and semaphore status can also persist long enough to affect later bring-up or job handling if not cleared according to the hardware semantics.

Address fields are particularly persistent and security-sensitive. VCPU cache/non-cache windows and LMI BARs point the VCN firmware and functional subblocks at GPU-visible memory. They must be reprogrammed after GPU reset or VCN power collapse, and they must match the VMID, address alignment, and memory layout expected by firmware and ring setup.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_offset.h`, which supplies the corresponding `reg...` addresses and base-index metadata. The masks are meaningful only when paired with the matching VCN 4.0.3 offsets.

The main integration points are AMDGPU's SOC15 register-access helpers (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_DPG_MODE`, `SOC15_REG_OFFSET`, `SOC15_WAIT_ON_RREG`, `REG_SET_FIELD`, `REG_GET_FIELD`) and the VCN/JPEG generation files. `vcn_v4_0_3.c` uses this generated header for firmware memory-window setup, DPG-mode programming, interrupt wiring, debug register listing, ring initialization, and power/reset sequencing. `jpeg_v4_0_3.c` includes the same generation header set and integrates VCN-generation register definitions with JPEG power, interrupt, and ring setup paths.

Firmware integration is central. The VCPU cache/non-cache registers map firmware, stack, context, and shared memory buffers; GPCOM and driver/firmware message registers are mailbox surfaces; interrupt fields route firmware-visible and host-visible events. Ring-buffer and semaphore fields integrate VCN command submission with GPU memory, VMIDs, and synchronization.

The file is generation-specific. Similar `UVD_*` names appear in VCN 4.0.5, VCN 5.x, and older UVD/VCN headers, but field positions and available bits are not guaranteed to match. Code should include and use the header for the active IP version instead of sharing masks across generations by name.

## Risks And Edge Cases

The primary risk is hardware ABI drift or a single incorrect bit value. These constants encode hardware register contracts; a wrong shift or mask can enable the wrong interrupt, fail to clear a latched interrupt, gate the wrong clock, reset the wrong block, misprogram a ring address, or point firmware at the wrong memory window.

Boundary blocks are easy to mishandle in chunked review. This line range begins after the `SCM_SUVD_CGC_CTRL` comment and ends before the complete `UVD_LMI_VCPU_CACHE_VMIDS_MULTI` definition. Any merged per-file document should reconcile the adjacent chunks so partial blocks are not mistaken for incomplete generated code.

The repeated CGC control definitions look mechanically identical, but some blocks intentionally omit newer fields. A reviewer should not "normalize" `UVD_MPBE0_SUVD_CGC_CTRL` or `UVD_MPBE1_SUVD_CGC_CTRL` to the fuller SUVD layout without checking the hardware source.

Interrupt layouts have sparse bits and bank-specific differences. Reusing a mask from an enable register for an ack or status register solely because the field names look similar can be wrong for second-bank or special fields. Acknowledgement registers also depend on hardware write semantics that are not documented by these masks.

Address and size fields have alignment and width constraints. Ring-buffer low base fields drop the low six bits, ring sizes start at bit four, VCPU cache offsets/sizes are 21-bit fields, non-cache offsets are 25-bit fields, and semaphore addresses are split into non-byte-aligned ranges. Callers must pass already-valid hardware addresses and sizes; the masks do not validate them.

Generated headers provide no type safety. All fields are preprocessor constants, so mixing `vcn_4_0_3` masks with a different generation's offsets, using a `_STATUS` mask in a `_CNTL` register, or writing a full-width payload register through the wrong address can compile cleanly and fail only on hardware.

## Test Signals

There are no direct unit tests for this header. Useful validation comes from build, integration, and hardware behavior:

- A kernel build covering `vcn_v4_0_3.c` and `jpeg_v4_0_3.c` catches missing or renamed macros from this generated header.
- VCN firmware load and boot should correctly program `UVD_LMI_VCPU_CACHE*_64BIT_BAR_*`, `UVD_VCPU_CACHE_OFFSET*`, and `UVD_VCPU_CACHE_SIZE*` registers and reach the expected VCPU status.
- Ring tests should submit decode/encode work through all configured rings without stuck `UVD_RBC_RB_CNTL`, bad read/write pointers, or malformed ring base/size programming.
- Interrupt tests should show expected VCPU, system, SUVD, encoder, and second-bank status bits and should clear them with the matching ack registers without interrupt storms.
- Suspend/resume, DPG, power-gating, GPU reset, and recovery tests should reprogram persistent VCN state and observe sane clock-gating/reset status bits.
- Memory-window and VMID-sensitive tests should verify firmware, stack, context, non-cache, semaphore, and LMI BAR programming does not produce page faults, poison interrupts, or data corruption.
- Cross-generation review should verify VCN 4.0.3 code includes `vcn_4_0_3_offset.h` with `vcn_4_0_3_sh_mask.h`, not sibling VCN 4.0.5 or VCN 5.x definitions with similar names.

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

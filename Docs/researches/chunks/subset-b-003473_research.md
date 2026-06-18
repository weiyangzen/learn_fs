# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_sh_mask.h lines 2275-4757

## Scope And Purpose

This chunk is a generated AMD VCN 5.0.0 shift/mask header segment. It contains C preprocessor constants only: each register field is exposed as a `<REGISTER>__<FIELD>__SHIFT` macro and a `<REGISTER>__<FIELD>_MASK` macro. It defines no functions, structs, enums, storage, control flow, locking, allocations, or direct MMIO operations.

The path lives under a `ceph-client` source mirror, but this is AMDGPU media-engine hardware metadata, not Ceph filesystem logic. Runtime behavior is supplied by AMDGPU VCN/JPEG drivers that include this header with `vcn_5_0_0_offset.h` and use the masks with SOC15 register helpers.

The chunk begins in the middle of the `SMP_SUVD_CGC_CTRL` register definition, after the first several shifts were introduced in the prior chunk. It ends at `UVD_JRBC_SCRATCH0__SCRATCH0__SHIFT`, so the matching mask and the rest of the JRBC block continue in the next chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position for packing and extracting a field.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask used in register reads, writes, waits, and packet construction.

Major register families in this chunk:

- SUVD clock-gating controls: `SMP_SUVD_CGC_CTRL`, `SRE_SUVD_CGC_CTRL`, `UVD_SUVD_CGC_CTRL`, `UVD_CGC_CTRL3`, `CDEFE_SUVD_CGC_GATE`, `CDEFE_SUVD_CGC_GATE2`, and `CDEFE_SUVD_CGC_CTRL`. These cover per-subblock mode/gate bits for SRE, SIT, SMP, SCM, SDB, SCLR, UVD_SC, ENT, IME, SITE, EFC, SAOE, SMPA, MPBE, AV1, MPC1, AVM, CDEFE, FBC clocks, LCM, MIF, VREG, PE, and PPU.
- Host/firmware command and interrupt registers: `UVD_GPCOM_VCPU_DATA0/1`, `UVD_GPCOM_SYS_CMD`, `UVD_GPCOM_SYS_DATA0/1`, `UVD_GPCOM_VCPU_CMD`, `UVD_DRV_FW_MSG`, `UVD_FW_DRV_MSG_ACK`, `UVD_MASTINT_EN`, VCPU/SYS/SUVD/ENC interrupt enable/status/ack groups, and `UVD_VCPU_INT_ROUTE`.
- VCN job and ring register fields: `UVD_JOB_DONE`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CONTEXT_ID2`, `UVD_NO_OP`, `UVD_RB_BASE_LO/HI`, `UVD_RB_SIZE`, the second through fourth ring base/size registers, `UVD_OUT_RB_*`, `UVD_IOV_ACTIVE_FCN_ID`, `UVD_IOV_MAILBOX`, `UVD_IOV_MAILBOX_RESP`, `UVD_RB_ARB_CTRL`, `UVD_CTX_INDEX`, `UVD_CTX_DATA`, and CXW write/interrupt context registers.
- Legacy decode surface and scratch fields: MPEG2 error/control, Y/UV base, pitch, width, height, picture count, MPRD initial XY, buffer base/size registers, `UVD_SCRATCH_NP`, clock-switch handshake, general-purpose scratch registers 0-23, audio ring base/size, VCPU secondary interrupt status/ack/en, and SUVD secondary clock-gating/interrupt registers.
- Power, reset, and status fields: `UVD_STATUS`, `UVD_ENC_PIPE_BUSY`, `UVD_FW_POWER_STATUS`, `UVD_CNTL`, `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, `UVD_WIG_CTRL`, `UVD_CGC_STATUS`, `UVD_CGC_UDEC_STATUS`, and `UVD_SUVD_CGC_STATUS`.
- VCPU boot/cache and local-memory-interface registers: `UVD_VCPU_CACHE_OFFSET0..8`, `UVD_VCPU_CACHE_SIZE0..8`, noncache windows, `UVD_VCPU_CNTL`, VCPU PRID/trace/indirect access registers, many `UVD_LMI_*_64BIT_BAR_LOW/HIGH` registers for decode/firmware/ring/source/destination surfaces, VMID multi-select registers, LMI latency/urgent/control/status/perfmon/swap/prefetch fields, RBC RB/IB VMIDs, MC credits, ADP atomic/indirect/page-fault controls, and SPH controls.
- JPEG decode and JRBC fields: `UVD_JPEG_CNTL`, JPEG ring base/wptr/rptr/size, decode count, SPS information, RE timer, scratch, interrupt enable/status, tier controls/status, output buffer control/wptr/rptr, pitch/UV pitch, GFX8/GFX10 tiling and address configuration, output size, JPEG GPCOM, JPEG soft reset, JRBC ring/IB pointers, timers, status, buffer status, preemption command/fence data, and the first `UVD_JRBC_SCRATCH0` field.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime use is indirect:

1. ASIC-specific AMDGPU VCN/JPEG files include `vcn_5_0_0_offset.h` for register addresses and this file for bit positions and masks.
2. Register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `SOC15_WAIT_ON_RREG`, and generated packet helpers combine the address macros with these mask constants.
3. VCN/JPEG driver code programs rings, firmware communication, interrupt routing, power states, reset sequencing, memory windows, VMIDs, tiling, and status waits.

Concrete include users in this tree include `amdgpu/jpeg_v5_0_0.c`, `amdgpu/jpeg_v5_0_1.c`, `amdgpu/jpeg_v5_0_2.c`, `amdgpu/vcn_v5_0_1.c`, and `amdgpu/vcn_v5_0_2.c`. For example, JPEG 5.x code uses `UVD_JRBC_STATUS__RB_JOB_DONE_MASK` to test or wait for ring-idle/job-done state, and register dump lists include `regUVD_JRBC_STATUS`, `regJPEG_DEC_ADDR_MODE`, `regJPEG_DEC_GFX10_ADDR_CONFIG`, `regUVD_JPEG_PITCH`, and related JPEG registers described by this chunk.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values persist in the VCN/JPEG hardware until firmware, the driver, a reset path, power gating, suspend/resume, or ASIC initialization reprograms them.

State represented by this chunk includes clock-gating configuration and status, interrupt enables/latches/acknowledges, host-firmware command mailboxes, job completion bits, ring base addresses and sizes, read/write pointers, arbitration policy, virtual-function mailbox state, context IDs, scratch registers, soft-reset requests and reset-status readback, power-status bits, VCPU cache and noncache memory windows, LMI base-address mappings, VMID assignments, latency/performance counters, urgent and prefetch controls, JPEG tiling/address mode, output dimensions, JRBC timeout controls, and preemption fences.

Access semantics are not encoded in the macro names. Some fields are writable configuration, some are read-only status, some are write-one-to-clear acknowledgements, some are self-clearing command bits, and some are firmware-owned or hardware-updated. Consumers must preserve reserved fields and use the sequencing rules from the VCN 5.0 programming model.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_offset.h`, which supplies the corresponding `reg...` addresses and base-index macros. It also aligns with VCN interrupt source headers under `include/ivsrcid/vcn/`, SOC15 register access helpers, AMDGPU ring management, firmware loading/shared-memory code, power-gating/reset paths, and JPEG decode ring code.

Primary integration points are:

- VCN firmware bring-up and messaging, where GPCOM, VCPU cache/noncache windows, `UVD_VCPU_CNTL`, firmware status, and scratch fields coordinate boot and runtime command exchange.
- VCN/JPEG ring setup, where ring base/size/pointer, JRBC, job-done, context, VMID, and doorbell-adjacent state determine command submission progress.
- Interrupt handling, where VCPU/SYS/SUVD/ENC/JPEG enable, status, ack, and routing masks control what reaches AMDGPU IRQ handlers.
- Power management and reset, where CGC, DPG-adjacent status, soft-reset, power-status, and clock-switch fields govern suspend/resume, idle, dynamic power gating, and recovery.
- Memory and tiling programming, where LMI BAR/VMID/control fields and JPEG GFX8/GFX10 address-mode fields map firmware, rings, source surfaces, destination buffers, and tiled output layouts.

## Risks And Edge Cases

- The chunk boundaries split complete register definitions. `SMP_SUVD_CGC_CTRL` begins before this range, and `UVD_JRBC_SCRATCH0` continues after it. The final per-file report should merge adjacent chunks before claiming completeness for those registers.
- Generated-header drift can compile successfully but misprogram hardware. A wrong mask for reset, interrupt ack, job-done, ring pointer, VMID, LMI BAR, or tiling field can lead to hangs, missed interrupts, memory faults, decode corruption, or reset failures.
- Interrupt enable/status/ack groups repeat similar field names with different semantics. Accidentally using an ACK mask where an enable or status mask is expected can lose interrupts or leave interrupt lines asserted.
- Soft-reset and reset-status bits share registers such as `UVD_SOFT_RESET` and `UVD_JPEG_DEC_SOFT_RST`. Full-register writes can accidentally reset extra subblocks or misinterpret status bits as writable control.
- 64-bit BAR pairs require low/high halves to be programmed consistently. Wrong ordering or stale high halves can direct VCN/LMI/JPEG traffic to the wrong GPU address.
- Ring and JRBC pointer/size fields are shifted and masked rather than full-width. Off-by-shift bugs can corrupt ring addressing, make idle waits fail, or cause command fetch timeouts.
- JPEG GFX8/GFX10 tiling and address configuration fields are generation-specific. Reusing the wrong field set can produce surface layout corruption that only appears for specific swizzle/tiling modes.
- Many status and counter fields are hardware- or firmware-owned. Treating them as persistent driver-owned state can race with firmware updates or acknowledge/clear latched events unexpectedly.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 5.x and JPEG 5.x support so include users catch missing or renamed macros.
- Mechanically compare this header with the authoritative generated register database and the companion `vcn_5_0_0_offset.h` address header.
- Verify every field in lines 2275-4757 has the expected shift/mask pair, accounting for chunk-boundary exceptions at `SMP_SUVD_CGC_CTRL` and `UVD_JRBC_SCRATCH0`.
- Run VCN/JPEG ring tests and boot/resume tests that exercise firmware load, GPCOM messaging, interrupt delivery, ring idle/job-done waits, and JPEG decode completion.
- Exercise suspend/resume, runtime power gating, soft reset, per-queue reset where supported, SR-IOV paths, and GPU recovery after media-ring hangs.
- Use register dumps for `UVD_STATUS`, `UVD_CGC_STATUS`, `UVD_SOFT_RESET`, `UVD_JRBC_STATUS`, `JPEG_DEC_ADDR_MODE`, `JPEG_DEC_GFX10_ADDR_CONFIG`, and JPEG pitch/output registers to confirm sane state transitions.
- Watch for kernel logs reporting VCN firmware boot failures, MMSCH/VCN timeouts, JPEG ring test failures, missed IRQs, memory faults, failed idle waits, decode corruption, and regressions that appear only with tiled surfaces, multi-ring workloads, or power-state transitions.

## Cross-Chunk Notes

The previous chunk is needed for the start of `SMP_SUVD_CGC_CTRL` and surrounding SUVD clock-gating registers. The next chunk is needed for the rest of `UVD_JRBC_SCRATCH0`, additional JRBC/JPEG state, and any trailing VCN 5.0.0 shift/mask content. Final reconciliation should merge all chunks for the source file before making complete claims about the generated VCN 5.0.0 register namespace.

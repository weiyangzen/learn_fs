# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003472`: lines 1-2274, `Docs/researches/chunks/subset-b-003472_research.md`
- `subset-b-003473`: lines 2275-4757, `Docs/researches/chunks/subset-b-003473_research.md`
- `subset-b-003474`: lines 4758-7370, `Docs/researches/chunks/subset-b-003474_research.md`
- `subset-b-003475`: lines 7371-7666, `Docs/researches/chunks/subset-b-003475_research.md`

## Chunk Research

### subset-b-003472: lines 1-2274

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_sh_mask.h lines 1-2274

## Scope And Purpose

This chunk is the opening portion of AMD's generated VCN 5.0.0 register shift/mask header for the `uvd_uvddec` address block. It does not implement executable logic; it publishes C preprocessor constants that downstream AMDGPU VCN code uses to compose, update, and decode MMIO register values without hard-coding bit positions.

The covered range defines the include guard, license, and the first 2,200 register field macros. Each hardware field is generally represented by a `...__SHIFT` constant and a matching `..._MASK` constant. The fields cover top-level VCN/UVD identification, coarse UVD clock-gating controls, and a large set of SUVD clock-gating gate and control registers for decode, encode, AV1, VP9, HEVC, H.264, FBC, and related media sub-blocks.

This is a chunk-level report only. The final per-file report should merge this with later chunks because the file continues beyond line 2274, and this chunk ends inside the `SMP_SUVD_CGC_CTRL` field list.

## Register Groups Covered

The first group, `UVD_TOP_CTRL`, exposes the low bits for the VCN/UVD block standard and standard-version fields. These are likely used for block identification or feature-version reads.

`UVD_CGC_GATE` defines per-subunit clock-gate enable bits for the broader UVD/VCN decode block: `SYS`, `UDEC`, `MPEG2`, `REGS`, `RBC`, memory-interface pieces (`LMI_MC`, `LMI_UMC`), codec datapath units (`IDCT`, `MPRD`, `MPC`, `UDEC_RE`, `UDEC_CM`, `UDEC_IT`, `UDEC_DB`, `UDEC_MP`), and infrastructure units such as `WCB`, `VCPU`, `MMSCH`, `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, and `PPU`.

`UVD_CGC_CTRL` defines mode and timing fields for the same coarse clock-gating domain. It includes `DYN_CLOCK_MODE`, `CLK_GATE_DLY_TIMER`, `CLK_OFF_DELAY`, mode bits for individual UDEC pieces, and mode bits for system, memory, register, parser, and scheduler units.

The repeated `*_SUVD_CGC_GATE` groups are the largest portion of this chunk. They share a 32-bit layout for sub-block gate bits:

- Common SUVD units: `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, `EFC`, `SAOE`, and `SMPA`.
- Codec-specific decode paths: H.264, HEVC, VP9, and AV1 variants such as `SRE_H264`, `SIT_HEVC`, `SCM_VP9`, `SDB_VP9`, `SRE_AV1`, and `SCM_AV1`.
- HEVC split decode/encode bits: `SIT_HEVC_DEC`, `SIT_HEVC_ENC`, and `IME_HEVC`.
- Frame-buffer compression clocks: `FBC_PCLK` and `FBC_CCLK`.

The identical `*_SUVD_CGC_GATE` layout is instantiated for `AVM`, `EFC`, `ENT`, `IME`, `PPU`, `SAOE`, `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, and `UVD`.

The `*_SUVD_CGC_GATE2` groups extend clock-gating coverage for newer blocks. They share a smaller layout with `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `SRE_AV1_ENC`, `CDEFE`, `AVM_0`, `AVM_1`, `SIT_NXT_CMN`, `SIT_NXT_DEC`, and `SIT_NXT_ENC`. In this chunk that layout is instantiated for `AVM`, `DBR`, `ENT`, `IME`, `SAOE`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, and `UVD`.

The `*_SUVD_CGC_CTRL` groups define clock-gating mode bits for the same SUVD domains. Their common layout includes mode bits for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, `EFC`, `SAOE`, `SMPA`, `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `AVM_0`, `AVM_1`, `SIT_NXT_CMN`, `SIT_NXT_DEC`, `SIT_NXT_ENC`, `CDEFE`, plus direct `FBC_PCLK` and `FBC_CCLK` bits. Complete groups in this chunk include `AVM`, `DBR`, `EFC`, `ENT`, `IME`, `PPU`, `SAOE`, `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, and `SMPA`. The chunk reaches only the first nine shift fields of `SMP_SUVD_CGC_CTRL`.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this range. The public interface is a set of preprocessor macros consumed by C code in the AMDGPU driver.

The important naming contract is:

- `REGISTER__FIELD__SHIFT` for fields named with a doubled separator before `SHIFT`, for example `UVD_CGC_GATE__SYS__SHIFT`.
- `REGISTER__FIELD_MASK` for the corresponding bit mask, for example `UVD_CGC_GATE__SYS_MASK`.
- Register comment markers such as `//UVD_CGC_GATE` and `//AVM_SUVD_CGC_CTRL`, which mirror generated register names and make this header navigable.

Callers normally combine these constants with helper macros or inline bit manipulation, for example by clearing `FIELD_MASK` and inserting `(value << FIELD__SHIFT) & FIELD_MASK`. Single-bit fields have masks that are powers of two; multi-bit fields such as `UVD_TOP_CTRL__STANDARD_MASK`, `UVD_CGC_CTRL__CLK_GATE_DLY_TIMER_MASK`, and `UVD_CGC_CTRL__CLK_OFF_DELAY_MASK` cover wider ranges.

## Control Flow

This header has no runtime control flow. Its effect is at compile time: inclusion makes symbolic register bit definitions available to the VCN 5.0 driver code. Runtime control flow lives in the code that includes this file and writes hardware registers.

The practical write pattern is still important:

1. Driver code selects a register address from the matching VCN 5.0 register offset header.
2. It computes a new register value using the shift and mask constants in this file.
3. It writes the value through AMDGPU register accessors.
4. Hardware interprets the selected bits as clock-gating gates, clock-gating modes, delay timers, or version fields.

Because the macros are generated constants, the main "flow" risk is not branching behavior but whether each macro accurately maps to the VCN 5.0 hardware specification.

## State And Persistence Behavior

The file stores no software state and has no persistence behavior of its own. It describes persistent hardware register layout. Values written using these masks affect GPU media-engine state until changed by later driver operations, reset, power management transitions, suspend/resume handling, or firmware-controlled sequencing.

The most stateful users are expected to be VCN initialization, power-gating, clock-gating, suspend/resume, reset, and firmware boot paths. Incorrect values can persist in hardware registers across portions of the driver lifecycle and can surface as decode/encode hangs, broken power saving, or inability to wake sub-blocks.

## Dependencies And Integration Points

This header depends only on the C preprocessor and its include guard. In practice it is coupled to the rest of AMDGPU's generated VCN 5.0 register headers, especially the companion register-offset header for `vcn_5_0_0` and any VCN 5.0 driver source that references these symbols.

Integration points include:

- AMDGPU VCN/UVD initialization paths that configure top-level block state.
- Dynamic clock-gating and power-management code that enables or disables gates for UVD and SUVD sub-blocks.
- Codec block setup for H.264, HEVC, VP9, AV1, encode/decode split paths, and frame-buffer compression clocks.
- Debug or bring-up code that reads registers and decodes bitfields for tracing or register dumps.
- Generated-header synchronization with AMD hardware register databases; manual divergence from those sources would be risky.

Although this repository path is under `ceph-client`, the source itself is Linux AMDGPU DRM code. It is unrelated to Ceph filesystem logic except by repository aggregation.

## Risks And Edge Cases

The highest risk is silent hardware misconfiguration from a wrong bit position or mask. A one-bit shift error in a clock-gating field can enable, disable, or put the wrong media sub-block into dynamic mode.

The repeated SUVD layouts reduce conceptual complexity but increase generated-header review risk. Many registers intentionally share identical field layouts, so accidental copy/paste or generator skew may not be obvious unless compared against the hardware register database or runtime traces.

The chunk boundary is an edge case for documentation and automated analysis: `SMP_SUVD_CGC_CTRL` begins at line 2265, but this chunk includes only `SRE_MODE` through `IME_MODE` shifts and none of its masks. Later chunks must complete that register group before any file-level summary treats it as fully covered.

Clock-gating fields are power-management sensitive. Setting gate bits without matching control-mode bits, sequencing requirements, or firmware expectations can cause hangs that may only appear under suspend/resume, video playback, encode workloads, or low-power transitions.

Several fields represent codec-specific sub-blocks. A failure in an AV1, VP9, HEVC, or FBC-specific gate may not be caught by generic boot or display tests, so media workload coverage matters.

## Test Signals

There are no direct unit tests for this header in the chunk. Useful validation signals are compile-time and hardware/runtime oriented:

- Full kernel or AMDGPU build succeeds with all VCN 5.0 users including this header.
- Static checks find no undefined generated macros in VCN 5.0 clock-gating and power-management code.
- Register write/readback traces show expected masks and shifts for `UVD_CGC_GATE`, `UVD_CGC_CTRL`, `*_SUVD_CGC_GATE`, `*_SUVD_CGC_GATE2`, and `*_SUVD_CGC_CTRL`.
- VCN 5.0 video decode and encode workloads pass for H.264, HEVC, VP9, and AV1 where supported.
- Suspend/resume, GPU reset, runtime power management, and dynamic clock-gating tests do not produce media-engine hangs.
- Power measurements or clock-gating debug counters show intended blocks entering and leaving gated states.
- Generated-header diff checks against the authoritative AMD register database catch accidental manual edits or stale generated output.

### subset-b-003473: lines 2275-4757

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

### subset-b-003474: lines 4758-7370

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_sh_mask.h lines 4758-7370

## Scope And Purpose

This chunk is a large middle section of the generated AMD VCN 5.0.0 shift/mask header. It contains C preprocessor constants that describe bit positions and already-shifted masks for VCN/UVD and JPEG hardware registers. The companion `vcn_5_0_0_offset.h` file supplies the register offsets; this file supplies the bitfield layout used by AMDGPU VCN 5.x and JPEG 5.x driver code to program those registers without hard-coded bit arithmetic.

The range starts just after `UVD_JRBC_SCRATCH0__SCRATCH0_MASK`, then covers the JMI/JPEG memory interface, JPEG common interrupt and memcheck registers, JPEG clock-gating/performance registers, VCN power-gating and dynamic power-gating state, ring-buffer and AGDB controls, MMSCH and UMSCH scheduler registers, VCN MES processor state, S/LMI apertures, context-indirect clock-gating and scratch registers, and the start of the LMI-adapter memory-check register bank. The chunk ends in the middle of `UVD_MEMCHECK_VCPU_INT_STAT`; later lines define the remainder of that register and adjacent ack/memcheck2 fields.

There is no executable logic here. The value of the chunk is as a hardware ABI description: if any `__SHIFT` or `_MASK` value is wrong, driver register writes may affect the wrong field, interrupt handling may acknowledge the wrong source, or firmware bring-up may point hardware at the wrong memory aperture.

## Register Field Groups

The `uvd_uvd_jmi0_uvd_jmi_dec` block defines decode-side JMI and LMI controls. It includes JPEG prefetch gating (`UVD_JPEG_DEC_PF_CTRL`), JRBC/JPEG arbitration and burst/swap controls (`UVD_LMI_JRBC_CTRL`, `UVD_LMI_JPEG_CTRL`), traffic drop bits (`JPEG_LMI_DROP`), VMID selectors for JRBC and JPEG traffic, split low/high 64-bit BAR fields for JPEG read/write, JRBC ring-buffer and indirect-buffer windows, preempt fences, and atomic write BARs. `UVD_JMI_DEC_SWAP_CNTL` and `UVD_JMI_ATOMIC_CNTL*` are especially sensitive because they encode memory-controller byte-swap policy, atomic burst/drop/gating state, and atomic MC/UVD swap fields.

The `uvd_uvd_jmi_common_dec` block covers common memory-interface behavior. It exposes urgent/QoS watermarks and timers (`UVD_JADP_MCIF_URGENT_CTRL`, `UVD_JMI_URGENT_CTRL`, `UVD_JMI_CTRL`), JPEG memcheck safe-address/clamping controls, latency counters and performance monitors, clean-status bits for LMI/JPEG read/write drains, and `UVD_JMI_CNTL__SOFT_RESET_MASK`. JPEG 5.x code uses `UVD_JMI_CNTL__SOFT_RESET_MASK` during JPEG software reset sequencing.

The `uvd_uvd_jpeg_common_dec` and `uvd_uvd_jpeg_common_sclk_dec` blocks describe JPEG reset, interrupt, memory-check, master interrupt, IH, arbitration, clock-gating, memory clock-gating, and performance-bank fields. `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_STATUS`, and `JPEG_SYS_INT_ACK` cover decode JRBC/core/PF/RAS sources; the `*1` variants cover encode-side EJPEG/EJRBC sources. The memcheck registers have separate enable/status/ack banks for decode (`DJRBC0`, `BSFETCH0`, `OBUF0`) and encode (`EJRBC`, `PELFETCH`, `SCALAR`, `BS`) read/write low/high errors. `JPEG_CGC_*` and `JPEG_*_CGC_MEM_CTRL` define clock-gating and memory light/deep sleep controls, while `JPEG_PERF_BANK_*` defines the small JPEG performance-counter interface.

The `uvd_uvd_pg_dec` block is the largest section in this chunk. It covers power status, dynamic power-gating (`UVD_DPG_LMA_CTL`, `UVD_DPG_LMA_DATA`, `UVD_DPG_LMA_MASK`, `UVD_DPG_PAUSE`, `UVD_DPG_LMA_CTL2`), scratch registers, firmware versioning, PF and GPU IOV status, VCPU error detection and instruction-address capture, LMI address-space aperture controls, address config registers, generic performance counters, clock deep-sleep controls, timestamp counter halves, feature and RAS status registers, UMSCH enable/control, JPEG and ring doorbell controls, AGDB controls/masks, ring enable and write-pointer controls, and several ring read/write pointer registers. VCN 5.x driver code uses the `UVD_DPG_PAUSE__NJ_PAUSE_DPG_REQ_MASK` and `UVD_DPG_PAUSE__NJ_PAUSE_DPG_ACK_MASK` fields when entering or leaving dynamic power-gating mode, and uses the ring pointer offsets/masks around ring initialization and submission.

The `uvd_mmsch_dec`, `uvd_vcn_umsch_dec`, and `uvd_vcn_cprs64dec` blocks describe scheduler and embedded-controller state. MMSCH fields include VF VMID/context address/size and mailbox registers. UMSCH fields include MES control, scheduler control, AGDB write pointers, four mailbox/response pairs, spare registers, UTCL1 controls, busy masks, ring base/size/rptr/wptr, master interrupt/IH controls, eight-bit interrupt enable/status/ack/source banks, context ID, and reset/force controls. The CPRS64/MES block resembles a RISC-V machine-state register file: program counter and interrupt routine addresses, MTVEC, control bits, pipe priority, MIE/MIP/MSTATUS/MEPC/MCAUSE/MBADADDR, cycle/time/instret counters, MISA/vendor/arch/implementation/hart IDs, cache operation controls, MTIMECMP, GP registers, local aperture base/mask/control fields, perfcount control, pending interrupt, interrupt data registers, and 16 data-cache aperture descriptors.

The `uvd_vcn_hypdec` block defines hypervisor-facing MES instruction/data base and bounds registers, including aliases such as `VCN_MES_IC_BASE_LO` and `VCN_MES_MIBASE_LO` sharing the same bit layout. The `uvd_slmi_adpdec` block defines eight non-cacheable MMSCH 64-bit BAR windows, VMID packing for those windows, MMSCH and UMSCH LMI status fields, and IOV active-function ID. The `uvdctxind` block defines context-indirect clock-gating memory controls, 16 software scratch registers, `UVD_IH_SEM_CTRL`, and miscellaneous preemption controls. The final `lmi_adp_indirect` portion begins with LMI CRC registers, swap control, and the main `UVD_MEMCHECK_SYS_INT_EN/STAT/ACK`, `UVD_MEMCHECK_VCPU_INT_EN`, and partial `UVD_MEMCHECK_VCPU_INT_STAT` layouts.

## Important APIs, Types, And Functions

This chunk exports only macros. There are no functions, structs, enums, inline helpers, or persistent C objects.

The generated API convention is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit shift for a field within a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned bit mask for that field.
- Split 64-bit registers use `*_LOW__BITS_31_0_*` and `*_HIGH__BITS_63_32_*` fields rather than a C 64-bit type.
- Multi-instance windows are represented as repeated register names, for example `UVD_LMI_MMSCH_NC0_64BIT_BAR_*` through `UVD_LMI_MMSCH_NC7_64BIT_BAR_*`, `VCN_MES_DC_APERTURE0_*` through `VCN_MES_DC_APERTURE15_*`, and `VCN_UMSCH_AGDB_WPTR0` through `VCN_UMSCH_AGDB_WPTR5`.

Consumers combine these macros with register offsets from `vcn_5_0_0_offset.h` and AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, and `SOC15_REG_OFFSET`. Generation-specific users include `amdgpu/vcn_v5_0_1.c`, `amdgpu/vcn_v5_0_2.c`, `amdgpu/jpeg_v5_0_1.c`, and `amdgpu/jpeg_v5_0_2.c`, which include both `vcn_5_0_0_offset.h` and `vcn_5_0_0_sh_mask.h`.

## Control Flow

The header itself has no runtime control flow. The control flow it supports appears in hardware initialization, reset, interrupt, and diagnostics paths:

1. Driver code selects a register offset from `vcn_5_0_0_offset.h`.
2. It composes a 32-bit register value using the `__SHIFT` and `_MASK` definitions from this file.
3. It writes the value to a SOC15 register, indirect register, or DPG SRAM shadow depending on the block and power mode.
4. Hardware updates persistent register state, begins or stops traffic, records status bits, gates clocks, acknowledges interrupts, or changes scheduler/MES state.
5. Driver code later reads status/counter/pointer registers and decodes the result with the matching masks.

Common flows represented by this chunk include JPEG software reset through `UVD_JMI_CNTL__SOFT_RESET_MASK`, JPEG interrupt enable/status/ack programming through `JPEG_SYS_INT_*`, dynamic power-gating pause request/ack polling through `UVD_DPG_PAUSE`, ring write-pointer programming through `UVD_RB_WPTR*` and `VCN_UMSCH_RB_WPTR`, UMSCH mailbox and interrupt handling, and memcheck enable/status/ack handling through the JPEG and UVD memcheck banks.

## State And Persistence Behavior

The macros do not store state, but they describe stateful hardware registers. BAR low/high fields persist configured memory apertures until the block is reset, power-gated, or reprogrammed. VMID fields persist the virtual-memory context used for hardware memory transactions. Ring pointer and doorbell fields persist producer/consumer state used by firmware and driver submission paths. Interrupt enable bits persist routing policy, while status bits latch hardware events until acknowledged through the matching ack register.

Power-gating and clock-gating fields are especially stateful. `UVD_DPG_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_CGC_*`, and `JPEG_CGC_*` describe whether subblocks are running, paused, gated, in memory light/deep sleep, or waiting for an acknowledge. VCN suspend/resume and GPU reset paths must restore required programming after power loss.

The MES/UMSCH and MMSCH fields describe firmware-visible execution context: program counters, exception state, timers, local apertures, mailboxes, busy masks, ring pointers, and interrupt source bits. These registers are not ordinary software variables; stale or incorrectly restored values can desynchronize the host driver, scheduler firmware, and hardware.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_offset.h`. It maps the fields in this chunk to concrete offsets, including JPEG common registers around `regJPEG_SYS_INT_*`, power-gating registers around `regUVD_DPG_*`, ring pointer registers around `regUVD_RB_*`, UMSCH registers around `regVCN_UMSCH_*`, MES registers around `regVCN_MES_*`, S/LMI registers around `regUVD_LMI_MMSCH_*`, context-indirect `ixUVD_*` registers, and LMI indirect `ixUVD_MEMCHECK_*` registers.

The main code integration points are the AMDGPU VCN and JPEG 5.x implementation files. `vcn_v5_0_1.c` and `vcn_v5_0_2.c` include this header for VCN ring setup, DPG pause/resume, ring write-pointer access, and reset/power-management sequences. `jpeg_v5_0_1.c` and `jpeg_v5_0_2.c` include it for JPEG reset and interrupt enable programming, including `UVD_JMI_CNTL__SOFT_RESET_MASK` and `JPEG_SYS_INT_EN__DJRBC0_MASK`. Similar-looking VCN 4.x and 5.3 files should not reuse these masks unless they also use the matching offset/header generation.

This header also integrates with firmware contracts. UMSCH/MES mailbox, ring, interrupt, cache, and aperture fields must match what VCN firmware expects. The names expose hardware concepts, but the legal sequencing and side effects are defined by the hardware/firmware interface rather than by this header.

## Risks And Edge Cases

The primary risk is bitfield drift. These are generated hardware definitions, so a one-bit error can silently program the wrong function. High-risk areas include sparse interrupt layouts, 64-bit low/high BAR pairs, repeated aperture windows, VMID packing fields, and status/ack pairs whose bit positions must match exactly.

Another risk is mixing generations or address spaces. The same logical register names appear in multiple VCN generations and in direct versus indirect address blocks. Code must pair `vcn_5_0_0_sh_mask.h` with `vcn_5_0_0_offset.h` and must use the correct SOC15 block, base index, instance, or indirect accessor. Reusing VCN 4.x masks or offsets with VCN 5.0 code can compile while programming a different hardware field.

Ack/status registers require care. The macros name bits but do not document whether hardware uses write-one-to-clear, write-one-to-acknowledge, sticky status, read side effects, or power-gated access restrictions. Drivers should acknowledge only bits from the matching status bank and avoid broad read/modify/write patterns that could drop a concurrent event.

The chunk boundary itself is an edge case for research and review: line 7370 stops before `UVD_MEMCHECK_VCPU_INT_STAT` is complete. Any final per-file analysis must reconcile this chunk with the following chunk before drawing conclusions about the full VCPU memcheck status/ack layout.

## Test Signals

There are no direct unit tests for this generated header. Useful validation signals are hardware-facing and integration-oriented:

- A kernel build of AMDGPU VCN/JPEG 5.x paths catches missing or renamed macros.
- VCN firmware load, ring initialization, and ring write-pointer update tests exercise `UVD_RB_WPTR*`, `VCN_RB_*`, UMSCH ring, and doorbell fields.
- JPEG decode/encode ring tests exercise `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_STATUS`, `JPEG_SYS_INT_ACK`, and `UVD_JMI_CNTL`.
- Suspend/resume, GPU reset, and dynamic power-gating tests exercise `UVD_DPG_PAUSE`, `UVD_DPG_LMA_*`, clock-gating, scratch, and restore-sensitive state fields.
- Fault-injection or RAS diagnostics should verify JPEG and UVD memcheck status bits latch expected low/high errors and clear only through the matching ack masks.
- Cross-generation review should verify every VCN 5.0 consumer includes the matching `vcn_5_0_0_offset.h` and does not borrow VCN 4.x or VCN 5.3 masks for fields with similar names.

### subset-b-003475: lines 7371-7666

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_sh_mask.h lines 7371-7666

## Scope And Purpose

This chunk is the final section of the generated AMDGPU VCN 5.0.0 shift/mask header. It defines C preprocessor constants for UVD/VCN memory-check interrupt status and acknowledge registers, then closes the `_vcn_5_0_0_SH_MASK_HEADER` guard. The source is data-only: it has no executable C logic, but it is still part of the hardware ABI used by VCN 5.0 and JPEG 5.0 driver code to decode or compose 32-bit indirect register values.

The chunk starts in the middle of the `UVD_MEMCHECK_VCPU_INT_STAT` field definitions and then covers the full `UVD_MEMCHECK_VCPU_INT_ACK`, `UVD_MEMCHECK2_SYS_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_ACK`, `UVD_MEMCHECK2_VCPU_INT_STAT`, and `UVD_MEMCHECK2_VCPU_INT_ACK` macro groups. The matching offsets live in `vcn_5_0_0_offset.h`: `ixUVD_MEMCHECK_VCPU_INT_STAT` is `0x0138`, `ixUVD_MEMCHECK_VCPU_INT_ACK` is `0x0139`, `ixUVD_MEMCHECK2_SYS_INT_STAT` is `0x0140`, `ixUVD_MEMCHECK2_SYS_INT_ACK` is `0x0141`, `ixUVD_MEMCHECK2_VCPU_INT_STAT` is `0x0142`, and `ixUVD_MEMCHECK2_VCPU_INT_ACK` is `0x0143`.

## Important APIs, Types, And Functions

The exported interface is entirely macro based. There are no functions, structs, enums, global variables, or inline helpers in this range. The macro naming convention is the generated AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already shifted one-bit mask for that field.

`UVD_MEMCHECK_VCPU_INT_STAT` exposes VCPU-visible memory-check error status bits for the first memory-check bank. The beginning of this register is defined just before the chunk; this slice completes the higher fields: `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, and `IT_RD`, plus the full mask table for all status fields. It uses paired low/high error bits for `RE`, `IT`, `MP`, `DB`, `DBW`, `CM`, `MIF_REF`, `VCPU`, `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, and `IT_RD`. `IT_RD` is sparse and occupies bits 30 and 31.

`UVD_MEMCHECK_VCPU_INT_ACK` mirrors the same first-bank VCPU bit layout for acknowledge operations. Its fields are named with `_ACK` rather than `_ERR`, but their shifts and masks line up with the corresponding `UVD_MEMCHECK_VCPU_INT_STAT` status bits. This pairing allows interrupt or diagnostic paths to acknowledge exactly the VCPU-visible error bits they observed in the first-bank status register.

The `UVD_MEMCHECK2_*` groups describe the second memory-check bank for read-side and extended memory clients. The covered sources are `CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, `LBSI_RD`, `RBC_RD`, `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, and `PREF`, again with low/high variants for status and acknowledge fields.

## Register Layout Details

`UVD_MEMCHECK2_SYS_INT_STAT` and `UVD_MEMCHECK2_SYS_INT_ACK` share one system-visible layout. Their low fields occupy bits 0 through 11 for `CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, and `LBSI_RD`, then skip bits 12 through 15. `RBC_RD` uses bits 16 and 17. The later extended clients are placed at high bits: `MIF_BSP2` at bits 22 and 23, `MIF_BSP3` at 24 and 25, `MIF_SCLR` at 26 and 27, `MIF_SCLR2` at 28 and 29, and `PREF` at 30 and 31.

`UVD_MEMCHECK2_VCPU_INT_STAT` and `UVD_MEMCHECK2_VCPU_INT_ACK` share a different VCPU-visible layout. They match the system layout through `RBC_RD` at bits 16 and 17, but place `MIF_BSP2` and later fields at bits 18 through 27 instead of bits 22 through 31. This leaves bits 28 through 31 unused by the second-bank VCPU status/ack macros in this VCN 5.0.0 header.

That system-versus-VCPU layout difference is the most important detail in this chunk. The field names are similar across registers, but the masks are not interchangeable between `UVD_MEMCHECK2_SYS_INT_*` and `UVD_MEMCHECK2_VCPU_INT_*` for `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, and `PREF`.

## Control Flow

There is no direct control flow in the header. Runtime flow is imposed by AMDGPU VCN/JPEG code that includes `vcn_5_0_0_offset.h` and `vcn_5_0_0_sh_mask.h`, then combines offsets, masks, and SOC15-style register helpers.

A typical use pattern is:

1. Hardware latches a memory-check error into a `*_INT_STAT` register.
2. Driver interrupt, reset, diagnostics, or firmware-facing code reads the appropriate indirect register.
3. The code tests source-specific masks from this header to identify which memory client reported a low or high bound error.
4. The handler writes the matching `*_INT_ACK` mask bits to the acknowledge register for the same bank and visibility domain.

The ack/status pairing is local to each register family. First-bank VCPU status bits pair with `UVD_MEMCHECK_VCPU_INT_ACK`; second-bank system bits pair with `UVD_MEMCHECK2_SYS_INT_ACK`; second-bank VCPU bits pair with `UVD_MEMCHECK2_VCPU_INT_ACK`.

## State And Persistence Behavior

The macros themselves are compile-time constants and hold no software state. They describe persistent state in hardware registers inside the VCN/UVD block. Status bits represent latched hardware fault state, and acknowledge bits describe the write interface used to clear or acknowledge that latched state. The exact write semantics are determined by the hardware register specification; this header only names bit positions and masks.

The register contents persist while the VCN block remains powered and configured. They may be reset by VCN block reset, GPU reset, power-gating transitions, suspend/resume reinitialization, firmware reload, or explicit writes from the driver. Any code that saves, restores, polls, or clears VCN memory-check state must use the offset header and this shift/mask header as a pair for the active VCN generation.

## Dependencies And Integration Points

The direct dependency is the companion `vcn_5_0_0_offset.h` header, which supplies the register offsets for the macro groups described here. The VCN 5.0 generation driver files include both headers, including `amdgpu/vcn_v5_0_0.c`, `amdgpu/vcn_v5_0_1.c`, `amdgpu/vcn_v5_0_2.c`, and JPEG 5.0 files such as `jpeg_v5_0_0.c`, `jpeg_v5_0_1.c`, and `jpeg_v5_0_2.c`.

The integration point is the AMDGPU register-access layer and VCN/JPEG IP block lifecycle: hardware initialization, firmware bring-up, interrupt handling, diagnostics, reset, and power-management flows can all depend on these constants if they touch memory-check status or acknowledge registers. Similar macro groups exist in VCN 3.x, 4.x, and 5.3 headers, but those files are generation-specific contracts and should not be mixed with this VCN 5.0.0 header without checking the matching offsets and bit layout.

## Risks And Edge Cases

The main risk is treating visually similar register groups as identical. In this chunk, `UVD_MEMCHECK2_SYS_INT_*` and `UVD_MEMCHECK2_VCPU_INT_*` diverge for the extended clients after `RBC_RD`; using a system mask against a VCPU register, or the reverse, would test or acknowledge the wrong bit.

Sparse high-bit fields are another review hazard. `UVD_MEMCHECK_VCPU_INT_STAT` and `UVD_MEMCHECK_VCPU_INT_ACK` place `IT_RD` at bits 30 and 31 after `SRE` at bits 24 and 25. The second-bank system registers also reserve gaps before `RBC_RD` and before `MIF_BSP2`. These gaps should be preserved rather than compacted by hand.

Because this is generated hardware-description data, small textual changes have large behavioral impact. A shifted mask can hide memory-check faults, create stuck interrupts, acknowledge unrelated latched events, or break firmware/driver synchronization. Review should compare changes against generated AMD register definitions or hardware specifications, not infer correctness from neighboring names alone.

## Test Signals

There are no unit tests for this macro-only header. Useful validation signals are hardware and integration oriented:

- A kernel build including VCN 5.0 and JPEG 5.0 implementation files catches missing or renamed macros.
- VCN/JPEG bring-up should complete without interrupt storms or stuck memory-check status after reset.
- Fault-injection or diagnostic testing should show expected bits in `UVD_MEMCHECK_VCPU_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_STAT`, and `UVD_MEMCHECK2_VCPU_INT_STAT`.
- Acknowledge paths should clear the matching status bits using the corresponding `*_INT_ACK` masks, especially for the second-bank fields whose system and VCPU masks differ.
- Suspend/resume, power-gating, and GPU-reset tests should verify that VCN state is reinitialized and stale memory-check interrupts do not remain latched.

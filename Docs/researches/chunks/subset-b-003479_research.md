# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h lines 4709-7202

## Scope And Purpose

This chunk is a 2,494-line segment of AMD's generated VCN 5.3.0 register shift/mask header. It defines C preprocessor constants only: hardware register fields are exported as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no functions, structs, enums, variables, branches, allocations, locks, or direct MMIO operations in this chunk.

The path sits under a `ceph-client` source mirror, but the content is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN/UVD/JPEG code that combines these field masks and shifts with address macros from the companion VCN 5.3.0 register address header and then reads or writes hardware through the SOC15/MMIO register helpers.

The chunk starts inside `UVD_ENC_PIPE_BUSY`: earlier shift definitions and some masks for that busy bitmap are in the previous chunk, while this range begins at `UVD_ENC_PIPE_BUSY__MIF_RD_GEN1_BUSY_MASK`. It continues through VCN/UVD power, reset, clock-gating, VCPU, LMI memory-interface, JRBC ring, JPEG/JMI, interrupt, and memcheck registers. It ends inside `JPEG_MEMCHECK_SYS_INT_ACK2`; the remaining `JPEG_MEMCHECK_SYS_INT_ACK2` masks and following file content are outside this chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: raw 32-bit field mask used for masked reads and writes.

Major register families in this chunk:

- VCN/UVD high-level power, reset, and clock state: `UVD_FW_POWER_STATUS`, `UVD_CNTL`, `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, `UVD_WIG_CTRL`, `UVD_CGC_STATUS`, `UVD_CGC_UDEC_STATUS`, `UVD_SUVD_CGC_STATUS`, `CDEFE_SUVD_CGC_GATE`, `CDEFE_SUVD_CGC_GATE2`, and `CDEFE_SUVD_CGC_CTRL`. These fields describe per-subblock power-off status, software resets and reset-status readbacks, MMSCH lock/reset, WIG/AVM reset and forced clocks, clock-gating status, and clock-gating enable/mode bits for decode, encode, codec, AV1, FBC, CDEFE, MPBE, MPC, AVM, and next-generation SIT/SMP/MPCMIF blocks.
- VCPU command, cache, and debug controls: `UVD_GPCOM_VCPU_CMD`, `UVD_VCPU_CACHE_OFFSET0` through `UVD_VCPU_CACHE_OFFSET8`, `UVD_VCPU_CACHE_SIZE0` through `UVD_VCPU_CACHE_SIZE8`, `UVD_VCPU_NONCACHE_OFFSET0/1`, `UVD_VCPU_NONCACHE_SIZE0/1`, `UVD_VCPU_CNTL`, `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, `UVD_VCPU_IND_INDEX`, and `UVD_VCPU_IND_DATA`. These cover host-to-VCPU command submission, cached/noncached firmware memory windows, VCPU clock enable, resets, abort/runstall, trace/debug selectors, JTAG enable, probe timeout, and indirect VCPU data access.
- LMI/ADP decode memory apertures and control: many `UVD_LMI_*_64BIT_BAR_LOW/HIGH` registers for RE, IT, MP, CM, DB, DBW, IDCT, MPRD, RBC ring/IB, LBSI, VCPU cache/noncache, CENC, SRE, MIF luma/chroma/DBW/coloc/BSP/BSD/scaler/imagepaste/privacy, plus `UVD_ADP_ATOMIC_CONFIG`, `UVD_LMI_ARB_CTRL2`, `UVD_LMI_VCPU_CACHE_VMIDS_MULTI`, `UVD_LMI_VCPU_NC_VMIDS_MULTI`, `UVD_LMI_LAT_CTRL`, `UVD_LMI_LAT_CNTR`, `UVD_LMI_AVG_LAT_CNTR`, `UVD_LMI_SPH`, `UVD_LMI_VCPU_CACHE_VMID`, `UVD_LMI_CTRL2`, `UVD_LMI_URGENT_CTRL`, `UVD_LMI_CTRL`, `UVD_LMI_STATUS`, `UVD_LMI_PERFMON_*`, `UVD_LMI_ADP_SWAP_CNTL`, `UVD_LMI_RBC_RB_VMID`, `UVD_LMI_RBC_IB_VMID`, `UVD_LMI_MC_CREDITS`, `UVD_LMI_ADP_IND_INDEX/DATA`, `UVD_LMI_ADP_PF_EN`, and `UVD_LMI_PREF_CTRL`. These fields describe 64-bit GPU addresses, VMIDs, byte-swap policy, data coherency, CRC controls, clean/idle status, urgent/QoS/stall thresholds, arbitration and credits, latency/perf counters, atomics, page-fault enablement, and prefetch programming.
- JPEG ring-buffer command processors: repeated `UVD_JRBC0_*`, `UVD_JRBC1_*`, `UVD_JRBC2_*`, and `UVD_JRBC3_*` register sets. Each JRBC instance has ring write/read pointers, ring control, IB size/update, urgent control, reference data, conditional-read timers, soft reset/status, buffer status, JPEG preempt command and fence data, ring size, and scratch. These macros are the field contract for programming and diagnosing four JPEG ring/IB engines.
- JPEG decode datapath registers: `UVD_JPEG_CNTL`, `UVD_JPEG_RB_BASE`, `UVD_JPEG_RB_WPTR`, `UVD_JPEG_RB_RPTR`, `UVD_JPEG_RB_SIZE`, `UVD_JPEG_DEC_CNT`, `UVD_JPEG_SPS_INFO`, `UVD_JPEG_SPS1_INFO`, `UVD_JPEG_RE_TIMER`, `UVD_JPEG_DEC_SCRATCH0`, `UVD_JPEG_INT_EN`, `UVD_JPEG_INT_STAT`, `UVD_JPEG_TIER_CNTL0/1/2`, `UVD_JPEG_TIER_STATUS`, `UVD_JPEG_OUTBUF_CNTL`, `UVD_JPEG_OUTBUF_WPTR/RPTR`, `UVD_JPEG_PITCH`, `UVD_JPEG_UV_PITCH`, `JPEG_DEC_Y_GFX8_TILING_SURFACE`, `JPEG_DEC_UV_GFX8_TILING_SURFACE`, `JPEG_DEC_GFX8_ADDR_CONFIG`, `JPEG_DEC_Y_GFX10_TILING_SURFACE`, `JPEG_DEC_UV_GFX10_TILING_SURFACE`, `JPEG_DEC_GFX10_ADDR_CONFIG`, `JPEG_DEC_ADDR_MODE`, `UVD_JPEG_OUTPUT_XY`, `UVD_JPEG_GPCOM_CMD/DATA0/DATA1`, `UVD_JPEG_SCRATCH1`, and `UVD_JPEG_DEC_SOFT_RST`. These cover JPEG decode mode, ring base/pointers/size, stream parameters, output buffers, tiling/address configuration, command mailbox, interrupts, tier controls, and soft reset.
- JPEG memory interface and JMI controls: `UVD_JPEG_DEC_PF_CTRL`, `UVD_LMI_JRBC_CTRL`, `UVD_LMI_JPEG_CTRL`, `JPEG_LMI_DROP`, `UVD_LMI_JRBC_IB_VMID`, `UVD_LMI_JRBC_RB_VMID`, `UVD_LMI_JPEG_VMID`, JPEG/JRBC/preempt/atomic 64-bit BARs, `UVD_JMI_DEC_SWAP_CNTL`, `UVD_JMI_ATOMIC_CNTL`, `UVD_JMI_ATOMIC_CNTL2`, `UVD_JADP_MCIF_URGENT_CTRL`, `UVD_JMI_URGENT_CTRL`, `UVD_JMI_CTRL`, `UVD_JMI_LAT_CTRL`, `UVD_JMI_LAT_CNTR`, `UVD_JMI_AVG_LAT_CNTR`, `UVD_JMI_PERFMON_*`, `UVD_JMI_CLEAN_STATUS`, and `UVD_JMI_CNTL`. These fields define page-fault handling, LMI/JRBC/JPEG arbitration, burst lengths, swaps, drop controls, VMIDs, preempt fences, atomic writes, urgent/QoS policy, latency counters, clean status, and JMI command control.
- JPEG system interrupts and memory-checking: `JPEG_SOFT_RESET_STATUS`, `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_EN1`, `JPEG_SYS_INT_STATUS`, `JPEG_SYS_INT_STATUS1`, `JPEG_SYS_INT_ACK`, `JPEG_SYS_INT_ACK1`, `JPEG_MEMCHECK_CLAMPING_CNTL`, `JPEG_MEMCHECK_SAFE_ADDR`, `JPEG_MEMCHECK_SAFE_ADDR_64BIT`, `JPEG_MEMCHECK_SYS_INT_EN`, `JPEG_MEMCHECK_SYS_INT_EN1`, `JPEG_MEMCHECK_SYS_INT_STAT`, `JPEG_MEMCHECK_SYS_INT_STAT1`, `JPEG_MEMCHECK_SYS_INT_STAT2`, `JPEG_MEMCHECK_SYS_INT_ACK`, `JPEG_MEMCHECK_SYS_INT_ACK1`, and the start of `JPEG_MEMCHECK_SYS_INT_ACK2`. These fields enable, report, and acknowledge JPEG/JRBC/EJRBC/scalar/bitstream/output-buffer read/write errors, plus memcheck high/low address errors and safe-address clamping.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime use is indirect:

1. ASIC-specific AMDGPU VCN/JPEG implementation files include a generated address header for VCN 5.3.0 offsets and this shift/mask header for field layout.
2. Driver startup, firmware boot, power management, reset, ring setup, command submission, interrupt handling, JPEG decode, and diagnostics build register values with these constants.
3. Register helpers such as SOC15 `RREG32`/`WREG32` variants, `REG_SET_FIELD`, and masked write helpers preserve unrelated fields while changing one hardware field.
4. Hardware then owns the actual state transitions: reset-status bits, busy/clean bits, command/ring pointers, interrupt status/acknowledge bits, latency/perf counters, and memcheck status are updated by VCN/JPEG blocks.

Concrete integration expected in this tree is under `drivers/gpu/drm/amd/amdgpu/` VCN generation code, especially VCN 5.x files. Those drivers typically use the companion `vcn_5_3_0_d.h` register addresses together with these macros to enable VCPU clocks, assert/deassert `UVD_SOFT_RESET` subblocks, program VCPU cache windows and LMI BARs, configure LMI/JMI VMIDs and swaps, initialize JRBC/JPEG rings, enable JPEG interrupts, acknowledge completed/error statuses, and set clock-gating or power-gating policy.

## State And Persistence Behavior

The macros themselves hold no software state and persist nothing. They describe stateful VCN/UVD/JPEG hardware registers whose values persist in the media engine until reprogrammed, reset, power-gated, or restored by driver resume/reinitialization.

State represented by this chunk includes firmware power-off status, reset request/status bits, clock-gating gates and status, VCPU command and debug state, VCPU cache/noncache aperture layout, LMI/JMI 64-bit BARs, VMIDs, coherency and swap policy, MC/UMC credits, urgent/QoS and latency/perf counter state, clean/idle status, four JRBC ring/IB pointer and buffer states, JPEG decode output and tiling state, JPEG preemption fences, atomic write targets, interrupt enable/status/acknowledge state, and memcheck safe-address/error state.

Access type is not encoded by the macro names. Some fields are writable configuration bits, some are read-only status, some are hardware-updated counters, some are write-one-to-clear or acknowledge bits, and some are self-clearing command bits. Consumers must preserve reserved bits and follow the ASIC programming sequence for clocks, resets, ring pointer updates, BAR/VMID setup, interrupt acknowledgement, preemption fences, and memcheck clamping.

## Dependencies And Integration Points

This chunk must stay synchronized with the companion VCN 5.3.0 address header, normally `vcn_5_3_0_d.h`, which supplies the actual register offsets such as `regUVD_*`, `mmUVD_*`, or generation-specific equivalents. The mask header is also tied to AMDGPU's SOC15 register-access layer and field-helper macros.

Primary functional integration points are AMDGPU media code paths that manage VCN firmware boot, clock/power gating, VCPU setup, memory-interface aperture programming, JPEG ring setup, JPEG command submission, interrupt routing, error handling, and reset/recovery. The generated names are a compile-time contract: missing or renamed macros usually fail the build, while wrong numeric masks or shifts can compile cleanly and misprogram hardware at runtime.

The repeated JRBC instance layout is also an integration contract. `UVD_JRBC0_*` through `UVD_JRBC3_*` expose parallel ring engines with nearly identical field layouts, so driver loops or instance-specific setup code must match the correct address block to the matching macro namespace.

## Risks And Edge Cases

- The chunk starts mid-register at `UVD_ENC_PIPE_BUSY` and ends mid-register at `JPEG_MEMCHECK_SYS_INT_ACK2`. Final per-file reconciliation must merge adjacent chunks before making complete claims about either register.
- Generated-header drift is high risk. Incorrect reset or clock-gating masks in `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, `UVD_CGC_STATUS`, `UVD_SUVD_CGC_STATUS`, or `CDEFE_SUVD_CGC_*` can leave VCN subblocks held in reset, falsely report reset completion, or gate clocks while decode/encode/JPEG work is active.
- `UVD_VCPU_CNTL` combines error status, clock enable, PMB/RBBM reset, abort, trace/debug, JTAG, timeout, block reset, runstall, and SRE command-interface reset fields. Full-register writes or bad masks can break firmware boot or recovery.
- LMI and JMI BAR fields are full-width halves of 64-bit GPU addresses. Low/high half mismatches, wrong VMIDs, or stale BARs can route media reads/writes to the wrong memory and produce IOMMU faults or silent corruption.
- Cache/noncache offset and size fields use narrow masks while many BAR fields are full 32-bit payloads. Consumers must not assume every address-like register uses the same alignment, width, or unit.
- LMI/JMI swap, coherency, drop, urgent, credits, and arbitration controls affect memory ordering and traffic priority. Wrong settings may only show up under high decode/JPEG bandwidth, preemption, or VM fault pressure.
- JRBC ring and IB fields are sequencing-sensitive. `RB_NO_FETCH`, read/write pointer fields, ring/IB sizes, conditional-read timers, buffer-valid status, and preempt fence data must be programmed in the right order or the command processor can fetch stale commands, hang, or report misleading timeout/error status.
- JPEG interrupt and memcheck registers have separate enable, status, and acknowledge namespaces, with similar names for ordinary system errors and memcheck errors. Confusing `*_STATUS` with `*_ACK`, or system interrupt bits with memcheck bits, can lose error diagnostics or leave interrupts latched.
- Repeated status bitmaps for `JPEG_SYS_INT_*`, `JPEG_MEMCHECK_SYS_INT_*`, and `UVD_JRBC*_UVD_JRBC_STATUS` are easy to copy incorrectly. A one-bit drift can affect only one DJRBC/JRBC lane, output buffer, scalar, bitstream fetch, or high/low address error path.
- Memcheck safe-address and clamping controls are protection-oriented. Incorrectly disabling clamping or programming an unsafe fallback address can turn a detected bad access into memory corruption.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 5.3 support so include users and `REG_SET_FIELD` expansions catch missing or renamed macros.
- Mechanically compare `vcn_5_3_0_sh_mask.h` against the authoritative generated register database and the companion `vcn_5_3_0_d.h` address header.
- Verify every field in lines 4709-7202 has the expected mask/shift pairing, while accounting for the chunk-boundary continuation at `UVD_ENC_PIPE_BUSY` and `JPEG_MEMCHECK_SYS_INT_ACK2`.
- Diff against adjacent VCN 5.x shift/mask headers where ASIC layout parity is expected, especially for `UVD_SOFT_RESET`, `UVD_VCPU_CNTL`, `UVD_LMI_*`, `UVD_JRBC*`, `UVD_JPEG_*`, `UVD_JMI_*`, and `JPEG_MEMCHECK_*`.
- Exercise VCN firmware boot, reset, suspend/resume, clock-gating and power-gating transitions, and watch for VCPU boot failures, stuck reset-status bits, lost clean/idle status, and recovery timeouts.
- Exercise JPEG decode across all exposed JRBC lanes where hardware supports them, including ring setup, IB submission, preemption fence writes, interrupt enable/status/ack handling, and error injection if available.
- Validate LMI/JMI BAR, VMID, coherency, swap, urgent/QoS, and credit programming with VM fault monitoring, ring pointer traces, high-bandwidth media workloads, and GPU reset recovery.
- Exercise JPEG memcheck paths by validating safe-address clamping, high/low read/write error reporting, status latching, and acknowledge behavior for DJRBC, EJRBC, bitstream fetch, output buffer, scalar, and BS write paths.

## Cross-Chunk Notes

The previous chunk is needed for the start of `UVD_ENC_PIPE_BUSY` and earlier VCN 5.3.0 register families. The following chunk is needed for the rest of `JPEG_MEMCHECK_SYS_INT_ACK2` and any later file content. The merge/reconciliation lane should combine all chunks before producing the final source-tree-aligned per-file report for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h`.

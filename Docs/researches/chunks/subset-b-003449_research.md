# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_6_0_sh_mask.h lines 1-2603

## Scope And Purpose

This chunk is the first 2,603 lines of AMD's generated `vcn_2_6_0_sh_mask.h` register field header. It exports C preprocessor constants only: each visible hardware field is represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no functions, structs, enums, local variables, allocations, branches, locks, or direct MMIO reads/writes in this chunk.

The path is under a `ceph-client` source mirror, but the content is AMDGPU VCN/JPEG hardware metadata, not Ceph distributed filesystem logic. Runtime behavior comes from AMDGPU media-codec drivers that combine these field definitions with register offsets from the companion VCN 2.6 offset/address headers and then program the VCN, JPEG, LMI/JMI, MMSCH, and JRBC blocks through SOC15 register helpers.

The line range starts at the file license and include guard, covers VCPU setup, JPEG decode, LMI/MC routing, MMSCH scheduler/SR-IOV control, JPEG memory-interface common logic, JPEG encode setup, and the beginning of the JRBC command processor block. It ends on the `//UVD_JRBC_IB_BUF_STATUS` marker, before that register's fields appear in the following chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit for packing or unpacking a field.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask for preserving, extracting, or updating the field.

Major address-block groups in this chunk:

- `uvd0_ecpudec` defines VCPU cache and non-cache window offsets/sizes, `UVD_VCPU_CNTL` reset/clock/abort/timeout/trace bits, VCPU PRID/trace fields, and indirect index/data access. These are the boot and diagnostics controls for the VCN embedded CPU side.
- `uvd0_jpegnpdec` defines JPEG decode front-end controls: request/error/huffman-speed enables, ring-buffer base/read/write/size fields, decode counters, picture size and chroma format, restart timer, interrupt enable/status fields, tier/table controls, output buffer pointers, pitches, GFX8/GFX10 tiling and address mode fields, GPCOM command/data, indirect index/data, scratch, and decoder soft reset/status.
- `uvd0_lmi_adpdec` is the largest block in this chunk. It defines many 64-bit BAR low/high pairs for RE, IT, MP, CM, DB/DBW, IDCT, MPRD, MPC, RBC, LBSI, VCPU cache/non-cache, CENC, SRE, MIF luma/chroma/reference/BSP/BSD/scaler/privacy/imagepaste paths, and MMSCH non-cache windows. It also defines VMID packing registers, MMSCH coherency control and status, atomic configuration, arbitration/urgent controls, latency/perfmon counters, SPH status, `UVD_LMI_CTRL2`, `UVD_LMI_CTRL`, `UVD_LMI_STATUS`, swap control, RBC VMIDs, MC credits, indirect ADP access, and `VCN_RAS_CNTL`.
- `uvd0_mmsch_dec` defines media micro-scheduler programming surfaces: microcode/SRAM address and data windows, VF/doorbell/context SRAM offsets, interrupts and acknowledgements, VF VMIDs, VF context and GPCOM memory ranges, mailbox registers, `MMSCH_CNTL`, non-cache ranges, processor state/last-access debug, scratch registers, GPUIOV scheduling blocks 0-2, command control/status, VM busy status, active function IDs, context descriptors, VFID FIFO head/tail registers, and NACK status.
- `uvd0_uvd_jmi_dec` defines JPEG memory interface controls: urgent/QoS watermarks, page-fault handling gates, JMI control and reset, JRBC/JPEG/EJRBC/EJPEG/scaler arbitration controls, drop/clamping/memcheck fields, safe-address fields, VMID routing for decode/encode ring buffers, JPEG/JRBC/JPEG2 read/write/preempt 64-bit BARs, decode and encode byte-swap controls, atomic write controls and BARs, RAS controls for DJPEG/EJPEG, latency/perfmon counters, and clean-status fields.
- `uvd0_uvd_jpeg_common_dec` defines shared JPEG reset status, system interrupt enable/status/ack, memcheck interrupt enable/status/ack, master interrupt overrun, IH control, and JRBBM arbitration-drop fields.
- `uvd0_uvd_jpeg_common_sclk_dec` defines JPEG clock-gating controls and status, common/decoder/encoder memory light/deep/shutdown sleep controls, atomic soft reset, and a four-counter performance bank.
- `uvd0_uvd_jpeg_enc_dec` and `uvd0_uvd_jpeg_enc_sclk_dec` define JPEG encoder interrupt enable/status, engine controls, SPS/source format and picture size, table size/control/data/index registers, MC request priority, encode idle status, pitches, luma/chroma base addresses, GFX10 tiling/address config, GPCOM command/data, CGC enable, scratch, and encoder soft reset/status.
- `uvd0_uvd_jrbc_dec` begins the JPEG ring-buffer controller block with ring write pointer/control, IB size, urgent priority, reference data, conditional-read timer, soft reset, status bits for job done, illegal commands, timeouts, traps, preemption, interrupt enable/ack, ring read pointer, and ring buffer status. The `UVD_JRBC_IB_BUF_STATUS` fields are not present in this chunk.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime use is indirect:

1. ASIC-specific VCN/JPEG/UVD code includes register offset headers and this shift/mask header.
2. Driver code reads or writes SOC15 registers through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `SOC15_WAIT_ON_RREG`, `WREG32_P`, and generated field helpers.
3. These macros supply the exact masks and shifts used to preserve reserved bits, build command packets, poll status bits, configure address windows, set VMIDs, acknowledge interrupts, and gate/reset hardware blocks.

Concrete integration patterns visible elsewhere in the AMDGPU tree include JPEG code waiting on `UVD_JRBC_STATUS__RB_JOB_DONE_MASK`, VCN/UVD code setting `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK` or `UVD_LMI_CTRL2__RE_OFLD_MIF_WR_REQ_NUM__SHIFT`, and media scheduler headers exposing `MMSCH_GPUIOV_CMD_CONTROL_*` register addresses whose fields are defined here.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe fields in stateful hardware registers. Register values persist in the VCN/JPEG/LMI/JMI/MMSCH blocks until firmware or the kernel changes them, the block is reset, the device enters a power-gated state, or suspend/resume reinitialization rewrites the programming sequence.

State represented by this chunk includes VCPU memory aperture layout, embedded-CPU control/reset/clock status, JPEG decode and encode ring pointers, source/output picture geometry, tiling modes, table programming, interrupt enable/status/ack latches, LMI/JMI 64-bit memory windows, VMID mappings, byte-swap policy, MC/UMC urgent and arbitration settings, coherency enables, clean/idle status, latency/perf counters, RAS enable/rearm/ready bits, MMSCH firmware/SRAM/mailbox/GPUIOV state, clock-gating and memory sleep controls, and JRBC job/error/preempt status.

Access type is not encoded in the macro names. Some fields are configuration bits, some are read-only hardware status, some are write-one-to-ack interrupt bits, some are command/mailbox payload windows, and some are reset or stall controls with ordering requirements. Consumers must follow the VCN 2.6 programming model and should prefer masked updates over full-register writes where reserved bits exist.

## Dependencies And Integration Points

This chunk depends on companion generated address metadata for the same ASIC generation, especially `vcn_2_6_0_offset.h`, which maps these field names to MMIO register offsets/base indices. It also shares many field names with older UVD and newer VCN/JPEG generations, so driver code often uses common macros or similar sequences across `uvd_*`, `vcn_*`, `jpeg_*`, and `mmsch_*` implementations.

Primary integration points are AMDGPU media-codec initialization, ring setup, firmware boot, scheduler/SR-IOV setup, JPEG decode/encode submission, interrupt handling, reset/resume paths, and power/clock gating. The register fields are consumed by code that:

- programs VCPU cache and non-cache ranges before starting firmware;
- configures JPEG decoder and encoder rings, output buffers, table data, picture metadata, pitches, and tiling/address modes;
- assigns VMIDs and BARs for ring buffers, indirect buffers, bitstreams, image surfaces, preempt fences, atomics, and scheduler non-cache windows;
- stalls or unstalls LMI/JMI arbitration during reset and power sequencing;
- polls clean/idle/status bits before power transitions or reset completion;
- enables, masks, reports, and acknowledges JPEG/JRBC/memcheck/RAS interrupts;
- configures MMSCH microcode/SRAM/mailbox/GPUIOV state for virtualized media scheduling.

The generated numeric constants are the ABI between the driver and the hardware register specification. Missing or renamed macros generally fail at compile time, while incorrect mask/shift values can compile successfully and fail only as media hangs, memory faults, reset timeouts, or corrupt output.

## Risks And Edge Cases

- This chunk ends at a register boundary marker for `UVD_JRBC_IB_BUF_STATUS`. The final per-file report must merge the following chunk before claiming complete JRBC buffer-status coverage.
- Generated-header drift is high risk. A wrong mask for a BAR high/low register, VMID field, swap field, or tiling/address-mode field can point hardware at the wrong memory, use the wrong address space, or corrupt decoded/encoded surfaces.
- Many LMI/JMI BARs are repetitive low/high pairs. Off-by-one copy errors can route a single client path, such as JPEG read, JPEG write, JRBC IB, preempt fence, scaler, privacy, or atomic write, to an incorrect address while adjacent paths still work.
- Reset, stall, clock-gating, and memory-sleep fields are sequencing-sensitive. Incorrect use of `UVD_VCPU_CNTL`, `UVD_JPEG_DEC_SOFT_RST`, `UVD_JPEG_ENC_SOFT_RST`, `UVD_JRBC_SOFT_RESET`, `JPEG_CGC_*`, `JPEG_*_CGC_MEM_CTRL`, `UVD_LMI_CTRL`, or `UVD_LMI_CTRL2` can deadlock a block or leave it inaccessible after resume.
- Interrupt and ack registers have matching names but different semantics. Mixing `*_INT_EN`, `*_INT_STAT`, and `*_INT_ACK` masks can either miss interrupts or clear fault information before it is logged.
- MMSCH GPUIOV fields include repeated blocks 0-2 and misspelled generated field names such as `FUNCTINO_ID`. Consumers must use the generated spelling exactly; "fixing" names in code would break builds.
- Memcheck/clamping/safe-address fields protect against bad memory transactions. Wrong enable or safe-address masks can turn recoverable faults into DMA to unintended memory, or can hide useful error reporting.
- Status and counter fields, including clean/idle bits, performance counters, RAS ready bits, and JRBC job/error bits, may be hardware-owned, latched, or write-one-to-clear. Treating them as normal writable configuration is unsafe.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 2.6/JPEG/MMSCH support enabled so include paths and macro references catch missing symbols.
- Mechanically compare this line range against AMD's authoritative VCN 2.6 register database and the companion `vcn_2_6_0_offset.h` address definitions.
- Check that each field in lines 1-2603 has the expected shift/mask pair, while accounting for register-boundary truncation at `UVD_JRBC_IB_BUF_STATUS`.
- Diff against nearby generated headers for related IP versions where layout parity is expected, especially for `UVD_LMI_CTRL2`, JPEG interrupt registers, JRBC status bits, JPEG CGC registers, and MMSCH GPUIOV blocks.
- Runtime exercise should cover firmware boot, VCPU cache setup, JPEG decode and encode submissions, ring pointer updates, GFX8/GFX10 tiling modes, interrupt enable/status/ack paths, page-fault/memcheck reporting, SR-IOV/MMSCH mailbox paths, suspend/resume, reset recovery, and power/clock gating.
- Watch for kernel logs reporting VCN/JPEG firmware boot failures, `SOC15_WAIT_ON_RREG` timeouts, JRBC illegal command or memory timeout bits, page-fault/memcheck interrupts, RAS events, bad VMID routing, corrupted decoded/encoded images, and hangs that reproduce only under concurrent media and memory pressure.

## Cross-Chunk Notes

This is the first chunk of the file and includes the include guard opening. It does not include the file guard close. The next chunk is required to complete `UVD_JRBC_IB_BUF_STATUS` and the remainder of the VCN 2.6 shift/mask namespace before a final per-file report can make whole-file claims.

# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_6_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003449`: lines 1-2603, `Docs/researches/chunks/subset-b-003449_research.md`
- `subset-b-003450`: lines 2604-4535, `Docs/researches/chunks/subset-b-003450_research.md`

## Chunk Research

### subset-b-003449: lines 1-2603

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

### subset-b-003450: lines 2604-4535

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_6_0_sh_mask.h lines 2604-4535

## Scope

This chunk is the second half of the generated VCN 2.6 shift/mask header. It contains preprocessor constants for bit-field layout of AMD VCN/UVD hardware registers, not executable code. The companion offset header supplies register addresses; this file supplies `__SHIFT` and `__MASK` constants used by AMDGPU code to compose, update, poll, and acknowledge register fields with `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `WREG32_SOC15_DPG_MODE`, `SOC15_REG_OFFSET`, and `SOC15_DPG_MODE_OFFSET`.

The chunk starts in the tail of the JPEG JRBC decode command block, then covers these address blocks:

- `uvd0_uvd_jrbc_enc_dec` at line 2646: JPEG ring-buffer command path for the encode/decode side.
- `uvd0_uvd_mpcdec` at line 2764: memory picture controller and decode data-path mux/cache policy fields.
- `uvd0_uvd_pg_dec` at line 2899: power-gating, DPG local-memory access, page-fault, clock, counter, and RAS fields.
- `uvd0_uvd_rbcdec` at line 3224: UVD ring-buffer command processor, semaphore, IB, writeback, and swap fields.
- `uvd0_uvddec` at line 3368 through the end guard: core UVD status, reset, clock gating, interrupts, ring buffers, mailbox/context, MPEG2 compatibility, version, and scratch registers.

## Purpose

The purpose is to keep VCN 2.6 register field definitions centralized and mechanically consistent with the ASIC register database. Runtime driver code should use these constants instead of literal bit numbers when programming the video decode, encode, JPEG, power-management, interrupt, and command submission hardware. The masks encode writable and readable bit ranges; the shifts encode how to place field values into those ranges.

For example, `vcn_v2_5.c` uses the MPC masks in this chunk while bringing up the engine: it clears `UVD_MPC_CNTL__REPLACEMENT_MODE_MASK`, writes `0x2 << UVD_MPC_CNTL__REPLACEMENT_MODE__SHIFT`, programs `UVD_MPC_SET_MUXA0`, `UVD_MPC_SET_MUXB0`, and `UVD_MPC_SET_MUX`, then unblocks VCPU register access by clearing `UVD_RB_ARB_CTRL__VCPU_DIS_MASK`. The same field constants are used in DPG-mode programming through `WREG32_SOC15_DPG_MODE`.

## Important Register Families

### JRBC and JPEG preemption fields

The opening lines finish the previous JPEG JRBC decode block with `UVD_JRBC_IB_BUF_STATUS`, `UVD_JRBC_IB_SIZE_UPDATE`, `UVD_JRBC_IB_COND_RD_TIMER`, `UVD_JRBC_IB_REF_DATA`, `UVD_JPEG_PREEMPT_CMD`, preemption fence data registers, `UVD_JRBC_RB_SIZE`, and `UVD_JRBC_SCRATCH0`.

The `uvd0_uvd_jrbc_enc_dec` block mirrors that shape for the encode-side JPEG ring buffer:

- Ring pointers and sizes: `UVD_JRBC_ENC_RB_WPTR`, `UVD_JRBC_ENC_RB_RPTR`, `UVD_JRBC_ENC_RB_SIZE`, and `UVD_JRBC_ENC_IB_SIZE`.
- Ring control and priority: `UVD_JRBC_ENC_RB_CNTL` has `RB_NO_FETCH`, `RB_RPTR_WR_EN`, and `RB_PRE_WRITE_TIMER`; `UVD_JRBC_ENC_URGENT_CNTL` has `CMD_READ_REQ_PRIORITY_MARK`.
- Conditional-read timers for RB and IB paths expose retry count, interval, continuous polling, and memory-timeout enable fields.
- Status and interrupt bits in `UVD_JRBC_ENC_STATUS` distinguish RB job done, IB job done, illegal command, conditional-register-read timeout, memory read/write timeout, trap, preempt status, interrupt enable, and interrupt acknowledge.
- Preemption command/fence fields, `UVD_JPEG_ENC_PREEMPT_CMD` and fence data registers, let driver or firmware request preemption and publish fence values.

These macros are part of the command-submission state machine for JPEG work. Misprogramming pointer masks, no-fetch bits, or timeout enables can produce stuck queues, lost preemption fences, or interrupts that are never acknowledged.

### MPC decode block

`uvd0_uvd_mpcdec` describes memory-picture-controller fields:

- `UVD_MP_SWAP_CNTL` and `UVD_MP_SWAP_CNTL2` provide two-bit memory-client swap settings for references 0 through 16.
- `UVD_MPC_LUMA_*` and `UVD_MPC_CHROMA_*` define search, hit, and hit-pending fields for luma/chroma references.
- `UVD_MPC_CNTL` includes replacement mode plus cache disable controls for luma/chroma and their direct-mapped modes.
- `UVD_MPC_PITCH`, `UVD_MPC_SET_MUXA0/A1`, `UVD_MPC_SET_MUXB0/B1`, `UVD_MPC_SET_MUX`, and `UVD_MPC_SET_ALU` configure the mux/ALU inputs used by the decode memory path.
- `UVD_MPC_PERF0` and `UVD_MPC_PERF1` expose max and average latency counters.
- `UVD_MPC_IND_INDEX` and `UVD_MPC_IND_DATA` provide indirect-indexed access to MPC-internal state.

This block is directly integrated by VCN initialization code. The common bring-up sequence programs replacement mode and mux sets before memory-controller resume and before VCPU release. The field widths are small and packed; callers must mask before ORing a new value, as seen with `tmp &= ~UVD_MPC_CNTL__REPLACEMENT_MODE_MASK`.

### Power gating, DPG, counters, page faults, and RAS

`uvd0_uvd_pg_dec` groups low-power and diagnostic control:

- `UVD_PGFSM_CONFIG` and `UVD_PGFSM_STATUS` contain two-bit power configuration/status fields for subblocks such as UVDM, UVDU, UVDF, UVDC, UVDB, UVDIL, UVDIR, UVDTD, UVDTE, UVDE, UVDW, and UVDJ.
- `UVD_POWER_STATUS` and `UVD_JPEG_POWER_STATUS` report power state/mode, power-gating enable, snoop disable controls, and stall-on-power-up controls.
- `UVD_DPG_LMA_CTL`, `UVD_DPG_LMA_DATA`, and `UVD_DPG_LMA_MASK` define the DPG local-memory access window, including read/write selection, mask enable, auto-increment, SRAM selection, and address.
- `UVD_DPG_PAUSE` has request/ack pairs for JPEG and non-JPEG DPG pause.
- `UVD_SCRATCH1` through `UVD_SCRATCH14`, `UVD_FREE_COUNTER_REG`, cache BAR low/high, DPG cache offset, and cache VMID are firmware/driver-visible scratch and address plumbing.
- `UVD_PF_STATUS` records and clears page faults for JPEG, NJ, encoder pipes 0 through 4, EJPEG, and atomic paths.
- `UVD_FW_VERSION`, `UVD_DPG_CLK_EN_VCPU_REPORT`, `UVD_GFX8_ADDR_CONFIG`, and `UVD_GFX10_ADDR_CONFIG` carry firmware version, VCPU clock report, and tiling/address configuration fields.
- `UVD_GPCNT2_*` and `UVD_GPCNT3_*` expose general counters with clear/start/count direction, target, status, and frequency/divider fields.
- `UVD_VCLK_DS_CNTL` and `UVD_DCLK_DS_CNTL` control deep-sleep state for video and decode clocks.
- `UVD_RAS_VCPU_VCODEC_STATUS`, `UVD_RAS_MMSCH_FATAL_ERROR`, `UVD_RAS_JPEG0_STATUS`, `UVD_RAS_JPEG1_STATUS`, and `UVD_RAS_CNTL_PMI_ARB` expose poisoned virtual-function/physical-function status and RAS arbitration ack/status bits.

The state represented here persists in hardware registers across normal register accesses and is reset by engine reset, power-gating transitions, or firmware-controlled sequences. The DPG and power-status fields are especially order-sensitive: software must request pause, poll ack/status, then update DPG state.

### RBC command processor and semaphore block

`uvd0_uvd_rbcdec` defines the decode ring-buffer command processor:

- IB size and remaining size: `UVD_RBC_IB_SIZE` and `UVD_RBC_IB_SIZE_UPDATE`.
- Ring control: `UVD_RBC_RB_CNTL` includes buffer/block size fields, no-fetch, write-pointer polling, no-update, read-pointer writeback enable, and block reset.
- Address and pointer plumbing: `UVD_RBC_RB_RPTR_ADDR`, `UVD_RBC_RB_RPTR_ADDR_HI`, `UVD_RBC_RB_BASE`, `UVD_RBC_RB_BASE_HI`, `UVD_RBC_RB_WPTR`, `UVD_RBC_RB_RPTR`, and write-pointer count/response timer fields.
- Status and fault fields: `UVD_RBC_STATUS`, `UVD_RBC_RB_RPTR_WR`, `UVD_RBC_RB_RPTR_WR_2`, `UVD_RBC_REG_RB_WPTR`, and `UVD_RBC_REG_RB_WPTR_2`.
- Semaphore controls: `UVD_SEMA_ADDR_LOW/HIGH`, command, control, timeout status, signal/wait incomplete and fault timeout controls.
- Job and buffering: `UVD_JOB_START`, `UVD_RBC_BUF_STATUS`, and `UVD_RBC_SWAP_CNTL`.

This block is the boundary between software-created command buffers in memory and VCN hardware consumption. Ring base and pointer fields use alignment shifts, so raw byte addresses or sizes must be pre-aligned before insertion. Semaphore timeout fields are test signals for hang detection and synchronization faults.

### UVD core decode block

`uvd0_uvddec` covers the broadest integration surface:

- Top-level status: `UVD_STATUS`, `UVD_ENC_PIPE_BUSY`, `UVD_FW_POWER_STATUS`, and `UVD_CNTL`.
- Reset controls: `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, and `UVD_WIG_CTRL`. The first reset register includes per-subblock reset bits plus clock-domain reset-status bits.
- Clock gating: `UVD_CGC_GATE`, `UVD_CGC_STATUS`, `UVD_CGC_CTRL`, `UVD_SUVD_CGC_GATE`, `UVD_SUVD_CGC_STATUS`, and `UVD_SUVD_CGC_CTRL` describe per-block clock enable/status/mode for decode, MPC, MPRD, VCPU, MMSCH, SUVD, and encode-related subblocks.
- Firmware communication: `UVD_GPCOM_VCPU_CMD/DATA0/DATA1`, `UVD_GPCOM_SYS_CMD/DATA0/DATA1`, `UVD_DRV_FW_MSG`, `UVD_FW_DRV_MSG_ACK`, and `UVD_VCPU_INT_ROUTE`.
- Interrupt control: `UVD_VCPU_INT_EN/STATUS/ACK`, `UVD_SUVD_INT_EN/STATUS/ACK`, `UVD_ENC_VCPU_INT_EN/STATUS/ACK`, `UVD_MASTINT_EN`, and `UVD_SYS_INT_EN` with corresponding system status and ack fields later in the block.
- Context and ring resources: `UVD_CONTEXT_ID`, `UVD_ENGINE_CNTL`, `UVD_RB_*` for multiple rings 1 through 4, output ring fields, `UVD_IOV_MAILBOX`, `UVD_IOV_MAILBOX_RESP`, `UVD_RB_ARB_CTRL`, `UVD_CTX_INDEX`, and `UVD_CTX_DATA`.
- Legacy/compatibility decode fields: `UVD_CXW_*`, `UVD_MPEG2_ERROR`, `UVD_TOP_CTRL`, `UVD_YBASE`, `UVD_UVBASE`, `UVD_PITCH`, `UVD_WIDTH`, `UVD_HEIGHT`, `UVD_PICCOUNT`, `UVD_MPRD_INITIAL_XY`, `UVD_MPEG2_CTRL`, `UVD_MB_CTL_BUF_BASE`, `UVD_PIC_CTL_BUF_BASE`, `UVD_DXVA_BUF_SIZE`, and `UVD_SCRATCH_NP`.
- Version and firmware scratch: `UVD_CLK_SWT_HANDSHAKE`, `UVD_VERSION`, and `UVD_GP_SCRATCH0` through `UVD_GP_SCRATCH23`.

The interrupt triplets share a consistent enable/status/ack pattern. Driver code must set the enable bit, test the matching status bit, and write the matching ack bit with the correct mask. The master interrupt register gates VCPU and SYS interrupts globally, so sub-interrupt enables are not sufficient by themselves.

## Control Flow and State Behavior

There is no C control flow in this header. The implied runtime control flow comes from consumers that use these constants during VCN initialization, power transitions, interrupt handling, and ring submission:

1. Disable or mask interrupts with `UVD_MASTINT_EN` and sub-interrupt fields.
2. Program memory and MPC fields, especially `UVD_MPC_CNTL` and mux fields.
3. Resume MC state and tiling/address configuration with `UVD_GFX8_ADDR_CONFIG` or `UVD_GFX10_ADDR_CONFIG`.
4. Unblock command/VCPU register access with `UVD_RB_ARB_CTRL__VCPU_DIS_MASK`.
5. Release reset bits in VCPU or UVD reset registers.
6. Poll `UVD_STATUS`, reset-status fields, power-status fields, or interrupt-status fields.
7. On shutdown or suspend, block LMI/UMC and VCPU access, wait for clean status, and assert reset/control bits.

Hardware state persists in memory-mapped registers, ring buffers, indirect register windows, scratch registers, and firmware-visible message registers. Pointer registers and scratch/message registers are mutable state shared between host driver, firmware, and hardware. Status/ack fields are transient but must be consumed correctly to avoid stale interrupt or fault state.

## Dependencies and Integration Points

- Depends on the companion VCN 2.6 offset header for `mmUVD_*` register address macros and base indices.
- Included indirectly by AMDGPU VCN version code through ASIC register include sets.
- Integrated with SOC15 register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, DPG-mode variants, and polling helpers.
- Used by VCN firmware loading and engine bring-up paths, especially the VCN 2.x code that programs MPC replacement/mux fields and `UVD_RB_ARB_CTRL__VCPU_DIS_MASK`.
- Shared conceptually with adjacent generated headers for other VCN generations. Similar macro names appear in VCN 1.0, 2.5, 4.0, and 4.0.5 code, but bit layouts can differ by generation; consumers must include the correct ASIC generation header.

## Risks

- Field layout drift is high impact. A wrong mask or shift can silently program the wrong hardware bit, producing hangs, missed interrupts, broken clock gating, corrupt command streams, or bad power transitions.
- Read-modify-write callers must clear masks before inserting shifted values. ORing fields into stale values is unsafe for multi-bit fields such as replacement mode, mux selectors, timer counts, and power-state fields.
- Pointer and base fields have alignment shifts. Supplying unaligned values without respecting masks can truncate low address bits or size bits.
- Interrupt enable/status/ack names are similar across VCPU, SYS, SUVD, and ENC paths. Mixing ack masks between domains can leave interrupts asserted or clear the wrong condition.
- DPG and power-gating fields are handshake-oriented. Updating power or DPG state without waiting on request/ack or status fields risks register access while blocks are gated.
- RAS/page-fault bits include per-VF and PF reporting. Incorrect clear/ack handling can hide faults or report them to the wrong virtualization context.
- The file is generated-style source. Manual edits are risky unless backed by ASIC register database updates or a direct hardware spec correction.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for all VCN 2.6 include paths; macro spelling or duplicate layout errors should fail compilation where fields are referenced.
- VCN engine bring-up reaches VCPU ready status after programming MPC fields and clearing `UVD_RB_ARB_CTRL__VCPU_DIS_MASK`.
- Ring submission updates RB/IB read and write pointers under the masks in `UVD_RBC_*`, `UVD_RB_*`, and JRBC fields without stuck `RB_NO_FETCH` or stale buffer-valid state.
- Interrupt tests exercise VCPU/SYS/SUVD/ENC enable, status, and ack paths and confirm no interrupt storm or lost ack.
- Suspend/resume and DPG-mode tests verify `UVD_PGFSM_STATUS`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_DPG_PAUSE`, clock-gating status, and reset-status fields transition as expected.
- Fault-injection or error-path tests inspect `UVD_PF_STATUS`, semaphore timeout status, `UVD_RBC_STATUS`, `UVD_JRBC_ENC_STATUS`, and RAS poisoned status fields.
- Firmware communication tests confirm `UVD_GPCOM_*`, `UVD_DRV_FW_MSG`, `UVD_FW_DRV_MSG_ACK`, `UVD_FW_VERSION`, and `UVD_GP_SCRATCH*` fields remain coherent across host/firmware handshakes.

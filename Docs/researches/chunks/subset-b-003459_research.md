# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_sh_mask.h lines 7292-8937

## Scope And Purpose

This chunk is the final 1,646-line segment of AMD's generated VCN 4.0.0 shift/mask header. It contains C preprocessor constants only: each hardware register field is represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. It defines no functions, structs, enums, storage, locking, allocation, or direct MMIO operations.

The path is under a `ceph-client` source mirror, but this file is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN and UMSCH code that combines these masks with companion register address macros from `vcn_4_0_0_offset.h` and register helper macros such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_UMSCH`.

This chunk starts mid-register with `UVD_LMI_MMSCH_NC1_64BIT_BAR_HIGH`, so the low half and NC0 definitions are in the previous chunk. It continues through UVD context/LMI/memcheck fields, UMSCH scheduler fields, MES microcontroller state and memory aperture registers, and closes the file guard with `#endif`.

## Important APIs, Types, And Macros

The exported API is the generated register-field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position used to pack or unpack a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the raw register mask for that field.

Major register groups in this chunk:

- MMSCH LMI apertures and controls: `UVD_LMI_MMSCH_NC1_64BIT_BAR_HIGH` through `UVD_LMI_MMSCH_NC7_64BIT_BAR_HIGH`, `UVD_LMI_MMSCH_NC_VMID`, `UVD_LMI_MMSCH_CTRL`, `UVD_MMSCH_LMI_STATUS`, and `VCN_RAS_CNTL_MMSCH`. These describe non-cacheable 64-bit BAR windows, per-window VMIDs, MMSCH coherency/VM/privilege/swap/read/write/drop controls, clean-status bits, and MMSCH RAS fatal/PMI/rearm/ready fields.
- UVD context clock and scratch registers: `UVD_CGC_MEM_CTRL`, `UVD_CGC_CTRL2`, `UVD_CGC_MEM_DS_CTRL`, `UVD_CGC_MEM_SD_CTRL`, `UVD_SW_SCRATCH_00` through `_15`, and `UVD_IH_SEM_CTRL`. These cover light-sleep, deep-sleep, shutdown, dynamic clock ramp, software scratch storage, and interrupt/semaphore stall/status/VMID/user-data/ring fields.
- LMI adapter and memcheck fields: `UVD_LMI_CRC0` through `UVD_LMI_CRC15`, `UVD_LMI_SWAP_CNTL2`, `UVD_MEMCHECK_SYS_INT_EN`, `UVD_MEMCHECK_SYS_INT_STAT`, `UVD_MEMCHECK_SYS_INT_ACK`, `UVD_MEMCHECK_VCPU_INT_EN`, `UVD_MEMCHECK_VCPU_INT_STAT`, `UVD_MEMCHECK_VCPU_INT_ACK`, and the second-bank `UVD_MEMCHECK2_*` status/ack registers. These expose CRC readbacks, byte-swap policy, and interrupt enable/status/ack masks for UVD memory range checks across RE, IT, MP, DB/DBW, CM, MIF, VCPU, IDCT, MPC, LBSI, RBC, BSP, scaler, and prefetch clients.
- UMSCH front-end scheduler registers: `VCN_UMSCH_MES_UTCL1_CNTL`, `VCN_UMSCH_MES_BUSY`, `VCN_UMSCH_RB_BASE_LO/HI`, `VCN_UMSCH_RB_SIZE`, `VCN_UMSCH_RB_RPTR`, `VCN_UMSCH_RB_WPTR`, `VCN_UMSCH_MASTINT_EN`, `VCN_UMSCH_IH_CTRL`, `VCN_UMSCH_SYS_INT_EN/STATUS/ACK/SRC`, `VCN_UMSCH_IH_CTX_CTRL`, `VCN_UMSCH_CGC_CTRL`, `VCN_UMSCH_CGC_STATUS`, and `VCN_UMSCH_CGC_MEM_CTRL`. These define UTCL1 retry/snoop/drop/invalidate controls, MES busy sub-states, ring buffer base/size/read/write pointers, interrupt controller fields, context ID, and scheduler clock/memory-gating controls.
- UMSCH debug, violation, and force registers: `UVD_INTERNAL_REG_VIOLATION_8`, `UVD_UMSCH_FORCE`, `UVD_UMSCH_DEBUG_INDEX`, `UVD_UMSCH_DEBUG_DATA_LO/HI`, `UVD_UMSCH_DEBUG_UTCL2_TCIU_IF`, and `UMSCH_MES_RESET_CTRL`. These expose internal access-violation address/master/op fields, instruction/data-cache GPUVM force bits, drop-disable force, debug indexed reads, UTCL2/TCIU debug data, and MES core soft reset.
- MES microcontroller control and CSR-like state: `VCN_MES_PRGRM_CNTR_START`, `VCN_MES_INTR_ROUTINE_START`, `VCN_MES_MTVEC`, `VCN_MES_CNTL`, `VCN_MES_PIPE_PRIORITY_CNTS`, `VCN_MES_PIPE0_PRIORITY` through `_PIPE3_PRIORITY`, `VCN_MES_HEADER_DUMP`, `VCN_MES_MIE`, `VCN_MES_INTERRUPT`, `VCN_MES_SCRATCH_INDEX/DATA`, `VCN_MES_INSTR_PNTR`, `VCN_MES_MSCRATCH`, `VCN_MES_MSTATUS`, `VCN_MES_MEPC`, `VCN_MES_MCAUSE`, `VCN_MES_MBADADDR`, `VCN_MES_MIP`, `VCN_MES_MCYCLE`, `VCN_MES_MTIME`, `VCN_MES_MINSTRET`, `VCN_MES_MISA`, `VCN_MES_MVENDORID`, `VCN_MES_MARCHID`, `VCN_MES_MIMPID`, `VCN_MES_MHARTID`, and `VCN_MES_MTIMECMP`. These define boot vectors, pipe reset/active/halt/cache-invalidate bits, priority controls, interrupts, scratch access, program counter, exception/status/timer/counter state, and machine identity readbacks.
- MES memory/cache/aperture setup: `VCN_MES_IC_OP_CNTL`, `VCN_MES_DC_BASE_CNTL`, `VCN_MES_DC_OP_CNTL`, `VCN_MES_LOCAL_*`, `VCN_MES_IC_BASE_*`, `VCN_MES_DC_BASE_*`, `VCN_MES_MIBASE_*`, `VCN_MES_MDBASE_*`, `VCN_MES_MIBOUND_*`, `VCN_MES_MDBOUND_*`, `VCN_MES_DC_APERTURE0_*` through `_15_*`, and `VCN_HYP_ME1_PIPE0/1_VMID_CNTL`. These describe instruction/data cache operations, VMID/cache policy/execute-disable settings, local instruction/data/scratch apertures, base and bound registers, 16 data-cache apertures with VMID and bypass mode, and hypervisor VMID allow/default controls.
- MES debug and miscellaneous data registers: `VCN_MES_DEBUG_INTERRUPT_INSTR_PNTR`, `VCN_MES_GP0` through `GP9`, `VCN_MES_DM_INDEX_ADDR/DATA`, `VCN_MES_DBG_FROM_RST`, `VCN_MES_PERFCOUNT_CNTL`, `VCN_MES_PENDING_INTERRUPT`, `VCN_MES_PRIV_LEVEL`, `VCN_MES_PRIV_LEVEL_VIOLATION_STATUS`, high halves of program/debug pointers, and `VCN_MES_INTERRUPT_DATA_16` through `_31`.

## Control Flow And Runtime Behavior

There is no control flow inside this header. The runtime pattern is indirect:

1. ASIC-specific AMDGPU files include the VCN 4.0.0 offset and shift/mask headers.
2. Code reads a register, uses `REG_SET_FIELD` or equivalent bit manipulation with these masks/shifts, and writes the result back through SOC15/VCN register helpers.
3. Hardware implements the actual side effects: UVD memory-clock gating, memcheck interrupt status, UMSCH ring activity, MES firmware boot, cache invalidation/priming, VM aperture translation, and interrupt delivery.

The strongest concrete consumer in this source tree is `drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.c`. Its UMSCH firmware load path clears `UMSCH_MES_RESET_CTRL.MES_CORE_SOFT_RESET`, programs `VCN_MES_CNTL` reset/halt/active/cache bits, sets `VCN_MES_IC_BASE_CNTL` VMID/execute/cache policy, writes instruction and interrupt start addresses, configures local instruction and data apertures, writes `VCN_MES_IC_BASE_*`, `VCN_MES_DC_BASE_*`, `VCN_MES_MIBOUND_LO`, and `VCN_MES_MDBOUND_LO`, forces IC/DC GPUVM through `UVD_UMSCH_FORCE`, invalidates/primes the instruction cache with `VCN_MES_IC_OP_CNTL`, releases the MES core, and then polls `VCN_MES_MSTATUS_LO` for the firmware-ready value.

The same file's ring setup programs `VCN_UMSCH_RB_BASE_LO/HI` and `VCN_UMSCH_RB_SIZE`, and stores `VCN_UMSCH_RB_WPTR`/`VCN_UMSCH_RB_RPTR` offsets for later ring operation. Older UVD generation files also use the shared `UVD_CGC_MEM_CTRL` field model to toggle memory low-power behavior, making this chunk part of the broader AMD media clock-gating contract.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values remain in the VCN, UVD, UMSCH, MES, LMI, and memcheck blocks until firmware, the driver, reset logic, power gating, or suspend/resume restore paths change them.

State represented by this chunk includes MMSCH non-cacheable BAR base/VMID mappings, MMSCH coherency/drop/swap controls, RAS enable/rearm/ready bits, UVD memory light/deep/shutdown sleep enables, dynamic clock ramp settings, scratch words, IH/semaphore state, LMI CRC readbacks, swap policy, memcheck interrupt enable/status/ack latches, UMSCH ring base/size/pointers, UMSCH busy and clock-gating status, MES boot vectors, control and machine-status registers, cache operation triggers, firmware-visible GP registers, timer/counter/identity state, local and translated memory aperture windows, DC aperture VMID/bypass controls, and hypervisor VMID permissions.

Access type is not encoded in the macro names. Some fields are persistent configuration, some are read-only status, some are write-one-to-ack interrupt bits, some are hardware-updated counters or pointers, and some are sequencing-sensitive commands such as cache invalidate/prime or reset/halt release. Consumers must preserve reserved bits and follow the hardware programming sequence for each register class.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_offset.h`, which supplies address macros such as `regUVD_LMI_MMSCH_NC*_64BIT_BAR_*`, `regVCN_UMSCH_RB_BASE_LO`, and `regVCN_MES_CNTL`. The shift/mask header alone cannot identify where a register lives; it only defines the bit layout once a consumer has the address.

Primary integration points are:

- AMDGPU UMSCH support in `amdgpu/umsch_mm_v4_0.c`, which relies on the `VCN_MES_*`, `UVD_UMSCH_FORCE`, `UMSCH_MES_RESET_CTRL`, and `VCN_UMSCH_RB_*` fields for firmware boot and ring setup.
- AMDGPU SOC15 register helpers and field helpers, especially `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_UMSCH`, `SOC15_WAIT_ON_RREG`, and `SOC15_REG_OFFSET`.
- AMD media clock-gating and power paths that use UVD/VCN CGC memory low-power controls and status bits.
- Interrupt handling and diagnostic paths that may enable, read, and acknowledge `UVD_MEMCHECK*`, `VCN_UMSCH_SYS_INT_*`, `VCN_UMSCH_IH_CTRL`, `UVD_IH_SEM_CTRL`, violation, debug, and pending-interrupt fields.
- Firmware and PSP load paths, because the values programmed into MES instruction/data base, bound, local aperture, GP, cache, and reset/control registers determine how the UMSCH microcontroller fetches and executes its firmware.

The generated macro names are a compile-time contract. Missing or renamed symbols usually fail to build, but wrong numeric masks or shifts can compile cleanly and produce hardware misconfiguration.

## Risks And Edge Cases

- The chunk starts in the middle of the MMSCH NC BAR sequence. `UVD_LMI_MMSCH_NC0_*` and `UVD_LMI_MMSCH_NC1_64BIT_BAR_LOW` are outside this chunk, so the final per-file report should merge neighboring chunks before describing the full NC aperture set.
- MES boot sequencing is sensitive. Incorrect `VCN_MES_CNTL`, `UMSCH_MES_RESET_CTRL`, `VCN_MES_IC_BASE_CNTL`, `VCN_MES_IC_OP_CNTL`, or start-address masks can leave firmware halted, executing from the wrong address, using a bad VMID, or failing the `VCN_MES_MSTATUS_LO` readiness poll.
- Base/mask/bound fields have alignment assumptions: instruction base low starts at bit 12, data base low starts at bit 16, UMSCH ring base low starts at bit 6, and several bound/aperture registers expose full 32-bit masks. Wrong shifts can silently truncate addresses or widen/narrow accessible firmware memory.
- UMSCH ring pointer and size fields use the same `WPTR`-named bit layout in size, read-pointer, and write-pointer registers. Consumers must not infer semantics from the field name alone without the register context.
- Interrupt and memcheck groups contain enable, status, and ack registers with similar field names. Mixing a status mask with an ack write, or acknowledging the wrong low/high error bit, can lose diagnostics or leave interrupt storms uncleared.
- Low-power fields in `UVD_CGC_MEM_CTRL`, `UVD_CGC_MEM_DS_CTRL`, and `UVD_CGC_MEM_SD_CTRL` target many subblocks. Wrong masks can block power savings or gate a memory domain while decode/scheduler firmware still needs it.
- RAS and violation/debug registers may expose latched fault data or rearm behavior. Treating those fields as ordinary writable control bits can hide faults or cause repeated fatal-error signaling.
- `UVD_LMI_MMSCH_CTRL` combines coherency, VM, privilege, swap, read/write, and drop policy. A field-width or polarity error can produce DMA coherency bugs, byte-order corruption, dropped transactions, or access with the wrong privilege/VM context.
- The repeated `VCN_MES_DC_APERTURE0` through `_15` triplets are easy to mis-index. An off-by-one register in generated data can affect only one aperture and appear only with specific firmware memory mappings.
- The file ends with `#endif`; this is the final chunk for the header. Any automated merge should account for the terminating guard but should not treat it as a runtime artifact.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 4.x and UMSCH support enabled so include dependencies, `REG_SET_FIELD` expansion, and direct users of `VCN_MES_*`, `UVD_UMSCH_FORCE`, `UMSCH_MES_RESET_CTRL`, and `VCN_UMSCH_RB_*` symbols are checked.
- Mechanically compare this line range against the authoritative VCN 4.0.0 register database and companion `vcn_4_0_0_offset.h`, verifying every field has the expected mask/shift pair and every register address has a matching bit-layout definition.
- Cross-check repeated families for consistency: MMSCH NC BAR low/high pairs, 16 scratch registers, memcheck enable/status/ack banks, 16 DC aperture base/mask/control triplets, interrupt data registers 16-31, and GP register low/high pairs.
- Runtime smoke should cover UMSCH firmware load, including MES reset/halt release, instruction cache invalidate/prime, instruction/data base programming, PSP and non-PSP firmware-load paths, and the `VCN_MES_MSTATUS_LO` ready poll.
- Ring tests should validate UMSCH ring base, size, read pointer, write pointer, doorbell, and interrupt delivery under command submission.
- Media stress should exercise VCN decode/encode workloads with memory low-power toggles, suspend/resume, power-gating transitions, and clock-gating entry/exit to catch bad CGC memory control masks.
- Fault-path tests should inject or observe memcheck/RAS/internal-violation conditions where possible, confirming enable/status/ack bits map to the intended low/high client errors and that diagnostics are not lost.
- Watch kernel logs for UMSCH firmware load failures, `regVCN_MES_MSTATUS_LO` timeout messages, ring stalls, interrupt storms, memory check errors, VM faults, bad firmware fetches, decode hangs, and regressions that appear only after suspend/resume or power-gating cycles.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of the MMSCH non-cacheable BAR register set. This chunk closes the header and has no following `vcn_4_0_0_sh_mask.h` content, but final reconciliation should still merge all chunks for the source file before making complete claims about the generated VCN 4.0.0 register namespace.

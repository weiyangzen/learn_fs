# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h lines 7305-8614

## Scope And Purpose

This chunk is the final 1,310-line segment of AMD's generated VCN 4.0.5 shift/mask header. It contains C preprocessor constants only: each hardware register field is represented as a `<REGISTER>__<FIELD>__SHIFT` macro and, when present in the generated database, a matching `<REGISTER>__<FIELD>_MASK` macro. It defines no functions, structs, enums, branches, locks, allocations, or direct MMIO access.

The path is under a `ceph-client` source mirror, but this file is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN and JPEG code that combines these field constants with register addresses from `vcn_4_0_5_offset.h` and accesses hardware through SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_REG_OFFSET`, and DPG-mode write helpers.

This chunk starts at the tail of `VCN_MES_LOCAL_INSTR_APERTURE`, after the corresponding `__SHIFT` macro that belongs to the previous chunk. It then covers MES scratch and data apertures, hypervisor decode base/bound registers, MMSCH and UMSCH LMI windows, context-indirect clock/memory controls, software scratch registers, performance/cache diagnostics, LMI arbitration/swap/VMID/coherency controls, memory-latency monitoring, extended non-cache/atomic BARs, memcheck interrupt status/acknowledge fields, and the closing include guard.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position used to pack or unpack a hardware field.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask for the same field where the generator emitted one.

Major register families in this chunk:

- MES local memory and interrupt data: `VCN_MES_LOCAL_SCRATCH_APERTURE`, `VCN_MES_LOCAL_SCRATCH_BASE_LO`, `VCN_MES_LOCAL_SCRATCH_BASE_HI`, `VCN_MES_PERFCOUNT_CNTL`, `VCN_MES_PENDING_INTERRUPT`, `VCN_MES_PRGRM_CNTR_START_HI`, and `VCN_MES_INTERRUPT_DATA_16` through `_31`. These describe aperture selectors, scratch base address halves, performance event selection, pending interrupt bits, program-counter start high bits, and 16 generic interrupt data dwords.
- MES data apertures: `VCN_MES_DC_APERTURE0_BASE/MASK/CNTL` through `VCN_MES_DC_APERTURE15_BASE/MASK/CNTL`. Each aperture has a 32-bit base, 32-bit mask, a 4-bit `VMID`, and a `BYPASS_MODE` bit.
- `uvd_vcn_hypdec` decode registers: `VCN_MES_IC_BASE_*`, `VCN_MES_MIBASE_*`, `VCN_MES_IC_BASE_CNTL`, `VCN_MES_DC_BASE_*`, `VCN_MES_MDBASE_*`, `VCN_MES_MIBOUND_*`, and `VCN_MES_MDBOUND_*`. These describe instruction/data base and bound windows, VMID selection, execute-disable, and cache-policy fields for VCN MES/hypervisor decode.
- `uvd_slmi_adpdec` MMSCH/UMSCH LMI registers: `UVD_LMI_MMSCH_NC0_64BIT_BAR_LOW/HIGH` through `NC7`, `UVD_LMI_MMSCH_NC_VMID`, `UVD_LMI_MMSCH_CTRL`, `UVD_MMSCH_LMI_STATUS`, `UMSCH_IOV_ACTIVE_FCN_ID`, and `UVD_UMSCH_LMI_STATUS`. These expose 64-bit non-cache BARs, per-window VMIDs, coherency and VM enablement, read/write/drop mode bits, unsupported AXI transaction status, active VF/PF selection, and scheduler LMI clean indicators.
- `uvdctxind` context-indirect controls: `UVD_CGC_MEM_CTRL`, `UVD_CGC_CTRL2`, `UVD_CGC_MEM_DS_CTRL`, and `UVD_CGC_MEM_SD_CTRL` cover memory light-sleep, deep-sleep, and shutdown enables for LMI/MC, MPC, MPRD, WCB, UDEC subblocks, SYS, VCPU, MIF, LCM, MMSCH, and MPC1, plus memory sleep entry/exit delays and OCLK/RCLK ramp controls. `UVD_SW_SCRATCH_00` through `_15` expose full 32-bit scratch data slots. `UVD_IH_SEM_CTRL` configures interrupt-handler and semaphore stall/clean state, VMID, user data, and ring ID. `UVD_MISC_FEATURE_CTL` controls row preemption and block-interface preemption behavior.
- `uvd_pg_indirect` counters: `UVD_GPCNT0_*` and `UVD_GPCNT1_*` define control, target, and status fields for two general-purpose counters.
- `ecpu_indirect` diagnostics: `UVD_VCPU_CACHE_MISS_COUNTER_CTL`, `UVD_VCPU_ICACHE_MISS_COUNTER`, `UVD_VCPU_DCACHE_MISS_COUNTER`, `UVD_VCPU_ICMISS_ADDR`, `UVD_VCPU_DCMISS_ADDR`, `UVD_VCPU_CACHE_MISS_CTRL1`, `UVD_VCPU_CACHE_MISS_CTRL2`, `UVD_VCPU_INSTR_CACHE_MISS_COUNT`, `UVD_VCPU_CACHE_MISS1` through `_3`, `UVD_VCPU_DATA_CACHE_MISS_COUNT`, and `UVD_LMI_VCPU_EXT40_MODE`. These describe VCPU cache-miss collection, address capture, loop/repeat tracking, reset controls, and 40-bit address mode.
- `lmi_adp_indirect` data-path controls: `UVD_LMI_CRC0` through `_15`, `UVD_LMI_UVD_SWAP_RD`, `UVD_LMI_UVD_SWAP_WR`, `UVD_LMI_VMID_INTERNAL*`, `UVD_LMI_CACHE_CTRL`, `UVD_LMI_ARB_CTRL`, `UVD_LMI_RD_BURST_CTRL`, `UVD_LMI_WR_BURST_CTRL`, `UVD_LMI_WR_COMB_CTRL*`, `UVD_LMI_ISOC_CTRL`, `UVD_LMI_CLEAN_STATUS*`, `UVD_LMI_SCPU_VM*`, `UVD_LMI_SWAP_CNTL2`, and `UVD_LMI_ADDR_EXT2`. These fields govern CRC readback, read/write byte swapping, internal VMID assignment, cache enable/flush, arbitration wait timers, burst sizing, write combining, isochronous prefetch ranges, clean-status bits, SCPU VM ranges, and address-extension bits.
- MIF windows and coherency controls: `UVD_LMI_MIF_BSP*_40BIT_BAR`, `UVD_LMI_MIF_BSD*_40BIT_BAR`, `UVD_LMI_MIF_REF_40BIT_BAR`, `UVD_LMI_MIF_GPGPU_40BIT_BAR`, `UVD_LMI_MIF_DBW_40BIT_BAR`, `UVD_LMI_VCPU_CACHE_40BIT_BAR`, `UVD_LMI_VCPU_NONCACHE_40BIT_BAR0` through `_7`, `UVD_LMI_MIF_RD_SWAP_CNTL*`, `UVD_LMI_MIF_WR_SWAP_CNTL*`, `UVD_LMI_MIF_SWAP_RD`, `UVD_LMI_MIF_SWAP_WR`, `UVD_LMI_MIF_RD_COMB_EN`, `UVD_LMI_DROP`, and `UVD_LMI_MIF_RD_COHERENCY`. These encode decode/writeback/reference/GPGPU/BSP/BSD BARs, swap and privilege/transaction/urgent attributes, read-combine enablement, explicit read/write drop controls, and per-client coherency disable/clean selection.
- Extended addressing, atomics, and latency monitoring: `UVD_LMI_ISOC_PREF_*_64BIT`, `UVD_LMI_PREF_64BIT_BAR_*`, `UVD_LMI_RDCOMB`, `UVD_LMI_MC_LAT_MON0` through `_7`, `UVD_LMI_MC_LAT_CFG0` through `_3`, `UVD_LMI_VCPU_NC2_64BIT_BAR_*` through `NC7`, `UVD_LMI_ATOMIC_USER0_WRITE_64BIT_BAR_*` through `USER3`, and `UVD_LMI_EXT40_MODE`. These describe 64-bit prefetch windows, read-combine timing/bandwidth controls, memory-controller latency histogram bins and configuration, additional VCPU non-cache BARs, atomic write-user BARs, and extended 40-bit LMI mode.
- Memcheck interrupt reporting: `UVD_MEMCHECK2_SYS_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_ACK`, `UVD_MEMCHECK2_VCPU_INT_STAT`, and `UVD_MEMCHECK2_VCPU_INT_ACK`. These define low/high address-range error bits and acknowledge bits for CM, DB, MIF, IDCT, MPC, LBSI, RBC, BSP2, BSP3, SCLR, SCLR2, and PREF clients, with different bit placement between SYS and VCPU status/ack registers for the later clients.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime use is indirect:

1. VCN 4.0.5-specific AMDGPU files include `vcn_4_0_5_offset.h` for register addresses and this file for field masks/shifts.
2. The driver initializes and tears down VCN/JPEG instances with SOC15 MMIO helpers, programs firmware/cache/non-cache BARs, configures ring buffers and doorbells, toggles clock/power-gating controls, and waits on status registers.
3. When a register field is narrower than a full register, masks and shifts from this header are used to construct read-modify-write values or to test status bits.

Concrete include users in this tree are `amdgpu/vcn_v4_0_5.c` and `amdgpu/jpeg_v4_0_5.c`. The source chunk's address families also match offsets in `vcn_4_0_5_offset.h`, including `regVCN_MES_DC_APERTURE0_BASE` and `regUVD_LMI_MMSCH_NC0_64BIT_BAR_LOW`. Older UVD generation files show the same style for shared context-indirect names such as `UVD_CGC_MEM_CTRL`: the driver reads `ixUVD_CGC_MEM_CTRL`, adjusts sleep-enable bits, and writes it back through UVD context-register helpers.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values remain in VCN/MES/LMI/context-indirect blocks until rewritten, reset, power-gated, or restored during resume and DPG transitions.

State represented by this chunk includes scratch apertures and scratch data, interrupt payloads, DC and instruction/data decode aperture programming, MMSCH and VCPU non-cache BARs, VMID routing, LMI coherency and byte-swap policy, clock-gating memory-sleep policy, scratch mailboxes, performance counter targets and counts, VCPU cache-miss diagnostic counters, CRC and latency-monitor accumulators, read/write clean status, explicit drop controls, 40-bit and 64-bit address-window state, atomic write BARs, and memcheck error/acknowledge latches.

Access type is not encoded by the macro names. Some fields are persistent configuration bits, some are read-only status, some are counters or histogram accumulators, and some are write-one-to-clear or acknowledge fields. Consumers must follow the ASIC programming guide and preserve reserved fields when using full-register writes.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_offset.h`, which supplies addresses for the field names in this shift/mask header. It also needs to remain consistent with sibling VCN 4.x/5.x generated headers where the hardware layout is intentionally shared.

Primary functional integration is in AMDGPU VCN/JPEG initialization, suspend/resume, DPG, clock-gating, firmware load, ring setup, and status-wait paths. `vcn_v4_0_5.c` writes VCN firmware cache BARs, VCPU non-cache BARs, LMI control/status fields, clock-gating fields, ring buffer registers, soft reset fields, power status fields, and interrupt enables. `jpeg_v4_0_5.c` includes the same generated header for JPEG-side power, clock, ring, and interrupt setup.

Several macro groups in this chunk are more diagnostic or firmware-facing than directly used by the visible C code. MES apertures, MMSCH/UMSCH NC windows, cache-miss counters, LMI latency histograms, atomic BARs, and memcheck status/ack fields may be programmed by firmware, debug tooling, virtualization paths, or future driver paths. The generated names are still the compile-time contract for any such code.

## Risks And Edge Cases

- The chunk starts mid-register: `VCN_MES_LOCAL_INSTR_APERTURE__APERTURE_MASK` appears here, while its `__SHIFT` definition is in the previous chunk. Final per-file reconciliation should merge the boundary before describing that register as complete.
- Many register groups are repetitive arrays, especially `VCN_MES_DC_APERTURE0` through `_15`, MMSCH `NC0` through `NC7`, scratch `00` through `15`, VCPU non-cache BARs, atomic user BARs, and memcheck bitfields. Copy-generation or offset drift can affect one lane while nearby lanes still work.
- Address-window fields split 40-bit and 64-bit GPU addresses across low/high registers or encode only high-aligned bits. Wrong shifts or masks can point firmware, VCPU, MMSCH, MIF, or atomic traffic at the wrong memory.
- VMID fields control isolation for MES, MMSCH, MIF, SCPU, VCPU, and internal clients. Incorrect VMID packing can cause GPUVM faults, data exposure across virtualization contexts, or firmware-visible address translation failures.
- `BYPASS_MODE`, coherency-disable, cache-enable/flush, byte-swap, privilege, transaction, urgent, and drop fields affect memory ordering and interpretation. Bad constants can present as data corruption, stale reads, endian/swap errors, or hangs under decode workloads.
- Clock-gating memory light-sleep/deep-sleep/shutdown fields touch many media subblocks. Incorrect masks can block power savings or gate RAM while a subblock is still active.
- Status and acknowledge registers such as `UVD_MMSCH_LMI_STATUS`, `UVD_UMSCH_LMI_STATUS`, `UVD_LMI_CLEAN_STATUS*`, `UVD_LMI_MC_LAT_MON*`, and `UVD_MEMCHECK2_*` may be read-only, latched, counter-like, or write-one-to-clear. Treating them as normal writable configuration registers is unsafe.
- The SYS and VCPU memcheck status/ack registers use different bit positions for the BSP/SCLR/PREF tail fields. Reusing one mask set for the other would acknowledge or test the wrong condition.
- Several generated entries have only `__SHIFT` and no `_MASK` in this chunk. Consumers should not infer a full-width mask unless the companion generated database or programming model says so.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 4.0.5 and JPEG 4.0.5 support so include users and field-helper expressions catch missing or renamed symbols.
- Mechanically compare `vcn_4_0_5_sh_mask.h` against the authoritative generated register database and the companion `vcn_4_0_5_offset.h` address header.
- Check that repetitive register arrays have consistent numbering, masks, and shifts: MES DC apertures, MMSCH NC BARs and VMIDs, scratch registers, VCPU NC BARs, atomic write BARs, latency monitor/config registers, and memcheck status/ack pairs.
- Diff against nearby VCN generated headers (`vcn_4_0_0`, `vcn_4_0_3`, `vcn_5_0_0`, and `vcn_5_3_0`) where parity is expected, while allowing intentional ASIC revisions.
- Runtime exercise should cover VCN firmware loading, VCPU cache and non-cache BAR programming, ring initialization, JPEG ring initialization, suspend/resume, DPG pause/resume, clock-gating mode changes, power-gating transitions, and decode/encode/JPEG workloads under GPUVM.
- Debug or bring-up validation should inspect LMI clean waits, VMID routing, memory coherency, byte-swap behavior, cache-miss counters, MC latency histograms, and memcheck error/ack paths when hardware support and tooling are available.
- Watch for kernel logs reporting VCN firmware boot failures, `SOC15_WAIT_ON_RREG` timeouts, GPUVM faults, ring write-pointer stalls, failed JPEG/VCN idle checks, unexpected memcheck interrupts, and regressions that appear only under virtualization, DPG, suspend/resume, or high memory-pressure media workloads.

## Cross-Chunk Notes

The previous chunk is needed for the start of `VCN_MES_LOCAL_INSTR_APERTURE` and other earlier VCN register groups. This chunk closes the file with the include guard `#endif`, so there is no following `vcn_4_0_5_sh_mask.h` content to merge after it, but the final per-file report should reconcile all chunks before making complete claims about the generated header namespace.

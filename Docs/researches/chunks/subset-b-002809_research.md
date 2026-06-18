# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h lines 2378-4756

## Chunk Scope

This chunk is a generated AMD MMHUB 3.0.2 shift/mask header segment. It covers source lines 2378-4756 and contains only C preprocessor constants for hardware register bitfields. Each complete field follows the AMDGPU generated-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the raw 32-bit mask.

There are no C functions, structs, enums, variables, branches, loops, locks, allocations, or direct MMIO operations in this range. Runtime behavior comes from AMDGPU code that includes this header with `mmhub/mmhub_3_0_2_offset.h`, especially `amdgpu/mmhub_v3_0_2.c`.

The range begins in the tail of `DAGB0_FATAL_ERROR_STATUS4`, includes complete `DAGB0_SDP_CGTT_CLK_CTRL` and `DAGB0_SDP_LATENCY_SAMPLING`, covers a large `DAGB1` read/SDP/control block, then covers `mmhub_pctldec`, L1 TLB status and performance-counter blocks, and the beginning of the MMVM L2/fault/identity-aperture block. It ends inside `MMVM_L2_CNTL4`, so adjacent chunks are required before making whole-file claims.

The chunk contains 2,172 `#define` entries: 1,086 `__SHIFT` constants and 1,086 `_MASK` constants.

## Purpose

The purpose of this header range is to encode MMHUB 3.0.2 register field layout for AMDGPU memory-hub programming. The companion offset header tells the driver where a register is; this shift/mask header tells it how to pack, update, and decode individual fields in that register.

The visible hardware areas are:

- DAGB read-side client arbitration, virtual-channel, credit, pending, performance, fatal-error, and SDP fields.
- MMHUB power-control and deep-sleep metadata through `PCTL_*`.
- MM L1 TLB status and performance counter fields.
- MMVM L2 cache, invalidation, dummy-page fault, protection-fault, and identity-aperture fields.

In the local driver, `gmc_v11_0.c` selects `mmhub_v3_0_2_funcs` when the MMHUB IP version is `3.0.2`. `mmhub_v3_0_2.c` directly includes this header and uses the generated macros through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The chunk exports no callable APIs or data types. Its API surface is the macro namespace itself.

Important DAGB and SDP families include:

- `DAGB0_FATAL_ERROR_STATUS4`: the visible tail decodes dropped, write-address-phase, and no-allocation fatal-error attributes. The beginning of this status word is in the previous chunk.
- `DAGB0_SDP_CGTT_CLK_CTRL` and `DAGB1_SDP_CGTT_CLK_CTRL`: clock-gating and light-sleep timing controls with on delay, off hysteresis, light-sleep assertion hysteresis, light-sleep disable, and busy override.
- `DAGB0_SDP_LATENCY_SAMPLING` and `DAGB1_SDP_LATENCY_SAMPLING`: sampler routing for DRAM/GMI/IO, read/write, atomic return/no-return, and virtual-channel selection.
- `DAGB1_RDCLI0` through `DAGB1_RDCLI23`: repeated read-client control registers with virtual-channel selection, TLB-credit checking, urgency thresholds, max/min bandwidth limits, OSD limiter enablement, and max outstanding request fields.
- `DAGB1_RD_CNTL`, `DAGB1_RD_IO_CNTL`, `DAGB1_RD_GMI_CNTL`, and `DAGB1_RD_ADDR_DAGB`: shared read-path control, IO/GMI credit and burst policy, DAGB enable/jump-ahead/self-init/identity fields, and address-path jump mode.
- `DAGB1_RD_ADDR_DAGB_MAX_BURST0..2` and `DAGB1_RD_ADDR_DAGB_LAZY_TIMER0..2`: packed per-client burst and lazy-timer nibbles for read address traffic.
- `DAGB1_RD_VC0_CNTL` through `DAGB1_RD_VC5_CNTL`, plus `DAGB1_RD_IO_VC_CNTL` and `DAGB1_RD_GMI_VC_CNTL`: per-VC storage, EA credits, bandwidth limiters, OSD limits, and IO/GMI virtual-channel credit thresholds.
- `DAGB1_RD_TLB_CREDIT`, `DAGB1_RD_RDRET_CREDIT_CNTL`, and `DAGB1_RD_RDRET_CREDIT_CNTL2`: TLB and read-return credit pool sizing.
- `DAGB1_RDCLI_*_PENDING`, `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, and `DAGB1_RD_CREDITS_FULL`: full-width or compact status bitmaps for read-client pipeline state.
- `DAGB1_CNTL_MISC`, `DAGB1_CNTL_MISC2`, `DAGB1_RD_CNTL_MISC`, `DAGB1_DAGB_DLY`, `DAGB1_L1TLB_REG_RW`, and `DAGB1_RESERVE1..4`: miscellaneous remap, clock-gating, soft-stall, delay, L1TLB register-access, and reserved full-width fields.
- `DAGB1_PERFCOUNTER_LO/HI`, `DAGB1_PERFCOUNTER0_CFG` through `2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL`: counter value, compare, selector range, mode, enable/clear, trigger, clear-all, and stop-on-saturate fields.
- `DAGB1_SDP_*`: SDP read bandwidth, priority override, read priority, client-to-SDP VC mapping, enable, credits, tag/VCC reserves, error status, request controls, always-on misc fields, general misc fields, arbitration controls, clock gating, and latency sampling.

Important PCTL families include:

- `PCTL_CTRL`: power-gating enablement, allowed deep-sleep mode, RSMU and DAGB idle thresholds, ignore-protection-fault policy for state control, EA0/EA1 acknowledgement override controls, and RSMU read-timer fields.
- `PCTL_MMHUB_DEEPSLEEP_IB`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_IGNORE_DEEPSLEEP_IB`: deep-sleep state, override, and ignore bitmaps for DS0 through DS16 plus ATHUB/CANE and IPS-related indicators where present.
- `PCTL_SLICE0_*` and `PCTL_SLICE1_*`: per-slice DAGB write/read busy masks, deep-sleep allow/IB allow masks, miscellaneous register-engine/tile-idle/light-sleep/critical-lock fields, register-engine execute controls, RAM index/data windows, and register save/exclusion ranges.
- `PCTL_UTCL2_MISC`, `PCTL_RENG_CTRL`, `PCTL_UTCL2_RENG_*`, and `PCTL_UTCL2_STCTRL_*`: UTCL2 power-control register-engine start pointers, locking, idle thresholds, light-sleep, execution triggers, RAM access, and save/restore range metadata.
- `PCTL_STATUS` and `PCTL_PERFCOUNTER*`: status bits for state-control idle, deep-sleep disconnect, PGFSM busy/state, critical register activity, and PCTL performance-counter selection/result control.
- `PCTL_RESERVED_0..3`: reserved full-width or structured fields that should be treated as generated hardware-reserved metadata rather than general scratch space unless a hardware guide says otherwise.

Important L1 TLB and MMVM L2 families include:

- `MMMC_VM_MX_L1_TLB0_STATUS` through `TLB5_STATUS`: busy and parity-error status for six visible MM L1 TLB instances.
- `MMMC_VM_MX_L1_PERFCOUNTER0_CFG` through `3_CFG`, `MMMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, and `MMMC_VM_MX_L1_PERFCOUNTER_LO/HI`: L1 performance counter select, mode, enable, clear, result select, trigger, global enable/clear, stop-on-saturate, low result, high result, and compare fields.
- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and `MMVM_L2_CNTL3`: MMVM L2 cache enablement, fragment processing, PTE/PDE endian and tag policy, default-page-out behavior, queue sizing, identity-mode behavior, invalidation controls, bank select, cache update modes, fragment sizes, force-miss controls, and effective cache sizes.
- `MMVM_L2_STATUS`: L2 busy, per-context-domain busy, and PTE/PDE cache parity-error status.
- `MMVM_DUMMY_PAGE_FAULT_CNTL` and dummy-page fault address registers: dummy-page fault enablement, logical-address comparison, and split low/high address fields.
- `MMVM_INVALIDATE_CNTL`: invalidate register alternation and maximum outstanding invalidate-register controls.
- `MMVM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, `MM_CNTL3`, and `MM_CNTL4`: status-address clearing, subsequent update permission, default routing for range/PDE/translate/NACK/dummy/valid/read/write/execute faults, no-retry and PRT interrupt client bitmaps, active page migration PTE behavior, retry fault interrupt enablement, and VML1 read/write client interrupt masks.
- `MMVM_L2_PROTECTION_FAULT_STATUS`: more-faults, walker error, permission faults, mapping error, client ID, RW, atomic, VMID, VF/VFID, and PRT decode fields.
- `MMVM_L2_PROTECTION_FAULT_ADDR_*` and `DEFAULT_ADDR_*`: logical fault page address and default physical fault page address split into low 32-bit and high 4-bit fields.
- `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: context-1 identity aperture low/high logical page numbers and physical offset.
- `MMVM_L2_CNTL4`: the chunk contains only the first three shift definitions; masks and remaining fields are in the next chunk.

## Control Flow

There is no executable control flow in the header. The only "flow" is C preprocessing: consumers include the header and expand macro constants into register read, write, and read-modify-write code.

Typical runtime flow in the local MMHUB 3.0.2 driver is:

1. `gmc_v11_0.c` selects `mmhub_v3_0_2_funcs` for MMHUB IP version 3.0.2.
2. `mmhub_v3_0_2_init()` records MMHUB register offsets and VM hub distances, including MMVM context, invalidation, and protection-fault registers.
3. `mmhub_v3_0_2_gart_enable()` programs page-table aperture registers, system aperture/default-page registers, L1 TLB control, MMVM L2 cache controls, VMID context controls, identity aperture disablement, and invalidation address ranges.
4. `REG_SET_FIELD` uses the shift/mask pairs from this header to insert field values into 32-bit register values before `WREG32_SOC15`.
5. `REG_GET_FIELD` uses the same pairs to decode status values, notably `MMVM_L2_PROTECTION_FAULT_STATUS` fields in `mmhub_v3_0_2_print_l2_protection_fault_status()`.

The DAGB and PCTL fields in this chunk are mostly metadata for tuning, diagnostics, clock/power control, or future/neighboring driver code. Sequencing rules, polling loops, reset behavior, write-one-to-clear semantics, and SR-IOV access policy live in the C driver and hardware documentation, not in this generated header.

## State And Persistence Behavior

The macros persist no software state. They describe hardware-visible MMHUB state:

- Persistent-until-reprogrammed configuration: DAGB read-client VC selection, urgency, bandwidth, OSD limits, GMI/IO credits, per-client burst/lazy timers, per-VC credits, SDP routing, PCTL deep-sleep permissions, MMVM L2 cache policy, default-page behavior, and identity aperture ranges.
- Volatile status: DAGB pending/FIFO/fullness fields, SDP error status, PCTL status, L1 TLB busy/parity status, MMVM L2 busy/context busy/parity status, and protection-fault status.
- Action/control bits: performance-counter enable/clear, result clear-all, stop-on-saturate, invalidate-all-L1 and invalidate-L2 bits, protection-fault status-address clear, and clock/light-sleep overrides.
- Fault and diagnostic state: dummy-page fault address, protection-fault logical/default addresses, CID/RW/VMID/VF fault decode, VML1 read/write fault interrupt bitmaps, performance counter low/high values, and latency sampler configuration.

In `mmhub_v3_0_2.c`, some fields from this chunk are programmed during GART enable, reset/disable, fault-default policy changes, or fault-status printing. SR-IOV virtual functions skip several protected MMVM L2 and aperture programming paths, so the same masks may be host/PF-owned in virtualized configurations.

## Dependencies And Integration Points

Direct dependencies are minimal: this generated header relies only on the C preprocessor and the whole-file include guard. Practical dependencies are the AMDGPU generated-register and SOC15 access conventions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_offset.h` supplies matching `reg...` offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c` directly includes this header and uses many `MMVM_*` fields from this range.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c` selects the MMHUB 3.0.2 function table based on IP version.
- `REG_SET_FIELD` and `REG_GET_FIELD` depend on the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` spelling.
- `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` combine companion offsets with this field metadata to read, write, or cache MMIO register addresses.
- `amdgpu_vmhub` uses MMVM context, invalidation-engine, and protection-fault offsets initialized by `mmhub_v3_0_2_init()`. This chunk provides field layout for several of the corresponding status/control registers.

Observed local integration points from `mmhub_v3_0_2.c` include:

- `mmhub_v3_0_2_init_system_aperture_regs()`: writes `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_LO32/HI32` and updates `MMVM_L2_PROTECTION_FAULT_CNTL2__ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
- `mmhub_v3_0_2_init_cache_regs()`: programs `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, and the beginning of `MMVM_L2_CNTL4` behavior visible at the end of this chunk.
- `mmhub_v3_0_2_disable_identity_aperture()`: writes the identity aperture low/high and physical-offset registers whose field splits are defined here.
- `mmhub_v3_0_2_set_fault_enable_default()`: updates default handling and crash-on-fault bits in `MMVM_L2_PROTECTION_FAULT_CNTL`.
- `mmhub_v3_0_2_print_l2_protection_fault_status()`: decodes `CID`, `RW`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, and `MAPPING_ERROR` from `MMVM_L2_PROTECTION_FAULT_STATUS`.
- `mmhub_v3_0_2_gart_disable()`: disables MMVM L2 cache with `MMVM_L2_CNTL__ENABLE_L2_CACHE` and clears `MMVM_L2_CNTL3`.

## Risks And Edge Cases

- Boundary incompleteness: line 2378 starts after most of `DAGB0_FATAL_ERROR_STATUS4`, and line 4756 stops before the masks and remaining fields of `MMVM_L2_CNTL4`. The final per-file report must merge adjacent chunks.
- Generated-header drift can compile cleanly but corrupt runtime behavior. A wrong mask in VM L2, protection-fault, identity-aperture, or DAGB credit fields can program the wrong bit while all C types remain valid.
- Header/offset mismatches are high risk. Pairing `mmhub_3_0_2_sh_mask.h` with another MMHUB generation's offset header can address the wrong register or decode a different layout.
- Repeated client and VC fields are easy to mis-audit. `DAGB1_RDCLI0..23`, per-client burst/lazy timer registers, and per-VC controls look regular but still need exact generated values.
- Fault-control fields are stability and security sensitive. Misprogramming default fault handling, no-retry/retry crash policy, PRT interrupts, or active page migration retry behavior can hide faults, create fault storms, or force GPU resets.
- Invalidation/cache fields can leave stale translations. `MMVM_L2_CNTL2`, L2 force-miss/update fields, and identity-aperture programming must agree with page-table and TLB invalidation flows.
- Address split fields require correct caller-side address shifts. Low 32-bit plus high 4-bit page-number fields are vulnerable to off-by-12 or off-by-44 mistakes in consuming code.
- Power-control fields lack access semantics in the header. PCTL deep-sleep, register-save, slice, RENG, and critical-lock fields may require block-idle sequencing or firmware coordination not visible here.
- Status, clear, and counter fields should not be treated as normal configuration. Full-width pending/status masks, performance-counter clear bits, and protection-fault clear bits may be sticky, write-one-to-clear, transient, or destructive depending on hardware semantics.
- SR-IOV behavior is asymmetric. The local driver skips several MMVM L2 and aperture writes for virtual functions, so tests must distinguish PF-owned and VF-accessible registers.

## Test Signals

Useful validation signals for this chunk are build-time, static-generation, and hardware-integration oriented:

- Build AMDGPU with MMHUB 3.0.2 support enabled so `mmhub_v3_0_2.c` includes `mmhub_3_0_2_offset.h` and `mmhub_3_0_2_sh_mask.h`. Missing or renamed macros should fail around `REG_SET_FIELD` and `REG_GET_FIELD` users.
- Static checks should verify every complete field in lines 2378-4756 has a matching `__SHIFT` and `_MASK`, masks align with shifts, and repeated `DAGB1_RDCLI*`, `PCTL_SLICE*`, and `MMMC_VM_MX_L1_PERFCOUNTER*` families remain structurally consistent.
- Regeneration diffs should compare this header range against the authoritative MMHUB 3.0.2 register database, with special attention to VM L2 cache/fault fields, identity aperture splits, PCTL deep-sleep maps, and repeated DAGB client registers.
- Boot and GART bring-up on MMHUB 3.0.2 hardware should validate system aperture programming, default-page fault address setup, L1 TLB enablement, L2 cache enablement, context setup, and identity aperture disablement.
- VM memory workloads should stress page-table updates, TLB invalidations, retry/no-retry fault behavior, XNACK-related policy, and high memory pressure to expose stale translation or fault-routing errors.
- Fault-path tests should trigger invalid GPU accesses and confirm `MMVM_L2_PROTECTION_FAULT_STATUS` decodes CID, RW, permission, mapping, walker, VMID, VF/VFID, and PRT fields consistently.
- Suspend/resume, reset, and clock/power stress should exercise PCTL deep-sleep, DAGB clock-gating, light-sleep, and state-save metadata where those fields are programmed by platform code or firmware.
- Debug/perf tests can exercise DAGB1, PCTL, and L1 TLB performance-counter select/enable/clear/result paths and verify counter values and stop-on-saturate behavior.
- High-traffic media/display/SDMA workloads are useful for DAGB/SDP arbitration and credit field regressions because the MMHUB client table for this generation includes clients such as DCEDMC, HDP, LSDMA, JPEG, VCN, VCNU, and VSCH.

## Cross-Chunk Notes

The previous chunk should complete the beginning of `DAGB0_FATAL_ERROR_STATUS4`, including the `PRI`, `CHAIN`, and related shift/mask context that precedes the visible `DROP`, `WADDR_PHASE`, and `NOALLOC` masks. The next chunk should complete `MMVM_L2_CNTL4` and continue later MMVM L2, MM group, bank-select, parity/ECC, context, and invalidation-engine definitions. Whole-file research for `mmhub_3_0_2_sh_mask.h` should treat this as one generated register-map slice, not as independent executable logic.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 7094-9528

## Scope And Purpose

This chunk is a generated-style MMHUB 1.0 register bitfield header for AMDGPU. It contains preprocessor constants only: each hardware register field is represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no C functions, structs, storage objects, or executable branches in this source range.

The range covers the middle of the MMHUB 1.0 mask namespace. It starts inside the `MMEA1_DSM_CNTLA`/DSM error-injection area, then defines power/control, L1 TLB, ATC L2, VM L2 fault/cache, VM context, TLB invalidation-engine, and page-table-address register fields. These constants are the hardware contract used by AMDGPU code to program MMHUB MMIO registers through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

The chunk is source-tree-aligned to the MMHUB 1.0 ASIC headers. It is paired with `mmhub_1_0_offset.h` for register addresses and `mmhub_1_0_default.h` for reset/default values.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the macro namespace:

- `MMEA1_DSM_CNTL2`, `MMEA1_DSM_CNTL2A`, and tail `MMEA1_DSM_CNTLA` masks describe DSM error injection and single-write/irritator controls for DRAM, RRET/WRET, GMI, and IO command/data/page memories. `MMEA1_CGTT_CLK_CTRL`, `MMEA1_EDC_MODE`, `MMEA1_ERR_STATUS`, and `MMEA1_MISC2` define clock-gating override, error-detection/correction mode, SDP response error status, and arbitration/burst-limit fields for the second memory-mapped engine instance.
- `PCTL_MISC`, `PCTL_MMHUB_DEEPSLEEP`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_DAGB` define MMHUB power-control/deepsleep and power-gating fields, including RSMU/DAGB idle thresholds, protection-fault ignore controls, deep-sleep bitsets `DS0` through `DS16`, and `SETCLEAR` semantics.
- `PCTL[0-2]_RENG_*`, `PCTL[0-2]_MISC`, and `PCTL[0-2]_STCTRL_REGISTER_SAVE_*` define three repeated power-controller register-engine banks. These cover RAM index/data accesses, execute controls (`EXECUTE_ON_PWR_UP`, `EXECUTE_ON_PWR_DOWN`, restart, busy, and program counter), replay/debug options, and register save/restore ranges or exclusion sets.
- `MC_VM_MX_L1_TLB[0-7]_STATUS` and `MC_VM_MX_L1_PERFCOUNTER*` define L1 TLB hit/miss status and event-counter controls/results. The status fields distinguish CAM and FIFO hits/misses; the counter config fields expose `PERF_MODE` and `PERF_SEL`.
- `ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CACHE_DATA*`, `ATC_L2_CNTL3`, `ATC_L2_STATUS*`, `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL` define address-translation-cache L2 request counts, cache update behavior, VMID modes, cache data readout, busy/invalidation status, memory power, and clock-gating controls.
- `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, `VM_L2_STATUS`, and `VM_L2_CACHE_PARITY_CNTL` define MMHUB virtual-memory L2 cache enablement, fragment handling, endian/swap modes, LRU/update behavior, invalidation controls, bank select, effective sizes, force-miss bits, tap/snoop behavior, parity/interrupt behavior, and status bits.
- `VM_DUMMY_PAGE_FAULT_*`, `VM_L2_PROTECTION_FAULT_*`, `VM_L2_CONTEXT1_IDENTITY_APERTURE_*`, and `VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*` define how L2 VM faults are redirected, logged, interrupted, decoded, and optionally translated through identity apertures. Important decoded fault-status fields include `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, `MAPPING_ERROR`, `CID`, `RW`, `ATOMIC`, `VMID`, `VF`, and `VFID`.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` define per-VMID context enable, page-table depth/block size, retry policy, and default/interrupt responses for range, dummy-page, PDE0, valid, read, write, and execute protection faults. `VM_CONTEXTS_DISABLE` supplies the per-context disable bitmap.
- `VM_INVALIDATE_ENG[0-17]_{SEM,REQ,ACK}` and `VM_INVALIDATE_ENG[0-17]_ADDR_RANGE_{LO32,HI32}` define 18 repeated invalidation engines. Request fields select VMIDs, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, and whether to clear the protection-fault status address; ACK fields report per-VMID completion.
- `VM_CONTEXT[0-15]_PAGE_TABLE_BASE_ADDR_{LO32,HI32}` and `VM_CONTEXT[0-15]_PAGE_TABLE_START_ADDR_{LO32,HI32}` define the low/high halves for page-directory entries and logical start page numbers. The chunk ends at the first fields for `VM_CONTEXT2_PAGE_TABLE_END_ADDR_HI32`; later context end-address definitions continue in the next chunk.

## Control Flow And State Behavior

This header chunk has no local runtime control flow. Runtime behavior appears in consumers that combine these bitfield constants with register offsets:

- `amdgpu/mmhub_v1_0.c` initializes MMHUB 1.0 GART and VM state. It writes `VM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*`, `VM_CONTEXT0_PAGE_TABLE_START_ADDR_*`, and `VM_CONTEXT0_PAGE_TABLE_END_ADDR_*` for VMID0, programs `VM_CONTEXT1_CNTL` and page-table aperture registers for user VMIDs, enables `VM_L2_CNTL`/`VM_L2_CNTL2`/`VM_L2_CNTL3`/`VM_L2_CNTL4`, and configures invalidation-engine address ranges.
- `amdgpu/mmhub_v1_0.c` also uses the protection-fault masks in this chunk to set the dummy/default fault page and to toggle whether range/PDE/dummy/valid/read/write/execute faults are redirected to the default page or made crash-worthy.
- `amdgpu/gmc_v9_0.c` uses `VM_L2_PROTECTION_FAULT_STATUS` field masks to decode page-fault status into client ID, read/write direction, permission/mapping/walker bits, and fault metadata for logging and fault-cache updates.
- `amdgpu/gmc_v9_0.c` forms invalidation requests with `VM_INVALIDATE_ENG0_REQ` masks: it selects the target VMID bit, flush type, L2 PTE/PDE invalidations, L1 PTE invalidation, and the clear-fault-status-address bit. Hardware then reports completion through the corresponding ACK register fields.
- `amdgpu/amdgpu_gmc.h` includes mode2 save/restore storage for many registers represented here, including `VM_L2_CNTL`, `VM_L2_CNTL2`, dummy fault registers, L2 protection fault registers, `VM_CONTEXT_CNTL[16]`, context page-table base/start/end arrays, and `MC_VM_MX_L1_TLB_CNTL`.

The state described by these macros is persistent only as GPU register state. The header does not store state, serialize access, or enforce ordering. Driver code must sequence MMIO writes around GPU reset, GART enable/disable, VMID setup, page-table updates, TLB invalidation, power management, and interrupt handling.

## Dependencies And Integration Points

This chunk depends on the larger AMDGPU register-description scheme:

- `mmhub/mmhub_1_0_offset.h` supplies `mm*` register offsets, for example `mmVM_L2_CNTL`, `mmVM_CONTEXT0_CNTL`, `mmVM_INVALIDATE_ENG0_REQ`, and `mmVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`.
- `mmhub/mmhub_1_0_default.h` supplies default values such as `mmVM_L2_CNTL_DEFAULT`, `mmVM_L2_CNTL3_DEFAULT`, `mmVM_CONTEXT0_CNTL_DEFAULT`, and `mmVM_INVALIDATE_ENG0_REQ_DEFAULT`.
- SOC15 access helpers (`RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and offset variants) provide MMIO reads/writes against these registers.
- `REG_SET_FIELD` and `REG_GET_FIELD` expect the exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` naming used in this header. Renaming a field or changing the register prefix breaks table-free field access at compile time.
- VM hub setup in `mmhub_v1_0.c`, later MMHUB revisions such as `mmhub_v1_7.c`/`mmhub_v1_8.c`, and common GMC code in `gmc_v9_0.c` rely on these masks to keep MMHUB programming aligned with hardware layouts.
- Power-management code can use the PCTL, deepsleep, ATC, and clock-gating masks when enabling MMHUB clock/power gating. The chunk's PCTL save/restore ranges are especially relevant to power-gated register preservation.

The repeated register layout also defines software assumptions about register spacing. `mmhub_v1_0_init()` computes distances between `VM_CONTEXT0` and `VM_CONTEXT1` registers and between invalidation engines; code then uses those distances to program repeated contexts/engines with `WREG32_SOC15_OFFSET`.

## Risks And Edge Cases

- Hardware contract drift is the primary risk. A wrong shift or mask can direct page-table base writes to the wrong bits, leave VM fault handling disabled, fail to invalidate stale translations, or corrupt power-control state.
- The chunk contains many repeated register families. Copy/paste or generation errors can affect only one VM context, invalidation engine, or PCTL bank while the rest look correct. Static checks should compare repeated groups for expected sameness and spacing.
- Some fields span the full register (`0xFFFFFFFFL`) while others use high bits with an `L` suffix. Consumers should use unsigned 32-bit values when shifting/masking to avoid sign-extension and host-width surprises.
- VM fault handling is safety-critical. Misprogramming `VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, or `VM_CONTEXT*_CNTL` can change whether faults are retried, redirected to a dummy/default page, logged, interrupted, or escalated to GPU reset/hang paths.
- Invalidation request fields are synchronization-critical. Omitting `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE*`, or `INVALIDATE_L1_PTES`, selecting the wrong VMID bit, or polling the wrong ACK mask can leave stale translations active after page-table updates.
- Page-table base/start/end fields are split across LO32 and HI32 registers and encode page numbers rather than raw byte addresses in consumers. Callers must preserve the driver convention of shifting addresses to the correct page granularity before writing.
- Power/deepsleep and register-save fields can interact with runtime power management. Incorrect `PCTL_*` save ranges, exclusion sets, or deep-sleep override bits may make state vanish across power gating or prevent MMHUB from entering low-power states.
- The range starts and ends mid-family: it begins with tail masks for `MMEA1_DSM_CNTLA` and ends at `VM_CONTEXT2_PAGE_TABLE_END_ADDR_HI32`. Merge-lane research must combine adjacent chunks before making whole-file claims about those complete register groups.

## Test And Validation Signals

There are no direct unit tests for this generated macro chunk. Useful validation signals are build-time and hardware/runtime oriented:

- Build AMDGPU paths that include `mmhub_1_0_sh_mask.h`, especially `mmhub_v1_0.c`, `gmc_v9_0.c`, and related SOC15 MMHUB code. Field-name mismatches show up as compile failures in `REG_SET_FIELD` or `REG_GET_FIELD` users.
- Static consistency checks can verify that every mask shifted by its matching `__SHIFT` becomes a dense field and that single-bit masks match their bit index. Repeated `VM_CONTEXT[0-15]`, `VM_INVALIDATE_ENG[0-17]`, and `PCTL[0-2]` groups should be checked for expected identical field layouts.
- Runtime GART/VM smoke tests on MMHUB 1.0-class hardware should exercise GART aperture setup, VMID context programming, GPUVM page-table updates, and TLB flush paths without VM faults or stale mappings.
- Fault-injection or forced page-fault tests should produce readable `VM_L2_PROTECTION_FAULT_STATUS` logs with plausible `CID`, `RW`, `VMID`, permission, walker, and mapping fields, and should clear/update status according to driver policy.
- Suspend/resume, runtime power-gating, and mode2 reset tests should preserve MMHUB VM and PCTL state. Register dumps before and after these transitions are useful for validating PCTL save ranges and `amdgpu_gmc` mode2 restore coverage.
- Clock/power-gating validation should confirm that `ATC_L2_MISC_CG`, `ATC_L2_CGTT_CLK_CTRL`, `MMEA1_CGTT_CLK_CTRL`, and PCTL deep-sleep fields do not regress MMHUB idle behavior or translation correctness.

## Chunk Notes For Merge Lane

This is one chunk of a larger generated MMHUB 1.0 mask header. Whole-file documentation should merge it with the preceding MMEA/DAGB sections and the following VM context end-address continuation. Treat this chunk as the central MMHUB VM/power-control bitfield section rather than as standalone logic.

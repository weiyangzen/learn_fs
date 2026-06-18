<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_regs.h

## Purpose
`pmmu_hbw_stlb_regs.h` is the address map for the Gaudi2 high-bandwidth PMMU shared TLB. It is auto-generated, guarded by `ASIC_REG_PMMU_HBW_STLB_REGS_H_`, and exports 60 `mmPMMU_HBW_STLB_*` macros from `0x4D01000` to `0x4D0114C`.

## Important APIs, Types, And Functions
There are no C functions or types. Address groups include STLB busy/status and ASID, HOP0 physical address, cache invalidation base/control, feature enable, AXI cache attributes, hop configuration, lookup masks, all/set/page-size invalidation controls, SRAM init, memory-cache invalidation/status/base/config, per-hop thresholds, multi-hit interrupt controls, L0 cache config, read ARPROT, range invalidation start/end, and ASID scrambler control/polynomial matrix registers.

## Control Flow
The header is consumed by MMU setup and invalidation routines. Typical flow is: program translation root and hop configuration; enable or tune STLB/cache features; perform memory-cache or range invalidation; poll status; clear or mask interrupts as needed. `gaudi2.c` references `mmPMMU_HBW_STLB_MEM_CACHE_INVALIDATION`, `mmPMMU_HBW_STLB_MEM_CACHE_INV_STATUS`, and `mmPMMU_HBW_STLB_BASE` during invalidation and setup.

## State And Persistence
All values live in hardware MMIO registers. Configuration persists until reset or driver reprogramming; busy, hit count, invalidation status, and interrupt bits are transient hardware state.

## Dependencies
Runtime use depends on `pmmu_hbw_stlb_masks.h`, the Gaudi2 MMU code, register access helpers, and base-address definitions. It also depends on hardware page-table and cache-invalidation semantics.

## Integration Points
This header is central to Gaudi2 HBW memory translation. It integrates with map/unmap invalidation, device boot MMU setup, protected-register policy in security code, and diagnostics for PMMU/cache failures.

## Risks
Incorrect addresses can cause MMU programming to affect unrelated PMMU/PIF registers. Missing synchronization around invalidation status can leave stale translations. Since this block controls high-bandwidth memory access, errors can appear as data corruption, RAZWI faults, or device hangs rather than simple probe failures.

## Test Signals
Test with MMU enable/disable paths, full and range invalidation, multi-ASID workloads, memory pressure and map/unmap stress, reset/resume reinitialization, and checks for PMMU timeout or multi-hit interrupt status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_regs.h -->

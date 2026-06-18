# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 10058-12395

## Chunk Scope

This chunk is part of AMD's generated GC 10.3.0 register shift/mask header. It contains C preprocessor constants only: register-field `__SHIFT` macros and matching `_MASK` macros. There are no functions, structs, enums, executable statements, or kernel-owned storage declarations.

The range starts at the tail of `CB_HW_CONTROL_4`, containing only the last five mask macros for that register, then covers full field definitions for color-buffer controls, GCEA/RMI/GCR/UTCL1 control/status blocks, GCVM L2 and fault registers, and GCVM context-control registers from context 0 through most of context 15. The final line is `GCVM_CONTEXT15_CNTL__VALID_PROTECTION_FAULT_ENABLE_INTERRUPT_MASK`; the remaining context 15 masks appear in the next chunk.

## Purpose

The macros define bit positions and masks for GC 10.3.0 register fields used by AMDGPU graphics, memory-management, KFD, SDMA, and power-management code. The matching `gc_10_3_0_offset.h` file supplies `mm...` register offsets; this header supplies the field layout inside each register. Driver code combines them through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, and `WREG32_SOC15`.

The hardware areas represented here are:

- Color buffer (`CB_*`) tuning: cache fetch depths, quad scoreboard behavior, clock gating disables, blend and DCC/CMASK/FMASK optimization controls, FIFO/tag depths, DCC overwrite-combiner controls, and CB memory-arbiter read/write weighting.
- GCEA blocks: fabric/cache arbitration, early write return, data-store memory test/error-injection controls, GL2C crossbar credits/burst limits, probe mapping, error status, request blocking, and RRET memory reservation.
- SPI throttling: PQ event control and exponential throttle controls.
- RMI blocks: request-interface burst/VMID/xbar controls, status counters, subblock FIFO/inflight status, xbar arbitration, UTCL1/XNACK behavior, demux controls, scoreboard flush/status controls, clock control, RB/GLX CID map, redundancy, and spare/debug registers.
- GCR/PMM/UTCL1 blocks: GCR request control, command/status, PIO access, page-size/cache bypass controls, invalidation force/done bits, fragment-size overrides, status, and targets disable fields.
- GCVM L2 and context blocks: L2 cache controls, invalidation controls, fault handling/default-page registers, identity aperture and physical offset registers, MM group routing class fields, reserved CID bank selection, parity controls, GCR linkage, walker throttles, PTE cache dump controls, and per-VM context fault policy.

## Important APIs, Types, and Macros

There are no callable APIs. The exported interface is the macro namespace:

- `CB_HW_CONTROL_4`, `CB_HW_CONTROL_3`, `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_DCC_CONFIG`, `CB_HW_MEM_ARBITER_RD`, and `CB_HW_MEM_ARBITER_WR` define color-buffer cache, compression, blend, clock-gating, FIFO-depth, and memory arbitration fields. These are sensitive performance/errata controls; many fields are named as disables or chicken bits.
- `GCEA_MISC`, `GCEA_LATENCY_SAMPLING`, `GCEA_DSM_CNTL*`, `GCEA_GL2C_XBR_*`, `GCEA_PROBE_*`, `GCEA_ERR_STATUS`, `GCEA_MISC2`, and `GCEA_RRET_MEM_RESERVE` define graphics cache/external-agent traffic policy, sampling, test/error injection, crossbar crediting, probe routing, and error-reporting fields.
- `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL` define shader processor throttle enable, periods, up/down steps, stall thresholds, and reset fields.
- `RMI_GENERAL_CNTL*`, `RMI_GENERAL_STATUS`, `RMI_SUBBLOCK_STATUS*`, `RMI_XBAR_CONFIG`, `RMI_XBAR_ARBITER_CONFIG*`, `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_DEMUX_CNTL`, `RMI_UTCL1_CNTL*`, `RMI_UTC_UNIT_CONFIG`, `RMI_TCIW_FORMATTER*`, `RMI_SCOREBOARD_CNTL`, `RMI_SCOREBOARD_STATUS*`, `RMI_CLOCK_CNTRL`, `RMI_UTCL1_STATUS`, `RMI_RB_GLX_CID_MAP`, `RMI_SPARE*`, `CC_RMI_REDUNDANCY`, and `GC_USER_RMI_REDUNDANCY` cover request-interface routing, arbitration, flush, retry, PRT/XNACK, CID, status, and redundancy fields.
- `GCR_GENERAL_CNTL`, `GCR_CMD_STATUS`, `GCR_SPARE`, `PMM_GENERAL_CNTL`, `GCR_PIO_CNTL`, and `GCR_PIO_DATA` define graphics-cache request controls, PIO transactions, command status, and spare/test controls.
- `UTCL1_CTRL`, `UTCL1_ALOG`, `UTCL1_UTCL0_INVREQ_DISABLE`, `GCRD_SA_TARGETS_DISABLE`, and `UTCL1_STATUS` define UTCL1 page-size controls, bypasses, invalidation force/done/status fields, adaptive log fields, and target-disable controls.
- `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_L2_CNTL4`, `GCVM_L2_CNTL5`, `GCVM_L2_STATUS`, `GCVM_INVALIDATE_CNTL`, `GCVM_DUMMY_PAGE_FAULT_*`, `GCVM_L2_PROTECTION_FAULT_*`, `GCVM_L2_CONTEXT1_IDENTITY_APERTURE_*`, `GCVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`, `GCVM_L2_MM_GROUP_RT_CLASSES`, `GCVM_L2_BANK_SELECT_RESERVED_CID*`, `GCVM_L2_CACHE_PARITY_CNTL`, `GCVM_L2_GCR_CNTL`, `GCVML2_WALKER_*`, and `GCVM_L2_PTE_CACHE_DUMP_*` define the graphics VM L2 cache, invalidation, page-fault/default-address, identity mapping, routing, parity, GCR, walker throttle, and diagnostic cache-dump fields.
- `GCVM_CONTEXT0_CNTL` through the chunk-local part of `GCVM_CONTEXT15_CNTL` define repeated per-VM context policy fields: context enable, page-table depth, block size, retry behavior, and interrupt/default-page behavior for range, dummy-page, PDE0, valid, read, write, and execute protection faults.

The macro naming convention is important for generated helper use: `REG_SET_FIELD(reg, REGISTER, FIELD, value)` expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` to exist. A missing or renamed macro breaks those helper expansions at compile time.

## Control Flow

This file has no software control flow. The behavioral flow appears in consumers that program hardware registers:

- `gfxhub_v2_1.c` includes `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and `gc_10_3_0_default.h`; it programs GCVM invalidation requests, prints L2 protection fault status with `REG_GET_FIELD`, initializes cache/TLB state, toggles GCVM L2 fault default-page behavior, and installs VM context fault-interrupt masks.
- VM invalidation requests are built by setting invalidation and flush fields, then written to GCVM invalidate-engine registers outside this chunk. The `GCVM_INVALIDATE_CNTL` fields in this chunk configure global invalidation queue behavior, while request/ack fields live elsewhere in the same generated header family.
- Fault-handling flow uses `GCVM_L2_PROTECTION_FAULT_STATUS` to decode faults, `GCVM_L2_PROTECTION_FAULT_CNTL` to decide whether faults redirect to a default page or crash, and per-context `GCVM_CONTEXTn_CNTL` bits to enable interrupt reporting and default handling for individual fault classes.
- Cache/TLB setup sequences write `GCVM_CONTEXT0_CNTL` plus offsets for all 16 contexts to disable or reprogram contexts, then configure L2 cache behavior through `GCVM_L2_CNTL*`.
- RMI and UTCL1 fields describe hardware handshakes and queues around retries, flushes, invalidations, XNACK, PRT, and scoreboard completion. Sequencing and polling requirements live in the code using these registers or in hardware programming tables, not in this generated header.

## State and Persistence

The state represented by these macros lives in GC hardware registers. The header itself persists nothing and allocates no memory. Register values persist according to hardware lifetime: until explicitly rewritten, reset by the relevant GC/GMC block, power-gated, restored after suspend, or reset with the ASIC.

Important state categories include:

- Render/backend state: CB cache depths, compression controls, blend optimization toggles, arbiter weights, stutter thresholds, and RB/RMI redundancy settings.
- Fabric/request state: GCEA arbitration, RMI xbar and demux modes, FIFO/inflight status, scoreboard flush state, CID maps, RRET reservations, and request-blocking/error state.
- Translation/cache state: UTCL1 page size and bypass controls, L1/L2 invalidation state, L2 cache mode, PTE/PDE cache behavior, bank-selection reserved CIDs, parity controls, and walker throttle settings.
- Fault state: dummy-page/default fault addresses, protection fault status/address registers, fault clearing controls, crash-on-fault policy, no-retry client interrupts, and per-context fault interrupt/default bits.
- Diagnostic/test state: GCEA DSM error-injection bits, probe routing, SPI throttle counters, RMI/GCR spare bits, GCR PIO access, and GCVM PTE cache dump controls.

`gfxhub_v2_1_save_regs()` and `gfxhub_v2_1_restore_regs()` explicitly save and restore many GCVM L2 and context registers named in this chunk into `adev->gmc` fields. That makes these register values part of driver-managed GPU power-management and reset recovery state, even though the generated header itself has no persistence logic.

## Dependencies and Integration Points

Direct GC 10.3.0 include sites in this tree are:

- `drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, the main semantic consumer for the GCVM L2/context/fault macros in this chunk.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which bridges GFX 10.3 hardware programming to KFD.
- `drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c` and `drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`, which include the generated GC 10.3 masks for SDMA-related register work.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the same offset and mask pair for Vangogh SMU power-management programming.

This chunk depends on:

- `gc_10_3_0_offset.h` for register offsets such as `mmCB_HW_CONTROL_4` at `0x1422`, `mmCB_HW_CONTROL_3` at `0x1423`, `mmCB_HW_CONTROL` at `0x1424`, `mmCB_DCC_CONFIG` at `0x1427`, `mmGCEA_MISC` at `0x14a2`, `mmRMI_GENERAL_CNTL` at `0x1520`, and the GCVM L2/context offset family used by `gfxhub_v2_1.c`.
- `gc_10_3_0_default.h` for hardware reset/default values used alongside these masks.
- AMD SOC15 register access helpers and field helpers (`SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_FIELD15`, `REG_SET_FIELD`, `REG_GET_FIELD`).
- Core AMDGPU VM/GMC structures that store VM hub offsets, context distances, fault masks, and saved GCVM register values.
- Hardware generator inputs for GC 10.3.0. Legal values, timing delays, register access restrictions, and ordering constraints are not encoded by these macros.

## Risks and Maintenance Notes

- This is generated hardware ABI. A one-bit shift or mask error can alter MMU fault policy, cache invalidation, render backend behavior, arbitration, or diagnostic/test paths.
- The range has split register definitions at both boundaries. `CB_HW_CONTROL_4` starts before this chunk, and `GCVM_CONTEXT15_CNTL` completes after it. Merge/reconciliation should combine adjacent chunk notes before treating either register as fully described.
- Many fields are named as disables, overrides, chicken bits, or error-injection controls. Accidentally enabling a disable bit or writing test fields outside intended flows can cause performance regressions, hangs, silent corruption, or spurious faults.
- Context-control macros are repeated for 16 VM contexts with identical field layouts. Copy/paste or offset-distance mistakes can program the wrong VMID context and affect unrelated processes or queues.
- Fault policy fields have high impact: switching between interrupt, retry, default-page, and crash behavior changes whether GPUVM errors are recoverable, logged, hidden by a dummy page, or escalated.
- RMI/UTCL1 invalidation, retry, and scoreboard fields interact with in-flight memory transactions. Writes likely require quiescent hardware, polling, or ordered flushes supplied by higher-level code.
- Reserved/spare fields are present throughout the chunk. Whole-register writes should preserve unknown bits unless generated defaults or hardware documentation explicitly requires them.
- SR-IOV access restrictions matter. `gfxhub_v2_1_set_fault_enable_default()` skips some GCVM L2 programming for VFs because the PF owns those registers.

## Test Signals

Useful validation for changes touching this area includes:

- Build coverage for all direct include paths: `gfxhub_v2_1.c`, KFD GFX 10.3, SDMA 5.2, shared SDMA, and Vangogh SMU.
- Static consistency checks that every `REGISTER__FIELD__SHIFT` in this range has a matching `REGISTER__FIELD_MASK` in the correct chunk after boundary reconciliation, and that corresponding `mmREGISTER` offsets exist in `gc_10_3_0_offset.h`.
- Cross-generation diffs against nearby GC headers such as `gc_10_1_0_sh_mask.h`, `gc_10_3_1_sh_mask.h`, or later GCVM/GFX hub headers to distinguish intentional generated deltas from accidental drift.
- GPUVM runtime tests: VM context creation/destruction, page-table updates, invalidation stress, eviction/migration paths, userptr/BO fault behavior, no-retry fault logging, and recovery after retry/default-page faults.
- Suspend/resume, BACO, reset, and SR-IOV VF/PF tests that exercise `gfxhub_v2_1_save_regs()` and `gfxhub_v2_1_restore_regs()` for the GCVM L2/context registers.
- Render and compute smoke tests on affected GC 10.3 ASICs to catch CB/RMI/UTCL1 regressions: modeset-independent graphics workloads, KFD queues, SDMA copies, memory pressure, GPU fault injection where available, and performance-counter sanity for arbitration/throttle changes.

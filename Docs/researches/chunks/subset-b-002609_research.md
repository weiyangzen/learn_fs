# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 42373-44638

## Scope

This chunk is the tail of AMD's generated GC 12.1.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, variables, allocations, locks, or executable branches. The covered register families are:

- The end of `GCVM_INVALIDATE_ENG11_REQ` plus complete request bitfields for invalidate engines 12-17.
- Acknowledgement and address-range fields for invalidate engines 0-17.
- Page-table base, start, and end address fields for GCVM contexts 0-15.
- Per-context and global GCVM L2 PTE-cache fragment-size controls.
- GCMC VM L2, GCUTCL2, GC ATC L2, and GC L2TLB performance counter configuration/result controls.
- Virtualization, host translation, IOMMU, framebuffer aperture, local/system memory aperture, and compression/translation bypass controls under the GC UTCL2 and GCMC VM blocks.
- GC ATC L2 cache/control/status/fault fields and GC L2TLB retry/reserved-space status fields.
- The `gfx_se_sqind` SQ wave debug-state bitfields from `SQ_DEBUG_STS_LOCAL` through `SQ_WAVE_EXEC_HI`, followed by the file's closing `#endif`.

The sibling offset constants for these registers live in `gc_12_1_0_offset.h`; this file defines how callers pack or decode each register value.

## Purpose

The purpose of this chunk is to expose hardware bit layouts for GC 12.1.0 GPU VM, translation cache, performance-monitor, virtualization, and shader-wave debug registers. AMDGPU code uses these macros through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` so driver code can set VM invalidation requests, program per-VMID page-table registers, configure fault/translation behavior, and decode diagnostic hardware state without hard-coding bit positions in C files.

The VM-side definitions support the graphics hub's address-translation path. `GCVM_INVALIDATE_ENG*_REQ` fields select VMIDs, flush type, L2 PTE/PDE invalidation levels, L1 PTE invalidation, fault-status clearing, request logging, 4K-only invalidation, and PDE3 invalidation. The matching `GCVM_INVALIDATE_ENG*_ACK` fields expose per-VMID completion acknowledgements and semaphore state. The `GCVM_CONTEXT*_PAGE_TABLE_*` fields define 64-bit page-directory entries and logical page ranges for each VM context.

The UTCL2/ATC/L2TLB definitions support translation-cache configuration and observability. They describe event selector ranges, counter enable/clear bits, trigger controls, ATC L2 request/cache behavior, fault logging, retry timeout attribution, reserved-space encoding detection, IOMMU enablement, VMID translation bypass, GPU host translation, and framebuffer/system-memory apertures.

The SQ definitions support low-level wavefront inspection. They provide masks for wave status, mode, exception flags, trap controls, program counter, execution mask, hardware IDs, scheduler state, instruction-buffer state, scratch base, TTMP registers, and XNACK state. In `gfx_v12_1.c`, these layouts pair with `ixSQ_WAVE_*` indices from the offset header for GPU hang/debug capture.

## Important APIs, Types, And Macros

The exported interface is entirely preprocessor macros using the generated naming scheme `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Key VM invalidate fields in this chunk include:

- `GCVM_INVALIDATE_ENG12_REQ` through `GCVM_INVALIDATE_ENG17_REQ`: `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0` through `INVALIDATE_L2_PDE3`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY`.
- `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK`: `PER_VMID_INVALIDATE_ACK` and `SEMAPHORE`.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through engine 17: low fields include `S_BIT` and `LOGI_PAGE_ADDR_RANGE_LO31`; high fields expose `LOGI_PAGE_ADDR_RANGE_HI14`.

Key per-context VM fields include:

- `GCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through context 15: 64-bit page-directory entry halves.
- `GCVM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32/HI32` and `END_ADDR_LO32/HI32` through context 15: logical page-number range halves, with 13-bit high logical-page fields.
- `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `GCVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`: small/big fragment size fields and `BANK_SELECT`.

Key performance monitor fields include:

- `GCMC_VM_L2_PERFCOUNTER*_CFG` for counters 0-15, `GC_ATC_L2_PERFCOUNTER*_CFG` for counters 0-15, `GCUTCL2_PERFCOUNTER*_CFG` for counters 0-3, and `GC_L2TLB_PERFCOUNTER*_CFG` for counters 0-3. Each configuration register has `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`.
- `*_PERFCOUNTER_RSLT_CNTL` registers expose `PERF_COUNTER_SELECT`, `START_TRIGGER`, `STOP_TRIGGER`, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`.
- `GCUTCL2_PERFCOUNTER_EVENTS_GROUP_SELECT` selects event groups for UTCL2 performance counter sets.

Key translation, aperture, and fault fields include:

- `GCVM_PCIE_ATS_CNTL`, `GCVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, `GCVM_IOMMU_CONTROL_REGISTER`, and `GCVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVML2_SEC_MASTER`, `GCUTC_TRANSLATION_FAULT_CNTL0/1`, `GCUTCL2_COMP_EN_OVERRIDES`, and `GCUTCL2_ROUTER_CNTL`.
- `GCMC_VM_FB_SIZE_OFFSET_VF0` through `VF7`, `GCMC_VM_FB_OFFSET`, `GCMC_VM_LOCAL_FB_ADDRESS_START/END`, `GCMC_VM_LOCAL_FB_ADDRESS_LOCK_CNTL`, and cacheable/local/LPDDR system-memory aperture registers.
- `GC_ATC_L2_FAULT_CNTL`, `GC_ATC_L2_FAULT_STATUS`, and `GC_ATC_L2_FAULT_ADDR_LO/HI`, which clear/log ATC L2 faults and identify fault type, client ID, access type, VMID, VF, VFID, and logical address.
- `GC_L2TLB_RETRY_TIMEOUT_STATUS_0/1/2` and `GC_L2TLB_TLB0_RESERVED_SPACE_ENCODING_STATUS`, which attribute timeout or reserved-space events to logical address, VMID/VFID/VF, permissions, TMZ/TEE, client, TLB ID, and clear bits.

Key SQ wave fields include:

- `SQ_WAVE_STATUS`, `SQ_WAVE_STATE_PRIV`, `SQ_WAVE_MODE`, `SQ_WAVE_EXCP_FLAG_PRIV`, `SQ_WAVE_EXCP_FLAG_USER`, and `SQ_WAVE_TRAP_CTRL` for wave state, privilege flags, exception flags, and trap enablement.
- `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_EXEC_LO/HI`, `SQ_WAVE_M0`, `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`, `SQ_WAVE_SCRATCH_BASE_LO/HI`, and `SQ_WAVE_XNACK_MASK`.
- `SQ_WAVE_HW_ID1/2`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_DVGPR_ALLOC_LO/HI`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_IB_DBG1`, `SQ_WAVE_SCHED_MODE`, `SQ_WAVE_ACTIVE`, and `SQ_WAVE_VALID_AND_IDLE`.

## Control Flow

There is no direct control flow in the header. Runtime behavior is in consumers that combine these masks with register offsets and MMIO helpers.

For VM invalidation, `gfxhub_v12_1_get_invalidate_req()` in `amdgpu/gfxhub_v12_1.c` builds a request word using `REG_SET_FIELD()` against `GCVM_INVALIDATE_ENG0_REQ`. It sets the target VMID bit, flush type, L2 PTE/PDE invalidation bits including `INVALIDATE_L2_PDE3`, and L1 PTE invalidation before the VM hub code writes the request to the selected invalidate engine. `gfxhub_v12_1_xcc_init()` records the per-XCC base offsets for engine 0 request/ack/semaphore registers and computes `eng_distance` and `eng_addr_distance` from adjacent generated offsets, so the same field layout applies across engines.

For page-table programming, `gfxhub_v12_1_xcc_setup_vm_pt_regs()` writes the low and high page-table base halves with `WREG32_SOC15_OFFSET()` at `hub->ctx_addr_distance * vmid`. The shift/mask macros in this chunk define the full 32-bit payload fields for those base registers and the start/end range registers that surround them in hardware.

For SQ wave debug, `gfx_v12_1.c` writes `regSQ_IND_INDEX` using `SQ_IND_INDEX` fields from earlier in the header, then reads `regSQ_IND_DATA`. `gfx_v12_1_read_wave_data()` collects fields such as status, PC, `EXEC_LO/HI`, hardware IDs, GPR/LDS allocation, IB status, `M0`, mode, privileged state, exception flags, trap control, active/valid state, DVGPR allocation, and scheduling mode. The macros in this chunk are the decode contract for interpreting the returned 32-bit values.

For performance counters and ATC/L2TLB diagnostics, this chunk supplies configuration and result-control bitfields. Actual control flow is in performance/debug tooling or driver code that writes event selectors, enables counters, reads low/high result registers, and clears or stops counters through the generated result-control fields.

## State And Persistence Behavior

The macros themselves hold no software state. They describe hardware registers whose contents are persistent or transient depending on the underlying block.

VM context base/start/end registers persist in the GC VM hub until rewritten, reset, or power-gated according to hardware rules. AMDGPU stores enough register-offset metadata in `adev->vmhub[]` to program these per XCC, and some hub versions save/restore page-table base registers across suspend/resume or reset paths.

Invalidate request registers are command-style hardware state. The driver writes request bits for one or more VMIDs, then observes acknowledgement bits and semaphores in the corresponding `ACK` registers. Address-range fields narrow the invalidation scope when range-based invalidation is used. Incorrect request or range fields can leave stale translations in L1/L2 TLB/PTE caches.

Fault status registers are sticky diagnostic state until cleared through the corresponding control fields. ATC L2 fault status and address registers capture fault metadata such as client, VMID, VF/VFID, access type, and logical address. Retry-timeout and reserved-space status registers similarly preserve the detected condition until a clear bit is written.

Performance counter configuration registers persist while programmed. Counter result registers accumulate events until cleared, stopped, saturated, disabled, or reset. The `CLEAR`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE` fields are therefore state-changing controls, not passive decode fields.

SQ wave registers expose live shader-queue state for a selected resident wave. Fields such as PC, EXEC, trap flags, TTMPs, XNACK state, scheduler mode, allocation, and IB status can change as the wave executes, traps, stalls, or exits. Debug consumers must correlate with `SQ_WAVE_STATUS`, `SQ_WAVE_ACTIVE`, and `SQ_WAVE_VALID_AND_IDLE` before treating a captured value as meaningful.

## Dependencies And Integration Points

This chunk depends on AMD's generated GC 12.1.0 register database and must stay synchronized with:

- `gc_12_1_0_offset.h`, which supplies the `reg*` and `ix*` addresses/indices for the field layouts defined here.
- `amdgpu/gfxhub_v12_1.c`, which uses `GCVM_INVALIDATE_ENG0_REQ`, context page-table base fields, fault-control/status fields, and generated offsets to initialize and drive the GC VM hub.
- `amdgpu/gfx_v12_1.c`, which uses SQ indirect offsets plus the SQ field definitions to collect type-4 wave debug data.
- `amdgpu/mes_v12_1.c`, `amdgpu/sdma_v7_1.c`, `amdgpu/soc_v1_0.c`, `amdgpu/imu_v12_1.c`, `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, and KFD v12.1 queue-management files, which include the GC 12.1.0 offset/mask headers for register programming.
- `include/soc24_enum.h`, which provides event enum namespaces such as `GCUTCL2_PERF_SEL` that pair with the performance-counter selector fields.
- AMDGPU SOC15 MMIO helpers (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`) and field helpers (`REG_SET_FIELD`, `REG_GET_FIELD`).

The path is under a `ceph-client` source mirror, but this file is AMD GPU driver metadata. It has no Ceph or distributed filesystem control path.

## Risks And Edge Cases

- The file is generated, untyped hardware metadata. Wrong shifts or masks can compile cleanly while silently writing the wrong hardware bits or decoding incorrect fault/debug data.
- GC 12.1.0 values are ASIC-specific. Similar macro names in GC 12.0, GC 11, or GCA headers do not prove identical bit layouts or register availability.
- VM invalidation errors are high impact. Missing `INVALIDATE_L2_PDE3`, wrong `PER_VMID_INVALIDATE_REQ`, wrong address-range high/low fields, or bad acknowledgement masks can cause stale translations, timeouts, or hard-to-debug GPU VM faults.
- Context start/end high masks expose only defined high logical-page bits. Treating the fields as unconstrained 64-bit addresses rather than hardware logical page-number pieces can program invalid ranges.
- Fault status is sticky and may represent the first fault unless subsequent updates are enabled. Consumers that do not clear or log in the documented order can misattribute later faults.
- Performance counter fields combine event selectors and control bits in one word. Accidental writes to `CLEAR`, `ENABLE`, or `CLEAR_ALL` while changing `PERF_SEL` can lose samples or start counters at the wrong time.
- Translation bypass, IOMMU enablement, GPU host translation, VF framebuffer aperture, and local FB lock fields are security/virtualization sensitive. Wrong values can expose incorrect memory apertures, bypass translation unexpectedly, or break SR-IOV/guest isolation.
- SQ wave state is volatile. Reading `PC`, `EXEC`, exception flags, or TTMPs without checking validity/idle state can report stale or unrelated wave-slot contents.
- The chunk boundary starts in the middle of `GCVM_INVALIDATE_ENG11_REQ` and ends at the file terminator. Whole-file conclusions should merge with preceding chunks for the complete engine 0-11 request definitions and earlier GCVM/SQ field groups.

## Test Signals

Useful validation signals include:

- Build AMDGPU with GC 12.1.0 support enabled. Missing or renamed macros should fail in GC 12.1 paths such as `gfxhub_v12_1.c`, `gfx_v12_1.c`, MES, SDMA, SOC, IMU, and KFD queue-management units.
- Exercise VM context setup on GC 12.1 hardware and verify page-table base registers are programmed per VMID/XCC through `gfxhub_v12_1_xcc_setup_vm_pt_regs()`.
- Run VM invalidation and GART/page-table update workloads under IOMMU/GPUVM pressure. Stale mappings, VM fault storms, invalidate timeout logs, or mismatched ACK bits point to request/ack/range field problems.
- Trigger or inspect GCVM/ATC/L2TLB faults and confirm decoded client ID, VMID, VF/VFID, access type, and fault address match the failing access.
- Use performance monitoring or register-level diagnostics for GCMC VM L2, GCUTCL2, GC ATC L2, and GC L2TLB counters. Counter enable/clear behavior and event counts should match selected event groups and `soc24_enum.h` event IDs.
- Capture wave data through GC 12.1 debug/hang paths and verify PC, EXEC, HW IDs, allocation, IB state, trap/exception flags, and scheduler fields are plausible and ordered consistently with `gfx_v12_1_read_wave_data()`.
- Mechanically compare this generated block against AMD's authoritative GC 12.1.0 register database and the matching offset header; manual review should treat any divergence from generation as suspicious.

## Cross-Chunk Notes

The final per-file report should merge this chunk with earlier chunks for the complete `gc_12_1_0_sh_mask.h` register namespace. Important adjacent dependencies include earlier `GCVM_INVALIDATE_ENG0_REQ` through `ENG11_REQ` definitions, `GCVM_CONTEXT*_CNTL` fault-enable fields used by `gfxhub_v12_1_xcc_init()`, `SQ_IND_INDEX`/`SQ_IND_DATA` fields used by the SQ indirect read path, and the earlier GCVM protection-fault status/control fields printed by `gfxhub_v12_1_print_l2_protection_fault_status()`.

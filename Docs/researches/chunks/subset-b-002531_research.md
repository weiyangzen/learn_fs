# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 12212-14595

## Chunk Scope

This chunk is a generated AMD GC 11.0.3 register shift/mask header segment. It contains C preprocessor constants only: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros for memory-mapped GPU registers. There are no functions, structs, enums, callbacks, locks, allocations, runtime branches, or software-owned storage declarations.

The range covers 2,170 `#define` entries: 1,083 shift definitions and 1,087 mask definitions across 198 visible register-group comments and 8 address-block markers. The chunk starts inside the `RMI_TCIW_FORMATTER1_CNTL` group with only the tail mask entries from the previous chunk, then covers complete RMI scoreboard/xbar/status/spare groups, PMM/GCR/UTCL1 control/status groups, shared GCMC and GCVM L2 page-fault/cache controls, ATC L2 controls, GCL2TLB and GPUVA/VMID translation-assist fields, GCMC VM aperture fields, `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL`, `GCVM_CONTEXTS_DISABLE`, and most of the GCVM invalidate-engine semaphore/request/ack families. It ends inside `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32`; the remainder of that range-address family is in the next chunk.

## Purpose

`gc_11_0_3_sh_mask.h` supplies symbolic bitfield definitions for GC 11.0.3 AMDGPU hardware programming. The matching `gc_11_0_3_offset.h` file supplies the register offsets, while this header supplies the bit positions and masks that consumers pass to helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15`.

This slice focuses on request-interface and graphics-VM hardware:

- RMI request-interface controls: scoreboard flush/VMID-invalidation status, xbar arbitration, dynamic clock masks, UTCL1 retry/fault status, RB-to-GLX CID maps, XNACK debug bits, spare/chicken bits, and redundancy controls.
- GCR/PMM/UTCL1 controls: PIO access, page migration monitor control/status, UTCL1 arbitration, bypass, wakeup, invalidation, stall, LRU, hit/miss, and fault-status fields.
- Shared GCMC and GCVM aperture controls: NB MMIO aperture, PCI arbitration, DRAM top, framebuffer offset, system aperture default address, steering, reset requests, memory light sleep, cacheable/local system-memory ranges, local framebuffer range/lock, L2 clock-gating and harvest controls, and group return-fault status.
- GCVM L2 controls: cache enable/mode, PTE/PDE fragment sizes, outstanding request limits, invalidation queue control, dummy/default fault addresses, L2 protection fault policy/status/address registers, identity aperture and physical offset registers, MM group routing classes, reserved-CID bank selection, parity, GCR linkage, walker throttling, PTE cache dump, and credit-safety fields.
- ATC L2 and GCL2TLB controls: ATC L2 cache settings, cache-data readback windows, status, memory light-sleep, SDP port controls, TLB status, and GPUVA/VMID translation-assist request/response fields.
- Per-VMID context and invalidation controls: 16 `GCVM_CONTEXTn_CNTL` groups, context disable bits, 18 invalidation-engine semaphore/request/ack groups, and the start of invalidate address-range groups.

Although the repository path includes `ceph-client`, this file is AMD GPU driver hardware metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The exported interface is the generated macro namespace.

Key macro families in this chunk:

- `RMI_SCOREBOARD_CNTL`, `RMI_SCOREBOARD_STATUS0`, `RMI_SCOREBOARD_STATUS1`, and `RMI_SCOREBOARD_STATUS2` describe completion and status fields for RB0/RB1 flushes, VMID invalidation progress, requested VMID, UTC/done state, flush type, force-done status, counters, underflow/overflow flags, and timestamp flush completion.
- `RMI_XBAR_ARBITER_CONFIG` and `RMI_XBAR_ARBITER_CONFIG_1` describe arbitration modes, weighted round-robin breaks, stall override/timer fields, and RD/WR weights for RMI xbar arbitration.
- `RMI_CLOCK_CNTRL`, `RMI_UTCL1_STATUS`, `RMI_RB_GLX_CID_MAP`, `RMI_XNACK_DEBUG`, `RMI_SPARE`, `RMI_SPARE_1`, `RMI_SPARE_2`, and `CC_RMI_REDUNDANCY` define dynamic clock busy/wakeup masks, UTCL1 fault/retry/PRT status, CB/DB client-ID routing, per-VMID XNACK debug state, no-fill and reorder spare controls, address masks, arbitration behavior, and redundant lane controls.
- `GCR_PIO_CNTL`, `GCR_PIO_DATA`, `PMM_CNTL`, and `PMM_STATUS` define graphics-cache PIO command/data and page migration monitor enable, mode, stall, trigger, busy, fault, and interrupt-status fields.
- `UTCL1_CTRL_1`, `UTCL1_ALOG`, and `UTCL1_STATUS` cover UTCL1 arbitration/burst settings, clock-gating controls, no-reorder and LRU behavior, line-fragment mode, forced invalidation acknowledgements, page-size controls, request counters, fault IDs, hit/miss counters, and PRT/fault/retry status bits.
- `GCMC_VM_*`, `GCUTCL2_*`, and `GCMC_SHARED_*` macros describe shared VM apertures and global configuration: MMIO base/limit, PCI controls, top-of-DRAM, FB offset, system aperture default address, steering, reset request, memory power, cacheable DRAM range, local system memory and framebuffer ranges, APT controls, lock bits, active function ID, clock-gating busy masks, no-allocate controls, harvest bypass groups, and group return-fault status.
- `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_L2_CNTL4`, and `GCVM_L2_CNTL5` define L2 TLB/cache behavior: enable bits, bank select, fragment size, cache mode, invalidation mode, PTE/PDE fetch and fragment controls, outstanding request limits, walker credits, and cache small/big fragment sizes.
- `GCVM_L2_STATUS`, `GCVM_DUMMY_PAGE_FAULT_*`, `GCVM_INVALIDATE_CNTL`, `GCVM_L2_PROTECTION_FAULT_CNTL`, `GCVM_L2_PROTECTION_FAULT_CNTL2`, `GCVM_L2_PROTECTION_FAULT_MM_CNTL3`, `GCVM_L2_PROTECTION_FAULT_MM_CNTL4`, `GCVM_L2_PROTECTION_FAULT_STATUS`, `GCVM_L2_PROTECTION_FAULT_ADDR_*`, and `GCVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` define fault counters, dummy-page handling, invalidation queue controls, default-page routing, interrupt/crash behavior, CID filtering, status decoding, and fault/default physical address fields.
- `GCVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `GCVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*` define identity-mapping aperture boundaries and offsets.
- `GCVM_L2_MM_GROUP_RT_CLASSES`, `GCVM_L2_BANK_SELECT_RESERVED_CID`, `GCVM_L2_BANK_SELECT_RESERVED_CID2`, `GCVM_L2_CACHE_PARITY_CNTL`, `GCVM_L2_ICG_CTRL`, `GCVM_L2_GCR_CNTL`, `GCVML2_WALKER_*`, `GCVM_L2_PTE_CACHE_DUMP_*`, `GCVM_L2_BANK_SELECT_MASKS`, and `GCVML2_CREDIT_SAFETY_*` define routing class maps, bank selection, parity/test controls, clock-gating, GCR integration, page-walker throttles, diagnostic PTE cache dump controls, and credit-safety settings.
- `GC_ATC_L2_*` macros define ATC L2 cache control, status, cache readback data words, miscellaneous clock-gating, memory light-sleep, and SDP port controls.
- `GCL2TLB_TLB0_STATUS` and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_*` define TLB validity/error status and request/response payload fields for translation assistance.
- `GCMC_VM_FB_LOCATION_*`, `GCMC_VM_AGP_*`, `GCMC_VM_SYSTEM_APERTURE_*`, and `GCMC_VM_MX_L1_TLB_CNTL` define framebuffer, AGP, system aperture, and L1 TLB controls used by VM hub setup.
- `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` provide repeated per-context fields: context enable, page-table depth and block size, range/dummy/PDE0/valid/read/write/execute protection fault interrupt bits, corresponding default-page enable bits, and `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT`.
- `GCVM_CONTEXTS_DISABLE` exposes disable bits for VM contexts 0 through 15 plus corresponding effective `DISABLE_CONTEXT_STATUS` bits.
- `GCVM_INVALIDATE_ENG0_SEM` through `GCVM_INVALIDATE_ENG17_SEM`, `GCVM_INVALIDATE_ENG0_REQ` through `GCVM_INVALIDATE_ENG17_REQ`, and `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK` define the GCVM invalidation engine handshake. Each request word includes per-VMID invalidation bits, `FLUSH_TYPE`, L2 PTE/PDE invalidation selections, L1 PTE invalidation, protection-fault status address clearing, request logging, and a 4K-page-only option.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`, `GCVM_INVALIDATE_ENG0_ADDR_RANGE_HI32`, and the first field of `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32` begin the optional logical page address range definitions for invalidation engines. The rest of this repeated address-range family belongs to the next chunk.

The generated naming convention is itself part of the API. `REG_SET_FIELD(value, GCVM_INVALIDATE_ENG0_REQ, INVALIDATE_L2_PTES, 1)` depends on both `GCVM_INVALIDATE_ENG0_REQ__INVALIDATE_L2_PTES__SHIFT` and `GCVM_INVALIDATE_ENG0_REQ__INVALIDATE_L2_PTES_MASK` being spelled exactly as generated.

## Control Flow

This header has no software control flow. Runtime sequencing is in the AMDGPU consumers that include the header.

The main direct GC 11.0.3 consumer in this tree is `drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`. It uses this chunk's macros to:

- Build a VM invalidation request in `gfxhub_v3_0_3_get_invalidate_req()` by setting `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0`, `INVALIDATE_L2_PDE1`, `INVALIDATE_L2_PDE2`, `INVALIDATE_L1_PTES`, and `CLEAR_PROTECTION_FAULT_STATUS_ADDR` on `GCVM_INVALIDATE_ENG0_REQ`.
- Decode and print `GCVM_L2_PROTECTION_FAULT_STATUS` fields such as `CID`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, `MAPPING_ERROR`, and `RW`.
- Program framebuffer and memory-controller aperture state with `GCMC_VM_FB_LOCATION_BASE`, `GCMC_VM_FB_OFFSET`, and system/AGP aperture registers.
- Initialize L2 cache and TLB controls with `GCVM_L2_CNTL*` and `GCMC_VM_MX_L1_TLB_CNTL`.
- Enable context 0 as the system domain through `GCVM_CONTEXT0_CNTL`.
- Program contexts 1 through 15 through offset-distance writes based on `GCVM_CONTEXT1_CNTL`, setting page-table depth, block size, default-page routing, and retry/no-retry policy.
- Program all 18 invalidation engine address ranges using the `GCVM_INVALIDATE_ENG0_ADDR_RANGE_*` offset family and `eng_addr_distance`.
- Toggle L2 protection fault default behavior through `GCVM_L2_PROTECTION_FAULT_CNTL`.
- Populate `amdgpu_vmhub` offsets and distances from `regGCVM_CONTEXT*`, `regGCVM_INVALIDATE_ENG*`, and `regGCVM_L2_PROTECTION_FAULT_*` offsets, while using this chunk's context fault interrupt masks for `vm_cntx_cntl_vm_fault`.

Other direct include users are `drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c` and `drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`. `imu_v11_0_3.c` includes the same generated mask namespace for IMU/RLC golden-register programming, including `GCVM_CONTEXT0_CNTL` entries.

The header does not encode register ordering, polling delays, read-only/write-one-clear behavior, power-domain access rules, or SR-IOV ownership. Those requirements live in the consuming code and hardware programming guides.

## State And Persistence Behavior

The header persists no software state. It names fields in hardware registers whose values persist according to GC block lifetime: until explicitly rewritten, reset by hardware, restored by firmware/golden-register tables, lost through power gating, or restored during driver resume/reset recovery.

Important represented hardware state includes:

- In-flight request and flush state in RMI scoreboard and xbar registers, including completion, running counters, overflow/underflow conditions, and timestamp flush state.
- Request routing and arbitration state for RMI, GCR, UTCL1, GCUTCL2, and ATC L2, including clock-gating, burst, wakeup, reorder, no-fill, redundancy, and credit-safety behavior.
- Global VM aperture state for MMIO, framebuffer, AGP, system aperture, cacheable DRAM, local system memory, local framebuffer, and default fault address windows.
- GCVM L2 cache/TLB state, including cache enablement, fragment sizes, bank selection, invalidation control, PTE/PDE behavior, parity handling, walker throttling, diagnostic cache dump, and group routing.
- Protection fault state, including sticky or live fault status, fault addresses, default-page addresses, CID filtering, interrupt/default-page policy, and crash-on-fault policy.
- Per-context VMID state in the 16 `GCVM_CONTEXTn_CNTL` registers, including page-table geometry and fault handling policy.
- Invalidation-engine state across 18 engines: semaphore, request, acknowledgement, and address-range register fields.
- Translation-assist state for GPUVA/VMID requests and responses.

`gfxhub_v3_0_3.c` treats many of these registers as driver-managed VM hub state during GART enable/disable and fault policy changes. SR-IOV restrictions are explicit for some identity-aperture and L2 protection-fault programming: the VF path skips those writes because the PF programs them instead.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which provides `reg...`/`mm...` register offsets and offset spacing used with these masks. GC 11.0.3 code also commonly includes default/golden-register data and SOC15 register helper infrastructure.

Observed direct include users in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`

Semantic integration points include:

- AMDGPU VM hub setup, GART aperture programming, context page-table programming, and invalidation request generation.
- VM fault reporting and recovery paths, including protection fault status decoding and default-page/crash policy.
- KFD-facing retry/no-retry behavior, because `GCVM_CONTEXTn_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` controls how memory faults interact with XNACK/no-retry process policy.
- IMU/RLC golden-register initialization and firmware-assisted hardware setup.
- GPU reset, suspend/resume, runtime power management, and SR-IOV PF/VF split ownership.
- Debug and diagnostics that read RMI, UTCL1, ATC L2, TLB, and PTE cache dump state.

The macros depend syntactically only on the C preprocessor, but semantically they are hardware ABI. Mixing this header with a different GC generation's offset header can compile while addressing the wrong register layout.

## Risks And Maintenance Notes

- Generated bitfield drift is high impact. A one-bit shift or mask error can alter VM fault policy, cache invalidation, aperture routing, retry behavior, or low-level request arbitration.
- This chunk has artificial boundaries. It starts at the tail of `RMI_TCIW_FORMATTER1_CNTL` and ends inside `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32`; merge/reconciliation must combine adjacent chunk documents before treating either boundary register family as complete.
- The VM context fields are highly repetitive across 16 contexts. Consumers often program context families by offset distances, so mismatched register spacing or a context-specific field typo can create VMID-dependent failures.
- Invalidation request construction is sensitive. Missing or incorrectly positioned `INVALIDATE_L2_PTES`, PDE bits, `INVALIDATE_L1_PTES`, `FLUSH_TYPE`, or per-VMID bits can leave stale GPU translations after page table updates.
- Fault handling policy is safety-critical. Default-page routing, interrupt enablement, retry/no-retry, and crash-on-fault fields determine whether faults are logged, retried, hidden behind dummy/default pages, or escalated to reset.
- Aperture fields affect global memory routing. Bad framebuffer, AGP, system aperture, local system-memory, or default-address programming can cause incorrect VRAM/host-memory access, spurious VM faults, or silent data exposure.
- Several RMI, UTCL1, ATC, and GCVM fields are named as disables, overrides, force bits, debug controls, spare bits, or test/parity controls. Whole-register writes must preserve unrelated and reserved bits unless hardware documentation or generated defaults explicitly define safe values.
- Status, request, acknowledgement, semaphore, and counter fields are mixed in adjacent groups. The header does not tell whether fields are read-only, write-one-to-clear, self-clearing, sticky, or firmware-owned.
- SR-IOV access restrictions matter. `gfxhub_v3_0_3.c` already avoids some writes from VFs; similar assumptions should be checked before adding new programming against fields in this range.

## Test Signals

Useful validation is build-time, generated-data, and hardware-integration oriented:

- Compile/preprocess GC 11.0.3 paths that include `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h`: `gfxhub_v3_0_3.c`, `gfx_v11_0_3.c`, and `imu_v11_0_3.c`.
- Static consistency checks that every complete field in the full header has matching `__SHIFT` and `_MASK` macros, with explicit exceptions only for chunk-boundary splits.
- Cross-check register names against `gc_11_0_3_offset.h`, especially context distances, invalidation engine distances, and address-range distances used by `amdgpu_vmhub`.
- VM hub runtime tests on GC 11.0.3 hardware: GART enable/disable, VMID context programming, page-table base/start/end setup, page-table updates, VMID invalidation, range invalidation where supported, and acknowledgement polling.
- Fault tests that trigger range, PDE, valid, read, write, execute, dummy-page, retry, and no-retry faults, then verify `GCVM_L2_PROTECTION_FAULT_STATUS` decoding, default-page behavior, interrupt behavior, and fault address reporting.
- Suspend/resume, GPU reset, runtime power-gating, IMU/RLC golden-register restore, and SR-IOV VF/PF tests to confirm ownership and persistence assumptions for GCVM L2/context/aperture registers.
- Stress tests with graphics and compute workloads under VM pressure, BO eviction/migration, userptr, KFD queues, SDMA interaction, and memory oversubscription to catch stale translations, retry storms, unexpected default-page use, or GPU hangs.
- Diagnostic checks for RMI/UTCL1/ATC state: scoreboard counters should not underflow/overflow during normal invalidation traffic, UTCL1 fault/retry status should match induced conditions, and PTE cache dump or translation-assist readbacks should be sampled only under synchronized debug conditions.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 12212-14595 of `gc_11_0_3_sh_mask.h`. Earlier chunks should cover the beginning of `RMI_TCIW_FORMATTER1_CNTL` and preceding RMI/UTCL1 fields. Later chunks should continue the invalidation address-range family beginning at `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32`, then cover page-table base/start/end and subsequent GC 11.0.3 register groups. The final per-file report should treat this file as generated AMD GC 11.0.3 hardware register metadata used by AMDGPU VM, GFX, KFD-facing fault policy, and IMU/golden-register paths.

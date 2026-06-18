# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h lines 4757-7198

## Scope

This chunk is a generated AMDGPU MMHUB 3.0.2 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, variables, allocations, locks, or executable branches. The range starts inside `MMVM_L2_CNTL4` after the first three field shifts were defined in the previous chunk, and it ends inside `MMMC_VM_MX_L1_TLB_CNTL` after `ENABLE_L1_TLB_MASK`; the remaining masks for that TLB register continue in the next chunk.

Within those boundaries the slice defines 2,124 `#define` entries across the MMHUB L2/UTCL2/MMVM shared register surface. Major covered blocks are:

- L2 cache and QoS controls: `MMVM_L2_CNTL4`, group real-time class bits, bank-select reserved client IDs, cache parity controls, clock-gating timing, `MMVM_L2_CNTL5`, GCR controls, busy controls, and PTE cache dump controls.
- GPUVA/VMID translation-assist request and response registers.
- Credit-safety registers for UTCL2/L2 return, invalidation, interrupt, and walker paths.
- `addressBlock: mmhub_mmutcl2_mmvml2vcdec`: VM context controls for contexts 0-15, context-disable bits, invalidation semaphore/request/ack/address-range registers for engines 0-17, page-table base/start/end address registers for contexts 0-15, and per-PF/VF PTE cache fragment-size controls.
- `addressBlock: mmhub_mmutcl2_mmvml2pldec` and `mmhub_mmutcl2_mmvml2prdec`: MM VM L2 and UTCL2 performance-counter configuration and result registers.
- `addressBlock: mmhub_mmutcl2_mmvmsharedhvdec`: per-VF framebuffer size/offset registers for VF0-VF15.
- `addressBlock: mmhub_mmutcl2_mmvmsharedpfdec`: physical-function/shared aperture, local memory, APT, clock/busy, no-allocate, harvest-bypass, and group-fault status controls.
- Beginning of `addressBlock: mmhub_mmutcl2_mmvmsharedvcdec`: framebuffer location, AGP aperture, system aperture, and the first field of L1 TLB control.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU MMIO metadata, not distributed-filesystem logic.

## Purpose

The purpose of the slice is to publish the bit-level ABI for MMHUB 3.0.2 registers. Each register field uses the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for the field.
- `<REGISTER>__<FIELD>_MASK`: 32-bit field mask used to isolate or compose values.

The matching `mmhub_3_0_2_offset.h` file supplies register addresses such as `regMMVM_CONTEXT0_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, `regMMMC_VM_FB_LOCATION_BASE`, and `regMMMC_VM_MX_L1_TLB_CNTL`. This header supplies the masks consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

The most important operational purpose is MMHUB virtual-memory programming for AMDGPU: enabling contexts, setting page-table geometry, defining GART/system/AGP/framebuffer apertures, issuing VMID-scoped invalidations, tuning L2/UTCL2 behavior, and exposing diagnostic/performance/status fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The public interface is the macro namespace consumed by AMDGPU MMHUB code.

Important macro groups include:

- `MMVM_L2_CNTL4` and `MMVM_L2_CNTL5`: L2 cache partitioning, VMC tap physical-request controls, non-RT/soft-RT IFIFO transaction limits, clock-gating overrides, visible-bank FIFO behavior, small-fragment size, walker priority client ID, walker PDE no-allocate/MTYPE enables, and fine-grain clock-gating disable bits.
- `MMVM_L2_MM_GROUP_RT_CLASSES`: 32 one-bit group real-time-class flags.
- `MMVM_L2_BANK_SELECT_RESERVED_CID` and `MMVM_L2_BANK_SELECT_RESERVED_CID2`: reserved read/write client IDs, enable bits, invalidation mode, private invalidation, and fragment-size selectors.
- `MMVM_L2_CACHE_PARITY_CNTL`: parity-check enables and forced parity-mismatch injection for 4K PTE, big-K PTE, and PDE caches, plus forced bank/cache/associativity selection.
- `MMVM_L2_CGTT_CLK_CTRL`, `MMVM_L2_CGTT_BUSY_CTRL`, `MMUTCL2_CGTT_CLK_CTRL`, and `MMUTCL2_CGTT_BUSY_CTRL`: clock-gating on-delay, off-hysteresis, light-sleep hysteresis, LS disable, busy override, read delay, and always-busy fields.
- `MMVM_L2_PTE_CACHE_DUMP_CNTL` and `MMVM_L2_PTE_CACHE_DUMP_READ`: PTE cache dump enable/ready selectors and dump data.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*` and `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_*`: address, VMID, VF/VFID, GPA mode, requested permissions, client ID, request/ack bits, response permissions, fragment size, snoop/SPA/IO/TMZ/no-PTE/MTYPE/MEMLOG/NACK/LLC-noalloc metadata.
- `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL`: context enable, page-table depth and block size, retry behavior, and interrupt/default handling for range, dummy-page, PDE0, valid, read, write, execute, and secure protection faults.
- `MMVM_CONTEXTS_DISABLE`: packed disable bits for contexts 0-15 and related context disable controls.
- `MMVM_INVALIDATE_ENG0_*` through `MMVM_INVALIDATE_ENG17_*`: semaphore fields, per-VMID invalidate request mask, flush type, L2 PTE/PDE and L1 PTE invalidate bits, protection-fault address clear, logging, 4K-only mode, ack bits, and invalidate address ranges.
- `MMVM_CONTEXT*_PAGE_TABLE_BASE_ADDR_*`, `MMVM_CONTEXT*_PAGE_TABLE_START_ADDR_*`, and `MMVM_CONTEXT*_PAGE_TABLE_END_ADDR_*`: low/high pieces for each context's page-table base and aperture bounds.
- `MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `MMVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`: per-PF/VF and per-context PTE cache fragment-size selectors for PF, VF0, and VF1.
- `MMMC_VM_L2_PERFCOUNTER*_CFG`, `MMUTCL2_PERFCOUNTER*_CFG`, `MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MMUTCL2_PERFCOUNTER_RSLT_CNTL`, and result LO/HI registers: performance event selection, selection-end range, mode, enable, clear, result-counter selection, start/stop trigger, global clear, stop-on-saturate, low counter bits, high counter bits, and compare value.
- `MMMC_VM_FB_SIZE_OFFSET_VF0` through `MMMC_VM_FB_SIZE_OFFSET_VF15`: packed virtual-function framebuffer size and offset fields.
- `MMMC_VM_FB_OFFSET`, `MMMC_VM_FB_LOCATION_BASE`, and `MMMC_VM_FB_LOCATION_TOP`: framebuffer offset/base/top fields used to derive memory-controller visible VRAM placement.
- `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*`, `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR`, and `MMMC_VM_SYSTEM_APERTURE_HIGH_ADDR`: default physical page address and system aperture logical address bounds.
- `MMMC_VM_AGP_BASE`, `MMMC_VM_AGP_BOT`, and `MMMC_VM_AGP_TOP`: AGP aperture address fields.
- `MMMC_VM_APT_CNTL`, cacheable-DRAM/local-system/local-FB address range fields, `MMMC_VM_LOCAL_FB_ADDRESS_LOCK_CNTL`, and `MMMC_VM_FB_NOALLOC_CNTL`: aperture translation policy, locality checks, fragment-size cap, local sysmem aperture control, lock bit, and no-allocate behavior.
- `MMUTCL2_HARVEST_BYPASS_GROUPS` and `MMUTCL2_GROUP_RET_FAULT_STATUS`: harvested/bypassed group mask and return-fault group status.
- Partial `MMMC_VM_MX_L1_TLB_CNTL`: shifts for L1 TLB enable, system access mode, unmapped system aperture access, advanced driver model, ECO bits, MTYPE, and only the first mask in this chunk.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by consumers in `amdgpu/mmhub_v3_0_2.c`:

1. `mmhub_v3_0_2_init()` records register offsets for page-table base registers, invalidation semaphore/request/ack registers, context control, L2 fault status/control, context stride, invalidation-engine stride, and the reserved CID2 register.
2. `mmhub_v3_0_2_gart_enable()` programs the GART page-table base, context 0 aperture start/end, AGP/system/default apertures, L1 TLB controls, L2 cache controls, context 0 enablement, context 1-15 VMID controls, and invalidation address ranges.
3. `mmhub_v3_0_2_get_invalidate_req()` composes an invalidate request with `MMVM_INVALIDATE_ENG0_REQ` fields: per-VMID bit, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, and protection-fault-address clear.
4. `mmhub_v3_0_2_setup_vmid_config()` iterates VM contexts 1-15 using `hub->ctx_distance`, programs `MMVM_CONTEXT1_CNTL` fields for enablement, page-table depth/block size, default fault behavior, and retry/no-retry behavior, then writes page-table start/end bounds using the address-register stride.
5. `mmhub_v3_0_2_program_invalidation()` iterates 18 invalidation engines using `hub->eng_addr_distance` and initializes each engine's address range to a broad range.
6. `mmhub_v3_0_2_gart_disable()` clears all 16 context-control registers, disables L1 TLB and advanced-driver-model bits in `MMMC_VM_MX_L1_TLB_CNTL`, disables L2 cache, and clears `MMVM_L2_CNTL3`.

Other fields in the chunk are diagnostic, RAS/validation, performance, SR-IOV, and power-management surfaces. The masks alone do not encode whether a field is read-only, write-one-to-clear, sticky, self-clearing, or sequencing-sensitive.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes MMIO-backed hardware state in the MMHUB memory-management path.

The represented hardware state includes:

- VM context state: context enable bits, page-table depth/block size, per-fault interrupt/default behavior, retry policy, and 64-bit page-table base/start/end address fields.
- Invalidation state: semaphore, request, ack, VMID mask, flush type, L2/L1 invalidation selectors, optional logging, 4K-only mode, and invalidate address ranges for 18 engines.
- Aperture and memory-placement state: GART/system/AGP/framebuffer bounds, default physical page, local FB/sysmem/cacheable-DRAM ranges, local FB lock, and memory steering.
- L2/UTCL2 cache and TLB state: L2 transaction limits, walker behavior, bank selection/reserved client IDs, PTE fragment sizes, parity checking/injection, PTE cache dump controls, L1 TLB enable and policy fields.
- SR-IOV partition state: per-VF framebuffer size and offset for VF0-VF15, plus per-PF/VF PTE cache fragment-size selectors and VF-aware translation-assist metadata.
- Translation-assist state: request and response payloads for GPUVA/VMID translation assistance, including VMID/VFID, permissions, client ID, memory type, snoop/SPA/IO, PTE TMZ, no-PTE, NACK, LLC no-allocate, request, and ack status.
- Diagnostic and performance state: L2 and UTCL2 performance counter configuration, result selection, triggers, clear bits, stop-on-saturate behavior, counter values, compare values, group return fault status, and harvest-bypass groups.
- Power/clock state: CGTT clock-control and busy-control fields for L2 and UTCL2, plus memory light-sleep setup/hold fields.

Persistence is hardware-defined. Configuration registers generally persist until reset, power-gating loss, suspend/resume restore, or explicit reprogramming. Status, clear, ack, request, counter, fault, and parity-injection fields may have side effects or transient behavior and need hardware-specific sequencing from the surrounding driver.

## Dependencies And Integration Points

This chunk depends on the generated MMHUB 3.0.2 register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_offset.h` supplies the matching register addresses and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c` directly includes this shift/mask header and the offset header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.h`, `amdgpu.h`, `soc15_common.h`, and common VM/MMHUB helpers provide the driver-side structures and MMIO helper APIs that consume these macros.

Direct integration observed in this tree:

- `mmhub_v3_0_2_get_invalidate_req()` uses `MMVM_INVALIDATE_ENG0_REQ` fields from this chunk to create the invalidate command consumed by common VM hub invalidation paths.
- `mmhub_v3_0_2_setup_vm_pt_regs()`, `mmhub_v3_0_2_init_gart_aperture_regs()`, and `mmhub_v3_0_2_setup_vmid_config()` use the context page-table base/start/end offsets whose fields are described here; the values are written in page-number units using low/high register pairs.
- `mmhub_v3_0_2_init_system_aperture_regs()` writes AGP and system aperture registers covered here and skips host-owned aperture bounds for SR-IOV virtual functions.
- `mmhub_v3_0_2_init_tlb_regs()` uses `MMMC_VM_MX_L1_TLB_CNTL` fields covered by the end of this chunk and masks continued in the next chunk to enable L1 TLB, advanced driver model, system access mode, and uncached MTYPE.
- `mmhub_v3_0_2_init_cache_regs()` writes `MMVM_L2_CNTL4` and `MMVM_L2_CNTL5` fields in this chunk and skips inaccessible cache registers for SR-IOV virtual functions.
- `mmhub_v3_0_2_enable_system_domain()` and `mmhub_v3_0_2_setup_vmid_config()` use context-control fields from this chunk for system VMID and user VMID setup.
- `mmhub_v3_0_2_program_invalidation()` uses invalidate-engine address-range registers from this chunk to initialize all 18 engines.
- `mmhub_v3_0_2_init()` derives `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` from adjacent register offsets whose field layouts are represented here, and builds `hub->vm_cntx_cntl_vm_fault` from `MMVM_CONTEXT1_CNTL` interrupt masks.
- `mmhub_v3_0_2_get_fb_location()` masks `regMMMC_VM_FB_LOCATION_BASE` with `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK`, and `mmhub_v3_0_2_get_mc_fb_offset()` reads `regMMMC_VM_FB_OFFSET`; both field definitions are in this chunk.

Indirect integration is expected in performance/debug tooling, SR-IOV management, firmware/hypervisor setup, and hardware validation code that uses the performance-counter, translation-assist, per-VF framebuffer, parity, PTE dump, and harvest/fault-status fields.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can silently program a different MMHUB field and cause VM faults, invalidation failure, stale translations, broken apertures, or GPU hangs.
- The chunk starts and ends mid-register. `MMVM_L2_CNTL4` is incomplete at the start, and `MMMC_VM_MX_L1_TLB_CNTL` is incomplete at the end. The merge lane must combine adjacent chunks before making complete file-level statements about those registers.
- Context registers are repeated 16 times with nearly identical layouts. Driver code often programs context 1 using `hub->ctx_distance` to reach contexts 1-15; offset or stride mismatches can leave some VMIDs disabled or with wrong fault/retry policy.
- Invalidation registers are repeated 18 times. Per-engine request/ack/range fields must stay aligned with `hub->eng_distance` and `hub->eng_addr_distance`; a bad stride can poll or program the wrong invalidation engine.
- Invalidation request fields are command-like, not passive data. Incorrect `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, L1/L2/PDE selectors, or address range can leave stale TLB/cache entries after VM page-table updates.
- Page-table base/start/end values are split across low/high 32-bit registers and written in shifted page-number units. Incorrect shifts or high/low ordering can point MMHUB at the wrong page tables or expose the wrong virtual address range.
- Fault-policy fields affect user-visible recovery behavior. Misprogramming interrupt/default/retry bits can hide faults by redirecting to default pages, cause fault storms, or crash on faults that should be recoverable.
- SR-IOV fields and access restrictions are sensitive. `mmhub_v3_0_2.c` deliberately skips some PF-owned registers for virtual functions; writing per-VF framebuffer, aperture, cache, or translation-assist controls from the wrong privilege context can be blocked or corrupt partitioning assumptions.
- Diagnostic fields such as parity injection, PTE cache dump, performance-counter clear, and translation-assist request/ack can have side effects. They should not be changed by ordinary VM setup paths without validation intent.
- Clock-gating/busy fields can interact with active traffic. Bad CGTT/LS/busy programming can produce hangs or performance regressions that only appear under idle transitions or suspend/resume.
- Cross-generation similarity is not enough. Many names resemble other MMHUB versions, but masks, field presence, and address offsets must be kept matched to the 3.0.2 offset/mask pair.

## Test Signals

Useful validation signals for this chunk are build coverage, generated-header consistency, and MMHUB VM behavior:

- Build AMDGPU with MMHUB 3.0.2 support enabled. Missing or mismatched macros should surface in `mmhub_v3_0_2.c` through `REG_SET_FIELD`, mask constants, and offset/mask include use.
- Compare this generated header slice against AMD's authoritative MMHUB 3.0.2 register database and the matching `mmhub_3_0_2_offset.h`; every field name must align with the correct register offset and bit layout.
- Boot hardware using `mmhub_v3_0_2_funcs.gart_enable` and confirm GART setup succeeds without MMHUB VM faults during memory allocations, command submission, DMA, display/media traffic, and suspend/resume.
- Exercise VMID page-table updates and invalidations. Signals include correct invalidation ack behavior, no stale mappings after unmap/remap, and no timeouts in common VM hub invalidation paths.
- Stress all programmed VM contexts, especially contexts 1-15, to catch wrong context-control stride, page-table bounds, retry behavior, or fault-default settings.
- Validate fault handling by toggling default fault behavior through `set_fault_enable_default`, provoking controlled VM faults, and checking that interrupt/default/retry behavior and logged client information match expectations.
- Test SR-IOV PF and VF paths separately. VFs should avoid PF-owned aperture/cache writes, while PF/hypervisor setup should correctly expose per-VF framebuffer size/offset and aperture state.
- Validate framebuffer and aperture helpers: `get_fb_location()` should decode `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK` correctly, and MC framebuffer offset reads should match platform memory maps.
- Run performance-counter/debug validation for L2 and UTCL2 counters: select events, clear, enable, set triggers, read LO/HI results, and verify stop-on-saturate or compare behavior where supported.
- Hardware validation can test parity/PTE-dump/translation-assist fields, but those should remain isolated from normal driver paths because they can inject errors, stall on ready/ack bits, or alter diagnostic state.

## Cross-Chunk Notes

The previous chunk owns the first `MMVM_L2_CNTL4` field shifts (`L2_CACHE_4K_PARTITION_COUNT`, `VMC_TAP_PDE_REQUEST_PHYSICAL`, and `VMC_TAP_PTE_REQUEST_PHYSICAL`). This chunk owns the rest of `MMVM_L2_CNTL4` masks and later fields. The next chunk owns the remaining `MMMC_VM_MX_L1_TLB_CNTL` masks plus following MMHUB 3.0.2 registers. The final per-file research document should reconcile those boundaries before describing complete L2 control or L1 TLB control behavior.

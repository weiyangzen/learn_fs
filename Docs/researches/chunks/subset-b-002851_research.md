# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 23605-25971

## Scope And Purpose

This chunk is a generated AMDGPU MMHUB 9.4.1 shift/mask header section. It contains preprocessor constants only: no C functions, structs, enums, storage objects, branches, or loops. The constants define bit offsets and masks for MMHUB power-control, ATC/L2, page-fault, VM-context, and invalidation-engine registers.

The covered range starts inside the `mmhub_pctldec0` address block immediately after the `PCTL0_MMHUB_DEEPSLEEP_IB` register heading, continues through `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, `mmhub_l1tlb_vml1prdec`, `mmhub_utcl2_atcl2dec`, `mmhub_utcl2_vml2pfdec`, and the first part of `mmhub_utcl2_vml2vcdec`, and ends inside the `VML2VC0_VM_INVALIDATE_ENG6_REQ` register. The neighboring chunk is needed for the final `CLEAR_PROTECTION_FAULT_STATUS_ADDR_MASK` for engine 6 and all later invalidation request/ack/address registers.

The practical purpose is to provide the bit-field contract consumed by AMDGPU MMHUB v9.4 code. Driver code combines these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with companion register offsets from `mmhub_9_4_1_offset.h`, defaults from `mmhub_9_4_1_default.h`, and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

## Important APIs, Types, And Register Families

There are no callable APIs or local types in this chunk. The public surface is the generated macro namespace.

Important register families covered here are:

- `PCTL0_MMHUB_DEEPSLEEP_IB`, `PCTL0_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL0_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL0_PG_IGNORE_DEEPSLEEP`, and `PCTL0_PG_IGNORE_DEEPSLEEP_IB`: per-domain deep-sleep request, override, inbound, and ignore bitmaps. They expose `DS0` through `DS16`, plus ATHUB/all-IP aggregate fields on selected registers and a `SETCLEAR` bit on the inbound deep-sleep register.
- `PCTL0_SLICE[0-4]_CFG_DAGB_BUSY`: single `BUSY` bit per slice for DAGB activity gating state.
- `PCTL0_SLICE[0-4]_CFG_DS_ALLOW` and `_IB`: per-slice deep-sleep-allow bitmaps for domains `DS0` through `DS16`.
- `PCTL0_UTCL2_MISC` and `PCTL0_SLICE[0-4]_MISC`: critical-register lock, tile idle threshold, RENG memory light-sleep enable, state-controller force-done, execute-on-register-update, read-timer enable, and slice-only `DEEPSLEEP_DISCSDP`.
- `PCTL0_UTCL2_RENG_EXECUTE` and `PCTL0_SLICE[0-4]_RENG_EXECUTE`: register-engine execution controls, including execute-now, execute-now mode, start pointer, and end pointer. UTCL2 uses an 11-bit index/start/end range shape, while slices use a 10-bit range shape.
- `PCTL0_*_RENG_RAM_INDEX` and `PCTL0_*_RENG_RAM_DATA`: register-engine RAM address and full 32-bit data fields for UTCL2 and slices 0-4.
- `PCTL0_*_STCTRL_REGISTER_SAVE_RANGE[0-4]` and `PCTL0_*_STCTRL_REGISTER_SAVE_EXCL_SET[0-1]`: state-controller register save base/limit pairs and exclusion pairs for UTCL2 and slices 0-4.
- `VML1_0_MC_VM_MX_L1_TLB[0-7]_STATUS`: L1 TLB status registers with `BUSY` and `VMID` fields.
- `VML1PL0_MC_VM_MX_L1_PERFCOUNTER[0-3]_CFG`, `VML1PL0_MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, `VML1PR0_MC_VM_MX_L1_PERFCOUNTER_LO`, and `VML1PR0_MC_VM_MX_L1_PERFCOUNTER_HI`: L1 TLB performance counter event select, compare, mode, enable, clear, start/stop trigger, low/high result, and saturation behavior.
- `ATCL2_0_ATC_L2_CNTL`, `CNTL2`, `CNTL3`, and `CNTL4`: ATC L2 cache enablement, faulting behavior, debugger disablement, invalidate requests, cache-update policy, transaction-limit, and real-time/non-real-time controls.
- `ATCL2_0_ATC_L2_CACHE_DATA[0-2]`, `ATCL2_0_ATC_L2_CACHE_4K_DSM_*`, and `ATCL2_0_ATC_L2_CACHE_2M_DSM_*`: cache debug/readback and DSM/error-injection fields for 4K and 2M entries, including inject delay, irritator data, single write, error injection, counter write, SEC/DED count, and FUE test fields.
- `ATCL2_0_ATC_L2_STATUS`, `STATUS2`, and `STATUS3`: ATC L2 busy and invalidation-finished status.
- `ATCL2_0_ATC_L2_MISC_CG`, `MEM_POWER_LS`, and `CGTT_CLK_CTRL`: clock gating, memory light-sleep, delay/hysteresis, and soft override controls.
- `ATCL2_0_ATC_L2_MM_GROUP_RT_CLASSES`: full-width group real-time class mapping.
- `VML2PF0_VM_L2_CNTL`, `CNTL2`, `CNTL3`, and `CNTL4`: VM L2 cache enablement, fragment processing, endian swap, PDE/PTE cache policy, default-page handling, invalidate mode, cache sizing, bank selection, force-miss controls, identity-mode fragment size, TAP request physical controls, transaction limits, and clock-gating override.
- `VML2PF0_VM_L2_STATUS`: L2 busy, per-context-domain busy bitmap, and PTE/PDE parity-error status fields.
- `VML2PF0_VM_DUMMY_PAGE_FAULT_*`: dummy-page fault enable/address controls.
- `VML2PF0_VM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, `MM_CNTL3`, `MM_CNTL4`, `STATUS`, address, and default-address registers: global protection-fault control, client interrupt masks, retry/PRT controls, VML1 read/write client masks, fault status decode fields, faulting logical address, and default physical page address.
- `VML2PF0_VM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `VML2PF0_VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: identity aperture low/high logical-page bounds and physical offset fields.
- `VML2PF0_VM_L2_MM_GROUP_RT_CLASSES`: 32 one-bit group real-time class flags.
- `VML2PF0_VM_L2_BANK_SELECT_RESERVED_CID` and `CID2`: reserved read/write client IDs, enable, reserved-cache invalidation mode, and private invalidation fields.
- `VML2PF0_VM_L2_CACHE_PARITY_CNTL` and `VML2PF0_VM_L2_CGTT_CLK_CTRL`: parity interrupt enables and cache/clock-gating override timing fields.
- `VML2VC0_VM_CONTEXT0_CNTL` through `VML2VC0_VM_CONTEXT15_CNTL`: per-VMID context enable, page-table depth, block size, retry behavior, and protection-fault interrupt/default controls.
- `VML2VC0_VM_CONTEXTS_DISABLE`: disable bitmap for contexts 0-15.
- `VML2VC0_VM_INVALIDATE_ENG0_SEM` through `ENG17_SEM`: one-bit invalidation-engine semaphore fields.
- `VML2VC0_VM_INVALIDATE_ENG0_REQ` through the partial `ENG6_REQ`: per-VMID invalidate request mask, flush type, invalidate L2 PTEs/PDE0/PDE1/PDE2/L1 PTEs, and clear-protection-fault-status-address request fields.

## Control Flow And State Behavior

This header chunk has no runtime control flow. Its constants are substituted into MMHUB driver code at compile time.

The runtime flow that uses these definitions is in AMDGPU MMHUB setup and maintenance code. `mmhub_v9_4.c` includes `mmhub_9_4_1_offset.h`, this shift/mask header, and `mmhub_9_4_1_default.h`. It reads default or current register values, uses `REG_SET_FIELD` with macros such as `VML2VC0_VM_CONTEXT0_CNTL__ENABLE_CONTEXT_MASK`, and writes the composed values through SOC15 register helpers.

Several flow patterns are implied by the field groups:

- Power-management and deep-sleep control code programs PCTL registers to allow, override, or ignore deep-sleep requests for UTCL2, slices, MMHUB, ATHUB, and aggregate domains. The `PCTL0_*_MISC` and RENG fields describe how register save/restore and register-engine command execution are triggered around power transitions.
- VM/GART initialization programs L2 cache controls, identity aperture bounds, default fault addresses, VM context controls, and invalidate ranges. In `mmhub_v9_4.c`, `mmhub_v9_4_enable_system_domain()` updates `VML2VC0_VM_CONTEXT0_CNTL`, `mmhub_v9_4_setup_vmid_config()` programs contexts 1-15 with page-table depth/block-size and fault policy, and `mmhub_v9_4_program_invalidation()` initializes invalidation-engine address ranges that are adjacent to this chunk.
- TLB/cache invalidation flow uses per-engine semaphore, request, ack, and address registers. This chunk covers semaphore fields for engines 0-17 and request fields for engines 0-6; the generic VM hub setup in `mmhub_v9_4_init()` records engine 0 register offsets and computes `eng_distance` from engine 1 minus engine 0 so common VM invalidation code can address all engines.
- Fault handling and diagnostics read `VML2PF0_VM_L2_PROTECTION_FAULT_STATUS` and fault address registers, then clear or control subsequent status updates through protection-fault control bits. The status fields decode `MORE_FAULTS`, walker error, permission fault class, mapping error, client ID, read/write, atomic, VMID, VF, and VFID.
- Clock-gating code reads and writes fields such as `ATCL2_0_ATC_L2_MISC_CG__ENABLE_MASK` and `ATCL2_0_ATC_L2_CGTT_CLK_CTRL` overrides to enable or disable medium-grain and light-sleep behavior.

State is entirely hardware state. The header does not store values, serialize writes, or validate access rights. Many fields are persistent configuration until reset, suspend/resume, GPU reset, power-gating, firmware programming, or driver reinitialization. Status, semaphore, request, invalidate, clear, counter, and fault-address fields are transient or side-effectful: they may be set by hardware, polled by the driver, cleared by write-one/control bits, or consumed by common VM invalidation/fault paths.

## Dependencies And Integration Points

The immediate companion files are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`, which supplies `mm*` register offsets and base-index macros for the register names in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h`, which supplies default register values such as VM context defaults, invalidation request defaults, and PCTL defaults.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, the primary consumer in this tree. It includes this header and uses these masks for VM context setup, L2 cache programming, fault controls, clock gating, EDC counters near the previous chunk boundary, and VM hub register layout initialization.

Key integration points in `mmhub_v9_4.c` include:

- `mmhub_v9_4_enable_system_domain()` uses `VML2VC0_VM_CONTEXT0_CNTL` fields to enable context 0 and set depth/retry behavior.
- `mmhub_v9_4_setup_vmid_config()` uses the repeated `VML2VC0_VM_CONTEXT1_CNTL` field layout as a template for contexts 1-15, relying on offset distances rather than hand-coded register names for every context.
- `mmhub_v9_4_init_cache_regs()` uses `VML2PF0_VM_L2_CNTL*` fields for cache enablement, bank selection, fragment size, and TAP request physical controls.
- `mmhub_v9_4_update_fault_enable_default()` uses `VML2PF0_VM_L2_PROTECTION_FAULT_CNTL` fields to control default fault handling and crash-on-fault behavior.
- `mmhub_v9_4_init()` records VM hub offsets for context base addresses, invalidation sem/request/ack, context control, and L2 protection fault status/control, then computes context and invalidation-engine distances from adjacent generated register offsets.
- `mmhub_v9_4_update_medium_grain_clock_gating()` uses `ATCL2_0_ATC_L2_MISC_CG__ENABLE_MASK` and related clock-gating fields.
- The RAS/EDC table in `mmhub_v9_4.c` uses adjacent `MMEA4_EDC_CNT3` fields from just before this chunk boundary; this chunk continues into other MMHUB reliability and diagnostics fields such as ATC DSM counters and parity/fault status.

Other consumers include media ring setup code that writes hard-coded packet values for `PCTL0_MMHUB_DEEPSLEEP_IB` in older JPEG paths. Comments in JPEG v4.0.3 note that the `PCTL0_MMHUB_DEEPSLEEP_IB` register can vary by MMHUB version, which reinforces why the matching versioned offset/mask header matters.

Although this repository path is under a Ceph client source import, this file belongs to the Linux AMDGPU DRM hardware interface. It has no Ceph filesystem control flow, wire protocol behavior, distributed lock state, or on-disk persistence.

## Risks And Edge Cases

- This file is a hardware ABI. A wrong mask, wrong shift, or mismatched versioned header can compile cleanly while programming the wrong MMHUB field, causing GPU memory faults, failed invalidations, stale translations, lost fault diagnostics, power-management regressions, or hangs.
- The chunk starts after the `PCTL0_MMHUB_DEEPSLEEP_IB` comment and ends before the final `VML2VC0_VM_INVALIDATE_ENG6_REQ__CLEAR_PROTECTION_FAULT_STATUS_ADDR_MASK`. Whole-file analysis must reconcile neighboring chunks before treating those two registers as complete.
- PCTL deep-sleep and register-engine fields are power-state controls, not passive metadata. Mistakes can prevent deep sleep, force domains into sleep at the wrong time, skip register save/restore, or run register-engine RAM commands with the wrong start/end pointer.
- `CRITICAL_REGS_LOCK`, save range, and exclusion-set fields imply protected register windows. Incorrect programming can either leave critical state unprotected during power transitions or block intended state restoration.
- `RENG_RAM_DATA` and several address/status fields use full-width `0xFFFFFFFFL` masks. Callers should treat them as 32-bit register values and avoid signed-extension or format-string confusion in diagnostics.
- ATC and VM L2 invalidate fields are side-effectful. Read-modify-write patterns must avoid accidentally asserting `INVALIDATE_ALL_L1_TLBS`, `INVALIDATE_L2_CACHE`, per-VMID invalidate bits, or clear-fault-status bits.
- Repeated VM context controls are highly regular but easy to misuse. The driver programs context 1 as a template using context-distance arithmetic; a broken generated offset or field layout for any context would affect many VMIDs.
- Fault-control fields combine default action, interrupt enable, retry/PRT behavior, client masks, and crash policy in adjacent bits. Incorrect defaults can suppress important faults, create interrupt storms, change no-retry/retry behavior, or crash the GPU on recoverable faults.
- Protection-fault status fields are packed and diagnostic-critical. Misdecoding `CID`, `VMID`, `VF`, or `VFID` can send debugging and RAS analysis toward the wrong client or virtual function.
- Identity aperture and dummy/default fault addresses are split into low 32-bit and high 4-bit fields. Callers must preserve GPU page-number semantics and not treat these as arbitrary byte addresses without the surrounding driver convention.
- ATC DSM/error-injection and parity controls should be isolated to diagnostics/RAS validation. Leaving injection, counter-write, FUE, or parity interrupt bits enabled unexpectedly can create false error reports or real fault handling noise.
- Clock-gating and memory light-sleep fields are timing-sensitive. Bad `ON_DELAY`, `OFF_HYSTERESIS`, light-sleep setup/hold, or override values can reduce power savings, introduce wake latency, or destabilize active VM/ATC traffic.
- Invalidation-engine request groups are repeated. This chunk contains complete request masks for engines 0-5 and all but one mask for engine 6; reviewers should check engine 0, a middle engine, and the boundary engine when validating generated consistency.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is compile-time, generated-data, and hardware-observation based:

- Build AMDGPU code that includes `mmhub_v9_4.c` and the MMHUB 9.4.1 headers to catch missing, renamed, or syntactically invalid macros.
- Run static mask/shift consistency checks: single-bit masks should match their shifts, multi-bit masks should be contiguous, fields in a register should not overlap, full-width fields should have shift zero, and repeated registers should preserve identical layouts.
- Cross-check `mmhub_9_4_1_sh_mask.h` against `mmhub_9_4_1_offset.h` so every register family in this chunk has the expected `mm*` offset and base index.
- Compare defaults in `mmhub_9_4_1_default.h` with the masks here, especially `PCTL0_CTRL`, `VML2VC0_VM_CONTEXT[0-15]_CNTL`, invalidation request defaults, and L2/fault-control defaults.
- Exercise GART and VM initialization on MMHUB 9.4 hardware or simulator. Signals include successful context 0 enablement, contexts 1-15 configured with expected depth/block size, correct L2 cache setup, and no unexpected VM fault storms.
- Exercise TLB invalidation under BO map/unmap, VM update, GPU reset, and process teardown. Watch per-engine semaphore/request/ack behavior and ensure invalidations complete without stale translations.
- Inject or observe protection faults and confirm that `VML2PF0_VM_L2_PROTECTION_FAULT_STATUS` decodes the expected client, VMID, VF/VFID, access type, and fault reason, and that clear/subsequent-update controls behave as expected.
- Run suspend/resume, runtime power management, and clock-gating tests to validate PCTL, ATC L2 clock-gating, memory light-sleep, and register-save/restore behavior.
- Use RAS/debug validation for ATC DSM, parity, and cache status fields only in controlled diagnostic paths, verifying that injection and counter bits do not persist into normal operation.

## Chunk Notes For Merge Lane

This is chunk 11 of 19 for `mmhub_9_4_1_sh_mask.h`. It continues the `mmhub_pctldec0` block that started in the previous chunk, then covers L1 TLB status/performance masks, ATC L2 masks, VM L2/page-fault/identity-aperture masks, VM context controls for contexts 0-15, context disable masks, invalidation semaphores for engines 0-17, and invalidation request masks through most of engine 6. The final per-file report should merge this with chunks 10 and 12 before making complete statements about PCTL0 control or the full invalidation-engine register set.

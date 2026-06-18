# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 18712-21060

## Scope

This chunk is a generated AMD MMHUB 1.8.0 register field header segment. It starts in the tail of the `MMEA4` address-decode block with `MMEA4_MISC2`, corrected-error status, and always-on link-manager fields. It then covers the `aid_mmhub_pctldec0` power-control block, L1 TLB status and performance-counter fields, ATC L2 fields, VM L2 control/fault/ECC fields, all `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` field masks, `VM_CONTEXTS_DISABLE`, and the beginning of the VM invalidation-engine request table through `VM_INVALIDATE_ENG4_REQ`.

The file contains preprocessor constants only. Every logical register field is represented as a `REGISTER__FIELD__SHIFT` macro plus a matching `REGISTER__FIELD_MASK` macro. There are no C functions, structs, variables, storage allocations, loops, branches, locks, or direct MMIO operations in this chunk. Runtime behavior comes from AMDGPU code that includes this header with the matching `mmhub_1_8_0_offset.h` register offsets and then uses `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15 helpers.

Major covered blocks are:

- `MMEA4_MISC2`, `MMEA4_CE_ERR_STATUS_LO`, `MMEA4_MISC_AON`, and `MMEA4_CE_ERR_STATUS_HI`.
- `PCTL0_CTRL`, global MMHUB deep-sleep/override/ignore registers, per-slice `PCTL0_SLICE{0..4}_CFG_*`, `PCTL0_UTCL2_MISC`, and `PCTL0_SLICE{0..4}_MISC`.
- `MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS`.
- L1 TLB performance-counter config, result-control, low-result, and high-result fields.
- `ATC_L2_CNTL`, cache data, status, clock/power, DSM error-injection/counting, and MM group real-time-class fields.
- `VM_L2_CNTL` through `VM_L2_CNTL5`, VM dummy-page fault fields, VM L2 protection-fault control/status/address fields, identity-aperture fields, MM group real-time-class selection, reserved-CID bank-select fields, parity control, clock/busy control, and ECC index/control/status fields.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL`, `VM_CONTEXTS_DISABLE`, `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`, and `VM_INVALIDATE_ENG0_REQ` through the start of `VM_INVALIDATE_ENG4_REQ`.

## Purpose

This header segment defines the bit layout for MMHUB register programming on ASICs using the MMHUB 1.8.0 register map. The companion offset header says where a register is located; this shift/mask header says how to pack and unpack individual fields in that register.

The practical purpose is to make VM, memory-routing, RAS, TLB, ATC, and power-management programming readable and generation-specific. For example, `mmhub_v1_8.c` uses these field names to configure the L1 TLB, L2 cache, VMID contexts, VM fault-default behavior, active page migration retry behavior, identity aperture disablement, and invalidation-engine metadata. The macros also support RAS status decoding for `MMEA4` corrected errors, ATC/VM L2 ECC status, and low-level performance counter setup.

Because the header is generated, the important contract is exactness: the field name, bit shift, and mask must match the hardware register database for MMHUB 1.8.0. A wrong mask can compile successfully while changing the wrong bit in a live MMIO register.

## Important Macro Families

### MMEA4 RAS, Throttling, and Always-On Fields

The chunk begins with `MMEA4_MISC2` fields for DRAM/GMI arbitration swap controls, DRAM/GMI burst limits, IO read/write priority enablement, return-swap mode, request blocking, request-blocked status, and DRAM/GMI read/write throttle bits. These fields describe MMEA address-decode behavior and throttling state for the fourth memory-mapped engine/address decode instance.

The `MMEA4_CE_ERR_STATUS_LO` and `MMEA4_CE_ERR_STATUS_HI` macros define corrected-error status latches. The low word records validity flags, an address field, and memory ID. The high word records ECC, error-info validity, error info, CE count, poison, and reserved bits. `mmhub_v1_8.c` includes `regMMEA4_CE_ERR_STATUS_LO` and `regMMEA4_CE_ERR_STATUS_HI` in `mmhub_v1_8_ce_reg_list`, so these masks are part of MMHUB RAS query/reset behavior even though the RAS code does not live in this header.

`MMEA4_MISC_AON` exposes link-manager partial-ack hysteresis and deassert-mode fields. Those are always-on control-plane bits and should be treated as hardware policy/state, not software-owned persistent data.

### PCTL0 Deep-Sleep, Power-Gating, and Slice Controls

`PCTL0_CTRL` contains global MMHUB power-control fields: power-gating enable, allowed deep-sleep mode, RSMU and DAGB idle thresholds, an option to ignore protection faults for state-control purposes, EA0 through EA5 partial/full acknowledgement override bits, and RSMU read-timer controls.

The deep-sleep bitmaps are repeated across several registers:

- `PCTL0_MMHUB_DEEPSLEEP_IB` exposes DS0 through DS16 plus a `SETCLEAR` bit.
- `PCTL0_MMHUB_DEEPSLEEP_OVERRIDE` and `_OVERRIDE_IB` expose DS0 through DS16 plus ATHUB/CANE or IB-specific override coverage.
- `PCTL0_PG_IGNORE_DEEPSLEEP` and `_IB` define which deep-sleep indications power-gating logic should ignore, including ATHUB and all-IPS variants.
- `PCTL0_SLICE{0..4}_CFG_DS_ALLOW` and `_IB` repeat DS0 through DS16 allow masks per slice.

The per-slice `PCTL0_SLICE{0..4}_CFG_DAGB_BUSY` fields are full-width `DB_LNCFG` masks. `PCTL0_UTCL2_MISC` and `PCTL0_SLICE{0..4}_MISC` define register-engine start pointers, critical-register locks, tile idle thresholds, memory light-sleep enablement, forced PGFSM completion, deep-sleep/disconnect behavior, register-engine execute-on-update, and read timer enablement. These fields connect MMHUB to clock, power, and reset sequencing paths.

### L1 TLB Status and Performance Counters

`MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS` are compact status registers with `BUSY` and `FOUND_PARITY_ERRORS` bits for eight L1 TLB instances. They are useful for debug, hang analysis, and parity/error validation after L1 TLB programming.

The L1 performance counter register families provide:

- Four counter configs, `MC_VM_MX_L1_PERFCOUNTER0_CFG` through `3_CFG`, each with `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`.
- `MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL` for selecting result counters, start/stop triggers, global enable, clear-all, and stop-on-saturate.
- `MC_VM_MX_L1_PERFCOUNTER_LO` and `_HI`, where the high word also carries a compare value.

The enable/clear/trigger fields are stateful hardware controls. Software must avoid assuming reads are passive if a selected counter mode has side effects elsewhere in the performance-monitoring pipeline.

### ATC L2 Translation, Cache, DSM, and Clock Fields

The ATC L2 block defines address-translation cache policy and observability fields:

- `ATC_L2_CNTL` covers translation read/write request counts, host translation request counts, address-mod dependence, cache invalidation mode, default-page-out-to-system-memory behavior, fragment/aperture interaction mode, and client GPA request fragment size.
- `ATC_L2_CNTL2` covers bank select/count, cache update mode, LRU update on write, tag-index swapping, VMID mode, and wildcard reference value.
- `ATC_L2_CACHE_DATA0..3` expose a cache-data inspection window containing validity, cached attributes, virtual page address high/low pieces, and physical page address pieces.
- `ATC_L2_CNTL3` covers fragment sizes, delayed invalidation requests, ATS request credits, clock-request hysteresis, and repeater fine-grain clock-gating override.
- `ATC_L2_STATUS` and `ATC_L2_STATUS2` expose busy/outstanding-request and uncorrectable-error status.
- `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL` define clock-gating and memory light-sleep controls.
- `ATC_L2_CACHE_{4K,32K,2M}_DSM_INDEX` and `_DSM_CNTL` define ECC/DSM index selection, error injection, single-write, delay, counter write, SEC/DED count, and FUE test controls.
- `ATC_L2_CNTL4` and `ATC_L2_MM_GROUP_RT_CLASSES` define invalidate-map miss-disable and MM group real-time-class classification.

These masks interact with GPU address translation and ATS behavior. In the local `mmhub_v1_8.c`, ATC is enabled through `MC_VM_MX_L1_TLB_CNTL__ATC_EN` outside this exact chunk, while this chunk supplies lower-level ATC L2 policy/status fields needed by debug, RAS, and platform-specific tuning.

### VM L2 Cache, Fault, Identity Aperture, and ECC Fields

The `VM_L2_*` families are the main VM translation cache controls in this chunk. `VM_L2_CNTL` defines L2 cache enablement, L2 fragment processing, PTE/PDE endian swap modes, PDE cache tag generation, LRU update behavior, default-page-out behavior, PDE cache split mode, effective queue size, PDE fault classification, context-1 identity access mode, identity-mode fragment size, and tag-index swapping. `mmhub_v1_8_init_cache_regs()` uses these fields to enable L2 cache, fragment processing, PDE tag generation policy, fault classification, and identity access mode.

`VM_L2_CNTL2` defines global invalidation controls, big-page optimization/VMID mode, invalidate-cache mode, PDE cache effective size, queue stall behavior, and retry-latency behavior. `mmhub_v1_8_init_cache_regs()` sets the `INVALIDATE_ALL_L1_TLBS` and `INVALIDATE_L2_CACHE` bits during cache bring-up.

`VM_L2_CNTL3`, `VM_L2_CNTL4`, and `VM_L2_CNTL5` define bank selection, update modes, wildcard values, 4K/bigK fragment and effective sizes, force-miss controls, partition count, physical walker request controls, MM IFIFO transaction limits, clock-gating overrides, VFIFO head-of-queue behavior, and walker fetch PDE mtype/noalloc controls. `mmhub_v1_8.c` programs `VM_L2_CNTL3` from `regVM_L2_CNTL3_DEFAULT` and adjusts bank/fragment fields based on `adev->gmc.translate_further`; it programs `VM_L2_CNTL4` from `regVM_L2_CNTL4_DEFAULT` and toggles physical request fields for XGMI CPU-connected or APP APU configurations.

The VM fault registers are split across dummy-page and protection-fault controls:

- `VM_DUMMY_PAGE_FAULT_CNTL` and address registers define dummy-page fault enablement, logical-address comparison behavior, and low/high dummy-page address fields.
- `VM_L2_PROTECTION_FAULT_CNTL` defines fault status clearing, subsequent status-address update permission, default handling for range/PDE/translate-further/NACK/dummy/valid/read/write/execute faults, no-retry client interrupt bitmaps, and crash-on-fault bits.
- `VM_L2_PROTECTION_FAULT_CNTL2` defines PRT fault interrupt client maps, active page migration PTE behavior, read-retry behavior, and retry fault interrupt enablement.
- `VM_L2_PROTECTION_FAULT_STATUS` exposes more-faults, walker error, permission faults, mapping error, client ID, read/write, atomic, VMID, VF/VFID, uncorrectable error, and fatal error detected bits.
- Protection fault address/default-address registers split logical or physical page addresses into low 32-bit and high 4-bit pieces.

`mmhub_v1_8_init_system_aperture_regs()` writes the protection-fault default address and sets `ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`. `mmhub_v1_8_set_fault_enable_default()` updates most default-fault policy bits and sets crash-on-no-retry/retry bits when default handling is disabled. Fault handling correctness therefore depends directly on these masks.

Identity-aperture fields define context-1 low/high logical page boundaries and physical offset. `mmhub_v1_8_disable_identity_aperture()` uses the corresponding offset registers and these field definitions describe the low/high split.

The VM L2 reliability and debug fields include `VM_L2_BANK_SELECT_RESERVED_CID`, `VM_L2_BANK_SELECT_RESERVED_CID2`, `VM_L2_CACHE_PARITY_CNTL`, `VM_L2_CGTT_CLK_CTRL`, `VM_L2_CGTT_BUSY_CTRL`, ECC index registers for VML2, walker memory, and UTCL2, ECC control registers with injection/test/count fields, ECC status registers, `UTCL2_EDC_MODE`, and `UTCL2_EDC_CONFIG`. These support RAS, error injection, and low-level diagnostics.

### VM Context Controls and Context Disable Bitmap

`VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` are repeated VMID context-control bit definitions. Each context has fields for:

- `ENABLE_CONTEXT`.
- Page-table depth and block size.
- Interrupt and default handling for range, dummy-page, PDE0, valid, read, write, execute, and secure protection faults.
- `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT`.

`mmhub_v1_8_enable_system_domain()` programs `VM_CONTEXT0_CNTL` with context enable, VMID0 page-table depth/block size, and retry fault behavior. `mmhub_v1_8_setup_vmid_config()` programs contexts 1 through 15 using `VM_CONTEXT1_CNTL` as the base and `hub->ctx_distance` spacing, enabling contexts and setting the default fault policy bits plus retry permission for per-process XNACK support.

`VM_CONTEXTS_DISABLE` is a 16-bit disable bitmap, one bit per context. It provides a compact hardware control for disabling VM contexts, distinct from writing each `VM_CONTEXTn_CNTL`.

The repeated field names are intentionally context-specific (`VM_CONTEXT7_CNTL__...`, etc.) even when the bit layout is identical. That lets generated code and register-field macros remain type/name safe for each concrete register.

### VM Invalidation Semaphores and Requests

The chunk defines single-bit semaphore fields for `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`. These registers arbitrate or signal use of the eighteen MMHUB invalidation engines.

It then defines request fields for `VM_INVALIDATE_ENG0_REQ` through the beginning of `VM_INVALIDATE_ENG4_REQ`:

- `PER_VMID_INVALIDATE_REQ` is a 16-bit VMID request bitmap.
- `FLUSH_TYPE` selects the invalidation/flush type.
- Individual invalidate bits cover L2 PTEs, L2 PDE0/PDE1/PDE2, and L1 PTEs.
- `CLEAR_PROTECTION_FAULT_STATUS_ADDR` requests fault-address status clearing.
- `LOG_REQUEST` requests request logging.

`mmhub_v1_8_init()` stores `regVM_INVALIDATE_ENG0_REQ` and computes `hub->eng_distance` from adjacent engine request offsets. Other TLB flush paths use these addresses indirectly through `amdgpu_vmhub`. The field masks in this chunk define the request value semantics that those paths must write.

## Control Flow and State Behavior

There is no executable control flow in this header. It affects runtime only when included into C code that expands the macros.

The state represented by the macros is hardware state:

- Configuration state, such as VM L2 cache enablement, fragment sizes, physical walker request policy, context enablement, retry-fault policy, ATC L2 request/cache policy, PCTL deep-sleep permission, and clock-gating settings.
- Status state, such as L1 TLB busy/parity status, ATC L2 busy/UCE status, VM L2 fault status, ECC status, and MMEA4 corrected-error latches.
- Counter and performance-monitoring state, such as L1 performance counters and DSM/ECC SEC/DED count fields.
- Request/acknowledgement state, such as VM invalidation semaphore and request registers.
- Error-injection/test state, such as ATC DSM controls and VML2/walker/UTCL2 ECC controls.

Some fields are write-one-to-clear, request, latch, or counter-control fields in hardware terms, but the header itself does not encode those semantics beyond names and masks. Ordering, timeouts, polling, reset values, and privilege constraints are implemented in driver code and hardware documentation.

AMDGPU also has mode2 save/restore storage for several VM/MMHUB registers in `struct amdgpu_gmc`, including `VM_L2_CNTL`, `VM_L2_CNTL2`, dummy-page fault registers, protection-fault registers, MM group RT class fields, bank select fields, parity control, all 16 VM context controls and page-table address arrays, and `MC_VM_MX_L1_TLB_CNTL`. This chunk contributes masks for many of those saved/restored registers, but the persistence itself is in the driver data structure, not in this generated header.

## Dependencies and Integration Points

This chunk depends on the AMD generated-register convention:

- `mmhub_1_8_0_offset.h` provides the matching `reg...` offset macros for the same MMHUB 1.8.0 register names.
- `soc15_common.h` and `soc15.h` provide SOC15 register-access helpers.
- `REG_SET_FIELD` and `REG_GET_FIELD` use the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` macros to modify packed register values.
- `amdgpu/mmhub_v1_8.c` is the primary local consumer for MMHUB 1.8 programming.

Observed integration points in `mmhub_v1_8.c` include:

- `mmhub_v1_8_init_system_aperture_regs()`, which programs `VM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` and updates `VM_L2_PROTECTION_FAULT_CNTL2__ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
- `mmhub_v1_8_init_cache_regs()`, which uses `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, and `VM_L2_CNTL4` fields to enable and tune the MMHUB L2 translation cache.
- `mmhub_v1_8_enable_system_domain()`, which uses `VM_CONTEXT0_CNTL` fields for VMID0 context enablement and page-table shape.
- `mmhub_v1_8_setup_vmid_config()`, which uses `VM_CONTEXT1_CNTL` fields and context spacing to initialize VMIDs 1 through 15.
- `mmhub_v1_8_disable_identity_aperture()`, which writes the identity aperture low/high and physical offset registers whose low/high page-number fields are defined here.
- `mmhub_v1_8_program_invalidation()` and `mmhub_v1_8_init()`, which rely on the invalidation-engine register family; this chunk provides semaphore and request field semantics for engines 0 through 4.
- `mmhub_v1_8_set_fault_enable_default()`, which uses `VM_L2_PROTECTION_FAULT_CNTL` masks to switch between default-page fault handling and crash-on-fault behavior.
- `mmhub_v1_8_ce_reg_list`, which references `MMEA4_CE_ERR_STATUS_LO/HI` offsets and depends on the matching status-valid, info-valid, address, memory-ID, CE-count, and poison field definitions for correct RAS interpretation.

## Risks

- Mask or shift drift is silent at compile time. A wrong bit definition can produce valid C that corrupts VM, ATC, power, or RAS behavior at runtime.
- The chunk mixes control, status, request, and error-injection fields. Treating request or clear bits as normal persistent configuration can lose fault information, trigger unexpected invalidations, or disturb performance counters.
- VM L2 fields are central to address translation. Incorrect `ENABLE_L2_CACHE`, invalidation, page-fragment, walker, or fault-classification masks can cause stale translations, VM faults, hangs, or data corruption.
- VM context fields are repeated across 16 contexts. A copy-generation error in one context's masks may only affect specific VMIDs and can be hard to reproduce.
- Invalidation request fields must align with the firmware/driver flush protocol. Bad `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, or L1/L2 invalidate masks can leave stale TLB entries after page-table updates.
- Protection-fault controls are security and stability sensitive. Incorrect default handling or crash-on-fault bits can either hide real faults by routing them to a dummy page or escalate recoverable faults into GPU resets.
- The address registers in this family split page addresses into low 32-bit and high 4-bit fields. Callers shift GPU addresses before writing, so mask mistakes here combine badly with address-shift mistakes in code.
- PCTL0 deep-sleep and clock/power fields can produce platform-specific failures. A wrong slice allow/ignore bit may only appear under suspend/resume, low-power states, clock gating, or multi-die activity.
- ATC L2 DSM/ECC controls include error injection and counter-write fields. Accidentally enabling injection or writing counters in production paths could pollute RAS telemetry or generate synthetic faults.
- The chunk stops mid-family at `VM_INVALIDATE_ENG4_REQ`; later invalidation-engine request, ack, and address-range fields are in subsequent lines/chunks and must be reconciled in the final per-file report.

## Test and Validation Signals

Useful validation is mostly build, boot, and hardware-integration testing:

- Build AMDGPU with MMHUB 1.8 support enabled to catch missing or renamed masks used by `mmhub_v1_8.c`.
- Boot on MMHUB 1.8 hardware and verify GART/VM bring-up, including VMID0 context programming and VMIDs 1 through 15 context setup.
- Run GPU memory-management workloads that update page tables and force TLB invalidations; hangs or stale mappings point at `VM_INVALIDATE_ENG*` request semantics or VM L2 invalidation fields.
- Exercise XNACK/retry-fault and active-page-migration paths, checking `VM_CONTEXTn_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` and `VM_L2_PROTECTION_FAULT_CNTL2` behavior.
- Trigger invalid memory accesses under debug kernels and confirm VM fault status decodes CID, VMID, RW/atomic, permission/mapping, VF/VFID, UCE, and FED fields as expected.
- Validate the default-page fault path by toggling `mmhub_v1_8_set_fault_enable_default()` behavior and confirming default-page routing versus crash-on-fault behavior.
- Run suspend/resume, reset, and clock/power-management stress tests to catch PCTL0 deep-sleep, slice, clock-gating, or UTCL2 miscellaneous field regressions.
- Query and reset MMHUB RAS state, verifying `MMEA4_CE_ERR_STATUS_LO/HI` decoded addresses, memory IDs, CE counts, poison, and validity flags.
- Use RAS injection or lab-only diagnostics for ATC DSM and VML2/walker/UTCL2 ECC fields, ensuring injection enable/count/test bits are only touched by intended diagnostic paths.
- Use performance-counter diagnostics to confirm L1 counter select, mode, enable, clear, trigger, result low/high, compare, and saturation behavior.
- Compare regenerated `mmhub_1_8_0_sh_mask.h` against the authoritative register database, with special attention to repeated VM context fields, PCTL slice fields, and invalidation-engine request fields.

## Cross-Chunk Notes

This chunk begins after most of `MMEA4_MISC2` has already been defined, so the complete `MMEA4_MISC2` field story is split with the previous chunk. It also ends while the invalidation-engine request family is still in progress; engines 5 through 17, invalidate acknowledgements, and address-range fields continue later in the source file. The merge/reconciliation lane should connect these neighboring chunks before producing the final per-file report.

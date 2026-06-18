# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 27043-29425

## Purpose

This chunk is generated-style register field metadata for the AMD GC 9.4.2 graphics core, used by Aldebaran-class AMDGPU paths. It defines `__SHIFT` and `_MASK` constants for shader resource descriptor words, shader queue cache controls, texture cache/texture pipe blocks, address-translation L2 blocks, L2 TLB performance counters, and VM L2 protection-fault reporting.

The definitions are compile-time data only. They let driver code use symbolic field names with macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, and SOC15 register accessors instead of hard-coding bit positions. The matching offsets live in `gc_9_4_2_offset.h`; this file supplies the bit-level layout for those registers.

The range begins at the tail of the `SQ_IMG_RSRC_WORD1` descriptor group, covers `SQ_IMG_RSRC_WORD2..7`, sampler descriptors, flat scratch and M0 index words, SQC UTCL1 controls, then moves through address blocks `gc_tcdec`, `gc_tcpdec`, `gc_tpdec`, `gc_utcl2_atcl2dec`, `gc_utcl2_atcl2pfcntldec`, `gc_utcl2_atcl2pfcntrdec`, `gc_utcl2_l2tlbdec`, `gc_utcl2_l2tlbpldec`, `gc_utcl2_l2tlbprdec`, and ends inside `gc_utcl2_vml2pfdec` after `VM_L2_MM_GROUP_RT_CLASSES`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or global variables in this range. The API surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit of a field.
- `REGISTER__FIELD_MASK` gives the unshifted 32-bit field mask.
- Full-word fields such as `SQ_IMG_RSRC_WORD7__META_DATA_ADDRESS_MASK`, `TCA_BURST_MASK__ADDR_MASK_MASK`, `TA_SCRATCH__SCRATCH_MASK`, `ATC_L2_CACHE_DATA1__VIRTUAL_PAGE_ADDRESS_LOW_MASK`, `ATC_L2_CACHE_DATA2__PHYSICAL_PAGE_ADDRESS_MASK`, and `VM_L2_PROTECTION_FAULT_ADDR_LO32__LOGICAL_PAGE_ADDR_LO32_MASK` represent entire register words.
- Address block comments identify hardware decode domains, not C namespaces.

Important macro families in this chunk include:

- Shader image resource descriptors: `SQ_IMG_RSRC_WORD2..7` fields describe image width, height, depth, pitch, destination component selects, base and last mip levels, swizzle mode, resource type, base array, array pitch, metadata address fragments, metadata layout/alignment flags, max mip, compression enablement, color transform, and lost color/alpha bits.
- Shader sampler descriptors: `SQ_IMG_SAMP_WORD0..3` cover clamp modes, anisotropy ratio/threshold/bias/override, depth compare function, unnormalized coordinates, degamma controls, coordinate truncation, filter modes, LOD min/max/bias, mip/filter selectors, PRT zero blending, border color pointer, and border color type.
- Scratch and indexing descriptors: `SQ_FLAT_SCRATCH_WORD0/1` describe flat scratch size and offset, while `SQ_M0_GPR_IDX_WORD` describes the M0-relative GPR index and source/destination relative-addressing flags.
- SQC UTCL1 controls and status: `SQC_ICACHE_UTCL1_CNTL1/2`, `SQC_DCACHE_UTCL1_CNTL1/2`, `SQC_ICACHE_UTCL1_STATUS`, and `SQC_DCACHE_UTCL1_STATUS` define GPUVM page-size defaults, permission and response modes, client ID, VMID invalidation fields, force-miss and in-order diagnostics, FIFO/cache depth reductions, bypass and snoop controls, performance event selection, and fault/retry/PRT status.
- `gc_tcdec` texture cache fabric controls: `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CHAN_STEER_0..5`, `TCP_ADDR_CONFIG`, `TCP_EDC_CNT`, `TCP_EDC_CNT_NEW`, `TC_CFG_L1/L2_*_POLICY*`, `TC_CFG_*_VOLATILE`, `TCI_*`, `TCC_*`, `TCA_*`, and `TCX_*` cover cache invalidation/status, channel steering, address swizzle configuration, load/store/atomic policy tables, volatile hints, clock-gating/chicken bits, FIFO/cache depth, writeback/invalidate behavior, SRAM EDC counters, redundancy/disable controls, soft reset, burst controls, and DSM/error-injection controls.
- `gc_tcpdec` TCP watch and UTCL1 controls: `TCP_WATCH0..3_ADDR_H/L/CNTL` provide address-watchpoint high/low address, mask, VMID, ATC, mode, and valid fields. `TCP_GATCL1_CNTL`, `TCP_UTCL1_CNTL1/2`, `TCP_UTCL1_STATUS`, `TCP_DSM_CNTL*`, and `TCP_PERFCOUNTER_FILTER*` define TCP-side translation-cache invalidation, response/fault modes, performance filters, and memory error-injection controls.
- `gc_tpdec` texture pipe controls: `TD_STATUS`, `TD_EDC_CNT`, `TD_DSM_CNTL*`, `TD_SCRATCH`, `TA_CNTL`, `TA_CNTL_AUX`, `TA_FEATURE_CNTL`, `TA_STATUS`, `TA_SCRATCH`, `TA_DSM_CNTL*`, and `TA_EDC_CNT` describe texture data/address FIFO state, EDC counters, determinism disables, filter and anisotropy behavior, LOD and cube-map controls, texture atomic/coalescing features, busy bits, scratch words, and DSM/error-injection controls.
- `gc_utcl2_atcl2dec` address translation cache L2 controls: `ATC_L2_CNTL*`, `ATC_L2_CACHE_DATA0..3`, `ATC_L2_STATUS*`, `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, `ATC_L2_CGTT_CLK_CTRL`, `ATC_L2_CACHE_{4K,32K,2M}_DSM_INDEX`, `ATC_L2_CACHE_{4K,32K,2M}_DSM_CNTL`, and `ATC_L2_MM_GROUP_RT_CLASSES` describe translation request crediting, host/device request modes, cache invalidation/update modes, bank/way selection, cached virtual/physical page data, uncorrectable-error status, clock and memory light-sleep controls, per-page-size DSM indexing, SED/DED counters, and RT class grouping.
- `gc_utcl2_atcl2pfcntldec` and `gc_utcl2_atcl2pfcntrdec` performance counters: `ATC_L2_PERFCOUNTER0_CFG`, `ATC_L2_PERFCOUNTER1_CFG`, `ATC_L2_PERFCOUNTER_RSLT_CNTL`, `ATC_L2_PERFCOUNTER_LO`, and `ATC_L2_PERFCOUNTER_HI` select ATC L2 events, event ranges, modes, enables, clears, trigger fields, saturation behavior, result low/high words, and compare values.
- `gc_utcl2_l2tlb*` TLB support: `L2TLB_TLB0_STATUS`, `UTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*`, `UTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_*`, `L2TLB_PERFCOUNTER*_CFG`, `L2TLB_PERFCOUNTER_RSLT_CNTL`, `L2TLB_PERFCOUNTER_LO`, and `L2TLB_PERFCOUNTER_HI` describe TLB busy state, GPUVA/VMID translation-assist request and response fields, and L2TLB performance measurement.
- `gc_utcl2_vml2pfdec` VM L2 controls: `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_STATUS`, dummy-page-fault controls and addresses, `VM_L2_PROTECTION_FAULT_CNTL*`, `VM_L2_PROTECTION_FAULT_STATUS`, protection-fault address/default-address registers, identity aperture low/high registers, identity physical offset registers, `VM_L2_CNTL4`, and `VM_L2_MM_GROUP_RT_CLASSES` define page-table cache mode, PDE/PTE force-miss controls, retry/fault behavior, page migration and PRT controls, fault identity, busy bits, and identity mapping apertures.

## Control Flow

This header chunk has no runtime control flow. Including code obtains constants that are folded by the C preprocessor and compiler into register read/modify/write expressions, table initializers, and field extraction code.

The typical runtime pattern in consumers is:

1. Include `gc_9_4_2_offset.h` and `gc_9_4_2_sh_mask.h` for the target ASIC.
2. Select an offset with `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, or generated `reg*` names.
3. Build or decode a field with `REG_SET_FIELD`, `REG_GET_FIELD`, or `SOC15_REG_FIELD`.
4. Read or write the hardware register with AMDGPU SOC15 accessors.

The main direct consumers in this tree are `amdgpu/gfx_v9_4_2.c` and `amdgpu/amdgpu_amdkfd_aldebaran.c`. `gfx_v9_4_2.c` includes this header for Aldebaran golden settings, RAS/EDC field tables, UTC EDC counter walking, and register programming. `amdgpu_amdkfd_aldebaran.c` includes it for KFD debug/trap and TCP address-watch programming. Other GC and MMHUB files show similar field patterns for sibling hardware generations, but they must not be treated as layout-compatible without checking the exact ASIC header.

## State And Persistence Behavior

The macros themselves are stateless and do not allocate or persist memory. They describe state held elsewhere:

- Descriptor state: `SQ_IMG_RSRC_WORD*`, `SQ_IMG_SAMP_WORD*`, `SQ_FLAT_SCRATCH_WORD*`, and `SQ_M0_GPR_IDX_WORD` describe GPU-visible descriptor words consumed by shader execution. The descriptor values persist in command buffers, kernel/user queues, or memory objects managed by higher layers, not in this header.
- Persistent hardware configuration: cache policy registers, channel steering, `TCP_UTCL1_CNTL*`, `SQC_*_UTCL1_CNTL*`, `TCI_CNTL_*`, `TCC_CTRL*`, `TCA_CTRL`, `TA_CNTL*`, `ATC_L2_CNTL*`, `VM_L2_CNTL*`, and protection fault controls remain active until reset, power transition, resume reprogramming, or another register write changes them.
- Volatile status: `TCP_STATUS`, SQC/TCP UTCL1 status registers, `TCI_STATUS`, `TD_STATUS`, `TA_STATUS`, `ATC_L2_STATUS*`, `L2TLB_TLB0_STATUS`, and `VM_L2_STATUS` expose current hardware condition and should be treated as observation points.
- Error counters and fault latches: `TCP_EDC_CNT_NEW`, `TCI_EDC_CNT`, `TCC_EDC_CNT*`, `TCA_EDC_CNT`, `TCX_EDC_CNT*`, `TD_EDC_CNT`, `TA_EDC_CNT`, ATC L2 DSM counter fields, and `VM_L2_PROTECTION_FAULT_STATUS` represent hardware error accounting or fault capture. Consumer code may clear counters after reading; `gfx_v9_4_2_query_sram_edc_count()` explicitly reads EDC registers and writes zero to clear them.
- Debug/watch state: `TCP_WATCH0..3_*` registers persist configured watchpoints for KFD debug until overwritten or cleared by the debug path.
- DSM/error-injection state: many `*_DSM_CNTL*` and `*_CACHE_*_DSM_CNTL` fields intentionally inject, delay, or count SRAM errors. These are validation features and should not be enabled during normal operation.

No disk state, kernel heap lifetime, locks, or reference counts are implemented in this file. Synchronization and lifetime rules belong to consuming code. For example, `gfx_v9_4_2_query_sram_edc_count()` uses `grbm_idx_mutex` while selecting instances, but this header only supplies the masks used by its field helpers.

## Dependencies

This chunk depends on the generated GC 9.4.2 register family and AMDGPU SOC15 helper conventions:

- `gc_9_4_2_offset.h` supplies the matching `reg*` offsets for the field names defined here.
- AMDGPU register helpers in the SOC15 stack provide `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `SOC15_REG_OFFSET`, `WREG32*`, and `RREG32*` usage.
- `gfx_v9_4_2.c` relies on this header for golden setting names such as `regTCP_CHAN_STEER_0..5`, `regTA_CNTL_AUX`, `regTCP_UTCL1_CNTL1`, and `regTCI_CNTL_3`, and for RAS field extraction from EDC counter registers covered by this chunk.
- `amdgpu_amdkfd_aldebaran.c` relies on `TCP_WATCH0_CNTL` field masks for address watchpoint mode, mask, and valid bits, plus TCP watch register offsets from the matching offset header.
- RAS code depends on `SOC15_REG_FIELD()` expansion for `TCP_EDC_CNT_NEW`, `TCI_EDC_CNT`, `TCC_EDC_CNT*`, `TCA_EDC_CNT`, `TCX_EDC_CNT*`, `TD_EDC_CNT`, `TA_EDC_CNT`, and ATC L2 DSM counters.

The definitions are hardware-contract data. They must match the GC 9.4.2 register specification and sibling offset definitions. Similar names across GC 9.x, GC 10.x, GC 11.x, GC 12.x, and MMHUB headers are not interchangeable because field widths and semantics can differ.

## Integration Points

Primary integration points include:

- Aldebaran graphics initialization in `gfx_v9_4_2.c`: golden setting arrays program TCP channel steering, texture address control, TCP UTCL1 behavior, and TCI control fields. Incorrect masks here can misroute cache channels or apply invalid tuning values during GPU bring-up.
- KFD debugging in `amdgpu_amdkfd_aldebaran.c`: `kgd_gfx_aldebaran_set_address_watch()` builds `TCP_WATCH0_CNTL` using the `MODE`, `MASK`, and `VALID` fields, writes `TCP_WATCH*_ADDR_H/L`, and returns the control word for the caller to program. The chunk's watch register fields are therefore part of user-visible GPU debugging behavior.
- SRAM EDC/RAS in `gfx_v9_4_2.c`: RAS tables read TCP, TCI, TCC, TCA, TCX, TD, and TA EDC counters using fields defined in this range. Query paths aggregate SEC/DED counts and clear counters after reads.
- UTC EDC/RAS in `gfx_v9_4_2.c`: `gfx_v9_4_2_utc_blocks` maps ATC L2 cache page-size DSM index/control registers to bank/way/memory iteration logic and uses the `SEC_COUNT`, `DED_COUNT`, and `WRITE_COUNTERS` fields for SED/DED accounting.
- Shader descriptor construction and decoding: while this source tree may not directly build all `SQ_IMG_RSRC_*` and `SQ_IMG_SAMP_*` fields in the GC 9.4.2 driver file, those macros represent the ABI between shader-visible descriptor words and the hardware texture/image/sampler units.
- VM fault handling and diagnostics: `VM_L2_*` fields align with the GFXHUB/MMHUB-style fault reporting model used elsewhere in AMDGPU. The status and address fields identify client ID, VMID, read/write/atomic nature, permission/mapping errors, VF/VFID, and logical/default physical fault addresses.
- Performance tooling: ATC L2 and L2TLB performance counter fields expose event selection, trigger, clear, enable, result, and compare layouts for low-level performance or debug paths.

## Risks

- A wrong mask or shift silently targets the wrong bits. Since these macros are normally used inside helper macros, many mistakes compile cleanly and only appear as bad hardware behavior.
- Cache and translation controls are high impact. Incorrect `SQC_*_UTCL1`, `TCP_UTCL1_*`, `ATC_L2_*`, or `VM_L2_*` fields can break GPUVM translation, fault handling, invalidation ordering, or cache coherency.
- Golden settings rely on exact field layouts. Bad `TCP_CHAN_STEER_*`, `TA_CNTL_AUX`, `TCP_UTCL1_CNTL1`, or `TCI_CNTL_3` definitions can regress boot, multi-die routing, texture determinism, or cache behavior on Aldebaran.
- Address watchpoint fields are user-debug visible through KFD. Incorrect `TCP_WATCH0_CNTL` mask, VMID, mode, ATC, or valid bits can miss debug watchpoints, trigger on the wrong address range, or leave a watchpoint active unexpectedly.
- Descriptor fields are ABI-like. Errors in `SQ_IMG_RSRC_WORD*` or `SQ_IMG_SAMP_WORD*` definitions can corrupt image dimensions, mip selection, swizzle mode, compression metadata, sampler filtering, LOD, border color, or PRT behavior.
- DSM and error-injection fields are dangerous outside validation. Accidental writes to `*_ENABLE_ERROR_INJECT`, `*_IRRITATOR_*`, `WRITE_COUNTERS`, or delay-selection fields can inject faults, disturb counters, or mask real hardware errors.
- EDC counter fields may be read-clear or explicitly cleared by consumers. Adding diagnostics around them without preserving existing read/clear order can lose error evidence or double count errors.
- Cross-generation copy/paste is unsafe. GC 9.4.2 names resemble GC 9.4.x, MMHUB, and later GCVM names, but offsets, prefixes, and fields differ enough that a wrong include can produce valid C and invalid register programming.
- Generated register headers should usually be regenerated from AMD register metadata. Manual edits are hard to audit and risk desynchronizing masks from offsets and defaults.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU configurations that compile `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`, proving all `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD` references still resolve.
- Static consistency checks that every register name referenced by this chunk has a matching offset in `gc_9_4_2_offset.h` and that field masks do not overlap unexpectedly within a register unless the hardware spec requires aliases.
- Aldebaran boot and graphics initialization tests that apply golden settings without invalid register access warnings, especially `TCP_CHAN_STEER_0..5`, `TA_CNTL_AUX`, `TCP_UTCL1_CNTL1`, and `TCI_CNTL_3`.
- KFD debug watchpoint tests that set, trigger, and clear `TCP_WATCH0..3` entries across different masks and modes, verifying the address-low alignment shift and valid bit behavior.
- RAS/EDC tests that inject or simulate SRAM errors and confirm `TCP_EDC_CNT_NEW`, `TCI_EDC_CNT`, `TCC_EDC_CNT*`, `TCA_EDC_CNT`, `TCX_EDC_CNT*`, `TD_EDC_CNT`, `TA_EDC_CNT`, and ATC L2 DSM counters report SEC/DED counts in the expected fields and clear correctly after query.
- GPUVM fault tests that exercise invalid mappings, permission faults, retry/no-retry faults, dummy-page fault behavior, PRT/page migration behavior, and protection-fault status/address capture.
- Cache invalidation and coherency stress tests that exercise SQC/TCP UTCL1 invalidation, ATC L2 invalidation/update modes, TCC writeback/invalidate, and L2TLB translation assist under memory pressure.
- Graphics and compute workloads that stress image resources, samplers, compressed metadata, mip/array selection, anisotropic filtering, texture atomics, and tiled/virtual memory paths.
- Suspend/resume and GPU reset tests to verify persistent hardware configuration covered by this chunk is restored or reinitialized by the owning driver paths.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.c

### Purpose
`intel_guc_ads.c` constructs and maintains the GuC Additional Data Struct blob: scheduling policies, GT system info, engine usage records, MMIO save/restore regsets, golden contexts, workaround KLVs, capture lists, and private firmware data.

### Important APIs, Types, And Functions
Exports include `intel_guc_ads_create()`, `intel_guc_ads_destroy()`, `intel_guc_ads_init_late()`, `intel_guc_ads_reset()`, `intel_guc_ads_print_policy_info()`, `intel_guc_global_policies_update()`, `intel_guc_engine_usage_offset()`, and `intel_guc_engine_usage_record_map()`. Important internals include `struct __guc_ads_blob`, offset/size calculators, `guc_policies_init()`, `guc_mapping_table_init()`, `guc_mmio_reg_state_create/init()`, `guc_prep_golden_context()`, `guc_init_golden_context()`, `guc_capture_prep_lists()`, `guc_waklv_init()`, and `__guc_ads_init()`.

### Control Flow
Creation first builds temporary sorted per-engine MMIO regsets from engine registers, workaround registers, whitelist slots, MOCS, and perf counters; precomputes golden-context, capture-list, and workaround-KLV sizes; allocates a GuC VMA of the combined page-aligned blob; maps it; then initializes ADS contents. Initialization writes policies, engine masks, system info, doorbell count, golden-context pointers, engine mapping table, capture-list pointers, MMIO save/restore pointers, workaround KLV address/size, private data pointer, and flushes the map. Late init copies recorded engine default states into golden-context storage once defaults exist. Reset rebuilds ADS and clears private data.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state includes `guc->ads_vma`, `ads_map`, computed sizes, `ads_regset_count`, and temporary `ads_regset` storage. Dependencies include GuC firmware interface structs, GuC capture APIs, engine workaround/whitelist data, MCR steering, shmem golden-context reads, iosys-map, GEM lmem/shmem allocation, and platform feature masks. Integration points are GuC firmware boot params, submission watchdog reset recovery, global scheduling policy updates, engine usage accounting, capture/coredump setup, and workaround delivery. Risks include size recomputation mismatch, sorted/deduplicated register list errors, MCR steering assumptions, null capture-list fallback, page-alignment mistakes, stale golden contexts before late init, and firmware-version/platform gating for WAKLVs. Test signals include GuC boot success with ADS pointer, policy update action success, engine usage mapping correctness, capture-list population, golden-context availability after defaults, and reset-time ADS reinitialization.

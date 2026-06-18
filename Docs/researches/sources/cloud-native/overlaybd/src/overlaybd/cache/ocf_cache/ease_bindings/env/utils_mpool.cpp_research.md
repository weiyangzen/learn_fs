<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.cpp

Purpose: Implements OCF memory-pool allocation buckets.

APIs and control flow: `env_mpool_create` allocates an `env_mpool`, creates per-power-of-two allocators for element counts up to `mpool_max`, and records header/element sizes. `env_mpool_get_allocator` rounds requested count up to a power-of-two bucket. `env_mpool_new_f` allocates from that bucket or falls back to zero allocation if allowed. `env_mpool_del` frees via allocator or fallback free.

State and persistence: Owns allocator array and allocation size policy; no disk state.

Dependencies and integration: Used by OCF environment allocator paths.

Risks and test signals: `name_perfix` typo is API-compatible but confusing. Tests should cover count 0, bucket boundaries, fallback, and destroy with outstanding allocations.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.cpp -->

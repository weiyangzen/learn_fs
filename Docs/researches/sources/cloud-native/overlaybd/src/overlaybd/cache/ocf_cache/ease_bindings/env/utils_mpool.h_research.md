<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.h

Purpose: Declares OCF memory-pool API.

APIs and types: Defines bucket enum `env_mpool_1` through `env_mpool_128`, opaque `env_mpool`, and functions to create, destroy, allocate, allocate with flags, and delete items.

State and persistence: Runtime allocator state is private to the implementation.

Dependencies and integration: Included by `ocf_env.h` and OCF code that requests variable-size arrays from pools.

Risks and test signals: Caller must pass the same count to delete that was used for allocation. Boundary tests around powers of two validate bucket selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.h -->

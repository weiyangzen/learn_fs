# sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy-internal.h

## Purpose
`dm-cache-policy-internal.h` provides inline wrappers and helper allocation utilities for DM cache policy users and policy implementations. It normalizes optional policy callbacks and exposes policy creation/destruction and identity accessors used by the cache target and metadata code.

## Important APIs, Types, and Functions
Wrappers include `policy_lookup()`, `policy_lookup_with_work()`, `policy_get_background_work()`, `policy_complete_background_work()`, `policy_set_dirty()`, `policy_clear_dirty()`, `policy_load_mapping()`, `policy_invalidate_mapping()`, `policy_get_hint()`, `policy_residency()`, `policy_tick()`, `policy_emit_config_values()`, `policy_set_config_value()`, and `policy_allow_migrations()`. Utility helpers include `bitset_size_in_bytes()`, `alloc_bitset()`, `clear_bitset()`, and `free_bitset()`. External declarations expose `dm_cache_policy_create()`, `dm_cache_policy_destroy()`, name/version getters, and hint-size getter.

## Control Flow
The wrappers mostly dispatch directly through function pointers in `struct dm_cache_policy`. Optional hooks have defaults: `lookup_with_work` falls back to `lookup`, `get_hint` returns zero when absent, `tick` is skipped when absent, config emission reports zero values when absent, and unsupported config set returns `-EINVAL`.

## State and Persistence
No persistent state is owned by the header. The bitset helpers allocate volatile vmalloc-backed bitsets used by policies such as SMQ for per-period hit tracking. Identity getters are used by metadata to decide whether persisted policy hints are compatible.

## Dependencies and Integration Points
It includes `dm-cache-policy.h` and Linux vmalloc support. The DM cache target uses these wrappers instead of reaching into policy function pointers directly, while policy implementations use the bitset helpers.

## Risks and Edge Cases
The fallback in `policy_lookup_with_work()` passes `NULL` for `background_queued`; policy implementations must tolerate that if they are used through the fallback. `policy_allow_migrations()` is not optional here, so every registered policy must provide it. `DMEMIT` in config emission assumes the caller has provided the usual `result`, `maxlen`, and size pointer context.

## Test Signals
Tests should exercise policies with and without optional callbacks, config status output for policies with no config, hint defaulting to zero, and bitset allocation/clear/free for cache sizes crossing word boundaries.

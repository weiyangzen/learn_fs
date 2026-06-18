# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ptrn.c

## Purpose
`dr_ptrn.c` manages the modify-header pattern cache used on devices that support the pattern/argument modify-header model. Instead of posting a full modify-header action blob for every rule, it stores reusable pattern objects in dedicated ICM memory and lets per-rule arguments supply the variable inline data.

## Important APIs, Types, And Functions
The file defines `struct mlx5dr_ptrn_mgr`, which owns a domain pointer, a `DR_ICM_TYPE_MODIFY_HDR_PTRN` ICM pool, a cached pattern list, and `modify_hdr_mutex`. Public APIs are `mlx5dr_ptrn_mgr_create()`, `mlx5dr_ptrn_mgr_destroy()`, `mlx5dr_ptrn_cache_get_pattern()`, and `mlx5dr_ptrn_cache_put_pattern()`. Internal helpers compare patterns (`dr_ptrn_compare_modify_hdr()`), find an existing list entry (`dr_ptrn_find_cached_pattern()`), allocate a new pattern (`dr_ptrn_alloc_pattern()`), and free one (`dr_ptrn_free_pattern()`).

## Control Flow
`mlx5dr_ptrn_cache_get_pattern()` locks the cache, searches for an equivalent pattern, and either increments the cached object refcount or allocates a new ICM chunk and object. New patterns are masked before posting: for SET, ADD, and INSERT_INLINE actions, inline data is cleared because hardware later ORs pattern and argument data. The pattern is then posted with `mlx5dr_send_postsend_pattern()`. If posting fails, the refcount is dropped and the pattern is freed. Cache hits are moved to the list head to bias lookup toward recently used patterns.

## State And Persistence
Patterns persist as long as their `refcount` remains nonzero. Each `struct mlx5dr_ptrn_obj` stores a copy of hardware action data, the ICM chunk, action count, hardware pattern index, list node, and refcount. The index is computed from the chunk ICM address relative to `hdr_modify_pattern_icm_addr` in action-cache-line units. The cache list is in-memory; the pattern bytes are persisted to device ICM through the send path.

## Dependencies And Integration Points
This code depends on STE v1 action layouts (`mlx5_ifc_dr_ste_v1.h`) to read `action_id`, the domain capability helper `mlx5dr_domain_is_support_ptrn_arg()`, ICM chunk allocation, and the send-ring pattern post API. It is used by the modify-header action path through the STE context when the domain supports pattern arguments. The manager is created and destroyed with the domain.

## Risks
Comparison deliberately treats COPY actions as full 64-bit values but compares only the low 32 bits for other action IDs. That matches the pattern/argument model but is subtle and can incorrectly deduplicate if a new action type carries meaningful high bits. The destroy path warns if the list is non-empty but still frees listed objects without freeing their chunks through `dr_ptrn_free_pattern()`; this assumes normal users returned all refs before manager destruction. Mutex coverage is essential because pattern refcounts and list order are shared domain state.

## Test Signals
Exercise duplicate patterns with different inline data, COPY actions that differ in high bits, get/put refcount lifetimes, allocation failure, postsend failure cleanup, and manager destruction after all patterns are released. Hardware-level signals are correct pattern index calculation and successful modify-header rules using shared pattern plus per-rule arguments.

# `sources/distributed-fs/ceph-client/mm/hugetlb_internal.h`

## Purpose
`hugetlb_internal.h` centralizes private HugeTLB declarations and small helpers shared by the HugeTLB core, sysfs, sysctl, and CMA-adjacent code. It avoids exporting these details through public headers while keeping hstate node iteration, gigantic-page gating, pool mutation, demotion, resize, and init hooks available across HugeTLB translation units.

## Important APIs, Types, And Functions
- `hstate_is_gigantic_no_runtime()` returns true for gigantic hstates when runtime gigantic-page support is unavailable.
- Node selection helpers: `next_node_allowed()`, `get_valid_node_allowed()`, `hstate_next_node_to_alloc()`, and `hstate_next_node_to_free()`.
- Iteration macros: `for_each_node_mask_to_alloc()` and `for_each_node_mask_to_free()` implement bounded round-robin traversal over allowed nodes.
- Core declarations exported from `hugetlb.c`: `remove_hugetlb_folio()`, `add_hugetlb_folio()`, `init_new_hugetlb_folio()`, `prep_and_add_allocated_folios()`, `demote_pool_huge_page()`, and `__nr_hugepages_store_common()`.
- Init declarations: `hugetlb_sysfs_init()` and conditional `hugetlb_sysctl_init()`.

## Control Flow
The inline node helpers normalize potentially stale `next_nid_to_alloc` or `next_nid_to_free` values against a caller-provided nodemask. Allocation returns the current valid node and advances the stored next-node pointer. Free selection uses `h->next_nid_to_free` similarly. The macros wrap these helpers with a `nodes_weight()` countdown so callers visit each allowed node at most once per operation.

`hstate_is_gigantic_no_runtime()` is used by sysfs/sysctl and core resize/free paths to reject operations that cannot work on gigantic pages without runtime support while still allowing boot-time accounting and reporting.

## State And Persistence Behavior
The header mutates hstate round-robin cursors via inline helpers: allocation updates an integer passed by pointer and free updates `h->next_nid_to_free`. It defines no independent persistent state.

## Dependencies And Integration Points
It depends on `linux/hugetlb.h` for `struct hstate` and hstate helpers, and `linux/hugetlb_cgroup.h` for cgroup types used by HugeTLB internals. It is included by `hugetlb.c`, `hugetlb_sysfs.c`, and `hugetlb_sysctl.c`.

## Risks
- The node iteration helpers assume non-empty allowed masks; they use `VM_BUG_ON(nid >= MAX_NUMNODES)` after `next_node_in()`. Callers must validate masks.
- The allocation/free macros evaluate helper calls inside loop conditions; callers must pass stable nodemask pointers and writable next-node storage.
- Changing `hstate_is_gigantic_no_runtime()` semantics affects sysfs/sysctl resize rejection, demotion, and freeing behavior.
- Declarations here are private but cross-file; prototype drift from `hugetlb.c` will produce build failures or worse if types remain compatible but semantics change.

## Test Signals
- Runtime resize and demotion tests with restricted nodemasks should show round-robin distribution and no out-of-mask allocation/free.
- Build configurations with and without `CONFIG_SYSCTL` should verify `hugetlb_sysctl_init()` resolves to a real function or inline no-op.
- Gigantic hstate tests on architectures with and without runtime support should verify resize/demotion rejection paths.

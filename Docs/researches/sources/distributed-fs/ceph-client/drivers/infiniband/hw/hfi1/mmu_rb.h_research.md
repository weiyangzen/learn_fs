# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mmu_rb.h

## Purpose
`mmu_rb.h` declares the HFI1 MMU notifier interval-tree abstraction. It defines the node, callback contract, handler state, and public functions used by HFI1 memory-registration code to track process virtual address ranges.

## Important APIs, types, and functions
- `struct mmu_rb_node` contains the virtual address range, interval-tree node, owning handler, LRU/delete list linkage, and kref.
- `struct mmu_rb_ops` supplies optional `filter()`, mandatory-style `remove()`, and optional eviction policy callback. The comment states `filter` and `evict` must not sleep; only `remove` may sleep.
- `struct mmu_rb_handler` stores the MMU notifier, spinlock-protected cached rb root, callback context, LRU and delete lists, work item, workqueue, and aligned allocation pointer.
- Public APIs are `hfi1_mmu_rb_register()`, `hfi1_mmu_rb_unregister()`, `hfi1_mmu_rb_insert()`, `hfi1_mmu_rb_release()`, `hfi1_mmu_rb_evict()`, and `hfi1_mmu_rb_get_first()`.

## Control flow
The header establishes the lifecycle: register a handler for the current `mm`, insert initialized nodes, search or evict them under the handler rules, release krefs through `hfi1_mmu_rb_release()`, and unregister to remove all remaining ranges and the notifier.

## State and persistence
All declared state is runtime-only and scoped to one `mmu_rb_handler`. Nodes are caller-allocated objects whose final cleanup is delegated to `ops->remove()`.

## Dependencies and integration points
The header includes `hfi.h`, which provides kernel and HFI1 context. The implementation integrates with Linux MMU notifiers, rb trees, lists, krefs, and HFI1 memory-cache users.

## Risks
- Callers must obey locking comments: `hfi1_mmu_rb_get_first()` requires the handler lock, while `hfi1_mmu_rb_release()` must not be called while already holding it.
- Callback sleepability requirements are part of the ABI and are easy to violate when adding new memory-cache users.
- Node address/length fields must be initialized before insertion and remain stable while in the tree.

## Test signals
- Compile all users after callback signature changes.
- Lockdep tests around search, release, notifier invalidation, and unregister.
- Fault-injection tests for registration allocation failure and MMU notifier registration failure.

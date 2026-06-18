<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_types.h

## Purpose

`xe_pt_types.h` defines page-table-related cache levels, page-table metadata, encoding operations, and staged update data structures shared between VM and page-table implementation code.

## Important APIs and Types

`enum xe_cache_level` names cache choices including uncached, write-through, write-back, and compression variants. `XE_VM_MAX_LEVEL` is 4. `struct xe_pt` embeds generic walker state, the backing BO, level, live-entry count, rebind and compact flags, and optional debug VA. `struct xe_pt_ops` abstracts PTE/PDE encoding for BOs, VMAs, raw addresses, and page-table BOs. `struct xe_vm_pgtable_update` describes one page-table BO update. `struct xe_vm_pgtable_update_op` groups updates for one VMA operation. `struct xe_vm_pgtable_update_ops` tracks a batch across operations, deferred destruction, update queue, page reclaim list, affected range, current op, and dependency/invalidation flags.

## Control Flow and State

These structures carry the persistent VM page-table tree and the temporary staging state used during bind/unbind. `children` represents committed CPU tree state, while `staging` represents prepared but not fully committed changes.

## Dependencies and Integration Points

It includes page reclaim and page-table walker definitions and is consumed by `xe_pt.c`, VM code, migration, and architecture-specific PTE encoding.

## Risks and Test Signals

The update arrays are sized around `XE_VM_MAX_LEVEL * 2 + 1`; changes to VM levels require auditing staging limits. Tests should verify cache-level-to-PAT mappings, compact flag behavior, deferred destruction, and batch state reset between operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_types.h -->

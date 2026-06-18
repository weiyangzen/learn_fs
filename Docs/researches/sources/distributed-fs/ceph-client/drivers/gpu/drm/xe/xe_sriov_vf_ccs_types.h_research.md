<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs_types.h

## Purpose

`xe_sriov_vf_ccs_types.h` defines the persistent data structures for VF CCS migration contexts.

## Important APIs, Types, and Functions

`enum xe_sriov_vf_ccs_rw_ctxs` defines read/save and write/restore contexts plus count. `for_each_ccs_rw_ctx()` iterates both. `struct xe_sriov_vf_ccs_ctx` stores context ID, migration exec queue, and CCS BB pool. `struct xe_sriov_vf_ccs` stores the context array and initialization flag.

## Control Flow

Initialization fills each context and then sets `initialized`. Attach, detach, rebase, register, and print paths iterate contexts using the macro.

## State and Persistence Behavior

The structures persist in `xe->sriov.vf.ccs` for the VF lifetime and are cleaned via devm actions from initialization.

## Dependencies and Integration Points

The header uses Linux types and forward-declared struct names through included users. It is embedded by VF types and consumed by CCS implementation/header.

## Risks and Test Signals

The enum ordering is semantically tied to GuC save versus restore types and to BO `bb_ccs[]` indexing. Tests should verify both contexts are initialized and mapped to the correct GuC context type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs_types.h -->

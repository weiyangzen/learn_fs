<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.h

## Purpose
`xe_ggtt.h` declares the public Global Graphics Translation Table API used by BO, display, GuC, migration, debug, and SR-IOV code.

## Important APIs, types, and functions
The header declares allocation, early and regular init, KUnit init, node shift, start/size queries, node insertion and transform insertion, node removal and PTE-size query, BO map/insert/remove helpers, largest-hole query, dump/print helpers, SR-IOV assignment/save/load under `CONFIG_PCI_IOV`, lockdep helper, PTE flag encoding/read, and node address/size accessors.

## Control flow and integration points
There is no executable control flow except a no-op inline `xe_ggtt_might_lock()` when lockdep is disabled. The API integrates tile initialization, BO placement, display GGTT transforms, VF migration, and debugfs-like reporting.

## State and persistence behavior
The header owns no state. The implementation manages per-tile GGTTs, nodes, BO node pointers, scratch mappings, and PTE contents.

## Dependencies, risks, and test signals
Dependencies include GGTT types, DRM printer/exec declarations, Xe BO/tile types, and optional PCI IOV. Risks include callers failing to remove nodes, using node addresses after VF shifts without `xe_ggtt_node_addr()`, and SR-IOV APIs missing in non-IOV builds. Test signals are build coverage across CONFIG_PCI_IOV/LOCKDEP, BO GGTT mapping tests, display transform users, and VF migration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.h -->

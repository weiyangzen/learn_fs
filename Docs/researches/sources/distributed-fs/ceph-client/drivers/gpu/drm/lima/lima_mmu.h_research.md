<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.h

## Purpose
Declares the Lima MMU lifecycle, TLB, VM switch, and page-fault resume APIs.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and `struct lima_vm`; exposes init/fini/resume/suspend, `lima_mmu_flush_tlb()`, `lima_mmu_switch_vm()`, and `lima_mmu_page_fault_resume()`.

## Control flow
No executable flow exists here.

## State and persistence
No state is stored in the header.

## Dependencies and integration points
Used by device IP descriptors, scheduler pipe task execution, and MMU fault recovery.

## Risks
Signature changes affect GP/PP scheduling and device lifecycle.

## Test signals
Build coverage plus VM switch and fault tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.h -->

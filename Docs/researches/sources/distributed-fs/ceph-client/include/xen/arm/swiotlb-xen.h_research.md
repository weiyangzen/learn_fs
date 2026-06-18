<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/swiotlb-xen.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/swiotlb-xen.h

## Purpose
This header provides ARM Xen detection logic for enabling Xen SWIOTLB DMA operations.

## Important APIs, Types, And Functions
- `xen_swiotlb_detect()` returns false outside Xen, true for direct-mapped Xen domains, true for legacy initial-domain cases without explicit not-direct-mapped feature, and false otherwise.

## Control Flow
DMA setup code calls `xen_swiotlb_detect()` during device initialization. The function checks `xen_domain()`, `xen_feature(XENFEAT_direct_mapped)`, `xen_feature(XENFEAT_not_direct_mapped)`, and `xen_initial_domain()`.

## State And Persistence
No state is stored. It reads Xen feature state populated elsewhere.

## Dependencies And Integration Points
It depends on Xen feature setup and Xen domain detection. It is used by ARM Xen DMA ops selection.

## Risks And Edge Cases
Feature availability differs across Xen versions; the legacy initial-domain fallback preserves behavior when explicit feature bits are absent. Incorrect detection can either miss necessary bounce buffering or impose unnecessary SWIOTLB overhead.

## Test Signals
Signals include expected true/false results for non-Xen, direct-mapped, not-direct-mapped, and legacy Dom0 configurations, followed by correct DMA behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/swiotlb-xen.h -->

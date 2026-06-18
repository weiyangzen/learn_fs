<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/features.h -->
# sources/distributed-fs/ceph-client/include/xen/features.h

## Purpose
This header exposes Xen feature discovery state and a simple feature-test helper.

## Important APIs, Types, And Functions
- `xen_setup_features()` populates feature bits from Xen.
- `xen_features` stores `XENFEAT_NR_SUBMAPS * 32` feature bytes.
- `xen_feature(int flag)` returns the requested feature byte.

## Control Flow
Boot/setup code calls `xen_setup_features()`, and later code branches on `xen_feature(XENFEAT_*)` for mapping, DMA, event, and other behavior.

## State And Persistence
`xen_features` is persistent global feature state for the running domain.

## Dependencies And Integration Points
It depends on Xen public feature definitions. Consumers include SWIOTLB detection, PV/HVM feature gating, event channel setup, and memory mapping paths.

## Risks And Edge Cases
Callers must not query out-of-range flags. Feature state must be initialized before use or defaults can select the wrong compatibility path.

## Test Signals
Signals include populated feature arrays after Xen setup, correct branch decisions for direct/not-direct mapping, and stable behavior when older Xen versions omit newer bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/features.h -->

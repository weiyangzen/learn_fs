# sources/distributed-fs/ceph-client/include/linux/vhost_iotlb.h

## Purpose
This header defines the vhost IOTLB interval map used to track guest IOVA to host address mappings for vhost and vDPA devices.

## Important APIs, types, and functions
Key types are `vhost_iotlb_map`, `vhost_iotlb`, and the iterator helper macro. APIs allocate/free an IOTLB, add/delete mappings, reset, translate by address/size, and initialize an embedded IOTLB.

## Control flow, state, and persistence
Users add mapping intervals with permissions and opaque metadata, translate IOVAs during data path setup, delete intervals on unmap, and reset on device teardown. State is an in-memory interval tree/list of mappings; no persistence is defined.

## Dependencies and integration points
It depends on interval trees, lists, and vhost UAPI permission flags. It integrates with vhost, vDPA, IOMMU/IOTLB update handling, and device-specific DMA translation.

## Risks and test signals
Risks include overlapping interval handling, permission mismatches, stale opaque pointers, and leaks on reset/free. Tests should cover add/delete/lookup boundaries, overlapping updates, permission filtering, full reset, and iteration order.

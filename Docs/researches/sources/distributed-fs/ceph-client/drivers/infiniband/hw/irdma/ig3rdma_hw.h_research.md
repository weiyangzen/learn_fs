# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_hw.h

## Purpose
`ig3rdma_hw.h` defines Gen3 RDMA MMIO window geometry, PF/VF count constants, hardware capability constants, and prototypes for Gen3 register lookup and virtual-channel send.

## Important APIs, types, and functions
Important definitions include `IG3_PF_RDMA_REGION_OFFSET`, `IG3_PF_RDMA_REGION_LEN`, `IG3_VF_RDMA_REGION_OFFSET`, `IG3_VF_RDMA_REGION_LEN`, `enum ig3rdma_device_caps_const`, `ig3rdma_get_reg_addr`, and `ig3rdma_vchnl_send_sync`.

## Control flow, state, and persistence
No runtime control flow exists in the header. Its constants are applied during Gen3 core probe when MMIO regions are mapped and during hardware initialization when limits are copied into `dev->hw_attrs`.

## Dependencies and integration points
The header is consumed by Gen3 hardware and interface files. `ig3rdma_vchnl_send_sync` is implemented in `ig3rdma_if.c` and used by common virtual-channel code through the generation setup.

## Risks and test signals
Risks are stale region offsets/lengths, PF/VF capability mismatch, and push-page limit exposure errors. Tests should verify PF and VF region mapping, virtual-channel timeout handling, and max inline/IRD/ORD/resource attributes reported to verbs.

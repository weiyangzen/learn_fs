<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.c

## Purpose
Implements mlx5 RDMA DMA handle (`ib_dmah`) allocation and deallocation for PCIe TPH steering-tag support. It validates mandatory/optional DMAH fields and allocates a mlx5 steering-tag index when requested.

## Important APIs, Types, And Functions
- `mlx5_ib_alloc_dmah()` is the provider allocation callback. It requires processing-hint (`IB_DMAH_PH_EXISTS`) data, validates that CPU ID and memory type are provided as an all-or-nothing pair, and allocates a steering-tag index through `mlx5_st_alloc_index()` when ST fields are present.
- `mlx5_ib_dealloc_dmah()` frees the steering-tag index with `mlx5_st_dealloc_index()` when the DMAH had CPU ID/ST state.
- `mlx5_ib_dev_dmah_ops` registers `.alloc_dmah` and `.dealloc_dmah` with RDMA core.

## Control Flow
Allocation first checks that the PH field is present because PCIe TPH requires a processing hint. It then forms the optional steering-tag field mask from `IB_DMAH_CPU_ID_EXISTS` and `IB_DMAH_MEM_TYPE_EXISTS`; if either optional field appears without the other, allocation fails. If both are present, the mlx5 core steering-tag allocator receives memory type and CPU ID and stores the resulting index in the private DMAH object. Deallocation mirrors this by freeing the stored index only when the optional CPU ID field was present.

## State And Persistence
The only persistent per-object state is `struct mlx5_ib_dmah::st_index`. Hardware or core allocator state for steering tags is owned by mlx5 core after `mlx5_st_alloc_index()` succeeds and released during deallocation. No on-disk persistence exists.

## Dependencies And Integration Points
The file depends on RDMA DMAH core types, uverbs standard types, Linux PCI TPH support, and mlx5 core steering-tag allocation helpers. It integrates with the mlx5 IB device ops table through `mlx5_ib_dev_dmah_ops`.

## Risks And Edge Cases
Optional field validation must remain synchronized with RDMA core's `valid_fields` contract. Deallocation tests only `IB_DMAH_CPU_ID_EXISTS`; because allocation rejects partial optional ST data, this is equivalent to checking the full optional pair, but future fields could change that assumption. The code does not use `attrs` directly, so all validation depends on the prefilled `ib_dmah`.

## Test Signals
Test DMAH allocation with missing PH, PH only, PH plus complete CPU/mem-type ST fields, and partial ST fields. Verify steering-tag allocation/deallocation calls are balanced and that repeated create/destroy cycles do not leak ST indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.c -->

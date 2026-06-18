<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.h

## Purpose
Declares the mlx5 private DMA handle object and provider ops used for DMAH/TPH support.

## Important APIs, Types, And Functions
- `mlx5_ib_dev_dmah_ops` is the device-ops bundle implemented in `dmah.c`.
- `struct mlx5_ib_dmah` embeds the RDMA core `ib_dmah` and stores the mlx5 steering-tag index.
- `to_mdmah()` converts `struct ib_dmah *` to `struct mlx5_ib_dmah *`.

## Control Flow
The header has no runtime control flow; it provides the object layout and inline conversion helper for the DMAH implementation.

## State And Persistence
Per-DMAH persistent state is limited to the embedded RDMA core object and `st_index`, which is valid when allocation requested steering-tag support.

## Dependencies And Integration Points
The header includes `mlx5_ib.h`, tying DMAH support to mlx5 IB private types and RDMA core definitions. It is consumed by `dmah.c` and by device setup code that installs `mlx5_ib_dev_dmah_ops`.

## Risks And Edge Cases
`to_mdmah()` assumes the `ib_dmah` is embedded in `struct mlx5_ib_dmah`; using it on another provider's object would be invalid. The header is small enough that most risk is in keeping `st_index` semantics aligned with allocation/deallocation logic.

## Test Signals
Provider build coverage and DMAH lifecycle tests should validate the ops declaration and conversion helper indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.h -->

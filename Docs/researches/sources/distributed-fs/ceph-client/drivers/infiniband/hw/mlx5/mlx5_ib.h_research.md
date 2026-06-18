# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mlx5_ib.h

## Purpose
`mlx5_ib.h` is the central private header for the mlx5 RDMA driver. It defines core object containers, device state, capability helpers, stage/profile infrastructure, mmap formats, memory-key and ODP state, GSI state, RoCE/representor/MACsec integration fields, and prototypes for operations implemented across the driver.

## Important APIs, Types, And Functions
Important container types include `mlx5_ib_dev`, `mlx5_ib_ucontext`, `mlx5_ib_pd`, `mlx5_ib_qp`, `mlx5_ib_cq`, `mlx5_ib_srq`, `mlx5_ib_mr`, `mlx5_ib_mw`, `mlx5_ib_flow_db`, `mlx5_ib_port`, `mlx5_roce`, `mlx5_ib_resources`, `mlx5_ib_gsi_qp`, `mlx5_ib_delay_drop`, `mlx5_var_table`, and `mlx5_macsec`. The header declares conversion helpers such as `to_mdev()`, `to_mqp()`, `to_mcq()`, `to_mmr()`, and many RDMA operation prototypes.

Key enums and macros define QP pseudo-types (`MLX5_IB_QPT_HW_GSI`, `MLX5_IB_QPT_DCI`, `MLX5_IB_QPT_DCT`), UMR update flags, mmap types and offset layout, MTT access flags, mkey types, optional counter types, debug congestion parameters, and `enum mlx5_ib_stages`. `struct mlx5_ib_profile` maps stage IDs to init/cleanup callbacks.

## Control Flow
The header has limited executable control flow through inline helpers. Page-size helpers build supported page-size and page-offset bitmaps for mlx5 command fields. User-index helpers validate CQE-version-dependent user indexes. ODP helpers store and dereference mkeys in an xarray with waitqueue release. LAG affinity helper centralizes when a user context should get default transmit-port affinity. Page-size helpers for MKC choose supported page sizes based on hardware min/max entity-size caps and IOVA alignment.

## State And Persistence Behavior
The header defines the shape of all major in-memory driver state. `mlx5_ib_dev` owns the RDMA device, core-device pointer, notifiers, port array, device resources, UMR/ODP/flow/counter/debug/data-direct/mkey state, profile pointer, special mkeys, and optional MACsec state. Per-object structures mirror RDMA-core objects and add mlx5 hardware IDs, buffers, locks, and firmware resources. No state is persisted by the header itself.

## Dependencies And Integration Points
It includes Linux kernel, RDMA core, mlx5 core, uverbs, mlx5 ABI, SRQ/QP, and MACsec headers. Every file in this work item depends on it directly or indirectly. Prototypes tie together implementations in AH, CQ, QP, MR, SRQ, MAD, memory, ODP, DevX, flow steering, counters, data-direct, and `main.c`.

## Risks
Because this is the central private ABI, layout or semantic changes can affect many compilation units. Locking responsibilities are embedded in comments and fields: QP mutexes, WQ spinlocks, CQ resize mutexes, flow DB mutex, delay-drop mutex, multiport spinlocks, data-direct lock, and MACsec lock must be honored by implementation files. Conditional fields under `CONFIG_MLX5_MACSEC` and ODP stubs require build-matrix coverage. Mmap enum values and object sizes are user ABI-adjacent and must remain compatible with uverbs expectations.

## Test Signals
Build coverage across feature combinations (`CONFIG_MLX5_ESWITCH`, `CONFIG_MLX5_MACSEC`, ODP, user access, IPoIB), sparse/lockdep where available, uverbs ABI tests for object sizes and mmap offsets, QP/CQ/MR/SRQ lifecycle tests, ODP mkey reference tests, GSI QP tests, and multiport/LAG/representor tests that exercise the fields defined here.

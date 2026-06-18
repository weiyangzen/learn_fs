# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mlx4_ib.h

## Purpose
`mlx4_ib.h` is the private shared header for the mlx4 RDMA driver. It defines driver constants, object wrappers around ib_core and mlx4 core resources, SR-IOV demux/tunnel structures, RoCE/GID/P_Key/counter state, the top-level `struct mlx4_ib_dev`, container conversion helpers, and cross-file prototypes for the mlx4_ib subsystem.

## Important APIs, types, and functions
- Constants and flags: `MLX4_IB_DRV_NAME`, SQ headroom constants, steering QPN constants, `MLX4_MR_PAGES_ALIGN`, tunnel buffer counts, alias GUID limits, `MLX4_PAGE_SIZE_SUPPORTED`, and QP create flags.
- Object wrappers: `mlx4_ib_ucontext`, `mlx4_ib_pd`, `mlx4_ib_xrcd`, `mlx4_ib_cq`, `mlx4_ib_mr`, `mlx4_ib_mw`, `mlx4_ib_qp`, `mlx4_ib_srq`, `mlx4_ib_ah`, `mlx4_ib_wq`, and `mlx4_ib_rwq_ind_table`.
- Flow and steering: `mlx4_ib_flow`, `mlx4_flow_reg_id`, `mlx4_ib_steering`, and `mlx4_wqn_range`.
- SR-IOV and MAD tunneling: `mlx4_ib_tunnel_header`, `mlx4_rcv_tunnel_hdr`, `mlx4_ib_proxy_sqp_hdr`, `mlx4_ib_demux_pv_qp`, `mlx4_ib_demux_pv_ctx`, `mlx4_ib_demux_ctx`, and `mlx4_ib_sriov`.
- Alias GUID state: `mlx4_sriov_alias_guid_info_rec_det`, `mlx4_sriov_alias_guid_port_rec_det`, and `mlx4_sriov_alias_guid`.
- RoCE state: `gid_cache_context`, `gid_entry`, `mlx4_port_gid_table`, and `mlx4_ib_iboe`.
- Top-level device: `struct mlx4_ib_dev` contains the embedded `ib_device`, mlx4 core device pointer, private UAR/PD, MAD agents, SM AHs, SL2VL cache, SR-IOV state, RoCE netdev/GID state, P_Key maps, counters, sysfs objects, steering resources, QP list, diagnostic counters, and mlx4 event notifier.
- Inline helpers: `to_mdev()`, `to_mpd()`, `to_mmr()`, `to_mqp()`, and similar container conversions; `mlx4_ib_bond_next_port()`; `mlx4_ib_ah_grh_present()`; and `mlx4_ib_umem_calc_optimal_mtt_size()`.

## Control flow
The header does not contain runtime control flow beyond inline helpers. Its declarations define the contract across implementation files. `main.c` populates `mlx4_ib_dev` and installs ops using the object sizes declared here. `mad.c` uses demux, tunnel, alias GUID, SL2VL, and P_Key structures. `mcg.c` uses `mlx4_ib_demux_ctx` and send helpers. `mr.c` uses MR/MW wrappers and the optimal MTT-size helper. QP/CQ/SRQ/AH implementation files use the shared wrapper structs and prototypes.

## State and persistence behavior
All structures describe in-memory driver state, with embedded handles to mlx4 hardware resources such as MPTs, MTTs, QPs, CQs, PDs, UARs, counters, and EQs. The header records which state is protected by locks in comments or member names: CQ locks and resize mutexes, QP mutexes, ucontext doorbell/WQN range mutexes, SR-IOV going-down spinlock, MCG table mutex, RoCE spinlock, counter mutexes, and reset-flow resource lock. Persistent effects occur only through implementation files that program hardware or expose sysfs/ib_device objects.

## Dependencies and integration points
The header includes Linux list/mutex/idr/notifier primitives, RDMA verbs, umem, MAD, SA APIs, and mlx4 device/doorbell/QP/CQ headers. It is the coupling layer for the whole mlx4_ib driver: prototypes span MR, CQ, AH, SRQ, QP, MAD, MCG, CM paravirt, alias GUID, sysfs, steering, WQ/RSS, and event subsystems. Any structure change can impact multiple C files and ib_core object layout registration.

## Risks and edge cases
- Embedded ib_core objects plus `container_of` helpers require object allocation sizes in `main.c` to match these structures exactly.
- Several arrays are dimensioned by mlx4 constants such as `MLX4_MAX_PORTS`, `MLX4_MFUNC_MAX`, `MLX4_MAX_PORT_GIDS`, and fixed alias GUID counts; capability mismatches can cause out-of-range bugs if callers do not validate indexes.
- SR-IOV demux state mixes workqueues, QP resources, DMA rings, atomic TIDs, GUID cache, and MCG table locks; lifecycle must follow the structure ownership model.
- Header-level inline `mlx4_ib_umem_calc_optimal_mtt_size()` determines MR page size behavior and returns `order_base_2(pg_sz)`; callers must treat negative values as errors and shift values as page orders.
- `mlx4_ib_ah_grh_present()` infers GRH presence differently for Ethernet and IB, which affects send-path header construction.

## Test signals
- Full-driver build is the primary signal for prototype/object-layout consistency.
- KASAN/lockdep tests around QP/CQ/MR/SR-IOV operations can expose misuse of shared structures and locks.
- ABI-sensitive tests should cover uverbs object allocation for all wrappers whose sizes are registered in `main.c`.
- Capability matrix tests should vary number of ports, VFs, GID/P_Key table lengths, RoCE v1/v2, RSS, XRC, memory windows, and flow steering to exercise array and optional-op assumptions.

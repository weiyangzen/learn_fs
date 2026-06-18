# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/ah.c

## Purpose
`ah.c` creates and queries mlx4 address vectors for InfiniBand and RoCE address handles, including SR-IOV slave AH creation.

## Important APIs, Types, And Functions
`mlx4_ib_create_ah()` dispatches to `create_ib_ah()` or `create_iboe_ah()` based on AH type. `create_ib_ah()` fills InfiniBand AV fields such as port/PD, SL, path bits, GRH, DLID, and static rate. `create_iboe_ah()` fills Ethernet/RoCE AV fields, resolves source MAC/VLAN from `sgid_attr`, maps GID index to real hardware index, handles multicast DLID requirements, and encodes traffic class/flow label. `mlx4_ib_create_ah_slave()` creates an AH using an explicit slave SGID index/source MAC/VLAN. `mlx4_ib_query_ah()` reconstructs an `rdma_ah_attr`.

## Control Flow
Create rejects RoCE AHs without GRH, then fills the hardware AV. RoCE creation reads L2 fields from the GID attribute unless called through the slave path, where the caller supplies the slave GID index, source MAC, and VLAN. Static rate is reduced until supported by device caps. Query decodes port, SL, DLID, static rate, path bits, and GRH from the stored AV.

## State And Persistence
The AV is stored inside `struct mlx4_ib_ah` for the lifetime of the RDMA AH. It reflects PD number, port, GID index, L2/L3 addressing, VLAN, and rate. There is no persistence beyond AH lifetime.

## Dependencies And Integration Points
The file uses RDMA AH/GID helpers, mlx4 device caps, PD numbers, `mlx4_ib_gid_index_to_real_index()`, `rdma_read_gid_l2_fields()`, and SR-IOV slave AH creation paths.

## Risks
RoCE source L2 resolution may sleep, and the comment notes atomic-context concerns. Querying RoCE AHs returns DLID zero and reconstructs only fields represented in the AV. The slave path clears a force-loopback bit and overwrites VLAN/source MAC; mistakes affect VF packet routing. Static-rate fallback depends on `stat_rate_support` bit numbering.

## Test Signals
Test IB and RoCE AH creation, RoCE missing-GRH rejection, VLAN priority encoding, multicast RoCE DLID placeholder, static-rate fallback, slave AH source MAC/VLAN override, query round-trips, and invalid GID-index mapping failures.

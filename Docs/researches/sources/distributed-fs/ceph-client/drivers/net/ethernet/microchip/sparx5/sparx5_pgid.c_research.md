## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_pgid.c

### Purpose
`sparx5_pgid.c` manages allocation of packet group IDs used for flood, CPU, and multicast forwarding masks in the Sparx5 analyzer block.

### Important APIs, Types, And Functions
The exported functions are `sparx5_pgid_init()`, `sparx5_pgid_alloc_mcast()`, `sparx5_pgid_free()`, and `sparx5_get_pgid()`. They operate on `sparx5->pgid_map[]`, whose entries use states such as `SPX5_PGID_FREE`, `SPX5_PGID_RESERVED`, and `SPX5_PGID_MULTICAST`.

### Control Flow
Initialization marks every PGID free, then reserves the fixed PGIDs through the CPU PGID. Multicast allocation scans from `PGID_MCAST_START` translated through `sparx5_get_pgid()` to the chip-specific absolute PGID space. Freeing rejects fixed PGIDs, out-of-range IDs, and already-free entries before returning the slot to the free state.

### State, Persistence, And Dependencies
State is in-memory only in `sparx5->pgid_map`; hardware PGID masks are updated by other files after an ID is allocated. `sparx5_get_pgid()` maps logical PGID constants after the physical front-port range by adding `n_ports`.

### Integration Points
Switchdev MDB handling allocates multicast PGIDs here, bridge flood programming uses fixed PGIDs, and MACT entries can target allocated PGIDs. The file relies on `sparx5_main.h` constants and the runtime `sparx5->data->consts` table.

### Risks
The allocator is linear and has no lock of its own; callers must serialize if concurrent MDB changes are possible. Freeing an ID does not clear hardware masks; callers must clear them first. Logical-to-absolute PGID mapping depends on chip constants matching register layout.

### Test Signals
Validate initialization reservations, allocation exhaustion, rejection of CPU/flood PGID free attempts, reuse after free, and correct interaction with MDB add/delete hardware mask clearing.

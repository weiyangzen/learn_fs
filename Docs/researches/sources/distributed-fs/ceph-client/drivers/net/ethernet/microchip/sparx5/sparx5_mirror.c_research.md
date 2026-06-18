## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_mirror.c

### Purpose
`sparx5_mirror.c` implements TC matchall mirroring support for Microchip Sparx5-family switch ports. It maps a source port, monitor port, and ingress/egress direction onto the chip's small set of ANA mirror probes and QFWD frame-copy monitor-port registers.

### Important APIs, Types, And Functions
The exported entry points are `sparx5_mirror_add()`, `sparx5_mirror_del()`, and `sparx5_mirror_stats()`, all operating on `struct sparx5_mall_entry`. Internal helpers read/write probe membership (`sparx5_mirror_port_get/add/del()`), direction (`sparx5_mirror_dir_get/set()`), and monitor port (`sparx5_mirror_monitor_get/set()`). `SPX5_MIRROR_PROBE_MAX` limits hardware probes to three, and the QFWD monitor register index is offset by `SPX5_QFWD_MP_OFFSET`.

### Control Flow
Adding a mirror rejects self-mirroring, checks that the source port is not already used as a monitor port, tries to reuse an existing probe with the same direction and monitor port, then falls back to an empty probe. It sets the source port bit in `ANA_AC_PROBE_PORT_CFG{,1}`, writes probe direction, writes the monitor port, and stores the selected probe index in the mall entry. Deletion removes the source port from the probe and only disables direction and resets monitor port when the probe becomes empty.

### State, Persistence, And Dependencies
Persistent state is split between hardware registers and `entry->mirror.idx`. Statistics baselining is kept in `entry->port->mirror_stats` and updated from `sparx5_get_stats64()`. The file depends on `sparx5_main.h`, generated register macros, TC mall entry definitions, `is_sparx5()` for 64-bit port masks, and Linux flow stats helpers.

### Integration Points
This is called from `sparx5_tc_matchall.c` for `FLOW_ACTION_MIRRED` matchall filters and reports hardware stats back through `TC_CLSMATCHALL_STATS`. It shares port statistics with the normal netdev stats path and uses switch hardware probes rather than VCAP rules.

### Risks
Only three probes exist, so multi-user mirror programming can return `-ENOENT`. Monitor-port exclusion is checked against the source port only, so callers must ensure action devices are valid Sparx5 ports. Probe state is hardware-resident; inconsistent `entry->mirror.idx` would delete the wrong probe membership. `do_div()` mutates the local `reg` variable intentionally, but this is easy to misread.

### Test Signals
Test ingress and egress mirror add/delete, duplicate source detection, source equal monitor rejection, monitor-port reuse, exhaustion after three distinct probe configurations, stats deltas across repeated reads, and delete behavior when multiple source ports share one probe.

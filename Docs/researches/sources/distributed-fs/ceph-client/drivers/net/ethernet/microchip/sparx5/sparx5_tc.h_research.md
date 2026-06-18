## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc.h

### Purpose
`sparx5_tc.h` defines TC action encoding constants for Sparx5 VCAP actions and declares the TC dispatcher and classifier handlers.

### Important APIs, Types, And Functions
It defines enums for port mask modes, ES0 forwarding selection, outer tag selection, TPID A/B selection, VID/PCP/DEI selectors, and inner tag selection. It declares `sparx5_port_setup_tc()`, `sparx5_tc_matchall()`, and `sparx5_tc_flower()`.

### Control Flow
No runtime control flow is present. The enum values are passed directly to VCAP action fields by `sparx5_tc_flower.c` and `sparx5_tc_matchall.c`.

### State, Persistence, And Dependencies
There is no state. The header depends on Linux flow offload and netdevice headers and must match hardware VCAP action encodings.

### Integration Points
Used by TC dispatcher, matchall mirror/goto handling, flower VCAP action construction, and mirror support.

### Risks
Wrong enum values would program valid-looking but incorrect VCAP actions. The header is a narrow contract; adding TC actions requires synchronized changes in flower/matchall parsing and hardware validation.

### Test Signals
Compile coverage plus VCAP action tests for mirror/redirect/trap/VLAN push/pop/mangle to confirm the encoded values produce expected hardware behavior.

## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_port.h

### Purpose
`sparx5_port.h` declares the public port configuration, status, and QoS programming interface for Sparx5 ports and provides inline helpers that classify port numbers and map them to hardware target instances.

### Important APIs, Types, And Functions
It defines PCP/DSCP rewrite mode constants, inline capability helpers (`sparx5_port_is_2g5()`, `sparx5_port_is_5g()`, `sparx5_port_is_10g()`, `sparx5_port_is_25g()`, `sparx5_port_is_rgmii()`), target mapping helpers, `struct sparx5_port_status`, and QoS map structs for PCP, PCP rewrite, DSCP, DSCP rewrite, and defaults. It declares port init/config/PCS/SerDes/status/enable and QoS functions implemented in `sparx5_port.c`.

### Control Flow
There is no runtime control flow beyond inline mapping. Port classes determine whether callers use DEV2G5, DEV5G, DEV10G, or DEV25G blocks and which PCS target applies. QoS structs encode the data passed down to register programming functions.

### State, Persistence, And Dependencies
The header has no storage but defines the shape of state consumed by the driver. It depends on `sparx5_main.h` for `struct sparx5`, `struct sparx5_port`, and `SPX5_PRIOS`.

### Integration Points
Included by netdev, phylink, and port implementation files. It is the contract between link-management code and hardware programming, and between QoS/DCB/TC code and per-port classifier/rewrite registers.

### Risks
Inline port-number ranges encode Sparx5 topology directly; variant support depends on `sparx5_ops` wrappers where available. `sparx5_port_is_rgmii()` returns false in this variant, so LAN969x or future chips must override through ops rather than this inline. QoS map array dimensions must match hardware register tables.

### Test Signals
Compile coverage across all users, unit-style validation of port-number mapping for boundary ports, and integration tests confirming chip ops override behavior for non-Sparx5 variants.

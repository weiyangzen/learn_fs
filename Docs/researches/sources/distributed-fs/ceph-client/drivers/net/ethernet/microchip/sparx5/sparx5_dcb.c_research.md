# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_dcb.c

## Purpose
This file implements Sparx5 DCBNL support for application priority mappings, apptrust policy, and priority rewrite tables. It translates kernel DCB app and rewrite state into hardware QoS configuration for each port.

## Important APIs, Types, And Functions
The exported objects/functions are `sparx5_dcbnl_ops` and `sparx5_dcb_init()`. Important helpers include `sparx5_dcb_app_validate()`, `sparx5_dcb_apptrust_validate()`, `sparx5_dcb_app_update()`, `sparx5_dcb_ieee_setapp()`, `sparx5_dcb_ieee_delapp()`, `sparx5_dcb_setapptrust()`, `sparx5_dcb_getapptrust()`, `sparx5_dcb_setrewr()`, and `sparx5_dcb_delrewr()`.

## Control Flow
Initialization attaches DCBNL ops to each netdev, defaults trust order to DSCP plus PCP, and enables DSCP rewrite mode. DCB app set/delete validates selector/protocol/priority, updates kernel DCB state, replicates DSCP mappings globally across all ports, and then rebuilds port QoS. `sparx5_dcb_app_update()` reads default priority, DSCP maps, PCP maps, PCP rewrite maps, and DSCP rewrite maps, enables only trusted classification sources, enables rewrite only when mappings exist, and calls `sparx5_port_qos_set()`.

## State And Persistence
Per-port apptrust state is held in the static `sparx5_port_apptrust[SPX5_PORTS]` pointer table. Mapping and rewrite state is held by the kernel DCB app database and mirrored into hardware QoS registers through `sparx5_port_qos_set()`. No disk persistence exists.

## Dependencies And Integration Points
The file depends on DCBNL, DCB app/rewrite helper APIs, Sparx5 QoS structures and setters, port netdevs, and constants for DSCP/PCP table sizes and priorities.

## Risks And Edge Cases
DSCP mappings are global in hardware but exposed through per-netdev DCB operations, so set/delete replicates across all ports and can fail midway. Apptrust validation is order-sensitive and only supports empty, DSCP, PCP, or DSCP then PCP. Default priority uses the highest set bit from the DCB mask. Static apptrust storage assumes port numbers are below `SPX5_PORTS`.

## Test Signals
Use `dcb app` and apptrust commands for DSCP, PCP, and default priority; test invalid selectors/ranges; verify global DSCP replication across ports; confirm PCP/DSCP rewrite only when trusted and mapped; and check hardware QoS classification with marked traffic.

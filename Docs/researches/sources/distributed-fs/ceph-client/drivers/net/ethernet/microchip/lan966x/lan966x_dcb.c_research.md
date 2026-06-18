# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_dcb.c

Purpose: implements optional DCBNL support for LAN966x QoS classification and rewrite mapping. It maps DCB APP entries, DSCP/PCP trust policy, default priority, and rewrite tables into the port QoS configuration consumed by lower-level port code.

Important APIs and functions: `lan966x_dcb_init` installs `dcbnl_ops` on each probed port, sets default apptrust to DSCP+PCP, and enables DSCP rewrite mode. DCB callbacks are `lan966x_dcb_ieee_setapp`, `lan966x_dcb_ieee_delapp`, `lan966x_dcb_setapptrust`, `lan966x_dcb_getapptrust`, `lan966x_dcb_setrewr`, and `lan966x_dcb_delrewr`. `lan966x_dcb_app_update` reads DCB app/rewrite maps and calls `lan966x_port_qos_set`.

Control flow: setapp validates selector/protocol/priority, removes an existing mapping for the same selector/protocol, replicates DSCP mappings to every LAN966x port because DSCP classification is global, stores the DCB entry, and refreshes hardware QoS. Rewrite callbacks follow the same validate/delete-existing/set/update pattern. Apptrust validation only accepts predefined ordered policies: empty, DSCP, PCP, or DSCP then PCP. `lan966x_dcb_app_update` builds a `struct lan966x_port_qos`, enabling PCP and/or DSCP ingress and rewrite maps only when the current trust policy contains that selector.

State and persistence: per-port apptrust pointers are held in the static `lan966x_port_apptrust[NUM_PHYS_PORTS]` array. DCB APP and rewrite mappings are stored in the kernel DCB app tables and re-read on every update. Hardware QoS state persists through `lan966x_port_qos_set` and DSCP rewrite mode programming.

Dependencies and integration points: depends on `CONFIG_LAN966X_DCB`, Linux DCBNL helpers (`dcb_getapp`, `dcb_ieee_setapp`, rewrite helpers), `struct lan966x_port_qos` from the main header, and port QoS programming functions from the port module.

Risks: static apptrust storage is indexed by chip port and assumes one active LAN966x instance or compatible lifetime behavior. DSCP replication means one port operation can fail midway and leave per-port DCB tables inconsistent. Rewrite maps use first-set-bit extraction and support only one rewrite target per priority/protocol. Hardware behavior depends on apptrust order, so accepting unsupported selector sequences would change classification semantics.

Test signals: `dcb app add/del` for DSCP, PCP, and default priority; invalid selector/protocol/priority rejection; apptrust policy changes; rewrite set/delete for PCP and DSCP; multiple ports sharing DSCP maps; DCB-disabled build; traffic priority classification and rewritten PCP/DSCP verification.

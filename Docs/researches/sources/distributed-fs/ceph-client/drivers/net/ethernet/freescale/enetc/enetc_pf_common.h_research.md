# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf_common.h

## Purpose
Declares the PF common helper interface shared by rev1 and rev4 PF drivers.

## Important APIs, Types, and Functions
It declares MAC, netdev, MDIO, phylink, RSS, and VLAN helper functions implemented in `enetc_pf_common.c`, and defines inline `enetc_get_ip_revision` to read `ENETC_G_EIPBRR0`.

## Control Flow
No runtime control flow beyond the inline revision read. The declarations allow generation-specific PF files to avoid duplicating common setup logic.

## State and Persistence
The header owns no state, but its APIs operate on persistent PF/SI/netdev state such as MAC registers, MDIO buses, phylink, RSS key, VLAN filter registers, and netdev feature flags.

## Dependencies and Integration Points
Includes `enetc_pf.h`, so consumers get PF state, ENETC hardware accessors, and phylink types. Used by `enetc_pf.c` and `enetc4_pf.c`.

## Risks
Prototype drift breaks both PF generations. The inline revision helper assumes PF global register mapping is valid before use.

## Test Signals
Build rev1 and rev4 PF drivers, verify revision reads during probe after generic PCI mapping, and confirm all declared helpers are exported for module linkage.

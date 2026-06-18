# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_port.c

## Purpose

`nfp_port.c` implements common NFP port helpers shared by PF data netdevs and representors. It maps netdevs to `struct nfp_port`, provides parent ID and physical port names, delegates TC setup to the active app, protects feature changes while TC offloads are active, retrieves/refreshes ETH-table port data, configures physical port up/down state, initializes physical-port metadata, and allocates/frees port objects.

## Important APIs, Types, and Functions

Public functions are `nfp_port_from_netdev()`, `nfp_port_get_port_parent_id()`, `nfp_port_setup_tc()`, `nfp_port_set_features()`, `__nfp_port_get_eth_port()`, `nfp_port_get_eth_port()`, `nfp_port_get_phys_port_name()`, `nfp_port_configure()`, `nfp_port_init_phy_port()`, `nfp_port_alloc()`, and `nfp_port_free()`.

## Control Flow

`nfp_port_from_netdev()` distinguishes core NFP netdevs from representors and returns their stored port pointer. `nfp_port_get_eth_port()` checks if a physical port has a changed flag and refreshes from the NSP ETH table before returning it. Port naming switches on type to emit `pN`, `pNsM`, `pfN`, `pfNsM`, or `pfNvfM`. Physical port configure ignores non-physical or forced ports and otherwise calls `nfp_eth_set_configured()`. Physical-port init validates the ETH table entry, handles override-changed invalidation, stores ETH IDs and MAC stats pointers, and updates `netdev->dev_port`.

## State and Persistence Behavior

`nfp_port_alloc()` adds port objects to the PF port list, and `nfp_port_free()` removes/frees them. Port fields persist netdev/type/app relationships, ETH-table pointers, port IDs, MAC stats pointers, vNIC IDs, split IDs, and TC offload count. `nfp_port_configure()` changes firmware/NSP configured state for physical interfaces.

## Dependencies and Integration Points

The file depends on NFP netdev/representor type checks, `nfp_app_setup_tc()`, CPP serial lookup, NSP ETH helpers, port structures in `nfp_port.h`, and RTNL/lockdep expectations from callers. It feeds netdev ops and ethtool ops.

## Risks and Edge Cases

Unknown netdev types trigger `WARN(1)`. `nfp_port_set_features()` refuses disabling HW TC while offloads are active, so offload counting must be accurate. `__nfp_port_get_eth_port()` intentionally returns NULL for non-physical ports. Refresh failures set `NFP_PORT_CHANGED` and callers must handle NULL ETH data. Forced ports bypass configured-state changes.

## Test Signals

Test phys-port names for split/non-split physical, PF, split-PF, and VF ports; parent ID reporting; TC setup delegation; HW TC disable with active offloads; ETH-table refresh on changed flags; forced and non-physical configure no-ops; and allocation/free list integrity.

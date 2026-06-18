# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app_nic.c

## Purpose
Provides shared NIC-app vNIC allocation helpers for binding a data vNIC to a physical NFP port and initializing its MAC address.

## Important APIs, Types, and Functions
- `nfp_app_nic_vnic_init_phy_port()` allocates an `NFP_PORT_PHYS_PORT`, initializes it from the PF ETH table by id, and returns whether the port was marked invalid.
- `nfp_app_nic_vnic_alloc()` calls the physical-port initializer and, for valid ports, reads the MAC address into the netdev using `nfp_net_get_mac_addr()`.

## Control Flow
App vNIC allocation calls this helper during PF/vNIC setup. If there is no ETH table, it silently leaves the vNIC without a physical port. If port initialization fails, it frees the allocated port and propagates the error. If the port is invalid, allocation returns success but skips MAC setup.

## State and Persistence Behavior
Mutates `nn->port` and netdev MAC address. The port object is owned by the vNIC/app lifecycle and later freed by common/app cleanup. No persistent storage.

## Dependencies and Integration Points
Depends on NSP/ETH table data, `nfp_port_alloc()`, `nfp_port_init_phy_port()`, `nfp_port_free()`, and common MAC retrieval. Used by app implementations that expose physical NIC ports.

## Risks
The return convention from `nfp_app_nic_vnic_init_phy_port()` is subtle: positive means invalid port but not fatal. Callers must preserve that behavior to avoid failing probe for intentionally invalid ports.

## Test Signals
Probe with no ETH table, valid ETH table, invalid ports, and failing `nfp_port_init_phy_port()`. Verify port object cleanup and MAC address assignment.

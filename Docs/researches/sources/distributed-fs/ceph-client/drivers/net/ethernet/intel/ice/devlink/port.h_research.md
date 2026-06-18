# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/port.h

## Purpose
`port.h` declares the devlink port lifecycle API and defines the dynamic-port state object used for PCI subfunctions.

## Important APIs, Types, And Functions
`struct ice_dynamic_port` contains the hardware address, administrative active flag, operational attached flag, embedded `struct devlink_port`, owning PF, associated VSI, representor ID, SF number, and flavour-specific SF device pointer. `ice_devlink_port_to_dyn()` maps from an embedded `devlink_port` back to the dynamic port.

Declared APIs cover cleanup of all dynamic ports, PF/VF/SF devlink port creation and destruction, SF auxiliary-device virtual port creation and destruction, and the `ice_devlink_port_new()` devlink operation.

## Control Flow
PF and VF setup paths call the respective create functions when their VSI and devlink context are ready. Switchdev/SF code calls `ice_devlink_port_new()` in response to userspace `devlink port add`, then later registers SF devlink ports and SF auxiliary virtual ports as the SF moves through activation and device creation. Teardown calls destroy/dealloc helpers in reverse order.

## State And Persistence
The header defines runtime dynamic-port state. It does not directly persist configuration, although `hw_addr`, `active`, and `attached` reflect devlink function configuration and SF operational state while the PF is alive.

## Dependencies And Integration Points
It includes `../ice.h` and `../ice_sf_eth.h`, so it is tightly coupled to the central PF/VSI definitions and SF Ethernet device support. The API is consumed by `devlink.c`, eswitch/SF code, and teardown paths that must remove all dynamic ports.

## Risks And Test Signals
The main risks are lifetime and ownership of the embedded devlink port and VSI pointer. Test signals include successful compilation of container conversions, SF add/delete cycles, no leaked xarray entries after `ice_dealloc_all_dynamic_ports()`, and correct port state reporting through devlink.

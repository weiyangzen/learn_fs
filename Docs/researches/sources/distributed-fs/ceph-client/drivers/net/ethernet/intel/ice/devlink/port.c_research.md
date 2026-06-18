# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/port.c

## Purpose
`port.c` implements ICE devlink port operations for physical PF ports, PCI VF ports, PCI SF dynamic ports, and virtual SF auxiliary-device ports. It also exposes firmware port split/unsplit options through devlink.

## Important APIs, Types, And Functions
Port split support uses `ice_devlink_port_split()`, `ice_devlink_port_unsplit()`, `ice_devlink_aq_set_port_option()`, and `ice_devlink_set_port_split_options()`. The implementation queries `ice_aq_get_port_options()`, chooses an option by requested split count, writes the selected option, and triggers NVM write activation requiring reboot.

PF ports are created by `ice_devlink_create_pf_port()` with physical flavour, PF port number, switch ID derived from PCI DSN, and split attributes on PF 0. VF ports are created by `ice_devlink_create_vf_port()` with PCI VF flavour and MAC get/set callbacks. SF support centers on `struct ice_dynamic_port`, `ice_devlink_port_new()`, `ice_alloc_dynamic_port()`, `ice_devlink_create_sf_port()`, `ice_devlink_destroy_sf_port()`, `ice_activate_dynamic_port()`, and `ice_dealloc_dynamic_port()`. SF function ops support MAC get/set and active/inactive state changes.

## Control Flow
Devlink `port_new` first validates attributes: only PCI SF flavour, no controller override, no user-defined port index, matching PF number, and dynamic MSI-X support. It also requires switchdev eswitch mode. Allocation reserves or inserts an SF number in `pf->sf_nums`, allocates a dynamic port and VSI, stores it in `pf->dyn_ports`, attaches it to the eswitch, and returns the devlink port. Activation delegates to `ice_sf_eth_activate()`; deactivation delegates to `ice_sf_eth_deactivate()`. Deallocation deactivates first, erases xarray entries, detaches from eswitch, frees VSI, and frees the dynamic port.

## State And Persistence
Port split selection is persisted to NVM and requires reboot/EMP activation semantics. Dynamic SF state is runtime state in `pf->dyn_ports`, `pf->sf_nums`, `dyn_port->active`, `dyn_port->attached`, `dyn_port->hw_addr`, `dyn_port->repr_id`, `dyn_port->sfnum`, `dyn_port->sf_dev`, and associated VSI. VF MAC changes update VF configuration through `__ice_set_vf_mac()`.

## Dependencies And Integration Points
This file depends on devlink port APIs, ICE admin queue port option definitions, NVM activation helpers, VSI allocation/free, eswitch attach/detach, SF Ethernet activation, SR-IOV VF structures, xarray allocation, PCI MSI-X dynamic allocation, and switch ID generation from PCI DSN.

## Risks And Test Signals
Risks include xarray reservation leaks on unwind, deleting active SF ports, allowing MAC changes while attached, stale devlink-rate leaves, and global `ice_active_port_option` state across devices. Test signals include `devlink port split/unsplit`, PF/VF port creation on probe and SR-IOV enable, SF creation only in switchdev mode, SF MAC set rejection while attached, SF activation/deactivation, and clean `devlink port del` unwind.

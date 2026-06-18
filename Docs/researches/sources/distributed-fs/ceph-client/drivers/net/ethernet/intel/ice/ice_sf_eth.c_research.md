# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_eth.c

## Purpose

`ice_sf_eth.c` implements Ethernet subfunction support for the ice driver. It registers an auxiliary bus driver named `ice.sf`, activates dynamic subfunction ports by creating auxiliary devices, probes those devices into VSI/devlink/netdev resources, and tears them down on deactivation or driver removal.

## Important APIs, Types, And Functions

- `ice_sf_netdev_ops` binds subfunction netdev operations to common ice handlers such as open/stop, transmit, VLAN add/delete, MTU change, stats, TX timeout, XDP, XDP transmit, and AF_XDP wakeup.
- `ice_sf_cfg_netdev()` allocates an Ethernet netdev sized for the subfunction VSI queues, sets hardware and permanent MAC address from the dynamic port, assigns features/XDP capabilities, links the devlink port, registers the netdev, and starts it carrier-off with stopped TX queues.
- `ice_sf_decfg_netdev()` unregisters and frees the netdev and clears VSI state bits.
- `ice_sf_dev_probe()` is the auxiliary-driver probe path that configures the VSI, allocates subfunction devlink private state, updates switchdev representation mapping, creates the SF devlink port, registers the netdev, links the parent dynamic devlink port to the SF devlink instance, adds NAPI, registers devlink, and marks the dynamic port attached.
- `ice_sf_dev_remove()` closes the VSI, removes netdev/devlink resources, frees the devlink instance, deconfigures the VSI, and marks the dynamic port detached.
- `ice_sf_driver_register()` and `ice_sf_driver_unregister()` register/unregister the auxiliary driver.
- `ice_sf_eth_activate()` allocates an xarray auxiliary ID, allocates `struct ice_sf_dev`, initializes and adds the auxiliary device, and stores it in `dyn_port->sf_dev`.
- `ice_sf_eth_deactivate()` deletes and uninitializes the auxiliary device.

## Control Flow

Activation begins from the dynamic-port/devlink control path. `ice_sf_eth_activate()` allocates a unique ID from `ice_sf_aux_id`, initializes an auxiliary device named `sf` with the PF PCI device as parent, and adds it to the auxiliary bus. The bus then invokes `ice_sf_dev_probe()`, which turns the preallocated dynamic-port VSI into an `ICE_VSI_SF`, configures the VSI, creates subfunction devlink resources, registers a netdev, links devlink instances, and registers NAPI/devlink. Failure paths unwind in reverse order: netdev, devlink port, VSI config, devlink allocation, and locks.

Removal is split between device remove and release. `ice_sf_eth_deactivate()` removes the auxiliary device, causing `ice_sf_dev_remove()` to tear down active networking resources. Later `auxiliary_device_uninit()` reaches `ice_sf_dev_release()`, which erases the ID from the xarray and frees the `ice_sf_dev` tracking object.

## State And Persistence

State is runtime-only. `dyn_port->vsi`, `dyn_port->pf`, `dyn_port->hw_addr`, `dyn_port->repr_id`, `dyn_port->attached`, and `dyn_port->sf_dev` connect the dynamic port to the subfunction device. `vsi->type`, `vsi->port_info`, `vsi->flags`, `vsi->sf`, `vsi->netdev`, and VSI state bits track the configured network side. `ice_sf_priv` owns the SF devlink port and backpointer. The xarray stores allocated auxiliary IDs until release.

## Dependencies And Integration Points

The file depends on core ice netdev/VSI/XDP/VLAN operations, `ice_allocate_sf()`, devlink helpers, dynamic port and representor code, the Linux auxiliary bus, xarray allocation, and PCI parent devices. It integrates with devlink subfunction activation, switchdev representor mapping, common VSI configuration/teardown, NAPI setup, and normal netdev operations.

## Risks

- `ice_sf_cfg_netdev()` returns `-ENOMEM` on `register_netdev()` failure instead of the original registration error, which can hide the actual failure reason.
- Deactivation assumes `dyn_port->sf_dev` is valid and does not clear it after uninitialization, so callers must avoid duplicate deactivate paths.
- Probe holds the SF devlink lock while configuring VSI/devlink/netdev resources; future changes must preserve lock ordering with parent devlink and rtnl paths.
- The netdev starts carrier-off and TX queues stopped; link-state notification paths must later transition it or the SF appears present but unusable.
- Error unwinding depends on the exact initialization order. Adding resources in probe requires matching reverse-order cleanup.

## Test Signals

Useful tests include auxiliary activation/deactivation smoke tests, failure injection at VSI config, devlink port creation, netdev registration, and devlink linking, verification that xarray IDs are erased on release, checks that netdev features/XDP capabilities match PF expectations, and lifecycle tests for repeated SF create/remove under devlink.

# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch.c

## Purpose
`ice_eswitch.c` implements the core switchdev/e-switch mode handling for the ice driver. It switches a PF between legacy and switchdev devlink modes, configures the uplink VSI for switchdev forwarding, creates and destroys VF/SF port representors, manages representor metadata destinations, maps Tx/Rx packets between representors and hardware VSIs, and coordinates bridge offload initialization.

## Important APIs, Types, and Functions
- `ice_eswitch_mode_set()` and `ice_eswitch_mode_get()` implement devlink eswitch mode operations.
- `ice_eswitch_enable_switchdev()` sets the uplink VSI and initializes switchdev-specific environment and bridge offloads.
- `ice_eswitch_disable_switchdev()` tears down bridge offloads and restores legacy uplink settings.
- `ice_eswitch_setup_env()` removes default VSI filters, configures software LLDP handling, disables uplink VLAN Rx filtering, installs default RX/TX VSI rules, enables local loopback override, and handles temporary down/up transitions.
- `ice_eswitch_release_env()` reverses switchdev uplink configuration.
- `ice_eswitch_attach_vf()` / `ice_eswitch_attach_sf()` create representors and attach them through the common `ice_eswitch_attach()`.
- `ice_eswitch_detach_vf()` / `ice_eswitch_detach_sf()` locate representors in the PF xarray and detach them through `ice_eswitch_detach()`.
- `ice_eswitch_setup_repr()` allocates a `metadata_dst` with `METADATA_HW_PORT_MUX` and points representor Tx toward the uplink netdev and target VSI number.
- `ice_eswitch_cfg_vsi()` and `ice_eswitch_decfg_vsi()` prepare or restore representee VSIs by clearing/setting antispoofing, adding VLAN zero, and restoring MAC/broadcast filters.
- `ice_eswitch_port_start_xmit()` sends representor-originated SKBs through the uplink with metadata destination set.
- `ice_eswitch_set_target_vsi()` writes switchdev target context into Tx descriptor offload parameters.
- `ice_eswitch_get_target()` maps received descriptor `src_vsi` values back to representor netdevs.
- `ice_eswitch_update_repr()` updates a representor after a VSI changes, including xarray key migration if the VSI number changed.

## Control Flow
Devlink mode changes only mutate `pf->eswitch_mode` and initialize or destroy the representor xarray; actual switchdev hardware setup is lazy and happens when the first representor is attached. VF attach acquires `devl_lock()`, creates a VF representor, and calls `ice_eswitch_attach()`. SF attach creates an SF representor and uses the same common path without the explicit devlink lock in this file.

`ice_eswitch_attach()` exits early in legacy mode. In switchdev mode, if the representor xarray is empty, it enables switchdev hardware state. It stops all representor Tx queues, calls the representor `add` op, sets up metadata destination, inserts the representor into `pf->eswitch.reprs`, stores the caller's representor id, then restarts queues. Error handling unwinds metadata, representor netdev creation, and switchdev environment if no representors remain.

Detach stops queues, removes the representor netdev through its ops, erases the xarray entry, disables switchdev if that was the last representor, releases representor metadata/VSI configuration, destroys the representor, and clears devlink rate topology when no representors remain. Packet Tx from a representor replaces the SKB dst with the stored metadata dst and queues to the lower uplink netdev; Tx from the uplink uses descriptor context to select either a specific VSI or uplink switching behavior.

## State and Persistence Behavior
The file maintains runtime PF state in `pf->eswitch_mode`, `pf->eswitch.is_running`, `pf->eswitch.uplink_vsi`, `pf->eswitch.reprs`, representor `dst`, representor ids, bridge port back-pointers, and VSI filter/security configuration in hardware. Devlink mode persists only as driver runtime state. Hardware filters and VSI settings are changed while switchdev is active and are restored during detach/disable paths.

## Dependencies and Integration Points
This file integrates with devlink eswitch mode APIs, xarray representor storage, ice VSI filter/VLAN/security helpers, LLDP configuration, local loopback update, representor creation/destruction/stat APIs, bridge offload setup from `ice_eswitch_br.c`, Tx offload descriptor definitions, Rx flex descriptor source VSI metadata, and ADQ/VF lifecycle checks. It also interacts with devlink rate topology cleanup when the last representor is detached.

## Risks and Edge Cases
- Mode switching is rejected when VFs exist, but lazy switchdev enable means failures can still occur during representor attach after mode has already been set.
- `ice_eswitch_setup_env()` temporarily downs a running uplink VSI; failure paths must restore filters, VLAN filtering, default VSI rules, local loopback, and interface state correctly.
- `ice_eswitch_update_repr()` updates `repr->br_port->vsi` but not every bridge-port field, so VSI index/id changes can be sensitive for bridge offload users.
- xarray key migration during representor update can erase the old key before a failed insert of the new key, leaving lookup gaps logged only as errors.
- `ice_eswitch_set_target_vsi()` special-cases LLDP when no metadata destination exists; other unmetadataed traffic is marked as uplink switchdev traffic.
- SF attach lacks the explicit `devl_lock()` used by VF attach in this file, so caller-side locking assumptions matter.

## Test Signals
- Devlink tests should cover legacy/switchdev mode get/set, rejection with existing VFs, rejection when ADQ is active, and unknown mode handling.
- Representor lifecycle tests should attach/detach first and last VF/SF representors, including failure injection for representor add, metadata allocation, and xarray insertion.
- Uplink environment tests should validate filter restoration and netdev up/down behavior on all error labels in `ice_eswitch_setup_env()`.
- Packet-path tests should verify representor Tx metadata routing, uplink Tx descriptor target programming, LLDP bypass behavior, and Rx `src_vsi` to representor mapping.
- Bridge integration tests should combine representor attach/detach with bridge offload state and devlink rate topology cleanup.

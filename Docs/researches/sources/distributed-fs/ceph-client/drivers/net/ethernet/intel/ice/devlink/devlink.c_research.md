# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/devlink.c

## Purpose
`devlink.c` implements the PF and SF devlink integration for the Intel ICE Ethernet driver. It exposes device identity and firmware component versions, devlink reload paths, flash update activation, configurable devlink parameters, Tx scheduler topology as devlink-rate objects, and devlink regions for NVM, shadow RAM, and device capabilities.

## Important APIs, Types, And Functions
The local `struct ice_info_ctx` is a per-request scratch object for `devlink info`: it stores a formatting buffer, pending inactive flash component versions, and discovered device capabilities. The `ice_devlink_versions[]` table maps fixed, running, and stored version keys to getter callbacks. `ice_devlink_info_get()` waits for reset quiescence, discovers capabilities, reads pending inactive versions when present, publishes the PCI DSN as serial number, and emits version entries through `devlink_info_version_*` helpers.

Reload support is split across `ice_devlink_reload_down()` and `ice_devlink_reload_up()`. Driver reinit unloads the PF, decfgs the main VSI under RTNL, deinitializes PF/HW/device state, then rebuilds in `ice_devlink_reinit_up()`. Firmware activation checks pending updates and calls `ice_aq_nvm_update_empr()`, then waits for reset completion. `ice_devlink_register_params()` registers RDMA, MSI-X, and optional scheduler/local-forwarding parameters; setters update runtime state, driverinit state, or persistent NVM TLVs depending on the parameter mode.

Scheduler integration includes `ice_devlink_rate_init_tx_topology()`, `ice_traverse_tx_tree()`, node/leaf setter callbacks, and `ice_devlink_set_parent()`. These translate devlink-rate node operations into `ice_sched_*` hardware scheduler operations while caching `struct devlink_rate *` on `struct ice_sched_node`.

## Control Flow
Initialization calls `ice_allocate_pf()` to allocate a devlink with `ice_devlink_ops`, registers via `ice_devlink_register()`, then registers parameters and regions after the PF has capability and flash sizing data. SF allocation uses a nested devlink under the PF devlink. Reload control enters from devlink ops, validates incompatible states such as switchdev, ADQ, or active VFs, then either tears down/rebuilds the PF or triggers EMP reset activation. Region reads and snapshots acquire the NVM semaphore, issue chunked reads, and release the semaphore on every path.

## State And Persistence
Persistent state includes Tx scheduler layer preference stored in an NVM PFA TLV and pending NVM/OROM/netlist versions reported from inactive banks. Runtime state includes `pf->nvm_region`, `pf->sram_region`, `pf->devcaps_region`, `pf->msix.{min,max}`, RDMA protocol bits in `pf->cdev_info`, `pi->local_fwd_mode`, scheduler node rate attributes, and `node->rate_node`. Local forwarding changes schedule a core reset. Tx scheduler layer changes require a PCI slot power cycle.

## Dependencies And Integration Points
This file depends on devlink core APIs, netlink extack, ICE admin queue helpers, NVM helpers, scheduler APIs, eswitch mode handlers, firmware update support, DCB/ADQ checks, RDMA auxiliary device plug/unplug, and SF Ethernet support. It uses definitions from `ice_adminq_cmd.h` for NVM TLV and activation flags, and `ice.h` for PF/VSI state and queue limits.

## Risks And Test Signals
The highest-risk paths are reload unwind ordering, NVM semaphore release on failures, scheduler tree mutation under `pi->sched_lock`, and devlink-rate parent changes that allocate or move hardware scheduler nodes. Useful test signals include `devlink dev info`, `devlink dev reload action driver_reinit`, firmware activation with and without pending updates, parameter get/set for RDMA/MSI-X/local forwarding/scheduler layers, `devlink region new/read`, and devlink-rate node creation and deletion while ADQ/DCB are active or inactive.

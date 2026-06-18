# subset-b-004478 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sched.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sched.c

## Purpose

`ice_sched.c` implements the Intel ice transmit scheduler software database and the firmware AdminQ operations used to build, move, suspend, resume, rate-limit, and replay scheduler topology. It mirrors firmware scheduler elements into `struct ice_sched_node` trees under `struct ice_port_info`, manages VSI and queue-group placement for LAN/RDMA queues, provides aggregator nodes for VSI grouping, and maintains rate-limit profiles for CIR, EIR, and shared bandwidth.

## Important APIs, Types, And Functions

- Firmware command wrappers include `ice_aq_query_sched_elems()`, `ice_aq_add_sched_elems()`, `ice_aq_delete_sched_elems()`, `ice_aq_cfg_sched_elems()`, `ice_aq_move_sched_elems()`, suspend/resume helpers, scheduler resource query, and RL profile add/remove.
- Topology initialization and cleanup are handled by `ice_sched_query_res_alloc()`, `ice_sched_get_psm_clk_freq()`, `ice_sched_init_port()`, `ice_sched_clear_port()`, `ice_sched_cleanup_all()`, and `ice_free_sched_node()`.
- Tree lookup and mutation helpers include `ice_sched_find_node_by_teid()`, `ice_sched_add_node()`, `ice_sched_add_elems()`, `ice_sched_add_nodes_to_layer()`, `ice_sched_move_nodes()`, and `ice_sched_update_parent()`.
- Layer helpers `ice_sched_get_qgrp_layer()`, `ice_sched_get_vsi_layer()`, and `ice_sched_get_agg_layer()` adapt the logical tree to 5/7/9-layer firmware topologies.
- VSI scheduling APIs include `ice_sched_cfg_vsi()`, `ice_sched_get_free_qparent()`, `ice_rm_vsi_lan_cfg()`, and `ice_rm_vsi_rdma_cfg()`.
- Aggregator APIs include `ice_cfg_agg()`, `ice_move_vsi_to_agg()`, `ice_sched_get_agg_node()`, `ice_sched_clear_agg()`, `ice_sched_replay_agg_vsi_preinit()`, `ice_sched_replay_agg()`, and `ice_replay_vsi_agg()`.
- Bandwidth APIs include `ice_cfg_q_bw_lmt()`, `ice_cfg_q_bw_dflt_lmt()`, `ice_cfg_vsi_bw_lmt_per_tc()`, `ice_cfg_vsi_bw_dflt_lmt_per_tc()`, `ice_sched_set_node_bw_lmt()`, `ice_sched_set_node_priority()`, `ice_sched_set_node_weight()`, `ice_cfg_rl_burst_size()`, and `ice_sched_replay_q_bw()`.

## Control Flow

Scheduler setup first queries resource allocation to populate `hw->num_tx_sched_layers`, physical layer count, flattening bitmap, maximum children per layer, and layer capabilities. `ice_sched_init_port()` then fetches firmware default topology for the logical port, creates the root node, inserts every default branch element into the software tree, records the software entry point layer, removes default leaf/intermediate nodes that software should own, marks the port ready, initializes `sched_lock`, and initializes per-layer rate-limit profile lists.

When a VSI is configured, `ice_sched_cfg_vsi()` locates the TC branch and VSI context, optionally suspends an existing VSI node when the TC is disabled, or creates a new VSI path when enabled. It calculates required support nodes from the software entry point to the VSI layer and child nodes from the VSI layer to the queue-group layer, adds nodes through AdminQ, stores queue context arrays, and resumes a suspended node if needed. Queue-parent selection balances queues across queue-group siblings belonging to the same VSI subtree and owner.

Removal walks all traffic classes under `sched_lock`. `ice_sched_rm_vsi_subtree()` refuses to remove a VSI subtree if leaf queue nodes remain, deletes LAN or RDMA-owned child nodes, removes empty VSI nodes, and clears aggregator VSI metadata only after all VSI nodes are gone. The code intentionally does not shrink scheduler nodes when a VSI later requests fewer queues because existing nodes may own rate-limit or shared-rate-limit configuration.

Aggregator control creates an aggregator node at the topology-dependent aggregator layer, with intermediate nodes inserted as needed. Moving a VSI to an aggregator either finds a free parent under the aggregator subtree or creates intermediate nodes, then performs a firmware move and updates the software parent arrays. Removing an aggregator first moves attached VSIs back to the default aggregator and only frees the aggregator subtree when no VSI children remain.

Bandwidth control converts requested Kbps values into firmware RL profile parameters using the PSM clock, profile multipliers, wake-up calculation, and burst size. The code reuses matching profiles per layer/type/bandwidth, tracks profile reference counts, configures scheduler element sections, and removes stale profiles when no longer referenced. Shared bandwidth and EIR are mutually exclusive, so the code clears one path before enabling the other. Replay functions rebuild aggregator membership and restore saved queue/VSI bandwidth after reset.

## State And Persistence

Persistent runtime state is in memory and hardware/firmware, not on disk. `pi->root`, `pi->sib_head`, `pi->sched_node_ids`, and each node's parent/children/sibling fields mirror the scheduler tree. `ice_vsi_ctx->sched` stores per-TC VSI nodes, maximum LAN/RDMA queue counts, queue contexts, and replay bandwidth information. `pi->rl_prof_list[layer]` stores created RL profiles with reference counts. `hw->agg_list` stores aggregator IDs, type, TC bitmaps, replay TC bitmaps, and per-aggregator VSI membership. Firmware state is changed through AdminQ calls; after resets, replay code reconstructs selected software-saved configuration.

## Dependencies And Integration Points

The file depends on `ice_sched.h`, `ice_common.h` types, AdminQ descriptors, `ice_aq_send_cmd()`, register access via `rd32()`, firmware scheduler element formats, Linux list/xarray/mutex primitives, VSI context helpers, and shared driver constants for traffic classes, bandwidth types, queue handles, TEIDs, and scheduler defaults. It is used by VSI setup/teardown, queue configuration, devlink or tc bandwidth controls, reset replay, RDMA queue setup, and aggregator/VSI grouping paths.

## Risks

- Most topology mutations require `pi->sched_lock`; lookup helpers document this but cannot enforce it, so misuse can corrupt parent/child/sibling state.
- `ice_sched_add_elems()` returns immediately on `kzalloc()` failure for a node name after firmware nodes may already have been added, leaving partial topology that callers must unwind via broader cleanup.
- Firmware command success is often checked using both status and returned count; mismatched count paths become `-EIO`, but software state may already be partly updated in multi-node loops.
- Shared-rate-limit layer selection may choose a parent or child of the requested node. The validation requires single-child relationships, so later topology changes can make replay/configuration fail.
- Bandwidth profile reference counts are local bookkeeping. Any missed decrement can leak firmware profiles; any extra decrement could remove a profile still in use.
- Aggregator replay relies on saved bitmaps and enabled TC discovery after reset, so missing TC nodes are silently skipped and logged only at higher replay failures.

## Test Signals

Useful tests include AdminQ-mocked topology initialization for 5/7/9-layer layouts, node add/move/remove checks that validate parent arrays and sibling heads, VSI queue growth tests for LAN and RDMA owners, refusal tests when removing subtrees with leaf nodes, aggregator create/move/remove/replay tests, RL profile reuse/refcount/default-clearing tests, shared-vs-EIR exclusivity tests, burst-size boundary tests, and reset replay tests that verify queue/VSI bandwidth and aggregator membership are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sched.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sched.h

## Purpose

`ice_sched.h` declares the ice transmit scheduler contract shared by scheduler implementation, VSI setup, queue setup, reset replay, and bandwidth/aggregator control code. It defines topology layer constants, burst-size and rate-limit profile math constants, aggregator bookkeeping structures, and public scheduler APIs.

## Important APIs, Types, And Functions

- Layer constants define 5-layer and 9-layer layouts plus offsets for queue-group, VSI, and aggregator layers.
- Burst-size constants encode the 12-bit firmware field, 64-byte versus 1-KB granularity, and accepted minimum/maximum byte ranges.
- Rate-limit constants define profile accuracy, multipliers, fractional encoding, and supported PSM clock frequencies.
- `struct ice_aqc_rl_profile_info` wraps a firmware RL profile element with list linkage, requested bandwidth, and reference count.
- `struct ice_sched_agg_vsi_info` records VSI membership and TC/replay bitmaps for an aggregator.
- `struct ice_sched_agg_info` records aggregator ID/type, member list, active/replay TC bitmaps, and per-TC saved bandwidth type information.
- Prototypes expose firmware scheduler element calls, topology mutation, VSI configuration/removal, aggregator configuration/move/replay, queue/VSI bandwidth limits, burst sizing, and queue bandwidth replay.

## Control Flow

The header has no runtime control flow, but it describes the legal call surface for `ice_sched.c`. Callers initialize scheduler resources, configure VSIs and queues, optionally create aggregators and bandwidth limits, then call replay helpers after reset. Many declared functions require the scheduler lock even where the header does not encode that requirement in the type system.

## State And Persistence

The header defines in-memory state structures used for scheduler persistence across driver reset replay. Aggregator TC bitmaps and bandwidth type information are saved locally, while actual scheduler nodes and rate-limit profiles live in firmware and are rebuilt through the C implementation. No file-backed persistence is involved.

## Dependencies And Integration Points

It includes `ice_common.h` for hardware, port, scheduler node, VSI context, AdminQ, bandwidth, and queue context types. Consumers include core VSI/queue code, SR-IOV and subfunction VSI setup, devlink or tc bandwidth paths, and reset recovery code.

## Risks

- Constants for layer offsets assume firmware topology conventions; new topology layouts require coordinated updates in both header and implementation.
- Public prototypes do not distinguish functions that require `sched_lock` from those that take it internally.
- Aggregator replay state is compact but subtle: active TC bitmaps and replay TC bitmaps have different meanings during reset recovery.
- Burst and RL profile constants must stay aligned with firmware encoding, or valid user bandwidth requests can be rejected or misprogrammed.

## Test Signals

Compile coverage should catch prototype drift. Runtime coverage comes from `ice_sched.c` tests for layer selection, burst-size boundaries, RL profile encoding, aggregator replay, and VSI/queue setup. Static assertions for constants and structure assumptions would be useful if accepted by the driver style.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_eth.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_eth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_eth.h

## Purpose

`ice_sf_eth.h` defines the Ethernet subfunction auxiliary-device data structures and the public activation/driver-registration API used by ice devlink/dynamic-port code.

## Important APIs, Types, And Functions

- `struct ice_sf_dev` embeds `struct auxiliary_device`, points to the owning `struct ice_dynamic_port`, and stores the allocated `struct ice_sf_priv`.
- `struct ice_sf_priv` links the subfunction device to its `struct devlink_port`.
- `ice_adev_to_sf_dev()` converts an auxiliary device back to `struct ice_sf_dev`.
- `ice_sf_driver_register()` and `ice_sf_driver_unregister()` expose auxiliary driver lifecycle.
- `ice_sf_eth_activate()` and `ice_sf_eth_deactivate()` expose dynamic-port Ethernet SF lifecycle.

## Control Flow

The header itself has no runtime control flow. It establishes the type relationship that lets the auxiliary bus call into `ice_sf_eth.c` and lets devlink dynamic-port code request activation or deactivation.

## State And Persistence

The declared structures own runtime pointers only. The auxiliary device lifetime is tied to activation/deactivation, and the embedded devlink port is created during probe and destroyed during remove. No persistent storage is defined.

## Dependencies And Integration Points

It includes `<linux/auxiliary_bus.h>` and `ice.h`, and is consumed by the SF Ethernet implementation plus any ice code that registers the SF driver or activates dynamic Ethernet subfunctions.

## Risks

- `ice_adev_to_sf_dev()` assumes every matching auxiliary device embeds `struct ice_sf_dev`; misuse with a different auxiliary device type would corrupt pointer interpretation.
- Lifetime is pointer-heavy: `ice_sf_dev`, `ice_dynamic_port`, `ice_sf_priv`, and devlink port lifetimes must stay ordered by the C implementation.

## Test Signals

Compile tests catch declaration drift. Runtime validation should come from SF activation/probe/remove tests that confirm `ice_adev_to_sf_dev()` round trips and that `ice_sf_priv` remains valid until remove completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_vsi_vlan_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_vsi_vlan_ops.c

## Purpose

`ice_sf_vsi_vlan_ops.c` initializes VLAN operation callbacks for subfunction VSIs. It selects the outer VLAN operation table in double VLAN mode and the inner VLAN operation table in single VLAN mode, then installs common add/delete VLAN helpers.

## Important APIs, Types, And Functions

- `ice_sf_vsi_init_vlan_ops()` is the only function. It selects `vsi->outer_vlan_ops` when `ice_is_dvm_ena(&vsi->back->hw)` is true, otherwise `vsi->inner_vlan_ops`.
- The installed callbacks are `ice_vsi_add_vlan` and `ice_vsi_del_vlan`.

## Control Flow

The function is a small initialization branch. Callers pass an SF VSI after its PF/backpointer is available. The function checks VLAN mode through the hardware object and writes the add/delete function pointers into the selected operation table.

## State And Persistence

State is limited to function pointers in `struct ice_vsi_vlan_ops` embedded in the VSI. There is no hardware programming and no persistence beyond the VSI lifetime; later VLAN add/delete requests use the installed callbacks.

## Dependencies And Integration Points

The file depends on `ice_vsi_vlan_ops.h`, `ice_vsi_vlan_lib.h`, `ice_vlan_mode.h`, `ice.h`, and its own header. It integrates with subfunction VSI initialization and common ice VLAN add/delete logic.

## Risks

- Only add/delete callbacks are installed here. If the broader VLAN ops table expects other callbacks for SF VSIs, they must be initialized elsewhere or guarded by callers.
- Correct inner-vs-outer selection depends entirely on `ice_is_dvm_ena()` matching the current hardware VLAN mode before VLAN operations are used.

## Test Signals

Tests should instantiate SF VSI-like objects in DVM and SVM modes and verify the selected operation table and function pointers. Integration tests should add and delete VLANs on an SF netdev in both VLAN modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_vsi_vlan_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_vsi_vlan_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_vsi_vlan_ops.h

## Purpose

`ice_sf_vsi_vlan_ops.h` declares the subfunction VSI VLAN operation initializer used by SF VSI setup code.

## Important APIs, Types, And Functions

- Includes `ice_vsi_vlan_ops.h` for the VLAN operation table contract.
- Forward-declares `struct ice_vsi`.
- Declares `ice_sf_vsi_init_vlan_ops(struct ice_vsi *vsi)`.

## Control Flow

The header has no runtime control flow. It exposes a single initialization hook implemented in `ice_sf_vsi_vlan_ops.c`.

## State And Persistence

The header owns no state. Its declared function mutates runtime VSI VLAN operation pointers when called.

## Dependencies And Integration Points

It is consumed by subfunction VSI setup paths and depends on the common ice VLAN operation type definitions.

## Risks

- The include guard name uses `_ICE_SF_VSI_VLAN_OPS_H_`, matching the file purpose. Any future split between SF-specific and generic VSI VLAN ops should keep this declaration unambiguous.
- Because only a forward declaration of `struct ice_vsi` is present, callers must include fuller VSI definitions before dereferencing VSI fields.

## Test Signals

Compile coverage validates the declaration. Runtime coverage is provided by the C file tests that verify callback initialization in DVM and SVM modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_vsi_vlan_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sriov.c

## Purpose

`ice_sriov.c` implements SR-IOV support for the ice PF driver. It enables and disables VFs, allocates per-VF queue/MSI-X resources, creates VF VSI resources, maps interrupts and queues into VF PCI-visible registers, handles VF resets and VFLR events, exposes netdev VF administration operations, supports per-VF MSI-X resizing, processes VF LAN overflow/MDD events, and restores VF MSI state after PF FLR.

## Important APIs, Types, And Functions

- VF lifecycle helpers include `ice_create_vf_entries()`, `ice_free_vf_entries()`, `ice_init_vf_vsi_res()`, `ice_start_vfs()`, `ice_free_vf_res()`, and `ice_free_vfs()`.
- SR-IOV enable/configuration entry points include `ice_sriov_configure()`, `ice_pci_sriov_ena()`, `ice_ena_vfs()`, `ice_check_sriov_allowed()`, and `ice_sriov_get_vf_total_msix()`.
- Mapping helpers include `ice_ena_vf_msix_mappings()`, `ice_ena_vf_q_mappings()`, `ice_ena_vf_mappings()`, `ice_dis_vf_mappings()`, and `ice_calc_vf_reg_idx()`.
- VF reset operations are collected in `ice_sriov_vf_ops`: clear reset state, clear mailbox registers, trigger reset, poll reset status, clear reset trigger, free, and post-VSI-rebuild.
- Event paths include `ice_process_vflr_event()`, `ice_vf_lan_overflow_event()`, `ice_print_vf_rx_mdd_event()`, `ice_print_vf_tx_mdd_event()`, and `ice_print_vfs_mdd_events()`.
- VF admin netdev hooks include `ice_set_vf_spoofchk()`, `ice_get_vf_cfg()`, `__ice_set_vf_mac()`, `ice_set_vf_mac()`, `ice_set_vf_trust()`, `ice_set_vf_link_state()`, `ice_set_vf_bw()`, `ice_get_vf_stats()`, and `ice_set_vf_port_vlan()`.
- Dynamic VF resource sizing is handled by `ice_sriov_set_msix_vec_count()` and `ice_sriov_remap_vectors()`.

## Control Flow

The sysfs SR-IOV path enters `ice_sriov_configure()`, which validates PF capability, safe-mode state, and nominal PF readiness. A request for zero VFs frees resources unless VFs are assigned to VMs. A positive request enters `ice_pci_sriov_ena()` and `ice_ena_vfs()`: OICR interrupt handling is temporarily disabled, PCI SR-IOV is enabled, the VF table lock is taken, per-VF vectors and queues are computed from available common MSI-X and queue resources, VF entries are allocated into the RCU hash table, and each VF is started by clearing reset triggers, allocating IRQs, creating a VF VSI, initializing host config, attaching to eswitch, enabling mappings, and setting `VFGEN_RSTAT` active.

Teardown uses `ice_free_vfs()`. It serializes with `ICE_VF_DIS`, disables PCI SR-IOV when VFs are not assigned, walks the VF table under lock, detaches each VF from eswitch, disables queues, frees virtual IRQs, disables mappings, releases control/LAN VSI resources, clears MDD/promisc state, optionally clears VFLR status bits, removes all VF hash entries, and clears PF SR-IOV flags.

VF reset handling is split between generic VF library orchestration and SR-IOV register operations provided through `ice_sriov_vf_ops`. Software resets write `VPGEN_VFRTRIG`; VFLR cleanup clears `GLGEN_VFLRSTAT`, polls PCI transaction pending status, clears mailbox registers, polls `VPGEN_VFRSTAT`, and re-enables mappings after VSI rebuild.

Netdev VF admin calls acquire a VF reference by ID, validate readiness, often take `vf->cfg_lock`, update stored VF state, and either apply immediately to the VSI or reset/notify the VF so virtchnl resource discovery picks up the change. Bandwidth configuration rejects min-rate with DCB enabled, prevents aggregate min-rate oversubscription against current link speed, and delegates scheduler programming to VSI min/max bandwidth helpers. Port VLAN configuration validates VLAN ID/QoS/protocol and resets the VF after updating `vf->port_vlan_info`.

## State And Persistence

VF state is runtime driver and hardware state. `pf->vfs.table` stores `struct ice_vf` objects protected by `pf->vfs.table_lock` with RCU lookup and kref lifetime. `pf->vfs.num_qps_per` and `pf->vfs.num_msix_per` store default allocation. Per-VF fields track VF ID, PCI VF device, VSI indexes, vector range, queue count, MAC state, spoof check, trust, link override, bandwidth, port VLAN, MDD counters, and state bits such as initialized, disabled, active, and promiscuous. Hardware persistence is through PCI SR-IOV capability, queue mapping registers, interrupt mapping registers, mailbox/reset registers, and VF reset status registers. No on-disk persistence is used.

## Dependencies And Integration Points

The file depends on core ice PF/VSI libraries, VF library private helpers, interrupt tracker helpers, eswitch attach/detach, virtchnl state/notification, flow director VF support, VLAN mode and VF VLAN ops, DCB link-speed helpers, firmware AQ event structures, PCI SR-IOV APIs, RCU/kref locking, and netdev VF rtnl operations. It is integrated with PF probe/remove, sysfs `sriov_numvfs`, VF mailbox/reset handling, netdev `.ndo_set_vf_*` hooks, MDD handling, and PF FLR recovery.

## Risks

- Enable and teardown paths are highly order-dependent: PCI SR-IOV, VF hash entries, VSI resources, eswitch attachment, interrupts, queue mappings, and reset status must unwind in the exact reverse order on failure.
- Several operations assume contiguous Tx/Rx queue mapping; scattered VF queue mapping logs errors and is not implemented.
- VF lifetime uses RCU plus krefs; missing `ice_put_vf()` or using a VF after dropping locks can lead to leaks or use-after-free.
- `ice_sriov_set_msix_vec_count()` remaps idle VFs to compact IRQ usage and rebuilds the target VSI; partial failure has a fallback path but still depends on IRQ availability for the old vector count.
- Bandwidth min-rate validation uses current link speed and current VF accounting; link changes after configuration can make prior allocations oversubscribed.
- Trust is rejected in switchdev mode, while other VF settings still operate; behavior must stay aligned with eswitch security expectations.
- VF reset and VFLR paths write hardware registers directly and rely on short polling loops; slow or wedged hardware can leave VF state inconsistent despite logs.

## Test Signals

Useful tests include SR-IOV enable/disable with varied VF counts and resource scarcity, failure injection for VF entry allocation/VSI setup/eswitch attach/IRQ allocation, assigned-VF teardown rejection, VFLR event handling, VF MSI-X resize success and rollback, spoof check/MAC/trust/link/VLAN/bandwidth netdev operation tests, min-rate oversubscription tests, DCB-enabled min-rate rejection, LAN overflow event mapping to VF reset, MDD log rate-limiting checks, and PF FLR MSI-state restore tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sriov.h

## Purpose

`ice_sriov.h` declares the SR-IOV interface used by the ice driver and provides no-op or `-EOPNOTSUPP` stubs when `CONFIG_PCI_IOV` is disabled. It also defines VF register constants, polling constants, and VF resource sizing limits shared with SR-IOV implementation and callers.

## Important APIs, Types, And Functions

- Register/status constants include `VF_DEVICE_STATUS`, `VF_TRANS_PENDING_M`, `ICE_PCI_CIAD_WAIT_COUNT`, and `ICE_PCI_CIAD_WAIT_DELAY_US`.
- VF resource constants define minimum queue pairs, non-queue MSI-X vector count, common MSI-X sizing tiers, minimum interrupt count, and VF reset retry/sleep limits.
- When PCI IOV is enabled, declarations cover VF lifecycle, SR-IOV configure, MAC/VLAN/bandwidth/trust/link/spoof/stat netdev hooks, VFLR handling, LAN overflow handling, MDD reporting, MSI restoration, MSI-X resource sysfs hooks, virtchnl pattern validation, and single Tx queue disable.
- When PCI IOV is disabled, inline stubs preserve call sites while returning unsupported or doing nothing.

## Control Flow

The header has compile-time control flow through `#ifdef CONFIG_PCI_IOV`. Enabled builds call real SR-IOV implementation in `ice_sriov.c` and related VF files. Disabled builds compile callers against stubbed operations that cannot enable or administer VFs.

## State And Persistence

The header does not own state. It defines constants used for VF resource allocation and reset polling, and prototypes for functions that mutate PF/VF runtime and hardware state.

## Dependencies And Integration Points

It includes `virt/fdir.h`, `ice_vf_lib.h`, and `virt/virtchnl.h`, and exposes entry points to PCI/sysfs SR-IOV, netdev VF administration, VF reset handling, MDD reporting, VF queue control, and virtchnl validation code.

## Risks

- Disabled-build stubs must match real signatures. Signature drift can break non-IOV builds or hide missing call-site guards.
- Resource constants encode policy for MSI-X and queue sizing; changing them affects VF capability advertised to guest drivers.
- Functions declared here span several subsystems, so include-order or type-dependency changes can have broad build impact.

## Test Signals

Build testing should cover both `CONFIG_PCI_IOV=y` and disabled configurations. Runtime tests for enabled builds should exercise every declared netdev VF hook, SR-IOV sysfs configuration, VFLR processing, MDD logging, MSI restore, MSI-X resize, and queue-disable integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sriov.h -->

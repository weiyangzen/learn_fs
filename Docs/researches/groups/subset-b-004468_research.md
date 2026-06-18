# subset-b-004468 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dpll.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dpll.c

## Purpose
`ice_dpll.c` implements Intel ice driver integration with the Linux DPLL subsystem. It discovers DPLL/CGU capabilities, registers EEC and PPS DPLL devices and their pins, exposes pin control callbacks through `struct dpll_device_ops` and `struct dpll_pin_ops`, handles SMA/U.FL software-controlled wrapper pins, supports recovered clock (`rclk`) pin-on-pin topology, polls hardware state, and emits DPLL netlink notifications when lock state, active input, or phase offset changes. The file has two major hardware paths: E810-style CGU-owned DPLLs and E825C generic-3K hardware where recovered clock parents can come from firmware-described fwnode pins.

## Important APIs, Types, and Functions
- Local type `enum ice_dpll_pin_type` classifies input, output, recovered-clock input, and software-controlled pins so common callbacks can route to the correct AdminQ command.
- `ice_dpll_is_sw_pin()` hides raw CGU pins that are represented to userspace as logical SMA/U.FL software pins.
- Frequency APIs are implemented by `ice_dpll_pin_freq_set()`, `ice_dpll_frequency_set()`, input/output wrappers, and software-pin wrappers that redirect to the currently active backing input or output pin.
- State APIs are implemented by `ice_dpll_pin_enable()`, `ice_dpll_pin_disable()`, `ice_dpll_pin_state_update()`, `ice_dpll_pin_state_set()`, and input/output/SMA/U.FL/recovered-clock wrappers.
- Priority APIs are implemented by `ice_dpll_hw_input_prio_set()`, `ice_dpll_input_prio_get/set()`, and software-pin priority wrappers.
- Phase APIs include `ice_dpll_pin_phase_adjust_get/set()`, `ice_dpll_phase_offset_get()`, `ice_dpll_is_pps_phase_monitor()`, and `ice_dpll_pps_update_phase_offsets()`.
- Embedded-sync and reference-sync APIs are implemented by `ice_dpll_input_esync_get/set()`, `ice_dpll_output_esync_get/set()`, software wrappers, `ice_dpll_input_ref_sync_get/set()`, `ice_dpll_init_ref_sync_inputs()`, and reference-sync registration.
- Recovered-clock support uses `ice_dpll_rclk_update()`, `ice_dpll_rclk_update_e825c()`, `ice_dpll_synce_update_e825c()`, and `ice_dpll_rclk_state_on_pin_get/set()`.
- DPLL registration uses `ice_dpll_init_dpll()`, `ice_dpll_deinit_dpll()`, `ice_dpll_init_pins()`, `ice_dpll_deinit_pins()`, `ice_dpll_init_rclk_pin()`, `ice_dpll_init_direct_pins()`, `ice_dpll_register_pins()`, and `ice_dpll_release_pins()`.
- E825C fwnode pin support uses `ice_dpll_pin_node_get()`, `ice_dpll_init_fwnode_pin()`, `ice_dpll_pin_notify()`, and `ice_dpll_pin_notify_work()`.
- Public entry points are `ice_dpll_init()` and `ice_dpll_deinit()`, gated by `CONFIG_PTP_1588_CLOCK` in the header.

## Control Flow
Initialization starts at `ice_dpll_init()`, dispatching E825 hardware to `ice_dpll_init_e825()` and other hardware to `ice_dpll_init_e810()`. E810 initialization creates the DPLL mutex, reads CGU abilities with `ice_aq_get_cgu_abilities()`, allocates input/output/priority arrays, initializes pin metadata, registers DPLL devices, registers pins and pin-on-pin recovered clock relationships, and starts a periodic kthread worker when the PF owns CGU support. E825 initialization focuses on fwnode parent pins and recovered clock registration, uses a completion to coordinate notifier work, and sets `ICE_FLAG_DPLL` only after successful setup.

At runtime, userspace DPLL netlink callbacks enter the registered ops tables. Most setters reject operations during PF reset through `ice_dpll_is_reset()`, acquire `pf->dplls.lock`, issue a CGU AdminQ or register-level command, update cached pin state, then release the lock. Software SMA/U.FL callbacks first update the PCA9575 SMA control register, then enable or disable the backing CGU input/output pin and notify the paired logical pin because one physical routing change can affect two exposed pins.

Periodic monitoring runs through `ice_dpll_periodic_work()`. It skips polling during reset, locks the DPLL state, updates EEC and PPS state with `ice_dpll_update_state()`, optionally reads PPS phase offset measurements, unlocks, emits device/pin notifications, and reschedules at 500 ms or 10 ms on transient update failure. After too many consecutive CGU acquisition failures it disables further periodic work.

Deinitialization clears `ICE_FLAG_DPLL`, stops the worker for CGU-owned devices, unregisters pin relationships, releases DPLL pins/devices, frees allocated arrays, and destroys the mutex. E825 fwnode deinit unregisters notifiers, flushes workqueue work, drops fwnode pin references, and destroys the single-thread workqueue.

## State and Persistence Behavior
The file maintains runtime-only driver state in `pf->dplls`, including cached input/output pin arrays, SMA/U.FL logical pin structures, recovered-clock pin state, DPLL indices, input priorities, current and previous active input, current and previous lock status, phase offsets, and periodic worker counters. Hardware configuration persists in device CGU state via AdminQ commands and CGU/SMA control registers, but the driver-side cache is rebuilt at probe/init. `ICE_FLAG_DPLL` is the primary initialized-state flag; `dpll_init` completion coordinates asynchronous fwnode notifier work. There is no disk persistence.

## Dependencies and Integration Points
This file depends on Linux DPLL APIs (`dpll_device_get/register/put`, `dpll_pin_get/register`, `dpll_pin_on_pin_register`, notifications, fwnode lookup), kernel work/kthread primitives, PCI DSN clock-id generation, fwnode properties, netdevice pin association, and the ice AdminQ/CGU helpers (`ice_aq_get_cgu_abilities`, `ice_aq_get/set_input_pin_cfg`, `ice_aq_get/set_output_pin_cfg`, `ice_get_cgu_state`, `ice_aq_get_cgu_input_pin_measure`, `ice_get_cgu_rclk_pin_info`, PHY recovered clock commands, E825C TSPLL helpers, SMA control helpers). It integrates with PF reset state, PTP port metadata, device IDs/mac types, and trace/debug logging.

## Risks and Edge Cases
- Many callbacks rely on cached `pin->flags`, `pin->freq`, and state arrays being refreshed before writes; stale cache can preserve or clear the wrong hardware bits.
- Error unwinding must maintain balanced DPLL pin/device reference counts, especially around partial pin registration and fwnode pin discovery.
- Software SMA/U.FL routing is subtle: a change to one logical pin can disable or activate a paired logical pin, so missing peer notifications or backing-pin updates can mislead userspace.
- E825C recovered-clock support depends on firmware fwnode names (`rclk0`, `rclk1`) and asynchronous DPLL pin create/delete notifiers; initialization ordering races are mitigated by the completion but remain a test-sensitive path.
- The periodic worker disables itself after `ICE_CGU_STATE_ACQ_ERR_THRESHOLD`; transient firmware/AdminQ failures above the threshold leave userspace with stale DPLL state until reinit.
- Several init paths allocate arrays sequentially; early allocation failures rely on later cleanup through `ice_dpll_deinit_info()`, so leak testing should cover all failure labels.
- `ice_dpll_init_info_sw_pins()` writes SMA control defaults during initialization, which changes hardware routing state and can surprise systems expecting firmware defaults.

## Test Signals
- Build with `CONFIG_PTP_1588_CLOCK` and DPLL subsystem enabled, including switch coverage for E810 and E825C mac types.
- Probe/remove and reset-cycle tests should verify no DPLL device/pin references leak and `ICE_FLAG_DPLL` is correct.
- DPLL netlink tests should exercise frequency, state, priority, phase adjust, phase offset monitor, embedded sync, and reference sync get/set paths.
- Hardware or mocked AdminQ tests should inject failures in CGU ability reads, pin get/set commands, DPLL registration, pin registration, fwnode lookup, and worker state polling to validate unwinding.
- SMA/U.FL tests should verify direction/state transitions, paired-pin notifications, active/inactive reporting, and backing pin enable/disable behavior.
- Recovered-clock tests should cover both AdminQ PHY recovered clock output and E825C SynCE bypass-mux programming, including parent pin on/off state queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dpll.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dpll.h

## Purpose
`ice_dpll.h` declares the driver-private DPLL data model and public DPLL initialization hooks for the Intel ice driver. It defines CGU/SynCE register bitfields, software pin indexing, per-pin state containers, per-DPLL device containers, and the aggregate `struct ice_dplls` stored on the PF.

## Important APIs, Types, and Functions
- `ICE_DPLL_RCLK_NUM_MAX` bounds recovered clock parent state arrays to four entries.
- `ICE_CGU_R10`, `ICE_CGU_R11`, and related masks describe SynCE recovered clock selection/divider/reset fields used by the E825C path in `ice_dpll.c`.
- `ICE_CGU_BYPASS_MUX_OFFSET_E825C` maps E825C port numbers into bypass mux selector values.
- `enum ice_dpll_pin_sw` defines the two software-controlled logical pin slots shared by SMA and U.FL arrays.
- `struct ice_dpll_pin_work` carries DPLL pin create/delete notifier work into the single-thread workqueue.
- `struct ice_dpll_pin` stores the Linux `dpll_pin`, PF back pointer, reference tracker, fwnode/notifier fields, hardware index, parent map, cached flags/state/frequency/phase data, logical software-pin backing input/output pointers, direction, status, ref-sync mapping, and visibility flags.
- `struct ice_dpll` stores one DPLL device instance, including Linux `dpll_device`, PF back pointer, reference tracker, hardware DPLL index, active input indices, cached lock mode/status, priorities, phase offset monitor period, active/previous input pins, and registered ops pointer.
- `struct ice_dplls` aggregates the DPLL subsystem state on a PF: kthread worker, delayed work, software workqueue, mutex, initialization completion, EEC/PPS DPLLs, input/output/SMA/U.FL/rclk pins, counts, CGU metadata, phase limits, periodic counter, and generic pin layout flag.
- Public functions `ice_dpll_init()` and `ice_dpll_deinit()` are real declarations when `CONFIG_PTP_1588_CLOCK` is enabled and inline no-ops otherwise.

## Control Flow
The header itself has no executable control flow beyond the `CONFIG_PTP_1588_CLOCK` compile-time gate. Runtime control flow is defined by consumers in `ice_dpll.c`, which allocate and fill the structures declared here during PF initialization, expose them through DPLL netlink callbacks, and free them during PF teardown.

## State and Persistence Behavior
All structures define in-memory PF lifetime state. Cached values mirror hardware CGU state and DPLL subsystem registrations but are not persisted to disk. Register masks describe persistent hardware registers, while the struct fields track current driver ownership and cached observations until deinit or reset.

## Dependencies and Integration Points
The header includes `ice.h` and depends on kernel DPLL types such as `struct dpll_pin`, `struct dpll_device`, `dpll_tracker`, `struct dpll_pin_properties`, `enum dpll_pin_direction`, `enum dpll_lock_status`, and `enum dpll_mode`. It also depends on kernel workqueue, completion, mutex, fwnode, and notifier types through included driver/kernel headers. It is consumed by the ice PF initialization/teardown path and DPLL implementation.

## Risks and Edge Cases
- Fixed-size arrays such as `parent_idx`, `flags`, and `state` must remain consistent with hardware parent counts; callers must validate counts before indexing.
- `struct ice_dpll_pin` has multiple ownership modes: direct DPLL pin, hidden backing pin, logical software pin, and fwnode parent pin. Misinterpreting those fields can lead to double unregisters or missed reference drops.
- Inline no-op behavior when PTP clock support is disabled means callers must not assume DPLL side effects exist in all builds.
- The `generic` flag in `struct ice_dplls` affects whether software pins and output pin resources are registered; future code must preserve that distinction.

## Test Signals
- Compile both with and without `CONFIG_PTP_1588_CLOCK` to verify call sites tolerate real and no-op DPLL hooks.
- Static analysis should focus on array bounds for `ICE_DPLL_RCLK_NUM_MAX`, `num_parents`, and DPLL index-based `state[]` access.
- Probe/remove tests should verify every tracked `dpll_tracker` and fwnode reference is balanced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch.c -->
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
- `ice_eswitch_update_repr()` updates `repr->br_port->vsi` but does not update every bridge-port field, so VSI index/id changes can be sensitive for bridge offload users.
- xarray key migration during representor update can erase the old key before a failed insert of the new key, leaving lookup gaps logged only as errors.
- `ice_eswitch_set_target_vsi()` special-cases LLDP when no metadata destination exists; other unmetadataed traffic is marked as uplink switchdev traffic.
- SF attach lacks the explicit `devl_lock()` used by VF attach in this file, so caller-side locking assumptions matter.

## Test Signals
- Devlink tests should cover legacy/switchdev mode get/set, rejection with existing VFs, rejection when ADQ is active, and unknown mode handling.
- Representor lifecycle tests should attach/detach first and last VF/SF representors, including failure injection for representor add, metadata allocation, and xarray insertion.
- Uplink environment tests should validate filter restoration and netdev up/down behavior on all error labels in `ice_eswitch_setup_env()`.
- Packet-path tests should verify representor Tx metadata routing, uplink Tx descriptor target programming, LLDP bypass behavior, and Rx `src_vsi` to representor mapping.
- Bridge integration tests should combine representor attach/detach with bridge offload state and devlink rate topology cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch.h

## Purpose
`ice_eswitch.h` declares the public switchdev/e-switch interface used by the rest of the ice driver. It exposes representor attach/detach, devlink eswitch mode operations, packet-path helpers, representor update, queue control, and VSI switchdev configuration helpers, with compile-time stubs when `CONFIG_ICE_SWITCHDEV` is disabled.

## Important APIs, Types, and Functions
- VF/SF lifecycle: `ice_eswitch_attach_vf()`, `ice_eswitch_detach_vf()`, `ice_eswitch_attach_sf()`, and `ice_eswitch_detach_sf()`.
- Devlink mode: `ice_eswitch_mode_get()`, `ice_eswitch_mode_set()`, and `ice_is_eswitch_mode_switchdev()`.
- Representor maintenance: `ice_eswitch_update_repr()` and `ice_eswitch_stop_all_tx_queues()`.
- Packet path: `ice_eswitch_set_target_vsi()`, `ice_eswitch_port_start_xmit()`, and `ice_eswitch_get_target()`.
- VSI setup/restore: `ice_eswitch_cfg_vsi()` and `ice_eswitch_decfg_vsi()`.
- Disabled-build stubs return no-op behavior, `-EOPNOTSUPP`, `NETDEV_TX_BUSY`, legacy mode semantics, or original Rx netdev fallback depending on call role.

## Control Flow
The header is a compile-time dispatch layer. When `CONFIG_ICE_SWITCHDEV` is enabled, call sites bind to the implementations in `ice_eswitch.c`. When disabled, the inline stubs keep non-switchdev builds linkable and force callers into legacy/no-op behavior. The notable disabled-build `ice_eswitch_mode_get()` stub returns `DEVLINK_ESWITCH_MODE_LEGACY` directly rather than writing through its `mode` pointer, which means call sites must match expected usage carefully.

## State and Persistence Behavior
The header owns no runtime state. It constrains possible state transitions by making switchdev operations unavailable in non-switchdev builds. Runtime state lives in PF/eswitch/representor structures managed by the implementation.

## Dependencies and Integration Points
It includes `<net/devlink.h>` and `devlink/port.h`, and relies on declarations for `struct ice_pf`, `struct ice_vf`, `struct ice_dynamic_port`, `struct ice_vsi`, `struct ice_tx_offload_params`, `struct ice_rx_ring`, `struct sk_buff`, `struct net_device`, and ice Rx descriptor types from surrounding headers. It is included by PF, VF, SF, Tx, Rx, devlink, and representor code that needs to remain buildable without switchdev.

## Risks and Edge Cases
- Disabled-build stubs must preserve caller expectations. Any caller expecting `ice_eswitch_mode_get(devlink, &mode)` to write `mode` in all builds would be wrong for the current stub.
- Stub return values intentionally differ by operation; attach returns unsupported, detach is no-op, representor Tx reports busy, and Rx target returns the physical netdev.
- New switchdev APIs must add matching stubs or non-switchdev builds will fail.

## Test Signals
- Compile with `CONFIG_ICE_SWITCHDEV=y` and disabled to validate both declaration and stub paths.
- Static checks should ensure callers handle `-EOPNOTSUPP` from attach/config helpers and do not depend on side effects from disabled stubs.
- Packet-path build tests should verify non-switchdev Rx fallback and Tx busy behavior do not break callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch_br.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch_br.c

## Purpose
`ice_eswitch_br.c` implements switchdev bridge offload support for ice e-switch mode. It tracks one offloaded bridge per e-switch, links PF uplink and port representor netdevs as bridge ports, offloads FDB entries into hardware advanced switch rules, handles bridge VLAN objects and attributes, ages dynamic FDB entries, and coordinates switchdev/netdev notifier lifetimes.

## Important APIs, Types, and Functions
- `ice_eswitch_br_offloads_init()` allocates bridge offload state, creates an ordered workqueue, registers switchdev and netdev notifiers, and starts delayed FDB ageing work.
- `ice_eswitch_br_offloads_deinit()` cancels delayed work, unregisters notifiers, destroys the workqueue, and deallocates bridge state under RTNL.
- `ice_eswitch_br_is_dev_valid()` accepts only ice PF netdevs, representors, and LAG masters.
- `ice_eswitch_br_netdev_to_port()` maps representor/PF/LAG netdevs to `struct ice_esw_br_port`.
- `ice_eswitch_br_port_link()` / `ice_eswitch_br_port_unlink()` handle bridge membership changes from `NETDEV_CHANGEUPPER`.
- `ice_eswitch_br_init()`, `ice_eswitch_br_get()`, `ice_eswitch_br_deinit()`, and `ice_eswitch_br_verify_deinit()` manage the single bridge object.
- `ice_eswitch_br_fdb_entry_create()`, `ice_eswitch_br_fdb_entry_find_and_delete()`, `ice_eswitch_br_fdb_flush()`, and cleanup helpers maintain FDB state.
- `ice_eswitch_br_flow_create()` creates a paired forward rule and guard rule for each FDB entry; `ice_eswitch_br_flow_delete()` removes both.
- `ice_eswitch_br_fwd_rule_create()` and `ice_eswitch_br_guard_rule_create()` build hardware advanced-rule lookup/action data for MAC and optional VLAN.
- `ice_eswitch_br_switchdev_event()` handles async FDB add/delete events by queueing `ice_eswitch_br_fdb_event_work()`.
- `ice_eswitch_br_event_blocking()` handles switchdev blocking object/attribute operations for VLAN add/delete, VLAN filtering, and ageing time.
- VLAN helpers include `ice_eswitch_br_vlan_filtering_set()`, `ice_eswitch_br_port_vlan_add()`, `ice_eswitch_br_port_vlan_del()`, `ice_eswitch_br_vlan_create()`, `ice_eswitch_br_set_pvid()`, and cleanup/flush helpers.
- `ice_eswitch_br_update_work()` runs periodic ageing of non-user FDB entries.

## Control Flow
Bridge offloads are initialized when switchdev mode is enabled by the e-switch core. Init allocates `pf->eswitch.br_offloads`, registers three notifier paths, and schedules periodic update work. Netdev upper-change notifications link or unlink valid devices to a Linux bridge. Link either creates the single bridge object for the bridge ifindex or reuses it, then creates an uplink bridge port for PF/LAG devices or a VF representor bridge port for representors. Unlink verifies the device belongs to the bridge, deinitializes the port, and destroys the bridge if it has no ports.

Switchdev FDB notifications are filtered for bridge upper devices and valid ice devices. FDB add/delete work is copied into an allocated work item because the notifier path may be atomic; the ordered workqueue later takes RTNL, maps the netdev to a bridge port, and creates or deletes the FDB entry. FDB creation optionally validates VLAN metadata, replaces existing entries, allocates an entry, creates hardware forward and guard rules, inserts the entry into the rhashtable and list, and sends switchdev offload notifications.

Blocking switchdev handlers process VLAN add/delete and bridge attributes synchronously. VLAN filtering changes flush the FDB before toggling the bridge flag. VLAN add supports trunk VLANs or a port VLAN/PVID mode with simultaneous PVID and untagged flags; port VLAN on the uplink is rejected. Periodic delayed work takes RTNL, removes non-user FDB entries whose `last_use + ageing_time` has expired, and reschedules itself every second.

## State and Persistence Behavior
All state is runtime-only. `pf->eswitch.br_offloads` points to the offload container. `br_offloads->bridge` tracks the single bridge, including `ifindex`, flags, ageing time, `ports` xarray, `fdb_ht` rhashtable, and `fdb_list`. Each bridge port records VSI pointer/index, type, representor id, PVID, and VLAN xarray. Each FDB entry stores MAC/VID key data, owning netdev, bridge port, hardware rule pair, user-added flag, and `last_use`. Hardware advanced rules persist in device state while entries exist and are explicitly deleted during cleanup.

## Dependencies and Integration Points
This file depends on Linux switchdev notifiers, blocking switchdev handlers, netdevice upper/lower APIs, bridge/VLAN object definitions, LAG master detection, RTNL locking, workqueues, xarrays, rhashtable, jiffies ageing helpers, and switchdev FDB notifications. It integrates with ice representors (`ice_netdev_to_repr`, `repr->br_port`), PF uplink netdevs (`ice_netdev_to_pf`, `pf->br_port`), ice switch advanced rules (`ice_add_adv_rule`, `ice_rem_adv_rule_by_id`), VLAN operations, VF port VLAN helpers, and tracepoints.

## Risks and Edge Cases
- Only one bridge is supported per e-switch; attempts to link ports to a different bridge return `-EOPNOTSUPP`.
- LAG support picks the first lower ice device; absence of an ice lower device returns no port or no-op link behavior.
- Dynamic FDB ageing uses `last_use` set at creation and is not refreshed in this file, so offloaded dynamic entries age based on driver-observed creation time unless another path updates it.
- VLAN filtering flushes the entire FDB, which is correct for lookup semantics but disruptive.
- Untagged filtering without VLAN filtering is not supported; FDB entries with VID are ignored in that mode.
- PVID/untagged VLAN push/pop is only supported together and not on uplink ports; partial flag combinations return `-EOPNOTSUPP`.
- FDB creation replaces existing entries before allocating and installing the new one; if new hardware rule creation fails, the old entry is already gone.
- Workqueue/notifier teardown relies on unregistering notifiers, destroying the queue, and taking RTNL to wait for in-progress events; ordering is critical to avoid use-after-free.

## Test Signals
- Switchdev bridge tests should link/unlink PF uplink, representors, and LAG masters; verify one-bridge-only enforcement and bridge destruction when last port leaves.
- FDB tests should add/delete user and dynamic entries with and without VLAN filtering, validate hardware forward/guard rule creation and deletion, and verify switchdev offload notifications.
- VLAN tests should cover trunk VLAN add/delete, duplicate VLAN updates, PVID+untagged success on representor ports, PVID-only or untagged-only rejection, uplink PVID rejection, and FDB flush on VLAN filtering toggles.
- Ageing tests should set bridge ageing time and verify non-user entries are removed while user-added entries are retained.
- Failure injection should cover allocation failures, rhashtable insertion failure, advanced rule add/delete failures, notifier registration failure labels, and workqueue allocation failure.
- Concurrency tests should stress FDB events during bridge unlink and offload deinit under RTNL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch_br.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch_br.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch_br.h

## Purpose
`ice_eswitch_br.h` declares the private data structures and entry points for ice switchdev bridge offloads. It models FDB keys, hardware rule pairs, FDB entries, bridge ports, the bridge object, bridge offload notifier container, queued FDB work, and VLAN metadata.

## Important APIs, Types, and Functions
- `struct ice_esw_br_fdb_data` is the rhashtable key: destination MAC address and VLAN ID.
- `struct ice_esw_br_flow` stores the two hardware rule handles associated with an FDB entry: forwarding rule and guard rule.
- `ICE_ESWITCH_BR_FDB_ADDED_BY_USER` distinguishes static/user FDB entries from dynamic entries for notification and ageing behavior.
- `struct ice_esw_br_fdb_entry` stores hash/list linkage, flags, owning netdev, bridge port, hardware flow, and last-use timestamp.
- `enum ice_esw_br_port_type` distinguishes uplink ports from VF representor ports.
- `struct ice_esw_br_port` stores bridge back pointer, VSI pointer/index, port type, PVID, representor id, and per-port VLAN xarray.
- `ICE_ESWITCH_BR_VLAN_FILTERING` is the bridge flag toggled by switchdev VLAN filtering attributes.
- `struct ice_esw_br` stores the single bridge state: offload container, port xarray, FDB rhashtable/list, Linux bridge ifindex, flags, and ageing time.
- `struct ice_esw_br_offloads` stores PF pointer, bridge pointer, netdev/switchdev notifier blocks, ordered workqueue, and delayed ageing work.
- `struct ice_esw_br_fdb_work` packages switchdev FDB notifications for deferred workqueue handling.
- `struct ice_esw_br_vlan` stores VID and bridge VLAN flags.
- Container macros convert notifier/work pointers back to bridge offload and FDB work structures.
- `ice_eswitch_br_is_vid_valid()` treats VID 0 and VID 1 as special untagged/PVID cases that should not add VLAN lookup fields.
- Exported functions are `ice_eswitch_br_offloads_init()`, `ice_eswitch_br_offloads_deinit()`, and `ice_eswitch_br_fdb_flush()`.

## Control Flow
The header has no standalone runtime flow. It defines the structures walked by `ice_eswitch_br.c`: notifier callbacks enter through `ice_esw_br_offloads`, bridge ports are looked up in `ice_esw_br.ports`, FDB entries are looked up by `ice_esw_br_fdb_data`, and delayed work uses the container macros to regain the parent offload object.

## State and Persistence Behavior
The declared structures are in-memory bridge offload state. They mirror Linux bridge configuration and ice hardware rules while switchdev offloads are active. No state is persisted across driver unload or switchdev teardown. FDB hardware rules are represented by pointers that must be explicitly deleted before freeing entries.

## Dependencies and Integration Points
The header depends on kernel rhashtable, workqueue, notifier, netdevice, switchdev, xarray, list, and Ethernet/VLAN types via included and surrounding driver headers. It is included by `ice_eswitch.c` for offload init/deinit and by `ice_eswitch_br.c` for implementation. It also embeds pointers to ice PF/VSI and representor-facing bridge port state.

## Risks and Edge Cases
- `ice_eswitch_br_is_vid_valid()` intentionally excludes VID 1 as well as VID 0; code adding VLAN lookups must preserve the bridge convention described in the comment.
- The FDB entry owns hardware rule pointers; freeing an entry without deleting both rules leaks hardware state.
- `struct ice_esw_br_port.vlans` needs xarray initialization and flush/destroy discipline in every port lifecycle path.
- The header models only VF representor bridge ports, even though current implementation also treats SF/representor netdevs through generic representor helpers; future type distinctions may need extension.

## Test Signals
- Compile coverage should ensure all container macros match the exact struct member names used by notifier and delayed-work registration.
- Static analysis should verify rhashtable key fields match `ice_fdb_ht_params` in the implementation.
- Runtime bridge tests should validate VID 0/1 handling, FDB rule cleanup, VLAN xarray cleanup, and ageing work container conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch_br.h -->

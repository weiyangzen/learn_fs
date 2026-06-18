# subset-b-005259 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe.c

## Purpose

`fcoe.c` is the software FCoE initiator driver that binds libfc/libfcoe to a Linux Ethernet netdevice. It registers the default `fcoe_sw` transport with libfcoe, creates and destroys FCoE controller and local-port instances, encapsulates and decapsulates Fibre Channel frames over Ethernet, handles FIP control traffic, reacts to netdevice/DCB events, exposes FC transport operations including NPIV vports, and delegates direct data placement/offload hooks to the lower network driver.

The file is the runtime bridge between three subsystems: the SCSI/FC transport, libfc exchange/lport/discovery code, and Linux networking packet receive/transmit APIs.

## Important APIs, types, and functions

- Module parameters: `ddp_min`, `debug_logging`, `e_d_tov`, and `r_a_tov` tune DDP matching, logging, and FC timeouts.
- Global state: `fcoe_config_mutex`, `fcoe_wq`, `fcoe_hostlist`, and per-CPU `fcoe_percpu` receive/trailer state.
- Transport templates: `fcoe_sysfs_templ`, `fcoe_libfc_fcn_templ`, `fcoe_nport_fc_functions`, `fcoe_vport_fc_functions`, and `fcoe_shost_template` connect this driver to libfcoe, libfc, FC transport, and SCSI midlayer callbacks.
- Interface lifecycle: `fcoe_interface_create()`, `fcoe_interface_setup()`, `fcoe_interface_remove()`, and `fcoe_interface_cleanup()` allocate an FCoE controller/sysfs device, program netdevice multicast/unicast filters, register packet handlers, and release references.
- Local-port lifecycle: `fcoe_if_create()`, `fcoe_if_destroy()`, `fcoe_create()`, `fcoe_ctlr_alloc()`, `fcoe_destroy()`, and `fcoe_destroy_work()` allocate FC/SCSI hosts, configure link/offload/WWN properties, add/remove hostlist membership, and defer teardown to `fcoe_wq`.
- Data path: `fcoe_xmit()` builds Ethernet and FCoE headers/trailers around an `fc_frame`, while `fcoe_rcv()`, `fcoe_receive_work()`, `fcoe_recv_frame()`, and `fcoe_filter_frames()` validate Ethernet/FCoE/FC framing and pass good frames to `fc_exch_recv()`.
- FIP integration: `fcoe_fip_recv()`, `fcoe_fip_vlan_recv()`, `fcoe_fip_send()`, `fcoe_elsct_send()`, `fcoe_flogi_resp()`, `fcoe_logo_resp()`, and `fcoe_set_port_id()` route control traffic to `fcoe_ctlr.c` and handle FLOGI/LOGO MAC assignment details.
- Offload hooks: `fcoe_netdev_features_change()`, `fcoe_ddp_setup()`, `fcoe_ddp_target()`, `fcoe_ddp_done()`, and `fcoe_em_config()` map netdevice FCoE offload capabilities into libfc exchange-manager ranges.
- NPIV: `fcoe_vport_create()`, `fcoe_vport_destroy()`, `fcoe_vport_disable()`, `fcoe_vport_remove()`, and `fcoe_set_vport_symbolic_name()` implement FC vport operations over the same FCoE interface.

## Control flow

Module initialization creates the per-CPU workqueue state, attaches the default FCoE transport to libfcoe, registers netdevice and DCB notifiers, and attaches FC transport templates. Creation can enter through libfcoe module parameters or sysfs. The create path locks `fcoe_config_mutex` and RTNL, rejects duplicate netdevices, allocates a `fcoe_ctlr_device`, initializes `struct fcoe_ctlr`, registers packet handlers for FCoE/FIP ethertypes, creates the master libfc local port, configures SCSI/FC transport attributes, allocates exchange managers, records DCB priorities, and starts fabric login.

Transmit flow starts from libfc `.frame_send = fcoe_xmit`. ELS frames may be diverted to `fcoe_ctlr_els_send()` for FIP encapsulation. Normal frames get CRC/EOF trailer allocation, optional CRC/segmentation offload flags, Ethernet source/destination selection from the controller, VLAN hardware tagging when appropriate, stats updates, and delivery through `fcoe_port_send()`/`fcoe_start_io()` with a retry queue on transmit failure.

Receive flow is packet-handler based. `fcoe_rcv()` validates link state, FIP source MAC in FIP mode, minimum frame length, FC destination/MAC mapping, and then queues the skb to a per-CPU worker selected by exchange ID. `fcoe_recv_frame()` linearizes, validates FCoE version, extracts CRC/EOF, trims the FC payload, filters CRC and invalid FIP-mode LOGO frames, and delivers to libfc exchange receive. FIP packets are enqueued to the controller receive worker in `fcoe_ctlr.c`.

Netdevice events drive link and teardown. MTU and feature changes refresh local-port settings; up/change events call `fcoe_ctlr_link_up()` if the controller is enabled and the link is usable; down events call `fcoe_ctlr_link_down()` and purge pending transmit frames; unregister tears down vports, the lport, packet handlers, controller resources, and the sysfs controller device.

## State and persistence behavior

Runtime state lives in kernel memory and netdevice registration state. `fcoe_hostlist` maps active netdevices to FCoE interfaces and is documented as RTNL-protected. `struct fcoe_interface` stores netdevice references, packet handlers, selected real device, offload exchange manager pointer, removal flag, and FCoE priority. `struct fcoe_port` in lport private data stores pending transmit queue, retry timer, source MAC, destroy work, queue-depth watermarks, and backpointer to the interface. Per-CPU `fcoe_percpu` state holds receive queues and reusable CRC/EOF trailer pages. Hardware-visible persistence is limited to netdevice MAC filter membership, multicast membership, DCB priority usage, and lower-driver offload contexts.

## Dependencies and integration points

The file depends on Linux networking (`net_device`, packet handlers, VLAN, DCB, ethtool features, RTNL), SCSI midlayer, FC transport, libfc, libfcoe, and FC/FIP/FCoE protocol headers. It integrates with lower Ethernet drivers through `netdev_ops` hooks such as `ndo_fcoe_enable`, `ndo_fcoe_disable`, `ndo_fcoe_get_wwn`, `ndo_fcoe_get_hbainfo`, and DDP hooks. The exported external surface is mostly indirect through the registered `struct fcoe_transport`, FC transport callbacks, and libfc templates.

## Risks and edge cases

- `fcoe_hostlist_lookup()` computes `ctlr = fcoe_to_ctlr(fcoe)` before checking whether `fcoe` is NULL. Current callers usually check for an existing interface or call under expected preconditions, but a NULL result would be unsafe.
- Teardown crosses RTNL, `fcoe_config_mutex`, workqueues, packet handler synchronization, SCSI host removal, libfc cleanup, and sysfs controller deletion. Ordering regressions can cause use-after-free or packet receive into freed lports.
- FIP/non-FIP/VN2VN mode changes alter multicast filters and destination MAC semantics. Incorrect mode state can silently send frames to the wrong MAC.
- Receive CPU selection uses FC exchange IDs masked by `fc_cpu_mask`; bad IDs or CPU hotplug edges rely on validation and per-CPU cleanup.
- `fcoe_start_io()` clones skbs before `dev_queue_xmit()`. Error handling leaves ownership with the retry queue in some paths, so queue length and skb ownership accounting are important.
- FDMI retrieval returns early on lower-driver error without freeing the allocated `fdmi` buffer, which is a leak risk on that error path.

## Test signals

Useful tests include module load/unload with `CONFIG_FCOE`, create/destroy on physical and VLAN netdevices, link up/down and MTU/feature-change notifier simulation, FIP discovery and non-FIP fallback, VN2VN mode switching, FLOGI/LOGO MAC updates, NPIV vport create/delete/disable, DDP-capable and non-DDP netdevices, and transmit failure retry-queue behavior. KASAN/KCSAN and lockdep are high-value for teardown and notifier races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe.h

## Purpose

`fcoe.h` is the private header for the software FCoE driver. It defines driver constants, debug logging macros, the per-netdevice `struct fcoe_interface`, pointer conversion helpers between the embedded `struct fcoe_ctlr` and interface object, and `fcoe_netdev()` for resolving an lport back to its netdevice.

## Important APIs, types, and functions

- Constants define queue depth, version/name/vendor strings, maximum LUN/target/outstanding command counts, and software exchange ID range.
- `FCOE_LOGGING`, `FCOE_NETDEV_LOGGING`, `FCOE_CHECK_LOGGING()`, `FCOE_DBG()`, and `FCOE_NETDEV_DBG()` gate printk-style diagnostics on the module-level `fcoe_debug_logging`.
- `struct fcoe_interface` stores list linkage, logical and real netdevices, packet-handler registrations for FCoE/FIP/FIP-over-realdev VLAN discovery, shared offload exchange manager, removal flag, and traffic priority.
- `fcoe_to_ctlr()` and `fcoe_from_ctlr()` encode the allocation layout where `struct fcoe_ctlr` is immediately followed by `struct fcoe_interface`.
- `fcoe_netdev()` obtains the interface from `struct fcoe_port` private data and returns the associated logical netdevice.

## Control flow

The header has no standalone runtime flow. Its helpers are used during allocation, data path, and teardown in `fcoe.c`. The pointer conversion macros assume the `fcoe_ctlr_device_add()` private allocation layout used by `fcoe_interface_create()`.

## State and persistence behavior

No global state is defined except the external debug variable declaration. `struct fcoe_interface` is the persistent runtime object for a software FCoE instance and stays alive while the corresponding controller/lport exists.

## Dependencies and integration points

The header includes `linux/skbuff.h` and `linux/kthread.h` and relies on libfc/libfcoe types visible to its includers, especially `struct fc_lport`, `struct fcoe_port`, and `lport_priv()`. It is intentionally local to the driver and not a public UAPI.

## Risks and edge cases

The conversion macros are layout-sensitive and provide no type or bounds checking. Any change to allocation ordering in `fcoe.c` or `fcoe_ctlr_device_add()` private data sizing would break all conversions. `fcoe_netdev()` assumes lport private data is a valid `struct fcoe_port` with `priv` pointing to `struct fcoe_interface`.

## Test signals

Compile coverage catches most type drift. Runtime create/destroy tests validate the allocation layout indirectly because interface setup, transmit, receive, and cleanup all traverse these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_ctlr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_ctlr.c

## Purpose

`fcoe_ctlr.c` implements the libfcoe FIP controller: fabric FCF discovery and selection, FIP-encapsulated ELS handling, keep-alives, Clear Virtual Link handling, non-FIP fallback, VN2VN negotiation/discovery, FIP VLAN discovery replies, WWN derivation, and libfc configuration for FCoE local ports. It is protocol and state-machine heavy; lower drivers provide send/update/get-MAC callbacks, while this file owns FIP parsing, timers, locks, and controller state transitions.

## Important APIs, types, and functions

- Exported controller lifecycle: `fcoe_ctlr_init()`, `fcoe_ctlr_destroy()`, `fcoe_ctlr_link_up()`, `fcoe_ctlr_link_down()`, and `fcoe_ctlr_recv()`.
- Exported protocol/libfc helpers: `fcoe_ctlr_els_send()`, `fcoe_ctlr_recv_flogi()`, `fcoe_wwn_from_mac()`, `fcoe_libfc_config()`, `fcoe_fcf_get_selected()`, and `fcoe_ctlr_set_fip_mode()`.
- Fabric discovery: `fcoe_ctlr_solicit()`, `fcoe_ctlr_parse_adv()`, `fcoe_ctlr_recv_adv()`, `fcoe_ctlr_age_fcfs()`, `fcoe_ctlr_select()`, `fcoe_ctlr_announce()`, `fcoe_sysfs_fcf_add()`, and `fcoe_sysfs_fcf_del()`.
- ELS/FLOGI path: `fcoe_ctlr_encaps()`, `fcoe_ctlr_els_send()`, `fcoe_ctlr_recv_els()`, `fcoe_ctlr_flogi_send_locked()`, `fcoe_ctlr_flogi_send()`, and `fcoe_ctlr_flogi_retry()`.
- Timer/worker path: `fcoe_ctlr_timeout()`, `fcoe_ctlr_timer_work()`, and `fcoe_ctlr_recv_work()`.
- VN2VN: `fcoe_ctlr_vn_start()`, `fcoe_ctlr_vn_restart()`, `fcoe_ctlr_vn_parse()`, `fcoe_ctlr_vn_recv()`, `fcoe_ctlr_vn_send()`, probe/claim/beacon handlers, remote-port callbacks, and VN discovery hooks.
- VLAN responder: `fcoe_ctlr_vlan_parse()`, `fcoe_ctlr_vlan_send()`, `fcoe_ctlr_vlan_disc_reply()`, and `fcoe_ctlr_vlan_recv()`.

## Control flow

Initialization sets state to `FIP_ST_LINK_WAIT`, initializes FCF lists, mutex/spinlock, timer, work items, and receive queue. On link up, non-FIP mode moves directly to `FIP_ST_NON_FIP`; fabric/auto mode enters `FIP_ST_AUTO`, calls `fc_linkup()`, and multicasts a FIP discovery solicitation; VN2VN starts the VN state machine and then links up libfc.

Fabric mode receives FIP frames via `fcoe_ctlr_recv()` into a workqueue. The handler validates destination MAC, version, descriptor length, and current state. In auto mode the first valid FIP frame switches to `FIP_ST_ENABLED`. Discovery advertisements are parsed into `struct fcoe_fcf` records, exposed through sysfs when a controller device exists, solicited for MTU validation if needed, aged by timer, and selected after the startup delay. Selection rejects conflicting fabric/VFID/FC-MAP advertisements and prefers lower priority or alternate FCFs not yet tried for FLOGI.

FLOGI ELS frames are intercepted by `fcoe_ctlr_els_send()`. In fabric FIP mode the original skb is retained as `flogi_req`, then timer work selects an FCF and sends a FIP-encapsulated clone. FLOGI LS_ACC updates granted MAC state and announces selected FCF; rejects can trigger retries against another FCF. Non-FIP fallback snoops FLOGI responses and chooses either mapped FC-OUI destination addressing or gateway source MAC addressing.

VN2VN mode uses a separate timer-driven sequence: propose a port ID, send two probes, claim the ID, set mapped source MAC/local ID, announce claims, then enter `FIP_ST_VNMP_UP` and send periodic beacons. Incoming probes, claim notifications/responses, and beacons resolve collisions, create/update libfc remote ports, age neighbors, and drive PLOGI login through discovery callbacks.

Clear Virtual Link frames verify selected FCF identity and descriptors, then reset the physical lport and/or matching NPIV ports. VLAN discovery frames are parsed only when `fip_resp` is enabled and replied to with configured VLAN information.

## State and persistence behavior

`struct fcoe_ctlr` holds the durable in-kernel controller state: mode/state, locks, selected FCF, FCF list/count, FLOGI request skb and OXID, control/data MAC addresses via callbacks, timers for solicit/selection/keepalive, VN2VN port ID/probe state/random state, VLAN responder flag, and work queues. FCF records persist until advertisement timeout, link reset, or controller destruction. Sysfs FCF devices mirror FCF records but may be absent for libfcoe users such as fnic. Hardware-visible state is limited to transmitted FIP/FCoE frames and callback-driven MAC updates.

## Dependencies and integration points

The file depends on FC/FIP/FCoE protocol structures, libfc local-port/discovery/exchange APIs, libfcoe sysfs device helpers, Linux timers/workqueues/skbs, Ethernet helpers, VLAN tags, and RTNL-visible netdevice state through higher layers. `fcoe_libfc_config()` is the key integration point that initializes libfc and installs VN2VN-specific discovery operations when the controller mode requires them.

## Risks and edge cases

- FIP descriptor parsing is length- and ordering-sensitive. Duplicate critical descriptors are rejected in most paths, but any parser gap risks malformed frames steering state transitions.
- Locking uses `ctlr_mutex`, `ctlr_lock`, libfc discovery locks, timers, workqueues, and sysfs locks. Deadlock or lifetime bugs are plausible around FCF deletion, FLOGI retry, and controller destruction.
- FCF selection returns NULL on conflicting fabric/VFID/FC-MAP records; environments with mixed advertisements can remain unable to log in.
- `fcoe_ctlr_age_fcfs()` temporarily removes FCFs from the list and then calls sysfs deletion; list/count consistency is critical.
- VN2VN port-ID conflict handling is probabilistic and timer based. Tests need collisions, repeated login failures, and beacon expiry.
- FIP VLAN response is gated by a mutable sysfs flag; enabling it on the wrong interface could answer VLAN discovery unexpectedly.

## Test signals

Tests should cover valid and malformed FIP advertisements, FCF add/update/delete and sysfs mirror behavior, FCF priority selection and conflicting-fabric rejection, FLOGI LS_ACC/LS_RJT retry paths, non-FIP fallback, Clear Virtual Link resets, keepalive scheduling, controller destroy with queued FIP packets, VN2VN probe/claim collision and beacon aging, VLAN discovery response, and mode switching while the lport is disabled. KUnit-style parser tests would be especially valuable for descriptor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_ctlr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_sysfs.c

## Purpose

`fcoe_sysfs.c` implements the `fcoe` bus and sysfs object model for FCoE controllers and discovered Fibre Channel Forwarders. It provides controller attributes for mode, enabled state, VLAN responder behavior, FC timeouts, FCF dev-loss timeout, and LESB counters; FCF attributes for fabric/switch identity, FC-MAP, VFID, MAC, priority, FKA period, state, selected flag, VLAN ID, and dev-loss timeout; and bus-level create/destroy attributes that delegate to libfcoe transport handlers.

## Important APIs, types, and functions

- Exported lifecycle: `fcoe_sysfs_setup()` registers the bus; `fcoe_sysfs_teardown()` unregisters it.
- Exported devices: `fcoe_ctlr_device_add()`, `fcoe_ctlr_device_delete()`, `fcoe_fcf_device_add()`, and `fcoe_fcf_device_delete()`.
- Attribute store paths: `store_ctlr_mode()`, `store_ctlr_enabled()`, `store_ctlr_fip_resp()`, `store_ctlr_r_a_tov()`, `store_ctlr_e_d_tov()`, `store_private_fcoe_ctlr_fcf_dev_loss_tmo()`, and `store_fcoe_fcf_dev_loss_tmo()`.
- Workqueue helpers: controller work queues handle FCF final deletion and delayed dev-loss timeout through `fcoe_fcf_device_final_delete()` and `fip_timeout_deleted_fcf()`.
- Attribute macro families generate show routines that optionally call low-level function-template getters before formatting values.

## Control flow

`fcoe_ctlr_device_add()` allocates a controller object plus driver-private tail memory, assigns an atomic ID, initializes FCF list/lock/default mode/default FCF dev-loss timeout, creates ordered workqueues, names the device `ctlr_N`, and registers it on the `fcoe` bus. The controller type automatically exposes controller and `lesb/` attribute groups.

Controller sysfs writes validate state before delegating. Mode changes are allowed only while disabled and require an LLD mode callback. Enabling/disabling toggles the controller state and calls the LLD `set_fcoe_ctlr_enabled()` callback. FC timeout writes are allowed only while disabled. FCF dev-loss writes update the controller default and propagate to connected FCF devices.

`fcoe_fcf_device_add()` either reconnects a matching disconnected FCF or allocates a new `fcf_N` child device under the controller. `fcoe_fcf_device_delete()` marks a connected FCF disconnected, clears its private pointer, and schedules delayed dev-loss removal. If the FCF reconnects before the delay expires, delayed work is canceled; if not, timeout work removes it from the list and queues final device unregister.

`fcoe_ctlr_device_delete()` marks all child FCFs deleted, queues final deletion, flushes work, destroys workqueues, and unregisters the controller device. Bus attributes `ctlr_create` and `ctlr_destroy` call the transport-layer store functions in `fcoe_transport.c`.

## State and persistence behavior

Atomic counters generate monotonically increasing controller and FCF IDs for the module lifetime. Each controller owns an FCF list protected by `ctlr->lock`, two ordered workqueues, a mode/enabled state, LESB values refreshed by callbacks, and default FCF dev-loss timeout. Each FCF device tracks connection state (`UNKNOWN`, `CONNECTED`, `DISCONNECTED`, `DELETED`), delayed deletion work, exported identity fields, selected/VLAN values refreshed through callbacks, and an LLD-private pointer. State is runtime-only and disappears on module unload or device unregister.

## Dependencies and integration points

The file depends on `<scsi/fcoe_sysfs.h>` and `<scsi/libfcoe.h>` for public object layouts and function templates, plus the local debug header. It integrates with `fcoe_ctlr.c` for FCF mirror creation/deletion and with `fcoe_transport.c` for bus-level create/destroy. Low-level drivers provide `struct fcoe_sysfs_function_template` callbacks for mode changes, enable state, LESB refresh, selected FCF state, and VLAN ID.

## Risks and edge cases

- `store_ctlr_enabled()` mutates `ctlr->enabled` before invoking the LLD callback. If the callback fails, the previous visible state is not restored.
- Workqueue existence is checked defensively, but deletion ordering depends on flushing controller work before destroying both queues.
- FCF dev-loss timeout conversion guards `u32` overflow, but a very large accepted value can leave disconnected FCF devices present for a long time.
- `fcoe_fcf_device_add()` reconnects a matching FCF and cancels dev-loss work; callers must hold `ctlr->lock` as documented or list/work races are possible.
- Attribute show callbacks can invoke LLD getters while users read sysfs, so getter locking must be compatible with controller and FCF locks.

## Test signals

Tests should verify bus registration, controller add/delete, sysfs mode/enable/timeout parsing, rejection while enabled, FCF add/reconnect/delete/dev-loss expiry, selected and VLAN getter callbacks, LESB refresh attributes, failed LLD enable callback behavior, and module unload with connected and disconnected FCF children. Lockdep and sysfs stress reads during FCF deletion are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_transport.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_transport.c

## Purpose

`fcoe_transport.c` implements the libfcoe transport registry and shared helper routines used by FCoE drivers. It owns the list of registered FCoE transports, maps netdevices to the transport that created an instance, provides module-parameter and sysfs create/destroy/enable/disable entry points, registers the FCoE sysfs bus, and exports utility functions for link speed, LESB counters, WWN formatting, vport validation, FC CRC calculation, transmit retry queues, and paged CRC/EOF trailer allocation.

## Important APIs, types, and functions

- Exported transport registry: `fcoe_transport_attach()` and `fcoe_transport_detach()`.
- User entry points: module parameters `show`, `create`, `create_vn2vn`, `destroy`, `enable`, `disable`, plus exported `fcoe_ctlr_create_store()` and `fcoe_ctlr_destroy_store()` used by sysfs bus attributes.
- Netdevice mapping helpers: `fcoe_add_netdev_mapping()`, `fcoe_del_netdev_mapping()`, `fcoe_netdev_map_lookup()`, and `libfcoe_device_notification()`.
- Exported helpers: `fcoe_link_speed_update()`, `__fcoe_get_lesb()`, `fcoe_get_lesb()`, `fcoe_ctlr_get_lesb()`, `fcoe_wwn_to_str()`, `fcoe_validate_vport_create()`, `fcoe_get_wwn()`, `fcoe_fc_crc()`, `fcoe_start_io()`, `fcoe_clean_pending_queue()`, `fcoe_check_wait_queue()`, `fcoe_queue_timer()`, and `fcoe_get_paged_crc_eof()`.
- Module lifecycle: `libfcoe_init()` registers the netdevice notifier and sysfs bus; `libfcoe_exit()` tears them down.

## Control flow

On module load, the transport layer registers a netdevice notifier and then registers the `fcoe` sysfs bus. FCoE drivers call `fcoe_transport_attach()` to register a named transport; the default software transport is placed at the tail so more specific transports can match first. Creation paths parse an interface name, resolve a netdevice, reject duplicates through the mapping list, find the first matching transport, call either `alloc()` for sysfs controller allocation or `create()` for legacy module-parameter creation, then record the netdevice-to-transport mapping. Destroy paths look up that mapping, call transport `destroy()`, and remove the mapping.

Transmit helper flow uses a per-lport pending skb queue. `fcoe_start_io()` clones an skb for `dev_queue_xmit()` and frees the original on success. If transmit fails, `fcoe_check_wait_queue()` keeps the skb queued, retries queued packets serially, sets `lport->qfull` above the max depth, clears it below the min depth, and arms the port timer for later retry.

Link/stat helper flow maps ethtool Ethernet speeds into FC transport speed bits and derives FCoE LESB counters by summing per-CPU libfc stats plus netdevice CRC error counters. `fcoe_get_paged_crc_eof()` reuses a per-CPU page for non-linear skb trailer fragments.

## State and persistence behavior

`fcoe_transports` under `ft_mutex` stores attached transports. `fcoe_netdevs` under `fn_mutex` stores live netdevice mappings. Module parameter writes mutate runtime state by creating or destroying instances through registered transport callbacks. Retry queues, timers, and CRC/EOF page state live in `struct fcoe_port`/`struct fcoe_percpu_s` owned by the caller. Nothing is persistent beyond module lifetime.

## Dependencies and integration points

The file depends on Linux module parameters, netdevice and ethtool APIs, CRC32 helpers, SCSI/libfc/libfcoe structures, and `fcoe_sysfs_setup()`/`fcoe_sysfs_teardown()`. Registered `struct fcoe_transport` implementations supply `match`, `alloc`, `create`, `destroy`, `enable`, and `disable` operations.

## Risks and edge cases

- `fcoe_ctlr_create_store()` calls `ft->alloc()` before adding the netdev mapping. If allocation succeeds but mapping allocation fails, the allocated controller is not destroyed in this function, creating a lifecycle leak risk.
- Legacy `fcoe_transport_destroy()` removes the netdev mapping even when `ft->destroy()` fails, while `fcoe_ctlr_destroy_store()` keeps the mapping on destroy failure. The two entry points differ in failure semantics.
- `fcoe_start_io()` leaks the cloned skb if `dev_queue_xmit()` returns nonzero after taking ownership assumptions are wrong; this pattern should be checked against current networking semantics.
- Interface name parsing truncates to `IFNAMSIZ` and strips trailing newlines only; malformed names should be tested.
- Queue length manipulation in `fcoe_check_wait_queue()` intentionally increments `qlen` around dequeue/requeue. It is subtle and vulnerable to future changes.

## Test signals

Tests should cover transport attach/detach ordering, duplicate create rejection, sysfs allocation failure cleanup, module-parameter create/destroy failure semantics, netdevice unregister mapping cleanup, interface-name parsing, link-speed mapping for common and unknown speeds, LESB aggregation, vport duplicate WWPN rejection, CRC over linear and fragmented skbs, retry queue qfull transitions, and paged trailer allocation at page boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/libfcoe.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/libfcoe.h

## Purpose

`libfcoe.h` is a private debug-support header for the local libfcoe implementation. It declares the module-level `libfcoe_debug_logging` bitmask and defines logging category bits plus macros used by `fcoe_ctlr.c`, `fcoe_sysfs.c`, and `fcoe_transport.c`.

## Important APIs, types, and functions

- Logging categories: `LIBFCOE_LOGGING`, `LIBFCOE_FIP_LOGGING`, `LIBFCOE_TRANSPORT_LOGGING`, and `LIBFCOE_SYSFS_LOGGING`.
- `LIBFCOE_CHECK_LOGGING()` conditionally executes a command block when a category bit is enabled.
- `LIBFCOE_DBG()`, `LIBFCOE_FIP_DBG()`, `LIBFCOE_TRANSPORT_DBG()`, and `LIBFCOE_SYSFS_DBG()` format logs with subsystem-specific prefixes.

## Control flow

There is no standalone flow. The macros expand inline at call sites and are gated by the runtime module parameter defined in `fcoe_transport.c`.

## State and persistence behavior

The header declares but does not define `libfcoe_debug_logging`. Logging state is global to the libfcoe module and mutable through the module parameter.

## Dependencies and integration points

The macros assume normal kernel logging helpers and, for FIP/sysfs variants, valid `struct fcoe_ctlr` or `struct fcoe_ctlr_device` pointers with host or ID fields. It is local-private despite its name; public libfcoe contracts come from `<scsi/libfcoe.h>`.

## Risks and edge cases

The debug macros evaluate context expressions when enabled; invalid controller/device pointers in logging paths can crash only under debug logging, making such bugs configuration-sensitive. Very verbose logging in FIP receive paths can be noisy under packet load.

## Test signals

Compile all local users with debug logging enabled and disabled. Runtime smoke tests can set each bitmask category and confirm expected messages in controller, transport, and sysfs paths without changing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/libfcoe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fdomain.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fdomain.c

## Purpose

`fdomain.c` is the shared low-level SCSI driver core for Future Domain TMC-16x0 ISA and TMC-3260 PCI host adapters. It implements chip detection, reset, PIO/FIFO data transfer, interrupt scheduling, the SCSI command state machine, error handling, BIOS geometry calculation, host allocation, IRQ registration, scan, destroy, and resume reset. Bus-specific ISA and PCI wrappers call `fdomain_create()` and `fdomain_destroy()`.

## Important APIs, types, and functions

- `enum chip_type` distinguishes TMC-1800, TMC-18C50, and TMC-18C30 variants.
- `struct fdomain` stores I/O base, active command, chip type, and deferred work.
- Hardware helpers: `fdomain_identify()`, `fdomain_test_loopback()`, `fdomain_reset()`, `fdomain_make_bus_idle()`, and `fdomain_select()`.
- Data transfer: `fdomain_read_data()` and `fdomain_write_data()` move data between the adapter FIFO and SCSI scatterlists using atomic sg mapping.
- Command engine: `fdomain_queue()`, `fdomain_irq()`, and `fdomain_work()` implement arbitration, selection, command, data, status, and message phases.
- Error/utility callbacks: `fdomain_abort()`, `fdomain_host_reset()`, and `fdomain_biosparam()`.
- Exported bus-wrapper APIs: `fdomain_create()` and `fdomain_destroy()`.
- `fdomain_template` is the SCSI host template with one queued command, 64 SG entries, PIO boundary, abort/reset callbacks, and per-command `struct scsi_pointer` storage.

## Control flow

The bus wrapper reserves resources and calls `fdomain_create()`. The core identifies the chip, resets it, validates loopback, allocates a SCSI host, sets optional SCSI ID, stores I/O/IRQ metadata, initializes work, requests IRQ, adds the host, and scans the bus.

SCSI commands enter through `fdomain_queue()`. The driver initializes per-command phase bookkeeping, stores the single active command in `fd->cur_cmd`, idles the bus, writes its initiator ID bit, enables arbitration interrupts, and returns. The interrupt handler disables adapter interrupts, ignores spurious interrupts when no command is active, and schedules `fdomain_work()`. Work runs under `host_lock`, advances arbitration and selection, then services SCSI REQ phases: COMMAND OUT writes command bytes, DATA IN/OUT enables FIFO and transfers data, STATUS IN stores status, MESSAGE IN detects command completion, and MESSAGE OUT rejects messages. Completion sets SCSI status/host/message bytes, idles the bus, calls `scsi_done()`, and clears `cur_cmd`.

Abort idles the bus, marks the current command aborted, sets `DID_ABORT`, and completes it. Host reset pulses SCSI reset and reinitializes adapter control registers. Destroy cancels work, removes the host, frees IRQ, and drops the host reference.

## State and persistence behavior

The driver supports one active command per host (`can_queue = 1`) and persists command progress in `struct scsi_pointer` private command data. Adapter state persists in I/O registers: bus control, mode, interrupt control, adapter control, FIFO data/count, and configuration registers. Runtime host state is freed on remove. Resume resets the hardware but does not preserve in-flight command state.

## Dependencies and integration points

The file depends on the SCSI midlayer, ISA/PCI wrappers for resource discovery, low-level port I/O, interrupts, workqueues, delays, and `fdomain.h` register definitions. ISA and PCI wrappers export module identities but share all core SCSI behavior here.

## Risks and edge cases

- The driver is PIO and register-state-machine based; missed interrupts or incorrect phase transitions can hang a command.
- `fdomain_queue()` does not appear to reject a new command if `fd->cur_cmd` is already set, relying on `can_queue = 1` and SCSI midlayer serialization.
- Abort handling is explicitly described as poor and completes the active command immediately after idling the bus.
- FIFO transfer loops assume residual accounting and sg mapping lengths remain consistent; underflow in `scsi_set_resid(cmd, scsi_get_resid(cmd) - len)` would be serious.
- Chip differences, especially TMC-1800 data phase handling versus FIFO-enabled later chips, are delicate.
- `fdomain_create()` resets and loopback-tests hardware before requesting IRQ; failure paths must leave bus-specific resources to wrappers.

## Test signals

Build both ISA and PCI variants. Hardware or emulator tests should scan devices, run read/write commands with varied transfer sizes and SG fragmentation, trigger no-connect selection timeout, test abort and host reset, unload while idle and after errors, resume from sleep, and validate geometry results for disks with and without partition-table hints. IRQ sharing should be tested on PCI/PCMCIA-style devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fdomain.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fdomain.h

## Purpose

`fdomain.h` defines the shared Future Domain adapter register map, bit definitions, command phase flags, constants, power-management macro, and exported create/destroy prototypes used by the core driver and ISA/PCI bus wrappers.

## Important APIs, types, and functions

- Constants: `FDOMAIN_REGION_SIZE` and `FDOMAIN_BIOS_SIZE`.
- Phase flags include `in_arbitration`, `in_selection`, `in_other`, `disconnect`, `aborted`, and `sent_ident`.
- Register offsets and bit masks cover SCSI data/bus status/control, adapter status/control, interrupt control/condition, FIFO status/count/data, ID/configuration registers, loopback, and chip-specific controls.
- `FDOMAIN_PM_OPS` resolves to the shared PM ops when sleep PM is enabled.
- Prototypes: `fdomain_create()` and `fdomain_destroy()`.

## Control flow

The header has no executable flow. Its constants are used by `fdomain.c` to program hardware and by `fdomain_isa.c` to derive IRQ/base settings.

## State and persistence behavior

No software state is stored here. The definitions describe persistent adapter register state manipulated through I/O port operations in the driver.

## Dependencies and integration points

The header expects kernel bit helpers and SCSI host declarations to be available through including C files. It is the contract between bus-specific discovery modules and the shared core.

## Risks and edge cases

Several registers are shared offsets with read/write-specific meanings, and some bits are absent on older chips. Misusing a definition on the wrong chip can program unrelated behavior. The PM ops macro changes with `CONFIG_PM_SLEEP`, so wrappers must use `FDOMAIN_PM_OPS` rather than referencing private symbols directly.

## Test signals

Compile ISA and PCI modules under PM-enabled and PM-disabled configurations. Runtime tests should verify register programming on each supported chip family, especially offsets marked absent on TMC-1800/TMC-18C50.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fdomain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fdomain_isa.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fdomain_isa.c

## Purpose

`fdomain_isa.c` is the ISA bus wrapper and autodetection layer for the Future Domain TMC-16x0 driver. It scans known BIOS ROM addresses and I/O ports, parses BIOS signatures and optional I/O-base hints, derives IRQ and host SCSI ID, reserves I/O regions, creates the shared `fdomain` SCSI host, and unregisters/release resources on remove. It also supports explicit `io`, `irq`, and `scsi_id` module parameters for up to four boards.

## Important APIs, types, and functions

- Module parameters: `io[]`, `irq[]`, and `scsi_id[]`.
- Probe tables: BIOS `addresses[]`, I/O `ports[]`, valid `irqs[]`, and `signatures[]` with signature text, ROM offset, length, default SCSI ID, and optional base-address offset.
- `fdomain_isa_match()` implements BIOS/port autodetection for the ISA driver.
- `fdomain_isa_param_match()` implements explicit parameter probing.
- `fdomain_isa_remove()` destroys the shared host and releases the I/O region.
- `fdomain_isa_driver` wires match/remove and PM ops into the ISA bus.
- `fdomain_isa_init()` chooses autodetect or parameter mode and registers the ISA driver.

## Control flow

Without explicit `io[0]`, the ISA driver probes `ADDRESS_COUNT + PORT_COUNT` slots. Early slots map BIOS ROM addresses, search for known signatures, optionally read the adapter I/O base from the ROM, and remember a signature if the ROM identifies a card but does not provide a base. Later slots probe fixed I/O ports. For a candidate base, the driver reserves the I/O region, decodes IRQ from `REG_CFG1`, picks the SCSI ID from a matching or saved signature, calls `fdomain_create()`, and stores the SCSI host in device driver data.

With explicit parameters, only parameter slots are probed. Each nonzero `io[]` is reserved, IRQ is taken from the parameter or decoded from hardware, and `fdomain_create()` is called with the requested SCSI ID. Remove reverses creation by calling `fdomain_destroy()`, releasing the I/O region, and clearing drvdata.

## State and persistence behavior

Module parameters persist for the module lifetime. Autodetection uses a static `saved_sig` to carry a BIOS signature from ROM scanning into later port scanning. Per-device state is the SCSI host pointer stored in drvdata. Hardware state is initialized by the shared core.

## Dependencies and integration points

The file depends on Linux ISA bus support, I/O memory mapping, I/O port reservation, `check_signature()`, and the shared `fdomain` core. It uses `fdomain.h` for BIOS/region sizes and register/IRQ definitions.

## Risks and edge cases

- `saved_sig` is static across probe attempts; multiple ROM signatures or multiple boards can make association with later I/O-port probes ambiguous.
- BIOS signature matching includes unsupported-board comments but only supported signatures are in the table; unusual BIOS versions may be missed.
- IRQ autodetection is really configuration-register decoding, not active interrupt probing. Bad jumpers/register reads can pass an invalid IRQ to the core.
- Explicit parameter mode switches the driver-wide match function and probe count based only on `io[0]`, so mixed explicit/autodetect probing is not supported.
- Resource ownership is split: this wrapper owns I/O regions while the core owns IRQ/SCSI host.

## Test signals

Tests should cover autodetect with BIOS-provided base, BIOS signature without base followed by fixed-port probe, fixed-port-only probe, explicit parameter probing, busy I/O region failure, invalid chip failure cleanup, IRQ decode, remove cleanup, and PM resume through the shared `FDOMAIN_PM_OPS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fdomain_isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fdomain_pci.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fdomain_pci.c

## Purpose

`fdomain_pci.c` is the PCI wrapper for Future Domain TMC-3260/TMC-36C70 adapters. It matches the Future Domain PCI device ID, enables the device, reserves PCI regions, validates BAR0, creates the shared `fdomain` SCSI host at BAR0 with the PCI IRQ, and releases all PCI/core resources on remove.

## Important APIs, types, and functions

- `fdomain_pci_probe()` handles PCI enablement, region reservation, BAR validation, core host creation, and drvdata storage.
- `fdomain_pci_remove()` destroys the shared SCSI host, releases regions, and disables the device.
- `fdomain_pci_table[]` matches `PCI_VENDOR_ID_FD` and `PCI_DEVICE_ID_FD_36C70`.
- `fdomain_pci_driver` uses `module_pci_driver()` and shared `FDOMAIN_PM_OPS`.

## Control flow

Probe calls `pci_enable_device()`, `pci_request_regions()`, rejects zero-length BAR0, and calls `fdomain_create(pci_resource_start(pdev, 0), pdev->irq, 7, &pdev->dev)`. On success the SCSI host is stored as PCI driver data. Failure paths release regions and disable the device. Remove performs the inverse order after retrieving the host pointer.

## State and persistence behavior

This wrapper stores only the SCSI host pointer in PCI drvdata. PCI enablement and resource reservations persist while the device is bound. The shared core owns command and IRQ state.

## Dependencies and integration points

The file depends on Linux PCI core and `fdomain.h`. All hardware protocol and SCSI behavior is delegated to `fdomain.c`.

## Risks and edge cases

- The wrapper assumes BAR0 is an I/O base suitable for `inb/outb` use by the core; it validates only nonzero length.
- It does not call `pci_set_master()`, which is fine for PIO but should remain intentional.
- Failure cleanup relies on the core not owning PCI regions; ownership boundaries are split cleanly but must stay that way.

## Test signals

Compile with PCI support, bind/unbind a matching device, test zero-length BAR failure cleanup, verify IRQ sharing behavior through the core, and exercise suspend/resume through shared PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fdomain_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/Makefile

## Purpose

`fnic/Makefile` defines how the Cisco FNIC FCoE HBA driver is built. When `CONFIG_FCOE_FNIC` is enabled, it builds `fnic.o` from the listed FNIC, FDLS, FIP, vNIC queue/device/interrupt, trace, debugfs, and PCI subsystem ID objects.

## Important APIs, types, and functions

- `obj-$(CONFIG_FCOE_FNIC) += fnic.o` makes the driver conditional on the kernel config symbol.
- `fnic-y := ...` lists component object files: `fip.o`, `fnic_attrs.o`, `fnic_isr.o`, `fnic_main.o`, `fnic_res.o`, `fnic_fcs.o`, `fdls_disc.o`, `fnic_scsi.o`, `fnic_trace.o`, `fnic_debugfs.o`, `vnic_cq.o`, `vnic_dev.o`, `vnic_intr.o`, `vnic_rq.o`, `vnic_wq_copy.o`, `vnic_wq.o`, and `fnic_pci_subsys_devid.o`.

## Control flow

There is no runtime control flow. Kbuild uses this file to compose the final `fnic.o` module or built-in object from its component translation units.

## State and persistence behavior

No runtime state is defined. Build state depends on `CONFIG_FCOE_FNIC` and the object list.

## Dependencies and integration points

The file integrates the FNIC directory with kernel Kbuild. It implies dependencies among FNIC modules, Cisco vNIC support code, FIP/FDLS discovery, SCSI command handling, tracing, and debugfs components, but those dependencies are resolved by linker composition rather than this file.

## Risks and edge cases

Missing an object from `fnic-y` can produce unresolved symbols or silently omit functionality. Object order can matter for initcall/linker-section behavior, though ordinary symbol resolution is order-tolerant in this context. The line-continuation style lacks spaces before backslashes on some entries but is accepted by Kbuild as written.

## Test signals

Build with `CONFIG_FCOE_FNIC=m` and `=y`, verify all listed objects compile and link, and run modpost to catch missing exports or unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_desc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_desc.h

## Purpose

`cq_desc.h` defines the common 16-byte Cisco vNIC completion queue descriptor layout and a decode helper for FNIC/vNIC completion processing. It abstracts descriptor type, color bit, queue number, and completed index extraction from little-endian hardware fields.

## Important APIs, types, and functions

- `enum cq_desc_types` identifies completion variants: Ethernet work queue, descriptor copy, exchange work queue, Ethernet receive queue, and FCP receive queue.
- `struct cq_desc` contains `completed_index`, `q_number`, 11 bytes of type-specific data, and `type_color`.
- Bit masks define field widths for type, color, queue number, and completed index.
- `cq_desc_dec()` decodes color first, issues `rmb()`, then decodes type, queue number, and completed index.

## Control flow

Callers pass a hardware-filled descriptor to `cq_desc_dec()`. The helper reads the color bit before the memory barrier because hardware guarantees the color byte is written last. After `rmb()`, the remaining descriptor fields can be read without observing stale data from a previous descriptor cycle.

## State and persistence behavior

The header stores no software state. Completion descriptors reside in DMA memory owned by the vNIC/FNIC queue implementation. The color bit is the producer/consumer generation signal.

## Dependencies and integration points

The header depends on kernel fixed-width/endian types, `le16_to_cpu()`, and `rmb()`. It is included by FNIC/vNIC completion queue code that interprets type-specific descriptor payloads after the common fields are decoded.

## Risks and edge cases

- The memory barrier is essential. Removing or moving it can make consumers observe new color with stale descriptor contents.
- The field name `type_specfic` is misspelled but part of the local struct API; fixing it mechanically would require all users to change.
- Queue and index masks intentionally truncate hardware fields to 10 and 12 bits. Queue sizes or hardware generations with wider fields would require updates.

## Test signals

Build FNIC users, run sparse/endian checks, and test completion queues under wraparound to validate color-bit handling. Synthetic descriptor tests should verify type/color/q_number/completed_index decoding and memory-order assumptions on weakly ordered architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_desc.h -->

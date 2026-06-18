# Research Report: subset-b-004465

This grouped report covers the ICE driver devlink, health, port, adapter, admin-queue, and accelerated RFS files listed for `subset-b-004465`. Each section is source-tree aligned and bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/devlink.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/devlink.h

## Purpose
`devlink.h` declares the public devlink-facing entry points used by the rest of the ICE driver. It is a narrow interface between probe/remove, PF/SF lifecycle code, devlink port management, devlink regions, and devlink-rate scheduler export.

## Important APIs, Types, And Functions
The allocation APIs are `ice_allocate_pf()` and `ice_allocate_sf()`. Registration APIs are `ice_devlink_register()`, `ice_devlink_unregister()`, `ice_devlink_register_params()`, and `ice_devlink_unregister_params()`. Port APIs expose PF and VF devlink port creation/destruction. Region APIs expose `ice_devlink_init_regions()` and `ice_devlink_destroy_regions()`. Rate APIs expose `ice_devlink_rate_init_tx_topology()`, `ice_tear_down_devlink_rate_tree()`, and `ice_devlink_rate_clear_tx_topology()`.

## Control Flow
Probe code allocates a PF through devlink rather than embedding devlink allocation directly in the bus probe path. After hardware and PF capability discovery, callers register parameters, ports, and regions. Remove or error unwind paths call matching destroy/unregister functions. Scheduler topology is exported after VSI and scheduler nodes exist and cleared before scheduler teardown or reload.

## State And Persistence
This header owns no state, but every function it declares manipulates PF devlink state: the devlink private PF object, registered devlink params, devlink ports, devlink regions, and cached devlink-rate pointers on scheduler nodes. Persistent behavior is mediated by the implementation, especially NVM-backed scheduler-layer settings and firmware activation.

## Dependencies And Integration Points
The header assumes `struct device`, `struct devlink`, `struct ice_pf`, `struct ice_sf_priv`, `struct ice_vf`, and `struct ice_vsi` are visible to including translation units. It is included by driver initialization, SR-IOV/VF paths, and scheduler or reset code that needs to expose or tear down devlink resources.

## Risks And Test Signals
The main risk is lifecycle mismatch: callers must pair each create/register/init with the matching destroy/unregister operation and must respect locking expectations from the implementation, especially devlink lock use around port operations. Build coverage is a strong signal because missing prototypes or type ordering errors surface immediately. Runtime signals are clean probe/remove, reload, VF creation/removal, and absence of stale devlink ports or regions after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/health.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/health.c

## Purpose
`health.c` implements ICE devlink health reporters. It converts firmware health status events, malicious-driver-detection events, and Tx hang reports into devlink health reports with diagnostic or dump payloads.

## Important APIs, Types, And Functions
`struct ice_health_status` maps firmware health status codes to user-facing descriptions, possible solutions, and labels for two auxiliary data words. `ice_health_status_lookup[]` must remain sorted because `ice_get_health_status()` uses `bsearch()`. `ice_describe_status_code()` formats syndrome, description, solution, and internal data into a `devlink_fmsg`.

Firmware and port health reporters use `ice_fw_reporter_diagnose()`, `ice_fw_reporter_dump()`, `ice_port_reporter_diagnose()`, and `ice_port_reporter_dump()` against the last stored firmware or port health element in `pf->health_reporters`. `ice_process_health_status_event()` validates the firmware-provided element count, classifies global versus PF/port event sources, stores the last element, and reports through devlink. Unknown health codes are logged at debug level as internal-only events.

MDD reporting uses `struct ice_mdd_event`, `ice_mdd_src_to_str()`, `ice_mdd_reporter_dump()`, and `ice_report_mdd_event()`. Tx hang reporting uses a pre-filled `struct ice_health_tx_hang_buf`, then `ice_report_tx_hang()` builds a dump with queue indices, descriptor pointers, descriptor binary data, and skb data.

## Control Flow
`ice_health_init()` creates MDD and Tx hang reporters unconditionally, then creates firmware and port reporters only when firmware health reporting is supported. It enables firmware health event delivery via `ice_aq_set_health_status_cfg()`. On event reception, the AQ event handler calls `ice_process_health_status_event()`, which copies relevant status data and invokes `devlink_health_report()`. `ice_health_deinit()` destroys reporters and disables firmware event delivery. `ice_health_clear()` marks MDD and Tx hang reporters healthy after reset.

## State And Persistence
The health state lives in `pf->health_reporters`: reporter pointers, the Tx hang staging buffer, and the last firmware/port health status elements. It is runtime diagnostic state only. Firmware event enablement is programmed through the admin queue and is disabled at deinit.

## Dependencies And Integration Points
This file depends on devlink health APIs, `ice_adminq_cmd.h` health status enums and event buffer structures, `ice.h` PF/ring definitions, and firmware admin queue helpers. It integrates with AQ event processing, MDD detection, Tx timeout handling, and reset recovery.

## Risks And Test Signals
Risks include the sorted lookup table requirement, event count validation, pointer lifetime for Tx hang ring/skb dump data, and the fact that firmware/port reporters are conditional on firmware support. Test signals include health event injection or firmware-triggered health reports, `devlink health show/dump/diagnose`, Tx hang report dumps with descriptor payloads, MDD reports, and clean reporter destruction on remove or reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/health.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/health.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/health.h

## Purpose
`health.h` defines the ICE devlink health interface and the PF-owned health state container. It lets the rest of the driver initialize health reporters and report firmware health, MDD, and Tx hang events without depending on implementation details in `health.c`.

## Important APIs, Types, And Functions
`enum ice_mdd_src` names the hardware source blocks for MDD events: TX PQM, TX TCLAN, TX TDPU, and RX. `struct ice_health` stores reporter pointers for firmware, MDD, port, and Tx hang reporters, a grouped Tx hang staging buffer, and the last firmware and port admin-queue health elements.

The public functions are `ice_process_health_status_event()`, `ice_health_init()`, `ice_health_deinit()`, `ice_health_clear()`, `ice_prep_tx_hang_report()`, `ice_report_mdd_event()`, and `ice_report_tx_hang()`.

## Control Flow
Driver startup initializes `struct ice_health` as part of PF setup. Firmware AQ health events are routed to `ice_process_health_status_event()`. Tx timeout code first calls `ice_prep_tx_hang_report()` from a context where allocating or dumping may be unsuitable, then reports later via `ice_report_tx_hang()`. MDD detection calls `ice_report_mdd_event()` directly with event metadata. Reset completion calls `ice_health_clear()` to mark transient reporters healthy.

## State And Persistence
All state is runtime PF state. The grouped `tx_hang_buf` is intentionally preallocated inside `struct ice_health` to carry minimal hang metadata from constrained contexts into the devlink reporter path. Firmware and port status elements hold the last known syndrome for diagnose/dump.

## Dependencies And Integration Points
The header forward-declares admin-queue health elements, PF, Tx ring, and receive queue event info to minimize includes, but includes Linux types. It is included by `ice.h`, making `struct ice_health` part of the central `struct ice_pf` layout.

## Risks And Test Signals
Layout changes in `struct ice_health` affect `struct ice_pf`. The Tx hang buffer depends on the referenced ring remaining valid until report generation. Test signals are build coverage, successful reporter initialization/deinitialization, and devlink health dumps for each event type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/health.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/port.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/port.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice.h

## Purpose
`ice.h` is the central driver-private header for the ICE Linux Ethernet driver. For this subset, it supplies the shared PF/VSI data model that devlink, health, adapter sharing, and ARFS operate on.

## Important APIs, Types, And Functions
The file defines constants for queue descriptors, MSI-X minima, queue mapping, reset waiting, MTU/TSO limits, switch filter priorities, and Flow Director statistics. Iteration macros cover VSIs, Tx/Rx/XDP queues, allocated queues, q_vectors, and channel traffic classes.

Key types include `enum ice_feature`, `struct ice_channel`, `struct ice_txq_meta`, `struct ice_tc_cfg`, `struct ice_qs_cfg`, `struct ice_sw`, `enum ice_pf_state`, `enum ice_vsi_state`, `struct ice_vsi`, `struct ice_q_vector`, `enum ice_pf_flags`, `struct ice_eswitch`, `struct ice_adapter` pointer usage, `struct ice_pf_msix`, and the central `struct ice_pf`. `struct ice_pf` owns devlink regions, the PF devlink port, adapter reference, VSI array, queue bitmaps, locks, reset counters, hardware object, eswitch state, dynamic SF xarrays, DPLL/hwmon/health state, and RDMA core device info.

Inline helpers include `ice_irq_dynamic_ena()`, `ice_netdev_to_pf()`, XDP/XSK helpers, `ice_get_max_txq()`, `ice_get_max_rxq()`, `ice_get_main_vsi()`, `ice_get_ctrl_vsi()`, `ice_find_vsi()`, `ice_is_switchdev_running()`, `ice_is_adq_active()`, RDMA capability setters, and primary/dual NAC helpers.

## Control Flow
Most implementation files include `ice.h` to access PF/VSI state and common helpers. Devlink reload uses `ice_get_main_vsi()`, state flags, init/deinit prototypes, and ADQ checks. Port code uses PF dynamic-port xarrays and VSI state. Health stores `struct ice_health` inside `struct ice_pf`. ARFS stores filter tables and counters inside the PF VSI.

## State And Persistence
This file defines runtime state more than behavior. Persistent effects are represented indirectly through fields such as NVM PHY types, link default override, RDMA enable flags, eswitch mode, and hardware capabilities mirrored from firmware. Reset state bits and counters govern rebuild behavior. Locks define concurrency domains: queue allocation, switch/VSI allocation, TC changes, auxiliary device access, LAG, AQ wait lists, xarray-backed dynamic ports, and health reporter state.

## Dependencies And Integration Points
`ice.h` pulls in Linux netdevice, PCI, devlink, XDP, tc, bridge, tunnel, auxiliary bus, CPU rmap, and many ICE internal headers. It is the integration hub for devlink, health, ARFS, adapter sharing, scheduler, RDMA, SR-IOV, eswitch, PTP, DPLL, GNSS, and queue management.

## Risks And Test Signals
Because this header defines central layouts, changes have broad ABI and compile impact inside the driver. Risks include cacheline/layout churn, incorrect state bit ordering before `ICE_STATE_NOMINAL_CHECK_BITS`, lock misuse, stale PF/VSI pointer access during reset, and helper assumptions such as `pf->vsi[0]` being the main VSI. Test signals include full driver build, probe/remove, reset/reload, SR-IOV and switchdev scenarios, XDP/XSK queue setup, RDMA enable/disable, and ARFS/RFS acceleration operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adapter.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adapter.c

## Purpose
`ice_adapter.c` manages shared `struct ice_adapter` objects across PFs belonging to the same physical adapter. This lets multiple PCI functions coordinate shared hardware resources such as PTP and Tx queue context registers.

## Important APIs, Types, And Functions
The file owns a global `DEFINE_XARRAY(ice_adapters)` and `DEFINE_MUTEX(ice_adapters_mutex)`. `ice_adapter_index()` computes a 64-bit adapter identity: most devices use PCI DSN with the fixed-index bit cleared, while E825C device IDs use a fixed index because each NAC can have a unique DSN while still sharing a clock source. `ice_adapter_xa_index()` folds the 64-bit identity on 32-bit systems.

`ice_adapter_new()` allocates and initializes refcount, spinlocks, port-list mutex, and port list. `ice_adapter_get()` loads or creates a shared adapter under the global mutex, reserves the xarray slot before allocation, increments refcount on reuse, and stores new adapters. `ice_adapter_put()` decrements the refcount and erases/frees the adapter when the last PF releases it.

## Control Flow
PF probe obtains an adapter via `ice_adapter_get(pdev)` and stores it in `pf->adapter`. Remove calls `ice_adapter_put(pdev)`. All global xarray mutation is serialized by `ice_adapters_mutex`. Adapter freeing warns if the shared ports list is not empty, then destroys its mutex.

## State And Persistence
The shared adapter state is runtime-only. It includes `refcount`, PTP GLTSYN time spinlock, Tx queue context spinlock, optional control PF pointer, shared ports list, and cached 64-bit index used for collision detection. No state survives driver unload.

## Dependencies And Integration Points
The file depends on Linux xarray, mutex, refcount, spinlock, PCI DSN, ICE device IDs, and `struct ice_adapter` from `ice_adapter.h`. It integrates with `ice.h` through `pf->adapter` and helper code such as `ice_get_primary_hw()`, which may use the adapter control PF.

## Risks And Test Signals
Risks include xarray index collisions on 32-bit systems, incorrect E825C sharing assumptions, reference leaks, freeing while ports remain linked, and missing `ice_adapter_put()` on probe unwind. Test signals include multi-PF probe/remove ordering, E825C dual-NAC behavior, lockdep coverage for shared locks, and refcount/xarray warnings on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adapter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adapter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adapter.h

## Purpose
`ice_adapter.h` defines the shared adapter data structure and its reference-management API. It abstracts resources that are common to multiple PFs on the same physical ICE adapter.

## Important APIs, Types, And Functions
`struct ice_port_list` wraps a list of ports with a mutex. `struct ice_adapter` contains a refcount, spinlocks for GLTSYN_TIME and GLCOMM_QTX_CNTX_CTL access, a control PF pointer, shared port list, and cached 64-bit adapter index. The public API is `ice_adapter_get()` and `ice_adapter_put()`.

## Control Flow
PF probe gets an adapter reference and stores it in `struct ice_pf`. PF remove releases the reference. Consumers use the embedded locks to serialize access to shared hardware registers and use the ports list to coordinate adapter-level port relationships.

## State And Persistence
All adapter fields are runtime state. `refcount` is the ownership mechanism; `ctrl_pf` identifies the control PF when one is selected; `ports` tracks adapter ports; the index identifies which PFs share the object.

## Dependencies And Integration Points
The header uses Linux type, spinlock, and refcount declarations and forward-declares PCI and PF types. It is included by `ice.h`, making the adapter pointer available throughout the driver.

## Risks And Test Signals
Risks include lock ordering against PF locks, stale `ctrl_pf`, and port-list lifetime mismatches. Test signals include multi-function probe/remove, PTP operations on shared timer registers, and no adapter free warnings about non-empty port lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adapter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adminq_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adminq_cmd.h

## Purpose
`ice_adminq_cmd.h` is the firmware/software ABI definition for ICE Admin Queue commands, response buffers, event payloads, opcodes, and bitfields. The devlink and health files in this subset rely on it for port options, NVM activation, scheduler topology, local forwarding, CGU information, and health status events.

## Important APIs, Types, And Functions
The header defines packed context buffers for Rx, Tx, full Tx, and TxTime queue contexts. It then declares descriptor and indirect-buffer formats for command families: MAC management, switch configuration, port parameters, resource allocation, VLAN mode, VSI add/update/free, recipes and switch rules, DCB/PFC, Tx scheduler topology and rate profiles, PHY/link commands, link topology/I2C/SFF, port options, NVM read/write/activate, PF/VF mailbox, LLDP, RSS, sideband, Tx queue handling, package download/info, CGU/DPLL, driver shared parameters, LAN overflow, and health status.

Notable subset-relevant definitions include `enum ice_local_fwd_mode`, `struct ice_aqc_get_port_options`, `struct ice_aqc_get_port_options_elem`, `struct ice_aqc_set_port_option`, NVM activation flags such as `ICE_AQC_NVM_ACTIV_REQ_EMPR`, `ICE_AQC_NVM_TX_TOPO_MOD_ID` and `struct ice_aqc_nvm_tx_topo_user_sel`, CGU info structures, health status masks/codes/scopes, `struct ice_aqc_health_status_elem`, and `enum ice_adminq_opc`.

## Control Flow
Implementation files populate these structures, convert fields with little-endian helpers, and submit them through common AQ wrappers. Indirect commands carry DMA buffer addresses in `addr_high`/`addr_low`; direct commands fit in the 16-byte descriptor payload. The opcode enum selects firmware operations.

## State And Persistence
The header itself owns no state, but it defines persistent hardware and NVM state transitions: NVM writes and activation, port option persistence, Tx scheduler topology selection, LLDP persistence flags, PHY/link configuration, and package data. It also defines volatile event payloads such as link, health, LAN overflow, and LLDP events.

## Dependencies And Integration Points
It depends on `libie/adminq.h` for shared Intel admin queue definitions and Linux types/macros. It is consumed by nearly every hardware-facing ICE module, including devlink info/regions/reload, port splitting, health reporting, scheduler setup, RSS, VSI configuration, and queue programming.

## Risks And Test Signals
Risks are ABI drift against firmware, incorrect packing/alignment, endian mistakes, wrong bit masks, and variable-length flexible-array buffer sizing. Test signals include compile-time `static_assert` coverage where present, AQ command success/failure telemetry, firmware compatibility tests, devlink port split and NVM activation behavior, health event decoding, scheduler operations, RSS configuration, and broad hardware regression on multiple ICE device families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adminq_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_arfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_arfs.c

## Purpose
`ice_arfs.c` implements accelerated Receive Flow Steering for the PF VSI when `CONFIG_RFS_ACCEL` is enabled. It converts Linux RFS flow-steer requests into ICE Flow Director perfect filters and periodically syncs pending filter additions/deletions to hardware.

## Important APIs, Types, And Functions
`ice_is_arfs_active()` checks whether the PF VSI has an ARFS hash table. `ice_rx_flow_steer()` is the netdev callback that validates an skb, extracts 4-tuple flow keys, checks Flow Director perfect-filter availability, finds or creates an `ice_arfs_entry`, updates queue selection, and schedules the service task. `ice_sync_arfs_fltrs()` scans all hash buckets, builds temporary add/delete lists under `arfs_lock`, then performs hardware programming outside the spinlock.

Hardware add/delete is performed by `ice_arfs_add_flow_rules()` and `ice_arfs_del_flow_rules()` through `ice_fdir_write_fltr()`. Active counters are maintained by `ice_arfs_update_active_fltr_cntrs()` and queried by `ice_is_arfs_using_perfect_flow()` so Flow Director can avoid conflicts. `ice_arfs_is_flow_expired()` uses `rps_may_expire_flow()` and a five-second UDP activation window. Initialization and teardown are handled by `ice_init_arfs()`, `ice_clear_arfs()`, `ice_remove_arfs()`, and `ice_rebuild_arfs()`.

## Control Flow
On initialization, the PF VSI allocates a 1024-bucket hlist table, active counters, last-filter-id atomic, and spinlock. When the networking stack asks to steer a flow, the driver rejects encapsulated, unsupported, fragmented IPv4, non-TCP/UDP, or unavailable perfect-flow cases. Existing active entries with a changed queue are marked inactive and their active counter is decremented. New entries are inserted as inactive. The service task later transitions inactive entries to active and programs Flow Director rules; expired active entries move to delete lists and are removed from hardware and memory.

## State And Persistence
State is runtime-only in the PF VSI: `arfs_fltr_list`, `arfs_fltr_cntrs`, `arfs_lock`, and `arfs_last_fltr_id`. Each entry stores Flow Director filter info, hlist node, optional UDP activation time, Linux flow id, and state (`INACTIVE`, `ACTIVE`, `TODEL`). Filter IDs wrap modulo `RPS_NO_FILTER`.

## Dependencies And Integration Points
The file depends on Linux RFS/RPS, skb flow dissector, IP/IPv6/TCP/UDP parsing, netdev CPU rmap support, ICE Flow Director programming, service task scheduling, and PF/VSI definitions from `ice.h`.

## Risks And Test Signals
Risks include active counter imbalance on update/delete failures, stale entries after reset, memory allocation under `GFP_ATOMIC`, races around hash-table mutation, UDP expiration timing, and conflicts with user-programmed Flow Director perfect filters. Test signals include `CONFIG_RFS_ACCEL` builds, `ndo_rx_flow_steer` behavior, RFS CPU rmap setup, Flow Director add/delete success, reset rebuild cleanup, and traffic steering moving flows to expected Rx queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_arfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_arfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_arfs.h

## Purpose
`ice_arfs.h` defines the accelerated RFS data structures and the conditional public API for ARFS support in the ICE driver.

## Important APIs, Types, And Functions
`enum ice_arfs_fltr_state` defines the software lifecycle for ARFS filters: inactive, active, and to-delete. `struct ice_arfs_entry` stores the Flow Director filter payload, hash-list node, UDP activation timestamp, flow id, and state. `struct ice_arfs_entry_ptr` is a temporary pointer wrapper used for add lists so entries can remain in the hash table while hardware programming occurs. `struct ice_arfs_active_fltr_cntrs` tracks active TCP/UDP IPv4/IPv6 perfect-filter counts with atomics.

When `CONFIG_RFS_ACCEL` is enabled, the header declares the ARFS lifecycle, sync, CPU rmap, flow-steer, and Flow Director conflict-query functions. When disabled, it provides no-op or `-EOPNOTSUPP` inline stubs.

## Control Flow
The conditional API lets the rest of the driver call ARFS hooks unconditionally. Enabled builds allocate state on the PF VSI, accept flow-steer callbacks, and sync filters through the service task. Disabled builds compile those call sites out to inert behavior.

## State And Persistence
The header defines runtime ARFS state only. The fields live in `struct ice_vsi` via pointers declared in `ice.h`; no ARFS state persists across reset or driver reload.

## Dependencies And Integration Points
It includes `ice_fdir.h` because ARFS entries are programmed as Flow Director filters. The public API integrates with netdev RFS acceleration, PF/VSI setup and teardown, reset rebuild, and Flow Director perfect-filter management.

## Risks And Test Signals
Risks include keeping stubs semantically aligned with enabled behavior, filter state mismatches, and active counter misuse. Test signals include builds with and without `CONFIG_RFS_ACCEL`, RFS steering callbacks returning filter IDs, and correct cleanup on reset/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_arfs.h -->

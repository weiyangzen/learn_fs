# subset-b-005444 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tb.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/tb.c

## Purpose
`tb.c` is the software connection manager for the Thunderbolt/USB4 domain. It is independent of the NHI transport details and is responsible for discovering routers behind the host router, reacting to hotplug and control-channel notifications, creating and destroying protocol tunnels, managing DisplayPort resources and bandwidth, handling asymmetric Gen 4 link transitions, and restoring topology state across system and runtime power transitions.

The file owns the connection-manager private state in `struct tb_cm`: an active tunnel list, a DP resource list, the `hotplug_active` gate used to drain asynchronous work during lifecycle transitions, a delayed removal worker, and seven USB4 DP bandwidth groups. It plugs this behavior into the domain core through the local `tb_cm_ops` table and is instantiated by `tb_probe()`.

## Important APIs, Types, and Functions
- `struct tb_cm` stores the software CM's runtime state: `tunnel_list`, `dp_resources`, `hotplug_active`, `remove_work`, and `groups`.
- `struct tb_hotplug_event` is the delayed-work payload used both for plug/unplug work and DP bandwidth request work. It carries a domain pointer, route, port, unplug flag, and retry counter.
- Startup and teardown entry points are `tb_start()`, `tb_stop()`, `tb_deinit()`, and `tb_probe()`.
- Power-management entry points are `tb_suspend_noirq()`, `tb_resume_noirq()`, `tb_freeze_noirq()`, `tb_thaw_noirq()`, `tb_complete()`, `tb_runtime_suspend()`, and `tb_runtime_resume()`.
- Event entry points are `tb_handle_event()`, `tb_handle_notification()`, `tb_queue_hotplug()`, `tb_handle_hotplug()`, `tb_queue_dp_bandwidth_request()`, and `tb_handle_dp_bandwidth_request()`.
- Topology discovery is done by `tb_scan_switch()`, `tb_scan_port()`, `tb_configure_link()`, `tb_scan_xdomain()`, `tb_switch_discover_tunnels()`, and `tb_discover_tunnels()`.
- Tunnel setup/teardown is handled by `tb_tunnel_usb3()`, `tb_create_usb3_tunnels()`, `tb_tunnel_pci()`, `tb_disconnect_pci()`, `tb_tunnel_dp()`, `tb_tunnel_one_dp()`, `tb_approve_xdomain_paths()`, `tb_disconnect_xdomain_paths()`, and `tb_deactivate_and_free_tunnel()`.
- Bandwidth and link-width management centers on `tb_available_bandwidth()`, `tb_consumed_usb3_pcie_bandwidth()`, `tb_consumed_dp_bandwidth()`, `tb_maximum_bandwidth()`, `tb_configure_asym()`, `tb_configure_sym()`, `tb_alloc_dp_bandwidth()`, `tb_recalc_estimated_bandwidth()`, and the bandwidth-group helpers.
- CLx and TMU policy is wrapped by `tb_enable_clx()`, `tb_disable_clx()`, `tb_enable_tmu()`, `tb_increase_tmu_accuracy()`, and `tb_restore_children()`.

## Control Flow
`tb_probe()` allocates a Thunderbolt domain with space for `struct tb_cm`, sets the security level based on whether ACPI allows PCIe tunneling, installs `tb_cm_ops`, initializes the tunnel and DP-resource lists, initializes delayed workers and bandwidth groups, and attempts to create PM dependency links for tunneled native ports through Apple-specific or ACPI helpers.

`tb_start()` allocates the root router at route 0, configures and adds it, configures the host TMU for low-resolution mode, and decides whether to discover existing firmware-created topology or reset USB4 state. In discovery mode it scans the topology, discovers firmware-created tunnels, suppresses switch uevents until authorization state is known, discovers DP resources for firmware-created DP tunnels, creates missing USB3 tunnels, adds root DP IN resources, enters redrive mode if needed, emits delayed switch add uevents, and finally sets `hotplug_active` so queued hotplug work may progress.

Hotplug notifications enter through `tb_handle_event()`. Plug events are acknowledged with `tb_cfg_ack_plug()` and queued to `tb->wq`; selected error notifications are acknowledged with `tb_cfg_ack_notification()`, with DP bandwidth errors queueing DP bandwidth work. `tb_handle_hotplug()` runtime-resumes the domain, locks `tb->lock`, validates the route and port, skips upstream ports, runtime-resumes the router, and then handles several cases: router unplug, XDomain unplug, DP resource loss, xHCI connect/disconnect requests, null-port scans for new routers, or DP resource availability. All topology and tunnel mutations are serialized under the domain lock.

Router scanning starts at a null lane adapter. `tb_scan_port()` waits for link presence, allocates/configures a downstream switch, removes any previous XDomain on that port, suppresses uevents during boot discovery, adds the switch, links the downstream/upstream ports, scans retimers, enables CLx/TMU, marks configuration valid, creates a USB3 tunnel for a true hotplug, adds DP resources, and recurses into the new switch. If switch allocation fails with errors that can indicate another host domain, it scans for an XDomain instead.

USB3 tunnels are created recursively with `tb_create_usb3_tunnels()`. For each USB4 router, `tb_tunnel_usb3()` finds the router USB3 UP adapter and the corresponding parent USB3 DOWN adapter, verifies the parent chain is ready, temporarily releases unused USB3 bandwidth from the first-hop tunnel, calculates available bandwidth, emits a low-bandwidth event below 1.5 Gb/s, allocates and activates a USB3 tunnel, links it into `tunnel_list`, then reclaims unused bandwidth for the parent branch.

DP tunneling is resource-driven. `tb_add_dp_resources()` records DP IN adapters that report available resources, placing device-router DP IN resources before host-router ones so external GPUs are preferred. `tb_tunnel_dp()` pairs inactive DP IN resources with suitable inactive DP OUT resources, constrained to the same host downstream branch when applicable. `tb_tunnel_one_dp()` keeps both endpoint routers awake, allocates the DP IN resource, attaches the DP IN to a bandwidth group, releases unused USB3 bandwidth, computes available bandwidth including possible asymmetric link capacity, allocates a DP tunnel, and activates it. DP activation may complete asynchronously through `tb_dp_tunnel_active()`, which validates consumed bandwidth, reclaims USB3 bandwidth, transitions links to asymmetric if needed, recalculates estimated bandwidth, and raises TMU accuracy for DP.

PCIe tunnels are policy-gated by domain approval. `tb_tunnel_pci()` finds the device PCIe UP adapter and a mapped or unused parent PCIe DOWN adapter, allocates/activates the PCIe tunnel, enables Titan Ridge PCIe L1, connects xHCI, and records the tunnel. `tb_disconnect_pci()` tears down the matching PCIe tunnel and disconnects xHCI. XDomain DMA path approval disables CLx along the path, allocates and activates a DMA tunnel between the host NHI port and the XDomain downstream port, and re-enables CLx when DMA paths are removed.

DP bandwidth allocation requests come from DPTX discovery/DP bandwidth notifications. `tb_handle_dp_bandwidth_request()` validates that the route and port refer to an active DP IN tunnel, handles the transition into USB4 DP bandwidth allocation mode, reads requested bandwidth, translates it into upstream or downstream request fields, and calls `tb_alloc_dp_bandwidth()`. That function normalizes rounded requests to the tunnel maximum, rejects impossible requests, reserves bandwidth released by smaller requests at group scope for ten seconds, releases unused USB3 capacity before larger requests, checks path availability, transitions links asymmetric when required, writes the new tunnel allocation, reclaims USB3 bandwidth, emits no-bandwidth events on failure, and retries a small number of times when the DP tunnel is not active yet.

System suspend tears down DP tunnels and resources, exits redrive, suspends the root switch hierarchy, and closes the hotplug gate. Resume resets non-USB4 hosts, resumes the root, frees invalid tunnels and unplugged children, restores CLx/TMU/link configuration, discovers and tears down firmware-created tunnels after hibernation, reactivates the driver's own tunnels, delays briefly for PCIe, re-enters redrive, and opens the hotplug gate. Runtime suspend follows a similar but lighter path under the lock; runtime resume reactivates existing tunnels and schedules delayed removal cleanup to avoid removal/runtime-resume deadlocks.

## State and Persistence Behavior
The primary persistent software state is in `tcm->tunnel_list`, `tcm->dp_resources`, and `tcm->groups`. Tunnels remain listed across many lifecycle events and are reactivated after resume/runtime resume unless invalidated or explicitly removed. DP resources are list-linked through `struct tb_port::list`; DP bandwidth group membership is stored in `struct tb_port::group` and `group_list`, with temporary released bandwidth stored in `struct tb_bandwidth_group::reserved` until its delayed release worker expires.

Per-router state is stored in `struct tb_switch` fields declared in `tb.h`: route-derived topology, link width/speed/generation, boot authorization, runtime-PM support, CLx state, TMU configuration, and unplug state. Per-port state includes remote links, XDomain pointers, HopID allocators, bandwidth group membership, max bandwidth, and redrive state. `hotplug_active` is not a hardware state flag; it is a software synchronization gate used to stop hotplug and bandwidth workers from making progress during init, suspend, runtime suspend, freeze, and shutdown.

The code does not persist state to disk. Hardware persistence is limited to router/adapter registers configured through helper APIs in other Thunderbolt files. Boot-firmware-created tunnels are either discovered and represented in `tunnel_list`, or deliberately torn down/reset when the software CM cannot trust them.

## Dependencies and Integration Points
This file depends on the domain core and common Thunderbolt object model from `tb.h`, register constants from `tb_regs.h`, and tunnel constructors/operations from `tunnel.h`. It calls into switch, port, link-controller, USB4, TMU, CLx, retimer, XDomain, NVM/domain, runtime-PM, ACPI policy, Apple platform, and control-channel helpers. Important external contracts include `tb_switch_*()`, `tb_port_*()`, `usb4_switch_*()`, `usb4_port_*()`, `usb4_dp_port_*()`, `usb4_usb3_port_*()`, `tb_tunnel_*()`, `tb_xdomain_*()`, `tb_retimer_*()`, `tb_cfg_ack_*()`, and `tb_acpi_may_tunnel_*()`.

The integration surface exposed to the rest of the driver is the `tb_cm_ops` vector. The domain core calls these hooks for startup, shutdown, suspend/resume, runtime PM, control-channel events, PCIe switch approval/disapproval, and XDomain DMA path approval/disconnection.

## Risks
- Hotplug, runtime PM, and delayed work interact heavily. Missing `hotplug_active` checks or lock coverage can race with suspend, shutdown, or device removal.
- DP bandwidth logic is complex and direction-sensitive. A mistake in upstream/downstream accounting, group reservation handling, rounded DP bandwidth, or USB3 reclaim/release sequencing can overcommit links or incorrectly deny bandwidth.
- Asymmetric link transitions temporarily disable CLx. Failures during `tb_configure_asym()` or `tb_configure_sym()` can leave performance or power state different than intended.
- DP resources are tracked with embedded list nodes in `struct tb_port`; double-add, stale list membership, or missing `list_del_init()` would corrupt global resource lists.
- Boot firmware tunnel discovery and hibernation cleanup intentionally tear down tunnels that may exist in hardware. Incorrect tunnel discovery can disrupt devices or leave stale paths active.
- XDomain DMA path handling disables CLx for correctness, and cleanup only re-enables it opportunistically. Multiple DMA tunnels sharing a path must be covered by the guard in `tb_enable_clx()`.
- The Apple PCIe device-link fallback is platform and PCI-topology specific. Missing links cause a warning because resume ordering can break tunnel re-establishment.
- Many helper calls ignore non-fatal failures with warnings to keep topology usable. Tests need to distinguish acceptable degraded operation from silently lost functionality.

## Test Signals
Useful test signals include successful cold-plug discovery of a router chain, suppression then emission of switch uevents during boot discovery, hotplug add/remove of single-lane and dual-lane routers, XDomain connect/disconnect, DP IN/OUT hotplug pairing and fallback, DP activation failure causing resource removal, PCIe approval/disapproval, USB3 tunnel creation under chained USB4 routers, and xHCI connect/disconnect notifications.

Bandwidth-specific tests should exercise DP bandwidth allocation mode enable, no-active-request estimated bandwidth recalculation, larger requests that borrow group reserved bandwidth, smaller requests that schedule release, retries while DP activation is in progress, no-bandwidth failure events, USB3 release/reclaim around DP changes, and Gen 4 symmetric/asymmetric transitions around `asym_threshold`.

Power-management tests should cover system suspend/resume, hibernation-style firmware-created tunnel cleanup, runtime suspend/resume with unplug during suspend, delayed `remove_work`, redrive enter/exit, retimer rescans, CLx/TMU restoration, and no progress from queued hotplug work while `hotplug_active` is false. Dynamic debug logs from `tb_dbg`, `tb_sw_dbg`, `tb_port_dbg`, tunnel events, runtime PM reference leaks, and link width/allocated bandwidth registers are practical observability points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tb.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/tb.h

## Purpose
`tb.h` is the central private interface for the Thunderbolt/USB4 driver. It defines the kernel-side object model for domains, routers, adapters, USB4 port devices, retimers, NVM images, paths, bandwidth groups, and connection-manager callbacks. It also declares most cross-file helper APIs used by the software connection manager, ICM firmware manager, switch/port code, USB4 router operations, retimer/NVM code, XDomain support, ACPI integration, and debugfs.

In USB4 terminology, `struct tb_switch` represents a router and `struct tb_port` represents an adapter or lane adapter. The header preserves Thunderbolt naming for existing driver code while documenting the USB4 mapping.

## Important APIs, Types, and Functions
- Quirk bits `QUIRK_FORCE_POWER_LINK_CONTROLLER`, `QUIRK_NO_CLX`, and `QUIRK_KEEP_POWER_IN_DP_REDRIVE` describe router-specific behavior needed by power, CLx, and redrive handling.
- `struct tb_nvm` and `enum tb_nvm_write_ops` model active/non-active NVM partitions, buffered writes, authentication state, and vendor operations.
- `enum tb_switch_tmu_mode` and `struct tb_switch_tmu` describe router Time Management Unit modes and requested/current state.
- `struct tb_switch` stores device identity, configuration-space header, ports, DMA/NVM/TMU/CLx state, topology fields, authorization/security state, runtime-PM fields, link parameters, credit preferences, quirks, and debugfs state.
- `struct tb_bandwidth_group` stores a group ID, member DP IN ports, temporary reserved bandwidth, and delayed release work.
- `struct tb_port` stores cached port registers, owning switch, remote router link, XDomain link, capability offsets, USB4 port device, lane-bonding data, HopID allocators, list nodes, credit state, DP bandwidth group state, maximum bandwidth, and redrive state.
- `struct usb4_port` and `struct tb_retimer` define child devices for USB4 lane adapters and retimers.
- `struct tb_path_hop`, `enum tb_path_port`, and `struct tb_path` define hop programming and unidirectional path state for protocol tunnels.
- `struct tb_cm_ops` is the connection-manager vtable used by the domain core to abstract software CM and firmware ICM behavior.
- Inline helpers such as `tb_priv()`, `tb_upstream_port()`, `tb_is_upstream_port()`, `tb_route()`, `tb_port_at()`, `tb_width_name()`, `tb_port_has_remote()`, type predicates, `tb_sw_read()`, `tb_sw_write()`, `tb_port_read()`, `tb_port_write()`, `tb_switch_parent()`, `tb_switch_downstream_port()`, `tb_route_length()`, and `tb_downstream_route()` centralize common topology and config-space operations.
- Iteration macros `tb_switch_for_each_port()`, `tb_for_each_port_on_path()`, `tb_for_each_upstream_port_on_path()`, and `tb_path_for_each_hop()` encode traversal contracts.

## Control Flow
`tb.h` itself has no runtime control flow, but it defines the contracts used by every runtime path. Domain allocation installs a `struct tb_cm_ops`; the domain core then calls connection-manager callbacks for start/stop, suspend/resume, runtime PM, events, authorization, PCIe disapproval, XDomain path approval, and USB4 router operation proxying. The software CM in `tb.c` fills this table with `tb_start()`, `tb_stop()`, `tb_handle_event()`, tunnel approval functions, and power hooks.

Topology traversal relies on route encoding. `tb_route()` combines `route_hi` and `route_lo` from the cached switch header. `tb_port_at()` extracts the port number for a switch depth from a route and returns the corresponding `struct tb_port`. `tb_downstream_route()` appends a downstream port number at the current switch depth. These helpers are used during scanning, event routing, XDomain setup, and path construction.

Config-space access is wrapped by `tb_sw_read()`, `tb_sw_write()`, `tb_port_read()`, and `tb_port_write()`. These helpers check `sw->is_unplugged` before issuing control-channel reads/writes, reducing the chance that removal paths continue touching gone hardware.

Path and tunnel code uses `struct tb_path` and `struct tb_path_hop` to program hop entries from ingress adapters to egress adapters. Higher-level tunnel constructors in `tunnel.h` build protocol-specific collections of paths using the port and path helper APIs declared here.

## State and Persistence Behavior
Most persistent in-memory Thunderbolt state is represented by structures in this header. `struct tb_switch` persists router identity, topology, link state, authorization, NVM pointers, runtime-PM support, and capability offsets for as long as the device is registered. `struct tb_port` persists adapter state and is embedded in the owning switch's `ports` array. `struct tb_path` persists programmed tunnel path state until deactivated and freed. `struct tb_nvm` persists buffered firmware update state until NVM cleanup.

The header also encodes state ownership expectations. `struct tb_nvm` documentation states that users must serialize concurrent access. Switch add/remove operations require the domain lock when modifying other switches. HopID allocators belong to ports. DP bandwidth group membership is stored on DP IN ports and in group lists. Runtime-PM completions and ICM connection identifiers are stored in `struct tb_switch` for firmware-managed domains.

No disk persistence is implemented here. NVM operations declared here write to device flash through other source files; this header defines the in-memory buffers, sizes, authentication flags, and APIs.

## Dependencies and Integration Points
The header includes Linux debugfs, nvmem, PCI, Thunderbolt UAPI, UUID, bitfield, and local `tb_regs.h`, `ctl.h`, and `dma_port.h`. It exposes a broad internal API surface to many driver compilation units: domain lifecycle, switch/port config, path programming, DROM, link controller, USB4 router operations, USB4 sideband/margining, retimer NVM, USB3/DP bandwidth, PCIe encapsulation, ACPI policy, debugfs, and quirks.

`tb_regs.h` supplies the packed register/config-space structures used inside `struct tb_switch`, `struct tb_port`, and register helper prototypes. `tb_msgs.h` is indirectly related through `ctl.h` and the control-channel event and config-space packet APIs.

## Risks
- Many packed register structures and bitfields are exposed through cached config headers. ABI drift with hardware specs can silently break topology parsing.
- `tb_port_at()` warns and returns NULL if the encoded port exceeds `max_port_number`; callers must handle NULL in hotplug/XDomain paths.
- Inline config-space helpers only guard `is_unplugged`; they do not serialize access. Callers must use domain locks and runtime-PM references appropriately.
- Several structures expose raw pointers and embedded list nodes. Ownership is implicit and cross-file, making double removal, stale pointers, or list corruption possible if contracts are violated.
- The broad prototype surface makes layering loose. Changes to router, port, USB4, XDomain, retimer, NVM, or tunnel behavior can affect `tb.c` without compiler-visible semantic checks.
- ACPI and debugfs fallback inline stubs change behavior depending on Kconfig, so tests need coverage with and without `CONFIG_ACPI` and `CONFIG_DEBUG_FS`.

## Test Signals
Compile coverage is a major signal because this header is included across the Thunderbolt driver. Runtime tests should validate route encoding/decoding, port type predicates, parent/downstream-port helpers, config-space read/write rejection after unplug, switch generation/vendor predicates, TMU and CLx state helpers, path iteration over multi-hop topologies, USB4 version detection, and ACPI/debugfs stub behavior under different configurations.

For integration, hotplug, suspend/resume, NVM update, retimer scan, USB4 sideband access, DP bandwidth allocation, PCIe tunneling, USB3 bandwidth allocation, XDomain DMA paths, and debugfs registration all exercise contracts declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tb_msgs.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/tb_msgs.h

## Purpose
`tb_msgs.h` defines the packed wire/control-channel message layouts used by Thunderbolt configuration transactions, Intel Connection Manager firmware messages, USB4 router operation proxy messages, and XDomain protocol packets. It is a protocol contract header: it carries no executable logic, but every field definition affects how packets are built, parsed, acknowledged, and routed.

## Important APIs, Types, and Functions
- `enum tb_cfg_space` identifies Thunderbolt config spaces: hops, port, switch, and counters.
- `enum tb_cfg_error` defines control-channel error and notification codes, including hotplug acknowledgement, DP bandwidth, router operation completion, PCIe wake, DP connection change, DPTX discovery, link recovery, and asymmetric link notifications.
- `struct tb_cfg_header`, `struct tb_cfg_address`, `struct cfg_read_pkg`, `struct cfg_write_pkg`, `struct cfg_error_pkg`, `struct cfg_ack_pkg`, `struct cfg_event_pkg`, and `struct cfg_reset_pkg` define base config-channel packet formats.
- `enum icm_pkg_code`, `enum icm_event_code`, `struct icm_pkg_header`, and ICM flag masks define the common Intel firmware message envelope.
- Falcon Ridge, Alpine Ridge, Titan Ridge, Ice Lake, and USB4 ICM structures define generation-specific driver-ready, topology, device connect/disconnect, XDomain, approval, key, challenge, boot ACL, RTD3 veto, and USB4 switch-op messages.
- XDomain packet definitions include `struct tb_xdomain_header`, `enum tb_xdp_type`, `struct tb_xdp_header`, UUID/property/link-state request and response structures, maximum property sizes, and `enum tb_xdp_error`.

## Control Flow
The control channel code uses the config packet structures to issue config-space reads/writes and to receive asynchronous events. `tb.c` consumes `struct cfg_event_pkg` in `tb_handle_event()` for plug/unplug events, and consumes `struct cfg_error_pkg` in `tb_handle_notification()` for notification-style errors such as DP bandwidth changes. Hotplug events are acknowledged with `TB_CFG_ERROR_ACK_PLUG_EVENT` semantics through the control helpers.

Firmware-managed domains use the ICM package definitions to negotiate driver readiness, fetch topology, approve devices, challenge devices with keys, manipulate preboot ACLs, approve or disconnect XDomains, receive device/XDomain events, and proxy USB4 router operations. Hardware generation differences are represented by separate `icm_fr_*`, `icm_ar_*`, and `icm_tr_*` structures because fields such as route, UUID, connection ID/key, security flags, and topology payloads differ across controllers.

XDomain services use the XDP structures to exchange UUIDs, properties, property-change notifications, and link-state status/change messages over DMA paths between host domains. The `length_sn` field combines length and sequence number bits; typed packet payloads then follow a common UUID/type header.

## State and Persistence Behavior
This header defines transient packet formats and constants only. It stores no persistent runtime state. Persistence is external: ICM firmware may keep ACLs, connection keys, topology state, and approval state; the Linux driver stores parsed results in `struct tb_switch`, `struct tb_xdomain`, and domain data structures defined elsewhere.

The packed structures are stateful only in the sense that they are ABI contracts. Any value written to a field is interpreted by hardware firmware, the control channel, or a peer domain according to these layouts.

## Dependencies and Integration Points
The header depends on `linux/types.h` and `linux/uuid.h`, and uses bit macros such as `BIT()` and `GENMASK()` from the broader kernel include environment. It integrates with `ctl.h` and control-channel transaction code, ICM implementation files, USB4 switch operation proxying, XDomain services, and the software CM's event path in `tb.c`.

The `tb_cfg_space` and packet structures pair with register definitions in `tb_regs.h`: config read/write packets select the config space and offsets of the register layouts defined there. ICM USB4 switch-op messages carry opcodes that correspond to USB4 router operation constants in `tb_regs.h`.

## Risks
- The structures are `__packed` and use C bitfields. Endianness, compiler bitfield layout assumptions, and ABI changes are high-risk for hardware protocol correctness.
- Multiple controller generations use similar but not identical messages. Accidentally parsing an Alpine Ridge or Titan Ridge event with the wrong structure would corrupt route, UUID, or connection fields.
- `cfg_write_pkg::data` has a fixed 64 dword maximum while `tb_regs.h` notes a smaller practical config frame limit. Callers must still respect control-channel length limits.
- XDomain property responses have variable-length trailing data and a maximum total property size. Length validation is critical before parsing.
- Error enum values include both failures and asynchronous notifications. Treating notification-style errors as fatal transaction errors would break hotplug, DP bandwidth changes, and wake handling.

## Test Signals
Protocol tests should verify structure sizes and offsets against the Thunderbolt/USB4/ICM specifications, especially packed bitfield fields. Runtime tests should cover config read/write round trips, hotplug event acknowledgement, DP bandwidth notification acknowledgement and queued handling, ICM driver-ready/topology parsing on each supported generation, device approval/challenge/key messages, boot ACL transfer, USB4 switch operation proxy messages, XDomain UUID/property/link-state request-response sequences, and rejection of malformed lengths or unknown XDP packet types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tb_msgs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/tb_regs.h

## Purpose
`tb_regs.h` defines Thunderbolt and USB4 config-space register layouts, capability IDs, port/router type constants, register offsets, bit masks, and packed hop-entry structures. It is the low-level register contract used by switch, port, path, link-controller, TMU, USB4, DP, PCIe, USB3, wake, and sideband code. The file does not perform register I/O itself; it names the offsets and fields that other files read and write through the config-channel wrappers declared in `tb.h`.

## Important APIs, Types, and Functions
- `TB_ROUTE_SHIFT` defines the 8-bit-per-port route encoding used by topology helpers.
- `TB_MAX_CONFIG_RW_LENGTH` defines the practical maximum dword count for config read/write transactions.
- Capability enums `tb_switch_cap`, `tb_switch_vse_cap`, and `tb_port_cap` identify switch and port capability chains.
- `enum tb_port_state` names PHY states such as disabled, connecting, up, CL0s, CL1, CL2, and unplugged.
- Packed capability structures include `tb_cap_basic`, `tb_cap_extended_short`, `tb_cap_extended_long`, `tb_cap_any`, `tb_cap_link_controller`, `tb_cap_phy`, `tb_eeprom_ctl`, and `tb_cap_plug_events`.
- `struct tb_regs_switch_header` and `struct tb_regs_port_header` are cached in `struct tb_switch` and `struct tb_port` respectively.
- Router register constants cover common router status/control registers, sleep/wake bits, USB4 router operation registers, and `enum usb4_switch_op`.
- TMU router and adapter constants define frequency windows, timestamp intervals, uni/enhanced modes, disable bits, and timing averages.
- `enum tb_port_type` names inactive, lane/null, NHI, DP IN/OUT, PCIe UP/DOWN, and USB3 UP/DOWN adapters.
- Adapter register constants cover basic adapter buffer/lock registers, lane link width/speed/CLx/asymmetric fields, USB4 port sideband and wake registers, DP adapter HPD/bandwidth/group/capability fields, PCIe enable/encapsulation fields, and USB3 bandwidth fields.
- `struct tb_regs_hop` defines the two-dword hop table entry used to route packets through a switch.
- Link-controller and low-power constants define plug events, PCIe command registers, CP low power fields, link controller descriptors, sink allocation, power, port mode, wake/sleep controls, link attributes, and xHCI connection requests.

## Control Flow
Register access flows through helper APIs in other files. For example, switch allocation reads `tb_regs_switch_header` from port 0 switch config space, port initialization reads `tb_regs_port_header` from each adapter, capability walkers use the capability structs and IDs, path activation writes `struct tb_regs_hop` entries in the hops config space, TMU helpers program `TMU_RTR_*` and `TMU_ADP_*` registers, USB4 router operations use `ROUTER_CS_26` fields with `enum usb4_switch_op`, and DP/USB3 bandwidth code uses the adapter-specific masks to query, estimate, request, allocate, and release bandwidth.

`tb.c` depends on these definitions indirectly through helpers. For instance, DP resource and bandwidth handling uses DP adapter group, estimated bandwidth, requested bandwidth, and allocated bandwidth fields; Gen 4 asymmetric transitions use lane adapter width masks and USB4 port asymmetric control; redrive and wake handling use DP resource and low-power/link-controller state; and tunnel path programming ultimately materializes as hop register writes.

## State and Persistence Behavior
The file defines hardware state layout, not software storage. Some values are cached into `struct tb_switch::config` and `struct tb_port::config` in memory, while most other fields are read or written directly by helper functions when needed. Hardware persists these registers until reset, unplug, firmware action, or driver reconfiguration. During suspend/resume, `tb.c` restores router/link/TMU state by calling helpers that use these register definitions.

Fields such as route, upstream port number, max port number, adapter type, max HopIDs, link width, CLx enable bits, DP group IDs, DP estimated/allocated/requested bandwidth, USB3 allocated bandwidth, and hop enable bits are the hardware-backed state that higher layers reason about.

## Dependencies and Integration Points
The header includes `linux/types.h` and relies on kernel bit helpers such as `BIT()` and `GENMASK()`. It is included by `tb.h` and used across the Thunderbolt driver. It integrates tightly with control-channel config spaces from `tb_msgs.h`: config packets choose switch, port, hops, or counters space and these constants define the offsets and bit meanings inside those spaces.

Router operation opcodes here are used by USB4 router operation helpers and by ICM USB4 switch-op proxy messages. DP register definitions feed the DP tunneling and bandwidth allocation code. Lane, TMU, low-power, and link-controller constants feed CLx/TMU/link configuration code. Hop entries feed path and tunnel activation.

## Risks
- Packed bitfield layouts must match hardware config-space definitions exactly. Any mismatch corrupts low-level router or adapter programming.
- Several fields are marked unknown or TODO. Code should avoid making assumptions beyond the named masks.
- `TB_MAX_CONFIG_RW_LENGTH` is lower than the theoretical packet data array in `tb_msgs.h`; callers must obey this practical limit.
- Duplicate-looking DP `ADP_DP_CS_8` definitions appear for bandwidth mode bits and requested bandwidth. Maintainers must avoid inconsistent edits.
- Link width and direction constants are easy to invert because upstream-port perspective differs from downstream-port and host-router perspective.
- Router and adapter registers have generation-specific semantics, especially USB4 v1/v2, Titan Ridge TMU bits, and asymmetric Gen 4 controls.

## Test Signals
Low-level tests should validate config-space reads of switch and port headers, capability-chain parsing, PHY state reads, lane speed/width reads and writes, lane bonding, CLx enable/disable, TMU configuration, USB4 router operations, hop entry programming, DP HPD/resource/bandwidth registers, USB3 bandwidth allocation/release, PCIe adapter enable and xHCI link-controller requests, wake/sleep bits, and sideband transactions.

Regression signals include correct route depth decoding, no config read/write longer than `TB_MAX_CONFIG_RW_LENGTH`, correct DP bandwidth granularity/group/estimated allocation behavior, successful asymmetric link transitions on Gen 4 hardware, and successful resume restoration of link/TMU/CLx state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tb_regs.h -->

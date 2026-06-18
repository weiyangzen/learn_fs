# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_expander.c

## Purpose

`sas_expander.c` implements libsas expander management: SMP command execution, expander and PHY discovery, route table configuration, topology validation, breadth-first discovery through expander trees, broadcast-change revalidation, hotplug add/remove, and BSG SMP forwarding to expanders. It is the main topology engine for SAS domains behind expanders.

## Important APIs, Types, and Functions

SMP execution helpers are `smp_execute_task_sg()`, `smp_execute_task()`, `alloc_smp_req()`, and `alloc_smp_resp()`. Discovery helpers include `sas_ex_general()`, `sas_ex_manuf_info()`, `sas_ex_phy_discover()`, `sas_expander_discover()`, `sas_discover_expander()`, `sas_discover_root_expander()`, `sas_ex_discover_devices()`, `sas_ex_discover_dev()`, `sas_ex_discover_end_dev()`, and `sas_ex_discover_expander()`.

Routing and PHY helpers include `sas_smp_phy_control()`, `sas_configure_phy()`, `sas_configure_parent()`, `sas_configure_routing()`, `sas_disable_routing()`, `sas_ex_disable_phy()`, `sas_ex_disable_port()`, `sas_smp_get_phy_events()`, `sas_get_report_phy_sata()`, `sas_get_phy_attached_dev()`, `sas_find_attached_phy_id()`, and `sas_ex_to_ata()`. Revalidation helpers include `sas_find_bcast_dev()`, `sas_find_bcast_phy()`, `sas_rediscover()`, `sas_rediscover_dev()`, `sas_discover_new()`, `sas_unregister_ex_tree()`, and `sas_ex_revalidate_domain()`. BSG integration is `sas_smp_handler()`.

The central structures are `struct domain_device`, `struct expander_device`, `struct ex_phy`, `struct sas_expander_device`, `struct sas_task`, `struct smp_*_resp`, `struct discover_resp`, `struct sas_phy`, `struct sas_port`, and discovery state in `struct sas_discovery`.

## Control Flow

Expander discovery begins with `sas_discover_root_expander()` adding the root rphy, setting level zero, and calling `sas_discover_expander()`. That notifies the low-level driver, issues REPORT GENERAL to learn change count, route table capacity, number of phys, self-configuration state, and enclosure ID, reads manufacturer info, allocates `ex_phy`, and performs DISCOVER for every expander PHY. Each DISCOVER response is normalized by `sas_set_ex_phy()`, which creates SAS PHY objects as needed, tracks attached type/address/linkrate/routing/change count, handles SATA pending detection, and logs meaningful changes.

After initial expander interrogation, topology validation checks subtractive boundaries and parent-child routing compatibility. Device discovery proceeds breadth-first by expander level. Each usable PHY is filtered for parent/backlink, duplicate domain addresses, empty/disabled/reset-problem states, unknown device types, and route configuration. Wide ports are joined when another PHY already points at the same attached SAS address. End devices become SATA/STP via `sas_ata_add_dev()` or SSP via `sas_ex_add_dev()`. Child expanders allocate a new SAS port and expander rphy, are added to the port device list, recursively discovered, and linked into the parent's child list.

Routing table configuration walks from a child expander up through parents. For each parent table-routed PHY leading toward the child, `sas_configure_present()` scans REPORT ROUTE INFORMATION entries for the target SAS address or a free slot, and `sas_configure_set()` sends CONFIGURE ROUTE INFORMATION to include or exclude the route. Self-configuring expanders skip explicit route table programming.

Broadcast-change revalidation starts at `sas_ex_revalidate_domain()`. It finds the expander whose change count and PHY change count changed, then iterates changed PHYs. `sas_rediscover_dev()` reads current attached address/type, removes old devices for vacant/no-phy/empty/communication-loss cases, treats SATA pending/end-device type flutter as reset noise, and otherwise unregisters the old device and discovers the new one. Removal tears down child expander subtrees recursively, disables routing for removed SAS addresses, removes PHYs from wide ports, and queues empty SAS ports for later deletion.

`sas_smp_handler()` services BSG SMP requests. If there is no rphy it delegates to the host SMP interpreter. For expander rphys it finds the matching domain device, rejects multi-segment payloads, executes the SMP task through the low-level driver, and reports received length based on underrun.

## State and Persistence Behavior

Expander state is volatile in `domain_device.ex_dev`: number of phys, route indexes, change count, t2t support, route-table configuration mode, self-configuring flag, enclosure logical ID, allocated `ex_phy` array, parent port, and child list. Each `ex_phy` stores attached SAS address, attached type/protocols, link rates, routing attribute, change count, last direct-address route index, SAS PHY object, SAS port, and phy state. Discovery-level state stores fanout and edge-expander boundary addresses and maximum BFS level. Route table changes are programmed into expanders and therefore affect hardware fabric state, but this file does not persist data across driver reloads.

SMP commands are serialized per expander by `ex_dev.cmd_mutex` and bracketed by runtime PM references. Slow tasks have timers and completions; failed or timed-out tasks are aborted through low-level callbacks.

## Dependencies and Integration Points

The file depends on libsas task execution callbacks, SAS transport rphy/phy/port objects, SMP protocol definitions, libata SATA helper hooks, SCSI BSG jobs, runtime PM, and the low-level driver's `lldd_execute_task()` and `lldd_abort_task()`. It calls into `sas_discover.c` for device notification/unregistration and into `sas_ata.c` for SATA/STP device creation and SATA FIS reporting.

## Risks and Edge Cases

SMP execution retries and timeout handling are delicate: the function frees tasks after completion, abort, underrun, overrun, or unknown-device responses and has a `BUG_ON` if retry accounting leaves a task live. `sas_set_ex_phy()` intentionally avoids mutating much state while ATA EH is active and instead marks revalidation pending; missing this guard can conflict with libata reset polling. Topology rules for fanout, edge expanders, table/subtractive routing, EEDS, and duplicate SAS addresses can disable ports or phys; incorrect detection may hide devices. Route table scanning uses the first free slot or remembered direct-address index, so expanders with inconsistent REPORT ROUTE INFO behavior can cause failed routing. Wide-port removal must avoid unregistering the child until the last PHY disappears.

## Test Signals

Strong test signals include REPORT GENERAL/manufacturer/DISCOVER parsing, discovery through multi-level expanders, SATA pending transitions, wide-port creation/removal, duplicate SAS address disabling, fanout and edge topology rule enforcement, route table include/exclude programming, self-configuring expander behavior, broadcast-change hot-add/hot-remove, subtree removal, PHY error counter reads, REPORT PHY SATA endian fixups, BSG SMP passthrough and host fallback, SMP timeouts/underruns/overruns, and runtime PM balance during SMP tasks.

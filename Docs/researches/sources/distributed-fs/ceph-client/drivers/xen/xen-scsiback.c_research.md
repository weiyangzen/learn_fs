# sources/distributed-fs/ceph-client/drivers/xen/xen-scsiback.c

## Purpose
`xen-scsiback.c` is the Xen paravirtual SCSI backend. It exposes Linux target-core LUNs to Xen frontends through the `vscsi` Xenbus protocol, translates guest virtual SCSI IDs to target portal groups and LUNs, maps guest grant pages into scatterlists, submits SCSI CDBs or task-management requests to target core, and returns responses on the shared ring.

## Important APIs, Types, And Functions
Main structures are `vscsibk_info` for one Xenbus backend instance, `vscsibk_pend` for an in-flight request, `v2p_entry` for virtual-to-physical LUN translation, and target-core objects `scsiback_tport`, `scsiback_tpg`, and `scsiback_nexus`. Request flow uses `scsiback_irq_fn()`, `scsiback_do_cmd_fn()`, `prepare_pending_reqs()`, `scsiback_gnttab_data_map()`, `scsiback_cmd_exec()`, `scsiback_cmd_done()`, and `scsiback_send_response()`. Xenbus lifecycle uses `scsiback_probe()`, `scsiback_frontend_changed()`, `scsiback_map()`, `scsiback_disconnect()`, and `scsiback_remove()`. Target configfs integration is the `target_core_fabric_ops scsiback_ops` table.

## Control Flow
Probe allocates `vscsibk_info`, initializes locks/lists/page cache, advertises `feature-sg-grant`, and enters `InitWait`. When the frontend reaches `Initialised`, the backend reads `ring-ref` and `event-channel`, maps the ring, binds a late-EOI threaded IRQ, processes configured `vscsi-devs`, and switches to `Connected`. IRQ handling drains ring requests until none remain or a ring error occurs. Each CDB maps direct or grant-backed SG descriptors, validates offsets/lengths, obtains a target-core session tag, submits the command, and later completes through `queue_data_in` or `queue_status`. Abort/reset requests become target TMRs. Reconfiguring scans `vscsi-devs` for LUN add/remove and reports `Reconfigured`.

## State And Persistence
Runtime state is per backend instance: mapped ring, IRQ, unreplied request count, v2p translation list, and grant page cache. Translation entries kref target portal groups and increment frontend-use counters so active frontends block nexus deletion. Xenstore persists vSCSI device state under `vscsi-devs/<entry>/state`, physical target strings in `p-dev`, virtual IDs in `v-dev`, feature flags, and Xenbus state. Configfs persists operator-created target ports, portal groups, aliases, nexus, and LUN links through target core.

## Dependencies And Integration Points
The file depends on Xenbus, Xen event channels, grant tables, balloon/page cache helpers, the `vscsiif` ring ABI, Linux SCSI and target core, configfs, and Xen backend registration. It bridges Xen frontends to target-core fabric sessions.

## Risks
Risk areas are guest-provided ring bounds, grant list validation, SG segment overflow, leaked grant mappings on early errors, races between LUN hotplug and in-flight commands, removing a nexus with active frontend references, ring halting on bogus producer indexes, and potential interrupt masking after ring errors. The code relies on request counters before disconnect and krefs on translation entries to prevent premature frees.

## Test Signals
Validate configfs creation of ports/TPGs/nexus/LUNs, Xenstore `vscsi-devs` hotplug state changes, guest SCSI inquiry/read/write, SG grant and direct SG paths, abort and LUN reset requests, frontend shutdown with zero unreplied requests, and grant page cache shrink behavior under load.

# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_port.c

## Purpose
`sas_port.c` manages libsas port formation, wide-port membership, port deformation, resume handling, port event workers, and per-HA port initialization. It is the topology bridge between per-phy link events and domain discovery.

## Important APIs, types, and functions
- `phy_is_wideport_member` checks whether a phy belongs in an existing port by matching attached SAS address and, when `strict_wide_ports` is set, the local SAS address.
- `sas_resume_port` notifies the LLDD that the port is formed, marks a suspended port active once, re-notifies all known devices as found, resets expander change counters to force full revalidation, and emits `DISCE_RESUME`.
- `sas_form_port_add_phy` links a phy to a port, updates target identity, `port->num_phys`, `phy_mask`, SAS addresses, protocols, OOB mode, and maximum link rate.
- `sas_form_port` either validates an existing port, resumes a suspended phy, attaches the phy to a matching wide port, or allocates a free port slot and creates the transport `sas_port`. It notifies the LLDD, starts domain discovery, and schedules expander revalidation when a port device already exists.
- `sas_deform_port` removes a phy from a port, unregisters/destructs devices if the last phy is gone, updates transport port membership, notifies LLDD deformation, clears port state when empty, and schedules expander revalidation for remaining wide ports.
- Event workers map port events to formation, revalidation, or deformation: `sas_porte_bytes_dmaed`, `sas_porte_broadcast_rcvd`, `sas_porte_link_reset_err`, `sas_porte_timer_event`, and `sas_porte_hard_reset`.
- `sas_register_ports` initializes all HA ports and discovery state; `sas_unregister_ports` deforms any still-attached phys.

## Control flow and state
On `PORTE_BYTES_DMAED`, libsas calls `sas_form_port`. Existing phy membership is checked first: nonmatching membership triggers deformation, suspended matching membership resumes the port and wakes the HA EH wait queue, and duplicate active membership is ignored. New membership is serialized by `sas_ha->phy_port_lock` plus each port's `phy_list_lock`. Wide-port lookup scans existing nonempty ports before claiming an empty port slot.

On deformation, device topology is torn down before removing the phy from port lists. If the port loses its last phy, all domain devices are unregistered/destructed and the transport port is deleted. If other phys remain, only the phy is removed and device-to-phy association is refreshed. Discovery queue flushes make event effects visible before returning.

## State and persistence behavior
Port state is held in `asd_sas_port`: `sas_addr`, `attached_sas_addr`, protocol fields, `oob_mode`, `linkrate`, `num_phys`, `phy_mask`, `phy_list`, `dev_list`, discovery lists, and transport `sas_port *`. Device `pathways` tracks wide-port path count. There is no persistence beyond in-memory kernel topology and SCSI transport objects.

## Dependencies and integration points
This file depends on SCSI SAS transport port APIs, LLDD callbacks `lldd_port_formed` and `lldd_port_deformed`, discovery helpers in libsas, device unregister/destruct helpers, expander revalidation state, and phy identity helpers from `sas_internal.h`.

## Risks and edge cases
- Port/phy locking order is critical: HA `phy_port_lock` wraps per-port `phy_list_lock` during formation and deformation.
- `sas_form_port` uses `BUG_ON(!port->port)` after `sas_port_alloc`, so allocation failure is fatal.
- Wide-port matching behavior changes when `strict_wide_ports` is enabled; mismatched local addresses prevent aggregation.
- `sas_porte_broadcast_rcvd` calls `sas_discover_event(phy->port, ...)` before checking `phy->port`; callers should ensure broadcast events have a live port.
- Deformation decrements `dev->pathways` when a port device exists; inconsistent wide-port accounting can affect path management.

## Test signals
- Single-phy link-up should allocate a transport port, add the phy, and emit domain discovery.
- Multiple phys with the same attached SAS address should form a wide port and update `pathways`/`phy_mask`.
- Loss of one wide-port phy should remove only that phy and schedule expander revalidation.
- Loss of the last phy should unregister/destruct devices and delete the transport port.
- Resume tests should re-notify LLDD devices and force expander change-count revalidation.

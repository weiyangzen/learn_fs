# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_attr.c

## Purpose
`bfad_attr.c` binds the BFAD initiator driver to the Linux FC transport and SCSI host sysfs attribute surfaces. It translates BFA/FCS adapter, port, target, statistics, vport, and firmware attributes into `fc_host_*`, `fc_starget_*`, FC vport operations, BSG hooks, and read-only host attributes.

## Important APIs, Types, and Functions
The file exports two `struct fc_function_template` instances: `bfad_im_fc_function_template` for the physical port and `bfad_im_vport_fc_function_template` for NPIV vports. Dynamic target callbacks (`bfad_im_get_starget_port_id`, `_node_name`, `_port_name`) locate `bfad_itnim_s` by SCSI target ID under `bfad_lock`. Host callbacks expose port ID, type, state, FC4s, speed, fabric WWN, and stats through BFA/FCS helpers. `bfad_im_get_stats` and `bfad_im_reset_stats` issue asynchronous BFA port-stat commands and wait on `bfad_hal_comp`. Vport callbacks create/delete/disable vports through `bfad_vport_create`, `bfa_fcs_vport_lookup`, `bfa_fcs_vport_stop/start`, and `bfa_fcs_vport_delete`. Sysfs show functions expose serial, model, model description, WWNs, symbolic name, hardware/firmware/option-ROM versions, port count, driver name/version, and discovered-port count.

## Control Flow
Transport callbacks enter from FC transport or sysfs, recover `bfad_im_port_s` from `shost->hostdata[0]`, and then call into BFA/FCS. Read-only lookups are mostly synchronous. Operations that touch firmware state lock `bfad->bfad_lock`, start BFA work, unlock, and wait for completion. Vport creation fills a `bfa_lport_cfg_s`, checks the preboot vport list for preserved preboot state, calls the BFAD vport constructor, looks up the resulting FCS vport, initializes the new vhost FC transport fields, and stores `fc_vport->dd_data`. Deletion marks `BFAD_PORT_DELETE`, starts FCS deletion, waits for callback completion, removes the SCSI host, unlinks the vport, and frees it.

## State and Persistence
The file mutates transport-visible host fields, `fc_vport` state, `fc_vport->dd_data`, `vport->drv_port.flags`, `vport->comp_del`, and per-port sysfs attribute values derived from live adapter state. Adapter names and firmware versions are read from BFA state; there is no direct on-disk persistence here. Vport preboot awareness is inherited from `bfad->pbc_vport_list`.

## Dependencies and Integration Points
It depends on `bfad_drv.h`, `bfad_im.h`, Linux FC transport, SCSI host sysfs, and many BFA/FCS APIs: `bfa_fcport_get_attr`, `bfa_port_get_stats`, `bfa_fcs_lport_get_attr`, `bfa_fcs_vport_*`, and adapter query helpers. It integrates BSG by wiring `bfad_im_bsg_request` and `bfad_im_bsg_timeout` into the physical-port FC template.

## Risks
Most callbacks assume `shost->hostdata[0]`, `rport->dd_data`, and FCS lookup results remain valid while locks are held. `strcpy` is used for vport symbolic names after checking only `strlen(vname) > 0`; safety depends on FC transport buffer sizing. Several operations can wait indefinitely if firmware callbacks do not complete. `bfad_im_num_of_discovered_ports_show` allocates a fixed 2048-entry qualifier buffer and reports BFA-filled counts, so behavior depends on BFA enforcing bounds.

## Test Signals
Useful signals are FC transport sysfs reads, `fc_vport_create/delete/disable` exercises, `issue_lip`, `get_fc_host_stats`/reset behavior, and BSG availability on physical hosts. Negative tests should cover invalid WWNs, max vport failures, firmware command failures, disabled vports, and missing `itnim` target mappings.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_attr.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_attr.c

Purpose: this file is the FC transport integration layer for the Chelsio FCoE driver. It registers/unregisters remote ports, populates FC host/rport sysfs attributes, exposes FC transport function templates, manages NPIV virtual port lifecycle, reads FC statistics, and translates dev-loss timeouts into serialized driver events.

Important APIs, types, and functions: exported driver-facing routines include `csio_reg_rnode()`, `csio_unreg_rnode()`, `csio_lnode_async_event()`, and `csio_fchost_attr_init()`. The public transport templates are `csio_fc_transport_funcs` for physical ports and `csio_fc_transport_vport_funcs` for vports. Key local helpers include `csio_get_host_port_id()`, `csio_get_host_port_type()`, `csio_get_host_port_state()`, `csio_get_host_speed()`, `csio_get_host_fabric_name()`, `csio_get_stats()`, `csio_set_rport_loss_tmo()`, `csio_vport_set_state()`, `csio_fcoe_alloc_vnp()`, `csio_fcoe_free_vnp()`, `csio_vport_create()`, `csio_vport_delete()`, `csio_vport_disable()`, and `csio_dev_loss_tmo_callbk()`.

Control flow: remote-port registration builds `fc_rport_identifiers`, creates an rport with `fc_remote_port_add()`, stores the driver rnode pointer in `rport->dd_data`, copies max frame size/classes, updates roles via `fc_remote_port_rolechg()`, and records `scsi_target_id`. Local-node async events refresh vport state or host attributes. Vport create allocates a new lnode/shost, validates requested WWNN/WWPN, ensures WWPN uniqueness, allocates a firmware VNP with mailbox retry on `-EBUSY`, initializes FC attributes, and stores the lnode in vport private data. Vport delete/disable block SCSI requests, clean I/O, stop or close lnode state, free firmware VNPs, and exit shosts. Dev-loss callback queues `CSIO_EVT_DEV_LOSS` and schedules the event worker unless removal or rnode recovery makes it unnecessary.

State and persistence behavior: the file updates in-memory `csio_lnode`, `csio_rnode`, `fc_rport`, and `fc_vport` state. Firmware VNP allocation persists in adapter firmware until explicitly freed. Host statistics accumulate in `ln->fch_stats` by adding hardware counters and lnode request counters; reset age is derived from `hw->stats.n_reset_start`.

Dependencies and integration points: it depends on FC transport class APIs, SCSI host request blocking, Chelsio mailbox helpers, lnode/rnode lookup/state helpers, FCoE firmware commands, and the hardware event queue in `csio_hw.c`.

Risks: mailbox commands run while holding `hw->lock` except for retry sleeps, so latency and lock ordering matter. Vport create error paths must unwind shost allocation and firmware VNP allocation correctly. Role updates assume existing `rn->rport` when roles are already set. Dev-loss enqueues a pointer payload, so rnode lifetime must outlive event processing.

Test signals: validate rport add/delete and role changes, sysfs FC attribute correctness, link speed mapping, fabric-name lookup, stats reads, NPIV create/delete/disable/enable including duplicate WWPN and invalid WWN failures, mailbox busy retry, dev-loss timeout event scheduling, and removal races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_attr.c -->

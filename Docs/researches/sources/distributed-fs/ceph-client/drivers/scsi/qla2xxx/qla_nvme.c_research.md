# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nvme.c

## Purpose
`qla_nvme.c` implements FC-NVMe initiator and unsolicited link-service support for the `qla2xxx` Fibre Channel driver. It registers qla2xxx HBAs and discovered FC ports with the Linux NVMe-FC transport, maps NVMe transport callbacks to qla2xxx SRBs and firmware IOCBs, builds `COMMAND_NVME` and LS4 pass-through IOCBs, handles command and link-service aborts, and routes unsolicited FC-NVMe LS requests into the NVMe-FC core.

The file is compiled around `CONFIG_NVME_FC` checks. When NVMe-FC is disabled, exported registration/delete functions return harmlessly or fail early without touching the transport.

## Important APIs, Types, And Functions
Transport registration uses `qla_nvme_register_hba()`, `qla_nvme_register_remote()`, `qla_nvme_unregister_remote_port()`, `qla_nvme_delete()`, `qla_nvme_localport_delete()`, and `qla_nvme_remoteport_delete()`. These functions create and destroy `nvme_fc_local_port` and `nvme_fc_remote_port` objects and link their `private` fields to `scsi_qla_host` and `qla_nvme_rport`.

The NVMe-FC port template is `qla_nvme_fc_transport`. It supplies callbacks for queue creation, LS request/abort, FCP I/O/abort, unsolicited LS response transmit, queue mapping, and local/remote delete notifications. It also advertises private-data sizes, queue/segment limits, DMA boundary, and default hardware queue count.

Per-request private state is `struct nvme_private`, defined in `qla_nvme.h`, and per-unsolicited-LS state is local `struct qla_nvme_unsol_ctx`. Both use `cmd_lock`, an SRB pointer, work items, and completion status fields to coordinate asynchronous completion and abort paths.

Command and LS completion functions include `qla_nvme_sp_done()`, `qla_nvme_sp_ls_done()`, `qla_nvme_sp_lsrsp_done()`, `qla_nvme_release_fcp_cmd_kref()`, `qla_nvme_release_ls_cmd_kref()`, `qla_nvme_release_lsrsp_cmd_kref()`, `qla_nvme_ls_complete()`, and `qla_nvme_lsrsp_complete()`.

Submission paths include `qla_nvme_alloc_queue()`, `qla_nvme_ls_req()`, `qla_nvme_xmt_ls_rsp()`, `qla_nvme_post_cmd()`, and `qla2x00_start_nvme_mq()`. Abort helpers are `qla_nvme_ls_abort()`, `qla_nvme_fcp_abort()`, `qla_nvme_abort_work()`, `qla_nvme_abort_set_option()`, `qla_nvme_abort_process_comp_status()`, and `qla_wait_nvme_release_cmd_kref()`.

Unsolicited LS handling is implemented by `qla2xxx_process_purls_iocb()`, `qla2xxx_process_purls_pkt()`, `qla2xxx_get_vha_from_vp_idx()`, `qla_nvme_fc_format_rjt()`, `qla_nvme_lsrjt_pt_iocb()`, and `qla_nvme_ls_reject_iocb()`.

## Control Flow
Remote registration starts when a discovered `fc_port` advertises NVMe PRLI target or discovery service parameters. `qla_nvme_register_remote()` verifies host NVMe enablement, ensures local-port registration, filters already registered or non-target/discovery ports, builds `nvme_fc_port_info` from WWNN/WWPN/PortID/dev-loss timeout, sets role bits from PRLI parameters, calls `nvme_fc_register_remoteport()`, updates devloss, stores the `fc_port` in `qla_nvme_rport`, and sets `NVME_FLAG_REGISTERED`.

Local HBA registration is serialized by `ha->vport_lock`. `qla_nvme_register_hba()` clamps module queue count `ql2xnvme_queues` to available qpairs, updates template `max_hw_queues`, fills local port name/node name/role/PortID, sets DMA boundary from the SCSI host, and calls `nvme_fc_register_localport()`. The returned local port stores `vha` in `private`.

Queue creation maps NVMe-FC queue indexes onto qla2xxx qpairs. `qla_nvme_alloc_queue()` maps admin queue and first I/O queue to index 0, returns `ha->base_qpair` when qpairs are not enabled, reuses an existing `queue_pair_map[qidx]`, or creates a new qpair with `qla2xxx_create_qpair()` and adjusts IOCB limits.

NVMe FCP I/O enters `qla_nvme_post_cmd()`. It validates the transport private pointer, qpair, `fcport`, registered state, abort-in-progress flag, and NVMe resetting flag. It maps the transport queue to a qpair, allocates a qpair SRB, initializes kref and locks, stores `nvme_private` in `sp->priv`, sets type/name/done/put callbacks, stores the transport descriptor, and calls `qla2x00_start_nvme_mq()`.

`qla2x00_start_nvme_mq()` holds the qpair lock, allocates a firmware handle and resources, checks request-ring space, detects admin async event commands, builds a `cmd_nvme` IOCB, sets direction/first-burst/EDIF/admin-async flags, fills NPORT handle, PortID, VP index, response and command IU DSDs, payload length, and data SG DSDs plus continuation entries, writes the ring doorbell, optionally processes pending responses, and returns busy on resource or ring exhaustion.

NVMe LS requests use `qla_nvme_ls_req()`, which allocates a normal SRB, stores the NVMe-FC LS request, DMA-syncs the request payload for device, and starts the SRB. Completion is deferred through work so `fd->done()` is not invoked directly from lower-level completion context.

Abort paths take `cmd_lock`, confirm the SRB still exists, acquire `cmd_kref` with `kref_get_unless_zero()`, then schedule `qla_nvme_abort_work()`. The work item skips aborts when firmware is stopped or the session is deleted, completes locally during host shutdown, otherwise calls `ha->isp_ops->abort_command(sp)`. If ABTS-wait mode is active and firmware will complete abort asynchronously, the kref is left for abort completion; otherwise the kref is dropped before leaving the work item.

Unsolicited PURLS/LS4 responses enter through `qla2xxx_process_purls_iocb()`. The code maps VP index to a VHA, extracts source/destination IDs and opcode, finds the `fc_port`, copies possibly multi-packet payload into a `purex_item`, allocates `qla_nvme_unsol_ctx`, links it to the FC port unsolicited context list, and queues processing. `qla2xxx_process_purls_pkt()` calls `nvme_fc_rcv_ls_req()`. If the NVMe-FC core rejects it or resources are missing, the driver emits either an LS reject or exchange terminate IOCB and frees the context.

## State And Persistence
There is no on-disk persistence. State lives in the NVMe-FC transport objects, qla2xxx host/port structures, SRBs, and per-request private data.

`vha->nvme_local_port` persists while the local NVMe-FC port is registered. Each `fc_port` may hold `nvme_remote_port`, NVMe PRLI service parameters, `nvme_flag` bits (`REGISTERED`, `RESETTING`, `DELETING`), `nvme_first_burst_size`, dev-loss timeout, and an unsolicited context list.

`struct nvme_private` is transport-allocated per LS or FCP request. It tracks the in-flight SRB, transport descriptor, scheduled LS/abort work, completion status, and a spinlock that serializes completion against abort.

`struct qla_nvme_unsol_ctx` persists from unsolicited LS receipt until the response is completed or the exchange is rejected/terminated. It stores VHA, FC port, SRB, response descriptor, exchange address, NPORT handle, OX_ID, completion status, work items, and list linkage.

Active admin async-event commands increment `ha->nvme_active_aen_cnt` and avoid normal command-count accounting because they can have long timeouts.

## Dependencies And Integration Points
The file depends on Linux NVMe-FC transport APIs (`nvme_fc_register_localport()`, `nvme_fc_register_remoteport()`, `nvme_fc_unregister_*()`, `nvme_fc_rcv_ls_req()`, `nvme_fc_set_remoteport_devloss()`), block multiqueue mapping (`blk_mq_map_hw_queues()`), scatterlists, DMA sync helpers, workqueues, krefs, and NVMe command opcodes/status constants.

It integrates with qla2xxx SRB allocation and submission helpers (`qla2x00_get_sp()`, `qla2xxx_get_qpair_sp()`, `qla2x00_start_sp()`, `qla2xxx_rel_qpair_sp()`, `qla24xx_calc_iocbs()`, `qla_get_fw_resources()`, `qla_put_fw_resources()`, qpair maps, response processing, purex copy/queue helpers, and firmware abort ops).

It shares FC session state through `fc_port_t`, VP lookup via `ha->vp_list`, PortID lookup via `qla2x00_find_fcport_by_nportid()`, EDIF flags, PRLI service parameter bits, and DPC/PCI flags.

## Risks And Edge Cases
Completion and abort race handling depends on `cmd_lock`, `priv->sp`/`uctx->sp`, and `cmd_kref`. Any path that drops the last kref before clearing private pointers can use-after-free the SRB; any path that forgets the abort-acquired kref can leak SRBs.

`qla2x00_start_nvme_mq()` reserves firmware IOCB and exchange resources after acquiring a handle. On all queueing errors it must release firmware resources and avoid leaving `outstanding_cmds[handle]` visible incorrectly.

Queue index handling decrements nonzero NVMe queue indexes before lookup. Boundary checks against `max_hw_queues` and `queue_pair_map` must stay aligned with how the NVMe-FC core numbers queues.

Unsolicited LS handling assumes a registered remote NVMe port exists for the source FC port. If `fcport->nvme_remote_port` is NULL or races with delete, dereferencing `rport->private` is risky unless higher-level session teardown prevents delivery.

LS reject/terminate fallback allocates IOCBs directly from a qpair. If allocation fails, the original exchange may remain pending in firmware. Error paths free `uctx` and purex items differently depending on where failure occurred, so memory ownership must remain explicit.

First-burst, EDIF, admin async-event, and ABTS-wait options are conditional on flags and PRLI bits. These paths need focused tests because they change firmware control flags and completion accounting.

## Test Signals
Build tests should cover both `CONFIG_NVME_FC=y` and disabled configurations. Disabled builds should confirm registration/delete functions return without dereferencing NVMe transport objects.

Registration tests should cover queue-count clamping, local-port race under `vport_lock`, remote-port role bit construction, discovery-only and target roles, duplicate remote registration, devloss update, and unregister completions.

I/O tests should cover read, write, no-data/admin, admin async event, large SG lists requiring continuation IOCBs, ring full, firmware resource exhaustion, qpair mapping, first-burst enabled/disabled, EDIF-enabled transfers, and response queue opportunistic processing.

Abort tests should cover LS abort, FCP abort, host shutdown, stopped firmware, deleted sessions, async TMF enabled, ABTS wait enabled, and abort completion statuses handled by `qla_nvme_abort_process_comp_status()`.

Unsolicited LS tests should cover valid PURLS, invalid VP index, missing FC port, multi-packet copy failure, allocation failure, NVMe-FC core rejection, LS reject formatting, exchange terminate, context list add/delete, and completion of `xmt_ls_rsp()`.

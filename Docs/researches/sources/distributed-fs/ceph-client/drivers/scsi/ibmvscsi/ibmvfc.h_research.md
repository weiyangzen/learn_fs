# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvfc.h

## Purpose
`ibmvfc.h` defines the protocol constants, packed wire-format structures, state enums, and in-memory driver objects used by the IBM Power Virtual Fibre Channel client driver. It is the contract between `ibmvfc.c`, the Linux SCSI/FC subsystems, and the VIOS/hypervisor-facing message protocol.

The header covers driver defaults, module-parameter defaults, MAD opcodes/status values, NPIV login data, target discovery, PLOGI/PRLI/query/move-login/logout commands, task management, FCP command/response layouts, FC passthrough, channel enquiry/setup, CRQ/SCRQ formats, async events, event pools, queues, channel collections, host/target state machines, trace records, and logging/sysfs trace helper macros.

## Important APIs, Types, and Constants
Driver identity and defaults include `IBMVFC_NAME`, `IBMVFC_DRIVER_VERSION`, timeout constants, queue depth defaults, maximum targets/LUN/sectors, discovery thread limits, target mempool size, max commands per LUN, init retry limits, dev-loss timeout, class-3 retry default, and multiqueue defaults.

`IBMVFC_NUM_INTERNAL_REQ` reserves base-queue events for ERP, initialization, NPIV logout, BSG passthrough, and discovery; `IBMVFC_NUM_INTERNAL_SUBQ_REQ` reserves subqueue events for channelized cancel commands. These macros depend on the C file's `disc_threads` module variable, so queue sizing is a header/C coupling point.

Protocol status and opcode enums include CRQ valid/init/transport event values, command status flags, fabric-mapped errors, VIOS errors, MAD opcodes, FC reason/type/explain values, FCP response info/flags, command flags, task attributes, TMF flags, CRQ formats, async events, link/FPIN states, target actions, protocols, host actions, and host states.

Important wire structs are `ibmvfc_mad_common`, `ibmvfc_npiv_login_mad`, `ibmvfc_npiv_logout_mad`, `ibmvfc_npiv_login`, `ibmvfc_npiv_login_resp`, `ibmvfc_discover_targets`, `ibmvfc_port_login`, `ibmvfc_move_login`, `ibmvfc_process_login`, `ibmvfc_query_tgt`, `ibmvfc_implicit_logout`, `ibmvfc_tmf`, `ibmvfc_fcp_cmd_iu`, `ibmvfc_fcp_rsp`, `ibmvfc_cmd`, `ibmvfc_passthru_mad`, `ibmvfc_channel_enquiry`, `ibmvfc_channel_setup`, `ibmvfc_connection_info`, `ibmvfc_crq`, `ibmvfc_sub_crq`, and `ibmvfc_async_crq`. Most are packed and explicitly aligned for hypervisor/VIOS DMA layout.

Important in-memory structs are `ibmvfc_target`, `ibmvfc_event`, `ibmvfc_event_pool`, `ibmvfc_queue`, `ibmvfc_channels`, and `ibmvfc_host`. They are not just declarations; their field layout expresses the driver's ownership model, queue model, target/rport lifecycle, and host state machine.

## Control Flow Expressed by the Header
The header encodes the CRQ transport framing: messages are either command responses, async events, or MAD/FCP payload descriptors. `union ibmvfc_iu` lets a single DMA-backed event storage slot carry any supported management command or FCP command, while `ibmvfc_crq.ioba` returns the event correlation token.

NPIV login flow is represented by `ibmvfc_npiv_login`, `ibmvfc_npiv_login_resp`, and capability flags. The client advertises migration, channel, FPIN, MAD-version, and VF-WWPN abilities; VIOS responds with native-FC support, flush/suppress-ABTS/MAD/channel/VF-WWPN capabilities, max commands, scsi ID, WWPNs, link speed, names, and service parameters. `ibmvfc.c` uses these fields to decide command IU version, multiqueue setup, host FC identity, and max queue depth.

Target discovery and login flow is encoded by `ibmvfc_discover_targets_entry`, `ibmvfc_discover_targets`, `ibmvfc_port_login`, `ibmvfc_process_login`, `ibmvfc_query_tgt`, `ibmvfc_implicit_logout`, and `ibmvfc_move_login`. The driver discovers SCSI port IDs and WWPNs, logs into ports, runs PRLI with SCSI-FCP service parameters, validates or updates existing targets, logs out old IDs, and optionally moves login state for NPIV failover cases.

I/O flow is represented by `ibmvfc_cmd`, `ibmvfc_fcp_cmd_iu`, `ibmvfc_fcp_rsp`, and scatterlist-related `srp_direct_buf` fields. The command struct includes status/error, adapter residual, flags, cancel key, exchange ID, external function descriptor, data descriptor, response descriptor, correlation, target identity, and both v1 and v2 IU layouts. The v2 layout inserts an extra reserved word and target WWPN support when `IBMVFC_HANDLE_VF_WWPN` is negotiated.

Recovery flow is represented by `ibmvfc_tmf`, cancel keys, TMF flags, event completions, host/target actions, and async event enums. These definitions let `ibmvfc.c` issue cancels, abort task sets, LUN/target resets, passthrough cancels, and host reset/relogin sequences in response to SCSI EH, timeouts, CRQ transport events, and async FC events.

## State and Persistence Behavior
`struct ibmvfc_host` is the root runtime object stored as SCSI host private data. It persists while the VIO device is bound and contains host state/action, target list, purge list, device pointers, DMA pools and buffers, CRQ/async/sub-CRQ queues, login buffers, channel setup buffer, log level, passthrough mutex, channel limits, task-set counter, state flags, scan status, pending async event flags, partition identity, worker callback, worker thread, tasklet, rport-add work, and wait queues.

`struct ibmvfc_target` persists per discovered FC target and contains list linkage, owning host, protocol, SCSI ID/WWPN/new SCSI ID, FC rport pointer, target ID, action, login/add flags, retry and move-login state, cancel key, service parameters, FC rport identifiers, job callback, ADISC timer, and kref.

`struct ibmvfc_event` is the unit of queued work. It holds list nodes, host/queue/target/SCSI command pointers, `free` and `active` atomics, DMA transfer IU pointer, callbacks, CRQ descriptor, local IU staging storage, optional synchronous response pointer, external scatterlist DMA buffer/token, completion objects, timer, hardware queue index, and reserved-event flag.

`struct ibmvfc_queue` tracks one CRQ-like queue page plus its event pool and sub-CRQ metadata. It stores the DMA-mapped message page, current ring index, lock pointers, sent/free event lists, depth accounting, cancel response IU, hypervisor cookies, IRQs, hardware queue ID, name, and IRQ handler. `struct ibmvfc_channels` groups SCRQs by protocol and tracks active/desired/max queue counts plus a DMA discovery buffer.

All protocol fields use big-endian integer types where VIOS expects big-endian wire data. There is no disk persistence; the header's state structs describe volatile kernel state rebuilt on probe and destroyed on remove.

## Dependencies and Integration Points
The header includes `linux/list.h`, `linux/types.h`, and `scsi/viosrp.h`; additional types are supplied by the C file's broader includes. `srp_direct_buf`, `struct scsi_lun`, `SCSI_SENSE_BUFFERSIZE`, `struct fc_rport`, `struct fc_rport_identifiers`, `struct Scsi_Host`, `struct scsi_cmnd`, DMA address types, timers, completions, mempools, work structs, tasklets, and wait queues are all part of the integration surface.

Packed/aligned protocol definitions integrate with VIOS DMA and pseries CRQ/SCRQ hypervisor calls. The CRQ, sub-CRQ, async CRQ, MAD common header, and all MAD payload structs must remain ABI-compatible with the firmware/VIOS contract.

The logging macros integrate with kernel device logging and the C file's `ibmvfc_debug`/`log_level` globals. Trace helper macros integrate with sysfs only when `CONFIG_SCSI_IBMVFC_TRACE` is enabled.

## Risks and Edge Cases
The protocol structs are ABI-sensitive. Changing packing, alignment, field order, endian annotations, or union layout can break VIOS communication. `ibmvfc_cmd` is especially sensitive because v1/v2 IU offsets are used to compute response DMA addresses.

Queue sizing depends on defaults and a macro that references `disc_threads` from the implementation file. This is convenient but creates non-obvious coupling: changes to discovery-thread behavior affect reserved event counts and can starve recovery if not considered.

Host and target action enums define allowed transitions in `ibmvfc.c`; adding states without updating `ibmvfc_set_host_action`, `ibmvfc_set_tgt_action`, `ibmvfc_work_to_do`, and `ibmvfc_do_work` can strand work or unblock I/O too early.

Capability flags select behavior at runtime. If the header and implementation disagree about `IBMVFC_HANDLE_VF_WWPN`, `IBMVFC_CAN_SUPPORT_CHANNELS`, suppress-ABTS, migration, or channel flags, the driver can send an IU version or channel request the partner does not understand.

The async event set includes FPIN constants, but the implementation's logged descriptor table does not include `IBMVFC_AE_FPIN` in the viewed source. Any functional FPIN handling would need explicit implementation support rather than only header constants.

## Test Signals
Header-focused validation should include compile coverage for big-endian conversions, struct size/offset assumptions around `ibmvfc_cmd.v1.rsp` and `v2.rsp`, and builds with trace enabled/disabled.

Protocol tests should validate NPIV login capability negotiation, channel enquiry/setup flags, discovery buffer entry parsing, target login MAD fields, TMF flags/cancel keys, passthrough payload descriptors, and CRQ/SCRQ message sizes.

State-machine tests should cover every `ibmvfc_host_action`, `ibmvfc_host_state`, and `ibmvfc_target_action` value through the implementation transitions, including reset, reenable, target delete, move login, and host offline removal.

Resource tests should validate event-pool depth math for base CRQ and sub-CRQ queues across different `disc_threads`, `scsi_qdepth`, hardware queue counts, and channel counts, ensuring reserved events remain available for initialization and recovery.

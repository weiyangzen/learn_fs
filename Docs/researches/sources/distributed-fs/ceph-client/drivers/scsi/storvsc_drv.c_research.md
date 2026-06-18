<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/storvsc_drv.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/storvsc_drv.c

## Purpose
`storvsc_drv.c` implements the Microsoft Hyper-V virtual storage SCSI driver. It negotiates the VM storage protocol over VMBus, exposes synthetic SCSI, IDE, and Fibre Channel devices to the Linux SCSI mid-layer, maps SCSI SG lists into Hyper-V multipage buffers, handles completions and unsolicited LUN-change notifications, and manages multichannel I/O distribution.

## Important APIs, Types, And Functions
Protocol structures include `struct vstor_packet`, `struct vmscsi_request`, `struct vmstorage_protocol_version`, `struct vmstorage_channel_properties`, and `struct hv_fc_wwn_packet`. Driver state is held in `struct storvsc_device` for per-VMBus-channel storage state and `struct hv_host_device` for SCSI host-private state. Each SCSI command uses `struct storvsc_cmd_request` as `cmd_size` private storage.

Key functions are `storvsc_probe()`, `storvsc_remove()`, `storvsc_suspend()`, `storvsc_resume()`, `storvsc_connect_to_vsp()`, `storvsc_channel_init()`, `storvsc_execute_vstor_op()`, `handle_multichannel_storage()`, `handle_sc_creation()`, `storvsc_queuecommand()`, `storvsc_do_io()`, `storvsc_on_channel_callback()`, `storvsc_on_receive()`, `storvsc_on_io_completion()`, `storvsc_command_completion()`, `storvsc_handle_error()`, and `storvsc_host_reset_handler()`.

## Control Flow
Module init computes the aligned VMBus ring size and maximum outstanding requests per channel, optionally attaches the FC transport, and registers `storvsc_drv`. Probe sizes `scsi_driver.can_queue` from ring capacity and subchannel count, allocates a SCSI host and `storvsc_device`, opens the primary VMBus channel, negotiates protocol versions from newest supported downward, queries channel properties, optionally fetches FC WWNs, ends initialization, creates subchannels when supported, sets SCSI host limits by device class, creates the ordered error workqueue, registers the host, and scans or adds the IDE boot device.

`storvsc_queuecommand()` filters known-bad legacy commands on older hosts, fills the VMSC SCSI request, maps the SCSI SG list, builds an inline or heap multipage-buffer payload, and calls `storvsc_do_io()` with the current CPU. `storvsc_do_io()` picks a VMBus channel by CPU affinity, NUMA locality, and ring free-space percentage, sends an in-band or MPB descriptor packet, and increments `num_outstanding_req`. The callback drains packets with a small time budget, validates packet length and transaction IDs, maps nonzero transaction IDs back to SCSI tags, unmaps DMA, copies status/sense/transfer length, runs error-specific work scheduling, completes the SCSI command, frees heap payloads, and wakes drain waiters when outstanding I/O reaches zero.

## State And Persistence Behavior
State is volatile guest-driver state: negotiated `vmstor_proto_version`, ring-buffer sizing module parameters, `stor_chns` CPU-to-channel cache, `alloced_cpus`, FC `node_name`/`port_name`, `destroy` and drain flags, and outstanding request count. No persistent storage metadata is written by this driver. Suspend drains requests, drains the error workqueue, closes the channel, frees channel mappings, and clears CPU masks; resume reconnects and renegotiates.

## Dependencies And Integration Points
The file integrates the Hyper-V VMBus API, Linux SCSI host/device/EH APIs, blk-mq tags, DMA mapping, CPU masks and NUMA topology, FC transport attributes when configured, and SCSI device scanning/removal workqueues. It depends on Hyper-V packet IDs: `VMBUS_RQST_INIT`, `VMBUS_RQST_RESET`, and command transaction IDs derived from SCSI tags plus one.

## Risks
High-risk areas are transaction-ID validation, unsolicited packet rejection, heap payload lifetime for large SG lists, races between removal and inbound completions, channel selection while target CPUs move, global `vmstor_proto_version` across devices, and trusting host-reported transfer lengths. The code clamps transfer length to the payload length and rejects bogus ID-zero completion/FC data packets, but correctness still depends on strict VMBus/SCSI tag pairing. Reset handling waits for all in-flight packets after bus reset because host responses may still be arriving.

## Test Signals
Test probe against SCSI, IDE, and synthetic FC GUIDs; protocol negotiation fallback; obsolete host rejection; multichannel creation and CPU retargeting; ring low-water channel fallback; large SG lists requiring heap MPB payloads; `PAGE_SIZE != HV_HYP_PAGE_SIZE` PFN construction; invalid transaction IDs and short packets; LUN add/remove notifications; capacity/granularity sense-triggered rescan; invalid-LUN removal; host reset drain; suspend/resume reconnect; FC WWN updates; queue-depth clamping; and legacy command filtering for `WRITE_SAME`/`SET_WINDOW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/storvsc_drv.c -->

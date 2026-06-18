<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scsi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scsi.h

Purpose: defines virtio SCSI configuration, control events, command request/response formats, task management, and sense data sizing.

Important APIs and types: feature bits cover hotplug, change events, target reset, request priority, and IO alignment. `struct virtio_scsi_config` exposes queues, segment limits, target/channel/lun limits, CDB and sense sizes, and alignment. Control types include TMF, asynchronous notification, and event acknowledgments. Request structures include `virtio_scsi_cmd_req`, `virtio_scsi_cmd_req_pi`, `virtio_scsi_cmd_resp`, and task management request/response formats with status and response codes.

Control flow, state, and persistence: the guest submits SCSI CDBs and optional protection information through request queues; control queue handles TMFs and events. Device state is SCSI target/lun state and pending commands outside this header.

Dependencies and integration points: integrates virtio with the Linux SCSI midlayer, block layer, hotplug, sense handling, and hypervisor storage backends.

Risks and test signals: risks include CDB/sense length mismatch, LUN encoding, TMF response handling, PI fields, queue count limits, and event ack ordering. Test inquiry/read/write, hotplug, abort/reset TMFs, sense data truncation, multi-queue I/O, and protection information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scsi.h -->

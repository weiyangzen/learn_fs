<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/hd.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/hd.h

Purpose: This header defines Greybus host devices and the host-controller driver operations needed to allocate CPorts, send messages, and control transport state.

Important APIs/types/functions: `struct gb_hd_driver` supplies host private size and callbacks for CPort allocate/release/enable/disable/connected/flush/shutdown/quiesce/clear, message send/cancel, latency tag enable/disable, and low-level output. `struct gb_host_device` embeds a device, bus id, driver pointer, module and connection lists, CPort IDA, CPort count, max buffer size, SVC pointer, and aligned private data. APIs reserve, allocate, release CPorts; create/add/delete/shutdown/put host devices; output messages; and init/exit host support.

Control flow, state, and persistence: Host controller drivers create a `gb_host_device`, add it to the Greybus core, and service message send/cancel callbacks from connections/operations. The host keeps persistent module/connection lists and CPort allocation state.

Dependencies/integration: It integrates Greybus core, Linux device model, IDA allocation, host-controller hardware drivers, SVC, and operation/message transport.

Risks and test signals: Buffer size, CPort count, and CPort allocation must match hardware. Send completion/cancel races affect operation lifetime. Tests should cover host add/delete, CPort reserve/allocate/release conflicts, message send errors, shutdown/quiesce phases, output from IRQ context, and host private data alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/hd.h -->

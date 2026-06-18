# sources/distributed-fs/ceph-client/arch/um/drivers/virtio_uml.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virtio_uml.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/virtio_uml.c

### Purpose
This is the UML virtio transport for vhost-user sockets. It negotiates vhost-user features, passes memory-table fds, configures vrings, handles kicks/calls, supports config access and slave requests, and creates devices from devicetree, command line, or mconsole.

### Important APIs, Types, And Functions
Key types are `virtio_uml_device`, `virtio_uml_platform_data`, and `virtio_uml_vq_info`. Important APIs include vhost-user send/receive helpers, feature/protocol negotiation, slave-request IRQ setup, config get/set, memory/vring programming, `vu_notify()`, `vu_interrupt()`, virtio config ops, command-line parsing, and suspend/resume.

### Control Flow
Probe connects to the backend socket, negotiates owner/features/protocol features, optionally registers a slave-request pipe IRQ, registers a virtio device, and later `find_vqs()` sends the memory table, creates vrings, sets call/kick fds or in-band notifications, sends vring layout, and enables rings. Slave requests record config changes or queue-call bits and are dispatched through the UML IRQ handler.

### State, Persistence, And Dependencies
Persistent state includes socket/request fds, UML IRQ number, negotiated features, max queue count, status byte, suspend flags, vq IRQ bitmap, and platform-device ownership. Dependencies include vhost-user ABI, UML `os_*` fd/socket helpers, time-travel support, `phys_mapping()`, virtio/vring core, platform/OF, and mconsole.

### Integration Points And Risks
Risks include protocol drift, the 64-vq bitmap limit, shared-memory visibility excluding the UML image/reserved range, stack/global DMA hazards, blocking waits during socket failure, ACK ordering under `sock_lock`, and wake behavior in time-travel/suspend modes.

### Test Signals
Test feature negotiation, queue limits, memory-table fd passing, eventfd versus in-band notifications, config get/set, slave config-change and queue-call messages, connection reset, command-line/mconsole creation, and suspend/resume wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virtio_uml.c -->

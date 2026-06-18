# sources/distributed-fs/ceph-client/arch/um/drivers/vhost_user.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vhost_user.h -->
## sources/distributed-fs/ceph-client/arch/um/drivers/vhost_user.h

### Purpose
This header defines the vhost-user protocol ABI consumed by `virtio_uml.c`.

### Important APIs, Types, And Functions
It provides message flags, feature/protocol bits, supported masks, master/slave request enums, packed header/config/vring/memory structures, a payload union, and `struct vhost_user_msg`.

### Control Flow
There is no executable flow. The exact packed layouts control how requests, replies, fd-passing memory tables, vring state, and slave notifications are serialized.

### State, Persistence, And Dependencies
State is per-message and backend-owned protocol state. Dependencies are Linux integer and bit macros plus vhost-user peer ABI compatibility.

### Integration Points And Risks
Risks include protocol extension drift, strict size/layout assumptions, and the hard-coded two memory-region array. Integration is with Unix socket control channels in the virtio-UML transport.

### Test Signals
Validate layout sizes, feature masks, malformed message-size handling, fd-passing memory-table exchange, and interoperability with vhost-user backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vhost_user.h -->

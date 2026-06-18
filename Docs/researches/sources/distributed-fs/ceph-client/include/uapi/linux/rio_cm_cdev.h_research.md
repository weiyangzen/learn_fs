<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rio_cm_cdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rio_cm_cdev.h

Purpose: defines the RapidIO channelized messaging character-device ABI for endpoint discovery, channel lifecycle, connection management, and message send/receive.

Important APIs and types: `struct rio_cm_channel` carries local/remote channel IDs, remote destination ID, and mport ID. `struct rio_cm_msg` carries channel number, message size, receive timeout, and userspace message pointer. `struct rio_cm_accept` carries channel number and accept timeout. Ioctls include endpoint list size/list, channel create/close/bind/listen/accept/connect, send/receive, and mport list.

Control flow: userspace discovers endpoints/mports, creates and binds a channel, listens/accepts or connects to a remote channel, then sends/receives messages with optional blocking timeouts. The kernel RapidIO CM driver manages channel state and routes messages over RapidIO.

State and persistence: state is runtime per channel and endpoint: bindings, listen/connect state, remote IDs, queues, and timeouts. No durable state is defined.

Dependencies and integration points: depends on Linux types/ioctl and integrates with RapidIO subsystem, mport devices, endpoint discovery, and user messaging applications.

Risks and test signals: risks include user pointer validation for message buffers, timeout semantics, channel ID reuse, remote disconnect handling, and endpoint list races. Test create/bind/listen/connect/accept, send/receive with blocking and timeout, endpoint hotplug, invalid sizes, and close during pending receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rio_cm_cdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg.h

Purpose: defines the rpmsg character-device ioctl ABI for creating, destroying, and flow-controlling remote-processor messaging endpoints and local service devices.

Important APIs, types, and functions: `RPMSG_ADDR_ANY` marks wildcard addresses. `struct rpmsg_endpoint_info` carries a 32-byte service name plus source and destination addresses. Ioctls include `RPMSG_CREATE_EPT_IOCTL`, `RPMSG_DESTROY_EPT_IOCTL`, `RPMSG_CREATE_DEV_IOCTL`, `RPMSG_RELEASE_DEV_IOCTL`, `RPMSG_GET_OUTGOING_FLOWCONTROL`, and `RPMSG_SET_INCOMING_FLOWCONTROL`.

Control flow: userspace opens an rpmsg control or endpoint character device, issues create ioctls with endpoint info, exchanges data through the resulting device, optionally queries or sets flow-control state, and destroys/releases endpoints when done.

State and persistence behavior: the header is declarative. Runtime endpoint state lives in rpmsg core, virtio/remoteproc transport state, and character-device instances. Created endpoints persist until destroyed, released, or the remote processor/device goes away.

Dependencies and integration points: depends on Linux ioctl and fixed-width type headers. It integrates with rpmsg char drivers, remoteproc, virtio rpmsg, and userspace services communicating with remote firmware.

Risks and edge cases: service names are fixed-size and may not be NUL-terminated if userspace fills all bytes. Address wildcarding, endpoint lifetime after remoteproc reset, and ioctl direction correctness for flow-control integers require care.

Test signals: create/destroy endpoints with wildcard and fixed addresses, test overlong/non-terminated names, reset the remote processor while endpoints are open, exercise flow-control ioctls, and verify data path error returns after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg.h -->

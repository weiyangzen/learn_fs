<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets.h

Purpose: defines the public AF_VSOCK socket address, socket options, well-known CIDs, flags, ioctls, and zerocopy notification constants.

Important APIs and types: socket options configure stream buffer size/min/max, peer VM ID, trust, connect timeout, and kernel-endpoint nonblocking TX/RX. `VMADDR_CID_*`, `VMADDR_PORT_ANY`, and `VMADDR_FLAG_TO_HOST` define addressing. `struct sockaddr_vm` is the AF_VSOCK address layout. `IOCTL_VM_SOCKETS_GET_LOCAL_CID` reports the local CID. `SOL_VSOCK` and `VSOCK_RECVERR` identify zerocopy error-queue notifications.

Control flow, state, and persistence: userspace binds/connects AF_VSOCK sockets using `sockaddr_vm`, queries or sets socket options, and may receive zerocopy completions. Per-socket state is in the networking stack.

Dependencies and integration points: integrates with Linux sockets, virtio/vmci/hyperv vsock transports, error queues, and libc time-size compatibility.

Risks and test signals: risks include 32/64-bit timeout compatibility, address structure size, CID routing flags, and option clamping. Test bind/connect/listen, local/host/hypervisor CIDs, zerocopy completion, old/new timeout constants, and mixed arch userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets.h -->

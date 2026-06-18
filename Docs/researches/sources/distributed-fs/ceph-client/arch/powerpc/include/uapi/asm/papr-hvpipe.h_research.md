<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-hvpipe.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-hvpipe.h

Purpose: Defines `/dev/papr-hvpipe` header format and handle-creation ioctl for PAPR hypervisor pipe payload exchange.

Important APIs/types/functions: `struct papr_hvpipe_hdr`, `PAPR_HVPIPE_IOC_CREATE_HANDLE`, `HVPIPE_MSG_AVAILABLE`, and `HVPIPE_LOST_CONNECTION`.

Control flow: Userspace creates a handle, reads messages prefixed by the header, and checks flags for payload availability or closed/unavailable pipe state.

State and persistence: Per-handle pipe connection state lives in the driver/hypervisor; the header serializes message status.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID, PowerPC ioctl encoding, and Linux types.

Risks: Header reserved bytes and version must remain compatible. Lost-connection handling must not be confused with empty payload.

Test signals: PAPR hvpipe userspace read/ioctl tests, connection loss simulations, and structure size checks.

Source read size: 33 lines, 816 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-hvpipe.h -->

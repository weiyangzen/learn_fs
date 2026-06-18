<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vtpm_proxy.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vtpm_proxy.h

Purpose: defines the userspace ABI for creating virtual TPM proxy devices and selecting TPM protocol/locality behavior.

Important APIs and types: `enum vtpm_proxy_flags` currently defines `VTPM_PROXY_FLAG_TPM2`. `struct vtpm_proxy_new_dev` carries input flags and output TPM number, file descriptor, major, and minor. `VTPM_PROXY_IOC_NEW_DEV` creates a proxy device. `TPM2_CC_SET_LOCALITY` and `TPM_ORD_SET_LOCALITY` define vendor-specific locality commands.

Control flow, state, and persistence: userspace issues the new-device ioctl, receives a proxy fd and device identifiers, then handles TPM command traffic through the proxy. Device state persists until fd/device teardown.

Dependencies and integration points: integrates with the TPM subsystem, container/VM TPM emulation, character devices, and ioctl userspace managers.

Risks and test signals: risks include fd lifetime leaks, TPM 1.2/2.0 flag mismatch, locality command handling, and device-number races. Test new device creation, fd closure cleanup, TPM2 flag behavior, command forwarding, and multi-device allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vtpm_proxy.h -->

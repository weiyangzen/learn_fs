<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/socket.h

Purpose: SPARC socket option and control-message ABI constants.

Important APIs and control flow: defines `SOL_SOCKET`, core `SO_*` values, Linux-specific options, timestamp/timeval old/new variants, security placeholders, zero-copy, BPF, busy-poll, device-memory, and newer ancillary aliases. Outside the kernel, `SO_TIMESTAMP`, `SO_RCVTIMEO`, and related names resolve to old or new values based on long/time_t width.

State, dependencies, and risks: state is socket options, ancillary message types, timeout/timestamp ABI selection, and filter attachment state. Dependencies include `linux/posix_types.h`, `asm/sockios.h`, `__BITS_PER_LONG`, and libc time_t width. Risks are value differences from other architectures, time64 selection mistakes, and new option collisions. Test signals are getsockopt/setsockopt ABI tests, timestamping in 32-bit and 64-bit userspace, BPF filter attach/detach, and SCM control-message decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/socket.h -->

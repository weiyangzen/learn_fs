<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/socket.h

Source read size: 173 lines, 4314 bytes.

Purpose: defines PA-RISC socket option numbers and timestamp/timeval compatibility selection. Important APIs: `SOL_SOCKET`, `SO_*` and `SCM_*` constants through modern options such as BPF, zerocopy, txtime, busy-poll, pidfd, devmem, passrights, and inq; old/new timestamp and timeout aliases selected by word/time size. Control flow: userspace passes constants to getsockopt/setsockopt and receives SCM control messages; preprocessor aliases select old or new time ABI outside the kernel. State and persistence: socket options persist in socket state; timestamp control messages are per packet. Dependencies and integration points: networking core, libc, `sockios.h`, time64 transition code, and compat syscalls. Risks: PA-RISC option values are architecture-specific and time-size aliases are subtle for 32-bit userspace. Test signals: socket option selftests, timestamping tests, BPF attach/detach, zerocopy, pidfd socket options, and 32-bit time64 ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/socket.h -->

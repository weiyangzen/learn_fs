<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/socket.h -->
# sources/distributed-fs/ceph-client/include/linux/socket.h

Purpose: This header is the kernel-side socket ABI and syscall helper declaration layer. It defines socket address/message structures, ancillary-data macros, address/protocol family numbers, send/receive flags, socket option levels, and internal syscall entry helpers.

Important APIs/types/functions: Key types are `struct sockaddr`, `sockaddr_unsized`, `linger`, `msghdr`, `user_msghdr`, `mmsghdr`, `cmsghdr`, `ucred`, and `scm_timestamping_internal`. Helper macros include `CMSG_ALIGN`, `CMSG_DATA`, `CMSG_SPACE`, `CMSG_LEN`, `CMSG_FIRSTHDR`, `CMSG_OK`, and `for_each_cmsghdr`. Internal APIs include `move_addr_to_kernel()`, `put_cmsg*()`, timestamping helpers, `__sys_*msg`, `__sys_socket*`, bind/connect/listen/accept/shutdown helpers, and `do_getsockname()`.

Control flow: The header documents how syscalls copy user message headers into kernel `msghdr`, iterate control messages with strict bounds, execute protocol operations through socket objects, and copy addresses/control messages back to user space. `__cmsg_nxthdr()` advances by aligned control-message length and returns NULL if the next header would exceed the supplied buffer.

State and persistence: No standalone state is stored here; it defines per-call message state and constants that must remain ABI stable. `msg_control_is_user`, `msg_get_inq`, zerocopy state, and iterator state are transient syscall/message fields.

Dependencies/integration: Pulls in architecture socket constants, sockios, UIO iterators, kernel types, compiler user-pointer annotations, and UAPI socket definitions. The declared helpers integrate with `net/socket.c`, protocol families, procfs socket display, timestamping, io_uring/kiocb paths, and compat handling via `MSG_CMSG_COMPAT`.

Risks and test signals: Risks cluster around ancillary-data length checks, user pointer copying, compat flag filtering, ABI number stability, and internal flags leaking into user-visible paths. Test signals include socket syscall tests, control-message fuzzing, compat 32-bit tests, timestamp SCM tests, address-length boundary tests, and build assertions such as `__sockaddr_check_size()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/socket.h -->

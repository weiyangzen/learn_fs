# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/linux/socket.h

## Purpose
This vendored Linux socket header supplies socket ABI types, constants, helper macros, and kernel syscall prototypes used by perf trace beauty code and generated socket lookup tables.

## Important APIs, Types, And Functions
Important types include `sa_family_t`, `struct sockaddr`, `struct sockaddr_unsized`, `struct linger`, `struct msghdr`, `struct user_msghdr`, `struct mmsghdr`, `struct cmsghdr`, `struct ucred`, and `struct scm_timestamping_internal`. Important macros include `CMSG_ALIGN`, `CMSG_DATA`, `CMSG_SPACE`, `CMSG_LEN`, `CMSG_FIRSTHDR`, `CMSG_OK`, `for_each_cmsghdr`, `AF_*`, `PF_*`, `SOMAXCONN`, `MSG_*`, `SOL_*`, and `MSG_INTERNAL_SENDMSG_FLAGS`.

## Control Flow
The only executable logic is inline ancillary-data iteration: `__cmsg_nxthdr()` advances by aligned cmsg length and returns null if the next header would exceed the control buffer; `cmsg_nxthdr()` wraps it for `struct msghdr`; `msg_data_left()` returns the remaining iterator count.

## State, Dependencies, And Integration
The header depends on `asm/socket.h`, `linux/sockios.h`, `linux/uio.h`, `linux/types.h`, `linux/compiler.h`, and `uapi/linux/socket.h`. In perf's beauty tree, constants feed socket family/level/protocol decoders, while structure definitions support augmented syscall argument interpretation.

## Risks And Test Signals
This copy must track kernel ABI definitions. Drift can cause wrong string tables or struct interpretation for recorded syscalls. Tests should verify socket family, protocol level, message flag, and ancillary-data related formatting against current UAPI values.

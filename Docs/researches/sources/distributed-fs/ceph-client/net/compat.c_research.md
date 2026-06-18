# sources/distributed-fs/ceph-client/net/compat.c

## Purpose
`compat.c` implements 32-bit compatibility handling for socket syscalls on 64-bit kernels. It translates 32-bit user `msghdr` and ancillary data layouts into native kernel forms, translates native control messages back into 32-bit layout, handles SCM_RIGHTS fd delivery, and exposes compat socket syscall wrappers including legacy `socketcall`.

## Important APIs, types, and functions
- `__get_compat_msghdr()` copies fields from an already loaded `compat_msghdr` into a kernel `msghdr`, clamps name length, sets control-user state, and optionally saves the user address pointer.
- `get_compat_msghdr()` copies the user header, calls the internal converter, and imports the compat iovec into `msg_iter`.
- `cmsghdr_from_user_compat_to_kern()` walks 32-bit control messages, computes native control length, allocates stack or socket memory, and copies/realigns ancillary records.
- `put_cmsg_compat()` writes a native control message into the caller's 32-bit control buffer, including old 32-bit timeval/timespec conversion when required.
- `scm_detach_fds_compat()` installs received file descriptors into the compat user's SCM_RIGHTS buffer and truncates when the buffer cannot hold all fds.
- Compat syscall wrappers dispatch `sendmsg`, `sendmmsg`, `recvmsg`, `recv`, `recvfrom`, `recvmmsg_time64`, optional `recvmmsg_time32`, and legacy `socketcall`.

## Control flow
Input message conversion copies the compat header from user memory, normalizes absent names to zero length, rejects negative name length and too many iovecs, imports iovecs as source or destination depending on receive/send context, and leaves control data marked as user-backed until ancillary conversion is requested.

Ancillary input conversion first validates every compat cmsg and accumulates the native aligned length. It then uses the provided stack buffer or `sock_kmalloc()`, copies each cmsg header and data payload into native `cmsghdr` layout, and only publishes `kmsg->msg_control` and native `msg_controllen` after the full conversion succeeds. Failure frees any socket allocation and returns `-EFAULT`, `-EINVAL`, or `-ENOMEM`.

Ancillary output conversion checks remaining user control space, converts old timestamp control payloads for 32-bit time ABIs, writes a `compat_cmsghdr`, copies payload data, sets `MSG_CTRUNC` when short, and advances `msg_control_user`/`msg_controllen`.

`socketcall` validates the subcall number, copies the expected number of 32-bit arguments, audits them, and dispatches to native socket helpers with pointer arguments passed through `compat_ptr()`. Individual compat syscall wrappers mostly call native `__sys_*` helpers with `MSG_CMSG_COMPAT` added to flags.

## State and persistence behavior
The file maintains no durable state. It mutates per-call `msghdr` cursors, flags, control pointers, and SCM cookies. Received fds installed by `scm_detach_fds_compat()` become normal process file descriptors; the SCM cookie is destroyed after detaching.

## Dependencies and integration points
This is generic networking compatibility code, not Ceph-specific. It depends on Linux compat types, uaccess helpers, socket core helpers, audit hooks, SCM fd helpers, timestamp ABI definitions, and native socket syscall implementations. The file lives under the same source tree subset but integrates with the kernel network syscall layer.

## Risks and edge cases
- Cmsg length validation and alignment are security-sensitive because they parse user-controlled buffers.
- Integer truncation between compat sizes and native sizes can corrupt cursor arithmetic if checks regress.
- `put_cmsg_compat()` copies only the truncated payload length after setting `MSG_CTRUNC`; callers must tolerate partial ancillary messages.
- Time conversion depends on `COMPAT_USE_64BIT_TIME` and old timestamp cmsg types.
- `scm_detach_fds_compat()` must avoid leaking file references when the user buffer is too small or fd installation fails.
- `socketcall` argument count table must match legacy syscall numbering.

## Test signals
Test valid and malformed compat msghdrs, boundary `msg_namelen`, excessive iovec counts, empty and invalid cmsg buffers, multiple cmsg realignment, stack versus socket allocation paths, timestamp cmsg conversion, short control buffers setting `MSG_CTRUNC`, SCM_RIGHTS delivery with too few slots, all compat syscall wrappers adding `MSG_CMSG_COMPAT`, and legacy `socketcall` dispatch/audit behavior.

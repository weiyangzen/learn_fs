# sources/distributed-fs/ceph-client/net/core/scm.c

## Purpose

`scm.c` implements common socket control-message processing for ancillary data passed through `sendmsg()` and `recvmsg()`. It handles `SOL_SOCKET` control messages such as `SCM_RIGHTS`, `SCM_CREDENTIALS`, `SCM_SECURITY`, timestamping control messages, and Unix-socket `SCM_PIDFD` receive support. The file is shared socket infrastructure used especially by Unix sockets and protocols that expose credentials, file descriptors, security labels, timestamps, or control-message output to user space.

## Important APIs, Types, And Functions

`struct scm_cookie` is the main transient container for ancillary state attached to a message. It can carry a `struct scm_fp_list` of file descriptors, credentials, a `struct pid` reference, and security data. `struct scm_fp_list` tracks referenced `struct file *` objects, the owning user, Unix-socket count, and optional Unix inflight graph state.

`scm_check_creds()` validates user-supplied `struct ucred` against the caller's current credentials and capabilities. `scm_fp_copy()` parses `SCM_RIGHTS`, validates file descriptor counts and individual descriptors, rejects io_uring file objects, takes file references, counts Unix sockets, and creates the fp list when needed.

`__scm_send()` is the main send-side parser. It walks control-message headers, validates `CMSG_OK()`, accepts `SCM_RIGHTS` only for Unix-family sockets, validates and stores `SCM_CREDENTIALS`, resolves pid references, and destroys partially built state on error. `__scm_destroy()` releases fp-list files and uid references. `scm_fp_dup()` duplicates an fp list and takes new file references.

`put_cmsg()` writes a control message to either user memory or a kernel msghdr buffer and handles truncation with `MSG_CTRUNC`. `put_cmsg_notrunc()` refuses to emit truncated output. `put_cmsg_scm_timestamping64()` and `put_cmsg_scm_timestamping()` convert internal timestamp arrays into new or old socket timestamping ABI structures.

`scm_detach_fds()` installs received `SCM_RIGHTS` files into the receiver's fd table, honoring `MSG_CMSG_CLOEXEC`, compatibility cmsg handling, truncation, and cleanup. `scm_recv()` and `scm_recv_unix()` are receive-side orchestrators. Unix receive additionally supports `scm_pidfd_recv()` when `sk_scm_pidfd` is enabled.

## Control Flow

On send, protocol code calls `__scm_send()` with a socket, userspace message, and initialized scm cookie. The function iterates each cmsghdr. Non-`SOL_SOCKET` messages are ignored by this common layer. `SCM_RIGHTS` requires `sock->ops->family == PF_UNIX` and is copied by `scm_fp_copy()`. `SCM_CREDENTIALS` must have exact length, pass `scm_check_creds()`, resolve or replace the stored pid reference with `scm_replace_pid()`, and convert uid/gid into kernel IDs. Any error destroys accumulated scm state before returning.

On receive, `scm_recv()` or `scm_recv_unix()` calls `__scm_recv_common()`. If the receiver provided no control buffer, the function marks `MSG_CTRUNC` when there was ancillary data to report, destroys scm state, and stops. Otherwise it emits credentials when requested by the socket, emits LSM security data when configured, detaches file descriptors if present, and leaves credential cleanup to the caller. `scm_recv_unix()` then optionally emits `SCM_PIDFD` and destroys credential references.

Control-message output uses `put_cmsg()`: validate control buffer capacity, optionally mark truncation, write cmsghdr fields and payload through hardened user access or kernel copies, advance `msg_control` and reduce `msg_controllen`.

## State And Persistence Behavior

Most state is per-message and reference-counted. File references taken during `SCM_RIGHTS` parsing persist until delivered to a receiver fd table or released by `__scm_destroy()`. The fp list stores a user reference to account the sender and, under Unix socket support, metadata used by inflight-cycle tracking elsewhere.

Credential and pid state lives in the `scm_cookie` for the lifetime of message transfer. `scm_replace_pid()` registers pidfs state and stores a `struct pid` reference; receive-side pidfd generation can allocate a new file descriptor and install the pidfd file only after the cmsg is successfully emitted. There is no disk persistence.

## Dependencies And Integration Points

This code integrates with VFS file references (`fget_raw()`, `fput()`, `get_file()`), fd installation (`scm_recv_one_fd()`, `fd_install()`), credential and namespace helpers, pidfs/pidfd helpers, LSM security context export, io_uring file detection, Unix socket helpers, compat cmsg handling, and hardened usercopy helpers.

It is tightly coupled to socket flags: `sk_scm_credentials`, `sk_scm_security`, and `sk_scm_pidfd` decide which ancillary data is emitted on receive. `MSG_CMSG_COMPAT`, `MSG_CMSG_CLOEXEC`, and `MSG_CTRUNC` affect ABI behavior.

## Risks And Edge Cases

Reference cleanup is the central risk. Errors while copying many file descriptors leave some references already acquired; `__scm_send()` calls `scm_destroy()` on error, and `scm_detach_fds()` destroys the fp list after successful fd installation attempts. Any future changes must preserve this ownership transfer.

Credential validation is security-sensitive. `scm_check_creds()` allows a supplied pid only if it matches the caller thread-group pid or the caller has `CAP_SYS_ADMIN` in the active pid namespace userns, and uid/gid only if they match real/effective/saved IDs or the caller has set-id capabilities. Namespace conversions must remain consistent.

Control buffer truncation is ABI-sensitive. `put_cmsg()` can emit truncated cmsgs and set `MSG_CTRUNC`, while `put_cmsg_notrunc()` and `scm_pidfd_recv()` use stricter checks. Mixing these semantics incorrectly can leak partially useful ancillary data or lose expected truncation signals.

`SCM_RIGHTS` rejects io_uring files and caps descriptor counts at `SCM_MAX_FD`. Unix sockets have additional inflight and cycle constraints outside this file; the `count_unix` and Unix-only fields must remain correctly initialized and duplicated.

## Test Signals

Test coverage should include Unix socket fd passing, invalid fd arrays, more than `SCM_MAX_FD`, io_uring fd rejection, credential spoofing attempts with and without capabilities, pid namespace behavior, empty or short cmsghdrs, no-control-buffer receive truncation, compat cmsg paths, `MSG_CMSG_CLOEXEC`, timestamping cmsg output, LSM security cmsg emission, and `SCM_PIDFD` truncation and successful fd installation.

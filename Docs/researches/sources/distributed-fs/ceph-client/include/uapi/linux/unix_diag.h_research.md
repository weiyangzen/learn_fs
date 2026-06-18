# sources/distributed-fs/ceph-client/include/uapi/linux/unix_diag.h

Purpose: Defines AF_UNIX socket diagnostic request, response, and attributes for sock_diag netlink.

Important APIs/types/functions: `struct unix_diag_req` filters by family, protocol, states, inode, show mask, and cookie. Show flags request name, VFS info, peer, pending connections, queue lengths, memory info, and UID. `struct unix_diag_msg` reports family/type/state/inode/cookie. Attribute enum includes name, VFS, peer, icons, receive queue length, meminfo, shutdown, and UID. `unix_diag_vfs` and `unix_diag_rqlen` carry inode/device and queue counters.

Control flow: Userspace sends a diagnostic request through netlink; the kernel filters AF_UNIX sockets and emits messages with requested optional attributes.

State and persistence behavior: Observes transient socket state only. Cookies help correlate sockets across dumps but are not persistent storage.

Dependencies and integration points: Includes `linux/types.h`; integrates with sock_diag, AF_UNIX, netlink diagnostics, and tools like `ss`.

Risks: Optional show flags can expose path, UID, peer, queue, or memory data and must respect permissions. Attribute numbering is ABI-stable.

Test signals: Dump active UNIX sockets with each show flag, verify cookie/inode filters, queue length reporting, pending connection icons, UID exposure, and malformed request handling.

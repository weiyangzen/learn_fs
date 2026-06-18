<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inet_diag.h -->
# sources/distributed-fs/ceph-client/include/linux/inet_diag.h

Purpose: Declares inet socket diagnostic handler interfaces for netlink-based socket dumps.

Important APIs/types/functions: `struct inet_diag_handler` binds protocol handlers with dump/destroy helpers and optional get-info logic. `struct inet_diag_dump_data` stores request nlattrs, bytecode, netlink cb data, and cgroup id. APIs fill common socket diagnostic messages/attrs, evaluate bytecode filters, and register/unregister handlers.

Control flow: Netlink diagnostic requests dispatch to registered protocol handlers, filter sockets with bytecode/cgroup data, and fill `inet_diag_msg` plus optional attributes.

State/persistence: Registered handlers persist until unregistered; dump data is per-netlink request.

Dependencies/integration: Depends on netlink, UAPI inet_diag, IPv6 optional attrs, cgroup socket data, and protocol hashinfo.

Risks: Attribute size calculations must match fill logic; handler lifetime must be synchronized with netlink dumps.

Test signals: `ss`/inet_diag dumps for TCP/UDP variants, bytecode filters, cgroup attrs, IPv6 attrs, and handler unregister during module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inet_diag.h -->

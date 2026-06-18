<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/port.h

Purpose: declares kernel/user functions for the UML `port:` channel backend, which accepts host TCP/telnet connections and binds them to waiting UML lines.

Important APIs/types/functions: prototypes include `port_data()`, `port_wait()`, `port_kern_close()`, `port_connection()`, `port_listen_fd()`, `port_read()`, `port_kern_free()`, `port_rcv_fd()`, and `port_remove_dev()`.

Control flow: kernel-side code allocates/listens/waits through `port_kern.c`; user-side code opens TCP sockets and helper processes through `port_user.c`.

State and persistence: no state is owned here. Runtime state is in `port_list`, `port_dev`, and `connection` objects in implementation files.

Dependencies and integration points: bridges `port_user.c` and `port_kern.c`, and is used by the `port_ops` channel backend.

Risks: the header includes some historical declarations not implemented in the researched files, so changes should confirm actual users before removing them.

Test signals: compile port backend and boot `con=port:<n>` or `ssl=port:<n>`, then connect with telnet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port.h -->

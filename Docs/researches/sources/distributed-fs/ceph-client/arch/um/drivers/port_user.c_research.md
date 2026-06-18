<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/port_user.c

Purpose: implements the host-side `port:` channel backend. It parses TCP port numbers, opens listening sockets, accepts host connections, and starts `in.telnetd` with UML's port-helper.

Important APIs/types/functions: `struct port_chan` stores raw-mode flag, saved termios, kernel-side port data, and printable port string. Backend callbacks are `port_init()`, `port_open()`, `port_close()`, `port_free()`, and `port_ops`. Host helpers are `port_listen_fd()`, `port_pre_exec()`, and `port_connection()`.

Control flow: `port_init()` parses `:port`, obtains shared kernel listener state through `port_data()`, and stores channel data. `port_open()` waits for a completed port connection, optionally sets raw mode, and returns the connected FD. `port_connection()` accepts a TCP connection, verifies the helper executable from `UML_PORT_HELPER` or default `OS_LIB_PATH/uml/port-helper`, creates a pipe, runs `in.telnetd -L <helper>`, and returns the accepted FD plus helper PID.

State and persistence: listener and connection state is runtime-only; no data is persisted. Environment variable `UML_PORT_HELPER` influences helper path.

Dependencies and integration points: depends on TCP sockets, `in.telnetd`, UML port-helper, FD pipes, `run_helper()`, raw terminal helpers, and `port_kern.c` queueing.

Risks: external helper availability is mandatory for useful telnet sessions. Accepted sockets and helper pipes must be closed on all failure paths. Raw-mode saved termios is captured but close does not restore it directly because telnet sessions are helper-managed.

Test signals: bind port, connect with telnet, missing helper path, custom `UML_PORT_HELPER`, multiple waiting devices, raw/non-raw sessions, and port removal while helper processes exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port_user.c -->

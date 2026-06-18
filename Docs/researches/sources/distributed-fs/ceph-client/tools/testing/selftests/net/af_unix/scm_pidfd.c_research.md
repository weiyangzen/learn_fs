# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_pidfd.c

Purpose: Validates AF_UNIX `SCM_PIDFD`, `SO_PASSPIDFD`, and `SO_PEERPIDFD` behavior for live and exited peers over stream and datagram sockets with pathname and abstract addresses.

Important APIs/types/functions: Uses `SO_PASSCRED`, `SO_PASSPIDFD`, `SCM_CREDENTIALS`, `SCM_PIDFD`, `SO_PEERCRED`, `SO_PEERPIDFD`, pidfd fdinfo parsing, `PIDFD_GET_INFO`, shared `mmap()` for client addresses, `fork()`, `socket/bind/connect/listen/accept`, and kselftest fixtures.

Control flow: Parent creates and binds a server socket, forks a child client, and synchronizes through a pipe. The child connects, enables credential/pidfd passing, receives a byte from the parent, parses credentials and pidfd, and validates the pidfd points to the parent. It then sends a byte back and exits with a special success code. The parent waits for child exit, enables credential/pidfd passing on its endpoint, receives the child's message, and validates the received pidfd can report the dead child's exit code through `PIDFD_GET_INFO`.

State and persistence behavior: Fixture stores server fd, child pid, startup pipe, server address, and shared client address. Pathname socket files are unlinked in teardown; abstract sockets have no filesystem artifact.

Dependencies and integration points: Includes `../../pidfd/pidfd.h` for pidfd ioctl definitions. Requires modern AF_UNIX pidfd passing support and kernel pidfd info support.

Risks: Uses `/proc/self/fdinfo` text parsing to validate pidfds, so procfs availability matters. Teardown kills the child unconditionally; if it already exited, `kill()` may fail harmlessly but wait is still attempted. Datagram behavior differs from stream for peer credential getsockopt, and the code intentionally skips stream-only checks for datagrams.

Test signals: Passing variants confirm live peer pidfd delivery, credential co-delivery, dead process pidfd exit reporting, abstract/pathname address handling, and stream `SO_PEERPIDFD` parity with `SO_PEERCRED`.

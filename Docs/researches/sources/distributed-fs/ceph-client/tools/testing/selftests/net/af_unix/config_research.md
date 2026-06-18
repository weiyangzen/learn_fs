# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/config

Purpose: Declares kernel configuration needed by AF_UNIX selftests.

Important APIs/types/functions: Requests `CONFIG_AF_UNIX_OOB=y`, `CONFIG_UNIX=y`, and `CONFIG_UNIX_DIAG=m`.

Control flow: Consumed by kselftest config tooling.

State and persistence behavior: No runtime state. It ensures AF_UNIX sockets, urgent/OOB support, and UNIX socket diagnostic netlink are available.

Dependencies and integration points: Supports `msg_oob.c` for urgent data, `diag_uid.c` for `NETLINK_SOCK_DIAG`, and all AF_UNIX socket behavior tests.

Risks: If `UNIX_DIAG` is modular but not loaded, diagnostic tests may fail unless autoload works. Missing `AF_UNIX_OOB` breaks urgent-data semantics.

Test signals: Built kernel exposes AF_UNIX sockets, `SOCK_DIAG_BY_FAMILY` UNIX diagnostics, and OOB behavior required by this directory.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/Kconfig -->
# sources/distributed-fs/ceph-client/net/unix/Kconfig

## Purpose
This Kconfig file defines build-time options for Unix domain sockets, optional AF_UNIX out-of-band message support, and the UNIX sock_diag monitoring interface.

## Important APIs, Types, and Functions
- `config UNIX` enables core Unix domain socket support.
- `config AF_UNIX_OOB` enables `MSG_OOB` support for Unix stream sockets and defaults to `y` when UNIX is enabled.
- `config UNIX_DIAG` builds the netlink sock_diag interface used by tools such as `ss`.

## Control Flow
The selected symbols control Makefile object inclusion and conditional code in `af_unix.c`, `diag.c`, and related files. `UNIX` is a boolean core feature, while `UNIX_DIAG` is tristate and can be a module.

## State and Persistence
There is no runtime state. These symbols persist in kernel configuration and shape compiled code and modules.

## Dependencies and Integration Points
`AF_UNIX_OOB` and `UNIX_DIAG` both depend on `UNIX`. `UNIX_DIAG` maps to `unix_diag.o`, and `AF_UNIX_OOB` enables OOB queue handling and `SIOCATMARK` support in the main socket implementation.

## Risks and Edge Cases
Disabling `UNIX` removes functionality many userspace programs assume is present. Disabling `AF_UNIX_OOB` makes `MSG_OOB` return unsupported behavior. `UNIX_DIAG` defaults to `n` despite common tooling depending on it for diagnostics.

## Test Signals
Build matrix tests should cover `UNIX=y`, `AF_UNIX_OOB=y/n`, and `UNIX_DIAG=y/m/n`, verifying object inclusion, socket creation, OOB behavior, and `ss -x`/sock_diag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/Kconfig -->

# sources/distributed-fs/ceph-client/include/linux/io_uring/net.h

Purpose: This small header exposes the socket-specific io_uring command entry point.

Important APIs, types, and functions: It forward-declares `struct io_uring_cmd` and declares `io_uring_cmd_sock(struct io_uring_cmd *cmd, unsigned int issue_flags)` when io_uring is enabled. Disabled builds return `-EOPNOTSUPP`.

Control flow: Network-capable uring commands are dispatched through `io_uring_cmd_sock` with core-provided issue flags; unsupported configurations fail immediately.

State and persistence: No state is defined here. Command and socket state live in io_uring core and networking code.

Dependencies and integration points: Integrates the io_uring command layer with socket/network command handling while avoiding full networking includes in generic users.

Risks: Callers must propagate `-EOPNOTSUPP` in disabled builds. Issue flags should be treated as an opaque mask from core. The header does not validate that the command's file is a socket.

Test signals: Build with and without `CONFIG_IO_URING`, exercise socket uring command dispatch, verify unsupported errors, and test cancellation/completion paths in networking command implementations.

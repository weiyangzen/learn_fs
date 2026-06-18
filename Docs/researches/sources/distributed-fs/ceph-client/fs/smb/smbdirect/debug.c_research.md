## sources/distributed-fs/ceph-client/fs/smb/smbdirect/debug.c

Purpose: Emits legacy proc/seq-file diagnostics for an SMBDirect socket so upper SMB code can expose transport status, negotiated parameters, counters, credits, and memory-registration state.

Important APIs and functions: `smbdirect_connection_legacy_debug_proc_show()` is exported and takes a socket, the caller's RDMA read/write threshold, and a `seq_file`. It reads `struct smbdirect_socket_parameters`, socket status, statistics, atomic credit counters, and MR counters.

Control flow: The function returns immediately for a NULL socket. Otherwise it prints multiple newline-separated groups: protocol/status, receive/send credits and sizes, fragmented sizes, keepalive and read/write limits, receive-buffer counters, reassembly counters, current credit counts, pending sends, and MR resource state.

State and persistence: It is read-only diagnostic code. It observes live in-memory socket fields without taking locks, so output is a best-effort snapshot and may race with connection teardown or data-path updates. It persists nothing.

Dependencies and integration points: Depends on `seq_file`, `internal.h`, `SMBDIRECT_V1`, `smbdirect_socket_status_string()`, and the socket layout in `socket.h`. It is exported for external SMB client/server diagnostic plumbing that still expects the older debug layout.

Risks and edge cases: Because values are read locklessly, counters and related fields can be internally inconsistent under concurrent traffic. A non-NULL socket being destroyed concurrently would require external lifetime protection by the caller. Keepalive interval is printed in microsecond-looking units by multiplying milliseconds by 1000, so consumers must know the legacy display convention.

Test signals: Proc/debug output should be checked for NULL sockets, connected sockets with active send/receive traffic, MR use, disconnecting sockets, and stable formatting expected by legacy consumers.

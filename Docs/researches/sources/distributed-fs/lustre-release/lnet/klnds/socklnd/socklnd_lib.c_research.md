# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_lib.c

## Purpose
Provides Linux socket-facing primitives used by the higher-level socklnd state machines: address discovery, capability checks, nonblocking send/receive, checksum calculation, socket option setup, callback install/reset, push/nodelay behavior, tunable inspection, and memory-pressure detection.

## Important APIs and functions
`ksocknal_lib_get_conn_addrs` snapshots peer/local socket addresses. `ksocknal_lib_zc_capable` checks route capabilities for scatter/gather and checksum offload. `ksocknal_lib_send_hdr`, `ksocknal_lib_send_kiov`, and `ksocknal_lib_recv` perform nonblocking I/O. `ksocknal_lib_csum_tx` computes v2 checksums. `ksocknal_lib_setup_sock` configures GFP_NOFS, linger, Nagle, buffers, keepalive, and TOS. Callback helpers save, set, and restore `sk_data_ready` and `sk_write_space`. `ksocknal_lib_memory_pressure` distinguishes retryable full-socket cases from ENOMEM-like stalls.

## Control flow
The scheduler calls send helpers without letting socket code mutate the driver's iov state. Header sends optionally compute checksum on first v2 send and use `MSG_MORE` when queued data remains. Payload sends use sendpage or `MSG_SPLICE_PAGES` for zero-copy-marked transfers, otherwise bvec iterators. Receive uses `sock_recvmsg` into the current iterator and accumulates checksum only for the protocol/data combinations that require it. Socket callbacks acquire global read locks, retrieve `sk_user_data`, and enqueue scheduler work or delegate to saved callbacks if termination already detached the conn.

## State and persistence
No standalone persistent state. It mutates connection address fields, RX checksum accumulator, socket callbacks, socket flags/options, and TCP Nagle/keepalive/TOS settings. Callback restoration is essential because sockets may outlive module code.

## Dependencies and integration points
Depends on Linux socket, TCP, bvec/iov iterator, page mapping, route capability, and compatibility macros. It is called by `socklnd.c` during connection creation/termination and by `socklnd_cb.c` during runtime I/O.

## Risks and test signals
Risks include callback lifetime races, checksum coverage mismatch across protocol versions, highmem mapping issues, kernel-version sendpage behavior, keepalive/TOS option failures, and false ENOMEM detection. Test with v2 checksums, v3/v4 checksum-off cases, zero-copy and non-zero-copy sends, callback reset under simultaneous socket readiness, configured buffer/keepalive/nagle/tos values, and kernels with and without `MSG_SPLICE_PAGES`.

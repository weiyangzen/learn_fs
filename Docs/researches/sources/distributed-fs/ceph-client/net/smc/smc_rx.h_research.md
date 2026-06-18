# sources/distributed-fs/ceph-client/net/smc/smc_rx.h

Purpose: Exposes the receive-side SMC entry points and the small data-availability helper used by AF_SMC socket code and peer CDC handling.

Important APIs/types/functions: `smc_rx_init()` installs receive callbacks and initializes connection receive state. `smc_rx_recvmsg()` receives into a userspace message or pipe. `smc_rx_wait()` waits on socket state plus caller-provided data criteria. `smc_rx_data_available()` returns `bytes_to_rcv - peeked` from the connection.

Control flow: Higher-level socket receive code calls `smc_rx_recvmsg()` under the socket lock. Other code can call `smc_rx_wait()` with either raw data availability or stricter criteria such as no pending splice bytes. The inline availability helper is used by both wait and receive loops.

State and persistence behavior: The header itself has no persistent state, but all functions operate on `struct smc_sock`/`struct smc_connection` receive counters, cursors, and socket wait queues.

Dependencies and integration points: Depends on Linux socket types and `smc.h`. It integrates with `smc_tx.h` through consumer updates implemented in the `.c` file and with socket receive operations in the AF_SMC layer.

Risks and test signals: Risks are mainly interface misuse: calling without expected socket locking, passing the wrong baseline for peeking, or ignoring splice-pending constraints. Test by compiling AF_SMC receive users and running read, peek, splice, timeout, and shutdown paths.

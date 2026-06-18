# sources/distributed-fs/ceph-client/net/smc/smc.h

## Purpose
`smc.h` is the socket-facing internal contract for the SMC subsystem. It defines SMC protocol versions, release level, protocol numbers, socket states, feature flags, CDC flag and cursor host representations, the central `struct smc_connection`, the `struct smc_sock` socket container, exported socket operation prototypes, callback helpers, byte-order helpers, IPsec detection, workqueue declarations, and accept/fallback utility prototypes.

## Important APIs, Types, And Functions
Important types include `enum smc_state`, `enum smc_supplemental_features`, `struct smc_wr_rx_hdr`, `struct smc_cdc_conn_state_flags`, `struct smc_cdc_producer_flags`, `union smc_host_cursor`, `struct smc_host_cdc_msg`, `enum smc_urg_state`, `struct smc_connection`, and `struct smc_sock`. Inline helpers include `smc_sk()`, `smc_init_saved_callbacks()`, `smc_clcsock_user_data()`, `smc_clcsock_user_data_rcu()`, `smc_clcsock_replace_cb()`, `smc_clcsock_restore_cb()`, `hton24()`, `ntoh24()`, `using_ipsec()`, and `smc_sock_set_flag()`. The header declares the socket operation functions implemented in `af_smc.c` and workqueue globals used by close, handshake, and TX/CDC logic.

## Control Flow
The header has little standalone execution, but it shapes the subsystem control flow. `struct smc_sock` is allocated as the protocol object and wraps a TCP CLC socket plus SMC connection state. Socket operations use `smc_sk()` to move from `struct sock` to the container. TCP callback replacement stores originals in `smc_sock` fields and restores them with the inline helpers during fallback or listen teardown. CDC receive and transmit paths update `struct smc_connection` cursors and flags, while close paths interpret `enum smc_state` values to progress active and passive shutdown.

## State And Persistence
`struct smc_connection` persists link-group membership, selected RDMA link, local alert token, peer RMB metadata, send/RMB buffer descriptors, cursor state for local TX/RX CDC messages, send-buffer and peer-buffer space counters, CDC sequence numbers, pending WR counters, TX retry work, urgent-data state, receive byte counters, close/abort work, SMC-D receive tasklet, peer token, and killed/freed/out-of-sync flags. `struct smc_sock` persists CLC socket pointer, saved callbacks, listen parent and accept queue, handshake work, fallback flags, peer diagnosis, and release locking. These fields are shared by socket operations, CDC/TX/RX, close, and core link-group code.

## Dependencies And Integration Points
`smc.h` includes Linux socket/sock/genetlink types and `smc_ib.h`, and is included across nearly all SMC modules. It integrates with TCP callback user-data conventions, optional XFRM/IPsec policy checks, netlink handshake-limit commands, SMC core link groups, RDMA link/buffer descriptors, SMC-D tasklet handling, and generic socket flags.

## Risks And Edge Cases
The header encodes wire-adjacent bitfield layout for CDC flags, so endian definitions must stay aligned with protocol expectations. Cursor copying uses atomic64 where available and a connection spinlock otherwise; mixed use can produce corrupt flow control. `struct smc_connection` lifetime is tied to async work, tasklets, and link-group cleanup, making field ownership and state transitions sensitive. TCP callback save/restore helpers only save once, so nested replacement must preserve ordering.

## Test Signals
Primary signals are build coverage across IPv4, IPv6, XFRM enabled/disabled, and architectures with or without `ATOMIC64_INIT`; runtime close-state, urgent-data, fallback-callback, and CDC cursor tests; static assertions or protocol tests for bitfield and 24-bit conversion layout; and lockdep/KCSAN coverage around cursor and callback state.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ktls.c

## Purpose
Implements optional kernel TLS transmit offload support for funeth when `CONFIG_TLS_DEVICE` is enabled. It creates a per-port hardware kTLS resource, registers `tlsdev_ops`, programs TLS contexts, removes them, and handles sequence resynchronization.

## Important APIs and Functions
`fun_ktls_init()` creates a `FUN_ADMIN_OP_KTLS` resource for `netdev->dev_port`, sets `fp->ktls_id`, installs `fun_ktls_ops`, and advertises `NETIF_F_HW_TLS_TX`. `fun_ktls_cleanup()` destroys the resource if present. `fun_ktls_add()` supports only TX direction, TLS 1.2, and AES-GCM-128; it sends key, IV, salt, record sequence, and TCP sequence via `FUN_ADMIN_SUBOP_MODIFY`. `fun_ktls_del()` sends a remove modify command. `fun_ktls_resync()` updates record sequence and TCP sequence for an existing hardware TLS id.

## Control Flow
Initialization is best-effort from `fun_create_netdev()`; failure leaves software TLS fallback. Add validates direction, protocol, and cipher, submits an admin command, zeroes key material with `memzero_explicit()`, then stores the returned hardware TLS id and `next_seq` in the socket driver context. Delete and resync are also admin modify commands keyed by `fp->ktls_id` and the per-socket `tlsid`.

## State and Persistence
Persistent state lives in `fp->ktls_id`, atomic TLS operation counters, and per-socket `struct fun_ktls_tx_ctx` (`tlsid`, `next_seq`). The Tx path in `funeth_tx.c` consumes this state to decide whether to tag a packet for hardware TLS or request/fallback to software encryption.

## Dependencies and Integration Points
Depends on Linux TLS device offload APIs and funeth admin command structures from `funeth.h`. It integrates with netdev features, `tls_driver_ctx()`, and Tx descriptor emission where `FUN_ETH_TX_TLS` and `struct fun_eth_tls` are appended.

## Risks and Test Signals
Risks include sequence tracking bugs causing plaintext/ciphertext mismatch, unsupported cipher fallback expectations, admin failure while feature bits are enabled, and key material lifetime. Test with TLS 1.2 AES-GCM-128 TX offload, out-of-order sequence resync, delete during socket close, module unload with active TLS sockets, and ethtool TLS counters (`tx_tls_ctx`, `tx_tls_del`, `tx_tls_resync`).

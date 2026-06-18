# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/tls.c

## Purpose
This file implements NFP kernel TLS device offload for TLS 1.2 AES-GCM-128. It negotiates firmware crypto operation bits, sends CCM mailbox commands to add/delete/update TLS contexts, manages per-direction enable counts, registers `tlsdev_ops`, and handles firmware-originated RX resync requests.

## Important APIs, types, and functions
- `nfp_net_tls_init()` validates firmware op bits and CCM message support, resets firmware TLS state, disables crypto ops initially, enables netdev TLS feature flags, and assigns `netdev->tlsdev_ops`.
- `nfp_net_tls_add()` validates cipher/socket family, enables the per-direction crypto opcode on first connection, builds IPv4/IPv6 add requests, copies key/IV/salt/record sequence, sends `NFP_CCM_TYPE_CRYPTO_ADD`, zeroes key material, stores firmware handle in TLS driver context, and sets RX resync mode when needed.
- `nfp_net_tls_del()` decrements connection count and sends delete by firmware handle.
- `nfp_net_tls_resync()` sends synchronous TX updates or posted/asynchronous RX resync/update messages.
- `nfp_net_tls_rx_resync_req()` maps firmware packet offsets to a socket lookup and asks the kernel TLS core to resync RX.

## Control flow
Connection add increments direction count under the control BAR lock; 0-to-1 transitions toggle the firmware opcode bit and run `NFP_NET_CFG_UPDATE_CRYPTO`. The add request uses synthetic connection IDs for TX because TX firmware matching does not need original 5-tuple, while RX uses reversed socket tuple fields for lookup. After mailbox add, nonzero firmware errors unwind the count and optionally log table-full once. RX resync requests validate header bounds, identify IPv4/IPv6, look up an established socket, verify it is RX device-offloaded and not shut down, optionally compare firmware handle, then calls `tls_offload_rx_resync_request()`.

## State and persistence
Persistent live state is in memory only: `ktls_tx_conn_cnt`, `ktls_rx_conn_cnt`, `dp.ktls_tx`, `ktls_conn_id_gen`, no-space/resync counters, and per-socket `nfp_net_tls_offload_ctx` firmware handles. Key material is transient in the request skb and is explicitly zeroed after the CCM transaction while holding an extra skb reference.

## Dependencies and integration points
This file depends on the CCM mailbox transport in `ccm_mbox.c`, firmware ABI structures in `fw.h`, Linux kTLS (`tlsdev_ops`, driver contexts, resync APIs), IPv4/IPv6 established socket lookup, and NFP TLV capability fields (`crypto_ops`, `crypto_enable_off`, `mbox_cmsg_types`, `tls_resync_ss`).

## Risks
The main risks are key handling, request layout, and async RX resync lifetime. The code assumes CCM does not reallocate the skb so key material can be zeroed in place. RX resync posting uses `GFP_ATOMIC` and does not wait for firmware completion. Connection counts are protected by the BAR lock, and failed reconfig must accurately undo count/opcode changes. Socket lookup from firmware-provided offsets must reject malformed packets.

## Test signals
Signals include TLS add/delete for IPv4, IPv4-mapped IPv6, native IPv6, unsupported ciphers, table-full firmware replies, TX resync sequence updates, RX resync request success/ignore counters, first/last connection crypto enable transitions, and firmware capability combinations that should leave TLS disabled.

# sources/distributed-fs/ceph-client/include/net/tls.h

## Purpose

`tls.h` is the core kernel TLS (kTLS) internal API. It defines TLS record sizing, software TX/RX contexts, device offload TX/RX contexts, cipher/protocol state, socket ULP context storage, driver offload callbacks, resync protocols, and helper accessors used by the TCP data path and TLS device drivers.

## Important APIs, types, and functions

Important constants include `TLS_MAX_PAYLOAD_SIZE`, `TLS_MIN_RECORD_SIZE_LIM`, `TLS_HEADER_SIZE`, `TLS_TAG_SIZE`, sequence/IV/salt sizes, and configuration values `TLS_BASE`, `TLS_SW`, `TLS_HW`, and `TLS_HW_RECORD`. Key types are `struct tls_sw_context_tx`, `struct tls_sw_context_rx`, `struct tls_strparser`, `struct tls_record_info`, `struct tls_offload_context_tx`, `struct tls_offload_context_rx`, `struct tls_context`, `struct tls_prot_info`, `union tls_crypto_context`, `struct tlsdev_ops`, and `struct tls_offload_resync_async`. Helpers expose context access (`tls_get_ctx()`, `tls_sw_ctx_rx()`, `tls_offload_ctx_tx()`), feature checks (`tls_sw_has_ctx_tx()`/`rx()`, `tls_is_skb_tx_device_offloaded()`), driver-private state (`tls_driver_ctx()`), and RX/TX resync requests.

## Control flow

For software TLS, TX paths encrypt records through `aead_send`, manage `open_rec` and `tx_list`, and schedule delayed TX work. RX paths parse records through the TLS strparser, decrypt asynchronously when possible, queue decrypted data, and wake readers. For device offload, the core tracks record boundaries and calls driver operations to add/delete/resync TLS state. TX validation uses `sk_validate_xmit_skb` to decide whether to offload or fall back to software. RX offload resync is requested through atomic sequence/log fields so hardware and core can re-align after out-of-sync records.

## State and persistence behavior

Per-socket state persists in `inet_connection_sock.icsk_ulp_data` as `struct tls_context`. It carries protocol info, cipher contexts, TX/RX config, saved socket callbacks, crypto info, netdevice pointer, partially sent record state, flags, and reference count. Software contexts own crypto transforms, queues, pending counters, wait queues, and work items. Device contexts own record lists, driver-private state, netdev degradation/closure flags, and resync state. Lifetime is tied to the socket and RCU/refcount release.

## Dependencies and integration points

It depends on TCP, sockets, netdevice, net namespaces, strparser, crypto AEAD, UAPI TLS structures, RCU, workqueues, mutexes, and optional `CONFIG_TLS_DEVICE`. It integrates with TCP ULP setup, sendmsg/recvmsg/sendfile, socket destruction, netdevice TLS offload callbacks, hardware resync, and BPF/diagnostic readers of ULP data.

## Risks and test signals

Risks include stale ULP context reads, wrong crypto-info sizing, asynchronous encrypt/decrypt completion races, netdevice down transitions leaving `TLS_HW` degraded state, record-list lifetime bugs, timestamp/sequence resync errors, and missing memory barriers around TX sync flags. Tests should exercise software TLS send/receive, async crypto, key update pending, partial records, device add/delete, netdev down/up fallback, RX resync modes, TX validation fallback, and builds with `CONFIG_TLS_DEVICE` disabled.

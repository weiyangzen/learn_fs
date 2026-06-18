<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_main.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_main.c

## Purpose
`tls_main.c` is the central TCP ULP registration and configuration layer for kernel TLS. It registers the `tls` ULP, builds TLS-specific `struct proto` and `struct proto_ops` overlays on top of TCP, accepts `SOL_TLS` socket options, creates and frees `struct tls_context`, and coordinates software, device, and TOE record paths. It is the integration point that turns an established TCP socket into a kTLS socket and switches the socket's send/receive operations as TX and RX configurations move from base TCP to software or hardware TLS.

## Important APIs, Types, and Functions
- `tls_cipher_desc[]` describes supported TLS ciphers, their key/IV/salt/record-sequence offsets, AEAD algorithm names, and whether device offload may use them. Compile-time `CHECK_CIPHER_DESC` assertions keep UAPI crypto structures aligned with cipher constants.
- `update_sk_prot()` installs the selected TLS protocol and socket operation tables based on `ctx->tx_conf` and `ctx->rx_conf`.
- `wait_on_pending_writer()`, `tls_push_sg()`, `tls_push_partial_record()`, and `tls_free_partial_record()` handle lower TCP writes and recovery from partially transmitted encrypted records.
- `tls_process_cmsg()` supports `TLS_SET_RECORD_TYPE` ancillary data and forces pending open records out before the record type changes.
- `tls_ctx_create()`, `tls_ctx_free()`, `tls_sk_proto_close()`, and `tls_sk_proto_cleanup()` own context lifetime and restore the original TCP protocol callbacks.
- `do_tls_setsockopt_conf()` and `do_tls_getsockopt_conf()` implement `TLS_TX` and `TLS_RX` key/configuration exchange with userspace, including TLS 1.3 rekey support.
- `do_tls_setsockopt_tx_zc()`, `do_tls_setsockopt_no_pad()`, and `do_tls_setsockopt_tx_payload_len()` expose zero-copy sendfile, TLS 1.3 no-padding expectation, and max payload length controls.
- `build_protos()` and `build_proto_ops()` construct the protocol matrices for combinations of `TLS_BASE`, `TLS_SW`, `TLS_HW`, and `TLS_HW_RECORD`.
- `tls_init()`, `tls_update()`, `tls_get_info()`, and `tls_get_info_size()` implement the TCP ULP hooks.
- `tls_register()` and `tls_unregister()` register per-net TLS statistics/proc support, the TLS strparser workqueue, device TLS support, and the TCP ULP.

## Control Flow
On module init, per-net MIB/proc state is registered, the TLS strparser workqueue is created, device TLS is initialized, and the `tls` ULP is registered with TCP. When userspace attaches the ULP, `tls_init()` ensures the socket is established, optionally lets TOE bypass normal TLS setup, allocates `tls_context`, records the original TCP protocol, and installs the base TLS proto table entry. `setsockopt(SOL_TLS, TLS_TX/TLS_RX)` copies crypto info, validates version/cipher consistency, attempts device offload first, falls back to `tls_set_sw_offload()`, updates statistics, arms RX parsing when needed, and then switches protocol operations. TX/RX operations are then dispatched through software or device functions from `tls_sw.c` and device TLS code. Close cancels TX work, waits on pending writers, releases TX/RX resources, restores original callbacks, invokes the underlying TCP close, and frees context when no hardware side owns it.

## State and Persistence
State is in-memory per socket and per net namespace. `tls_context` stores original TCP callbacks, selected TX/RX configurations, crypto material, cipher contexts, partial-record state, and options such as `zerocopy_sendfile`, `rx_no_pad`, and `tx_max_payload_len`. Crypto key material is wiped with `memzero_explicit()` when configs fail or contexts are freed. Per-net TLS counters are allocated as percpu `linux_tls_mib` storage and exported through `/proc/net/tls_stat`. Protocol and ops matrices are process-global caches keyed by IPv4/IPv6 and TX/RX config, rebuilt when the underlying TCP proto pointer changes.

## Dependencies and Integration Points
This file depends on TCP ULP infrastructure, inet diag ULP info, net namespace pernet operations, proc/MIB support, `net/tls.h` UAPI definitions, software TLS in `tls_sw.c`, stream parsing in `tls_strp.c`, optional device TLS, and optional TOE support in `tls_toe.c`. It exposes `MODULE_ALIAS_TCP_ULP("tls")` and integrates with userspace through `SOL_TLS` socket options, cmsgs, netlink inet diagnostic attributes, and proc statistics.

## Risks and Edge Cases
The highest-risk areas are protocol pointer switching under lock/RCU rules, close-time ordering across software and hardware contexts, partial encrypted-record accounting, and rekey rules. `setsockopt` must reject mixed TLS versions/ciphers across directions and must not leave partially copied crypto material live on error. `tls_push_sg()` owns page references and memory charging while splicing pages into TCP; failures must preserve enough state to resume or free correctly. TLS 1.3 rekey is intentionally limited to same version/cipher and uses error counters on invalid attempts.

## Test Signals
Useful signals include kTLS selftests that attach `TCP_ULP=tls`, set TX/RX keys for each cipher, verify fallback from hardware to software, exercise TLS 1.3 rekey, cmsg record type changes, close with pending records, `TLS_TX_MAX_PAYLOAD_LEN`, `TLS_RX_EXPECT_NO_PAD`, inet diag ULP info, and `/proc/net/tls_stat` counter changes. Fault injection around crypto-info copy, device-offload failure, and low memory should leave no leaked keys, pages, or protocol overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_main.c -->

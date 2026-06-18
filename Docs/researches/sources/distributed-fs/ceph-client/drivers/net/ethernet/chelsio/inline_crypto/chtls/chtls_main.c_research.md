# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_main.c

## Purpose

`chtls_main.c` is the module and ULD integration layer for the Chelsio inline TLS TOE driver. It registers with `cxgb4`, registers a `tls_toe_device`, manages device lifetimes, dispatches RX CPLs to `chtls_handlers`, installs TLS-aware socket protocol operations, and handles SOL_TLS setsockopt/getsockopt for hardware keys.

## Important APIs, Types, and Functions

- Module lifecycle: `chtls_register()` and `chtls_unregister()`.
- ULD hooks: `chtls_uld_add()`, `chtls_uld_state_change()`, `chtls_uld_rx_handler()`, and `chtls_uld_info`.
- TLS TOE registration: `chtls_register_dev()`, `chtls_free_uld()`, `chtls_dev_release()`, and `chtls_free_all_uld()`.
- Listen integration: notifier registration, `listen_notify_handler()`, `chtls_start_listen()`, `chtls_stop_listen()`, and `listen_backlog_rcv()`.
- RX dispatch: `copy_gl_to_skb_pkt()`, `chtls_recv_packet()`, `chtls_recv_rsp()`, and `chtls_recv()`.
- Socket operations: `chtls_install_cpl_ops()` and `chtls_init_ulp_ops()`.
- TLS options: `chtls_setsockopt()`, `do_chtls_setsockopt()`, `chtls_getsockopt()`, and `do_chtls_getsockopt()`.

## Control Flow

On module init, the driver copies base TCP protocol structures, overrides close/disconnect/destroy/shutdown/send/receive/TLS option methods, initializes request-socket ops, registers a listen notifier, and registers `CXGB4_ULD_TLS`. When a Chelsio adapter adds the ULD, `chtls_uld_add()` allocates `chtls_dev`, copies LLDI, caches response SKBs, initializes IDR/listen/deferred-queue/key state, optionally initializes the key map, and adds it to the global list. On `CXGB4_STATE_UP`, the TLS TOE device is registered with the TLS core; on detach, it is removed and released through `kref`.

Listening sockets call the TLS TOE hash/unhash hooks. The main file validates TCP/non-loopback constraints, sets a backlog handler, and uses a raw notifier to call the connection-manager listener functions. Incoming adapter responses are converted to SKBs and dispatched to `chtls_handlers` by opcode. `CPL_RX_PKT` is specially synthesized into a PASS_ACCEPT-like SKB path; response-only CPLs use cached or newly allocated SKBs; packet-gl data uses `cxgb4_pktgl_to_skb()`.

For `SOL_TLS` setsockopt, the code validates TLS 1.2, accepts AES-GCM-128/256 crypto-info layouts, copies full crypto info from userspace into `csk->tlshws.crypto_info`, and calls `chtls_setkey()`. Getsockopt returns a minimal `tls_crypto_info` with TLS 1.2 version.

## State and Persistence Behavior

Global state includes `cdev_list`, `cdev_mutex`, `notify_mutex`, `listen_notify_list`, protocol templates, request-socket ops, and module parameter-like `send_page_order`. Per-device state includes cached SKBs, key map, deferred queue, LLDI copy, and TLS TOE refcount. All state is volatile kernel memory and released on detach/module unload.

## Dependencies and Integration Points

The file integrates with `cxgb4_register_uld()`, Linux TLS TOE registration, TCP protocol structs, raw notifier chains, Chelsio packet-gl conversion, Chelsio TID/CPL handlers, and userspace SOL_TLS APIs. It calls into `chtls_cm.c`, `chtls_io.c`, and `chtls_hw.c`.

## Risks and Edge Cases

- Device release resets adapter TLS stats and frees cached SKBs; detach ordering must avoid RX handlers accessing freed `cdev`.
- `chtls_uld_add()` has multi-stage allocation with partial cleanup; response SKB cache count must match the loop index on failure.
- `copy_gl_to_skb_pkt()` synthesizes PASS_ACCEPT request space around packet data, so header offsets must match hardware packet shift.
- `do_chtls_getsockopt()` ignores opt length validation and returns only base crypto info.
- Listen notification allocates `chtls_listen` and expects notifier handlers to free it.

## Test Signals

Validate module load/unload, ULD add/detach, TLS TOE device registration, listener hash/unhash, RX dispatch for response-only and packet-gl CPLs, SOL_TLS option validation for version/cipher/short buffers, IPv6 protocol replacement, and failure cleanup when key map or SKB cache allocation fails.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/crypto.h

## Purpose
This header declares the NFP network-driver crypto offload interface shared by TLS and IPsec code. It provides minimal cross-file types for per-connection TLS firmware handles and per-packet IPsec metadata, plus configuration-dependent stubs so the rest of the driver can call into crypto support without scattering preprocessor checks.

## Important APIs, types, and functions
- `struct nfp_net_tls_offload_ctx` stores the two-word firmware handle returned by the TLS firmware and, for TX only, the next TCP sequence. The zero-length `rx_end` marker documents the split between RX-sized driver state and TX-only fields.
- `nfp_net_tls_init()` enables/registers TLS device offload when `CONFIG_TLS_DEVICE` is built; the stub returns success when disabled.
- `nfp_net_tls_rx_resync_req()` handles firmware RX resync requests when TLS device offload exists; the stub returns `-EOPNOTSUPP`.
- `struct nfp_ipsec_offload` carries high/low packet sequence and offload handle for TX descriptors.
- `nfp_net_ipsec_init()`, `nfp_net_ipsec_clean()`, `nfp_net_ipsec_tx_prep()`, and `nfp_net_ipsec_rx()` are exported only when `CONFIG_NFP_NET_IPSEC` is enabled.

## Control flow
The file has no runtime control flow beyond inline stubs. It shapes compile-time routing: callers can invoke TLS/IPsec init and packet helpers from common paths, while the compiler either links real implementations from `tls.c`/`ipsec.c` or substitutes no-op/unsupported behavior.

## State and persistence
The TLS context embeds firmware handle state in the kernel TLS driver context associated with a socket. The IPsec offload struct is transient per-packet/descriptor metadata. No persistent storage is managed here.

## Dependencies and integration points
This header is included by crypto implementation files and by NFP netdev data paths that need to initialize crypto offloads or attach crypto metadata to packets. It forward-declares `struct nfp_net`, `struct net_device`, and `struct nfp_net_tls_resync_req` to avoid dragging firmware-layout headers into every consumer.

## Risks
The layout of `struct nfp_net_tls_offload_ctx` is ABI-sensitive against `TLS_DRIVER_STATE_SIZE_TX/RX` checks in `tls.c`. Any new RX fields before `rx_end` could exceed kernel TLS RX driver state. Stub behavior must stay compatible with callers that treat init as optional but data-path helpers as feature-gated.

## Test signals
Build coverage should include TLS enabled/disabled and IPsec enabled/disabled configurations. Runtime signals are TLS offload setup reaching `nfp_net_tls_init()`, RX resync requests returning supported/unsupported as expected, and IPsec init attaching `xfrmdev_ops` only when hardware capability and build config allow it.

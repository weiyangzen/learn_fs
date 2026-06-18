# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ktls.h

## Purpose
Defines the compile-time interface between funeth core/Tx code and optional kTLS transmit offload support.

## APIs and Types
Declares `struct fun_ktls_tx_ctx` with a big-endian hardware `tlsid` and host-order `next_seq`. When `CONFIG_TLS_DEVICE` is enabled, declares `fun_ktls_init()` and `fun_ktls_cleanup()`. Otherwise it supplies inline no-op stubs so the rest of the driver can call cleanup/init unconditionally.

## Control Flow and Integration
`funeth_main.c` initializes and cleans kTLS through this header; `funeth_tx.c` reads `struct fun_ktls_tx_ctx` via TLS core helpers when `tls_is_skb_tx_device_offloaded()` is true. The conditional stubs preserve build compatibility on kernels/configurations without TLS device offload.

## State and Persistence
The header defines per-TLS-socket offload state but does not allocate it. TLS core owns the memory for the driver context; funeth stores hardware ids and sequence cursor there.

## Dependencies and Risks
Depends on `<net/tls.h>` and the netdev type declarations available through kernel headers. The main risk is ABI mismatch between `TLS_DRIVER_STATE_SIZE_TX` expected by TLS core and the size required for `fun_ktls_tx_ctx`; the implementation must ensure the netdev advertises a compatible context size through TLS infrastructure. Test signals are successful builds with `CONFIG_TLS_DEVICE=y/m` and disabled, and runtime TLS offload add/remove paths.

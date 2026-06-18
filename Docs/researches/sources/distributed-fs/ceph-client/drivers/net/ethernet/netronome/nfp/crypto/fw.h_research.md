# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/fw.h

## Purpose
This header defines the firmware ABI structures and constants used for NFP TLS crypto CCM messages. It describes request/reply packet layouts for reset, add, delete, update, and RX resync operations and the opcode values for TLS 1.2 AES-GCM-128 encrypt/decrypt.

## Important APIs, types, and functions
- `NFP_NET_CRYPTO_OP_TLS_1_2_AES_GCM_128_ENC/DEC` identify firmware crypto operation bits.
- `struct nfp_net_tls_resync_req` is sent from firmware to host and carries a TLS handle, TCP sequence, and packet L3/L4 offsets.
- `struct nfp_crypto_reply_simple` and `struct nfp_crypto_reply_add` are CCM replies with firmware error and, for add, a two-word handle.
- `struct nfp_crypto_req_add_front`, `_back`, `_v4`, and `_v6` define the variable add request. The `struct_group_tagged` and `static_assert` protect the variable-address layout.
- `struct nfp_crypto_req_del`, `struct nfp_crypto_req_update`, and `struct nfp_crypto_req_reset` define delete/update/reset requests.

## Control flow
There is no executable control flow. The structures are filled by `tls.c`, passed through the CCM mailbox transport, and interpreted by firmware. The front/back split lets the same add code support IPv4 and IPv6 by changing the address span between fixed header and crypto material.

## State and persistence
State represented here is firmware session state: add requests create firmware handles, update requests advance record/TCP sequence, delete requests invalidate handles, and reset clears endpoint state. The header itself stores nothing.

## Dependencies and integration points
The header depends on `../ccm.h` for `struct nfp_ccm_hdr`. It is tightly coupled to `crypto/tls.c` and to firmware TLV/CCM ABI expectations, including byte order, packed VLAN/IP version field masks, key material sizes, and operation bits exported in `nn->tlv_caps.crypto_ops`.

## Risks
The request structures carry key material and are ABI-sensitive. Field order, padding, and endian conversions must remain exactly compatible with firmware. The `struct_group_tagged` comment is important: adding fields outside the grouped front header would silently corrupt variable-length address handling. Key zeroization in `tls.c` depends on these layout boundaries.

## Test signals
Compile-time layout assertions are the first signal. Runtime validation includes successful TLS reset/add/update/delete CCM transactions for IPv4 and IPv6 sockets, correct rejection when firmware returns nonzero error, and RX resync requests being parsed from `struct nfp_net_tls_resync_req` offsets.

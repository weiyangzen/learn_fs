<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/nfd3.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/nfd3.h

## Purpose
`nfd3.h` defines the NFD3 host TX descriptor layout, software TX buffer descriptor, descriptor flag constants, and public function prototypes used by the NFD3 datapath implementation.

## Important APIs, Types, And Functions
`struct nfp_nfd3_tx_desc` is the packed 16-byte hardware TX descriptor with DMA address, length, packet offset/EOP, MSS, LSO header length, flags, L3/L4 offsets or VLAN tag, and total data length. `struct nfp_nfd3_tx_buf` tracks the software owner for a descriptor: skb, page fragment, or AF_XDP buffer; DMA address; fragment index or XSK reuse state; packet count; and real byte length. The header declares NFD3 TX/RX, NAPI, control, freelist, AF_XDP, metadata parse, and optional IPsec helpers.

## Control Flow
No runtime control flow exists except the `CONFIG_NFP_NET_IPSEC` conditional: without IPsec support `nfp_nfd3_ipsec_tx()` is an inline no-op; with support it is implemented in `ipsec.c`.

## State And Persistence
The structures define per-descriptor transient ring state. Their fields are persisted only while descriptors are owned by the driver or hardware and are reset by ring cleanup paths.

## Dependencies And Integration Points
The header is included by `dp.c`, `rings.c`, `xsk.c`, and `ipsec.c`. It depends on NFP net datapath types declared elsewhere and on Linux bit macros for descriptor flags.

## Risks
Descriptor field packing is ABI with firmware; any layout or endian change breaks TX. `offset_eop` combines packet offset with EOP in one byte, so metadata prepend size must fit the mask. The union in `nfp_nfd3_tx_buf` is context-sensitive and relies on ring type and `is_xsk_tx`/`fidx` discipline.

## Test Signals
Compile coverage with and without `CONFIG_NFP_NET_IPSEC`, descriptor dump validation through `rings.c`, TX path tests for checksum/TSO/VLAN/IPsec flags, and AF_XDP completion tests that distinguish XSK TX completions from RX-buffer XDP_TX reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/nfd3.h -->

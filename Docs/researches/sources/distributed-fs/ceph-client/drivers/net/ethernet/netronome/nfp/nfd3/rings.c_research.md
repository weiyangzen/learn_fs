<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/rings.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/rings.c

## Purpose
`rings.c` allocates, frees, resets, and debugs NFD3 TX rings, including special handling for XDP/AF_XDP rings, and publishes the NFD3 datapath operations table.

## Important APIs, Types, And Functions
Important functions are `nfp_nfd3_tx_ring_alloc()`, `nfp_nfd3_tx_ring_free()`, `nfp_nfd3_tx_ring_reset()`, `nfp_nfd3_tx_ring_bufs_alloc()`, `nfp_nfd3_tx_ring_bufs_free()`, `nfp_nfd3_print_tx_descs()`, and the `const struct nfp_dp_ops nfp_nfd3_ops` table. `NFP_NFD3_CFG_CTRL_SUPPORTED` lists firmware control bits supported by this datapath version.

## Control Flow
Allocation sets the descriptor count from `dp->txd_cnt`, allocates coherent descriptor memory, allocates zeroed software txbufs, and configures XPS for normal netdev TX queues. Reset walks outstanding normal TX descriptors, unmaps head/fragments, frees SKBs at the last fragment, and resets pointers. For XDP rings, reset delegates to AF_XDP buffer completion/free handling. XDP ring buffer allocation preallocates page-backed RX-style buffers for XDP_TX reuse and unwinds on failure. Debug printing dumps all descriptor words, associated skb/xdp pointers, DMA address, and host/device read/write markers.

## State And Persistence
The file owns ring memory lifetimes and pointer reset state. `txds` are coherent DMA memory, `txbufs` are kernel memory, XDP ring buffers are DMA-mapped pages, and `nfp_nfd3_ops` is static driver configuration. State persists for the netdev datapath lifetime, not across reload.

## Dependencies And Integration Points
It depends on `nfd3.h`, NFP net datapath ring structs, DMA allocation APIs, AF_XDP helpers, seq_file debug output, netdev XPS, and the core NFP datapath registration that selects `nfp_nfd3_ops`.

## Risks
Reset assumes non-XDP descriptors with non-null SKBs while `rd_p != wr_p`; corrupted or partially initialized rings can fault. `nfp_nfd3_tx_ring_bufs_free()` returns on the first empty XDP buffer, so partial allocation order must remain strictly sequential. The ops `cap_mask` advertises many offloads; unsupported firmware/hardware combinations must be filtered elsewhere.

## Test Signals
Test ring allocation failure injection, reset idempotence with empty/full/gather rings, XDP ring buffer partial allocation unwind, AF_XDP completion cleanup, descriptor debug output, XPS assignment, and datapath capability negotiation using `nfp_nfd3_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/rings.c -->

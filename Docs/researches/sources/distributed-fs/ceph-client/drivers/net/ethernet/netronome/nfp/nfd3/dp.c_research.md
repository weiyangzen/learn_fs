<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/dp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/dp.c

## Purpose
`dp.c` implements the NFD3 datapath for normal packet TX/RX, XDP TX from RX buffers, metadata parsing, checksum/TSO/VLAN/TLS/IPsec metadata handling, NAPI polling, and control vNIC TX/RX.

## Important APIs, Types, And Functions
The key public functions are `nfp_nfd3_tx()`, `nfp_nfd3_tx_complete()`, `nfp_nfd3_rx_ring_fill_freelist()`, `nfp_nfd3_rx_csum()`, `nfp_nfd3_parse_meta()`, `nfp_nfd3_poll()`, `nfp_nfd3_ctrl_tx_one()`, and `nfp_nfd3_ctrl_poll()`. Important internal helpers include TX queue stop/wake predicates, `nfp_nfd3_tx_tso()`, `nfp_nfd3_tx_csum()`, `nfp_nfd3_prep_tx_meta()`, RX buffer allocation/give/drop, `nfp_nfd3_tx_xdp_buf()`, normal RX, XDP completion, and control RX validation.

## Control Flow
TX checks ring space, handles TLS transmit preparation, prepends metadata for port mux/TLS/VLAN/IPsec, DMA maps the head and fragments, fills NFD3 descriptors, sets TSO/checksum/IPsec/VLAN flags, advances ring pointers, stops the netdev queue if needed, and flushes write pointers according to xmit-more. TX completion reads the hardware completion pointer, unmaps head/fragments, consumes SKBs on the last descriptor, updates stats, completes netdev queue bytes, and wakes queues with memory-barrier protection.

RX polls descriptors until budget or no DD bit. It computes metadata and packet offsets, syncs DMA to CPU, parses descriptor or chained metadata, runs XDP when allowed, handles control-port packets, maps representor port IDs, builds SKBs, allocates replacement buffers before giving the old buffer to the stack, applies checksum/VLAN/TLS/IPsec metadata, and delivers via GRO or egress redirect. `nfp_nfd3_poll()` combines TX completion, RX, NAPI completion/IRQ unmask, and adaptive moderation samples.

Control path TX queues SKBs when full, optionally prepends control metadata, maps one descriptor, and flushes immediately. Control poll drains TX completions and queued control TX under a spinlock, then processes control RX up to a fixed budget and reschedules on overflow.

## State And Persistence
State is ring-resident: software TX/RX buffers, DMA addresses, descriptor rings, `wr_p`, `rd_p`, `qcp_rd_p`, `wr_ptr_add`, queue stats, and NAPI/tasklet state. Metadata is transient per packet. No disk persistence exists; hardware state is synchronized through queue controller pointers and DMA-visible descriptors.

## Dependencies And Integration Points
The file depends on NFP net datapath structs, NFP app control RX, representor lookup/stats, XDP/BPF APIs, TLS device offload, IPsec offload, DMA mapping APIs, netdev queue APIs, NAPI/GRO, DIM adaptive coalescing, and AF_XDP helpers for XSK-enabled RX rings.

## Risks
Descriptor ownership depends on memory barriers and pointer arithmetic; off-by-one errors can corrupt rings. TX error unwind must unmap exactly the descriptors already mapped. Metadata prepend changes skb offsets and must remain consistent with TSO/checksum offsets. RX allocates replacement buffers after building the skb; failures must preserve or correctly free the original page. Control RX metadata validation differs depending on app metadata support. XDP and representor/control-port paths bypass parts of normal RX and need dedicated coverage.

## Test Signals
Exercise TX with linear, fragmented, TSO, encapsulated checksum, VLAN v1/v2 metadata, TLS, and IPsec packets; TX_BUSY and queue wake paths; RX with descriptor RSS and chained metadata, control port packets, representor redirects, XDP PASS/TX/DROP/ABORTED, replacement-buffer allocation failure, checksum/VLAN/TLS/IPsec metadata, and NAPI completion/IRQ unmask behavior. Ring corruption warnings and DMA debug are strong regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/dp.c -->

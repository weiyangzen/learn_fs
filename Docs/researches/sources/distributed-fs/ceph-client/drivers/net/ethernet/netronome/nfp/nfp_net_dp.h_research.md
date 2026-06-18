# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_dp.h

## Purpose

`nfp_net_dp.h` is the shared datapath interface for NFP netdev implementations. It defines DMA helper inlines, ring-space helpers, interrupt unmasking, the `struct nfp_dp_ops` abstraction, wrappers around datapath-specific operations, and exported common datapath entry points.

## Important APIs, Types, and Functions

Important inlines are `nfp_net_dma_map_rx()`, `nfp_net_dma_sync_dev_rx()`, `nfp_net_dma_unmap_rx()`, `nfp_net_dma_sync_cpu_rx()`, `nfp_net_tx_full()`, `nfp_net_tx_xmit_more_flush()`, `nfp_net_read_tx_cmpl()`, `nfp_net_free_frag()`, and `nfp_net_irq_unmask()`. `enum nfp_nfd_version` identifies NFD3 versus NFDK. `struct nfp_dp_ops` provides poll, xsk_poll, ctrl_poll, normal xmit, control TX, freelist fill, TX ring allocation/reset/free, TX buffer allocation/free, and descriptor debug printing hooks. Extern ops are `nfp_nfd3_ops` and `nfp_nfdk_ops`.

## Control Flow

Most runtime control flow is indirect. Core code calls wrapper functions in this header, which dispatch through `dp->ops` to the selected datapath implementation. Common code uses the DMA helpers when allocating/freeing RX buffers and uses queue-controller helpers for TX completion and write-pointer updates. Interrupt handlers clear CFG BAR ICR entries through `nfp_net_irq_unmask()` when firmware auto-masking is not used.

## State and Persistence Behavior

The header itself owns no storage, but its helpers mutate DMA mappings, queue-controller write pointers, TX pending-add counters, and CFG BAR interrupt-cause bytes. The ops table establishes persistent behavior selection for the life of a datapath instance and constrains capabilities through `cap_mask`, `dma_mask`, and minimum descriptors per packet.

## Dependencies and Integration Points

It includes `nfp_net.h` and relies on Linux DMA APIs, NFP queue-controller helpers, `struct napi_struct`, tasklets, seq_file, netdev TX APIs, and descriptor/ring structures declared in the main NFP headers. It is consumed by datapath C files, debugfs, XSK support, and netdev TX dispatch.

## Risks and Edge Cases

DMA helper lengths subtract `NFP_NET_RX_BUF_NON_DATA` and add/subtract headroom, so buffer sizing must remain consistent with allocation and firmware RX offset. `nfp_net_tx_full()` uses host pointer copies and may be conservative until completions are refreshed. `nfp_net_tx_xmit_more_flush()` relies on a write memory barrier before queue-controller pointer update. Ops table omissions or mismatched capability masks can break NFD3/NFDK feature gating.

## Test Signals

Compile both NFD3 and NFDK paths, exercise TX batching with `xmit_more`, RX DMA sync/unmap under XDP and non-XDP, interrupt auto-mask/unmask modes, debugfs descriptor printing, control TX, and datapath selection for PF and VF devices.

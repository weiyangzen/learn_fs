# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_main.c

## Purpose
`fm10k_main.c` is the central datapath and queueing implementation for the Intel FM10K Ethernet switch host interface driver. It registers the module-wide workqueue and PCI driver, implements NAPI polling, Rx buffer recycling, Tx descriptor construction, checksum/TSO/tunnel offload preparation, interrupt moderation, and queue-vector allocation. It is the bridge between Linux networking packet objects (`sk_buff`, NAPI, netdev queues) and FM10K descriptor rings.

## Important APIs, types, and functions
The module lifecycle is handled by `fm10k_init_module()` and `fm10k_exit_module()`, which allocate/destroy `fm10k_workqueue`, initialize debug support, and register/unregister the PCI driver through `fm10k_register_pci_driver()` and `fm10k_unregister_pci_driver()`.

The Rx path is built around `fm10k_alloc_rx_buffers()`, `fm10k_fetch_rx_buffer()`, `fm10k_add_rx_frag()`, `fm10k_process_skb_fields()`, `fm10k_cleanup_headers()`, and `fm10k_clean_rx_irq()`. These functions manage page-backed buffers, DMA sync/unmap operations, descriptor status bits, checksum/hash metadata, VLAN tag reconstruction, GLORT/macvlan selection, GRO delivery, and per-ring statistics.

The Tx path uses `fm10k_xmit_frame_ring()`, `fm10k_tso()`, `fm10k_tx_csum()`, `fm10k_tx_encap_offload()`, `fm10k_tx_map()`, `fm10k_maybe_stop_tx()`, and `fm10k_clean_tx_irq()`. These functions validate offload eligibility, populate the first descriptor with header/MSS state, map skb head and fragments to DMA descriptors, handle BQL, stop/wake netdev subqueues, reclaim completed descriptors, and detect repeated Tx hangs.

Queueing and interrupt support is implemented by `fm10k_poll()`, `fm10k_update_itr()`, `fm10k_qv_enable()`, `fm10k_set_num_queues()`, `fm10k_alloc_q_vector()`, `fm10k_alloc_q_vectors()`, `fm10k_init_msix_capability()`, `fm10k_assign_rings()`, `fm10k_init_reta()`, `fm10k_init_queueing_scheme()`, and `fm10k_clear_queueing_scheme()`. The key local structures are `struct fm10k_ring`, `struct fm10k_q_vector`, `struct fm10k_ring_container`, `struct fm10k_rx_buffer`, and `struct fm10k_tx_buffer`, all declared in shared driver headers.

## Control flow
On module load, the file creates a per-CPU workqueue, initializes debugfs support, and registers the PCI driver. Runtime packet flow enters through netdev code in `fm10k_netdev.c`, then reaches `fm10k_xmit_frame_ring()` for Tx and `fm10k_poll()` for NAPI Rx/Tx cleanup.

Rx control flow starts when an interrupt schedules NAPI. `fm10k_poll()` first reclaims Tx completions for all Tx rings in the q_vector, then splits the NAPI budget across Rx rings. `fm10k_clean_rx_irq()` replenishes descriptors in batches, checks descriptor writeback status, synchronizes DMA data for CPU access, constructs or extends an skb, handles multi-buffer frames until EOP, drops malformed/error descriptors, fills hash/checksum/VLAN/GLORT metadata, and submits the skb via `napi_gro_receive()`. Incomplete frames remain in `rx_ring->skb` for the next poll.

Tx control flow starts with descriptor counting and queue-space checks. `fm10k_xmit_frame_ring()` records the first Tx buffer, applies TSO if possible, otherwise applies checksum offload or software checksum fallback, and delegates DMA mapping to `fm10k_tx_map()`. `fm10k_tx_map()` writes one or more descriptors, adds RS/INT flags at writeback FIFO boundaries, marks the last descriptor, updates BQL, publishes `next_to_watch` after a write barrier, advances `next_to_use`, and rings the hardware tail when needed. `fm10k_clean_tx_irq()` later observes the EOP descriptor DONE bit, consumes the skb, unmaps all DMA segments, updates statistics, wakes queues when enough descriptors are free, and schedules reset on confirmed hangs.

Queue setup first derives RSS/QoS queue counts, requests MSI-X vectors, allocates q_vectors with embedded ring arrays, maps logical rings to hardware register indexes, and initializes the RETA table. Teardown reverses q_vector and MSI-X allocation.

## State and persistence behavior
The file maintains volatile driver state only; there is no on-disk persistence. Ring progress is tracked by `next_to_use`, `next_to_clean`, `next_to_alloc`, `next_to_watch`, and hardware tail/head registers. Rx page lifetime is tracked in `rx_buffer->page`, `dma`, and `page_offset`; reusable pages are refcounted and synchronized back for DMA. Tx state is tracked through `tx_buffer` DMA lengths, skb pointers, GSO segment counts, and BQL counters.

Persistent across resets only in the driver instance are configuration fields stored on `struct fm10k_intfc`, including queue feature limits, ITR defaults, RETA/RSS key values, and statistics accumulators. Hardware-visible state is pushed through MMIO descriptor registers and queue tail writes; these must be reconstructed after reset by PCI/netdev code.

## Dependencies and integration points
This file depends on Linux networking (`sk_buff`, NAPI, GRO, VLAN, checksum, TSO/GSO, RSS hash APIs), DMA mapping APIs, MSI-X setup through PCI helpers, memory barriers, page recycling helpers, and driver-local macros from `fm10k.h`. It calls into `fm10k_netdev.c` for resource cleanup helpers, into `fm10k_pci.c` for register reads and PCI driver registration, and into debug helpers (`fm10k_dbg_*`). It relies on hardware register and descriptor definitions shared across the fm10k driver.

Integration with macvlan/L2 acceleration occurs on Rx by mapping descriptor DGLORT values to accelerated macvlan devices via RCU-protected `ring->l2_accel`. Tunnel offload integration recognizes VXLAN and NVGRE encapsulation for PF devices and enforces the FM10K tunnel header length limit.

## Risks and edge cases
The most sensitive areas are DMA ordering and ring index consistency. `wmb()`, `dma_rmb()`, `smp_rmb()`, and `smp_mb()` are required to avoid publishing descriptors or consuming writebacks out of order. Rx page reuse must not recycle non-reusable, remote, pfmemalloc, or externally referenced pages. Tx DMA error handling walks backward through partially mapped descriptors; mistakes there would leak DMA mappings or free the wrong skb.

Offload eligibility is narrow: tunnel TSO/checksum only supports specific VXLAN/NVGRE inner protocols and header sizes, and unsupported tunnel TSO disables `NETIF_F_GSO_UDP_TUNNEL`. Queue stopping/waking depends on descriptor accounting and can cause stalls if the threshold logic diverges from hardware progress. Tx hang detection deliberately requires two checks to avoid false positives, but reset scheduling still depends on service work progress.

## Test signals
Useful validation signals include successful module load/unload, PCI probe creating q_vectors and MSI-X entries, `ip link set up/down` without resource leaks, NAPI packet receive with GRO delivery, Tx under fragmented and GSO skb workloads, VLAN tag insertion/stripping behavior, VXLAN/NVGRE offload fallback, queue wake after descriptor pressure, and reset on forced Tx hang. Runtime counters to watch include `alloc_failed`, checksum good/error counts, Rx descriptor error buckets, `restart_queue`, `tx_busy`, per-ring packet/byte counters, and dev logs for DMA map failures or Tx unit hangs.

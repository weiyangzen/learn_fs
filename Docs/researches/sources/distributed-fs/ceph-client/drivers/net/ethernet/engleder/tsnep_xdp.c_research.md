## sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_xdp.c

## Purpose
Provides the TSNEP netdev BPF/XDP setup helpers for installing an XDP program and binding/unbinding AF_XDP zero-copy pools to queue pairs.

## Important APIs, Types, and Functions
Exports `tsnep_xdp_setup_prog` and `tsnep_xdp_setup_pool`. Internal helpers `tsnep_xdp_enable_pool` and `tsnep_xdp_disable_pool` validate queue IDs, require paired TX/RX queues, map/unmap XSK pools for DMA, and delegate runtime queue conversion to `tsnep_enable_xsk`/`tsnep_disable_xsk` in `tsnep_main.c`.

## Control Flow and State
Program setup atomically swaps `adapter->xdp_prog` with `xchg` and drops the old BPF reference. Pool setup enables when a pool pointer is present and disables otherwise. Enable validates that the RX and TX queue indices match the requested queue, DMA maps the pool with `DMA_ATTR_SKIP_CPU_SYNC`, sets RX queue info through `tsnep_enable_xsk`, and unwinds DMA mapping on failure. Disable looks up the pool by queue id, disables XSK mode in the main driver, and DMA unmaps the pool.

## Dependencies and Integration Points
Depends on BPF program lifetime rules, AF_XDP pool APIs, DMA mapping, queue topology from `tsnep_main.c`, and netdev `ndo_bpf` dispatch. Actual XDP action execution and XSK RX/TX are implemented in `tsnep_main.c`.

## Risks and Test Signals
Risks include no explicit feature rejection for programs needing unsupported metadata, races around program replacement while RX is polling, queue-pair assumptions for future asymmetric queue layouts, and ensuring pool DMA unmap always follows successful map. Test with XDP attach/detach loops, replacing programs under traffic, invalid queue ids, AF_XDP zero-copy bind/unbind, queue-pair mismatch simulation, and packet paths for XDP_PASS/DROP/TX/REDIRECT.

# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/vmxnet3_drv.c

## Purpose
`vmxnet3_drv.c` is the main Linux PCI/netdev driver for VMware's vmxnet3 virtual Ethernet NIC. It owns PCI probing/removal, BAR register access, device revision negotiation, DMA-backed queue/shared-memory allocation, interrupt setup, NAPI polling, TX/RX datapaths, link/event handling, reset/quiesce, MTU changes, VLAN and multicast filters, suspend/resume, and module registration.

## Important APIs, Types, And Functions
- Exposes `vmxnet3_driver_name`, `vmxnet3_check_ptcapability()`, `vmxnet3_activate_dev()`, `vmxnet3_quiesce_dev()`, `vmxnet3_reset_dev()`, `vmxnet3_force_close()`, `vmxnet3_tq_destroy_all()`, `vmxnet3_rq_destroy_all()`, `vmxnet3_rq_create_all()`, `vmxnet3_adjust_rx_ring_size()`, and `vmxnet3_create_queues()` to sibling vmxnet3 files through `vmxnet3_int.h`.
- Registers `struct pci_driver vmxnet3_driver` with `probe`, `remove`, `shutdown`, and PM callbacks. `vmxnet3_probe_device()` installs `net_device_ops` including open/stop, TX, MAC/MTU changes, feature negotiation hooks, stats, timeout, RX mode, VLAN filter updates, netpoll, BPF setup, and XDP transmit.
- TX core: `vmxnet3_tq_xmit()`, `vmxnet3_map_pkt()`, `vmxnet3_parse_hdr()`, `vmxnet3_copy_hdr()`, `vmxnet3_tq_tx_complete()`, `vmxnet3_unmap_pkt()`, `vmxnet3_tq_cleanup()`, `vmxnet3_tq_create()`, `vmxnet3_tq_destroy()`.
- RX core: `vmxnet3_rq_alloc_rx_buf()`, `vmxnet3_rq_rx_complete()`, `vmxnet3_rx_csum()`, `vmxnet3_rx_error()`, `vmxnet3_rq_init()`, `vmxnet3_rq_create()`, `vmxnet3_rq_cleanup()`, `vmxnet3_rq_destroy()`, `vmxnet3_create_pp()`, `vmxnet3_pp_get_buff()`.
- Interrupt/NAPI: `vmxnet3_intr()` for INTx/MSI, `vmxnet3_msix_tx()`, `vmxnet3_msix_rx()`, `vmxnet3_msix_event()`, `vmxnet3_poll()`, `vmxnet3_poll_rx_only()`, `vmxnet3_request_irqs()`, `vmxnet3_free_irqs()`.

## Control Flow
Probe allocates and registers a multiqueue Ethernet netdev after DMA, BAR, revision, capability, queue-count, shared-memory, interrupt, feature, NAPI, and MAC setup. `ndo_open` queries descriptor sizes, creates queues, and activates the device by initializing rings, filling RX buffers, requesting IRQs, publishing the shared block to BAR1, issuing `VMXNET3_CMD_ACTIVATE_DEV`, posting producer indices, applying filters, enabling NAPI/interrupts, and checking link.

TX maps SKBs into hardware descriptors, handles TSO/checksum/tunnel/VLAN/timestamp metadata, flips generation bits after `dma_wmb()`, and rings the producer threshold. Completion unmaps descriptors, frees SKBs or returns XDP frames, advances completion indices, and wakes stopped queues. RX NAPI consumes completion descriptors, validates ring IDs, runs XDP when eligible, handles SKB/page refills, checksum/LRO/VLAN/RSS metadata, GRO delivery, out-of-order refilling, producer updates, and redirect flushes. Reset, MTU, ring-size, close, suspend, and resume paths all revolve around quiesce/reset/recreate/activate sequencing guarded by adapter state bits.

## State And Persistence
Runtime state is centered in `struct vmxnet3_adapter`: queues, active VLAN bitmap, interrupt metadata, command lock, coherent shared areas, netdev/pci pointers, BAR mappings, revision/capability fields, queue counts/sizes, RSS/coalescing settings, reset/quiesce bits, XDP program pointer, latency config, and disabled offload mask. Per-queue state tracks ring indices/generation bits, DMA addresses, buffer ownership, driver stats, NAPI objects, page pools, and interrupt indices.

## Dependencies And Integration Points
Depends on Linux PCI, DMA mapping, netdevice, NAPI, XDP/page_pool, VLAN, GRO/LRO/GSO, RSS, MSI/MSI-X, netpoll, workqueues, PM, and VMware vmxnet3 ABI definitions. Integrates with `vmxnet3_ethtool.c` for stats/features/control and `vmxnet3_xdp.c` for BPF/XDP.

## Risks
Risks include descriptor lifetime bugs, generation-bit ordering mistakes, DMA leaks on partial TX mapping failure, out-of-order RX refill corner cases, reset races around NAPI/IRQ teardown, revision-specific feature mismatches, XDP/page_pool ownership mistakes, and shared-memory ABI drift. Many invariants use `BUG_ON()`, so corrupted hardware-facing state can become fatal.

## Test Signals
Module load/probe/remove across revisions, open/close, MSI-X/MSI/INTx fallback, multiqueue RSS, TX checksum/TSO/tunnel traffic, RX checksum/LRO/GRO/VLAN/RSS, XDP pass/drop/tx/redirect and `ndo_xdp_xmit`, ring/MTU changes, multicast/VLAN filters, netpoll, suspend/resume with WOL, forced TX timeout/reset, DMA fault injection, and ethtool controls.

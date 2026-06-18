# sources/distributed-fs/ceph-client/drivers/soc/ti/k3-ringacc.c

## Purpose
This file implements the TI K3 NAVSS Ring Accelerator driver. It provides a shared ring abstraction for K3 DMA, message, and proxy ring users, plus a separate initializer for UDMA-style DMA rings embedded in DMA controllers. The driver owns ring allocation, hardware/TI-SCI programming, coherent ring memory, proxy thread allocation, MSI IRQ mapping for ring events, and push/pop operations over memory, FIFO MMIO, or proxy datapaths.

## Important APIs, Types, And Functions
Core types are `struct k3_ringacc`, `struct k3_ring`, `struct k3_ring_state`, register layout structs, `struct k3_ring_ops`, and SoC match data. Exported APIs include `k3_ringacc_request_ring`, `k3_ringacc_request_rings_pair`, `k3_ringacc_ring_cfg`, `k3_ringacc_ring_free`, `k3_ringacc_ring_reset`, `k3_ringacc_ring_reset_dma`, `k3_ringacc_ring_push`, `k3_ringacc_ring_push_head`, `k3_ringacc_ring_pop`, `k3_ringacc_ring_pop_tail`, `k3_ringacc_get_ring_id`, `k3_ringacc_get_tisci_dev_id`, `k3_ringacc_get_ring_irq_num`, `of_k3_ringacc_get_by_phandle`, and `k3_ringacc_dmarings_init`. Internal operation tables select memory-ring, message-FIFO, proxy, forward-DMA, and reverse-DMA behavior.

## Control Flow
`k3_ringacc_probe` allocates the accelerator, runs SoC init, then publishes it on `k3_ringacc_list` for phandle lookup. `k3_ringacc_init` resolves MSI domain, TI-SCI handle/resource ranges, MMIO resources, proxy counts, ring arrays, and per-ring register windows. Clients request a ring, configure size/mode/element size, and then call push/pop helpers. Configuration allocates coherent memory and sends `ti_sci_rm_ringacc_ops->set_cfg`. Runtime access dispatches through `ring->ops`; pop paths refresh hardware occupancy when local state is empty. Freeing tears down TI-SCI configuration, coherent memory, proxy allocation, flags, and module refs.

## State And Persistence
Runtime state is in memory only: global accelerator list, bitmaps for ring/proxy usage, per-ring use counts, flags, cached occupancy/free counts, ring memory pointers, and indices. Hardware-visible state persists in ring accelerator registers, doorbells, and TI-SCI-managed ring configuration until reset/free. DMA ring reset includes an AM65x SR1.0 quirk that doorbells through the 21-bit occupancy wrap condition before reset.

## Dependencies And Integration Points
The driver depends on device tree properties `ti,num-rings`, `ti,sci`, `ti,sci-dev-id`, and TI-SCI GP ring resources, plus named resources `rt`, `fifos`, `proxy_gcfg`, and `proxy_target`. It integrates with TI-SCI INTA MSI domains, `soc_device_match` revision data, coherent DMA APIs, CPPI5 teardown markers, and K3 UDMA/BCDMA/PKTDMA clients.

## Risks And Test Signals
Key risks are occupancy-cache drift, proxy mode errors, missing MSI domain causing probe deferral, TI-SCI resource mismatches, DMA coherent allocation failures, shared ring misuse, and reset quirks that can hang if doorbell semantics change. Test signals include probe logs with ring/proxy counts, successful TI-SCI set_cfg calls, IRQ lookup via `msi_get_virq`, push/pop behavior for each access mode, DMA teardown marker handling, and stress tests for request/free/shared/proxy paths.

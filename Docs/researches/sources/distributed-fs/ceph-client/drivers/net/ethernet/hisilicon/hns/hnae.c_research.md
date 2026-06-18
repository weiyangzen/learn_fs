# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hnae.c

## Purpose
`hnae.c` implements the Hisilicon Network Acceleration Engine framework core. It provides a class device registry for AE providers, maps firmware nodes to registered AE devices, allocates/free rings and descriptors for consumers, owns the notifier chain for AE registration, and exports the handle lifecycle used by upper network drivers.

## Important APIs and Functions
The exported entry points are `hnae_get_handle`, `hnae_put_handle`, `hnae_ae_register`, `hnae_ae_unregister`, `hnae_register_notifier`, `hnae_unregister_notifier`, and `hnae_reinit_handle`. `hnae_get_handle` finds an AE by fwnode, calls the provider `get_handle`, installs default or caller-supplied buffer ops, initializes every queue, pins the provider module, and adds the handle to the AE handle list. `hnae_put_handle` reverses that setup, including queue teardown, provider reset/put, module put, and class-device ref release. Internally, `hnae_init_ring`, `hnae_alloc_desc`, and `hnae_alloc_buffers` construct descriptor state; `hnae_fini_ring` and `hnae_free_buffers` tear it down.

## Control Flow
AE providers register through `hnae_ae_register`, which validates mandatory ops, creates a `hnae` class child device, initializes the handle list lock, and notifies listeners with `HNAE_AE_REGISTER`. Consumers later call `hnae_get_handle`, which uses `class_find_device` and `__ae_match` against OF or ACPI fwnodes, asks the AE for a handle, initializes TX and RX rings for all queues, and then exposes the fully initialized handle. Reinitialization first frees queues, invokes the provider reset callback, then rebuilds each queue.

## State and Persistence
Persistent state is in memory only: class devices, AE handle lists protected by spinlock/RCU list helpers, per-ring descriptor arrays, descriptor control blocks, DMA mappings, and allocated RX pages. No disk persistence exists. RX rings receive page buffers during initialization; TX rings allocate descriptor memory but not packet buffers until upper layers submit packets.

## Dependencies and Integration Points
This file depends on Linux class devices, DMA mapping APIs, notifier chains, module refcounting, RCU list operations, firmware-node APIs, and `sk_buff`/page allocation helpers. It integrates with provider-specific `struct hnae_ae_ops` implementations, notably the DSAF adapter in `hns_ae_adapt.c`.

## Risks
DMA direction is inferred from ring flags, so wrong flags can map descriptors or buffers with the wrong direction. `hnae_free_desc` unmaps descriptor memory with `ring_to_dma_dir`, matching allocation here but relying on consistent flags. `hnae_reinit_handle` can leave a handle with all queues torn down if queue reinitialization fails after provider reset. The AE class match path assumes providers have valid OF or ACPI fwnode data.

## Test Signals
Useful checks include successful AE registration/unregistration, `hnae_get_handle` failure injection at descriptor/buffer allocation points, DMA mapping error handling, RX buffer refill correctness, notifier delivery on AE registration, and queue teardown without leaks under repeated handle get/put and reinit cycles.

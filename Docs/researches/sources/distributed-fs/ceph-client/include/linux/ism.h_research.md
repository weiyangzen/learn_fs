# sources/distributed-fs/ceph-client/include/linux/ism.h

## Purpose
`ism.h` defines the IBM Internal Shared Memory device/client interface used by ISM hardware and SMC-D integration.

## Important APIs, types, and functions
It defines `MAX_CLIENTS`, `ISM_NR_DMBS`, `struct ism_dev`, `struct ism_event`, `struct ism_client`, `ism_register_client`, `ism_unregister_client`, `ism_get_priv`, `ism_set_priv`, and `ism_get_smcd_ops`.

## Control flow
Clients register an `ism_client` to receive events. ISM devices maintain per-client private pointers and subscriber slots. Event delivery invokes `handle_event`. SMC-D code can obtain `smcd_ops` from the ISM implementation.

## State and persistence
Runtime state includes device locks, command serialization lock, global device list link, PCI/DIBS pointers, SBA and event-queue DMA addresses, SBA bitmap, per-client private data, event queue index, and subscriber array. No on-disk persistence exists.

## Dependencies and integration points
It depends on workqueue includes, PCI/DIBS/SMC-D types supplied elsewhere, spinlocks, DMA mappings, bitmaps, and client registration code.

## Risks and test signals
Risks include client ID exhaustion, private-pointer misuse, event delivery after unregister, DMA/SBA bitmap leaks, and command-lock deadlocks. Tests should cover max-client registration, event fanout, unregister races, SBA allocation/free, PCI remove, and SMC-D ops availability.

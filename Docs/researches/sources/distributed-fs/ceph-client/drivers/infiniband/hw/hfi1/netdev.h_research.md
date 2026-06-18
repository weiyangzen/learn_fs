# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/netdev.h

## Purpose
`netdev.h` defines the shared HFI1 receive-context abstraction used by accelerated netdev/IPoIB support. It provides the receive queue structure, top-level RX manager structure, constants, inline accessors, and public lifecycle/table APIs.

## Important APIs, types, and functions
- `struct hfi1_netdev_rxq` binds one NAPI object to one HFI1 receive context and its parent `hfi1_netdev_rx`.
- `struct hfi1_netdev_rx` owns the dummy NAPI netdevice, HFI1 device pointer, RX queue array, receive queue count, first free RMT index, QPN/device xarray, and atomic reference counters for enabled queues and active netdevs.
- `HFI1_MAX_NETDEV_CTXTS` limits accelerated netdev contexts to eight.
- Inline helpers return context count, receive context pointer, and free RMT index.
- Public APIs allocate/free the RX manager, initialize/destroy shared RX queues, enable/disable queues, compute context count, and manage xarray data by ID.
- `hfi1_netdev_rx_napi()` is declared as the chip-level NAPI poll function.

## Control flow
Higher-level device setup calls `hfi1_alloc_rx()` to allocate the manager. IPoIB netdev setup calls `hfi1_netdev_rx_init()` to allocate contexts on first user and `hfi1_netdev_rx_destroy()` on final user. Open/stop call `hfi1_netdev_enable_queues()` and `hfi1_netdev_disable_queues()` to toggle NAPI and hardware receive context state. Receive demultiplexing uses the xarray APIs to map QPN-like IDs to netdev private data.

## State and persistence
State is runtime-only. Atomic `netdevs` reference-counts users of the shared queue allocation; atomic `enabled` reference-counts netdevs that have enabled receive processing. `dev_tbl` stores dynamic ID-to-data mappings for IPoIB devices and VLAN-like children.

## Dependencies and integration points
The header depends on Linux netdevice, NAPI, and xarray APIs plus HFI1 core context types. It integrates IPoIB setup, netdev RX implementation, MSI-X request paths, and chip-level receive polling.

## Risks
- Inline accessors assume `dd->netdev_rx` and the indexed `rxq` exist; callers must honor lifecycle ordering.
- Atomic counters drive allocation and enable/disable transitions; imbalance can leak receive contexts or disable queues while users remain.
- Xarray operations use caller-provided integer IDs; ID collisions return errors during add and must be handled by netdev setup.

## Test signals
- Multi-netdev open/close tests should verify `netdevs` and `enabled` transitions.
- Receive demultiplexing tests should add, find, iterate, and remove xarray entries, including collision handling.
- Context-count tests should cover AIP disabled, no available contexts, CPU mask limits, and the eight-context cap.

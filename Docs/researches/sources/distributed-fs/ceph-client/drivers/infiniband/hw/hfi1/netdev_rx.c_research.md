# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/netdev_rx.c

## Purpose
`netdev_rx.c` manages HFI1 receive contexts dedicated to accelerated netdev traffic. It allocates hardware receive contexts, attaches NAPI instances and MSI-X interrupts, enables/disables queues under shared reference counts, and stores QPN-to-netdev mappings for IPoIB receive demultiplexing.

## Important APIs, types, and functions
- `hfi1_netdev_allocate_ctxt()` creates a kernel receive context with netdev-specific flags, fast/slow handlers, and sequence count setup.
- `hfi1_netdev_setup_ctxt()` allocates receive header queues, eager buffers, configures receive-control bits, and installs netdev receive function maps.
- `hfi1_netdev_deallocate_ctxt()` disables receive control, frees MSI-X IRQs, clears TIDs/P_Keys, decrements stats, and frees the context.
- `hfi1_num_netdev_contexts()` chooses how many contexts to reserve based on AIP capability, available contexts, NUMA-local CPUs, and `HFI1_MAX_NETDEV_CTXTS`.
- `hfi1_netdev_rxq_init()` allocates `rxq` entries, allots contexts, adds NAPI to a dummy netdev, and requests netdev receive IRQs.
- `hfi1_netdev_rx_init()`/`destroy()` reference-count shared RX queue allocation.
- `hfi1_netdev_enable_queues()`/`disable_queues()` reference-count active NAPI/hardware queue enable state.
- `hfi1_alloc_rx()`/`hfi1_free_rx()` own the top-level `dd->netdev_rx` manager.
- Xarray helpers add, remove, load, and iterate data by integer ID.

## Control flow
At device initialization, `hfi1_alloc_rx()` creates the manager and a dummy netdev used only for NAPI registration. When the first IPoIB netdev initializes, `hfi1_netdev_rx_init()` increments `netdevs` from zero and calls `hfi1_netdev_rxq_init()` under `hfi1_mutex`. That function allocates one queue per configured netdev context, creates and configures each HFI1 context, pins it with `hfi1_rcd_get()`, attaches NAPI, and requests an MSI-X vector using the netdev NAPI interrupt handler.

On netdev open, `hfi1_netdev_enable_queues()` increments `enabled`; only the first opener enables all NAPI objects and hardware receive contexts. On stop, `hfi1_netdev_disable_queues()` decrements the counter; the final disable synchronizes all netdev IRQs, disables receive contexts/interrupts, synchronizes NAPI, and disables NAPI. Final netdev destruction deinitializes NAPI, contexts, IRQs, and queue memory.

## State and persistence
Runtime state includes the RX manager, dummy netdev, queue array, hardware receive contexts, MSI-X assignments, NAPI state, xarray device table, and atomic user counters. Hardware receive context state and interrupts are enabled only while at least one netdev is open. Nothing persists across device teardown.

## Dependencies and integration points
This file integrates HFI1 context allocation, receive header/eager buffer setup, receive-control programming, NAPI, MSI-X netdev IRQ requests, HFI1 global mutex, xarray demultiplexing, IPoIB RSM setup from `ipoib_rx.c`, and chip-level receive handlers.

## Risks
- Error unwinding in `hfi1_netdev_rxq_init()` iterates down from the failing index and must handle partially initialized entries correctly.
- `hfi1_netdev_disable_queues()` depends on `atomic_dec_if_positive()` semantics; counter imbalance can skip the actual disable path or over-disable.
- Receive context allocation is blocked when `HFI1_FROZEN` is set; callers need to surface `-EIO`.
- Xarray add uses `GFP_NOWAIT`, so allocation failure can make IPoIB netdev init fail under memory pressure.
- MSI-X and NAPI lifetimes are tightly coupled; IRQs must be synchronized before disabling/freeing NAPI contexts.

## Test signals
- Probe with AIP enabled/disabled, no available contexts, different NUMA CPU masks, and frozen device state.
- Fault-inject context creation, receive header queue setup, eager buffer setup, NAPI/IRQ request failures, and verify unwind.
- Open/stop multiple IPoIB netdevs concurrently and confirm hardware queues enable once and disable once.
- Validate xarray ID collision, lookup, removal, and iteration during receive demux.

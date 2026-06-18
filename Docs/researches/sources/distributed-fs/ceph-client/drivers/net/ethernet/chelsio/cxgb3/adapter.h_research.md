# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/adapter.h

## Purpose
`adapter.h` defines the OS-facing T3 adapter, port, SGE queue, and helper structures for `cxgb3`. It is included through `common.h` and centralizes Linux-specific state around netdevs, PCI, interrupts, work items, DMA rings, and offload device integration.

## Important APIs, Types, And Functions
- `struct iscsi_config` stores iSCSI MAC flags and optional send/receive hooks.
- `struct port_info` connects an adapter to a netdev port, queue-set assignment, PHY, MAC, link config, iSCSI address/config, activity, and link-fault state.
- Adapter flags include `FULL_INIT_DONE`, `USING_MSI`, `USING_MSIX`, `QUEUES_BOUND`, `TP_PARITY_INIT`, and `NAPI_INIT`.
- SGE data structures model free lists (`struct sge_fl`), response queues (`struct sge_rspq`), TX queues (`struct sge_txq`), queue sets (`struct sge_qset`), and the top-level `struct sge`.
- `struct adapter` aggregates `t3cdev`, PCI/MMIO state, device maps, parameters, interrupt stats, MSI-X metadata, SGE/MC5/MC7 modules, ports, delayed/workqueue jobs, debugfs root, locks, and a no-fail SKB.
- Inline helpers are `t3_read_reg`, `t3_write_reg`, `adap2pinfo`, `phy2portid`, `tdev2adap`, and `offload_running`.
- Prototypes expose SGE control, interrupt handler selection, netdev TX, management TX, queue allocation/coalescing, OS link callbacks, and EDC firmware loading.

## Control Flow And State
The header defines state used throughout the driver lifecycle. Probe allocates and fills `struct adapter`, creates netdev ports with `port_info`, prepares SGE queues, and binds queues/interrupts. Open/close paths update `open_device_map`, start/stop SGE, timers, and NAPI. Interrupt paths update `irq_stats`, queue work items, and dispatch through SGE/OS handlers. Offload uses the embedded `t3cdev` and `OFFLOAD_DEVMAP_BIT`.

## State And Persistence Behavior
Software state persists for the device lifetime: ring indices/generation bits, DMA addresses, queue credits, counters, work items, link state, and hardware module statistics. Hardware state is accessed by `t3_read_reg`/`t3_write_reg` through `adapter->regs`. Queue rings are DMA-backed and mirrored by software descriptor arrays.

## Dependencies And Integration Points
The header depends on Linux PCI, spinlocks, interrupts, timers, cache alignment, mutexes, bit operations, I/O accessors, `t3cdev`, and netdev internals. It integrates SGE, MC5/MC7, PHY/MAC common definitions, iSCSI/offload hooks, debugfs, workqueues, MSI/MSI-X, and netdev transmit queues.

## Risks And Edge Cases
Many fields are concurrency-sensitive: queue locks, response lock, adapter work lock, MDIO mutex, and stats lock must match their call paths. Ring indices/generation bits and DMA mappings must stay synchronized with hardware contexts. `phy2portid` assumes at most two ports and compares against port 0's embedded PHY. The no-fail SKB and workqueue paths imply recovery paths that must be robust under memory pressure and hardware fatal errors.

## Test Signals
Signals include clean probe/remove, open/close, MSI/MSI-X and legacy interrupt coverage, queue allocation/free with DMA leak checks, NAPI packet receive and TX reclaim, offload open/close state, link-fault work execution, and debugfs/stat counters matching traffic and injected errors.

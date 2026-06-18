# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad.h

## Purpose
Defines the Linux-facing BNAD private driver state, resource limits, flags, stats, Tx/Rx unmap metadata, exported helper prototypes, and small macros used by `bnad.c`, ethtool, debugfs, and firmware-image code.

## Important APIs, Types, and Functions
Important constants include queue depths and limits (`BNAD_TXQ_DEPTH`, `BNAD_RXQ_DEPTH`, `BNAD_MAX_RXP_PER_RX`, `BNAD_MAX_TXQ_PER_TX`), IRQ vector layout, timer frequencies, timeout values, MTU and queue-depth limits, refill threshold, and frame-size calculation. `struct bnad_rx_ctrl` binds one CCB to a NAPI instance and poll/interrupt counters. `struct bnad_completion` groups synchronous completions used around asynchronous BNA commands. `struct bnad_drv_stats` and `struct bnad_stats` feed ethtool and netdev stats. Resource wrappers `bnad_tx_res_info` and `bnad_rx_res_info` hold BNA resource arrays.

Data-path private structures include `bnad_tx_info`, `bnad_rx_info`, `bnad_tx_vector`, `bnad_tx_unmap`, `bnad_rx_vector`, `bnad_rx_unmap`, `bnad_rxbuf_type`, and flexible `bnad_rx_unmap_q`. The aggregate `struct bnad` holds netdev, BNA instance, queues, VLAN bitmap, coalescing settings, BAR, PCI device, MSI-X table, locks, timers, resources, completions, permanent MAC, workqueue, debugfs data, and names.

Exports include firmware `bfi_fw`, `cna_get_firmware_buf`, netdev/config helpers (`bnad_set_rx_mode`, `bnad_get_netdev_stats`, `bnad_mac_addr_set_locked`, `bnad_enable_default_bcast`, `bnad_restore_vlans`, `bnad_set_ethtool_ops`, `bnad_cb_completion`), setup/teardown helpers, coalescing helpers, stats fill helpers, and debugfs init/uninit.

## Control Flow and State
There is no standalone runtime control flow except macros. Flags split into `cfg_flags` values such as DIM/promisc/allmulti/default/MSI-X and `run_flags` bit positions such as CEE running, MTU set, mailbox IRQ disabled, netdev registered, DIM/stats timer running, and Tx priority set. `bnad_enable_rx_irq_unsafe()` is a performance-sensitive macro that reprograms coalescing and acknowledges the Rx interrupt block only if the Rx queue is marked started.

## State and Persistence Behavior
The header defines transient driver state only. It is the main in-memory persistence layer while the module is loaded: active VLANs, queue/resource allocations, timer state, stats, debugfs register read buffers, and firmware command completions are all rooted in `struct bnad`.

## Dependencies and Integration Points
Includes networking, firmware, VLAN, checksum, IPv6, workqueue, mutex, and `bna.h` definitions. It is included by all BNAD companion files and is the binding point between Linux APIs and the BNA control layer.

## Risks and Test Signals
Risks are fixed array limits not matching firmware attributes, flexible-array size calculations for unmap queues, stats string assumptions that mirror `struct bnad_drv_stats`, flag bit/value confusion between `cfg_flags` masks and `run_flags` bit positions, and exported prototypes drifting from implementation. Test signals include build coverage with netpoll and VLAN configs, Rx path counts at CPU/MSI-X limits, ethtool stats layout checks, and open/stop with debugfs enabled.

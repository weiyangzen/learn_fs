# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth.h

## Purpose
Primary internal header for the Fungible Ethernet driver. It defines admin queue sizes, default queue depths/coalescing, maximum MTU, device-private state, queue-set state, virtual port state, and cross-file function declarations.

## Important APIs, Types, And Functions
Key types are `struct fun_ethdev`, which subclasses `struct fun_dev`; `struct funeth_priv`, the `netdev_priv` state; `struct fun_qset`, a replaceable grouping of Rx/Tx/XDP queues; and `struct fun_vport_info` for SR-IOV virtual port policy. Declared APIs include port read/write, RSS configuration, queue replacement/count changes, ring count updates, ethtool setup, and Tx binding.

## Control Flow
`funeth_main.c` allocates a `fun_ethdev`, enables the embedded `fun_dev`, creates netdevices, initializes `funeth_priv`, and uses the declared helpers across Tx/Rx/ethtool/devlink modules. Queue sets allow reconfiguration by allocating a new set, transitioning it through states, and replacing live RCU queue pointers.

## State And Persistence
All state is runtime memory: PCI/netdev pointers, RCU queue arrays, IRQ xarray, link/capability data protected by seqcount, ethtool queue/coalescing settings, cumulative queue counters, RSS key/table and DMA config, stats DMA area, XDP program, devlink port, hardware timestamp config, kTLS counters, and virtual port settings.

## Dependencies And Integration Points
Includes Linux Ethernet, timestamp, mutex, seqcount, xarray, devlink, and funcore headers. Integrates with funeth Tx/Rx, ethtool, devlink, XDP, RSS, SR-IOV, stats, and optional TLS paths.

## Risks
The private state has many concurrent access domains: RTNL/state mutex, RCU queue pointers, seqcount link state, xarray IRQs, and atomic TLS counters. Queue replacement and XDP transitions must synchronize carefully. RSS/stats DMA buffers require exact allocation/free ordering.

## Test Signals
Probe/remove, netdev open/close, queue resizing, ethtool coalescing/ring/RSS operations, XDP attach/detach, SR-IOV VF configuration, devlink port registration, hardware timestamp get/set, stats DMA reads, and kTLS counters when enabled.

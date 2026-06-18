# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_rx.h

## Purpose
Declares the original HiNIC logical Rx queue structure, Rx statistics, checksum constants, and public queue lifecycle/stat APIs used by the main driver and ethtool/stat paths.

## Important APIs And Types
`struct hinic_rxq_stats` tracks packets, bytes, generic errors, checksum errors, other errors, allocation failures, and a `u64_stats_sync` seqlock for lockless 64-bit stats reads. `struct hinic_rxq` binds a Linux `net_device` to a hardware `hinic_rq`, stats, IRQ name, buffer sizing, Rx buffer shift, and NAPI instance. Public functions are `hinic_rxq_get_stats()`, `hinic_init_rxq()`, and `hinic_clean_rxq()`. Constants describe hardware checksum-offload masks and special error bits.

## Control Flow And State
The header exposes the state that `hinic_rx.c` manages. Queue lifetime begins with `hinic_init_rxq()`, which initializes stats, preposts buffers, and requests IRQ/NAPI. Runtime state is split between hardware RQ saved SKBs/CQEs and `struct hinic_rxq` metadata. `hinic_clean_rxq()` disables IRQ/NAPI and frees outstanding SKBs.

## Dependencies And Integration Points
It includes Linux netdevice, interrupt, and stats synchronization headers plus `hinic_hw_qp.h`. `hinic_main.c` allocates an array of these objects per netdev; `hinic_rx.c` owns their behavior; stats aggregation reads them through `hinic_rxq_get_stats()`.

## Risks And Test Signals
Risks are mostly structural: adding stats without updating aggregation or cleaning, changing buffer fields without matching Rx code, or using stats without `u64_stats_sync`. Signals include clean compilation, correct stats under 32-bit and 64-bit builds, Rx queue creation/teardown, and ethtool/netdev stats matching packet traffic.

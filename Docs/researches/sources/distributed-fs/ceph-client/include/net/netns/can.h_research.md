# sources/distributed-fs/ceph-client/include/net/netns/can.h

Purpose: Defines per-network-namespace Controller Area Network state.

Important APIs/types/functions: `struct netns_can` holds procfs entries, all-device receive filter lists, receive-list lock, statistics timer, package/list stats, and CAN gateway job list.

Control flow: CAN core initializes per-net receive lists and stats, receive paths consult `rx_alldev_list` under `rcvlists_lock`, stats timer updates counters, and gateway code tracks jobs in `cgw_list`.

State and persistence: Runtime per-net state with timers, locks, hlist/list nodes, and optional procfs dentries. It must be torn down before namespace release.

Dependencies/integration: Depends on CAN core receive lists, procfs, timers, spinlocks, CAN BCM proc entries, and CAN gateway.

Risks/test signals: Test namespace create/destroy, procfs entry cleanup, concurrent filter updates, stats timer shutdown, gateway job cleanup, and all-device receive filter behavior.

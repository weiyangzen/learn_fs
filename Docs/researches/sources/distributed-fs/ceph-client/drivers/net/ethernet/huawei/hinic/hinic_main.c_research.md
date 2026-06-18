# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_main.c

## Purpose
Provides the original HiNIC PCI netdevice driver entry point. It handles module parameters, PCI probe/remove/shutdown, netdevice allocation and registration, feature initialization, open/close sequencing, Rx/Tx queue lifecycle, RSS setup, link events, VLAN/MAC netdev operations, stats, and SR-IOV netdev operation wiring.

## Important APIs And Functions
Driver lifecycle is implemented by `hinic_probe()`, `nic_dev_init()`, `hinic_remove()`, `hinic_shutdown()`, `hinic_module_init()`, and `hinic_module_exit()`. Runtime netdev operations include `hinic_open()`, `hinic_close()`, `hinic_change_mtu()`, `hinic_set_mac_addr()`, VLAN add/remove callbacks, `hinic_set_rx_mode()`, `hinic_tx_timeout()`, `hinic_get_stats64()`, `hinic_fix_features()`, and `hinic_set_features()`. Queue helpers are `create_txqs()`, `create_rxqs()`, `free_txqs()`, `free_rxqs()`, plus RSS helpers such as `hinic_enable_rss()` and `hinic_rss_init()`.

## Control Flow And State
Probe enables PCI, reserves BARs, sets DMA mask, initializes `hinic_hwdev`, allocates a multiqueue `net_device`, fetches/sets MAC and MTU, registers management event callbacks, applies offload features, initializes interrupt coalescing/debugfs, and registers the netdev. `hinic_open()` brings hardware up, creates Tx then Rx queues, enables RSS, configures queue counts, enables port/function state, samples link state, notifies VFs, sets `HINIC_INTF_UP`, and wakes queues if link is up. `hinic_close()` disables Tx NAPI first, clears interface/link state under `mgmt_lock`, disables port/function state, tears down RSS and queues, and calls hardware ifdown. Persistent driver state lives in `struct hinic_dev`: flags, queue arrays, VLAN bitmap, RSS template, coalescing arrays, workqueue, and SR-IOV info.

## Dependencies And Integration Points
It integrates `hinic_hw_dev`, `hinic_port`, `hinic_tx`, `hinic_rx`, `hinic_debugfs`, `hinic_devlink`, and `hinic_sriov`. The netdev ops differ for PF versus VF; PF exposes VF configuration callbacks. Firmware management callbacks update carrier state and cable/module flags.

## Risks And Test Signals
Risk lies in resource unwinding across many probe/open failure labels, races between link events and close/remove, delayed rx-mode work, RSS template cleanup, and SR-IOV removal coordination. Test signals include probe/remove loops, open/close loops, feature toggles, VLAN/MAC sync, link flap, Tx timeout diagnostics, SR-IOV enable/disable, and fault injection for queue, IRQ, workqueue, and firmware-command failures.

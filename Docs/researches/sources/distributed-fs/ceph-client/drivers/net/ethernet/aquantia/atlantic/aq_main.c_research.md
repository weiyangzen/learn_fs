## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_main.c

Purpose: main Atlantic Linux netdev module entry and `net_device_ops` implementation.

Important APIs/types: exports XDP static key `aq_xdp_locking_key`, workqueue scheduler `aq_ndev_schedule_work()`, netdev allocator `aq_ndev_alloc()`, open/close functions, and module init/exit. Defines `aq_ndev_ops` with open, stop, start_xmit, multicast, MTU, MAC address, features, VLAN, TC, BPF/XDP, XDP xmit, and hardware timestamp operations.

Control flow: module init creates a single-thread workqueue then registers PCI driver; exit unregisters PCI and destroys the workqueue. Allocation creates a multiqueue Ethernet netdev and attaches netdev/ethtool ops. Open initializes NIC, reapplies saved RX NFC rules, updates VLAN filters, then starts the NIC. Close stops and deinitializes. TX diverts PTP timestamped or PTP UDP/L2 traffic to PTP queues when PTP datapath is up, otherwise uses normal NIC transmit. Feature changes clear ntuple/VLAN rules when disabling features, update config, restart for LRO/VLAN strip/insert changes, and reprogram RX checksum offload. XDP setup enforces MTU constraints for non-frag XDP programs, disables LRO if needed, swaps BPF program, updates static key, and restarts if RX mode changes.

State and persistence: stores runtime config in `aq_nic_s`/`aq_nic_cfg_s`, active VLAN bitmap, XDP program pointer, workqueue, and netdev features. State persists only across netdev close/open inside driver memory.

Dependencies/integration: coordinates `aq_nic`, PCI registration, ethtool ops, PTP, filters, hardware utilities, vector/XDP code, Linux TC mqprio, hwtstamp, and BPF APIs.

Risks: `aq_ndev_start_xmit()` inspects IP/UDP headers for PTP without visible skb protocol/linearization checks in this file, relying on stack assumptions. Feature restarts call close/open and must handle errors without leaving stale config. XDP program swaps require correct refcount/static-branch handling. VLAN kill path has special `-ENOENT` handling to update plain VLAN filters.

Test signals: module load/unload, PCI probe through dependent code, open/close error unwind, PTP traffic transmit, MTU/XDP constraints, feature toggles, VLAN add/kill, mqprio TC setup with max/min rates, hwtstamp get/set, and XDP attach/detach/xmit.

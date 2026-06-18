# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/txgbevf_main.c

Purpose: PCI virtual-function driver for Wangxun 10/25/40GbE devices. It is a compact adapter around shared `libwx` VF helpers, responsible for PCI enablement, netdevice allocation, BAR mapping, mailbox setup, queue sizing, feature defaults, interrupt scheme setup, and registration.

Important APIs: `txgbevf_pci_tbl` lists VF PCI IDs. `txgbevf_netdev_ops` wires open/stop/start-xmit/MAC-address operations to shared VF helpers. `txgbevf_set_num_queues()` asks the PF for traffic-class/default queue configuration and chooses queue counts using mailbox API level and RSS limits. `txgbevf_init_type_code()` maps device IDs to SP or AML MAC type. `txgbevf_sw_init()` initializes shared software state, mailbox, hardware reset, MAC address, ring/work defaults, and AML feature flags. `txgbevf_probe()` performs PCI resource setup and netdev registration. `txgbevf_remove()` delegates removal to `wxvf_remove()`.

Control flow: probe enables PCI memory access, sets 64-bit DMA, requests BARs, allocates a multiqueue netdev with `struct wx`, maps BAR0 and BAR4, initializes common/VF state, initializes service work, interrupt scheme, firmware version, then registers the netdev and stops TX queues until open. Error paths free interrupt/service/mailbox/common allocations and release PCI resources.

State and dependencies: state lives in `struct wx`: `pdev`, `netdev`, BAR mappings, mailbox, `vfinfo`, queue counts, ring counts, RSS key/table, feature flags, service timer/task, and interrupt vectors. Dependencies include PCI, DMA API, netdevice, `libwx` hardware/mailbox/VF/common/ethtool helpers, and PM callbacks.

Risks and tests: mailbox negotiation with PF, PF-reset handling, random MAC fallback, BAR4 mapping, AML merge/head-writeback flags, queue count selection, and cleanup ordering are the main risks. Test with SR-IOV enabled PFs, PF reset while VF probes, API <1.3 and >=1.3, suspend/resume, module unload, and traffic over one and multiple queues.

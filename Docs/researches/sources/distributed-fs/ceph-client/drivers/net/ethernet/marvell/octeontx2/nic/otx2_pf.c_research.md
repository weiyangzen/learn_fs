# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_pf.c

`otx2_pf.c` is the Physical Function driver entry point. It registers the PCI driver, probes/removes PF netdevs, manages AF and VF mailboxes, initializes NPA/NIX resources, opens/stops packet I/O, handles interrupts/resets, exposes netdev operations, manages SR-IOV, applies VF MAC/VLAN/trust settings, configures hardware timestamps, and integrates QoS, XDP, AF_XDP, TC, devlink, DCB, MACsec, and IPsec.

Important functions include `otx2_probe`, `otx2_remove`, `otx2_init_rsrc`, `otx2_open`, `otx2_stop`, `otx2_init_hw_resources`, `otx2_free_hw_resources`, PF-AF mailbox init/interrupt/work handlers, PF-VF mailbox forwarding, FLR/ME interrupt handling, queue/CQ interrupt handlers, `otx2_reset_task`, SR-IOV enable/disable/configure, and the `otx2_netdev_ops` table.

Probe enables PCI, configures DMA, allocates netdev queues, initializes AF mailbox and NPA/NIX resources, configures LMTST, obtains MAC/PTP/IOMMU, initializes MCAM, capabilities, MACsec/IPsec, features, TC, devlink, VF config, link events, AF_XDP bitmap, DCB, and QoS. Open allocates queue memory, initializes hardware, registers NAPI/IRQs, configures MTU/RSS/segmentation/coalescing/VLAN/timestamps/QoS/DMAC/TC, enables RXT, and sets RX mode. Stop disables traffic, IRQs, NAPI, refill work, and hardware resources while preserving ring-size settings.

State is held in `struct otx2_nic`, netdev, PCI drvdata, mailbox regions, workqueues, queue memory, and hardware. VF state is `vf_configs`; flags track interface-down, timestamp, pause, port-up, shutdown, and feature state. Dependencies include almost all local modules plus PCI, netdev, NAPI, IRQ/MSI-X, IOMMU, BPF/XDP, VLAN, page-pool, and RVU firmware.

Risks are teardown order, mailbox forwarding correctness, reset races, partial probe unwind, queue-count interactions with QoS/XDP/PFC, and restoring timestamp/pause/PFC/VLAN/DMAC state after reopen. Test probe/remove loops, up/down cycles, traffic, MTU/queue/ring changes, XDP/AF_XDP, TC/QoS, ntuple, VLAN, timestamps, SR-IOV, VF FLR/mailbox traffic, link events, and AF failure/defer paths.

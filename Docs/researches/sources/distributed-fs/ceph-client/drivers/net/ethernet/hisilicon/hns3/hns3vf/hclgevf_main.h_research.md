# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_main.h

Defines the shared HNS3 VF driver contract: register offsets, constants, state bits, device structs, MAC table nodes, reset statistics, vector data, and cross-file prototypes. `struct hclgevf_dev` is the central runtime object holding PCI/device resources, RSS, reset state, vectors, mailbox response/ARQ, service work, TQPs, NIC/RoCE handles, MAC/VLAN shadows, and devlink.

Important definitions include `enum hclgevf_states`, `struct hclgevf_mac`, `struct hclgevf_hw`, `struct hclgevf_misc_vector`, `struct hclgevf_rst_stats`, `struct hclgevf_mac_table_cfg`, and prototypes for mailbox handling, link/speed updates, reset/mailbox scheduling, port-base VLAN updates, and handle lookup.

The header has no execution flow but controls all implementation flow by defining the state bitmap and MMIO offsets for queues, interrupts, resets, GRO, RX descriptor layout, and BAR4 device memory. Dependencies are Linux net/VLAN/devlink types and HNS3 shared mailbox, command, HNAE3, RSS, and TQP stat headers. Risks are hardware-ABI register changes, state-bit misuse, and BAR layout assumptions. Test signals are compile coverage plus successful queue/vector/reset/mailbox/register-dump paths.

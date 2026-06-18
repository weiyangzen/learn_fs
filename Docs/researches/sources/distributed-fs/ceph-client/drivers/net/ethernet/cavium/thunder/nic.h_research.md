# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic.h

Purpose: Defines the shared Thunder NIC PF/VF protocol, device constants, VF private state, statistics structures, RSS state, mailbox messages, and helper declarations.

Important APIs, types, and functions: Constants cover PCI IDs, BARs, VF/MSI-X counts, frame-size bounds, queue counts, interrupt masks, RSS sizes, timeout values, and silicon revision helpers. `struct nicvf` is the VF netdev state with queue sets, XDP, secondary queue sets, link, RSS, pause, workqueues, timestamping, stats, NAPI, MSI-X, and mailbox state. `struct nicvf_hw_stats` and `struct nicvf_drv_stats` back ethtool counters. Mailbox message structs encode PF/VF operations for queue setup, RSS, MAC, FRS, BGX stats/link, secondary queue sets, loopback, stats reset, pause, PTP, and multicast filtering. `union nic_mbx` is the fixed two-word shared mailbox payload.

Control flow: VF code sends `union nic_mbx` commands to PF; `nic_main.c` interprets them and writes hardware registers or calls BGX helpers. VF ethtool and netdev paths use declarations here to reconfigure queues, RSS, stats, and timestamps.

State and persistence: State is volatile in PF/VF driver memory, hardware registers, and mailbox registers. No persistent configuration is stored here.

Dependencies and integration: Includes netdevice, interrupt, PCI, and `thunder_bgx.h`. It is shared by `nic_main.c`, `nicvf_main.c`, `nicvf_queues.c`, and `nicvf_ethtool.c`.

Risks: `BUILD_BUG_ON(sizeof(union nic_mbx) > 16)` in PF enforces the mailbox size; adding fields can break ABI. Bitfield and packed message changes must remain synchronized across PF and VF.

Test signals: Mailbox ABI size, every message type ACK/NACK path, VF queue count and SQS topology, RSS key/table updates, PTP single-packet TX timestamp constraints, and pass1/pass2 silicon feature gating.

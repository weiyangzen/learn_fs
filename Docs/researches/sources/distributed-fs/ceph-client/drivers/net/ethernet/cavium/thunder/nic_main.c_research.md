# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic_main.c

Purpose: Implements the Thunder NIC physical-function PCI driver. It initializes global NIC hardware, enables SR-IOV, handles PF mailbox interrupts from VFs, programs PF-owned queue/RSS/scheduler/BGX registers, and arbitrates resources.

Important APIs, types, and functions: `struct nicpf` stores PCI device, hardware capability table, node, flags, enabled VFs, register base, secondary qset maps, VF-to-LMAC map, CPI/RSSI bases, and MSI-X IRQ state. `nic_get_hw_info()` derives chip-specific capacities from subsystem IDs. `nic_init_hw()` enables the block, configures backpressure, TNS bypass, PKIND, timer, VLAN parsing, and CQM drop level. `nic_set_lmac_vf_mapping()` maps LMACs to primary VFs and programs credits. Mailbox handlers configure qsets, RQs/SQs, RSS, CPI, FRS, loopback, pause, PTP timestamping, multicast filters, BGX link/stats, SQS allocation, and VF shutdown. Probe enables PCI, maps BAR0, initializes hardware, registers MSI-X mailbox interrupts, and enables SR-IOV.

Control flow: VF writes a mailbox message; PF mailbox IRQ reads the two-word payload, dispatches by message ID, writes hardware or calls BGX helpers, then sends ACK/NACK or a data response. Shutdown disables VF/BGX LMAC paths and frees SQS allocations.

State and persistence: State is PF driver memory plus NIC/BGX CSRs and SR-IOV enablement. It is recreated on probe and removed on PCI remove.

Dependencies and integration: Uses `nic_reg.h`, `nic.h`, `q_struct.h`, `thunder_bgx.h`, PCI SR-IOV/MSI-X APIs, and relaxed MMIO accesses justified by ThunderX ordering.

Risks: PF trusts many VF-provided indexes after limited validation. Resource maps for SQS and VF/LMAC must stay consistent across VF reset/shutdown. Hardware revision branches change mailbox write order and register programming.

Test signals: Probe/remove unwind, SR-IOV VF count limits, mailbox ACK/NACK for every message, pass1/pass2 behavior, RSS/CPI/scheduler register programming, SQS allocation/free, BGX link and MAC operations, and reset/shutdown races.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic_reg.h

Purpose: Defines Thunder NIC PF/VF register offsets, register counts, bit shifts, tunnel constants, and the PKIND configuration bitfield.

Important APIs, types, and functions: PF offsets cover global config/status, interrupt timers, mailbox interrupt registers, VLAN/tunnel parser definitions, ECC/BIST, interfaces, MCAM, CPI/MPI/RSSI tables, LMAC credits/config, channel config, RX sync, transmit scheduler TL2/TL3/TL4, VF mailboxes, per-VNIC stats, qset config, and PF MSI-X. VF offsets cover VNIC config, PF mailbox registers, interrupts, RSS config/key, VNIC stats, queue set CQ/RQ/SQ/RBDR registers, and VF MSI-X. Shifts define queue number, queue set ID, VF number, and MSI-X vector layout. `struct pkind_cfg` models min/max length, length-error enable, receive header mode, and header skip.

Control flow: PF and VF drivers compose register addresses by ORing base offsets with shifted VF/qset/queue indexes, then read/write through their MMIO helpers.

State and persistence: The header has no state, but every constant maps to hardware state whose values persist until reset or reprogramming.

Dependencies and integration: Used by Thunder PF main, VF main, queues, and ethtool register dump. Tunnel constants are consumed when PF enables Geneve/NVGRE/VXLAN parsing.

Risks: A wrong offset or shift corrupts unrelated hardware state. `nicvf_get_regs()` depends on register count matching the dump sequence. Bitfield layout in `pkind_cfg` must match endian-specific hardware format.

Test signals: Register dump length/indexing, qset address construction, PF mailbox interrupt masks for 128 VFs, PKIND programming under PTP enable/disable, and tunnel parsing register writes.

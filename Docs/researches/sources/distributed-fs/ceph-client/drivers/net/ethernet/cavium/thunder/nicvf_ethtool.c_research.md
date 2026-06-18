# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_ethtool.c

Purpose: Implements ethtool operations for the Thunder NIC virtual-function netdev.

Important APIs, types, and functions: Stat descriptor arrays expose hardware, driver, queue, and BGX stats. Link helpers report speed/duplex/port capabilities from PF-provided link state. Stats functions update VF and LMAC stats, aggregate per-CPU driver stats, and append primary/secondary qset queue counters. Register dump functions read VF mailbox, interrupt, RSS, stats, CQ/RQ/SQ/RBDR registers while avoiding a known bus-error register. Ring parameter setters clamp to supported powers of two and restart the interface when running. RSS functions get/set hash fields, indirection table, key, and hash function. Channel setters adjust RX/TX/XDP queue counts and secondary qset count, restart when needed, and update XDP feature flags. Pause operations use PF mailbox `NIC_MBOX_MSG_PFC`. Timestamp info reports Cavium PTP hardware clock support.

Control flow: Users invoke ethtool; operations read cached VF state, MMIO registers, or send mailbox commands to PF for BGX/PFC-backed settings. Some mutating operations stop/open the netdev to rebuild queues.

State and persistence: Updates volatile VF fields such as message level, queue lengths/counts, RSS config/key/table, pause config, and XDP feature flags. Hardware register writes and PF mailbox changes last until reconfiguration/reset.

Dependencies and integration: Depends on `nic.h`, `nic_reg.h`, `nicvf_queues.h`, queue stats helpers, `thunder_bgx.h`, and Cavium PTP common code.

Risks: `nicvf_get_regs()` has a likely typo in the RX stats loop using `stat` instead of `i` for offset construction. Queue/channel changes can fail during reopen, leaving partially updated software counts. RSS changes require RSS enabled and valid hash field combinations.

Test signals: `ethtool -S`, `-d`, `-g/-G`, `-x/-X`, `-l/-L`, `-a/-A`, timestamp info, pass1 ringparam rejection, XDP queue constraints, secondary qset stats, and PF mailbox timeout on pause operations.

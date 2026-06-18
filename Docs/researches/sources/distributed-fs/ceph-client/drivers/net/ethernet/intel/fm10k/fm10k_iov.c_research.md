# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_iov.c

## Purpose
`fm10k_iov.c` implements PF-side SR-IOV support for fm10k: VF mailbox message handling, VF reset/event processing, VF resource allocation and teardown, DGLORT/lport setup, default MAC/VLAN assignment, VF stats, and netdev VF configuration NDOs.

## Important APIs, types, and functions
Static mailbox handlers include `fm10k_iov_msg_error` and `fm10k_iov_msg_queue_mac_vlan`; `iov_mbx_data` registers TLV handlers. Runtime entry points are `fm10k_iov_event`, `fm10k_iov_mbx`, `fm10k_iov_suspend`, `fm10k_iov_resume`, `fm10k_iov_update_pvid`, `fm10k_iov_disable`, `fm10k_iov_configure`, `fm10k_iov_update_stats`, and NDO helpers for VF MAC, VLAN, bandwidth, config, and stats.

## Control flow
VF MAC/VLAN mailbox requests are validated against VF enabled state, PF-assigned VLAN, locked MAC, multicast permission, and selected VID before calling hardware VLAN ops or queueing MAC requests to the PF switch manager. `fm10k_iov_event` handles VFLR by reading reset bits, resetting resources, and reconnecting VF mailboxes. `fm10k_iov_mbx` processes VF mailboxes under the PF mailbox lock, drains the upstream SM mailbox, resets invalid lports or timed-out mailboxes, checks SM mailbox space, and rotates `next_vf_mbx` to avoid starvation. Configure paths disable existing SR-IOV when safe, allocate `iov_data`, initialize PF/VF mailboxes, resume hardware resources, and enable PCI SR-IOV.

## State and persistence behavior
Persistent state lives in `interface->iov_data`, each `fm10k_vf_info`, mailbox state, VF GLORT/lport resources, VF stats arrays, PF/VF VLAN and MAC settings, VF rate limits, and `next_vf_mbx`. The pointer is freed with `kfree_rcu`; readers use RCU in event/mailbox paths. Hardware state includes DGLORT maps, VF lports, VLAN tables, queues, AER completion-abort mask, and PCI SR-IOV VF enablement.

## Dependencies and integration points
The file depends on `fm10k_pf.h`, `fm10k_vf.h`, TLV/mailbox helpers, PCI SR-IOV APIs, netdev VF NDOs, RCU, and hardware operation tables under `hw->iov`, `hw->mac`, and `hw->mbx`. It integrates with service task mailbox polling, reset/suspend/resume, netdev admin commands, and stats update.

## Risks
SR-IOV cannot be safely modified while VFs are assigned; the code logs and preserves current VF count. VF mailbox floods can starve the PF switch-manager mailbox, so backpressure handling and `next_vf_mbx` fairness matter. VLAN/MAC validation is security-sensitive because rogue VFs must not receive unauthorized traffic. RCU lifetime and mailbox locking must be preserved. The resume path masks PCIe completer abort reporting because VF reads of unowned queues can otherwise destabilize platforms.

## Test signals
Enable/disable varying VF counts, attempt changes while VFs are assigned, exercise VF FLR, mailbox traffic, MAC/VLAN/multicast requests, PF-assigned VLAN enforcement, VF rate limits, stats reads, suspend/resume, and AER behavior. Watch for mailbox timeout counters, SM mailbox full counters, stale MAC/VLAN queue entries, and RCU/lockdep warnings.

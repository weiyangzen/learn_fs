# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/ngbevf_main.c

## Purpose
`ngbevf_main.c` is the concrete PCI/netdev wrapper for Wangxun GbE virtual functions. It matches VF PCI IDs, allocates and initializes `struct wx`, wires shared VF common operations into netdev/PM hooks, initializes mailbox/reset state, registers the netdev, and delegates most runtime behavior to `libwx`.

## Important APIs, Types, and Functions
Important routines are `ngbevf_probe()`, `ngbevf_remove()`, `ngbevf_sw_init()`, and `ngbevf_set_num_queues()`. `ngbevf_netdev_ops` maps open/close to `wxvf_open()`/`wxvf_close()`, transmit to `wx_xmit_frame()`, validation to `eth_validate_addr()`, and MAC set to `wx_set_mac_vf()`. PCI PM uses `wxvf_suspend()` and `wxvf_resume()`.

## Control Flow
Probe enables PCI memory, sets DMA mask, requests BARs, allocates a one-queue netdev, maps BAR0, installs ethtool and netdev ops, then calls `ngbevf_sw_init()`. Software init runs `wx_sw_init()`, initializes mailbox parameters and lock, resets the VF through the PF, negotiates API 1.3, obtains or randomizes a MAC, sets queue/ITR/ring/work limits, and installs the queue-count callback. Probe then enables minimal features, initializes service and interrupt scheme, queries firmware version, registers the netdev, stores drvdata, and stops TX queues until open.

## State and Persistence Behavior
Runtime state is in `struct wx`: mailbox, VF API, MAC, ring counts, one TX/RX queue, interrupt scheme, service timer/work, firmware id string, and allocated `vfinfo`/RSS/MAC tables from shared init. No persistence beyond PCI/device state; all state is rebuilt on probe or VF reset.

## Dependencies and Integration Points
It depends on shared `wx_type`, `wx_hw`, `wx_lib`, `wx_mbx`, `wx_vf`, `wx_vf_common`, and `wx_ethtool` APIs. The VF depends on a functioning PF for reset, mailbox API negotiation, MAC assignment, queue configuration, link notifications, and MAC/VLAN filter programming.

## Risks and Edge Cases
If the PF is down or in reset, software init fails after allocations and must clean up correctly. Random MAC assignment occurs when PF provides none, but PF-side policy may still reject later MAC changes. Only one TX/RX queue and one MSI-X vector are configured, so queue-query results above one are not used here. Feature set is minimal compared to PF.

## Test Signals
Probe/remove with PF up/down, no assigned MAC, random MAC fallback, mailbox timeout, firmware version query failure, interrupt scheme failure, and netdev registration failure. Exercise open/close, MAC change, suspend/resume, link update, and PF reset recovery.

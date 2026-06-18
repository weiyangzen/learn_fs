# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_main.h

## Purpose
`hclge_main.h` is the central PF-side contract for the Hisilicon HNS3 `hclge` Ethernet controller driver. It collects BAR/register offsets, reset and interrupt bits, link-speed definitions, traffic-management state, MAC/FEC/statistics layouts, flow director rule structures, vport/VF shadow state, and the exported PF helper prototypes used by mailbox, MDIO, PTP, register dump, TM, debugfs, reset, and client callbacks. The file does not implement behavior itself, but it defines almost all long-lived PF and vport state that the implementation files mutate.

## Important APIs, Types, And Data
- Device constants include PF/VF limits, vector register bases, TQP/ring BAR offsets, RSS table size, UMV capacity, TQP reset retries, reset interrupt registers, frame size bounds, and advertised speed-ability bitmaps from 10M through 200G.
- `enum HCLGE_DEV_STATE` is the core driver state bitmap: down/disabled/removing, NIC/RoCE/service initialization, reset/mbox/error scheduling and handling, statistics and link update states, flow-director changes, PTP enable/TX handling, and FEC statistics updating.
- `struct hclge_mac` stores negotiated/requested link settings, media/module/FEC abilities, WOL state, PHY/MDIO pointers, and ethtool link-mode masks.
- `struct hclge_dev` is the PF device root. It owns PCI and AE device pointers, common hardware wrapper, misc vector, MAC/FEC stats, reset state and counters, queue/vport allocation, scheduler and FC state, MSI accounting, service timer/work, vport array, clients, flags, packet buffer sizes, VLAN tables, flow-director tables, UMV accounting, MAC tunnel log FIFO, PTP state, devlink pointer, and RSS config.
- `struct hclge_vport` is the PF/VF virtual-port shadow object. It records allocated queues, qset offset, bandwidth, VLAN filter and port-based VLAN state, TX/RX VLAN tag policy, handles for NIC/RoCE clients, liveness/notification bits, MPS, VF policy (`spoofchk`, trusted, link state, max TX rate, requested promisc flags), and pending MAC/VLAN lists protected by `mac_list_lock`.
- Flow Director definitions (`enum HCLGE_FD_*`, `struct hclge_fd_rule`, `struct hclge_fd_cfg`) describe tuple/meta matching, user-defined offsets, TCAM x/y encoding, ARFS/flower/ethtool-private rule variants, and rule lifecycle states.
- Exported prototypes expose PF operations such as `hclge_mbx_handler()`, vport promisc/MAC/VLAN mutation, ring-vector binding, flow control, TQP reset, vport start/stop/MTU, reset notification, debug read dispatch, port-base VLAN push/restore, stats update, PTP helpers through `hclge_ptp.h`, and SCC version query.

## Control Flow And State Behavior
This header acts as the dependency hub for runtime control flow. `hclge_main.c` initializes `struct hclge_dev`, creates vports and queue mappings, schedules service/reset/mailbox work via state bits, and registers operation tables that call into the specialized files in this subset. Mailbox code uses `hclge_vport`, VF policy state, VLAN/MAC list helpers, and reset helpers. MDIO code reads `hclge_mac` PHY fields and updates requested speed/duplex after PHY callbacks. PTP code uses `hclge_dev::ptp` plus `HCLGE_STATE_PTP_EN` and `HCLGE_STATE_PTP_TX_HANDLING`. TM code reads and writes `hclge_tm_info`, vport RSS/qset fields, FC mode, and `hw_tc_map`.

Persistent driver state is in memory only and is reconstructed during probe, reset, and restore paths. Several fields are shadow copies of hardware state that must be replayed after reset: MAC/VLAN pending lists, port-base VLAN config, RSS config, TM/PFC settings, PHY requested speed/duplex, PTP timestamp config, and flow-director rules. Synchronization is explicit through bitmaps, `reset_sem`, `vport_lock`, `fd_rule_lock`, `mac_list_lock`, the PTP spinlock, and service work scheduling.

## Dependencies And Integration Points
The header depends on Linux networking, PHY, VLAN, debugfs, kfifo, devlink, IPv6, and HNS3 common headers (`hclge_cmd.h`, `hclge_comm_rss.h`, `hclge_comm_tqp_stats.h`, `hnae3.h`, `hclge_ptp.h`). It binds the PF implementation to the HNAE3 abstract Ethernet framework through `struct hnae3_handle`, `struct hnae3_client`, queue metadata, reset notifications, and ethtool/devlink-facing operations. It also shares register definitions with register-dump and mailbox code.

## Risks And Edge Cases
- Many arrays are sized by hardware constants (`HNAE3_MAX_TC`, `HCLGE_VPORT_NUM`, `MAX_FD_FILTER_NUM`); incorrect firmware-reported limits or unchecked indexes in implementation code can corrupt shadow state or program invalid hardware entries.
- The file mixes PF and VF vport numbering conventions. Implementations must consistently distinguish `vport_id`, VF id, and PF-relative queue ids.
- Several fields are reset-sensitive shadow state. Missing restore after FLR, PF reset, or global reset can leave hardware and software inconsistent.
- Because many modules depend on this header, changing state layout or enum bits has broad ABI-like impact inside the driver.

## Test Signals
Useful validation signals include probe/remove across PF and SR-IOV VFs, PF/VF reset and FLR recovery, mailbox traces, ethtool stats/register/timestamp output, VLAN/MAC restore after reset, DCB/PFC configuration, RSS queue counts, devlink reload behavior, and sparse/build coverage for structure layout and prototypes.

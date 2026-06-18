# subset-b-004436 research

Grouped research for the HNS3 PF/VF networking driver files in subset B. Each section is delimited for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_main.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mbx.c

## Purpose
`hclge_mbx.c` implements PF-side mailbox handling for VF and firmware-originated requests. It drains the command receive queue, validates messages, dispatches by mailbox opcode, mutates PF/VF shadow state, invokes hardware configuration helpers, sends synchronous responses when requested, and pushes asynchronous notifications such as link, reset, and port-base VLAN state to VFs.

## Important APIs And Functions
- `hclge_mbx_handler()` is the entry point scheduled by the PF service path. It loops until the CRQ is empty, checks command disable state, validates descriptor ownership and source VF id, traces received messages, dispatches, clears descriptors, advances the CRQ pointer, and writes back the head register.
- `hclge_gen_resp_to_vf()` builds a `HCLGEVF_OPC_MBX_PF_TO_VF` response descriptor, mirrors original code/subcode/match id, bounds response length, maps negative errno to a u16 response status, traces, and sends through the command queue.
- `hclge_send_mbx_msg()` is the common async PF-to-VF sender used by reset, link, and VLAN notifications.
- `hclge_get_ring_chain_from_mbx()`, `hclge_map_unmap_ring_to_vf_vector()`, and `hclge_get_vf_ring_vector_map()` convert VF mailbox ring parameters into `hnae3_ring_chain_node` chains and bind/query interrupt vector mappings.
- VF configuration handlers cover promisc requests, UC/MC MAC updates, VLAN filter and RX strip changes, VF alive/start/stop, MTU, queue id translation, RSS key paging, queue reset, VF reset request, link mode/status, media type, MAC address query, VF FLR cleanup, VF uninit cleanup, NCSI error reset escalation, and VF table clear.
- `hclge_mbx_ops_list[]` maps `HCLGE_MBX_*` opcodes to small handler wrappers that translate results into synchronous responses.

## Control Flow
The receive path is descriptor-driven. `hclge_mbx_handler()` reads CRQ descriptors, verifies `HCLGE_CMDQ_RX_OUTVLD_B`, rejects out-of-range VF ids, and populates `hclge_mbx_ops_param` with the addressed `hdev->vport[mbx_src_vfid]`. `hclge_mbx_request_handling()` looks up the opcode in `hclge_mbx_ops_list`, calls the handler, and sends a response only when `mbx_need_resp` is set and the opcode is below the FLR-status boundary, because PF must not reply to IMP-owned messages.

Configuration requests usually do not program hardware immediately in this file. Promisc and MAC modify paths update vport request/shadow state and schedule the PF service task. VLAN filter, MTU, TQP reset, ring-vector bind, and queue-id translation call direct helpers. Keepalive marks `last_active_jiffies` and transitions initialized VFs to alive, then pushes pending link/reset/VLAN notifications. Link-change messages schedule the PF service task and optionally decode link-failure codes.

## State And Persistence Behavior
The file updates in-memory VF state under `struct hclge_vport`: requested promisc flags, `HNAE3_PFLAG_LIMIT_PROMISC`, MAC/VLAN pending lists, port-base VLAN notification bits, liveness bits, `last_active_jiffies`, `mps`, and queue/vector mapping. It also reads shared PF state such as MAC link/speed/duplex, RSS key, supported/advertising link modes, and reset type. On VF FLR or uninit it removes MAC and VLAN table state, either preserving or deleting list entries depending on the path. NCSI errors set a global reset request through the AE device operations.

## Dependencies And Integration Points
This file depends on `hclge_main.h`, mailbox command layouts from `hclge_mbx.h`, HNAE3 helpers, common RSS state, tracepoints in `hclge_trace.h`, command queue send/read/write helpers, PF vport MAC/VLAN management, reset helpers, and service scheduling. It integrates directly with the VF driver protocol: response payload sizes, opcodes, match ids, and multi-message RSS key/link-mode queries must remain compatible with hns3 VF code and firmware expectations.

## Risks And Edge Cases
- Mailbox payload parsing is offset- and struct-layout-sensitive. Incorrect `msg_len`, ring counts, or untrusted VF indexes could lead to invalid queue/vector operations if validation is incomplete.
- `hclge_errno_to_resp()` stores `abs(errno)` into a u16 and clamps out-of-range values to `EIO`; unusual positive statuses may not map as VF expects.
- Some handlers update shadow state and schedule service work instead of synchronously applying hardware changes, so response success may precede actual hardware programming.
- Link-mode responses only send one `unsigned long` chunk selected by VF query index; compatibility depends on both sides agreeing on bitmap paging.
- `hclge_get_basic_info()` reads `basic_info->pf_caps` from zeroed response storage before setting bits, which is safe only because the response buffer is cleared before dispatch.

## Test Signals
Exercise SR-IOV VF probe, mailbox handshake, VF MAC/VLAN add/delete, spoofed MAC rejection, promisc and limited-promisc requests, RSS key paging with invalid indexes, vector map/unmap/query, VF queue reset, VF initiated reset, PF reset notifications, link changes, NCSI error escalation, and tracepoint output for `hclge_pf_mbx_get/send`. Kernel fault injection around command send and allocation failures should validate response/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mdio.c

## Purpose
`hclge_mdio.c` connects the PF MAC to an external PHY through a Linux `mii_bus` backed by HNS3 firmware command descriptors. It implements Clause 22 MDIO read/write callbacks, registers the MDIO bus when a PHY address exists, connects the PHY to the PF netdev, adjusts MAC speed/duplex and flow control on PHY link updates, starts/stops/disconnects the PHY, and provides direct firmware PHY register read/write helpers.

## Important APIs And Functions
- `hclge_mac_mdio_config()` validates `hdev->hw.mac.phy_addr`, allocates and registers a devm MDIO bus, sets `read`, `write`, `priv`, `phy_mask`, and stores `mac->phydev`/`mac->mdio_bus`.
- `hclge_mdio_read()` and `hclge_mdio_write()` build `HCLGE_OPC_MDIO_CONFIG` descriptors, encode phy id, register id, start/ST/op fields, check command-disable state, send commands, and return data or errno.
- `hclge_mac_connect_phy()` attaches the stored PHY to the PF netdev using `phy_connect_direct()` with SGMII, limits PHY supported modes to MAC-supported modes, configures Marvell LED flags, and sets default advertising.
- `hclge_mac_adjust_link()` is the PHY link callback. On link-up it calls `hclge_cfg_mac_speed_dup()`, updates requested speed/duplex shadow fields, and reconfigures flow control.
- `hclge_mac_start_phy()`, `hclge_mac_stop_phy()`, and `hclge_mac_disconnect_phy()` wrap PHY lifecycle calls.
- `hclge_read_phy_reg()` and `hclge_write_phy_reg()` use `HCLGE_OPC_PHY_REG` firmware commands for direct register access separate from the Linux MDIO bus callbacks.

## Control Flow
Probe/init calls `hclge_mac_mdio_config()` only when the PF reports a valid PHY address. The registered `mii_bus` makes subsequent PHY library operations call into `hclge_mdio_read/write()`. Client open/connect paths call `hclge_mac_connect_phy()` and later `hclge_mac_start_phy()`. When the PHY reports link changes, `hclge_mac_adjust_link()` updates MAC speed/duplex and flow-control hardware. Stop/remove paths call `hclge_mac_stop_phy()` and `hclge_mac_disconnect_phy()`.

## State And Persistence Behavior
State is kept in `hdev->hw.mac`: `phydev`, `mdio_bus`, requested speed and duplex, supported/advertising masks, and PHY address. MDIO bus allocation is devm-managed, but failed PHY lookup after registration explicitly unregisters the bus. No persistent storage is written; link parameters are shadowed in memory and reprogrammed after PHY events or reset-driven reconnect.

## Dependencies And Integration Points
The file integrates Linux PHY/MDIO APIs (`devm_mdiobus_alloc`, `mdiobus_register`, `mdiobus_get_phy`, `phy_connect_direct`, `phy_start/stop/disconnect`, linkmode helpers) with HNS3 command descriptors. It relies on `hclge_cmd_send()`, bitfield helpers, MAC configuration helpers in PF main code, and flow-control setup from TM/main code. It has a Marvell-specific LED dev flag and assumes `PHY_INTERFACE_MODE_SGMII`.

## Risks And Edge Cases
- `PHY_INEXISTENT` is a driver-local sentinel value of 255; firmware must not use it for a real bus address.
- Only Clause 22 operations are implemented, so Clause 45 PHY requirements would need additional support.
- `hclge_mac_stop_phy()` reads `netdev->phydev`, while other helpers use `hdev->hw.mac.phydev`; mismatch after partial connect/disconnect could matter.
- `hclge_mac_adjust_link()` ignores link-down events, so hardware link-down handling must occur elsewhere.
- Command-disabled state returns `-EBUSY` for MDIO bus operations during reset; PHY library callers must tolerate transient failures.

## Test Signals
Validate probe with no PHY, invalid PHY address, missing PHY after bus registration, successful SGMII PHY attach, autoneg/link changes, Marvell LED flag behavior, ethtool PHY register reads/writes, reset-time `-EBUSY` handling, and MAC speed/duplex/flow-control changes when PHY link comes up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mdio.h

## Purpose
`hclge_mdio.h` is the small PF MDIO/PHY interface header. It exposes the lifecycle and register-access helpers implemented in `hclge_mdio.c` to PF initialization, client open/close, and diagnostic code.

## Important APIs
- `hclge_mac_mdio_config(struct hclge_dev *hdev)` allocates/registers the MDIO bus and locates the configured PHY.
- `hclge_mac_connect_phy(struct hnae3_handle *handle)` attaches the PHY to the PF netdev and constrains advertised modes.
- `hclge_mac_disconnect_phy(struct hnae3_handle *handle)` detaches the PHY.
- `hclge_mac_start_phy(struct hclge_dev *hdev)` and `hclge_mac_stop_phy(struct hclge_dev *hdev)` control PHY polling/link state.
- `hclge_read_phy_reg()` and `hclge_write_phy_reg()` provide firmware-command register access.

## State, Dependencies, And Integration
The header forward-declares `struct hclge_dev`, includes `hnae3.h` for the handle type, and intentionally hides all MDIO command layout details from callers. It integrates the PF main driver with Linux PHY lifecycle code without exporting the static bus callbacks.

## Risks And Test Signals
The main risk is API sequencing: callers must configure MDIO before connect/start and must tolerate null PHY devices on PHY-less media. Build coverage should catch signature drift, while runtime tests should cover probe/open/stop/remove with both PHY-present and PHY-absent hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_ptp.c

## Purpose
`hclge_ptp.c` implements PF hardware timestamping and PHC support for HNS3 devices with PTP capability. It registers a Linux PTP clock, configures timestamp modes through firmware commands, reads and writes PTP MMIO registers, handles TX and RX hardware timestamp delivery, supports clock get/set/adjtime/adjfine operations, and enables/disables PTP interrupts.

## Important APIs And Functions
- `hclge_ptp_init()` checks `HNAE3_DEV_SUPPORT_PTP_B`, creates the PHC if needed, reads cycle parameters, enables PTP interrupt, sets base frequency, restores timestamp mode, initializes PHC time from real time, and sets `HCLGE_STATE_PTP_EN`.
- `hclge_ptp_uninit()` disables interrupt and timestamp mode, clears state/flags, releases any pending TX skb, unregisters the PTP clock, and frees the PTP object.
- `hclge_ptp_set_tx_info()` is called from the TX path. It accepts at most one outstanding timestamp skb by testing `HCLGE_STATE_PTP_TX_HANDLING`, stores an skb reference, and increments counters.
- `hclge_ptp_clean_tx_hwts()` reads TX timestamp registers, stamps and frees the saved skb if present, records sequence id and counters, and clears the TX handling bit.
- `hclge_ptp_get_rx_hwts()` combines descriptor-provided low seconds/nanoseconds with high seconds from a current-time register under lock and writes skb hardware timestamp metadata.
- `hclge_ptp_get_cfg()`/`hclge_ptp_set_cfg()` implement hwtstamp get/set, validating that PHC support is enabled.
- PTP clock callbacks `hclge_ptp_adjfine()`, `hclge_ptp_adjtime()`, `hclge_ptp_gettimex()`, and `hclge_ptp_settime()` provide frequency, offset, read, and set operations.
- `hclge_ptp_cfg_qry()` is an exported firmware query helper used by diagnostics.

## Control Flow
Initialization allocates `struct hclge_ptp`, sets `ptp_clock_info` callbacks, maps `io_base` to the PTP register window, registers the PTP clock, validates cycle denominator, enables interrupt via `HCLGE_OPC_PTP_INT_EN`, writes cycle and timestamp mode config, and sets PHC time. Runtime timestamp configuration flows through `hclge_ptp_set_ts_mode()`: TX and RX filter settings are translated to hardware bits, `HCLGE_OPC_PTP_MODE_CFG` is sent, then software flags and cached `ts_cfg` are updated.

TX timestamp flow starts in the transmit path through `hclge_ptp_set_tx_info()`, then interrupt/service logic in PF main calls `hclge_ptp_clean_tx_hwts()` once hardware has produced a timestamp or timeout service needs cleanup. RX timestamp flow occurs per received skb with descriptor timestamp fields. Clock adjustment paths write MMIO registers protected by `ptp->lock`; large `adjtime` values fall back to get-plus-set.

## State And Persistence Behavior
`hdev->ptp` owns PTP state: registered clock, saved TX skb, mode flags, MMIO base, cached timestamp config, last TX sequence id, cycle parameters, counters, last RX time, and timeout counters. `HCLGE_STATE_PTP_EN` gates public operations; `HCLGE_STATE_PTP_TX_HANDLING` serializes TX timestamp requests. Configuration is in-memory and hardware-register-backed, and must be reinitialized after reset. The code uses `spin_lock_irqsave()` around PTP register sequences that require coherent multi-register access.

## Dependencies And Integration Points
The file depends on Linux PTP clock APIs, network timestamping APIs, skb timestamp helpers, MMIO read/write, firmware command descriptors, HNAE3 capability bits, and PF service/reset paths. It is wired into the PF operation table for `set_tx_hwts_info`, `get_rx_hwts`, `get_ts_info`, `hwtstamp_get`, and `hwtstamp_set`, and PF service code calls TX timestamp cleanup.

## Risks And Edge Cases
- Only one TX timestamp can be outstanding; additional timestamp requests are skipped and counted. Workloads expecting many concurrent TX timestamps may see drops.
- `hclge_ptp_set_tx_info()` increments `ptp->tx_skipped` after checking `ptp` but before any locking of the rest of `ptp`; lifecycle must ensure no concurrent uninit.
- RX high seconds are read from current-time registers rather than descriptor space; rollover between descriptor timestamp and high-second read is a subtle boundary risk.
- `hclge_ptp_init()` destroys the PTP clock on several failures, even when `hdev->ptp` was newly created in the same call; reset paths must not reuse stale pointers.
- Unsupported filters return `-ERANGE`; user tools should see normalized filters for accepted broad PTP v1/v2 event classes.

## Test Signals
Validate `ethtool -T`, `SIOCSHWTSTAMP`/netlink hwtstamp set/get for accepted and rejected filters, PHC registration, `phc2sys`/`testptp` adjustment, TX timestamp delivery and skipped-counter behavior under load, RX timestamp correctness near second rollover, reset/reinit preserving config, PTP interrupt enable failure paths, and debugfs/config query output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_ptp.h

## Purpose
`hclge_ptp.h` defines the PF PTP register map, software PTP state, command payloads, timestamp configuration bits, and exported PTP helper prototypes. It is shared by the PF main header and PTP implementation.

## Important Types And Constants
- Register offsets under `HCLGE_PTP_REG_OFFSET` cover TX timestamp sequence/nsec/sec registers, current/set time registers, adjust/sync registers, cycle quotient/numerator/denominator registers, and masks for nsec/seconds fields.
- `HCLGE_PTP_FLAG_EN`, `HCLGE_PTP_FLAG_TX_EN`, and `HCLGE_PTP_FLAG_RX_EN` are per-PTP mode flags.
- `struct hclge_ptp_cycle` stores hardware cycle quotient, numerator, and denominator used by frequency adjustment.
- `struct hclge_ptp` stores the PTP clock, outstanding TX skb, flags, PTP MMIO base, `ptp_clock_info`, cached `kernel_hwtstamp_config`, lock, cached hardware config, last sequence id, cycle values, and diagnostic counters.
- `struct hclge_ptp_int_cmd` and `struct hclge_ptp_cfg_cmd` define firmware command payloads for interrupt enable and mode configuration.
- Enums encode supported UDP PTP packet matching modes, PTP message type modes, and PTP v2 message subtype fields.
- `hclge_ptp_get_hdev()` maps a `ptp_clock_info` callback pointer back to `struct hclge_dev`.

## Control Flow And Integration
Callers use the declared functions to initialize/uninitialize PTP, set/get hardware timestamp config, provide TX timestamp skb state, attach RX timestamps, expose ethtool timestamp info, and query hardware config for diagnostics. The header depends on Linux PTP/net timestamp headers and forward-declares `struct hclge_dev` and `struct ifreq`.

## State And Risks
The state object contains both lifecycle-owned resources (`clock`, `tx_skb`) and live hardware configuration shadow (`flags`, `ts_cfg`, `ptp_cfg`, `cycle`). Changes to masks or offsets directly affect MMIO access correctness. The TX skb pointer requires careful lifecycle cleanup during uninit/reset. `spinlock_t lock` is documented as protecting PTP registers, so new paths touching multi-register time state should use it consistently.

## Test Signals
Build coverage verifies the ABI between `hclge_main.h`, `hclge_ptp.c`, and PF op tables. Runtime signals include PHC creation, timestamp mode changes, TX/RX timestamp counters, frequency and time adjustment behavior, reset reinitialization, and debug hardware config queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_regs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_regs.c

## Purpose
`hclge_regs.c` implements PF register dump support for ethtool/debug consumers. It calculates dump size, emits a TLV-framed register blob with a magic header, reads direct PF BAR registers, per-queue ring registers, TQP interrupt registers, firmware-reported 32-bit and 64-bit register groups, and DFX diagnostic register groups including per-tunnel RPU data.

## Important APIs And Functions
- `hclge_get_regs_len()` returns the byte length required for the complete PF register dump by querying firmware for 32/64-bit register counts and DFX BD counts, then adding direct BAR and TLV/header overhead.
- `hclge_get_regs()` fills the caller buffer, sets the firmware version, writes the header, emits PF direct registers, queried 32-bit/64-bit registers, and DFX groups.
- `hclge_query_bd_num_cmd_send()` sends the multi-descriptor `HCLGE_OPC_DFX_BD_NUM` query used by diagnostics and exported through the header.
- `hclge_get_32_bit_regs()` and `hclge_get_64_bit_regs()` send multi-BD query commands, account for leading non-data words, and copy little-endian descriptor data into host-endian output.
- `hclge_get_dfx_reg_bd_num()`, `hclge_get_dfx_reg_len()`, and `hclge_get_dfx_reg()` manage DFX group sizing and fetching across BIOS/common, SSU, IGU/EGU, RPU, NCSI, RTC, PPP, RCB, TQP, and SSU2 opcodes.
- `hclge_fetch_pf_reg()` reads static register address lists for command queue, common PF state, each TQP ring, and each used interrupt vector.

## Control Flow
Length computation first queries firmware for dynamic register counts. DFX length computation asks firmware how many BDs each diagnostic group requires, multiplies by descriptor data size, and adds TLV overhead, including one extra RPU group per tunnel id from device specs. Data dumping follows the same order: header, static PF TLVs, query-32 TLV, query-64 TLV, then DFX TLVs. Each TLV stores a tag and length before raw register values. On command failure, `hclge_get_regs()` logs and returns early because the ethtool callback is void.

## State And Persistence Behavior
No persistent driver state is mutated except the output buffer and returned version. The code reads live hardware MMIO and firmware command responses. It depends on current queue count (`kinfo->num_tqps`) and `hdev->num_msi_used`, so dump layout varies with runtime resource allocation. Output uses a fixed magic number representing `hns3regs` and `is_vf = 0` to identify PF dumps.

## Dependencies And Integration Points
The file depends on `hclge_cmd.h`, `hclge_main.h`, `hclge_regs.h`, common command/register definitions, queue `io_base` values from HNAE3 private info, firmware opcodes, and AE device specs (`tnl_num`). It is exposed through PF operation table hooks for ethtool register length and register dump callbacks.

## Risks And Edge Cases
- `hclge_get_regs()` cannot report errors directly after a partial fill, so consumers must tolerate short or partially populated dumps if commands fail.
- Length and data paths both query firmware; if register counts change between calls, caller buffer sizing could diverge.
- The code assumes descriptor data packing and non-data offsets for 32/64-bit queries; firmware format changes would corrupt parsing.
- `hdev->num_msi_used - 1` is used for TQP interrupt TLVs; zero or unexpected MSI accounting would underflow in length math if invariants break.
- DFX BD counts drive allocation sizes and loops; bad firmware values could cause large allocations or oversized dumps.

## Test Signals
Run `ethtool -d`/register dump paths on PFs with different queue/vector counts, device versions, and tunnel counts. Validate TLV parser alignment, magic header, PF/VF marker, dynamic size matching, command failure logging, allocation failure handling, endian correctness, and static register reads for all queues and vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_regs.h

## Purpose
`hclge_regs.h` declares the PF register-dump interface implemented in `hclge_regs.c`. It keeps the ethtool/debug register dump entry points visible without exposing the internal TLV tags, static address lists, or DFX parsing helpers.

## Important APIs
- `hclge_query_bd_num_cmd_send(struct hclge_dev *hdev, struct hclge_desc *desc)` issues the DFX BD-count command and is available for code that needs raw diagnostic sizing.
- `hclge_get_regs_len(struct hnae3_handle *handle)` computes the required dump buffer size.
- `hclge_get_regs(struct hnae3_handle *handle, u32 *version, void *data)` writes the live register dump.

## State, Dependencies, And Integration
The header includes Linux types and `hclge_comm_cmd.h` for descriptor definitions, forward-declares PF device and HNAE3 handle types, and integrates with the PF operation table. Callers are responsible for passing a buffer sized by `hclge_get_regs_len()`.

## Risks And Test Signals
The main risk is contract mismatch between the length and fill functions if firmware dynamic counts differ or callers ignore negative length errors. Build tests should catch signature drift; runtime tests should compare returned length against actual TLV traversal and confirm graceful behavior on command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.c

## Purpose
`hclge_tm.c` programs and queries HNS3 PF traffic management: priority-to-TC and DSCP-to-TC mapping, priority-group/priority/qset hierarchy, queue-to-qset and qset-to-priority mapping, shapers, DWRR weights, scheduler modes, flow control, MAC pause, PFC, qset backpressure, RSS/TC queue allocation updates, and debug getters for TM state.

## Important APIs And Functions
- `hclge_tm_schd_init()` initializes FC mode, validates scheduler mode constraints, initializes software scheduler state, initializes DSCP mapping defaults, and calls `hclge_tm_init_hw()`.
- `hclge_tm_init_hw()` validates TC-base or vNET-base scheduler mode, then runs `hclge_tm_schd_setup_hw()` and `hclge_pause_setup_hw()`.
- `hclge_tm_schd_setup_hw()` performs the hardware programming sequence: mapping, shapers, DWRR weights, scheduler modes, and TM flush disable.
- `hclge_shaper_para_calc()` converts Mbps rates into hardware IR_B/IR_U/IR_S parameters for port, PG, priority, or qset shapers.
- Mapping helpers include `hclge_up_to_tc_map()`, `hclge_dscp_to_tc_map()`, `hclge_tm_pg_to_pri_map()`, `hclge_tm_pri_q_qs_cfg()`, `hclge_vport_q_to_qs_map()`, and low-level command wrappers for PG-to-priority, qset-to-priority, and queue-to-qset links.
- Shaper and scheduler helpers configure port, PG, priority, VF/vNET, and qset shapers; DWRR weight helpers configure PG, priority, qset, and ETS TC weights.
- Flow-control helpers include `hclge_mac_pause_en_cfg()`, `hclge_pfc_pause_en_cfg()`, `hclge_pause_addr_cfg()`, `hclge_mac_pause_setup_hw()`, `hclge_pause_setup_hw()`, and `hclge_tm_bp_setup()`.
- Runtime update APIs include `hclge_tm_schd_info_update()`, `hclge_tm_prio_tc_info_update()`, `hclge_tm_pfc_info_update()`, `hclge_tm_vport_map_update()`, `hclge_tm_qs_shaper_cfg()`, and `hclge_reset_tc_config()`.
- Debug getters query qset/priority/PG/queue mapping, scheduler mode, weights, shaper parameters, node counts, and port shaper state from hardware.

## Control Flow
Software state is initialized first. `hclge_tm_pg_info_init()` creates one active priority group by default with full bandwidth; `hclge_tm_tc_info_init()` maps user priorities to TCs; `hclge_tm_vport_info_update()` recalculates PF/VF RSS size, queue counts, qset offsets, bandwidth, and per-TC queue offsets; `hclge_tm_pfc_info_update()` reconciles FC mode with PFC/DCB state.

Hardware setup then writes mappings and scheduler parameters in dependency order. User-priority and optional DSCP maps define TC selection. PG-to-priority, qset-to-priority, and queue-to-qset links build the hierarchy differently for TC-base and vNET-base modes. Port/PG/priority/qset shapers are calculated and written. DWRR weights and scheduler modes are programmed, with ETS TC weight command tolerated as unsupported on older firmware. Pause/PFC setup writes pause parameters and MAC pause bits, then DCB-capable devices get PFC and backpressure qset bitmaps.

## State And Persistence Behavior
The file mutates `hdev->tm_info`, `hdev->hw_tc_map`, `hdev->fc_mode_last_time`, PF RSS config, and each vport's `qs_offset`, `bw_limit`, `dwrr`, `kinfo.rss_size`, `kinfo.num_tqps`, and `kinfo.tc_info`. These are in-memory shadows of hardware scheduler state and must be replayed after resets. `hclge_reset_tc_config()` clears mqprio TC state, recomputes default scheduler state, and reinitializes RSS indirection. MAC/PFC packet stats are read from `hdev->mac_stats` offsets rather than command queries.

## Dependencies And Integration Points
The file depends on `hclge_cmd.h`, `hclge_main.h`, `hclge_tm.h`, HNAE3 queue/TC/private-info structures, firmware opcodes, DCB capability helpers, AE device specs (`max_tm_rate`), RSS common helpers, and PF MAC state. It integrates with ethtool/DCB/mqprio paths, PF/VF resource allocation, reset restore, pause/FEC/link handling, and debugfs diagnostics that call the getter functions.

## Risks And Edge Cases
- Shaper calculation rejects rates above firmware max and has several rounding paths; off-by-one errors can under/over-shape traffic.
- TC-base and vNET-base modes use different hierarchy semantics. Incorrect `tx_sch_mode`, `num_pg`, or qset offsets can map queues to the wrong scheduler node.
- VF handling deliberately limits VFs to one TC for simplicity; changing VF TC support would require broad updates.
- Backpressure bitmap programming depends on qset id bitfield layout and switches grouping when `num_tqps > HCLGE_TQP_MAX_SIZE_DEV_V2`.
- `hclge_tm_pri_vnet_base_shaper_qs_cfg()` currently calculates qset shaper parameters but does not send a qset shaper command in the visible code path; this may be intentional hardware behavior or a maintenance hazard.
- `hclge_pause_setup_hw()` suppresses PFC `-EOPNOTSUPP` only during init on GE MAC; later failures become hard errors.

## Test Signals
Validate default probe scheduler setup, mqprio create/destroy, DSCP mapping mode, DCB/PFC enable/disable, pause autoneg/manual modes, VF max TX rate/qset shaper changes, PF/VF queue allocation with multiple TCs, reset restore, GE MAC PFC unsupported path, large TQP backpressure grouping, debug getters matching programmed state, and traffic tests confirming TC/priority bandwidth behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.h

## Purpose
`hclge_tm.h` defines PF traffic-management command payloads, bitfields, defaults, shaper encoding helpers, and public TM APIs. It is the hardware command ABI companion to `hclge_tm.c`.

## Important Types And Constants
- MAC pause and scheduler constants define TX/RX pause enable bits, pause defaults, DWRR/SP masks, max Ethernet rate, legacy PF priority/qset counts, DSCP mapping descriptor count, and TM flush timing.
- Mapping command structs include PG-to-priority, qset-to-priority, queue-to-qset, queue-to-TC, and backpressure-to-qset mapping payloads. Qset id bitfields include an extended high-bit representation for qset ids at or above 1024.
- Weight and scheduler structs define PG, priority, qset, and ETS TC DWRR state plus priority/qset scheduler modes.
- Shaper structs define priority, PG, qset, and port shaper payloads with encoded IR/BS fields, valid flags, and rates. `hclge_tm_set_field()` and `hclge_tm_get_field()` wrap HNAE3 bitfield helpers for shaper encoding.
- Flow-control structs define PFC enable, pause parameter MAC/gap/time payloads, and PFC stats command layout.
- Public prototypes cover scheduler initialization/setup/update, pause/PFC config, PFC stats extraction, qset/port shapers, debug getters, mapping config, flush, and TC reset.

## Control Flow And Integration
Callers use the declared APIs from PF initialization, reset restore, DCB/mqprio configuration, ethtool pause/PFC paths, VF rate limiting, and debugfs. The header keeps the command-payload layout visible to implementation and diagnostic code while forward-declaring `struct hclge_dev` and `struct hclge_vport`.

## State And Risks
The header itself stores no state, but its structs must match firmware descriptor layouts exactly. Bitfield macros are central to qset id conversion and shaper parameter packing; drift from firmware definitions would cause silent misconfiguration. Public APIs assume callers pass valid TC/qset/priority ids and properly initialized `hclge_dev` TM state.

## Test Signals
Build and sparse checks catch layout/prototype drift. Runtime validation should include programming and reading back shapers, scheduler modes, weights, queue/qset mappings, PFC and MAC pause state, and TM flush support across device versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_trace.h

## Purpose
`hclge_trace.h` defines Linux tracepoints for HNS3 PF mailbox and command-queue activity. It provides structured observability for PF receiving VF mailbox requests, PF sending mailbox responses/notifications, and PF command descriptors sent to or received from firmware.

## Important Trace Events
- `hclge_pf_mbx_get` captures source VF id, mailbox code/subcode, PCI name, netdev name, and the raw VF-to-PF mailbox command as a u32 array.
- `hclge_pf_mbx_send` captures destination VF id, PF-to-VF mailbox code, PCI name, netdev name, and the raw PF-to-VF mailbox command.
- `hclge_pf_cmd_template` is a reusable event class for normal command descriptors, recording opcode, flag, retval, reserved field, descriptor index, descriptor count, PCI name, and descriptor data words.
- `hclge_pf_cmd_send` and `hclge_pf_cmd_get` instantiate the normal descriptor template.
- `hclge_pf_special_cmd_template` traces special command data as a descriptor-sized u32 array.
- `hclge_pf_special_cmd_send` and `hclge_pf_special_cmd_get` instantiate the special descriptor template.

## Control Flow And Integration
`hclge_mbx.c` defines `CREATE_TRACE_POINTS` before including this header, making it the tracepoint definition unit. Command code elsewhere can include the header and call the generated trace functions. The trace header sets `TRACE_SYSTEM hns3`, uses the standard include-guard plus `TRACE_HEADER_MULTI_READ` pattern, then sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE hclge_trace` before including `<trace/define_trace.h>`.

## State And Dependencies
The tracepoints read live `hclge_dev`, `hclge_comm_hw`, mailbox command, and command descriptor fields but do not mutate state. They depend on kernel tracepoint infrastructure, command/mailbox struct definitions being visible before use, PCI and netdev names being valid, and descriptor data lengths from common HNS3 headers.

## Risks And Edge Cases
- Raw mailbox and descriptor data may include sensitive or high-volume information; tracing should be enabled deliberately.
- `hdev->vport[0].nic.kinfo.netdev->name` is accessed in trace assignment; trace calls before netdev setup or after teardown would risk invalid pointers.
- Struct-size-derived array lengths couple trace ABI to command layout. Layout changes alter trace payload shape.

## Test Signals
Enable ftrace/perf trace events for `hns3:*` while exercising VF mailbox requests and firmware commands. Confirm event registration, field decoding, PCI/netdev names, raw arrays, and no crashes during probe/reset/remove with tracing enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_cmd.h

## Purpose
`hclgevf_cmd.h` defines VF-side command queue constants, command descriptor aliases, hardware register offsets, VF resource/query payloads, queue/vector mapping payloads, and exported command helpers for the HNS3 virtual-function driver.

## Important Types And Constants
- Command queue bits include RX invalid/out-valid bits, RX ring head sync enable, NIC reset-ready bit, default CMQ descriptor count, descriptor-count shift, and query-device-specs BD count.
- TQP register constants define VF TQP register offset/size, v2 maximum size, and extended register offset.
- `struct hclgevf_tqp_map` describes PF/VF task queue pair mapping with absolute TQP id, VF id, map type/enabled flag, and virtual id.
- `enum hclgevf_int_type` and `struct hclgevf_ctrl_vector_chain` encode vector-to-TX/RX/event cause mappings with up to ten TQP elements per command.
- `struct hclgevf_query_res_cmd` reports VF queue count, MSI-X bases, and VF interrupt vector count.
- GRO, link status, common TQP queue enable, TX queue pointer, and device specs command structs define firmware descriptor payloads.
- `hclgevf_cmd_setup_basic_desc()` aliases the common command descriptor setup helper.
- Exported functions are `hclgevf_cmd_send()` and `hclgevf_arq_init()`.

## Control Flow And Integration
The VF main implementation includes this header to send firmware/PF commands, initialize async receive queues, query resources and device specs, map interrupt vectors, enable queues, configure GRO, query link, and participate in reset readiness. VF mailbox code also relies on `hclgevf_cmd_send()` when exchanging descriptors with PF/firmware.

## State And Persistence Behavior
The header defines wire-format command state rather than owning runtime state. Values returned through these payloads populate VF device state in `hclgevf_main.c`, such as queue counts, interrupt vector counts, device limits, and link status. Reset readiness bits and queue enable commands affect hardware-visible VF state that must be restored after reset.

## Dependencies And Risks
The header depends on Linux IO/types, `hnae3.h`, and `hclge_comm_cmd.h`. Firmware layout compatibility is the dominant risk: bit positions, little-endian fields, descriptor counts, and structure padding must match hardware. The TQP id masks and vector element limit must be checked by callers before filling command payloads.

## Test Signals
Validate VF probe resource query, interrupt vector mapping, queue enable/disable, GRO configuration, link status query, reset readiness, device specs query over four BDs, and command timeout/error handling in `hclgevf_cmd_send()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_devlink.c

## Purpose
`hclgevf_devlink.c` provides devlink support for the HNS3 VF driver. It registers a devlink instance, reports running firmware version, and implements devlink reload with `DEVLINK_RELOAD_ACTION_DRIVER_REINIT` by driving the VF NIC client down/uninit and init/up notification sequence.

## Important APIs And Functions
- `hclgevf_devlink_info_get()` formats `hdev->fw_version` as four dotted bytes using HNAE3 firmware version masks and publishes it as `DEVLINK_INFO_VERSION_GENERIC_FW`.
- `hclgevf_devlink_reload_down()` rejects reload during reset handling, supports only `DRIVER_REINIT`, takes `rtnl_lock()`, sends `HNAE3_DOWN_CLIENT` then `HNAE3_UNINIT_CLIENT` reset notifications, and unwinds the lock on errors.
- `hclgevf_devlink_reload_up()` sets `*actions_performed = BIT(action)`, supports only `DRIVER_REINIT`, takes `rtnl_lock()`, sends `HNAE3_INIT_CLIENT` then `HNAE3_UP_CLIENT`, and returns unsupported for other actions.
- `hclgevf_devlink_ops` wires info and reload callbacks and advertises the reload action bit.
- `hclgevf_devlink_init()` allocates a devlink with private storage, stores `hdev`, saves the devlink pointer on the VF device, and registers it.
- `hclgevf_devlink_uninit()` unregisters and frees the devlink.

## Control Flow
VF probe calls `hclgevf_devlink_init()` after the VF device object and PCI device exist. Userspace `devlink dev info` calls `info_get`. Userspace reload calls first enter `reload_down`; if no reset is in progress and the action is driver reinit, the VF client is quiesced and uninitialized under RTNL. `reload_up` then initializes and brings the client up, also under RTNL. Remove calls `hclgevf_devlink_uninit()`.

## State And Persistence Behavior
The file stores the devlink pointer in `hdev->devlink` and stores a back pointer to `hdev` in `struct hclgevf_devlink_priv`. It does not persist config; reload operates through client reset-notify callbacks that tear down and rebuild VF NIC runtime state. Firmware version is read from cached `hdev->fw_version`.

## Dependencies And Integration Points
It depends on Linux devlink and RTNL APIs, `hclgevf_main.h` through the header, HNAE3 firmware version masks, VF reset state bit `HCLGEVF_STATE_RST_HANDLING`, `hdev->nic_client->ops->reset_notify`, and the VF probe/remove lifecycle in `hclgevf_main.c`.

## Risks And Edge Cases
- `reload_up()` sets `actions_performed` before action validation, so unsupported actions still briefly receive a bit assignment before returning `-EOPNOTSUPP`.
- Reload sequencing depends on NIC client callbacks being valid and correctly idempotent under RTNL.
- Reload during asynchronous reset is rejected, but races around reset state changes require broader VF reset synchronization.
- `devlink_register()` return value is not checked in this kernel API form; behavior depends on the API version used by the source tree.

## Test Signals
Run `devlink dev info` for VF firmware string formatting, `devlink dev reload action driver_reinit`, reload while reset is active, unsupported reload actions, VF traffic before/after reload, probe failure injection for `devlink_alloc`, and remove/unregister with devlink userspace watchers active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_devlink.h

## Purpose
`hclgevf_devlink.h` declares the VF devlink integration interface and private devlink storage for the HNS3 VF driver.

## Important APIs And Types
- `struct hclgevf_devlink_priv` holds the `struct hclgevf_dev *hdev` back pointer retrievable through `devlink_priv()`.
- `hclgevf_devlink_init(struct hclgevf_dev *hdev)` allocates/registers devlink state for a VF.
- `hclgevf_devlink_uninit(struct hclgevf_dev *hdev)` unregisters/frees devlink state.

## State, Dependencies, And Integration
The header includes `hclgevf_main.h` so it has the full VF device type. It is used by VF probe/remove code and by `hclgevf_devlink.c`. The private structure links devlink callbacks back to VF runtime state and cached firmware version.

## Risks And Test Signals
The header creates a direct include dependency on VF main definitions; include cycles or changing `struct hclgevf_dev` visibility could affect build ordering. Runtime validation should cover successful devlink init/uninit, probe allocation failure, and devlink callbacks using the expected private pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_devlink.h -->

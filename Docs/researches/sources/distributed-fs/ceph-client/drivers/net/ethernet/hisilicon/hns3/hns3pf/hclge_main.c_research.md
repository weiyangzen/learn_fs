# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_main.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004434`: lines 1-9370, `Docs/researches/chunks/subset-b-004434_research.md`
- `subset-b-004435`: lines 9371-12943, `Docs/researches/chunks/subset-b-004435_research.md`

## Chunk Research

### subset-b-004434: lines 1-9370

# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_main.c lines 1-9370

## Scope

This chunk covers the first 9370 lines of the HNS3 PF (`hclge`) ae-algorithm implementation. It includes module identity and PCI IDs, command queue wrappers, MAC/FEC/statistics plumbing, PF resource discovery, vport/TQP/MSI setup, MAC speed/autoneg/link handling, packet buffer allocation, reset and service-task orchestration, RSS/vector binding, promiscuous mode, flow director/aRFS/tc-flower rule management, loopback and start/stop paths, and the beginning of MAC/VLAN table management through `hclge_set_mac_addr()`'s declaration/body start. Later-line code in the same file completes VLAN, MTU, flow control, probe/uninit, client ops tables, and module registration.

## Purpose And Role

`hclge_main.c` is the PF control-plane core for Hisilicon HNS3 Ethernet devices. The code in this chunk translates kernel networking, ethtool, tc, SR-IOV, RoCE, reset, interrupt, and service-work requests into firmware command descriptors and BAR register operations. Its main responsibilities are:

- Query firmware/static config, derive device capabilities, and populate `hclge_dev`, `hclge_mac`, `hnae3_ae_dev->dev_specs`, and per-vport `hnae3_handle` fields.
- Allocate and map TQPs, MSI/MSI-X vectors, vports, buffer waterlines, and optional RoCE handle metadata.
- Maintain shadow state for MAC address tables, flow-director rules, RSS config, link/FEC/autoneg settings, reset state, and per-vport liveness so hardware can be replayed after reset.
- Drive asynchronous work from a shared service workqueue: mailbox handling, reset, hardware error recovery, PTP cleanup, link/statistics/FD/MAC/VLAN periodic sync.
- Expose implementation functions used by `hnae3` NIC/RoCE clients and other hclge units (`hclge_mbx`, `hclge_err`, `hclge_tm`, `hclge_ptp`, VLAN code later in the file).

## Important Data And Constants

- `HCLGE_NAME`, `ae_algo_pci_tbl`, `hclge_wq`, and `ae_algo` define driver identity and integration with the hnae3 ae-algorithm framework.
- `g_mac_stats_string` maps ethtool statistic strings to `struct hclge_mac_stats` offsets and firmware statistic-version gates. `hclge_comm_get_count()`, `hclge_comm_get_strings()`, and `hclge_comm_get_stats()` use it to expose only supported counters.
- `meta_data_key_info` and `tuple_key_info` describe the hardware flow-director TCAM key layout. The tuple entries include bit widths, endian conversion mode, and offsets into `struct hclge_fd_rule` and its mask.
- `speed_bit_map` plus SR/LR/CR/KR link-mode maps translate firmware/HCLGE speed ability bits to ethtool link mode bitmaps.
- `hclge_mgr_table` seeds the MAC ethertype manager table, currently with an LLDP multicast entry.
- State bitmaps matter throughout: `hdev->state` (`HCLGE_STATE_*`), `vport->state` (`HCLGE_VPORT_STATE_*`), `hdev->reset_pending`, `hdev->reset_request`, `hdev->default_reset_request`, `hdev->fd_bmap`, and `hdev->vport_config_block`.

## Command And Statistics APIs

- `hclge_cmd_send()` is the PF wrapper over `hclge_comm_cmd_send()`. Trace callbacks `hclge_trace_cmd_send()` and `hclge_trace_cmd_get()` are registered through `hclge_cmq_ops` and emit normal vs special command descriptors.
- MAC stats support two firmware paths: `hclge_mac_update_stats_defective()` uses legacy fixed 21 descriptors for partial stats, while `hclge_mac_update_stats_complete()` sizes the descriptor array from `dev_specs.mac_stats_num`. Both accumulate counters into `hdev->mac_stats`.
- `hclge_mac_query_reg_num()` and `hclge_query_mac_stats_num()` discover stats register count, with compatibility fallback for V2 and older firmware behavior.
- `hclge_update_stats_for_all()` refreshes PF TQP, FEC, and MAC stats from periodic service; `hclge_update_stats()` is the handle-level path with `HCLGE_STATE_STATISTICS_UPDATING` serialization.
- `hclge_get_sset_count()`, `hclge_get_strings()`, `hclge_get_stats()`, `hclge_get_mac_stat()`, `hclge_get_fec_stats()`, and helpers provide ethtool-facing statistic/test/FEC data.

## Configuration And Resource Discovery

- `hclge_query_function_status()` polls `HCLGE_OPC_QUERY_FUNC_STATUS`, validates `HCLGE_PF_STATE_DONE`, sets main-PF flag, and stores MAC ID.
- `hclge_query_pf_resource()` reads TQP count, packet/TX/DV buffer sizes, NIC/RoCE MSI counts, and validates at least `HNAE3_MIN_VECTOR_NUM` NIC vectors.
- `hclge_get_cfg()` issues multi-descriptor `HCLGE_OPC_GET_CFG_PARAM`; `hclge_parse_cfg()` extracts TC count, descriptor count, PHY/media/RX buffer, default MAC, speed ability, VLAN filter capability, UMV space, PF/VF RSS limits, and TX spare buffer size.
- `hclge_query_dev_specs()` initializes default device specs for older devices and queries firmware specs for V3+, including RSS table/key sizes, interrupt moderation bounds, max frame size, UMV, multicast MAC table size, tunnel count, and hilink version.
- `hclge_configure()` applies queried config into `hdev`, including MAC defaults, RSS limits, TC/DCB defaults, FD enablement, default speed/duplex/autoneg, supported link modes, max speed, kdump resource reduction, and VLAN filter capability flags.

## TQP, Vport, MSI, And Buffer Setup

- `hclge_alloc_tqps()` allocates `hdev->htqp`, initializes each queue's descriptor counts, IO base, optional TX push memory base, and ae algorithm pointer.
- `hclge_alloc_vport()` creates PF plus requested VF vports, initializes per-vport MAC/VLAN lists, locks, default MPS, VLAN offload/filter defaults, and calls `hclge_vport_setup()`/`hclge_knic_setup()` to allocate per-handle queue pointer arrays.
- `hclge_assign_tqp()` assigns free hardware queues to a vport and derives `kinfo->rss_size` from PF RSS size, TC count, and available NIC MSI vectors.
- `hclge_map_tqp()` programs `HCLGE_OPC_SET_TQP_MAP` for all vports using physical TQP index, virtual index, and PF/VF type.
- `hclge_init_msi()` allocates MSI/MSI-X vectors, tracks `num_msi_left/used`, and initializes `vector_status`/`vector_irq`; `hclge_get_misc_vector()` reserves vector 0 for miscellaneous events.
- `hclge_buffer_alloc()` calculates and programs TX buffers, RX private buffers, shared buffer size, private waterlines, common thresholds, and common waterlines. The RX algorithm first tries full private/shared allocation, then reduced waterlines, then drops non-PFC and PFC private buffers, with a DCB-only private-buffer fallback.
- `hclge_init_roce_base_info()` initializes RoCE handle metadata when RoCE is supported: vector base after NIC vectors, netdev pointer, IO/memory bases, PCI device, ae algorithm, and NUMA mask.

## MAC, Link, FEC, And Port Control

- Speed conversion flows through `hclge_parse_speed()`, `hclge_get_speed_bit()`, `hclge_check_port_speed()`, `hclge_convert_to_fw_speed()`, `hclge_cfg_mac_speed_dup_hw()`, and `hclge_cfg_mac_speed_dup()`. Speeds above 100M force full duplex.
- `hclge_parse_link_mode()` selects fiber, copper, or backplane support mapping. FEC ability may be firmware-reported or inferred from speed by `hclge_convert_setting_fec()`.
- Autoneg APIs include `hclge_set_autoneg_en()`, `hclge_set_autoneg()`, `hclge_get_autoneg()`, `hclge_restart_autoneg()`, and `hclge_halt_autoneg()`.
- FEC APIs include `hclge_update_fec_stats_hw()`, lane parsing, total/lane ethtool conversion, `hclge_set_fec_hw()`, `hclge_set_fec()`, and `hclge_get_fec()`.
- `hclge_mac_init()` re-applies autoneg, forced speed, user FEC, MTU/MPS, default loopback, and buffer allocation. It resets link state and enables SFP querying.
- `hclge_get_mac_phy_link()` combines PHY state and firmware link query. `hclge_update_link_status()` serializes via `HCLGE_STATE_LINK_UPDATING`, updates port info on link-up, notifies NIC and RoCE clients, configures MAC tunnel interrupt state, and pushes link state to live VFs in auto mode.
- `hclge_get_sfp_info()` and `hclge_update_port_info()` update module type, lane count, speed ability, active FEC, autoneg, advertised/supported modes, port shaper, and forced speed for fiber/backplane. Copper ports use PHY IMP link ksettings helpers.

## Interrupt, Service, And Reset Control Flow

- Misc vector interrupt handling starts in `hclge_misc_irq_handle()`: disable vector, classify cause via `hclge_check_event_cause()`, schedule error/reset/mailbox service or clean PTP TX timestamp state, clear the relevant interrupt source, and re-enable only for non-reset/non-error events.
- `hclge_service_task()` runs error handling, reset handling, PTP cleanup, mailbox handling, and periodic work, then reruns error/reset/mailbox paths because periodic work can delay or reschedule work.
- `hclge_periodic_service_task()` updates link, MAC table, promiscuous mode, and FD table every pass; once per second it updates VF liveness, stats at interval, port info, VLAN filter sync, and aRFS expiration.
- Reset orchestration is split into scheduling (`hclge_reset_task_schedule()`), priority selection (`hclge_get_reset_level()`), request assertion (`hclge_do_reset()`), prepare/wait/rebuild (`hclge_reset_prepare()`, `hclge_reset_wait()`, `hclge_reset_rebuild()`), and failure retry (`hclge_reset_err_handle()`).
- Reset priorities are IMP > global > function > FLR. Lower-priority requests are cleared when a higher-priority reset is selected.
- PF/FLR reset preparation notifies VFs through mailbox, sets VF reset state in firmware, waits for all VFs ready if firmware supports it, notifies NIC/RoCE clients down/uninit/up/init through hnae3 client ops, disables command queue use around reset, and replays the ae device through `hclge_reset_ae_dev()` (implemented later in the file).
- Hardware error recovery is delegated to `hclge_err` helpers. Depending on RAS IMP support, the code finds/logs errors, handles MAC tunnel/VF queue errors, or services misc MSIX/RAS status, then requests the reset level demanded by hardware errors.

## RSS, Vectors, Rings, And Promiscuous Mode

- `hclge_get_vector()` allocates client vectors from NIC vectors excluding vector 0; `hclge_put_vector()` frees by IRQ lookup; `hclge_get_vector_info()` returns IRQ and BAR interrupt-control address, including extended vector register addressing for indexes beyond V2 limits.
- RSS state is stored in `hdev->rss_cfg`. `hclge_get_rss()`, `hclge_set_rss()`, `hclge_set_rss_tuple()`, `hclge_get_rss_tuple()`, `hclge_init_rss_tc_mode()`, and `hclge_rss_init_hw()` program hash key, algorithm, tuple selection, indirection table, and per-TC queue offset/size.
- `hclge_bind_ring_with_vector()` maps or unmaps ring chains to an interrupt vector with one or more `HCLGE_OPC_ADD_RING_TO_VECTOR`/`DEL_RING_TO_VECTOR` commands. It encodes ring type, TQP index, and GL index.
- `hclge_cmd_set_promisc_mode()` programs per-vport unicast/multicast/broadcast RX/TX promiscuous bits. It handles older V1/V2 compatibility fields and suppresses UC TX promiscuous when `HNAE3_PFLAG_LIMIT_PROMISC` is set.
- `hclge_request_update_promisc_mode()` only marks vport state; `hclge_sync_promisc_mode()` is declared in this chunk and implemented later, then called from periodic service.

## Flow Director, aRFS, And tc Flower

- `hclge_init_fd_config()` queries FD mode and allocation, chooses max key length, initializes stage-1 tuple/meta key selection, enables IPv6 low words, conditionally enables MAC and user-defined tuples, and programs key config.
- Shadow state includes `hdev->fd_rule_list`, `fd_bmap`, `hclge_fd_rule_num`, `fd_active_type`, user-defined offset refcounts, and rule states (`TO_ADD`, `ACTIVE`, `TO_DEL`, `DELETED`).
- `hclge_fd_config_rule()` writes action data first (`hclge_config_action()`/`hclge_fd_ad_config()`) then TCAM key data (`hclge_config_key()`/`hclge_fd_tcam_config()`). TCAM keys are split into X/Y data from tuple values and masks; metadata encodes NIC packet type and destination vport.
- Etntuple paths: `hclge_fd_check_spec()` validates flow type, location, VLAN/MAC/user-def extension support, masks, and tuple availability. `hclge_fd_get_tuple()` converts ethtool IPv4/IPv6/TCP/UDP/SCTP/user-IP/ether fields and masks into `hclge_fd_rule`. `hclge_add_fd_entry()` and `hclge_del_fd_entry()` expose add/delete.
- aRFS paths: `hclge_add_fd_entry_by_arfs()` accepts `flow_keys`, refuses operation when user/flower FD rules are active, deduplicates by tuple, assigns first free bit, and schedules deferred hardware programming. `hclge_rfs_filter_expire()` asks RFS whether active flows may expire and marks them `TO_DEL`.
- tc flower paths: `hclge_parse_cls_flower()` supports basic, MAC, VLAN, IPv4/IPv6 address, and port dissector keys only. `hclge_add_cls_flower()` maps priority to hardware location and selects a TC action; `hclge_del_cls_flower()` deletes by cookie.
- Mode mixing is restricted: `hclge_add_fd_entry_common()` rejects user ntuple or flower additions when the other explicit rule type is active; aRFS is cleared before explicit user rules are installed.
- Deferred persistence: `hclge_restore_fd_entries()` turns active rules back to `TO_ADD` after reset; `hclge_sync_fd_table()` handles clear-all, user-def config replay, and list add/delete retries from periodic work.

## Loopback, Start/Stop, And Vport Lifecycle

- Loopback support includes app MAC loopback, serial/parallel SerDes loopback through common loopback commands, PHY loopback via phylib or firmware common loopback, and external no-op handling. `hclge_get_sset_count()` exposes only supported ethtool tests.
- `hclge_set_loopback()` optionally adjusts SSU loopback switch behavior for V2+, configures selected loopback, waits for link status where needed, and enables/disables TQPs to match loopback state.
- `hclge_ae_start()` enables MAC mode, clears DOWN, resets TQP stats, and starts PHY. `hclge_ae_stop()` sets DOWN, clears aRFS rules, handles reset-specific PFC/PHY cases, resets TQPs, disables MAC tunnel interrupt, disables MAC mode, stops PHY, resets stats, and updates link.
- `hclge_vport_start()` marks vport initialized/alive, sets promisc-change, records heartbeat, clears notifications, and restores MAC/VLAN tables if the vport was blocked during reset. `hclge_vport_stop()` clears init/alive and pending notifications.

## MAC/VLAN Table And UMV State

- Hardware MAC/VLAN table access uses `hclge_prepare_mac_addr()`, `hclge_lookup_mac_vlan_tbl()`, `hclge_add_mac_vlan_tbl()`, `hclge_remove_mac_vlan_tbl()`, and status decoding in `hclge_get_mac_vlan_cmd_status()`.
- UMV space is allocated by `hclge_init_umv_space()` through `HCLGE_OPC_MAC_VLAN_ALLOCATE`. The allocation is split into private per-vport quota and shared spillover (`priv_umv_size`, `share_umv_size`), with `used_umv_num` per vport and `used_mc_mac_num` globally.
- `hclge_add_uc_addr_common()` validates unicast addresses, looks up duplicates, consumes UMV quota on new hardware entries, and reports overflow. `hclge_rm_uc_addr_common()` removes and frees UMV accounting even when hardware says the entry is already absent.
- `hclge_add_mc_addr_common()` and `hclge_rm_mc_addr_common()` manage multicast entries as shared entries with VFID bitmaps spanning descriptors. `hclge_update_desc_vfid()` sets/clears function bits; `hclge_is_all_function_id_zero()` decides when the shared multicast entry can be deleted.
- Software MAC lists (`uc_mac_list`, `mc_mac_list`) hold `hclge_mac_node` entries in `TO_ADD`, `ACTIVE`, or `TO_DEL` states. User/client changes enqueue list state through `hclge_update_mac_list()`; periodic service calls `hclge_sync_mac_table()` to delete first, add second, merge temporary add/delete lists, and retry failures.
- Overflow flags (`HNAE3_OVERFLOW_UPE/MPE`) are updated from sync success and UMV fullness. These flags interact with promiscuous fallback paths implemented later in the file.
- Reset/uninit paths use `hclge_rm_vport_all_mac_table()`, `hclge_uninit_mac_table()`, and `hclge_update_mac_node_for_dev_addr()` to preserve or remove shadow entries depending on whether the list is being deleted permanently or temporarily blocked for later restore.
- `init_mgr_tbl()` programs the manager ethertype table from `hclge_mgr_table`; `hclge_get_mac_addr()` returns the PF default MAC. The chunk ends inside the beginning of `hclge_set_mac_addr()`, so validation and hardware/list update completion are cross-chunk.

## Dependencies And Integration Points

- Kernel subsystems: PCI/MSI-X, netdevice/ethtool, rtnetlink, phylib, tc flower/flow dissector, RFS acceleration, workqueues/timers, interrupts, devm memory, bitmaps, spinlocks/mutex/semaphore, and module/pci ID infrastructure.
- HNS3 common modules: `hclge_comm_cmd`, `hclge_comm_rss`, `hclge_comm_tqp_stats`, `hclge_cmd`, `hclge_tm`, `hclge_mbx`, `hclge_err`, `hclge_ptp`, `hclge_dcb`, `hclge_mdio`, `hclge_regs`, and `hclge_devlink`.
- hnae3 framework: `hnae3_ae_dev`, `hnae3_handle`, `hnae3_client`, reset notifications, RoCE/NIC client type distinction, client callbacks for link status, reset, hardware error processing, vector/ring/RSS/offload APIs.
- Firmware command interface: many paths depend on opcodes such as stats, config, PF resource, TQP map, buffer allocation, MAC/FEC/autoneg/link/SFP, PHY link ksettings, FD key/TCAM/action/user-def, common loopback, MAC/VLAN table, UMV allocation, reset, and PF reset done.
- Hardware BAR registers: reset/global/function state, misc vector interrupt status, CMDQ source, PF other interrupt, vector control, TQP register windows, and command queue handshake registers.

## State And Persistence Behavior

- Most hardware state is shadowed in RAM and replayed after reset rather than persisted externally. Key replay stores are MAC lists, FD rules, RSS config, MAC request speed/autoneg/duplex/FEC, VLAN state implemented later, and vport block bits.
- Reset clears or disables command usage, notifies clients down/uninit, waits for hardware and VFs, reinitializes the ae device, clears interrupt causes, restores clients, and marks active FD rules for replay.
- Service-task state bits are used as coarse-grained latches. `test_and_set_bit()` prevents concurrent stats, FEC, link, mailbox, and reset handling; failure paths often restore the bit so periodic service retries.
- MAC list sync intentionally moves entries to temporary lists so firmware commands can run outside `mac_list_lock`, then reconciles races from concurrent add/delete requests.
- Flow-director user-defined field offsets are globally constrained per layer and tracked with refcounts. Hardware user-def config is only reprogrammed when refcounts/offsets change.
- UMV quota accounting is in memory and reset by `hclge_reset_umv_space()` later in the file after hardware reset; MAC table restore repopulates the hardware accounting.

## Risks And Edge Cases

- Firmware compatibility branches are frequent (`-EOPNOTSUPP`, V1/V2/V3 checks, old PF reset done command, old SFP speed-only query). Regressions can break older boards even when newer firmware works.
- Reset ordering is delicate: command queue disable, VF notification, mailbox drain, client down/up notifications, rtnl locking, and handshake bits must remain ordered or VFs/NIC/RoCE can race hardware reset.
- MAC/FD list handling relies on lock discipline and temporary list reconciliation. Bugs can leak nodes, double-account UMV/FD bitmap entries, or lose a requested MAC/FD rule during add/delete races.
- `hclge_fd_convert_tuple()` reads rule fields using byte offsets and casts to `u16`/`u32`; tuple metadata must stay aligned with `struct hclge_fd_rule` layout and endian expectations.
- Flow-director mode conflicts are intentional. Feature changes must preserve mutual exclusion among aRFS, ethtool ntuple, and tc flower or define a new conflict policy.
- Buffer allocation depends on packet buffer size, MPS, DCB/PFC map, DV buffer, and TC count. Incorrect rounding or threshold math can produce firmware-rejected waterlines or packet loss under pause/PFC.
- Vector accounting is manual (`num_msi_left/used`, `vector_status`, `vector_irq`); bad error unwinding can leak vectors or allow duplicate allocation.
- The code uses several busy/wait loops in reset, link, loopback, and flush paths. Timeout changes affect boot/reset latency and reliability.

## Test Signals

- Build coverage: kernel compile for HNS3 PF with `CONFIG_HNS3`, SR-IOV, PTP, DCB, RFS, and tc flower relevant configs catches API drift in ethtool/tc/phylib/hnae3 interfaces.
- Probe/init smoke: device probe should query function/PF resources, allocate MSI vectors, vports, TQPs, UMV, buffers, initialize FD/RSS/MAC, request misc IRQ, and register NIC/RoCE clients without errors.
- Etntuple/tc/aRFS tests: add/delete/list IPv4, IPv6, TCP/UDP/SCTP, ether, VLAN, FLOW_MAC_EXT, user-def offsets, drop/direct queue/select TC actions; verify conflict rejection and reset replay.
- Reset tests: trigger function, FLR, global, and IMP reset; verify client notifications, VF reset sync, command queue disable/enable, MAC/VLAN/FD/RSS restore, link notification, and reset statistics.
- SR-IOV tests: create VFs, set VF MAC/link state, heartbeat timeout, push link status, VF reset during PF reset, and multicast VFID bitmap add/remove.
- MAC table stress: fill UC/MC table to UMV and mc table limits, verify overflow flags/promiscuous fallback, duplicate handling, delete retries, and restore after reset.
- Link/FEC/autoneg tests: SFP and copper paths, unsupported firmware query fallback, forced speed/duplex, autoneg halt/restart, FEC mode/statistics, port shaper update on speed change.
- Loopback tests: app, serial/parallel SerDes, PHY, and external ethtool self-tests with expected TQP enable/disable and link wait behavior.
- Error/interrupt tests: inject misc MSIX/RAS/CMDQ/IMP reset/PTP events and verify correct work scheduling, interrupt re-enable policy, and error-to-reset escalation.

## Cross-Chunk References

- `hclge_set_mac_addr()` starts at the chunk boundary and is completed after line 9370.
- Forward-declared or called functions implemented later include VLAN filter/config sync, MTU handling, VLAN restore, flow control, device init/uninit/reset entrypoints, promisc sync, final client ops registration, PCI/module init, and final `hclge_reset_ae_dev()`.
- The final per-file report should reconcile this chunk with later chunks to describe complete probe/remove/client ops and VLAN/MTU/control-plane behavior.

### subset-b-004435: lines 9371-12943

# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_main.c lines 9371-12943

## Scope and Purpose

This chunk covers the late PF-side implementation of the HNS3 `hclge_main.c` driver. It starts inside `hclge_set_mac_addr()` and runs through module registration. The code in this range supplies many of the `hnae3_ae_ops` callbacks used by the NIC, ethtool, SR-IOV, reset, VLAN, MTU, queue reset, Wake-on-LAN, EEPROM, RSS channel, and client lifecycle paths.

The dominant responsibilities in this span are:

- MAC address programming handoff and MII ioctl routing.
- VLAN filter, VF VLAN, port-base VLAN, VLAN offload, and VLAN restore/sync state.
- Hardware table restore after reset for MAC, VLAN, and flow director entries.
- MTU and queue reset commands.
- Pause/frame flow control and link/media helper callbacks.
- NIC/RoCE client instance initialization and teardown.
- PCI, command queue, interrupt, TQP, vport, MAC, VLAN, TM, RSS, FD, PTP, WOL, devlink, and service task initialization/teardown.
- PF/global reset rebuild and state reinitialization.
- VF administrative controls: spoof checking, trust, rate limiting, VLAN cleanup, and SR-IOV disable cleanup.
- Runtime ethtool-style helpers for channels, LEDs, link modes, GRO, SFP EEPROM, link diagnosis, DSCP priority, WOL, PTP timestamping, and hardware stats.
- Final assembly of the `hnae3_ae_ops` table and module init/exit registration.

This is not a self-contained file view: many helpers, data structures, and constants are declared earlier in `hclge_main.c`, companion HNS3 files, and common HNAE3/HCLGE headers. The chunk is nevertheless the integration surface that wires those helpers into the NIC framework.

## Important APIs, Types, and Data

Key local objects and state:

- `struct hclge_dev`: PF device state. This chunk updates `state`, `reset_type`, `reset_level`, `reset_pending`, `rst_stats`, `mps`, `vlan_table`, `vf_vlan_full`, `vport_config_block`, `tm_info.fc_mode`, `fc_mode_last_time`, `gro_en`, `hw.mac.*`, `rss_cfg`, `misc_vector`, `reset_timer`, `service_task`, and client pointers.
- `struct hclge_vport`: PF/VF vport state. This chunk uses `vport_id`, `nic`, `roce`, `back`, `state`, `need_notify`, `vf_info`, `port_base_vlan_cfg`, `txvlan_cfg`, `rxvlan_cfg`, `vlan_list`, `vlan_del_fail_bmap`, `mps`, `alloc_tqps`, `last_promisc_flags`, and `overflow_promisc_flags`.
- `struct hnae3_handle`: callback-facing handle used by NIC, ethtool, and upper HNAE3 layers. Most callbacks convert this to `hclge_vport` via `hclge_get_vport()`.
- `struct hnae3_ae_dev`: bus/device integration object. This chunk uses `pdev`, `priv`, `caps`, `dev_version`, `dev_specs`, and reset/error-request state.
- Firmware command descriptor structs such as `hclge_vlan_filter_ctrl_cmd`, `hclge_vlan_filter_vf_cfg_cmd`, `hclge_vlan_filter_pf_cfg_cmd`, `hclge_vport_vtag_tx_cfg_cmd`, `hclge_vport_vtag_rx_cfg_cmd`, `hclge_reset_tqp_queue_cmd`, `hclge_reset_cmd`, `hclge_query_wol_supported_cmd`, `hclge_wol_cfg_cmd`, `hclge_set_led_state_cmd`, and SFP EEPROM descriptor payloads.
- Bitmaps and lists are persistent in-memory mirrors of firmware state: `hdev->vlan_table[vlan_id]` tracks which vports use a VLAN, `hdev->vf_vlan_full` tracks firmware VF VLAN table exhaustion, `vport->vlan_list` tracks VLANs requested by the stack, and `vport->vlan_del_fail_bmap` tracks delete operations deferred during reset or firmware failure.

Primary exported or callback-visible functions in this chunk:

- MAC/ioctl: `hclge_set_mac_addr()`, `hclge_do_ioctl()`.
- VLAN/filter/offload: `hclge_enable_vport_vlan_filter()`, `hclge_en_hw_strip_rxvtag()`, `hclge_update_port_base_vlan_cfg()`, `hclge_set_vlan_filter()`, `hclge_set_vf_vlan_filter()`, `hclge_rm_vport_all_vlan_table()`, `hclge_uninit_vport_vlan_table()`, `hclge_restore_vport_port_base_vlan_config()`, `hclge_restore_vport_vlan_table()`.
- Reset/restore: `hclge_restore_mac_table_common()`, `hclge_reset_tqp()`, `hclge_reset_prepare_general()`, `hclge_reset_done()`, `hclge_reset_ae_dev()`, `hclge_uninit_ae_dev()`.
- Flow/link/ethtool: `hclge_cfg_flowctrl()`, `hclge_get_pauseparam()`, `hclge_set_pauseparam()`, `hclge_get_ksettings_an_result()`, `hclge_get_media_type()`, `hclge_get_mdix_mode()`, `hclge_get_fw_version()`, `hclge_query_scc_version()`, `hclge_get_channels()`, `hclge_set_channels()`, `hclge_set_led_id()`, `hclge_get_link_mode()`, `hclge_gro_en()`, `hclge_get_module_eeprom()`, `hclge_get_link_diagnosis_info()`, `hclge_get_dscp_prio()`.
- Client/device lifecycle: `hclge_init_client_instance()`, `hclge_uninit_client_instance()`, `hclge_init_ae_dev()`, `hclge_init()`, `hclge_exit()`.
- VF controls: `hclge_set_vf_spoofchk()`, `hclge_set_vf_trust()`, `hclge_set_vf_rate()`, `hclge_clean_vport_config()`.
- WOL: `hclge_get_wol()`, `hclge_set_wol()`.

The chunk concludes with `static const struct hnae3_ae_ops hclge_ops`, `static struct hnae3_ae_algo ae_algo`, and `module_init()`/`module_exit()` hooks.

## MAC Address and MII IOCTL Flow

`hclge_set_mac_addr()` validates the new unicast MAC, programs the pause frame address through `hclge_pause_addr_cfg()`, updates the vport unicast MAC list under `mac_list_lock`, and copies the new address into `hdev->hw.mac.mac_addr` while still holding that lock. The lock is intentionally held across the device-address update so the set-RX-mode path cannot remove the address concurrently. On failure after changing the pause address, non-initial calls try to restore the old pause address.

`hclge_do_ioctl()` routes MII ioctls either through a PHY device (`phy_mii_ioctl()`) or the firmware-backed implementation path (`hclge_mii_ioctl()`) when no `phydev` exists and the device supports PHY implementation commands. `hclge_mii_ioctl()` supports `SIOCGMIIPHY`, `SIOCGMIIREG`, and `SIOCSMIIREG`; all other commands return `-EOPNOTSUPP`.

## VLAN Filter and VLAN Offload Behavior

The VLAN logic has several layers:

- Firmware control toggles: `hclge_set_vlan_filter_ctrl()` reads the current VLAN filter config, adjusts feature bits, and writes it back. `hclge_set_port_vlan_filter_bypass()` is used on devices with port VLAN bypass support.
- Vport filter policy: `hclge_need_enable_vport_vlan_filter()` decides whether a vport's VLAN filtering should be enabled based on port-base VLAN state, trusted VF promiscuous requests, PF user promiscuous mode, requested filter enable, hardware capability bits, and whether nonzero VLAN entries exist in the vport VLAN list.
- State transition: `__hclge_enable_vport_vlan_filter()` compares the computed need against `cur_vlan_fltr_en`, applies hardware changes only when needed, and updates `cur_vlan_fltr_en`. `hclge_enable_vport_vlan_filter()` wraps this under `hdev->vport_lock` while recording `req_vlan_fltr_en`.
- VF-specific table programming: `hclge_set_vf_vlan_filter_cmd()` builds a two-descriptor command with a VF bitmap. `hclge_check_vf_vlan_cmd_status()` treats normal success and some benign missing-entry responses as success, marks `hdev->vf_vlan_full` when firmware reports a full VF VLAN table, and returns `-EIO` for unexpected firmware response codes.
- PF/port VLAN programming: `hclge_set_port_vlan_filter()` computes the VLAN offset bitmap for `HCLGE_OPC_VLAN_FILTER_PF_CFG`. `hclge_need_update_port_vlan()` maintains the in-memory `hdev->vlan_table[vlan_id]` vport bitmap and avoids duplicate add/delete hardware operations.
- Combined hardware update: `hclge_set_vlan_filter_hw()` validates VLAN ID, programs the per-VF table via `hclge_set_vf_vlan_common()`, updates the port-level VLAN table only when the first vport adds or last vport removes the VLAN, and ignores VLAN 0 delete operations.

VLAN TX/RX offload state is stored in `vport->txvlan_cfg` and `vport->rxvlan_cfg`, then pushed through `hclge_set_vlan_tx_offload_cfg()` and `hclge_set_vlan_rx_offload_cfg()`. `hclge_vlan_offload_cfg()` derives these settings from the port-base VLAN state, default VLAN tag/QoS, device generation, and the requested RX VLAN strip state. Port-base VLAN enabled mode causes TX insertion of tag1 and RX stripping/discard behavior to change; disabled mode accepts normal tagged traffic and uses tag2 stripping according to `rx_vlan_offload_en`.

Initialization uses `hclge_init_vlan_config()`:

1. Initialize VF and port VLAN filter state with `hclge_init_vlan_filter()`.
2. Program VLAN protocol types to 802.1Q via `hclge_init_vlan_type()`.
3. Initialize per-vport VLAN offload config.
4. Add VLAN 0 to the PF VLAN filter path.

The code keeps requested VLANs in `vport->vlan_list` using `hclge_add_vport_vlan_table()`, `hclge_add_vport_all_vlan_table()`, `hclge_rm_vport_vlan_table()`, and `hclge_rm_vport_all_vlan_table()`. The `hd_tbl_status` flag records whether a list entry is currently written to hardware. This matters when port-base VLAN is active: user VLAN requests are remembered but not necessarily written to firmware until port-base VLAN is disabled.

## Port-Base VLAN and VF VLAN Control

`hclge_set_vf_vlan_filter()` is the PF-facing callback for configuring a VF's port-base VLAN. It rejects unsupported device versions, invalid VF IDs, VLAN IDs beyond `VLAN_N_VID - 1`, QoS values above 7, and protocols other than 802.1Q. It computes whether the request is no-op, enable, disable, or modify via `hclge_get_port_base_vlan_state()`, then applies it with `hclge_update_port_base_vlan_cfg()`.

`hclge_update_port_base_vlan_cfg()` first updates VLAN offload state. If the VLAN filter entry must change, it either modifies an existing port-base VLAN tag with `hclge_modify_port_base_vlan_tag()` or switches between enabled/disabled entry sets with `hclge_update_vlan_filter_entries()`. Enabling port-base VLAN removes all normal vport VLAN entries from hardware, force-deletes VLAN 0 in the VF table, and adds the new base VLAN. Disabling port-base VLAN force-adds VLAN 0, removes the old base VLAN, and restores all recorded normal VLANs. It then updates `port_base_vlan_cfg.state`, the exposed handle state, old/current VLAN info, `tbl_sta`, and the vport VLAN filter change bit.

For pre-version-3 devices, `hclge_set_vf_vlan_filter()` pushes the port-base VLAN state to a live VF with `hclge_push_vf_port_base_vlan_info()` or records `HCLGE_VPORT_NEED_NOTIFY_VF_VLAN` when the VF is not alive. This makes VF notification state persistent across the alive/un_alive timing window.

`hclge_set_vlan_filter()` is the general add/delete VLAN callback. It records delete failures in `vlan_del_fail_bmap` if reset handling or reset failure is active. When port-base VLAN is disabled, it writes the hardware filter immediately and records `writen_to_tbl = true`; otherwise it only updates the vport VLAN list. Failed deletes are also recorded for later retry. `hclge_sync_vlan_filter()` drains up to `HCLGE_MAX_SYNC_COUNT` delayed delete bits per service pass, removes list entries after successful hardware deletion, and then calls `hclge_sync_vlan_fltr_state()` to reconcile filter enablement.

## Reset Restore and Persistence

Hardware reset paths are designed around in-memory shadow state:

- MAC list entries are converted by `hclge_mac_node_convert_for_reset()`: active entries become `HCLGE_MAC_TO_ADD`, delete-pending entries are removed, and the vport MAC table change bit is set. This ensures service work can repopulate hardware MAC tables after global or IMP reset.
- `hclge_restore_vport_port_base_vlan_config()` iterates all VFs and reprograms port-base VLANs that were enabled before reset. It uses either current or old VLAN info depending on `tbl_sta`, clears the `vlan_table` bit before re-adding, and records whether firmware programming succeeded.
- `hclge_restore_vport_vlan_table()` replays normal VLAN list entries when port-base VLAN is disabled.
- `hclge_restore_hw_table()` coordinates PF MAC restore, VF port-base VLAN restore, PF VLAN restore, flow director restore, and FD user-defined state.

`hclge_reset_prepare_general()` serializes reset preparation with `reset_sem`, sets `HCLGE_STATE_RST_HANDLING`, assigns `reset_type`, and retries `hclge_reset_prepare()` when preparation fails or reset remains pending. It disables the misc vector and command channel before reset completion and increments FLR reset stats for FLR.

`hclge_reset_done()` reenables the misc vector, calls `hclge_reset_rebuild()`, clears `reset_type`, and releases `reset_sem` if it owned the reset-handling state.

`hclge_reset_ae_dev()` is the reset rebuild routine. It sets the device down, clears stats, and for IMP/global resets clears VLAN and UMV shadow tables that firmware has lost. It reinitializes command queues, TQP mapping, MAC/TP port, TSO/GRO, VLAN, traffic manager, RSS, manager table, FD, PTP, error handling, NIC/RoCE error interrupts, vport alive state, spoof checking, VF rates, RX descriptor layout, and WOL. It returns the first hard failure, so reset recovery is all-or-fail for these stages.

## MTU, Queue Reset, Flow Control, and Link Helpers

`hclge_set_vport_mtu()` computes hardware max frame size as MTU plus Ethernet header, FCS, and two VLAN headers. It enforces device max frame size and a minimum/default frame size. VF vports may not exceed PF `hdev->mps`; PF changes may not drop below any VF's stored `mps`. PF MTU changes stop clients, program the MAC max frame size, update PF/vport `mps`, reallocate packet buffers, and bring clients back up.

Queue reset uses two mechanisms. `hclge_reset_rcb()` sends an RCB reset command for the handle's queue range; if firmware reports the command is unsupported it falls back to `hclge_reset_tqp_cmd()`, which resets each global queue ID, polls readiness up to `HCLGE_TQP_RESET_TRY_TIMES`, and deasserts soft reset. PF resets first disable TQPs with `hclge_tqp_enable(handle, false)`.

Pause/flow control code distinguishes link-level pause from priority flow control. `hclge_cfg_pauseparam()` refuses to override PFC mode and otherwise writes MAC pause settings. `hclge_cfg_flowctrl()` resolves advertised pause capabilities through MII helpers when autonegotiation is active, disables pause in half duplex, and applies the result. `hclge_set_pauseparam()` prevents changing autonegotiation through the pause callback, refuses changes during PFC, updates PHY advertised pause, records user-selected `fc_mode_last_time`, and either writes hardware directly or restarts PHY autonegotiation.

Link helper callbacks expose firmware or cached state: `hclge_get_ksettings_an_result()`, `hclge_get_media_type()` with a forced `hclge_update_port_info()`, and `hclge_get_mdix_mode()` for copper PHYs using vendor page/register reads.

## Device and Client Lifecycle

`hclge_init_ae_dev()` is the primary probe path. It allocates `hclge_dev`, initializes locks/semaphores and defaults, enables PCI/DMA/resources, maps BARs, initializes firmware command queues, clears hardware resources, queries capabilities and device specs, configures the device, initializes MSI and misc IRQ, allocates TQPs and vports, maps TQPs, initializes copper PHY/MDIO where needed, initializes UMV space, MAC, TSO/GRO, VLAN, TM scheduler, RSS config/hardware, manager table, flow director, PTP, port info, work/timer state, error handling, RX descriptor advanced layout, WOL, devlink, driver state bits, and finally enables the misc vector and schedules the service task.

The error path unwinds only the stages reached: PTP, MDIO bus, misc IRQ, IRQ vectors, command queue, PCI mappings/regions/device, and the vport lock. Stages initialized without explicit unwind in this visible path rely on earlier failure placement or companion cleanup outside this chunk, which is a maintenance risk if initialization order changes.

`hclge_uninit_ae_dev()` performs device teardown: reset VF rates, clear VF VLANs, mark state as down/removing, cancel reset timer and service work, uninit PTP and RX descriptor layout, remove MAC/FD tables, unregister MDIO, disable misc vector and all hardware interrupts, uninitialize command queue, misc IRQ, devlink, PCI resources, vport VLAN lists, lock, and `ae_dev->priv`.

NIC/RoCE clients are initialized through `hclge_init_client_instance()`. The NIC path calls `client->ops->init_instance()`, marks NIC registered, rejects races with reset by comparing `rst_stats.reset_cnt`, enables NIC hardware error interrupts, and sets the client init flag. The RoCE path checks RoCE support and registered clients, initializes RoCE base info, calls RoCE client init, detects reset races, enables RoCE RAS interrupts, and sets the RoCE client init flag. Both init paths wait out reset handling before invoking client uninit on failure. `hclge_uninit_client_instance()` tears down RoCE first when present, then NIC unless the unregistering client is RoCE-only.

## VF Administrative State

Spoof checking has separate MAC and VLAN hardware controls. `hclge_set_vf_spoofchk()` validates device generation and VF ID, warns when enabling spoof checking while the VF VLAN or UMV MAC tables are full, applies MAC and VLAN spoof hardware config, and records `vport->vf_info.spoofchk`. `hclge_reset_vport_spoofchk()` reapplies spoof settings after reset.

VF trust is an in-memory policy change. `hclge_set_vf_trust()` updates `vport->vf_info.trusted`, marks promiscuous mode changed, and schedules service work. Later `hclge_sync_vport_promisc_mode()` allows trusted VFs to request unicast/multicast promiscuous modes, also considering overflow-promiscuous flags, while untrusted VFs only retain requested broadcast behavior. A successful promiscuous update marks VLAN filter state changed because promiscuity affects whether VLAN filtering should be enabled.

Rate limiting supports only `min_tx_rate == 0` and `max_tx_rate` in `[0, mac.max_speed]`. `hclge_set_vf_rate()` configures the TM queue-set shaper and stores `vf_info.max_tx_rate`. Reset and remove paths either restore stored nonzero rates (`hclge_resume_vf_rate()`) or reset all VF rates to default (`hclge_reset_vf_rate()`).

SR-IOV disable cleanup flows through `hclge_clean_vport_config()`, which calls `hclge_clear_vport_vf_info()` for each VF. That clears vport init/alive state, notification bits, `mps`, VF rate, port-base VLAN, spoof checking, and the entire `vf_info` structure.

## WOL, EEPROM, Channels, LEDs, GRO, and Diagnostics

Wake-on-LAN state is stored in `hdev->hw.mac.wol`. `hclge_init_wol()` checks support, queries supported modes, and writes a default/current config. `hclge_set_wol()` validates requested options against support, records secure-on password bytes when `WAKE_MAGICSECURE` is set, writes firmware config, and clears `wol_current_mode` on firmware failure. `hclge_update_wol()` reapplies this stored config after reset.

RSS/channel callbacks expose maximum channels as `min(pf_rss_size_max, vport->alloc_tqps)`. `hclge_set_channels()` records the requested RSS size, updates TM vport mapping, programs RSS TC mode, and if the user has not supplied an indirection table, rebuilds an even modulo indirection table sized by `dev_specs.rss_ind_tbl_size`.

`hclge_set_led_id()` maps ethtool physical ID active/inactive states to firmware LED on/off commands. `hclge_gro_en()` toggles `hdev->gro_en`, reprograms GRO, and rolls back the field on error. `hclge_get_link_mode()` copies supported and advertising bitmaps from cached MAC state.

SFP EEPROM reads first require fiber media and module presence (`hclge_module_existed()`). `hclge_get_sfp_eeprom_info()` sends a six-descriptor read command, copies data from descriptor 0 and then descriptors 1-5, and returns the actual bytes copied. `hclge_get_module_eeprom()` loops until the requested length is filled or a read returns zero.

`hclge_get_link_diagnosis_info()` is firmware-version gated to devices newer than version 2 and returns a firmware status code. `hclge_get_dscp_prio()` validates DSCP range and exposes the current TC map mode plus DSCP-to-priority mapping, defaulting invalid priorities to 0.

## Dependencies and Integration Points

This chunk depends heavily on:

- Linux kernel networking APIs: `net_device` flags through HNAE3, ethtool callback types, MII/PHY helpers, VLAN constants, link mode bitmaps, workqueues, timers, mutexes, spinlocks, semaphores, bitmaps, PCI, DMA, devm/pcim mapping, IRQs, and module registration.
- HNS3/HNAE3 common command infrastructure: `hclge_cmd_setup_basic_desc()`, `hclge_comm_cmd_reuse_desc()`, `hclge_cmd_send()`, common command queue init/uninit, RSS common helpers, and command opcodes.
- Firmware/hardware feature gates: `hdev->ae_dev->dev_version`, `hdev->ae_dev->caps`, `hnae3_dev_phy_imp_supported()`, `hnae3_dev_roce_supported()`, `hnae3_ae_dev_rxd_adv_layout_supported()`, `hnae3_ae_dev_wol_supported()`, and RAS capability checks.
- Traffic manager, RSS, FD, PTP, devlink, mailbox, PHY/MDIO, and reset helpers implemented elsewhere in the driver.
- Upper clients through `struct hnae3_client` and `struct hnae3_ae_ops`. The `hclge_ops` table is the outward-facing integration contract for the rest of the HNS3 stack.

## Control Flow and State Transitions

Major control paths:

- Probe: `hclge_init()` registers `ae_algo`; later the bus/core calls `.init_ae_dev = hclge_init_ae_dev`, followed by `.init_client_instance` as clients bind.
- Runtime settings: ethtool/netdev callbacks enter via `hclge_ops`, convert `hnae3_handle` to `hclge_vport`, mutate software shadow state, and send one or more firmware commands.
- Service reconciliation: operations that cannot complete during reset or that depend on aggregated vport state set bits such as `HCLGE_VPORT_STATE_VLAN_FLTR_CHANGE`, `HCLGE_VPORT_STATE_PROMISC_CHANGE`, and `HCLGE_VPORT_STATE_MAC_TBL_CHANGE`; service work later synchronizes hardware.
- Reset: reset prepare disables command/misc interrupt paths; reset rebuild recreates hardware state from shadow structures; reset done clears reset state and releases serialization.
- Remove: `.uninit_client_instance` detaches clients; `.uninit_ae_dev` stops timers/work, interrupts, hardware tables, firmware command queues, PCI resources, and in-memory VLAN lists; module exit unregisters the AE algorithm and destroys the workqueue.

Important persistence patterns:

- `vport->vlan_list`, `port_base_vlan_cfg`, `vf_info`, `rxvlan_cfg`, `txvlan_cfg`, WOL info, GRO flag, RSS state, FD state, MAC lists, and VF rate/trust/spoof values are software truth used to reconstruct firmware after reset.
- `tbl_sta`, `hd_tbl_status`, `vlan_del_fail_bmap`, and `vf_vlan_full` describe divergence between software intent and firmware tables.
- Reset handling clears or preserves these mirrors selectively depending on reset scope; IMP/global reset clears hardware-lost tables, while PF reset avoids clearing table state.

## Risks and Edge Cases

- `hclge_reset_prepare_general()` proceeds to disable the misc vector and command channel even if all reset-prepare retries fail. This may be intentional for reset sequencing, but failures before the break leave `reset_sem` handling dependent on the loop state and downstream reset completion.
- VLAN delete during reset returns `-EBUSY` after recording `vlan_del_fail_bmap`. Callers must tolerate the returned failure while the driver later reconciles state.
- `hclge_sync_vlan_filter()` holds `vport_lock` while sending firmware commands. Other paths in this chunk also send commands under that mutex. This simplifies state consistency but can make command latency visible to unrelated vport operations.
- VF VLAN table full handling is asymmetric: add operations may become no-ops once `vf_vlan_full` is set unless spoof checking is enabled. This prevents more firmware churn but can surprise tests that expect every software VLAN list entry to have a hardware entry.
- Port-base VLAN transitions are multi-command sequences with partial-failure windows. The code records `tbl_sta` and old VLAN info, but failed middle steps can leave software/hardware divergence until reset or restore.
- `hclge_get_sfp_eeprom_info()` uses a fixed maximum per firmware request. Bounds depend on descriptor layout constants; any mismatch between firmware response layout and copy lengths would corrupt returned EEPROM data.
- Init and reset paths are long ordered sequences. Adding a new initialized subsystem without matching failure unwind, reset rebuild, and uninit handling can leak resources or lose state across reset.
- `hclge_set_wol()` clears only `wol_current_mode` on firmware failure after having possibly updated secure password fields. A later retry path should be checked if secure-password consistency matters.
- `hclge_set_channels()` allocates a temporary RSS indirection table after updating TM/RSS TC mode. Failure during allocation or later RSS programming can leave partial channel changes depending on earlier helper side effects.
- Many functions rely on device version/capability gates. Tests and future changes need to cover older firmware/device revisions, especially version 1/2 VLAN paths and unsupported RCB/WOL/RXD-advanced-layout commands.

## Test Signals

Useful validation signals for this chunk include:

- MAC address tests: reject zero/broadcast/multicast addresses; verify pause address rollback on failure; verify service task schedules MAC table sync.
- MII/PHY tests: PHY-backed and firmware-backed MII ioctls, unsupported command returns, and no-phy unsupported-device behavior.
- VLAN tests: add/delete VLAN 0 and nonzero VLANs; duplicate adds/deletes; port-base VLAN enable/disable/modify; VF VLAN table full response; spoof-check interaction with full VF VLAN table; VLAN filter enable policy under PF promiscuous mode, trusted VF requests, and VLAN filter modification capability.
- Reset tests: global/IMP reset should clear/replay VLAN/MAC/FD state; PF reset should preserve in-memory table state; reset races during client init should unwind correctly; delayed VLAN deletes should be retried by sync.
- MTU tests: PF MTU lower than VF MPS rejection; VF MTU above PF MPS rejection; max/min frame boundaries; buffer reallocation failure after MAC frame-size programming.
- Queue reset tests: successful RCB reset; unsupported RCB fallback to per-TQP reset; timeout waiting for ready-to-reset; global queue ID conversion.
- Flow-control tests: PFC refusal, autoneg mismatch rejection, PHY pause advertisement, half-duplex pause disable, PHY implementation path without `phydev`.
- Lifecycle tests: probe failure injection at each major stage, matching cleanup; reset rebuild failure injection; module init workqueue allocation failure; uninit after partial client registration.
- VF admin tests: spoof check warnings under full MAC/VLAN tables, trust toggles causing promiscuous resync, VF rate bounds, SR-IOV disable cleanup resetting VLAN/rate/spoof/VF info.
- Ettool helper tests: channel resizing with and without user RSS indirection, LED active/inactive commands, GRO rollback on firmware failure, link mode bitmap copy, MDIX invalid when no PHY.
- WOL/EEPROM tests: unsupported WOL no-op, invalid WOL options, magic secure password programming, WOL restore after reset, fiber-only EEPROM reads, no-module `-ENXIO`, multi-descriptor EEPROM reads crossing the per-command length.

## Cross-Chunk References

The following visible calls require earlier or companion chunks for full behavior:

- MAC table helpers: `hclge_update_mac_node_for_dev_addr()` begins immediately before this chunk; MAC sync and UMV handling are elsewhere.
- Reset service: `hclge_reset_prepare()`, `hclge_reset_rebuild()`, `hclge_reset_timer()`, `hclge_service_task()`, and reset-event helpers are outside this span.
- Hardware setup helpers: `hclge_configure()`, `hclge_init_msi()`, `hclge_misc_irq_init()`, `hclge_alloc_tqps()`, `hclge_alloc_vport()`, `hclge_map_tqp()`, MAC/PHY init, TM/RSS/FD/PTP/devlink setup, and error handling are external to this chunk.
- Netdev/ethtool callbacks mapped in `hclge_ops` such as stats, FEC, RSS tuple, loopback, FD, flower, PTP timestamping, VF MAC/link state, command queue stats, and reset status are implemented outside this visible range.

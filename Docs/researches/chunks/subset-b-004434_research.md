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

# Research Group: subset-b-004533

This grouped report covers mlx5 Ethernet RX/TX health reporting, receive resource tables, RSS, TX queue selection, TC action parsing, connection-tracking steering backends, flow meters, post actions, internal-port forwarding, and packet sampling. Each file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/reporter_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/reporter_rx.c

Purpose: Implements the mlx5e devlink health reporter for RX-side failures. It reports and recovers RQ CQE errors, ICOSQ CQE errors, RX timeouts, and exposes diagnose/dump data for RQs, ICOSQs, RX resources, RSS TIR/RQT numbers, and optional PTP RX queues.

Important APIs and functions: `mlx5e_reporter_rx_create()` and `mlx5e_reporter_rx_destroy()` register the `"rx"` `devlink_health_reporter_ops`. `mlx5e_reporter_rx_timeout()`, `mlx5e_reporter_rq_cqe_err()`, and `mlx5e_reporter_icosq_cqe_err()` build `mlx5e_err_ctx` records and call `mlx5e_health_report()`. Recovery is split across `mlx5e_rx_reporter_err_rq_cqe_recover()`, `mlx5e_rx_reporter_err_icosq_cqe_recover()`, `mlx5e_rx_reporter_timeout_recover()`, and the generic `mlx5e_rx_reporter_recover()`.

Control flow: Error entry points attach a context-specific recover function and dump function. RQ CQE recovery deactivates the RQ, flushes it from ERR state, clears `MLX5E_RQ_STATE_RECOVERING`, reactivates, increments recovery stats, and schedules NAPI. ICOSQ recovery takes `icosq_recovery_lock`, validates the hardware SQ state is ERR, deactivates regular and XSK RQs, waits for ICOSQ flush, transitions the SQ to ready, resets producer/consumer counters, frees missing RX descriptors, and reactivates queues. Timeout recovery loops on `netdev_trylock()` until channels close or lock acquisition succeeds, then calls EQ/channel recovery under `priv->state_lock`.

State and persistence: The reporter stores only `priv->rx_reporter`; queue state lives in RQ/ICOSQ bitfields, counters, CQ/EQ objects, and hardware RQ/SQ state. The string table must remain aligned with `MLX5E_RQ_STATE_*`. Recoveries mutate queue enabled/recovering bits and stats but do not persist outside live kernel/hardware state.

Dependencies and integration: Uses devlink health, mlx5 core RQ/SQ query and state transition helpers, `health.h` fmsg/dump helpers, `rx_res`/RSS getters, PTP channel state, NAPI triggers, and `netdev_lock`. It is called from RX datapath/CQE timeout paths and is consumed by devlink userspace health tooling.

Risks: Deadlock avoidance depends on try-lock loops and channel-active checks. ICOSQ recovery assumes CQ draining reaches `cc == pc`; timeout leaves the reporter unable to reset counters. XSK and PTP queues add branch coverage. Diagnose helpers mostly ignore nested helper return values, so malformed devlink output is possible if lower helpers fail. Tests should exercise RQ CQE, ICOSQ CQE, timeout, XSK-enabled channels, PTP RX, closed netdev, and devlink diagnose/dump paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/reporter_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/reporter_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/reporter_tx.c

Purpose: Implements the mlx5e devlink health reporter for TX-side failures, including TX SQ ERR CQEs, watchdog timeouts, and unhealthy PTP timestamp queues.

Important APIs and functions: `mlx5e_reporter_tx_create()`/`destroy()` own the `"tx"` reporter. `mlx5e_reporter_tx_err_cqe()`, `mlx5e_reporter_tx_timeout()`, and `mlx5e_reporter_tx_ptpsq_unhealthy()` publish health events. Recovery is handled by `mlx5e_tx_reporter_err_cqe_recover()`, `mlx5e_tx_reporter_timeout_recover()`, and `mlx5e_tx_reporter_ptpsq_unhealthy_recover()`. Diagnose and dump functions enumerate SQs, TIS config, CQ/EQ state, and hardware QPC/send buffer dumps.

Control flow: ERR CQE recovery verifies the SQ is in recovering state, obtains the netdev instance lock without blocking close flows forever, checks hardware SQ state, stops the netdev TXQ, waits for SQ flush, moves the hardware SQ to ready, resets `cc/pc`, clears recovering, activates SQ, and schedules NAPI. Timeout recovery first tries channel EQ recovery, then falls back to `mlx5e_safe_reopen_channels()`. PTP SQ recovery closes and reopens the PTP channel while toggling carrier state around channel deactivation/reactivation.

State and persistence: State is live in SQ bitfields, TXQ stopped state, SQ counters, recovery stats, PTP channel pointers, and `priv->tx_reporter`. `mlx5e_tx_timeout_ctx.status` communicates whether a single SQ or all channels recovered. The SQ state string table is compile-time checked against `MLX5E_NUM_SQ_STATES`.

Dependencies and integration: Uses devlink health reporter ops, mlx5 SQ query/ready helpers, `health.h` dump helpers, `ptp.h`, DCB TC count, profile TIS getters, NAPI triggers, and netdev instance locking. Entry points are called by TX completion, watchdog, and PTP timestamp-health paths.

Risks: Recovery ordering is subtle because netdev locks overlap with channel close/reopen. SQ flush timeouts leave the queue unrecovered. Timeout recovery can escalate from local EQ recovery to full channel reopen. PTP recovery temporarily drops carrier and must restore it correctly. Tests should cover ERR CQE, watchdog timeout fallback, PTP unhealthy recovery, multiple TCs, PTP enabled/disabled, and devlink dump without opened channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/reporter_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rqt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rqt.c

Purpose: Owns mlx5 receive queue table creation, destruction, and redirection for direct and RSS-indirection receive paths.

Important APIs: `mlx5e_rqt_init_direct()`, `mlx5e_rqt_init_indir()`, `mlx5e_rqt_destroy()`, `mlx5e_rqt_redirect_direct()`, `mlx5e_rqt_redirect_indir()`, `mlx5e_rqt_size()`, `mlx5e_rqt_max_num_channels_allowed_for_xor8()`, and `mlx5e_rss_params_indir_init_uniform()`.

Control flow: Direct initialization creates an RQT with one initial RQN and max size either one or the indirection-table size. Indirect initialization translates an RSS indirection table into RQNs, optionally inverting indices for XOR hash, then creates an RQT. Redirect paths build `modify_rqt_in` input and rewrite the RQN list. `fill_rqn_list()` handles plain RQNs or cross-vHCA `rq_vhca` entries.

State and persistence: `struct mlx5e_rqt` stores the primary mlx5 device, RQTN, and max size. Hardware RQT state persists until `mlx5_core_destroy_rqt()`. Indirection arrays are caller-owned and are copied into command buffers only during create/modify.

Dependencies and integration: Uses mlx5 transobj commands, device capabilities for `cross_vhca_rqt`, `max_rqt_vhca_id`, and `log_max_rqt_size`, and ethtool RSS hash constants. RSS and RX resource code call this file for all hardware RQT programming.

Risks: Invalid indirection entries produce `WARN_ON` and `-EINVAL`. Cross-vHCA support must be capability-gated and id ranges validated. XOR hash is capped by a 256-entry allowed RQT size. Tests should validate direct and indirect creation, table resizing, XOR index inversion, out-of-range indirection indices, cross-vHCA enabled/disabled, and redirect error rollback by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rqt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rqt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rqt.h

Purpose: Declares the receive queue table abstraction and RSS indirection-table storage used by mlx5e RX resources.

Important types and APIs: `struct mlx5e_rss_params_indir` holds an indirection array plus actual and maximum table sizes. `struct mlx5e_rqt` holds the mlx5 device, RQTN, and table size. The header exports direct/indirect init and redirect APIs, `mlx5e_rqt_get_rqtn()`, sizing helpers, and uniform indirection initialization.

Control flow and state: The header defines ownership boundaries but no complex logic. Callers allocate and own `mlx5e_rqt` and call the C implementation to create/destroy hardware tables. `MLX5E_INDIR_MIN_RQT_SIZE` fixes the minimum RSS RQT size at 256 entries.

Dependencies and integration: Included by `rss.h`, `rx_res.h`, and RQT users that need RQTN numbers for TIR builders. It depends on Linux kernel types and forward-declares `mlx5_core_dev`.

Risks and test signals: ABI drift between the header and `rqt.c` would break RSS and direct TIR setup. Tests should confirm all callers destroy initialized RQTs, pass table sizes matching `max_table_size`, and handle `mlx5e_rqt_size()` limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rqt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rss.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rss.c

Purpose: Implements an RSS context around one indirect RQT, per-traffic-type TIRs, hash parameters, indirection table, optional inner TIRs, enable/disable redirection, and ethtool RSS mutation.

Important APIs: `mlx5e_rss_init()`, `mlx5e_rss_cleanup()`, refcount helpers, `mlx5e_rss_enable()`/`disable()`, `mlx5e_rss_get_rxfh()`/`set_rxfh()`, `mlx5e_rss_get_hash_fields()`/`set_hash_fields()`, `mlx5e_rss_packet_merge_set_param()`, `mlx5e_rss_obtain_tirn()`, and TIR/RQTN getters. `rss_default_config` maps mlx5 traffic types to default L3/L4 and hash fields.

Control flow: Initialization allocates an RSS object and indirection table, seeds Toeplitz hash and default fields, creates an RQT initially pointing at the drop RQ, and optionally creates all outer and inner TIRs. Enable redirects the RQT through `mlx5e_rqt_redirect_indir()`. Disable points it back to the drop RQ. `set_rxfh()` snapshots the old RSS object, applies requested hfunc/key/indir/symmetric changes, redirects the RQT when enabled, rolls back on redirect failure, and modifies TIR RSS state when hash parameters changed.

State and persistence: The RSS object owns hash params, indirection table allocation, per-traffic-type `rx_hash_fields`, TIR pointers, the RQT, `enabled`, and `refcnt`. Hardware TIR/RQT objects persist until cleanup or destroy. Refcount prevents cleanup unless the owner has exclusive reference.

Dependencies and integration: Uses RQT, TIR builder/modify APIs, mlx5 traffic type constants, ethtool hash constants, packet merge configuration from RX resources, and capability flags supplied by `rx_res`. `reporter_rx.c` diagnoses TIR/RQTN state through these getters.

Risks: `mlx5e_rss_copy()` shallow-copies then restores the indirection pointer; future fields with owned allocations require care. Hash field updates can partially update outer TIR before inner TIR fails; the code attempts best-effort rollback. `set_rxfh()` ignores return from `mlx5e_rss_update_tirs()` after successful RQT change. Tests should cover lazy TIR creation, inner FT unsupported errors, hfunc validation, rollback after RQT redirect failure, packet merge updates, refcounted cleanup, and ethtool RSS changes while enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rss.h

Purpose: Public interface for mlx5e RSS contexts, including init modes, parameters, TIR/RQT accessors, RSS hash/indirection configuration, and refcounting.

Important types: `enum mlx5e_rss_init_type` selects lazy/no-TIR or precreated TIR initialization. `struct mlx5e_rss_init_params` passes packet merge parameters and channel sizing. `struct mlx5e_rss_params` carries inner FT support, drop RQN, and self-loopback block. The opaque `struct mlx5e_rss` hides implementation details.

Control flow and state: Callers create an RSS object with `mlx5e_rss_init()`, optionally enable it with live RQNs/vHCA IDs, query TIRNs for flow steering, and mutate RSS via ethtool-facing methods. Cleanup returns `-EBUSY` if references remain.

Dependencies and integration: Includes `rqt.h`, `tir.h`, and `fs.h`; consumed by RX resource manager, reporters, and flow-steering code needing RSS TIRNs.

Risks and test signals: Because the struct is opaque, correctness rests on callers honoring lifecycle, reference count, and enabled-state expectations. Tests should validate compile-time call sites under `CONFIG_*` variants, cleanup error handling, and that callers do not request inner TIRs without support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rx_res.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rx_res.c

Purpose: Manages all mlx5e receive steering resources for an interface: default and auxiliary RSS contexts, per-channel direct RQTs/TIRs, PTP direct RQT/TIR, packet-merge state, XSK RQ switching, multi-vHCA RQN mapping, and TLS TIR creation.

Important APIs: `mlx5e_rx_res_create()`/`destroy()`, channel activate/deactivate, `mlx5e_rx_res_xsk_update()`, RSS init/destroy/count/index/get/configuration functions, direct/RSS/PTP TIRN and RQTN getters, `mlx5e_rx_res_packet_merge_set_param()`, and `mlx5e_rx_res_tls_tir_create()`.

Control flow: Creation allocates RQN/vHCA arrays, initializes default RSS with TIRs, creates a direct RQT/TIR pair for every max channel, and creates the PTP TIR/RQT. Activation populates `rss_rqns` from regular or XSK channel RQNs, enables all RSS contexts, redirects each direct RQT, and redirects PTP if supported. Deactivation disables RSS and points direct/PTP RQTs back to the drop RQ. XSK updates swap one channel's RQN then re-enable RSS and the direct RQT.

State and persistence: `struct mlx5e_rx_res` owns feature flags, max channel count, drop RQN, packet-merge parameters protected by `rw_semaphore`, RSS context pointers, active RSS RQNs/vHCA IDs, direct channel objects, and PTP object. Hardware RQTs/TIRs persist while the resource exists.

Dependencies and integration: Uses `channels.h` for RQNs, `params.h`, RSS, RQT, TIR builders, TLS TIR builder mode, packet merge, PTP feature flags, and multi-vHCA support. Reporters and flow-steering code query its TIR/RQTN getters.

Risks: Activation iterates `chs->num` for RSS but only `mlx5e_channels_get_num()` for direct activation, so channel-count semantics must remain consistent. Packet merge modification can partially fail across RSS and direct TIRs. RSS destroy can fail when refcounts remain and logs warnings during destroy-all. Tests should cover init unwind, max_nch sizing, XSK updates, multi-vHCA IDs, PTP absent/present, packet merge update failures, TLS TIR creation under concurrent packet-merge changes, and RSS auxiliary lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rx_res.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rx_res.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rx_res.h

Purpose: Declares the RX resource manager interface and feature flags used by mlx5e receive flow steering.

Important types and APIs: `MLX5E_MAX_NUM_RSS` limits RSS contexts to 16. `enum mlx5e_rx_res_features` controls inner flow-table support, PTP TIR, multi-vHCA RQT entries, and self-loopback block. The header exports setup/teardown, TIRN/RQTN getters, activate/deactivate, XSK update, RSS ethtool operations, packet merge, RSS context management, and TLS TIR creation.

Control flow and state: The opaque `struct mlx5e_rx_res` is created once for the netdev profile and then reprogrammed as channels open, close, or change. Callers must not use TIR/RQTN getters before create succeeds.

Dependencies and integration: Includes RQT, TIR, FS, and RSS headers; used by channel setup, flow steering, reporters, TLS acceleration, PTP, and ethtool RSS configuration.

Risks and test signals: The header declares `bool mlx5_rx_res_rss_inner_ft_support(struct mlx5e_rx_res *res);`, but this function is not implemented in the read source set, so callers must be checked elsewhere or this is dead/API drift. Tests should validate compile/link coverage for all exported symbols and feature-flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rx_res.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/selq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/selq.c

Purpose: Implements mlx5e `ndo_select_queue` policy with support for regular queues, DCB traffic classes, PTP port timestamp queues, and HTB offload queues.

Important APIs: `mlx5e_selq_init()`, `cleanup()`, `prepare_params()`, `prepare_htb()`, `apply()`, `cancel()`, `is_htb_enabled()`, and `mlx5e_select_queue()`.

Control flow: A standby parameter block is prepared under `state_lock`, then atomically swapped into `active` with `rcu_replace_pointer()`; `synchronize_net()` waits for in-flight queue selection to see a consistent state. `mlx5e_select_queue()` uses RCU BH dereference, chooses regular queues through `netdev_pick_tx()`, normalizes to channel index, applies UP/TC offset, or routes PTP/HTB packets to special queues.

State and persistence: `mlx5e_selq_params` holds regular queue count, channels, TCs, special-queue flags, HTB major id, and default class. Active state is RCU-protected; standby is reused after swaps. Cleanup swaps a dummy/null-ish state and frees both allocations.

Dependencies and integration: Uses netdev queue selection, VLAN or DSCP priority extraction under DCB, PTP `mlx5e_use_ptpsq()`, HTB class-to-TXQ lookup, `state_lock`, and RCU networking synchronization. Called from netdev operations on the TX hot path.

Risks: This is datapath code; incorrect queue normalization can select PTP/HTB queues for regular traffic or wrong TC queues. DSCP trust depends on `READ_ONCE` of DCB state. Cleanup intentionally prepares/applies under lock; misuse of prepare/apply/cancel sequencing triggers warnings. Tests should cover no-special, multi-TC, PTP, HTB, HTB+PTP fallback, DSCP vs VLAN UP, profile-change null active workaround, and lockdep expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/selq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/selq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/selq.h

Purpose: Declares the queue selection state object, lifecycle/configuration APIs, and helper functions for mapping TX queue numbers to channel indexes.

Important APIs and types: `struct mlx5e_selq` contains RCU `active`, standby params, a pointer to `priv->state_lock`, and an `is_prepared` guard. Inline `mlx5e_txq_to_ch_ix()` and `mlx5e_txq_to_ch_ix_htb()` normalize queue indexes for regular and HTB-special layouts.

Control flow and state: Users initialize the selector, prepare either general params or HTB params while holding `state_lock`, then apply or cancel. `mlx5e_select_queue()` is exported for netdev operations.

Dependencies and integration: Depends on kernel types and forward-declares mlx5e params/netdev/sk_buff. Included by channel/profile code and netdev ops.

Risks and test signals: The inline HTB mapping has a fast path for high queue numbers (`>= num_channels << 3`) and a loop for moderate overflow; tests should include boundary values. API correctness depends on callers respecting prepare/apply sequencing under the state lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/selq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/accept.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/accept.c

Purpose: Provides the TC `FLOW_ACTION_ACCEPT` parser for mlx5e TC offload.

Important API: Exports `mlx5e_tc_act_accept`, whose `parse_action` sets `MLX5_FLOW_CONTEXT_ACTION_FWD_DEST` and `MLX5_ATTR_FLAG_ACCEPT`, and marks the action as terminating.

Control flow, state, dependencies: No persistent state. It mutates the current `mlx5_flow_attr` during TC action parsing and depends on `act.h` and `tc_priv.h`.

Risks and tests: Its behavior is intentionally small; tests should verify accept terminates parsing as expected and sets FWD_DEST without adding destinations incorrectly in FDB/NIC contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/accept.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/act.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/act.c

Purpose: Central dispatcher and helper implementation for mlx5e TC action parsing.

Important APIs: `mlx5e_tc_act_get()` maps `flow_action_id` to a `struct mlx5e_tc_act` table for FDB or NIC namespace. `mlx5e_tc_act_init_parse_state()` zeroes and seeds parser state. `mlx5e_tc_act_post_parse()` runs per-action `post_parse` hooks over a range. `mlx5e_tc_act_set_next_post_act()` writes a post-action handle into the modify-header action list and sets FWD_DEST/MOD_HDR.

Control flow: The parser obtains action vtables from `tc_acts_fdb` or `tc_acts_nic`; unsupported action ids return NULL to the caller. Post-parse walks the original `flow_action`, filters by index range, and invokes only actions with a hook.

State and dependencies: Static action tables are the key state. Parse state carries transient flags such as encap, decap, mpls, ptype_host, tunnel info, ifindexes, and CT private pointer. Depends on post-action register programming and TC private flow structs.

Risks and tests: Adding a new action requires namespace table updates and extern declarations. Array indexing relies on `act_id < NUM_FLOW_ACTIONS` from callers. Tests should cover FDB/NIC action table differences, post-parse ordering, unsupported actions, and chained post-action handle programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/act.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/act.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/act.h

Purpose: Defines the mlx5e TC action parser interface, shared parse state, action operation callbacks, and extern parser instances.

Important types: `struct mlx5e_tc_act_parse_state` tracks flow, extack, accumulated actions, tunnel/MPLS/VLAN state, output ifindexes, CT private data, and branch flags. `struct mlx5e_tc_act` is a vtable for validation, parsing, post-parse, multi-table decisions, standalone action offload/destroy/stats, branch control, and termination metadata.

Control flow and state: Parser code initializes one parse state per flow and passes it through all action vtables, allowing earlier actions to affect later validation, such as `ptype` before redirect-ingress or tunnel encap before mirred.

Dependencies and integration: Includes flow offload, netlink extack, eswitch, and pedit declarations. Consumed by every file under `tc/act` and by higher-level TC flow parser code.

Risks and tests: The shared mutable parse state is easy to misuse when action order changes. Tests should exercise action combinations that rely on transient flags: tunnel+mirred, mpls+vlan eth push/pop, ptype+redirect_ingress, ct+post_parse, and police branch controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/act.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/csum.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/csum.c

Purpose: Validates TC checksum recalculation offload constraints for mlx5e.

Important API: `mlx5e_tc_act_csum` exposes `can_offload` and a no-op parse action. `csum_offload_supported()` requires an existing modify-header action and restricts update flags to IPv4/TCP/UDP.

Control flow and state: No persistent state. Validation observes `attr->action` to ensure a previous pedit/mangle action requested `MLX5_FLOW_CONTEXT_ACTION_MOD_HDR`.

Dependencies and integration: Uses kernel TC csum flags, netlink extack, and netdev warnings. Integrated through the TC action dispatch table.

Risks and tests: Action order matters: csum before pedit should fail. Unsupported checksum flags must return a clear extack. Tests should cover pedit+csum success, csum-only failure, and unsupported flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/csum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/ct.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/ct.c

Purpose: Bridges TC connection-tracking actions into mlx5 TC CT offload.

Important API: `mlx5e_tc_act_ct` validates, parses, post-parses, and marks CT as multi-table/missable except for clear actions. Parsing calls `mlx5_tc_ct_parse_action()`, post-parse calls `mlx5_tc_ct_flow_offload()`.

Control flow: Commit CT actions cannot be the last flow action. Parsing may reset eswitch split/output counts after CT processing, because CT creates a multi-table boundary. The post-parse hook performs actual CT flow offload only if `MLX5_ATTR_FLAG_CT` was set.

State and dependencies: Mutates `attr` flags and eswitch attr split state; uses `parse_state->ct_priv` and `en/tc_ct.h`. No independent persistent state.

Risks and tests: CT action ordering, clear-vs-non-clear behavior, and FDB split reset are subtle. Tests should cover CT commit last rejection, CT clear, CT with redirect destinations, post-parse errors, and missable/multi-table decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/drop.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/drop.c

Purpose: Provides TC drop action parsing for mlx5e.

Important API: `mlx5e_tc_act_drop` sets `MLX5_FLOW_CONTEXT_ACTION_DROP` and is marked terminating.

Control flow, state, dependencies: No persistent state. It only mutates `attr->action` during parse and depends on common action/TC private headers.

Risks and tests: Tests should confirm drop is terminating and does not leave forwarding destinations active in combinations where higher-level parser must reject conflicting actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/drop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/goto.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/goto.c

Purpose: Validates and parses TC goto-chain actions for mlx5e TC offload.

Important API: `mlx5e_tc_act_goto` provides can-offload, parse, post-parse, and marks goto as terminating. `validate_goto_chain()` checks chain range, backward-chain support, flow type, and firmware support for forwarding after reformat/decap.

Control flow: Validation chooses eswitch or NIC chain object, checks destination chain against range and direction constraints, then parse sets FWD_DEST and `attr->dest_chain`. Post-parse rejects decap+goto and mirroring goto chain rules for NIC flows.

State and dependencies: Mutates `attr->dest_chain` and action bits. Depends on eswitch chains, NIC TC chains, firmware capabilities, flow type helpers, and extack.

Risks and tests: Goto combines poorly with decap, packet reformat, mirred, and unsupported backward chains. Tests should cover FDB/NIC chain ranges, backward unsupported, FT flow rejection, decap+goto post-parse, and reformat capability gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/goto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mark.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mark.c

Purpose: Handles TC skbedit mark offload for NIC namespace flows.

Important API: `mlx5e_tc_act_mark` validates that marks fit `MLX5E_TC_FLOW_ID_MASK`, stores `act->mark` into `attr->nic_attr->flow_tag`, and sets FWD_DEST.

Control flow and state: No persistent state; it mutates NIC flow attribute state.

Dependencies and integration: Included in the NIC action table only. Uses `en_tc.h` for flow tag mask definitions and extack reporting.

Risks and tests: Only 16-bit marks are supported. Tests should cover max supported mark, overflow rejection, and NIC-only availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mirred.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mirred.c

Purpose: Parses FDB mirred/redirect actions, including representor forwarding, tunnel encap destinations, VLAN device adjustment, OVS internal port forwarding, BareUDP/MPLS constraints, and LAG/bond handling.

Important APIs: Exports non-terminating `mlx5e_tc_act_mirred` and terminating `mlx5e_tc_act_redirect`. Validation is `tc_act_can_offload_mirred()`. Parsing is split into `parse_mirred_encap()`, `parse_mirred()`, and `parse_mirred_ovs_master()`.

Control flow: Validation rejects missing devices, unsupported MPLS/VLAN-eth combinations, duplicate or excessive output ports, invalid switch-parent relationships, and invalid filter-device contexts. Encap parsing stores duplicated tunnel info and optional MPLS info. Plain mirred resolves macvlan, bond/LAG, VLAN push/pop actions, validates uplink forwarding, resolves representor vport/mdev, and appends a destination. OVS master forwarding programs internal-port actions and resets `if_count`.

State and dependencies: Mutates parse state ifindex tracking, encap/MPLS flags, `parse_attr` tunnel/MPLS arrays, `esw_attr->dests`, `out_count`, VLAN actions, and flow action bits. Depends on eswitch representors, bonding/LAG, BareUDP, VLAN helpers, internal-port helpers, and tunnel encap helpers.

Risks and tests: Device topology and action-order interactions dominate risk. Tests should cover duplicate output rejection, max vports, VF-to-self, uplink-to-uplink capability gating, VLAN upper/lower devices, macvlan, bond active slave, encap redirect, MPLS push through BareUDP, OVS internal port, and filter-device mismatch replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mirred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mirred_nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mirred_nic.c

Purpose: Handles NIC namespace redirect action by marking the flow as hairpin to another mlx5 netdev on the same hardware.

Important API: `mlx5e_tc_act_mirred_nic` validates only `FLOW_ACTION_REDIRECT`, requires matching netdev ops and same hardware device, stores target ifindex in `mirred_ifindex[0]`, sets flow flag `HAIRPIN`, sets FWD_DEST, and is terminating.

Control flow and state: No persistent state; it mutates parse attributes and flow flags.

Dependencies and integration: Uses `mlx5e_same_hw_devs()`, netdev operations, extack, and the NIC action table.

Risks and tests: Target device validity is crucial. Tests should cover redirect vs mirred action id, same/different mlx5 devices, non-mlx5 devices, NULL or stale device handling by caller, and hairpin flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mirred_nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mpls.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mpls.c

Purpose: Parses MPLS push/pop TC actions for FDB offload, mainly with BareUDP and L3-to-L2 decap flows.

Important APIs: `mlx5e_tc_act_mpls_push` validates `reformat_l2_to_l3_tunnel` support and MPLS unicast protocol, then records MPLS fields in parse state. `mlx5e_tc_act_mpls_pop` validates action position and BareUDP filter device, then sets packet reformat and `L3_TO_L2_DECAP`.

Control flow and state: Push only stores transient `parse_state->mpls_push` and `mpls_info`; `mirred` later consumes it. Pop mutates `attr->esw_attr->eth.h_proto`, action flags, and flow flags.

Dependencies and integration: Depends on BareUDP device recognition, eswitch firmware caps, `tc_priv` flow flags, and later VLAN/mirred parsing for Ethernet push requirements.

Risks and tests: MPLS support is action-order constrained. Tests should cover push with non-MPLS_UC, missing firmware cap, pop not first or not after decap, non-BareUDP filter device, pop plus VLAN eth push, and mirred after MPLS push.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mpls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/pedit.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/pedit.c

Purpose: Parses TC pedit mangle/add actions into mlx5 modify-header software shadow structures.

Important APIs: `mlx5e_tc_act_pedit_parse_action()` is shared by VLAN rewrite code. `mlx5e_tc_act_pedit` parses action entries, sets MOD_HDR, and for FDB updates split/output parse state.

Control flow: The parser rejects legacy unspecified pedit and namespaces without mod-hdr support. It maps header type to offsets inside `struct pedit_headers`, inverts the TC mask, and records masked values in set/add slots. Acting twice on the same masked location is rejected.

State and dependencies: Mutates `attr->parse_attr->hdrs[cmd]`, `attr->action`, `esw_attr->split_count`, and `parse_state->if_count`. Depends on `en/mod_hdr.h`, TC pedit constants, and namespace helpers.

Risks and tests: Offset and mask handling is sensitive to endianness and header layout. Tests should cover SET and ADD, duplicate location rejection, unsupported legacy pedit, namespace without mod-hdr actions, FDB split reset, and each supported header type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/pedit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/pedit.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/pedit.h

Purpose: Declares pedit header shadow structures and the shared pedit parse helper.

Important types: `struct pedit_headers` mirrors editable Ethernet, VLAN, IPv4, IPv6, TCP, and UDP header fields. `struct pedit_headers_action` stores value and mask shadows plus a pedit count.

Control flow and state: Higher-level parsers pass an array of `pedit_headers_action` for SET/ADD commands; this header defines the storage that later mod-header construction consumes.

Dependencies and integration: Includes `en_tc.h`; used by pedit and VLAN mangle/rewrite parsers.

Risks and tests: Struct layout must match offsets used by parsers. Tests should ensure VLAN rewrite and pedit share mask/value semantics and do not overlap fields incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/pedit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/police.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/police.c

Purpose: Handles TC police action parsing, standalone action lifecycle, meter creation/update/destruction, stats, and branch control for conform/exceed decisions.

Important APIs: `mlx5e_tc_act_police` supplies validation, parse, multi-table marker, offload/destroy/stats callbacks, and `get_branch_ctrl`. It uses `mlx5e_tc_meter_get()`, `replace()`, `update()`, `put()`, and stats helpers.

Control flow: Validation permits only pipe/accept/jump/drop controls and rejects peakrate/avrate/overhead. `fill_meter_params_from_act()` converts byte rate to bit rate, packet rate, or MTU mode. Parsing either sets execute-ASO flow meter or MTU range-match forwarding. Standalone offload gets or creates a meter; destroy performs two puts, one for the lookup and one for cleanup; stats query meter counters.

State and dependencies: Mutates `attr->meter_attr.params`, action bits, ASO type, MTU flag, and branch-control outputs. Persistent state is owned by `meter.c`. Depends on flow meter capability, flow steering range-match capability for MTU, extack, and `flow_stats_update()`.

Risks and tests: Refcount pairing in destroy is easy to regress. MTU mode skips ASO allocation but still uses meter handles/counters differently. Tests should cover BPS, PPS, MTU, unsupported controls, unsupported peakrate/avrate/overhead, missing meter subsystem, meter update path, destroy refcount, and stats reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/police.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/ptype.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/ptype.c

Purpose: Parses skbedit packet type action needed by redirect-to-ingress internal-port offload.

Important API: `mlx5e_tc_act_ptype` accepts only `PACKET_HOST` and sets `parse_state->ptype_host`.

Control flow and state: No persistent state; parse-state flag is later required by `redirect_ingress.c`.

Dependencies and integration: Uses action parser interface and `tc_priv`. Available in the FDB action table.

Risks and tests: Tests should verify non-host ptype is rejected and redirect_ingress fails unless ptype host was parsed earlier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/ptype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/redirect_ingress.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/redirect_ingress.c

Purpose: Parses FDB redirect-to-ingress actions for OVS internal ports.

Important API: `mlx5e_tc_act_redirect_ingress` validates OVS master destination, rejects redirect from an internal-port filter device, requires prior `ptype host`, requires no existing destinations, then programs internal-port ingress forwarding actions.

Control flow and state: Parsing sets FWD_DEST, calls `mlx5e_set_fwd_to_int_port_actions()` with `MLX5E_TC_INT_PORT_INGRESS`, resets `if_count`, and increments eswitch output count.

Dependencies and integration: Depends on OVS master netdev detection, internal-port helper code, extack, and parse-state `ptype_host`.

Risks and tests: It is valid only for a narrow ordered action sequence. Tests should cover missing ptype, non-OVS destination, source OVS filter dev, multiple destinations, internal-port creation failures, and metadata restore behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/redirect_ingress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/sample.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/sample.c

Purpose: Parses TC sample actions into mlx5 flow attributes and decides whether sampling requires a multi-table implementation.

Important APIs: `mlx5e_tc_act_sample` parses sample rate, psample group, optional truncation, sets `MLX5_ATTR_FLAG_SAMPLE`, and marks flow flag `SAMPLE`. `mlx5e_tc_act_sample_is_multi_table()` returns true when `reg_c_preserve` is supported or decap is present.

Control flow and state: No long-lived state here; it fills `attr->sample_attr` for the later offload implementation in `tc/sample.c`.

Dependencies and integration: Includes psample and `en/tc/sample.h`. The multi-table decision is reused by the full sample offload path.

Risks and tests: Tests should cover truncation enabled/disabled, group number propagation, rate propagation, decap requiring post-action path, and no-reg-preserve fallback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/sample.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/sample.h

Purpose: Declares the shared helper that determines whether a TC sample action should be implemented as a multi-table action.

Important API: `mlx5e_tc_act_sample_is_multi_table(struct mlx5_core_dev *mdev, struct mlx5_flow_attr *attr)`.

Control flow and state: No state. The declaration lets the action parser and sample offload implementation share one decision.

Dependencies and integration: Includes flow offload and `tc_priv` types. Used by `tc/act/sample.c` and `tc/sample.c`.

Risks and tests: The decision must stay synchronized with offload implementation capabilities. Tests should compile with sampling enabled and disabled, and verify decap/reg_c_preserve behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/sample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/trap.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/trap.c

Purpose: Parses TC trap action by forwarding matching packets to the eswitch slow FDB table.

Important API: `mlx5e_tc_act_trap` sets FWD_DEST and assigns `attr->dest_ft = mlx5_eswitch_get_slow_fdb()`.

Control flow and state: No persistent state; it mutates the current flow attr.

Dependencies and integration: Depends on eswitch slow FDB accessor and common action parser.

Risks and tests: Tests should verify trap routes to slow path and coexists with parser termination rules in the higher-level action loop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/trap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/tun.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/tun.c

Purpose: Parses tunnel encap/decap TC actions into parse-state flags consumed by later actions.

Important APIs: `mlx5e_tc_act_tun_encap` validates non-null tunnel info and sets `parse_state->tun_info`/`encap`. `mlx5e_tc_act_tun_decap` sets `parse_state->decap`.

Control flow and state: No persistent state. Encap parsing defers actual destination/tunnel duplication to mirred parsing; decap affects goto/sample/MPLS behavior later.

Dependencies and integration: Uses TC tunnel encap data, extack, and downstream tunnel encap/offload code.

Risks and tests: Action order is critical. Tests should cover null tunnel rejection, encap followed by redirect, decap followed by goto rejection, and sample with decap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/tun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan.c

Purpose: Parses VLAN push/pop, VLAN ethernet push/pop, and helper-generated VLAN adjustments for VLAN upper/lower devices in FDB offload.

Important APIs: `mlx5e_tc_act_vlan` parse/post-parse vtable. Shared helpers `mlx5e_tc_act_vlan_add_push_action()` and `mlx5e_tc_act_vlan_add_pop_action()` synthesize VLAN actions for mirred paths. `parse_tc_vlan_action()` handles VLAN depth, firmware support, push/pop action bits, eth push/pop parse-state flags, and VLAN metadata.

Control flow: Direct VLAN push after VLAN pop is converted into VLAN rewrite. Regular parsing records VLAN push/pop actions and resets FDB split/if_count. Post-parse replaces VLAN pop with priority-tag rewrite when firmware requires prio tags.

State and dependencies: Mutates `attr->esw_attr` VLAN fields, total VLAN depth, Ethernet header fields, action bits, parse-state eth flags, split count, and if_count. Depends on VLAN netdev helpers, firmware VLAN capabilities, pedit-based VLAN rewrite, and match-header accessors.

Risks and tests: VLAN depth and action-order interactions are easy to break. Tests should cover nested VLAN devices, pop+push rewrite, prio-tag-required rewrite, VLAN eth push only after L3-to-L2 decap, eth pop only with MPLS push, firmware unsupported depth, and split_count updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan.h

Purpose: Declares VLAN action helper APIs shared by mirred and VLAN mangle parsing.

Important APIs: `mlx5e_tc_act_vlan_add_push_action()`, `mlx5e_tc_act_vlan_add_pop_action()`, and `mlx5e_tc_act_vlan_add_rewrite_action()`.

Control flow and state: The helpers mutate `mlx5_flow_attr`, parse attributes, action bits, and possibly output netdev pointers; this header defines their call contract.

Dependencies and integration: Includes flow offload and `tc_priv`; used by `mirred.c`, `vlan.c`, and `vlan_mangle.c`.

Risks and tests: Because helpers are called from multiple parsers, tests should cover both explicit VLAN actions and implicit VLAN push/pop through VLAN netdev forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan_mangle.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan_mangle.c

Purpose: Implements VLAN rewrite/mangle by translating VLAN VID modification into a pedit modify-header action.

Important API: `mlx5e_tc_act_vlan_add_rewrite_action()` validates VLAN protocol match and unchanged priority, creates a synthetic pedit action at `vlan_ethhdr.h_vlan_TCI`, and sets MOD_HDR. `mlx5e_tc_act_vlan_mangle` invokes it and updates FDB split state.

Control flow and state: The helper reads match criteria/value from the flow spec to ensure a VLAN tag is matched and prio is not changed. It then calls the shared pedit parser.

Dependencies and integration: Depends on VLAN header layout, match-header accessors, pedit parser, extack, and namespace selection.

Risks and tests: Endianness and mask construction are critical. Tests should cover missing VLAN match rejection, priority-change rejection, VID rewrite success, FDB split reset, and pedit duplicate-field collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan_mangle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act_stats.c

Purpose: Tracks per-action hardware stats for TC actions by mapping TC action cookies to mlx5 flow counters and returning deltas to flow offload action stats.

Important APIs: `mlx5e_tc_act_stats_create()`, `free()`, `add_flow()`, `del_flow()`, and `fill_stats()`.

Control flow: Creation initializes an auto-shrinking rhashtable. `add_flow()` walks each flow attr, carrying the current counter and adding unique consecutive action cookies to the table. `del_flow()` removes all cookies for flows marked `USE_ACT_STATS` under a spinlock and frees entries with RCU. `fill_stats()` looks up a cookie, queries cached raw counter values, reports deltas from saved last values, and updates saved counters.

State and persistence: `mlx5e_tc_act_stats_handle` owns the rhashtable and spinlock. Each entry stores cookie, counter pointer, last packets/bytes, hash node, and RCU head. State persists until flow deletion or handle free.

Dependencies and integration: Uses rhashtable, RCU, mlx5 flow counters, `flow_stats_update()`, and TC flow attrs/cookies.

Risks and tests: `fill_stats()` updates last counters under only RCU read lock, so concurrent stats reads for the same cookie could race. Add-flow rollback deletes all entries for the flow. Tests should cover duplicate cookies, missing counters, add failure rollback, delete under concurrent lookup, delta correctness, and `USE_ACT_STATS` disabled flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act_stats.h

Purpose: Declares the TC action stats handle and lifecycle/flow/stats APIs.

Important APIs: `mlx5e_tc_act_stats_create()`, `mlx5e_tc_act_stats_free()`, `mlx5e_tc_act_stats_add_flow()`, `mlx5e_tc_act_stats_del_flow()`, and `mlx5e_tc_act_stats_fill_stats()`.

Control flow and state: Callers create one handle, add flows after successful offload, remove flows on teardown, and query stats by action cookie.

Dependencies and integration: Includes flow offload and TC private types; implementation depends on mlx5 counters and rhashtable.

Risks and tests: API users must pair add/delete and avoid querying after handle free. Tests should cover missing cookie returning `-ENOENT` and cleanup ordering during flow deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs.h

Purpose: Defines an abstract connection-tracking flow-steering backend interface with DMFS, SMFS, and HMFS implementations.

Important types: `struct mlx5_ct_fs` holds netdev, device, and backend private storage. `struct mlx5_ct_fs_rule` is an opaque base. `struct mlx5_ct_fs_ops` supplies init/destroy, CT rule add/delete/update, and `priv_size`.

Control flow and state: CT owner selects a backend by calling `mlx5_ct_fs_dmfs_ops_get()`, `mlx5_ct_fs_smfs_ops_get()`, or `mlx5_ct_fs_hmfs_ops_get()`, allocates `struct mlx5_ct_fs` with `priv_size`, initializes against CT/CT-NAT/post-CT tables, then manages backend rules through the ops table.

Dependencies and integration: Conditional declarations depend on `CONFIG_MLX5_SW_STEERING` and `CONFIG_MLX5_HW_STEERING`. Backends integrate with legacy TC rule insertion, software steering DR, or hardware steering HWS.

Risks and tests: `mlx5_ct_fs_priv()` returns private flexible-array storage; allocation size must include `priv_size`. Tests should cover backend selection under config permutations and rule lifecycle through the abstract ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_dmfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_dmfs.c

Purpose: Provides the direct/legacy mlx5 TC rule backend for CT flow steering.

Important API: `mlx5_ct_fs_dmfs_ops_get()` returns ops whose init/destroy are no-ops and whose add/delete/update wrap `mlx5_tc_rule_insert()` and `mlx5_tc_rule_delete()`.

Control flow: Rule add allocates `mlx5_ct_fs_dmfs_rule`, inserts a TC rule, stores attr, and returns the embedded base. Update inserts a replacement rule first, deletes the old rule, then swaps handle/attr. Delete removes the stored rule and frees the wrapper.

State and dependencies: Per-rule state is only flow handle and attr pointer. Depends on netdev-private `mlx5e_priv`, `en_tc.h`, and `tc_ct` definitions.

Risks and tests: Update is not fully atomic if insertion succeeds and deletion has side effects, but it avoids deleting before replacement. Tests should cover add allocation failure, insert failure, update insert failure preserving old rule, update success, and delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_dmfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_hmfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_hmfs.c

Purpose: Provides the hardware steering (HWS/HMFS) backend for CT flow steering using HWS tables, BWC matchers, HWS actions, and BWC rules.

Important APIs: `mlx5_ct_fs_hmfs_ops_get()` returns ops. Init captures CT, CT-NAT, and post-CT HWS tables and creates shared forward and last actions. Rule add validates the flow rule, gets a matcher keyed by NAT/IP version/protocol, fills counter/modify/fwd/last actions, creates a BWC rule, and stores counter/matcher refs. Update replaces rule actions and swaps counter ownership. Delete destroys the rule, releases the HWS counter action, matcher, and wrapper.

State and persistence: `struct mlx5_ct_fs_hmfs` owns HWS table pointers, context, shared actions, a lock, and two arrays of six refcounted matchers for NAT/non-NAT combinations. Per-rule state owns a BWC rule, matcher ref, and counter pointer.

Dependencies and integration: Uses HWS pools/actions/tables, flow counters as HWS actions, CT validity helpers, IP version helpers, modify header HWS action data, and post-CT table forwarding.

Risks and tests: Matcher refcounting and action ownership are high risk. `get_matcher_idx()` encodes protocol combinations; unsupported protocols collapse to UDP slot when not TCP/GRE. Error paths must release `mlx5_fc_get_hws_action()` ownership. Tests should cover missing HWS tables, matcher creation races, NAT and non-NAT matchers, IPv4/IPv6 TCP/UDP/GRE, add failure after matcher get, action update failure, counter swap, and destroy order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_hmfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_smfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_smfs.c

Purpose: Provides the software steering (SMFS/DR) backend for CT flow steering.

Important APIs: `mlx5_ct_fs_smfs_ops_get()` returns ops. Init extracts DR tables, creates a forward action to post-CT, initializes matcher lists. Rule add validates flow rule, creates a flow-counter action, gets a protocol matcher, and creates a DR rule with counter, modify-header, and forward actions. Update creates a replacement rule on the existing matcher and destroys the old rule. Delete destroys rule, matcher ref, counter action, and wrapper.

State and persistence: `struct mlx5_ct_fs_smfs` owns CT/CT-NAT DR tables, matcher pools for NAT/non-NAT, a shared fwd action, CT-NAT table pointer, and lock. Matchers are refcounted and maintained in priority-sorted used lists.

Dependencies and integration: Uses `lib/smfs`, mlx5 DR matcher/action/rule APIs, CT validity helpers, flow spec match masks, and `ZONE_TO_REG` register matching.

Risks and tests: Mask generation must match CT tuple semantics for IPv4/IPv6 and TCP/UDP/GRE. Priority allocation through a sorted used list can regress with concurrent matcher creation/destruction. Tests should cover backing table absence, all protocol matcher combinations, NAT vs non-NAT, update failure preserving old rule, count action cleanup, and matcher refcount/list removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_smfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/int_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/int_port.c

Purpose: Manages OVS internal-port offload objects, metadata mappings, RX restore rules, and skb forwarding for internal ingress/egress ports.

Important APIs: `mlx5e_tc_int_port_supported()`, init/cleanup, rep RX init/cleanup, get/put, metadata getters, flow source getter, and `mlx5e_tc_int_port_dev_fwd()`.

Control flow: Init creates a metadata mapping context keyed by SW image GUID. `get()` locks, checks uplink RX readiness, looks up an existing `(ifindex,type)` object or allocates one. Allocation reserves metadata, maps it into reg_c0 object pool for miss handling, creates an RX rule matching metadata and forwarding to uplink root FT, adds the object to an RCU list, and sets refcount. Put removes and frees on last reference. Rep RX cleanup marks RX not ready and deletes RX rules in-place while preserving objects.

State and persistence: `mlx5e_tc_int_port_priv` owns device, mutex, RCU list, port count, readiness flag, and metadata mapping. Each internal port stores type, ifindex, match metadata, reg_c0 mapping id, RX rule, refcount, and RCU head.

Dependencies and integration: Requires eswitch vport metadata and `reg_c_preserve`, mapping API, reg_c0 object pool, uplink representor root table, flow rules, and skb forwarding helpers. Action parsers call into this code to program internal-port actions.

Risks and tests: Cleanup currently destroys the mutex and mapping without explicitly draining the int-port list; expected callers must release refs first. RX teardown leaves objects with `rx_rule = NULL`, so add/remove paths must tolerate it. `mlx5e_tc_int_port_dev_fwd()` uses `init_net` and does not `dev_put()` after `dev_get_by_index()`, which should be reviewed for reference handling in the broader code. Tests should cover max port count, duplicate get refcounting, metadata allocation/free, rep RX teardown/reinit, ingress/egress skb rewrite, unsupported caps, and concurrent get/put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/int_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/int_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/int_port.h

Purpose: Declares internal-port offload types and APIs, with stubs for builds without `CONFIG_MLX5_CLS_ACT`.

Important types and APIs: `enum mlx5e_tc_int_port_type` distinguishes ingress and egress internal ports. APIs cover support check, init/cleanup, representor RX lifecycle, skb forwarding, get/put, metadata accessors, and flow-source selection.

Control flow and state: Callers obtain a refcounted `mlx5e_tc_int_port` and later put it; metadata and flow source are used when building match/action rules.

Dependencies and integration: Includes `en.h`; consumed by TC action parsers and offload restore paths.

Risks and tests: Stub coverage is incomplete for some functions when `CONFIG_MLX5_CLS_ACT` is disabled; compile configurations should be tested. Runtime tests should cover ingress vs egress flow source and metadata matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/int_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/meter.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/meter.c

Purpose: Implements mlx5e TC flow meter resources using ASO flow meter objects, flow counters, meter handle refcounting, rate/burst encoding, and stats aggregation.

Important APIs: `mlx5e_flow_meters_init()`/`cleanup()`, `mlx5e_tc_meter_get()`, `put()`, `replace()`, `update()`, `modify()`, `get_stats()`, `get_namespace()`, and `mlx5e_flow_meter_get_base_id()`.

Control flow: Initialization checks flow-meter ASO capability and post-action availability, allocates a PD and ASO SQ, and initializes lists/hash. Meter allocation creates action/drop counters and, for rate meters, allocates a slot from a partial ASO object or creates a new object. `modify()` converts BPS/PPS rate and burst to hardware mantissa/exponent fields, builds an ASO WQE, posts it under `aso_lock`, and polls completion. `replace()` gets or allocates a handle under `sync_lock` then updates params. `put()` decrements refcount and frees counters/ASO slot/object at zero.

State and persistence: `mlx5e_flow_meters` owns namespace, ASO, locks, PDN, hash table, partial/full ASO object lists, device, and post_act. Meter handles own counters, ASO object slot, params, refcount, and hash node. ASO objects persist until all slots are free.

Dependencies and integration: Uses mlx5 ASO, general object commands, flow counters, post-action subsystem, TC police parser, QoS caps, and kernel bitmap/list/hash utilities.

Risks: Rate conversion truncates to closest representable hardware value and rejects zero or oversized CIR/CBS. PPS mode scales rate/burst. Cleanup does not walk the hash/list to free live meters, so users must release all handles first. Refcount is plain int protected by `sync_lock`. Tests should cover BPS/PPS/MTU allocation, ASO slot reuse and full/partial list transitions, max burst clamp, invalid rate/burst, ASO command failure, replace update path, stats aggregation, and cleanup with no live meters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/meter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/meter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/meter.h

Purpose: Declares flow meter parameter, handle, and meter attribute types plus lifecycle/update/stat APIs.

Important types: `enum mlx5e_flow_meter_mode` selects BPS or PPS. `struct mlx5e_flow_meter_params` carries police index, rate, burst, and MTU. `struct mlx5e_flow_meter_handle` owns flow-meter subsystem pointer, ASO object slot, refcount, params, hash node, action counter, and drop counter. `struct mlx5e_meter_attr` embeds params and post-meter linkage.

Control flow and state: Police parsing fills params, then offload code gets/replaces/updates handles and releases them via `put()`. Stats aggregate action and drop counters.

Dependencies and integration: Used by police action parser, post-meter steering, and TC private flow attrs. `mlx5e_flow_meter_get_base_id()` has a stub when class-act support is disabled.

Risks and tests: Callers must not dereference ASO fields for MTU-only meters. Tests should compile with `CONFIG_MLX5_CLS_ACT` on/off and validate get/put/refcount API usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/meter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_act.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_act.c

Purpose: Implements post-action steering: a global table matching a generated FTE id in a register and applying deferred TC rule actions.

Important APIs: `mlx5e_tc_post_act_init()`/`destroy()`, `add()`/`del()`, `offload()`/`unoffload()`, `get_ft()`, and `set_handle()`.

Control flow: Init requires ignore-flow-level support, creates a global chains table, and initializes an xarray allocator. `add()` normalizes the post attr to chain/prio zero, strips decap, sets no-in-port, resets FDB split count, and allocates a handle id. `offload()` creates a spec matching `FTEID_TO_REG` to handle id and offloads the rule. `set_handle()` emits a modify-header action that writes the handle id into the register.

State and persistence: `mlx5e_post_act` owns namespace, chains, global FT, priv, and xarray ids. Each handle owns namespace, attr, rule, and id. Hardware table/rules persist until unoffload/destroy.

Dependencies and integration: Uses fs chains, register mapping helpers, TC rule offload/unoffload, mod-header actions, and firmware flow-table capabilities. It is used by sample, meter, and multi-table action chaining.

Risks and tests: The xarray id limit is derived from register bit width; exhaustion returns errors. Destroy assumes handles/rules are already cleaned up. Tests should cover unsupported firmware, id allocation/free/reuse, FDB split reset, decap stripping, set_handle mod-header failure, and offload/unoffload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_act.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_act.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_act.h

Purpose: Declares the post-action steering subsystem interface and opaque handle types.

Important APIs: Init/destroy, add/del, offload/unoffload, table getter, and handle-to-register modify-header setup.

Control flow and state: Callers create a post-action context for a namespace/chains pair, allocate handles for deferred attrs, offload matching rules, and add register-setting actions to previous rules.

Dependencies and integration: Includes mlx5e core types and fs chains; used by TC action parsing/offload code that needs multi-table continuation.

Risks and tests: Handle lifecycle must be paired carefully with rule offload. Tests should include add failure, offload failure cleanup, and using `get_ft()` for sample/default table paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_act.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_meter.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_meter.c

Purpose: Creates post-meter steering tables that branch on meter color or MTU result and forward to conform/exceed flow attributes with shared counters.

Important APIs: `mlx5e_post_meter_init()`, `cleanup()`, and getters for rate FT and MTU true/false FTs.

Control flow: Rate mode creates one unmanaged table, a flow group matching packet color register C5, and two rules for red and green colors. MTU mode creates separate green/red tables with miss groups and zero-spec rules. `mlx5e_post_meter_add_rule()` attaches action/drop counters according to branch action, sets no-in-port and match levels, offloads through eswitch, and clears COUNT from attr afterward to avoid freeing counters it does not own.

State and persistence: `mlx5e_post_meter_priv` stores type and either a rate table with green/red rules/attrs or MTU tables with separate FTs/groups/rules/attrs. Hardware flow tables, groups, and rules persist until cleanup.

Dependencies and integration: Uses packet color register mapping, eswitch rule offload, flow table namespace lookup, flow counters from meter handles, post-action/meter branching attrs, and FDB slow-path priorities.

Risks and tests: Cleanup assumes initialization fully succeeded for the selected type. Error paths must destroy already-created tables/groups/rules. Counter ownership is intentionally borrowed. Tests should cover rate red/green branch action selection, MTU true/false tables, missing namespace, rule creation failure at each step, cleanup ordering, and COUNT flag clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_meter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_meter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_meter.h

Purpose: Declares post-meter branching types, packet color register mapping, table getters, init, and cleanup APIs.

Important types and APIs: `packet_color_to_reg` maps packet color into metadata register C5. `enum mlx5e_post_meter_type` selects rate or MTU branching. APIs expose FTs and create/cleanup post-meter state when class-act support is enabled.

Control flow and state: Police/meter offload uses these tables to branch from ASO color or MTU comparison to true/false attrs.

Dependencies and integration: Depends on mlx5 flow table/counter/eswitch types and class-act config stubs.

Risks and tests: Stub behavior should be compiled for disabled class-act builds. Runtime tests should confirm branch tables returned by getters match the selected mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_meter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/sample.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/sample.c

Purpose: Implements the full TC psample offload model for eswitch/FDB flows using sampler objects, termination table, restore mappings, optional post-action table, and per-vport default tables.

Important APIs: `mlx5e_tc_sample_init()`/`cleanup()`, `mlx5e_tc_sample_offload()`/`unoffload()`, and `mlx5e_tc_sample_skb()`.

Control flow: Init creates a termination table forwarding sampled packets to the manager vport and initializes sampler/restore hash locks. Offload allocates a sample flow, selects post-action table or per-vport default table, gets or creates a sampler object keyed by rate and default table, maps sample restore data in reg_c0 object pool, gets or creates a restore modify-header/rule, creates a pre-rule that points to the sampler object and writes restore metadata, and stores pointers in `attr->sample_attr`. Unofoffload deletes the pre-rule first, then restore mapping, sampler, optional post rule, attrs, and wrapper. `mlx5e_tc_sample_skb()` sends restored packets to psample with truncation metadata.

State and persistence: `mlx5e_tc_psample` owns eswitch, termination table/rule, sampler hash, restore hash, locks, and post_act. Samplers are refcounted by `(ratio, default_table_id)`. Restore contexts are refcounted by object id and own modify header plus restore rule. Per-flow state links sampler, restore, pre/post attrs/rules.

Dependencies and integration: Uses psample, eswitch vport tables, mapping API, post-action subsystem, mod-header register setters, sampler general object commands, termination table capability, and TC sample action parser state.

Risks: Delete order is firmware-sensitive and documented as fixed. Restore count is checked outside the lock after decrement, which relies on no resurrection after zero. `mlx5e_tc_sample_skb()` pushes MAC header before sampling and should be tested for skb layout assumptions. Tests should cover capability failures, sampler reuse/refcount, restore reuse/refcount, reg_c preserve vs per-vport default path, decap path, encap slow-path source-port clearing, error unwinds at every allocation/offload step, and sample skb truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/sample.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/sample.h

Purpose: Declares TC psample offload state, sample attributes embedded in flow attrs, and sampling APIs with disabled-config stubs.

Important types and APIs: `struct mlx5e_sample_attr` stores group number, rate, trunc size, restore object id, sampler id, and per-flow sample state pointer. APIs cover skb sampling, offload/unoffload, init, and cleanup.

Control flow and state: The action parser fills `mlx5e_sample_attr`; the offload implementation populates restore/sampler ids and per-flow state; teardown uses those fields to free hardware resources.

Dependencies and integration: Includes eswitch types and depends on `CONFIG_MLX5_TC_SAMPLE` for real implementations.

Risks and tests: Callers must handle `-EOPNOTSUPP` stubs when sample support is disabled. Tests should compile enabled/disabled configs and validate attr fields are initialized before offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/sample.h -->

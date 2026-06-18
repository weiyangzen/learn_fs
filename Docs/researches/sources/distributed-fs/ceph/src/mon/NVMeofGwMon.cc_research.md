# sources/distributed-fs/ceph/src/mon/NVMeofGwMon.cc

## Purpose
`NVMeofGwMon.cc` implements the monitor Paxos service for NVMe-oF gateway HA maps. It loads and commits `NVMeofGwMap` versions, handles admin commands, receives gateway beacons, sends map ACKs/slices to gateways, tracks beacon timeouts, periodically advances map state, and exposes gateway status/listener queries.

## Important APIs, Functions, and Types
Lifecycle functions include `init()`, `on_restart()`, `on_shutdown()`, `create_pending()`, `encode_pending()`, `update_from_paxos()`, `get_trim_to()`, `cleanup_pending_map()`, `restore_pending_map_info()`, `recreate_gw_epoch()`, and `synchronize_last_beacon()`.

Periodic/subscription functions are `tick()`, `check_beacon_timeout()`, `check_subs()`, `check_sub_unconditional()`, `check_sub()`, and `get_gw_by_addr()`. Command handlers are `preprocess_query()`, `prepare_update()`, `preprocess_command()`, `prepare_command()`, and `get_gw_listeners()`. Beacon flow is implemented in `preprocess_beacon()`, `prepare_beacon()`, `apply_beacon()`, `process_gw_down()`, `get_ack_map_epoch()`, and `do_send_map_ack()`.

## Control Flow
On restart, the service clears `last_beacon`, resets the pending map, and calls `synchronize_last_beacon()` to seed timeout tracking for gateways that were available in the committed map. That function also forces gateways to receive ACK/full map information after leader election by setting beacon indexes and sequence/out-of-order flags.

`tick()` is leader-only and active-only. It compensates for missed monitor ticks by resetting beacon timestamps, then asks `pending_map` to expire active FSM timers, checks beacon timeouts, tracks deleting gateways using any live subsystem snapshot in each group, auto-enables beacon diff once the monitor quorum supports `FEATURE_NVMEOF_BEACON_DIFF`, handles abandoned ANA groups, and proposes if any of those actions changed pending state.

Paxos proposal flow mirrors other monitor services. `create_pending()` saves the previous pending map, copies committed `map`, restores selected non-persistent gateway fields, and increments epoch. `encode_pending()` asserts the expected next epoch, recreates missing `gw_epoch` entries under `NVMEOFHAMAP`, encodes with quorum features, stores the version and last-committed marker, and persists health checks. `update_from_paxos()` decodes the latest committed version, loads health, and notifies subscriptions.

Read commands are handled in `preprocess_command()`. `nvme-gw show` prints group epoch, beacon-diff status, feature/load-balancing hints, ANA group list, namespace counts, per-gateway location/admin/availability/startup/listener/state data, and disaster state. `nvme-gw listeners` aggregates live listeners by subsystem NQN and gateway id.

Mutating commands are handled in `prepare_command()`. `nvme-gw create/delete`, `enable/disable`, `set-location`, `disaster-set`, `disaster-clear`, and `set beacon-diff` call matching `NVMeofGwMap` mutators. If a real map change is needed, the command waits for the next commit; otherwise it replies immediately with errors or idempotent success.

Beacon handling is the most important runtime flow. `preprocess_beacon()` always returns false so the leader prepare path runs. `prepare_beacon()` parses gateway id, pool/group, beacon version, header version, sequence, reported availability, last OSD epoch, last gateway-map epoch, and subsystem list. A `GW_CREATED` beacon from a known gateway clears subsystems, sets beacon sequence, handles fast reboot by marking the old available gateway down and suppressing failovers briefly, records startup/address state, and refreshes `last_beacon`. Non-created beacons from unknown or deleting gateways are ignored/no-replied.

For existing gateways, enhanced beacon sequence numbers are checked. Out-of-order available beacons suppress failover briefly and force the gateway back through created/full-map handling. `apply_beacon()` either replaces full subsystem state for legacy beacons or applies add/change/delete subsystem deltas for enhanced beacons. It also clears old nonce maps when diff mode takes over and derives effective availability from admin state, subsystem presence, and listener presence. Available beacons refresh timeout state and call `process_gw_map_ka()`; unavailable or created states call `process_gw_down()`.

ACK logic deliberately separates proposal from response. The monitor periodically ACKs available correct-sequence beacons according to `mon_nvmeofgw_beacons_till_ack`, always ACKs cases that need recovery/full-map behavior, and sends an ACK immediately when no conflicting proposal is pending or when the gateway is in created state. ACK maps may contain a single gateway slice and use per-group `gw_epoch` when available.

## State and Persistence
Committed durable state is `map`; uncommitted state is `pending_map`. `last_beacon` and `last_beacon_check` are runtime timeout state, not encoded in Paxos. `gws_deleting_time` tracks how long gateways have been in deleting state for health warnings and is also runtime state. Selected non-persistent gateway fields (`allow_failovers_ts`, down/failback timestamps, map-epoch validity, beacon index, beacon sequence and out-of-order flag) are restored across pending map recreation.

Old NVMe-oF map versions are trimmed according to `mon_max_nvmeof_epochs`; the service keeps only a bounded history.

## Dependencies and Integration Points
The service integrates `PaxosService`, `md_config_obs_t`, `Monitor`, monitor sessions/subscriptions, `MMonCommand`, `MNVMeofGwBeacon`, `MNVMeofGwMap`, `NVMeofGwMap`, monitor feature negotiation, OSDMonitor through map blocklisting requests, and monitor health encoding. Gateway clients depend on ACK/map semantics for liveness and ANA ownership transitions.

## Risks
Beacon and timer handling is sensitive to monitor leadership gaps and local slowness; the tick compensation resets beacon clocks after missed ticks to avoid false failovers. `check_beacon_timeout()` erases entries while iterating over `last_beacon`, which should be scrutinized for C++ iterator correctness. Command preprocessing for read paths uses `map.created_gws[group_key]`, which can create empty groups in a non-const map if not carefully guarded.

ACK decisions combine feature bits, proposal state, gateway availability, sequence correctness, and beacon index; regressions could either spam ACKs or starve gateways of map updates. Runtime-only fields restored in `restore_pending_map_info()` are easy to miss when new fields are added. Unknown/deleting gateways get `no_reply`, so client retry behavior is part of the contract.

## Test Signals
Tests should cover restart synchronization, beacon-timeout suppression after missed ticks, Paxos encode/load/trim, subscription full-map versus unicast-map behavior, command idempotency and error replies, beacon created/available/unavailable paths, fast reboot suppression, out-of-order sequence ACKs, legacy full subsystem replacement, enhanced subsystem diff application, no-subsystem/no-listener downgrade, ACK epoch selection, and health updates after map changes.

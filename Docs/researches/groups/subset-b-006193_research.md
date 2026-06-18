# subset-b-006193 Research

Grouped code research for the Ceph client copy of Linux ethtool ioctl and netlink handlers under `sources/distributed-fs/ceph-client/net/ethtool`. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/ioctl.c -->
# sources/distributed-fs/ceph-client/net/ethtool/ioctl.c

## Purpose
This file implements the legacy `SIOCETHTOOL` ioctl entry point for network devices. It adapts user-space `ETHTOOL_*` command structs to `struct ethtool_ops`, PHY helpers, SFP helpers, RSS context tracking, feature toggles, devlink compatibility fallbacks, and netlink notifications.

## Important APIs, Types, And Functions
The public exports include `ethtool_op_get_link()`, `ethtool_op_get_ts_info()`, `__ethtool_get_link_ksettings()`, link-mode conversion helpers, `ethtool_virtdev_set_link_ksettings()`, `netdev_rss_key_fill()`, `ethtool_sprintf()`, `ethtool_puts()`, `dev_ethtool()`, `ethtool_rx_flow_rule_create()`, and `ethtool_rx_flow_rule_destroy()`. The main internal dispatcher is `__dev_ethtool()`, which switches on `ETHTOOL_*` commands after capability checks and driver begin/complete bracketing.

Major command families cover features, flags, link settings, driver info, string sets, RX NFC and RSS hash configuration, registers, WOL, EEE, EEPROM/module EEPROM, coalesce/ring/channel/pause parameters, self tests, stats, PHY stats/tunables, FEC, dumps, firmware flash fallback, and packet classification rule conversion.

## Control Flow
`dev_ethtool()` copies the command word, preloads flash-specific state, takes RTNL, calls `__dev_ethtool()`, then performs post-RTNL devlink fallbacks for flash updates and firmware version filling. `__dev_ethtool()` resolves the interface name, gates privileged commands with `CAP_NET_ADMIN`, locks netdev ops, performs runtime PM, checks device presence, calls optional `begin()`, dispatches to the command helper, calls `complete()`, reports feature changes, and releases locks.

Variable-length ioctl protocols are two-phase: handlers first exchange sizes/counts, allocate `kcalloc()` or `vzalloc()` buffers, call driver hooks, then copy results back. RSS handlers additionally hold `dev->ethtool->rss_lock` while validating indirection tables, hash keys, input transforms, and context xarray entries.

## State And Persistence
Most state changes are stored in the device or driver through `ethtool_ops`; ioctl state itself is transient. The file updates `dev->wanted_features`, `dev->ethtool->wol_enabled`, `dev->ethtool->rss_indir_user_size`, and `dev->ethtool->rss_ctx`. RSS contexts persist in the device ethtool xarray until removed. Module firmware flashing state is consulted through `dev->ethtool->module_fw_flash_in_progress` to block resets, module EEPROM reads, and some settings.

## Dependencies And Integration Points
The file depends on netdevice core locking, runtime PM, `ethtool_ops`, `ethtool_phy_ops`, PHY drivers, SFP buses, devlink compatibility helpers, flow dissector/offload APIs, RSS context helpers, and netlink notifications through `ethtool_notify()` and `ethtool_rss_notify()`. It is the legacy peer of `net/ethtool/netlink.c`: many successful ioctl mutations emit the same `ETHTOOL_MSG_*_NTF` notifications used by the generic netlink interface.

## Risks And Edge Cases
The ioctl ABI has many size handshakes and compatibility paths; malformed userspace buffers can return `-EFAULT`, `-EINVAL`, `-ETOOSMALL`, or silent zero-length replies depending on legacy convention. `ethtool_phys_id()` drops RTNL while blinking and uses a static `busy` flag, so only one physical identification operation can run globally. RSS context creation must unwind xarray entries on driver failure and avoid deleting busy contexts. Several legacy conversions lose high link-mode bits and warn rather than failing. `ethtool_get_dump_data()` allocates the full driver dump length even for partial user reads.

## Test Signals
Useful validation signals are ioctl ABI tests in ethtool/kselftest coverage, driver-specific ethtool selftests, RSS context create/modify/delete tests, syzkaller coverage for variable-length copy paths, and netlink monitor checks confirming ioctl mutations emit matching notifications. Focused tests should exercise compat `ethtool_rxnfc`, RSS transform validation, busy queue rejection in channel downsizing, module flashing blockers, and devlink fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/linkinfo.c -->
# sources/distributed-fs/ceph-client/net/ethtool/linkinfo.c

## Purpose
This file implements generic netlink `LINKINFO_GET` and `LINKINFO_SET` handling for physical link metadata: port type, PHY address, MDI/MDI-X state, MDI-X control, and transceiver type.

## Important APIs, Types, And Functions
`struct linkinfo_req_info` embeds `ethnl_req_info`. `struct linkinfo_reply_data` stores `struct ethtool_link_ksettings` and a pointer to its base `struct ethtool_link_settings`. `ethnl_linkinfo_get_policy`, `ethnl_linkinfo_set_policy`, and `ethnl_linkinfo_request_ops` are the exported integration objects. The main callbacks are `linkinfo_prepare_data()`, `linkinfo_reply_size()`, `linkinfo_fill_reply()`, `ethnl_set_linkinfo_validate()`, and `ethnl_set_linkinfo()`.

## Control Flow
GET calls `ethnl_ops_begin()`, retrieves link ksettings through `__ethtool_get_link_ksettings()`, completes driver ops, sizes five `u8` attributes, and emits them. SET validates the driver has both `get_link_ksettings` and `set_link_ksettings`, fetches current settings, updates only supplied attributes via `ethnl_update_u8()`, returns no-op when unchanged, otherwise calls the driver's `set_link_ksettings()`.

## State And Persistence
The file stores no persistent state. SET mutates driver-maintained link settings through the ethtool ops callback. The generic set wrapper in `netlink.c` emits `ETHTOOL_MSG_LINKINFO_NTF` when the callback reports a change.

## Dependencies And Integration Points
It depends on the shared netlink request framework in `netlink.c`/`netlink.h`, common ethtool ksettings helpers in `ioctl.c`, and driver `ethtool_ops`. It shares the same `ethtool_link_ksettings` object with `linkmodes.c`, splitting metadata from advertised modes and speed/duplex fields for netlink ABI purposes.

## Risks And Edge Cases
Unsupported drivers return `-EOPNOTSUPP`. The setter does not locally validate enumerated port or MDI-X values, relying on netlink policy type checks and the driver. Because it rewrites the whole ksettings structure after changing a few base fields, drivers must tolerate unchanged link mode fields being passed back.

## Test Signals
Tests should cover GET on devices with and without `get_link_ksettings`, no-op SET, SET failure propagation, and notification emission. Good integration checks compare ioctl `GLINKSETTINGS`/`GSET` output with netlink `LINKINFO_GET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/linkinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/linkmodes.c -->
# sources/distributed-fs/ceph-client/net/ethtool/linkmodes.c

## Purpose
This file implements netlink `LINKMODES_GET` and `LINKMODES_SET`, covering autonegotiation, advertised and peer link mode bitsets, speed, duplex, lane count, master/slave configuration and state, and rate matching.

## Important APIs, Types, And Functions
`struct linkmodes_reply_data` carries `ethtool_link_ksettings`, the base link settings pointer, and a `peer_empty` flag. Important callbacks are `linkmodes_prepare_data()`, `linkmodes_reply_size()`, `linkmodes_fill_reply()`, `ethnl_auto_linkmodes()`, `ethnl_check_linkmodes()`, `ethnl_update_linkmodes()`, `ethnl_set_linkmodes_validate()`, and `ethnl_set_linkmodes()`. `ethnl_linkmodes_request_ops` registers the handlers.

## Control Flow
GET fetches ksettings under `ethnl_ops_begin()`, masks `lanes` to zero for drivers without lane support, records whether link-partner advertising is empty, computes bitset sizes with compact-bitset awareness, and emits our/peer bitsets plus scalar fields.

SET first validates master/slave values and lane power-of-two/range rules. It fetches current ksettings, applies requested autoneg, advertising bitset, speed, lanes, duplex, and master/slave configuration. If autonegotiation is enabled and userspace requested speed, lanes, or duplex without explicit advertising, `ethnl_auto_linkmodes()` rebuilds advertising from supported modes matching those constraints. Modified settings are committed through `set_link_ksettings()`.

## State And Persistence
No state is held in this file. Persistent behavior is delegated to the driver and PHY/link management. Notifications use `ETHTOOL_MSG_LINKMODES_NTF` through the generic set wrapper.

## Dependencies And Integration Points
The file depends on `bitset.h` helpers for named netlink bitsets, global `link_mode_names` and `link_mode_params`, ksettings helpers from `ioctl.c`, and driver `ethtool_ops`. It complements `linkinfo.c`: both operate on the same kernel ksettings snapshot.

## Risks And Edge Cases
Lane handling is subtle: lane configuration is allowed only as powers of two from 1 to 8 and can be rejected if autoneg is off and the driver lacks `cap_link_lanes_supported`. When autoneg is off and lanes were previously set but omitted in a new request, the code clears lanes to zero. The auto-advertising behavior intentionally emulates ioctl userspace behavior in kernel; mismatches in `link_mode_params` can select unexpected advertising masks.

## Test Signals
Tests should cover compact and verbose bitset encodings, peer bitset omission, invalid master/slave and lane values, auto-advertising when autoneg is enabled, lane clearing when autoneg is disabled, no-op SET, and notification emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/linkmodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/linkstate.c -->
# sources/distributed-fs/ceph-client/net/ethtool/linkstate.c

## Purpose
This file implements netlink `LINKSTATE_GET`, reporting carrier state, PHY signal quality indicator values, extended link state/substate, and optional link-down statistics.

## Important APIs, Types, And Functions
`struct linkstate_reply_data` stores link state, SQI/SQI max, `struct ethtool_link_ext_stats`, and `struct ethtool_link_ext_state_info`. Key helpers are `linkstate_get_sqi()`, `linkstate_get_sqi_max()`, `linkstate_sqi_critical_error()`, `linkstate_sqi_valid()`, `linkstate_get_link_ext_state()`, `linkstate_prepare_data()`, `linkstate_reply_size()`, and `linkstate_fill_reply()`. `ethnl_linkstate_request_ops` registers GET handling.

## Control Flow
Preparation resolves an optional target PHY with `ethnl_req_get_phydev()`, enters driver ops, reads link with `__ethtool_get_link()`, queries SQI and SQI max while holding `phydev->lock`, and suppresses non-critical `-EOPNOTSUPP`/`-ENETDOWN` SQI failures. If the netdevice is up, it queries driver extended link state and accepts lack of data. Optional stats are initialized to `ETHTOOL_STAT_NOT_SET` and filled from PHY and netdevice hooks when `ETHTOOL_FLAG_STATS` is present.

## State And Persistence
The file is read-only. It snapshots current carrier, PHY quality, extended state, and counters into reply data without persisting anything.

## Dependencies And Integration Points
It depends on PHY driver `get_sqi`/`get_sqi_max`, device `get_link_ext_state` and `get_link_ext_stats`, `phy_ethtool_get_link_ext_stats()`, the shared netlink header policies with stats support, and link-state ioctl helper `__ethtool_get_link()`.

## Risks And Edge Cases
SQI is emitted only if both values are nonnegative and `sqi <= sqi_max`; invalid pairs are silently omitted. Critical SQI driver errors abort the whole request, while unsupported/down states are tolerated. Extended link state is queried only when `IFF_UP` is set, so down devices can report carrier false without richer reason data.

## Test Signals
Tests should cover absent PHY, valid and invalid SQI pairs, `-ENETDOWN` handling, extended state with and without substate, stats flag behavior, and interaction with explicit `phy_index` requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/linkstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/mm.c -->
# sources/distributed-fs/ceph-client/net/ethtool/mm.c

## Purpose
This file implements netlink MAC Merge (`MM_GET`/`MM_SET`) support and exports a generic software verification state machine for drivers that lack hardware verification for frame preemption/MAC Merge.

## Important APIs, Types, And Functions
The netlink side uses `struct mm_reply_data`, `ethnl_mm_get_policy`, `ethnl_mm_set_policy`, `mm_prepare_data()`, `mm_put_stats()`, `mm_fill_reply()`, `mm_state_to_cfg()`, `ethnl_set_mm_validate()`, `ethnl_set_mm()`, and `ethnl_mm_request_ops`. Exported driver helpers are `__ethtool_dev_mm_supported()`, `ethtool_dev_mm_supported()`, `ethtool_mmsv_init()`, `ethtool_mmsv_get_mm()`, `ethtool_mmsv_set_mm()`, `ethtool_mmsv_stop()`, `ethtool_mmsv_link_state_handle()`, and `ethtool_mmsv_event_handle()`.

## Control Flow
GET requires `get_mm`, initializes stats, calls driver `get_mm`, optionally calls `get_mm_stats`, and emits administrative state, verification state, timing, fragment sizes, and requested stats. SET fetches current state, derives a mutable config, applies supplied booleans and numeric fields, validates verify time against device maximum, enforces verification requires TX enabled and TX requires pMAC enabled, then calls `set_mm()`.

The software verifier uses a timer and event callbacks. `ethtool_mmsv_apply()` either configures pMAC/TX immediately when verification is disabled or starts a verify/retry process. The timer sends Verify mPackets up to the retry limit and activates TX after a Response event marks verification succeeded.

## State And Persistence
Netlink request state is transient. Persistent MAC Merge state lives in drivers or in `struct ethtool_mmsv`: flags for pMAC, TX, verification, verify time, retry count, status, timer, lock, device pointer, and ops. Timer state must be stopped before hardware state loss.

## Dependencies And Integration Points
The file depends on `ethtool_ops::{get_mm,set_mm,get_mm_stats}` and `struct ethtool_mmsv_ops` driver callbacks for configuring pMAC/TX and sending mPackets. `pause.c` calls `__ethtool_dev_mm_supported()` when users request eMAC/pMAC pause statistics.

## Risks And Edge Cases
The verifier mixes timer context, interrupt context, and task context under a spinlock. Drivers must call `ethtool_mmsv_stop()` during stop/suspend and must supply events accurately; otherwise TX may remain inactive or verification may be reported incorrectly. SET validation does not allow enabling TX without pMAC, and requests exceeding `max_verify_time` are rejected. Stats are omitted field-by-field when left at `ETHTOOL_STAT_NOT_SET`.

## Test Signals
Useful tests include GET/SET validation, stats omission, device support probing under RTNL, verifier retry-to-failed behavior, Response-to-succeeded behavior, link-down reset behavior, and driver callback ordering for pMAC before verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/module.c -->
# sources/distributed-fs/ceph-client/net/ethtool/module.c

## Purpose
This file implements netlink module power-mode GET/SET and the asynchronous module firmware flash action with progress notifications for CMIS-capable optical modules.

## Important APIs, Types, And Functions
Power-mode handling uses `struct module_reply_data`, `module_get_power_mode()`, `module_prepare_data()`, `module_fill_reply()`, `ethnl_set_module_validate()`, `ethnl_set_module()`, and `ethnl_module_request_ops`. Firmware flashing uses `ethnl_module_fw_flash_act_policy`, `module_flash_fw_work_list_add()`, `module_flash_fw_work()`, `module_flash_fw_work_init()`, `ethnl_module_fw_flash_sock_destroy()`, `module_flash_fw_schedule()`, `ethnl_module_fw_flash_validate()`, `ethnl_act_module_fw_flash()`, and notification helpers `ethnl_module_fw_flash_ntf_*()`.

## Control Flow
GET enters ethtool ops and reads module power mode unless firmware flashing is in progress. SET validates a supplied power-mode policy, checks flashing state and driver support, fetches current policy, and calls `set_module_power_mode()` only when changed.

Firmware flashing parses a header, file name, and optional password; takes RTNL and netdev ops lock; validates EEPROM page ops, reset support, device-down state, non-split devlink port, and no existing flash. It requests firmware, reads the module physical identifier from EEPROM page 0 address `0x50`, accepts CMIS-capable IDs, records socket-private state, adds the work item to a global list, and schedules work. The worker calls `ethtool_cmis_fw_update()`, removes itself from the list, clears `module_fw_flash_in_progress`, drops the netdev reference, releases firmware, and frees memory.

## State And Persistence
Power-mode values persist in device/module state through driver callbacks. Firmware flash state is held in `dev->ethtool->module_fw_flash_in_progress`, a global protected work list, a held netdev reference/tracker, firmware memory, notification port/sequence, and a closed-socket flag.

## Dependencies And Integration Points
The file depends on firmware loading, SFP identifiers, devlink port metadata, netdev locks, `ethtool_ops` module EEPROM and reset methods, `ethnl_sock_priv_set()`/socket destruction from `netlink.c`, and CMIS implementation supplied by `ethtool_cmis_fw_update()`.

## Risks And Edge Cases
There is a subtle failure-path risk in `module_flash_fw_schedule()`: after setting `module_fw_flash_in_progress` and taking a netdev reference, later errors jump to firmware release/free paths without visibly clearing the flag or dropping the netdev reference. Duplicate work is rejected by portid/device pair, and socket close only suppresses notifications rather than cancelling work. Flashing is blocked while the netdevice is up and also blocks module reads/resets elsewhere.

## Test Signals
Tests should exercise unsupported module IDs, missing driver callbacks, device-up rejection, split-port rejection, duplicate request rejection, socket-close notification suppression, failure unwinds after `ethnl_sock_priv_set()`, and complete/error/in-progress notification payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/module_fw.h -->
# sources/distributed-fs/ceph-client/net/ethtool/module_fw.h

## Purpose
This header defines the shared data structures and function declarations for ethtool module firmware flashing, especially CMIS firmware update work and notifications.

## Important APIs, Types, And Functions
`struct ethnl_module_fw_flash_ntf_params` stores netlink port id, sequence, and `closed_sock`. `struct ethtool_module_fw_flash_params` stores an optional big-endian module password. `struct ethtool_cmis_fw_update_params` bundles the target netdevice, flash params, notification params, and firmware image. `struct ethtool_module_fw_flash` is the async work/list/refcount wrapper used by `module.c`. The header declares socket-destroy, notification, and `ethtool_cmis_fw_update()` entry points.

## Control Flow
`module.c` allocates `struct ethtool_module_fw_flash`, fills the nested CMIS update params, queues `work`, and later the worker calls `ethtool_cmis_fw_update()`. CMIS code calls the declared notification helpers to emit started, progress, error, and completed messages.

## State And Persistence
The structures hold transient in-kernel state for one flash operation. They persist only until the worker releases firmware, drops the netdev hold, and frees the wrapper.

## Dependencies And Integration Points
The header depends on UAPI ethtool definitions, netlink internal socket types, `struct net_device`, `struct firmware`, workqueues, and netdevice reference tracking. It forms the contract between `module.c` and CMIS firmware update code.

## Risks And Edge Cases
The notification sequence is mutable and shared with the worker. `closed_sock` is advisory and suppresses notifications only after socket destruction is observed. Password validity is bitfield state, so initialization must zero the struct before optional password assignment.

## Test Signals
Header-level validation is compile-time: consumers must agree on struct layout and declarations. Runtime tests should verify that CMIS update code can call all notification helpers and that socket-private teardown correctly toggles `closed_sock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/module_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/mse.c -->
# sources/distributed-fs/ceph-client/net/ethtool/mse.c

## Purpose
This file implements netlink `MSE_GET` for PHY mean-square error diagnostics, reporting capability limits and current snapshots for supported channels.

## Important APIs, Types, And Functions
`struct mse_reply_data` stores PHY MSE capability, a dynamically allocated snapshot array, and count. Helpers include `get_snapshot_if_supported()`, `mse_get_channels()`, `mse_prepare_data()`, `mse_cleanup_data()`, `mse_reply_size()`, `mse_channel_to_attr()`, and `mse_fill_reply()`. `ethnl_mse_request_ops` registers a PHY-aware GET operation.

## Control Flow
Preparation resolves the target PHY, enters ethtool ops, locks `phydev->lock`, validates driver callbacks and link-up state, reads capabilities, and calls `mse_get_channels()`. Channel selection prefers individual A-D snapshots, then worst-channel, then link-wide snapshot. Reply filling emits a capabilities nest and one nest per selected channel with average, peak, and worst-peak values gated by capability bits.

## State And Persistence
The file is read-only. Snapshot memory is allocated per request and freed by `mse_cleanup_data()` or immediately on prepare failure.

## Dependencies And Integration Points
It depends on PHY driver callbacks `get_mse_capability()` and `get_mse_snapshot()`, PHY channel/capability enums, `ethnl_req_get_phydev()`, and the per-PHY dump machinery in `netlink.c`.

## Risks And Edge Cases
`mse_get_channels()` allocates space for four entries but can request worst or link-wide only when no individual channels were added, so the array remains bounded. If a snapshot callback fails after allocation, cleanup is split between prepare failure handling and normal cleanup. Requests fail with `-ENETDOWN` when the PHY link is down, unlike linkstate SQI which tolerates down state.

## Test Signals
Tests should cover no PHY, missing callbacks, link down, each capability priority path, mixed metric capability bits, allocation failure, invalid channel mapping, and per-PHY dump with explicit `phy_index`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/mse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/netlink.c -->
# sources/distributed-fs/ceph-client/net/ethtool/netlink.c

## Purpose
This file is the generic netlink core for ethtool. It registers the `ethtool` family, defines common header policies, parses device/PHY selectors, provides generic GET/SET/dump/notify machinery, owns netlink socket private teardown, and dispatches every `ETHTOOL_MSG_*` command to the appropriate request ops or action handler.

## Important APIs, Types, And Functions
Public helpers include `ethnl_sock_priv_set()`, `ethnl_bcast_seq_next()`, `ethnl_ops_begin()`, `ethnl_ops_complete()`, `ethnl_parse_header_dev_get()`, `ethnl_req_get_phydev()`, `ethnl_fill_reply_header()`, `ethnl_reply_init()`, `ethnl_dump_put()`, `ethnl_bcastmsg_put()`, `ethnl_unicast_put()`, `ethnl_multicast()`, `ethnl_notify()`, and exported `ethtool_notify()`. Internal core types are `struct ethnl_dump_ctx` and `struct ethnl_perphy_dump_ctx`. Dispatch tables include `ethnl_default_requests`, `ethnl_default_notify_ops`, `ethnl_notify_handlers`, and `ethtool_genl_ops`.

## Control Flow
Single GET uses `ethnl_default_doit()`: allocate request/reply blocks, parse header and type-specific request data, lock RTNL and netdev ops, call `prepare_data()`, size and allocate reply skb, fill header and payload, cleanup, and reply. Dump GET uses start/dump/done callbacks and iterates netdevices; per-PHY dump variants iterate `dev->link_topo->phys` and set `req_info->phy_index` for each PHY.

SET uses `ethnl_default_set_doit()`: parse a required device, run optional `set_validate()`, lock RTNL and netdev ops, clone `dev->cfg` into `cfg_pending`, enter ethtool ops, call type-specific `set()`, swap pending config on success, and call `ethnl_notify()` if the type reports a change. Notifications rebuild a compact GET reply and multicast it to the monitor group.

## State And Persistence
Global state includes the registered genl family, `ethnl_ok`, broadcast sequence, and per-socket private data used by module firmware flashing. Persistent device configuration is not stored here except transient `dev->cfg_pending` handling during SET. Dump cursors persist in `netlink_callback` context across dump iterations.

## Dependencies And Integration Points
The file depends on generic netlink, netdevice lookup/refcounting, RTNL, netdev ops locking, runtime PM, PHY link topology, module firmware flashing teardown, and all per-command `ethnl_request_ops` declared in `netlink.h`. It also listens for netdevice feature-change and pre-up events, emitting feature notifications and blocking port-up during module flash.

## Risks And Edge Cases
Header parsing permits ifindex/name matching and optional `phy_index`; bad combinations return extack-rich errors. Dumps ignore a device selector for normal per-device operations but preserve it for per-PHY dumps. SET swaps `dev->cfg` and `cfg_pending` only after callback success, so callback implementations must update the pending config consistently. A failed notifier registration after family registration is only warned; the family remains usable. The source snippet contains an apparent duplicated `struct ethnl_dump_ctx {` line in this checkout, which would be a compile-time issue if literal.

## Test Signals
Test signals include genetlink policy validation, GET/SET no-op/change/error paths, dump continuation across small skbs, per-PHY dump filtering by device, notification monitor payloads, socket-private destroy during module flashing, runtime PM pairing, and `NETDEV_PRE_UP` rejection while flashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/netlink.h -->
# sources/distributed-fs/ceph-client/net/ethtool/netlink.h

## Purpose
This header declares the internal ethtool netlink framework shared by all per-command files. It defines common request/reply base structs, update helpers, socket-private state, request operation contracts, policies, request ops externs, and action handler prototypes.

## Important APIs, Types, And Functions
Important inline helpers are `ethnl_strz_size()`, `ethnl_put_strz()`, `ethnl_update_u32()`, `ethnl_update_u8()`, `ethnl_update_bool32()`, `ethnl_update_bool()`, `ethnl_update_binary()`, `ethnl_update_bitfield32()`, `ethnl_reply_header_size()`, and `ethnl_parse_header_dev_put()`. Core types are `struct ethnl_req_info`, `struct ethnl_reply_data`, `enum ethnl_sock_type`, `struct ethnl_sock_priv`, and `struct ethnl_request_ops`.

## Control Flow
Per-command files instantiate `struct ethnl_request_ops` with request/reply command ids, header attr id, struct sizes, optional parse/prepare/size/fill/cleanup callbacks, and optional SET validation and mutation callbacks. `netlink.c` consumes these definitions to implement generic GET, dump, SET, and notifications.

## State And Persistence
The base request tracks referenced netdevice, ref tracker, common flags, and optional PHY index. Reply base stores the current device. Socket-private state stores device, portid, and type for long-running operations such as module firmware flashing.

## Dependencies And Integration Points
The header depends on UAPI ethtool netlink definitions, netdevice, generic netlink, sock internals, and all ethtool command modules. Its extern lists are the integration surface: adding a command generally requires a new request ops object, policy declaration, and `genl_ops` entry in `netlink.c`.

## Risks And Edge Cases
The inline update helpers rely on policy validation to match attribute types. `ethnl_update_binary()` compares and copies only `min(nla_len, len)`, so callers must ensure partial writes are acceptable. `ethnl_parse_header_dev_put()` unconditionally calls `netdev_put()` on the stored pointer; callers must only use it after successful parse or a known-held ref.

## Test Signals
Compile-time coverage is significant because every command includes this header. Runtime tests should verify no-op detection through update helpers, compact reply sizing, request ops cleanup callbacks, socket-private destruction, and invalid `phy_index` header behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/pause.c -->
# sources/distributed-fs/ceph-client/net/ethtool/pause.c

## Purpose
This file implements netlink `PAUSE_GET` and `PAUSE_SET` for pause-frame autonegotiation, RX/TX pause enablement, and optional pause statistics from aggregate/eMAC/pMAC sources.

## Important APIs, Types, And Functions
`struct pause_req_info` stores requested stats source. `struct pause_reply_data` stores `ethtool_pauseparam` and `ethtool_pause_stats`. Key callbacks are `pause_parse_request()`, `pause_prepare_data()`, `pause_reply_size()`, `pause_put_stats()`, `pause_fill_reply()`, `ethnl_set_pause_validate()`, and `ethnl_set_pause()`. `ethnl_pause_request_ops` registers GET and SET.

## Control Flow
Request parsing accepts `ETHTOOL_A_PAUSE_STATS_SRC` only when `ETHTOOL_FLAG_STATS` is set, defaulting to aggregate stats. Preparation verifies `get_pauseparam`, initializes stats, enters ethtool ops, rejects eMAC/pMAC stats when MAC Merge is unsupported, reads pause parameters, and optionally reads pause stats. SET fetches current pause parameters, updates supplied boolean fields using `ethnl_update_bool32()`, and calls `set_pauseparam()` when changed.

## State And Persistence
The file itself is stateless. SET updates driver/device pause configuration; GET snapshots current pause configuration and stats.

## Dependencies And Integration Points
It depends on `ethtool_ops::{get_pauseparam,set_pauseparam,get_pause_stats}` and `__ethtool_dev_mm_supported()` from `mm.c` for eMAC/pMAC source validation. It uses stats-capable common header policy and generic notification `ETHTOOL_MSG_PAUSE_NTF`.

## Risks And Edge Cases
Supplying a stats source without the stats flag is rejected. eMAC/pMAC source requests require MAC Merge support even if a driver might have partial stats. SET policy declares booleans as `NLA_U8` rather than max-1, so nonzero values are normalized by `ethnl_update_bool32()`.

## Test Signals
Tests should cover stats source parsing, aggregate versus eMAC/pMAC requests, unsupported MAC Merge rejection, absent stats hook with stats flag, no-op SET, and notification after change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/pause.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/phc_vclocks.c -->
# sources/distributed-fs/ceph-client/net/ethtool/phc_vclocks.c

## Purpose
This file implements netlink `PHC_VCLOCKS_GET`, returning PTP hardware clock virtual clock indexes associated with a netdevice.

## Important APIs, Types, And Functions
`struct phc_vclocks_reply_data` stores the count and dynamically allocated index array. The callbacks are `phc_vclocks_prepare_data()`, `phc_vclocks_reply_size()`, `phc_vclocks_fill_reply()`, and `phc_vclocks_cleanup_data()`. `ethnl_phc_vclocks_request_ops` registers GET handling.

## Control Flow
Preparation enters ethtool ops, calls `ethtool_get_phc_vclocks(dev, &index)`, stores the returned count and pointer, and completes ops. Reply sizing and filling emit nothing when the count is non-positive; otherwise they emit count and the signed index array. Cleanup frees the array.

## State And Persistence
The file is read-only. The index array is per-request heap state freed after reply generation.

## Dependencies And Integration Points
It depends on the time-stamping/PTP helper `ethtool_get_phc_vclocks()` and the common netlink request framework. It is adjacent to, but separate from, timestamp information handlers.

## Risks And Edge Cases
Negative returns from `ethtool_get_phc_vclocks()` are stored in `num` and cause an empty successful reply because `phc_vclocks_prepare_data()` returns the earlier `ethnl_ops_begin()` status rather than propagating `num`. If the helper uses negative errno to signal failure, this file masks it.

## Test Signals
Tests should cover devices with zero, one, and multiple virtual clocks, allocation failure in the helper, negative helper returns, and cleanup after partial reply failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/phc_vclocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/phy.c -->
# sources/distributed-fs/ceph-client/net/ethtool/phy.c

## Purpose
This file implements netlink `PHY_GET`, exposing metadata for PHY devices attached to a netdevice or selected by PHY index: PHY index, driver name, MDIO device name, upstream topology, and SFP bus names.

## Important APIs, Types, And Functions
`struct phy_reply_data` stores copied strings and topology fields. Main callbacks are `phy_prepare_data()`, `phy_reply_size()`, `phy_fill_reply()`, and `phy_cleanup_data()`. `ethnl_phy_request_ops` registers a per-PHY GET operation.

## Control Flow
Preparation resolves the target PHY with `ethnl_req_get_phydev()`, finds its node in `dev->link_topo->phys`, copies the MDIO name, optional driver name, upstream type, optional upstream PHY index, parent SFP bus name, and downstream SFP bus name. Fill emits the scalar and string attributes, and cleanup frees all copied strings.

## State And Persistence
The file is read-only. Reply strings are duplicated per request and freed after reply or dump item completion.

## Dependencies And Integration Points
It depends on PHY link topology (`struct phy_link_topology`, xarray of PHY nodes), SFP bus names, `ethnl_req_get_phydev()`, and per-PHY dump support in `netlink.c`. RTNL is expected to be held while topology is inspected.

## Risks And Edge Cases
Missing or null PHY returns `-EOPNOTSUPP` rather than a more specific no-device status. `upstream_index` is emitted only if nonzero, so a valid upstream PHY index of zero would be suppressed; PHY indexes are generally minimum one in header policy. Partial allocation failures unwind already duplicated strings.

## Test Signals
Tests should cover attached PHY default selection, explicit `phy_index`, missing topology node, PHY without driver, upstream PHY versus SFP topology, downstream SFP name, and allocation failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/plca.c -->
# sources/distributed-fs/ceph-client/net/ethtool/plca.c

## Purpose
This file implements netlink PLCA configuration and status operations for multidrop PHYs: `PLCA_GET_CFG`, `PLCA_SET_CFG`, and `PLCA_GET_STATUS`.

## Important APIs, Types, And Functions
`struct plca_reply_data` stores `struct phy_plca_cfg` and `struct phy_plca_status`. Important helpers are `plca_update_sint()`, `plca_get_cfg_prepare_data()`, `plca_get_cfg_fill_reply()`, `ethnl_set_plca()`, `plca_get_status_prepare_data()`, and `plca_get_status_fill_reply()`. `ethnl_plca_cfg_request_ops` and `ethnl_plca_status_request_ops` register the operations.

## Control Flow
GET config resolves a PHY, checks global `ethtool_phy_ops->get_plca_cfg`, enters ops, initializes all config fields to `0xff` so signed fields become `-1`, calls the PHY op, and emits only nonnegative fields. SET resolves the PHY, checks `set_plca_cfg`, initializes a config to all `-1`, updates only supplied fields with `plca_update_sint()`, returns no-op if nothing changed, otherwise calls the PHY op. GET status similarly resolves PHY, calls `get_plca_status`, and emits the boolean status.

## State And Persistence
The file holds no persistent state. SET persists through the PHY driver's PLCA configuration; GET snapshots current PHY state.

## Dependencies And Integration Points
It depends on global `ethtool_phy_ops`, PHY device resolution with optional `phy_index`, and the per-PHY dump framework. The operation is integrated into default SET and per-PHY GET dispatch in `netlink.c`.

## Risks And Edge Cases
The code uses all-ones initialization as a sentinel for unsupported fields, which relies on signed integer layout in `phy_plca_cfg`. `plca_update_sint()` uses the set policy table type at runtime; policy/table drift can trigger warnings or wrong extraction. GET status emits `!!pst` without checking a sentinel, so an uninitialized all-ones status would appear true if a driver returned success without filling it.

## Test Signals
Tests should cover field omission for `-1`, range policy enforcement, no-op SET, partial SET of individual fields, missing `ethtool_phy_ops`, explicit PHY selection, and status driver behavior on unfilled output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/plca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/privflags.c -->
# sources/distributed-fs/ceph-client/net/ethtool/privflags.c

## Purpose
This file implements netlink `PRIVFLAGS_GET` and `PRIVFLAGS_SET`, exposing driver-defined private flags as named bitsets.

## Important APIs, Types, And Functions
`struct privflags_reply_data` stores allocated flag names, count, and current 32-bit flags. Core helpers are `ethnl_get_priv_flags_info()`, `privflags_prepare_data()`, `privflags_reply_size()`, `privflags_fill_reply()`, `privflags_cleanup_data()`, `ethnl_set_privflags_validate()`, and `ethnl_set_privflags()`. `ethnl_privflags_request_ops` registers GET and SET.

## Control Flow
GET validates driver support for private flags, string counts, and strings; under ethtool ops it obtains the count and names, caps usable flags to 32 after allocating enough names for all reported flags, reads current flags, and emits a named bitset. SET requires the flags attribute, detects compact versus named bitset encoding, obtains names only when needed, reads current flags, applies bitset updates, and calls `set_priv_flags()` when changed.

## State And Persistence
The file has transient allocated name arrays per request. Persistent state is the driver-maintained private flag word changed by `set_priv_flags()`.

## Dependencies And Integration Points
It depends on driver `ethtool_ops::{get_priv_flags,set_priv_flags,get_sset_count,get_strings}` and `bitset.h` helpers for `ethnl_bitset32_*`. Successful SET emits `ETHTOOL_MSG_PRIVFLAGS_NTF`.

## Risks And Edge Cases
Netlink can name more than 32 flags, but the legacy driver `get_priv_flags()` API returns only `u32`; the code warns and caps count to 32 after fetching all names. Compact bitset SET does not need names, but named SET does, so allocation failures are possible only for named mode. Drivers reporting inconsistent counts or names can make bitset updates ambiguous.

## Test Signals
Tests should cover compact and named GET/SET, more-than-32 flag reporting, missing callbacks, no-op updates, invalid bit names, allocation failure, and notification after a changed flag word.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/privflags.c -->

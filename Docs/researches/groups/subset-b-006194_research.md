<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/pse-pd.c -->
# sources/distributed-fs/ceph-client/net/ethtool/pse-pd.c

## Purpose
Implements the ethtool generic-netlink interface for Ethernet PSE and PD control and status. It exposes `ETHTOOL_MSG_PSE_GET`, `ETHTOOL_MSG_PSE_SET`, and PSE event notification plumbing for PHY-attached Power Sourcing Equipment, including PoDL, Clause 33, available power limits, power limit ranges, priority, and device identity.

## APIs, Types, and Functions
The file defines `struct pse_req_info`, `struct pse_reply_data`, `ethnl_pse_get_policy`, `ethnl_pse_set_policy`, and `ethnl_pse_request_ops`. The read path is `pse_prepare_data()`, `pse_get_pse_attributes()`, `pse_reply_size()`, `pse_fill_reply()`, `pse_put_pw_limit_ranges()`, and `pse_cleanup_data()`. The write path is `ethnl_set_pse_validate()` and `ethnl_set_pse()`. `ethnl_pse_send_ntf()` is exported for drivers or PSE core code to multicast PSE event bits.

## Control Flow, State, and Persistence
GET resolves the target PHY from the ethtool header, enters the device ethtool critical section with `ethnl_ops_begin()`, validates that a `phy_device` and `phydev->psec` exist, clears `data->status`, then delegates to `pse_ethtool_get_status()`. Reply sizing and serialization are sparse: only positive or nonzero status fields are emitted, and allocated power limit ranges are released in cleanup. SET resolves the same PHY, validates attached PSE support and PoDL/C33 capability, then applies priority, available power limit, and admin control changes in sequence. The file itself persists no configuration; persistence is in the PSE controller reached through `phydev->psec`.

## Dependencies and Integration
Depends on ethtool netlink helpers, phylib, and the PSE core in `linux/pse-pd/pse.h`. Integration points are `ethnl_req_get_phydev()`, `ethnl_ops_begin()/complete()`, `pse_ethtool_get_status()`, `pse_ethtool_set_prio()`, `pse_ethtool_set_pw_limit()`, `pse_ethtool_set_config()`, and `ethnl_multicast()`.

## Risks and Test Signals
Risks include partial SET ordering if earlier updates succeed and later updates fail, mismatch between reply size and optional fields, driver/PSE allocations for `c33_pw_limit_ranges`, and unsupported PHY/PSE paths returning accurate extack messages. Test signals are netlink policy validation, GET with no PHY, GET with no PSE, SET unsupported PoDL/C33 controls, range serialization, priority update, power-limit update, and notification multicast failure tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/pse-pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/rings.c -->
# sources/distributed-fs/ceph-client/net/ethtool/rings.c

## Purpose
Provides ethtool netlink GET and SET support for NIC ring parameters, including legacy pending queue counts and newer kernel-only ring attributes such as RX buffer length, TCP data split, CQE size, TX/RX push, TX push buffer length, and header-data-split thresholds.

## APIs, Types, and Functions
Defines `struct rings_req_info`, `struct rings_reply_data`, `ethnl_rings_get_policy`, `ethnl_rings_set_policy`, and `ethnl_rings_request_ops`. The main functions are `rings_prepare_data()`, `rings_reply_size()`, `rings_fill_reply()`, `ethnl_set_rings_validate()`, and `ethnl_set_rings()`.

## Control Flow, State, and Persistence
GET requires `dev->ethtool_ops->get_ringparam`, snapshots `supported_ring_params`, seeds `kernel_ringparam.tcp_data_split` and `hds_thresh` from `dev->cfg`, calls the driver, and serializes only supported/nonzero maximums plus selected kernel fields. SET first gates each requested attribute against `ops->supported_ring_params`, then reads current ring configuration with `ethtool_ringparam_get_cfg()`, applies netlink updates into local copies, and exits with no notification if nothing changed. Before invoking the driver it rejects TCP data split with single-buffer XDP, rejects disabling TCP data split or setting nonzero HDS threshold while a memory provider is enabled, bounds requested counts against driver maxima, and bounds TX push buffer length. Pending HDS settings are staged in `dev->cfg_pending`, while durable device state is set by `ops->set_ringparam()`.

## Dependencies and Integration
Depends on ethtool core helpers, netdev queue helpers, XDP single-buffer checks, memory-provider channel checks, and driver `get_ringparam`/`set_ringparam` callbacks. The request ops emit `ETHTOOL_MSG_RINGS_NTF` when changes are accepted.

## Risks and Test Signals
Risks include stale maxima if a driver reports inconsistent current configuration, arithmetic mistakes in `rings_reply_size()`, staged `cfg_pending` values when a driver later fails, and cross-feature conflicts around XDP or page-pool memory providers. Test signals include unsupported attribute extacks, max-bound failures, no-op SET returning zero, XDP/HDS conflict rejection, TX push buffer max validation, and notification on successful mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/rings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/rss.c -->
# sources/distributed-fs/ceph-client/net/ethtool/rss.c

## Purpose
Implements the ethtool netlink RSS API: reading, dumping, modifying, creating, and deleting receive-side scaling contexts, indirection tables, hash keys, hash functions, input transforms, and per-flow hash-field selections.

## APIs, Types, and Functions
Defines `struct rss_req_info`, `struct rss_reply_data`, flow-type mapping table `ethtool_rxfh_ft_nl2ioctl`, GET/SET/CREATE/DELETE policies, and `ethnl_rss_request_ops`. Important helpers include `rss_parse_request()`, `rss_prepare_flow_hash()`, `rss_get_data_alloc()`, `rss_prepare_get()`, `rss_prepare_ctx()`, `rss_prepare()`, `rss_fill_reply()`, dump helpers `ethnl_rss_dump_start()` and `ethnl_rss_dumpit()`, mutation helpers `rss_set_prep_indir()`, `rss_set_prep_hkey()`, `ethnl_set_rss_fields()`, `rss_set_ctx_update()`, plus `ethnl_rss_create_doit()` and `ethnl_rss_delete_doit()`.

## Control Flow, State, and Persistence
GET parses an optional context ID, rejects `START_CONTEXT`, snapshots flow hash fields if supported, and either calls driver `get_rxfh()` for the default context or loads a saved `struct ethtool_rxfh_context` from `dev->ethtool->rss_ctx`. Dumps iterate devices and context IDs using callback cursor state. SET prepares current state, validates/rebuilds an indirection table, duplicates and updates the hash key, handles hash function and input transform changes, updates per-flow fields under `dev->ethtool->rss_lock`, then calls `set_rxfh()` or `modify_rxfh_context()` as needed and mirrors accepted values back into kernel context storage. CREATE allocates a context, assigns or inserts an XArray ID, calls the driver, builds a reply, and converts the same skb into a create notification. DELETE checks context busy state, calls driver removal, erases the XArray entry, frees the context, and emits delete notification. Persistent state is per-netdev RSS metadata: `rss_ctx`, `rss_indir_user_size`, and context fields.

## Dependencies and Integration
Depends on ethtool driver operations `get_rxfh`, `set_rxfh`, `create_rxfh_context`, `modify_rxfh_context`, `remove_rxfh_context`, `get_rxfh_fields`, and `set_rxfh_fields`; on `dev->ethtool->rss_lock`; on XArray context storage; and on RX ring count helpers. It integrates with ethtool notifications, rtnl and netdev ops locks, and generic-netlink dump cursors.

## Risks and Test Signals
Risks include races between driver callbacks and XArray state, validating user indirection tables against changing queue counts, partial flow-field updates before later driver RSS config failure, symmetric input-transform conflicts with non-symmetric flow fields, and notification build failures after context creation. Test signals should cover default and per-context GET, dump start context, indirection replication and reset, queue out-of-range errors, key length checks, unsupported per-context key/fields, symmetric transform conflicts, create with automatic and explicit IDs, busy delete, and create/delete notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/rss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/stats.c -->
# sources/distributed-fs/ceph-client/net/ethtool/stats.c

## Purpose
Implements standard ethtool netlink statistics groups and exports helpers that aggregate MAC merge EMAC/PMAC statistics into aggregate counters.

## APIs, Types, and Functions
Defines `stats_std_names`, per-group statistic name arrays, `struct stats_req_info`, `struct stats_reply_data`, `ethnl_stats_get_policy`, and `ethnl_stats_request_ops`. Main functions are `stats_parse_request()`, `stats_prepare_data()`, `stats_reply_size()`, `stat_put()`, group serializers such as `stats_put_mac_stats()` and `stats_put_rmon_stats()`, and aggregation exports `ethtool_aggregate_mac_stats()`, `ethtool_aggregate_phy_stats()`, `ethtool_aggregate_ctrl_stats()`, `ethtool_aggregate_pause_stats()`, and `ethtool_aggregate_rmon_stats()`.

## Control Flow, State, and Persistence
Requests must include a nonempty stats group bitset and may request aggregate, EMAC, or PMAC source. `stats_prepare_data()` resolves the PHY, enters ethtool ops, rejects EMAC/PMAC source when MAC merge is unsupported, initializes all counters to `ETHTOOL_STAT_NOT_SET`, stamps source fields, and invokes PHY or driver group callbacks only for requested groups. Reply sizing counts requested groups and possible counters, including RMON histograms. Serialization nests each group with group ID and string-set ID, then emits only counters not left at `ETHTOOL_STAT_NOT_SET`; 64-bit alignment is handled explicitly. Aggregation helpers query EMAC and PMAC variants and sum each u64 counter while preserving not-set semantics.

## Dependencies and Integration
Depends on ethtool bitset helpers, phylib stats helpers, driver stats callbacks, MAC merge support detection, netlink nested attribute encoding, and string-set names consumed by `strset.c`.

## Risks and Test Signals
Risks include group struct layout assumptions in generic aggregation, not-set sentinel handling during sums, reply size over/underestimation for sparse counters and histograms, PHY fallback behavior, and source validation for devices without MAC merge. Test signals include empty group rejection, group bitset parsing by names and indexes, aggregate versus EMAC/PMAC requests, not-set counters being omitted, RMON histogram ranges, 64-bit alignment on strict architectures, and aggregation where one or both sources are unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/strset.c -->
# sources/distributed-fs/ceph-client/net/ethtool/strset.c

## Purpose
Serves ethtool string-set queries over netlink, combining global static string sets with per-device and PHY-provided sets. It supports both full string payloads and counts-only responses.

## APIs, Types, and Functions
Defines `struct strset_info`, `info_template`, `struct strset_req_info`, `struct strset_reply_data`, `ethnl_strset_get_policy`, and `ethnl_strset_request_ops`. Key functions are `strset_parse_request()`, `strset_include()`, `strset_prepare_set()`, `strset_prepare_data()`, `strset_reply_size()`, `strset_fill_string()`, `strset_fill_set()`, `strset_fill_reply()`, and `strset_cleanup_data()`.

## Control Flow, State, and Persistence
Parsing optionally walks nested string-set requests and records requested `ETH_SS_*` IDs in a bitmap-like `u32`; counts-only is honored when explicit string sets are supplied. Preparation copies `info_template` into reply data. Nodev queries are allowed only for non-device string sets. Device queries may resolve a PHY, enter ethtool ops, and for each included per-device set ask driver or PHY ops for count and strings; allocated per-device string arrays are marked for cleanup. Reply sizing and filling skip empty sets, include set ID and count, and include indexed string values unless counts-only was requested. The file maintains no persistent state beyond static global string tables.

## Dependencies and Integration
Depends on ethtool string tables from `common.h`, driver `get_sset_count()` and `get_strings()`, optional `ethtool_phy_ops`, PHY resolution via ethtool header flags, and netlink nesting helpers. The static sets include features, RSS hash functions, tunables, link modes, message classes, WoL modes, timestamping names, UDP tunnel types, and standard stats names.

## Risks and Test Signals
Risks include `ETH_SS_COUNT` exceeding the `u32` request bitmask, driver count changing between count and strings retrieval, allocation cleanup on partial failure, nodev requests accidentally asking for per-device sets, and string names with missing static arrays. Test signals include global nodev query, per-device stats/test/private flags queries, counts-only mode, PHY stats fallback, unknown string-set ID rejection, and cleanup after allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/strset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/ts.h -->
# sources/distributed-fs/ceph-client/net/ethtool/ts.h

## Purpose
Provides shared timestamping netlink declarations for ethtool timestamp information and timestamp configuration handlers.

## APIs, Types, and Functions
Defines the nested policy `ethnl_ts_hwtst_prov_policy` for `ETHTOOL_A_TS_HWTSTAMP_PROVIDER_INDEX` and `ETHTOOL_A_TS_HWTSTAMP_PROVIDER_QUALIFIER`, and declares `ts_parse_hwtst_provider()`.

## Control Flow, State, and Persistence
There is no executable control flow or mutable state in this header. It centralizes validation constraints for timestamp provider descriptors so both `tsinfo.c` and `tsconfig.c` parse the same nested attribute shape.

## Dependencies and Integration
Depends on `netlink.h` for ethtool netlink definitions and on timestamp provider UAPI constants such as `HWTSTAMP_PROVIDER_QUALIFIER_CNT`. `tsconfig.c` includes this header for provider SET parsing; `tsinfo.c` provides the implementation and uses the same policy for GET filtering.

## Risks and Test Signals
Risks are limited but include policy drift if provider attributes evolve without updating both the policy and parser contract. Test signals are malformed nested provider attributes, qualifier max-bound validation, and shared behavior between tsinfo GET filtering and tsconfig SET source selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/ts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tsconfig.c -->
# sources/distributed-fs/ceph-client/net/ethtool/tsconfig.c

## Purpose
Implements ethtool netlink GET and SET for active hardware timestamp configuration: selected timestamp provider, TX type, RX filter, and hwtstamp flags.

## APIs, Types, and Functions
Defines `struct tsconfig_req_info`, `struct tsconfig_reply_data`, `ethnl_tsconfig_get_policy`, `ethnl_tsconfig_set_policy`, and `ethnl_tsconfig_request_ops`. Main functions are `tsconfig_prepare_data()`, `tsconfig_reply_size()`, `tsconfig_fill_reply()`, `tsconfig_send_reply()`, `ethnl_set_tsconfig_validate()`, `tsconfig_set_hwprov_from_desc()`, and `ethnl_set_tsconfig()`.

## Control Flow, State, and Persistence
GET requires `ndo_hwtstamp_get`, reads the active kernel hwtstamp config through `dev_get_hwtstamp_phylib()`, converts selected TX/RX enums into single-bit bitsets, preserves flags, then reports an explicit provider from `dev->hwprov` or derives one from `__ethtool_get_ts_info()`. SET requires both hwtstamp netdev ops, rejects absent devices, optionally parses a new provider descriptor, resolves it to either netdev or PHY topology, and fetches current config unless the provider is changing. It updates bitsets for TX type, RX filter, and flags, enforcing exactly one TX type and one RX filter, then validates with `net_hwtstamp_validate()`. If provider changes, current timestamping is disabled, `dev->hwprov` is replaced with RCU cleanup, and modified config is applied via `dev_set_hwtstamp_phylib()`. SET sends an action reply with the new config and has no notification.

## Dependencies and Integration
Depends on net timestamping, PTP clock descriptors, phylib timestamp plumbing, RCU replacement under RTNL, ethtool bitset helpers, provider parsing from `ts.h`, and device hwtstamp netdev ops.

## Risks and Test Signals
Risks include returning early in GET after derived PHC failure without calling `ethnl_ops_complete()`, provider switch leaving timestamping disabled if the later config application fails, single-bit selection edge cases when a bitset becomes zero, and topology lookup ambiguity between netdev and PHY providers. Test signals include GET with explicit `dev->hwprov`, GET fallback to tsinfo, no PHC, provider not in topology, multi-bit TX/RX rejection, flags validation, provider switch with zeroed old config, and action-reply generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tsconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tsinfo.c -->
# sources/distributed-fs/ceph-client/net/ethtool/tsinfo.c

## Purpose
Implements ethtool netlink timestamp capability and statistics queries, including per-provider filtering and dump traversal across netdev and PHY timestamp providers.

## APIs, Types, and Functions
Defines `struct tsinfo_req_info`, `struct tsinfo_reply_data`, `ethnl_tsinfo_get_policy`, `ethnl_tsinfo_request_ops`, and dump context `struct ethnl_tsinfo_dump_ctx`. Important functions are `ts_parse_hwtst_provider()`, `tsinfo_parse_request()`, `tsinfo_prepare_data()`, `tsinfo_reply_size()`, `tsinfo_fill_reply()`, `tsinfo_put_stats()`, `ethnl_tsinfo_dump_one_netdev()`, `ethnl_tsinfo_dump_one_phydev()`, `ethnl_tsinfo_dump_one_net_topo()`, `ethnl_tsinfo_dumpit()`, `ethnl_tsinfo_start()`, and `ethnl_tsinfo_done()`.

## Control Flow, State, and Persistence
GET optionally parses a provider descriptor. With an explicit provider it calls `ethtool_get_ts_info_by_phc()` and returns that provider's data. Without a provider, it optionally initializes and collects timestamp stats, then calls `__ethtool_get_ts_info()`. Replies encode timestamping capabilities, TX types, RX filters, PHC index, provider descriptor, source, PHY index, and optional stats. Dump setup allocates request and reply data, parses an optional device header, and initializes netdev/PHY cursors. Dumping walks either one device or all devices under RTNL, then for each device emits supported netdev qualifiers and PHY providers from either the legacy `dev->phydev` or `dev->link_topo->phys`. State is only per-dump callback cursor data; no durable configuration is changed.

## Dependencies and Integration
Depends on ethtool timestamp helpers, driver `get_ts_info()` and `get_ts_stats()`, PHY timestamp support checks, link topology XArray iteration, compact bitset encoding, and generic-netlink dump lifecycle hooks.

## Risks and Test Signals
Risks include cursor correctness across partial dump buffers, stats only being available for non-provider-specific GET, PHY topology iteration under concurrent changes, source/PHY index omission when fields are zero, and provider qualifier support drift. Test signals include explicit provider lookup, stats flag output, compact and verbose bitsets, dump of netdev and PHY providers, partial `-EMSGSIZE` dump resume, devices without timestamp ops, and cleanup of allocated dump context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tsinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tunnels.c -->
# sources/distributed-fs/ceph-client/net/ethtool/tunnels.c

## Purpose
Serves ethtool netlink tunnel offload information for UDP tunnel port tables, including dynamic NIC UDP tunnel tables and the static IANA VXLAN port convention.

## APIs, Types, and Functions
Defines `ethnl_tunnel_info_get_policy`, `struct ethnl_tunnel_info_dump_ctx`, and direct/dump handlers `ethnl_tunnel_info_doit()`, `ethnl_tunnel_info_start()`, and `ethnl_tunnel_info_dumpit()`. Helpers include `ethnl_udp_table_reply_size()`, `ethnl_tunnel_info_reply_size()`, and `ethnl_tunnel_info_fill_reply()`.

## Control Flow, State, and Persistence
Direct GET parses a device header, locks RTNL, computes reply size from `dev->udp_tunnel_nic_info`, allocates an ethtool reply, fills nested UDP port table attributes, unlocks, releases the device, and replies. Fill iterates NIC tunnel tables until a table with zero entries, emits table size, tunnel type bitset, and entries provided by `udp_tunnel_nic_dump_write()`. If the device advertises static IANA VXLAN support, a synthetic one-entry table for port 4789 and VXLAN type is appended. Dumps parse an optional device filter but then clear it, walk netdevs with an ifindex cursor, skip devices returning `-EOPNOTSUPP`, and return a partial skb length when `-EMSGSIZE` occurs after data was emitted.

## Dependencies and Integration
Depends on `udp_tunnel_nic_info`, UDP tunnel dump helpers, VXLAN IANA constants, compact ethtool bitsets, RTNL, and ethtool generic-netlink header helpers. Static asserts keep ethtool tunnel type IDs aligned with kernel UDP tunnel type bit positions.

## Risks and Test Signals
Risks include inconsistent dump behavior if a requested device filter is intentionally ignored, reply size drift versus tunnel dump helper output, static VXLAN table encoding with zero type bitset, and partial dump resume correctness. Test signals include no tunnel info extack, multi-table dump, static VXLAN support, compact type bitsets, direct GET, all-netdev dump skipping unsupported devices, and small-skb `-EMSGSIZE` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tunnels.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/wol.c -->
# sources/distributed-fs/ceph-client/net/ethtool/wol.c

## Purpose
Implements ethtool netlink GET and SET for Wake-on-LAN modes and the optional SecureOn password.

## APIs, Types, and Functions
Defines `struct wol_req_info`, `struct wol_reply_data`, `ethnl_wol_get_policy`, `ethnl_wol_set_policy`, and `ethnl_wol_request_ops`. Main functions are `wol_prepare_data()`, `wol_reply_size()`, `wol_fill_reply()`, `ethnl_set_wol_validate()`, and `ethnl_set_wol()`.

## Control Flow, State, and Persistence
GET requires `get_wol`, calls the driver in the ethtool ops section, then decides whether to include the SecureOn password: it is only shown for direct replies, never notifications, and only when `WAKE_MAGICSECURE` is supported. Reply serialization uses a supported/value bitset for WoL modes plus optional raw password bytes. SET validates driver support, reads current settings, updates the WoL mode bitset, rejects requested modes outside `wol.supported`, optionally updates the SecureOn password only if MagicSecure is supported, and calls `set_wol()` only when something changed. On success it updates `dev->ethtool->wol_enabled`.

## Dependencies and Integration
Depends on driver `get_wol()` and `set_wol()` callbacks, ethtool bitset helpers, WoL mode string names, and ethtool notification support through `ETHTOOL_MSG_WOL_NTF`.

## Risks and Test Signals
Risks include exposing SecureOn secrets if notification detection regresses, driver callbacks returning stale supported masks, unsupported password updates, and `wol_enabled` divergence if drivers adjust requested modes. Test signals include GET with and without MagicSecure, notification hiding `sopass`, unsupported mode rejection, password length policy, no-op SET, successful SET notification, and `wol_enabled` update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/wol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/Makefile -->
# sources/distributed-fs/ceph-client/net/handshake/Makefile

## Purpose
Builds the generic kernel handshake service and optional KUnit tests.

## APIs, Types, and Functions
Declares `obj-y += handshake.o`, composes `handshake-y` from `alert.o`, `genl.o`, `netlink.o`, `request.o`, `tlshd.o`, and `trace.o`, and conditionally builds `handshake-test.o` under `CONFIG_NET_HANDSHAKE_KUNIT_TEST`.

## Control Flow, State, and Persistence
The file has no runtime control flow. Its build aggregation determines which source files form the always-built handshake object and whether test code is compiled.

## Dependencies and Integration
Integrates the handshake directory with kbuild. The unconditional `obj-y` means the service is part of the networking build when this directory is included, while the KUnit object depends on its config symbol.

## Risks and Test Signals
Risks include missing new handshake implementation files from `handshake-y`, generated `genl.*` drift not reflected in the build, or test object linkage assumptions. Test signals are successful link of `handshake.o`, presence of tracepoints, and optional KUnit suite discovery when `CONFIG_NET_HANDSHAKE_KUNIT_TEST` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/alert.c -->
# sources/distributed-fs/ceph-client/net/handshake/alert.c

## Purpose
Implements TLS alert send/receive helpers used around kTLS-backed kernel handshake sessions.

## APIs, Types, and Functions
Exports `tls_alert_send()`, `tls_get_record_type()`, and `tls_alert_recv()`. `tls_alert_send()` constructs a two-byte TLS alert record and a `SOL_TLS/TLS_SET_RECORD_TYPE` control message. `tls_get_record_type()` parses `SOL_TLS/TLS_GET_RECORD_TYPE` control messages. `tls_alert_recv()` extracts alert level and description from an incoming kvec-backed message.

## Control Flow, State, and Persistence
Sending traces the alert, fills a two-byte alert payload, builds a `msghdr` with a TLS record-type control message, sets `MSG_DONTWAIT`, initializes a kvec iterator, and calls `sock_sendmsg()`, mapping positive byte counts to zero. Receiving does not own socket state; it assumes the message iterator has alert bytes in `msg_iter.kvec`, copies the first two bytes to outputs, and traces. The file persists no state.

## Dependencies and Integration
Depends on kTLS UAPI/control messages, socket sendmsg infrastructure, kvec iterators, and handshake tracepoints. The helpers are exported for TLS consumers and the handshake TLS adapter.

## Risks and Test Signals
Risks include assuming kvec-backed receive iterators, short alert payloads, nonblocking send failures, and control-message layout errors. Test signals include sending close_notify alerts on a kTLS socket, parsing correct and irrelevant cmsgs, tracepoint observation, and handling `sock_sendmsg()` error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/alert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/genl.c -->
# sources/distributed-fs/ceph-client/net/handshake/genl.c

## Purpose
Generated generic-netlink family registration data for the handshake UAPI defined by `Documentation/netlink/specs/handshake.yaml`.

## APIs, Types, and Functions
Defines netlink policies for `HANDSHAKE_CMD_ACCEPT` and `HANDSHAKE_CMD_DONE`, the split ops table dispatching to `handshake_nl_accept_doit()` and `handshake_nl_done_doit()`, multicast groups `none` and `tlshd`, and the exported `handshake_nl_family`.

## Control Flow, State, and Persistence
There is no complex runtime logic beyond generic-netlink dispatch. The ops table enforces admin permission for ACCEPT, allows DONE without admin permission, and binds policies and max attribute IDs. The family is netns-aware, permits parallel ops, and is registered/unregistered by `netlink.c`.

## Dependencies and Integration
Depends on generated UAPI constants in `uapi/linux/handshake.h`, generic-netlink core, and handler functions declared in `genl.h`. It is generated code and should be updated from the YAML spec rather than edited directly.

## Risks and Test Signals
Risks include generated policy drift from the YAML spec, handler-class max constraints diverging from UAPI, and multicast group indexes changing without matching userspace. Test signals are family registration, YNL conformance tests, ACCEPT requiring admin permission, DONE fd/status parsing, and multicast listener group behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/genl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/genl.h -->
# sources/distributed-fs/ceph-client/net/handshake/genl.h

## Purpose
Generated header for the handshake generic-netlink family, shared by generated family data and handwritten netlink handlers.

## APIs, Types, and Functions
Declares `handshake_nl_accept_doit()`, `handshake_nl_done_doit()`, multicast group indexes `HANDSHAKE_NLGRP_NONE` and `HANDSHAKE_NLGRP_TLSHD`, and external `struct genl_family handshake_nl_family`.

## Control Flow, State, and Persistence
The header has no control flow or state. It provides the compile-time linkage contract between generated netlink registration code and the implementation in `netlink.c`.

## Dependencies and Integration
Depends on netlink/genetlink headers and the handshake UAPI. It is generated from `Documentation/netlink/specs/handshake.yaml` and integrated by `genl.c` and `netlink.c`.

## Risks and Test Signals
Risks are generated-code drift and stale declarations after UAPI changes. Test signals include clean compilation after regenerating YNL sources and successful registration of `handshake_nl_family`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/genl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/handshake-test.c -->
# sources/distributed-fs/ceph-client/net/handshake/handshake-test.c

## Purpose
KUnit coverage for the generic handshake request API, focused on allocation validation, submission error handling, request lookup, duplicate submission, cancellation races, and destroy callbacks.

## APIs, Types, and Functions
Defines test callbacks `test_accept_func()`, `test_done_func()`, and `test_destroy_func()`, several test `struct handshake_proto` variants, parameterized allocation cases, and individual KUnit tests for `handshake_req_alloc()`, `handshake_req_submit()`, `handshake_req_hash_lookup()`, `handshake_req_next()`, `handshake_req_cancel()`, `handshake_complete()`, and request destruction.

## Control Flow, State, and Persistence
Allocation tests fuzz invalid protocol descriptors and excessive private size. Submit tests create TCP sockets in `init_net`, sometimes attach files with `sock_alloc_file()`, and assert behavior for NULL request, NULL socket, missing `sock->file`, max pending overflow, successful hash lookup, and duplicate submission returning `-EBUSY`. Cancel tests cover cancellation before accept, after simulated accept via `handshake_req_next()`, and after completion. The destroy test installs a protocol destroy callback, cancels a request, forces file teardown with `__fput_sync()`, and checks that socket destruction released the request. Static `handshake_req_destroy_test` records the destroyed request.

## Dependencies and Integration
Depends on KUnit, exported-for-KUnit handshake internals, kernel socket creation, file-backed sockets, init net namespace, generic-netlink definitions, and `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.

## Risks and Test Signals
Risks include tests mutating `hn_pending` directly, relying on socket/file lifetime details, and not exercising actual generic-netlink ACCEPT/DONE messages. Strong test signals are coverage of invalid proto inputs, one-request-per-socket enforcement, pending cap enforcement, hash lookup, pre/post-accept cancellation, completion-versus-cancel behavior, and destructor callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/handshake-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/handshake.h -->
# sources/distributed-fs/ceph-client/net/handshake/handshake.h

## Purpose
Internal header for the generic handshake service, defining per-net state, request lifetime structures, protocol callbacks, flag bits, and cross-file function declarations.

## APIs, Types, and Functions
Defines `struct handshake_net`, `struct handshake_req`, `struct handshake_proto`, flag enums for network, request, and protocol state, and declarations for alert, netlink, and request helpers. Key fields include `hn_pending`, `hn_pending_max`, `hn_requests`, `hr_list`, `hr_rhash`, `hr_flags`, `hr_proto`, `hr_sk`, `hr_odestruct`, and flexible private storage `hr_priv`.

## Control Flow, State, and Persistence
No executable logic is present, but the header encodes lifecycle invariants. A `handshake_req` is owned by a protocol, maps one-to-one to a socket through the rhashtable, may sit on a per-net pending list before userspace accepts it, stores the original socket destructor for restoration/chaining, and carries protocol-private data at the end. Protocols provide accept, done, and optional destroy callbacks plus a handler class and notification flag.

## Dependencies and Integration
Shared by `alert.c`, `netlink.c`, `request.c`, `tlshd.c`, `trace.c`, and tests. It bridges internal implementation with exported public handshake APIs in `include/net/handshake.h`.

## Risks and Test Signals
Risks include flag misuse causing double completion, callback contracts not being honored by protocol implementations, private size overflow, and inconsistent list/hash lifetime. Test signals are allocation validation, hash lookup, single completion semantics, socket destructor chaining, per-net draining, and protocol-private data access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/handshake.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/netlink.c -->
# sources/distributed-fs/ceph-client/net/handshake/netlink.c

## Purpose
Implements the generic-netlink control plane and per-network-namespace registration for the kernel handshake service.

## APIs, Types, and Functions
Provides `handshake_genl_notify()`, `handshake_genl_put()`, `handshake_nl_accept_doit()`, `handshake_nl_done_doit()`, `handshake_pernet()`, module init/exit, and pernet operations `handshake_net_init()` and `handshake_net_exit()`.

## Control Flow, State, and Persistence
`handshake_genl_notify()` checks protocol notification flag and multicast listeners, then sends `HANDSHAKE_CMD_READY` with handler class. ACCEPT validates handler class, selects the next pending request for that class, prepares an fd for the socket file, calls the protocol `hp_accept()` callback to build a reply, publishes the fd on success, or completes the request with `-EIO` on failure. DONE looks up the socket fd, finds the outstanding request by socket, extracts an optional status, and calls `handshake_complete()`. Per-net init sets a memory-scaled cap for pending handshakes, initializes a spinlock and list, and clears flags. Per-net exit marks draining, splices unaccepted requests, and completes them with timeout. Module init initializes the request hash, registers the netlink family, then registers pernet state last so `handshake_pernet()` stays NULL until safe.

## Dependencies and Integration
Depends on generic-netlink, net namespace generic storage, fd allocation helpers, socket file references, request hash/list APIs, and handshake tracepoints. It registers the generated `handshake_nl_family`.

## Risks and Test Signals
Risks include fd reference handling on ACCEPT error paths, completing accepted requests during namespace teardown only when sockets later close, pending cap sizing, listener absence returning `-ESRCH`, and init ordering around `handshake_net_id`. Test signals include READY multicast with listeners, ACCEPT empty queue returning `-EAGAIN`, ACCEPT fd publication, DONE unknown fd/request, per-net draining, and init failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/request.c -->
# sources/distributed-fs/ceph-client/net/handshake/request.c

## Purpose
Owns handshake request allocation, socket association, pending-list management, hash lookup, completion, cancellation, and destruction.

## APIs, Types, and Functions
Defines the global rhashtable `handshake_rhashtbl` and exports or exposes for KUnit `handshake_req_hash_init()`, `handshake_req_hash_destroy()`, `handshake_req_hash_lookup()`, `handshake_req_alloc()`, `handshake_req_private()`, `handshake_req_next()`, `handshake_req_submit()`, `handshake_complete()`, and `handshake_req_cancel()`. Internal helpers include `handshake_req_hash_add()`, `handshake_req_destroy()`, `handshake_sk_destruct()`, `remove_pending()`, and pending-list add/remove helpers.

## Control Flow, State, and Persistence
Allocation validates protocol class and callbacks, then allocates a flex-array request. Submit validates socket and file, binds the request to `sock->sk`, replaces `sk_destruct` with `handshake_sk_destruct`, checks per-net availability and pending cap, atomically inserts into the socket-keyed rhashtable and pending list, notifies userspace, and holds the socket until completion/cancel. If notification fails after removal from pending, the request is destroyed and destructor restored. ACCEPT removes requests from pending via `handshake_req_next()`. Completion uses `test_and_set_bit(HANDSHAKE_F_REQ_COMPLETED)` to guarantee one `hp_done()` callback and one `sock_put()`. Cancellation races with completion, removes unaccepted requests when possible, marks completion, and releases the socket. Actual memory is freed from socket destruction through the installed destructor, which removes the request from the rhashtable, calls optional protocol destroy, then chains the original destructor.

## Dependencies and Integration
Depends on rhashtable, per-net handshake state, socket lifetime rules, spinlocks, RCU/list usage, protocol callbacks, and generic-netlink notification from `netlink.c`.

## Risks and Test Signals
Risks include replacing `sk_destruct` before all failure paths are known, hash/list consistency under races, callback double-invocation, pending counter imbalance, and request memory surviving until socket close even after completion. Test signals include invalid submit inputs, duplicate submit `-EBUSY`, pending cap `-EAGAIN`, lookup by socket, accept ordering by class, cancellation before and after accept, completion/cancel race behavior, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/tlshd.c -->
# sources/distributed-fs/ceph-client/net/handshake/tlshd.c

## Purpose
Adapts the generic handshake framework to TLS sessions handled by the userspace `tlshd` agent for kernel socket consumers.

## APIs, Types, and Functions
Defines private `struct tls_handshake_req`, `tls_handshake_proto`, and exported public APIs `tls_client_hello_anon()`, `tls_client_hello_x509()`, `tls_client_hello_psk()`, `tls_server_hello_x509()`, `tls_server_hello_psk()`, `tls_handshake_cancel()`, and `tls_handshake_close()`. Helpers include `tls_handshake_req_init()`, `tls_handshake_remote_peerids()`, `tls_handshake_done()`, `tls_handshake_private_keyring()`, `tls_handshake_put_peer_identity()`, `tls_handshake_put_certificate()`, and `tls_handshake_accept()`.

## Control Flow, State, and Persistence
Each public client/server helper allocates a generic request, initializes common fields from `struct tls_handshake_args`, sets message type and auth mode, copies certificates, private keys, or peer IDs, and submits the request. ACCEPT optionally links a configured keyring into the process keyring, builds a netlink reply containing socket fd, message type, peername, timeout, keyring, auth mode, peer identities or certificate tuple, and replies to the accepting agent. DONE extracts up to five remote peer identity attributes, sets the session flag when status is zero, and calls the kernel consumer callback with `-status` and the first peer ID. `tls_handshake_close()` finds the request for a socket, clears the active session bit, and sends TLS close_notify. Persistent state is held in the outstanding request until socket destruction.

## Dependencies and Integration
Depends on the generic handshake framework, kTLS alert helper, generic-netlink attributes from the handshake UAPI, keyrings when `CONFIG_KEYS` is enabled, and public TLS handshake argument definitions.

## Risks and Test Signals
Risks include PSK peer ID array bounds, server PSK assuming at least one peer ID, keyring link side effects in the userspace agent process, status sign conversion, missing remote peer IDs, and close_notify only if the request still maps to the socket. Test signals include all five public handshake modes, ACCEPT payload per auth mode, keyring linking failures, DONE with multiple remote auth attributes, consumer callback status mapping, cancel, and close_notify after successful session.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/tlshd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/trace.c -->
# sources/distributed-fs/ceph-client/net/handshake/trace.c

## Purpose
Instantiates transport security handshake tracepoints.

## APIs, Types, and Functions
Defines `CREATE_TRACE_POINTS` and includes `trace/events/handshake.h` after importing network, socket, inet, netlink, genetlink, and internal handshake types.

## Control Flow, State, and Persistence
There is no runtime logic beyond tracepoint definition generation at build time. This translation unit causes the tracepoint storage and metadata declared in the trace header to be emitted once.

## Dependencies and Integration
Depends on the trace event definitions for handshake, TLS alerts, and related socket context. It is linked into `handshake.o` by the Makefile and used by `alert.c`, `netlink.c`, and `request.c`.

## Risks and Test Signals
Risks are mainly build integration failures if trace event prototypes drift from included types. Test signals are successful build with tracing enabled and observable events for submit, notify errors, accept, done, cancel, destruct, TLS alert send/receive, and content type parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/Kconfig -->
# sources/distributed-fs/ceph-client/net/hsr/Kconfig

## Purpose
Defines kernel configuration entries for IEC 62439-3 HSR/PRP support and the optional PRP duplicate-discard KUnit test.

## APIs, Types, and Functions
Provides tristate `CONFIG_HSR` for "High-availability Seamless Redundancy (HSR & PRP)" and, under `if HSR`, tristate `CONFIG_PRP_DUP_DISCARD_KUNIT_TEST` depending on KUnit and defaulting to `KUNIT_ALL_TESTS`.

## Control Flow, State, and Persistence
There is no runtime control flow. The help text documents operating modes DANH and DANP, redundant transmission over two slave interfaces, ring and parallel network expectations, standard versions, and the need for user validation before safety-critical deployment.

## Dependencies and Integration
Integrates the HSR directory with kernel configuration and kbuild through symbols consumed by `Makefile`. It indirectly controls compilation of the HSR module and PRP duplicate-discard test.

## Risks and Test Signals
Risks include users assuming formal IEC compliance despite the help text warning that this is best effort, and test config accidentally enabled in production-like builds. Test signals are menu visibility, correct tristate dependency behavior, HSR module build under `CONFIG_HSR`, and test suite build under KUnit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/Makefile -->
# sources/distributed-fs/ceph-client/net/hsr/Makefile

## Purpose
Builds the HSR/PRP networking implementation and optional PRP duplicate-discard KUnit test.

## APIs, Types, and Functions
Defines `obj-$(CONFIG_HSR) += hsr.o`, composes `hsr-y` from main, frame registry, device, netlink, slave, and forwarding objects, adds `hsr_debugfs.o` when `CONFIG_DEBUG_FS` is set, and builds `prp_dup_discard_test.o` under `CONFIG_PRP_DUP_DISCARD_KUNIT_TEST`.

## Control Flow, State, and Persistence
No runtime behavior is present. The file controls which implementation units are linked into the HSR module/object based on configuration.

## Dependencies and Integration
Integrates with kbuild and the Kconfig symbols in this directory. The object list shows that this subset is partial: `hsr_netlink.c`, `hsr_slave.c`, and the PRP test are required integration peers even though they are not part of this work item.

## Risks and Test Signals
Risks include missing objects from `hsr-y`, debugfs helper stubs not matching the optional object, and test object linkage drift. Test signals are successful modular and built-in HSR builds with and without debugfs, and KUnit test discovery when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_debugfs.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_debugfs.c

## Purpose
Adds debugfs visibility for HSR/PRP node tables, including node MAC pairs, ingress timestamps, AddrB port, and PRP SAN/DANP classification.

## APIs, Types, and Functions
Defines root dentry `hsr_debugfs_root_dir`, show function `hsr_node_table_show()`, `DEFINE_SHOW_ATTRIBUTE(hsr_node_table)`, and public helpers `hsr_debugfs_rename()`, `hsr_debugfs_init()`, `hsr_debugfs_term()`, `hsr_debugfs_create_root()`, and `hsr_debugfs_remove_root()`.

## Control Flow, State, and Persistence
Root creation makes `/sys/kernel/debug/hsr`. Per HSR device, `hsr_debugfs_init()` creates a directory named after the netdev and a read-only `node_table` file. Reads take RCU, walk `priv->node_db`, skip the self node, and print MAC A, MAC B, last-seen times for slave A/B, AddrB port, and either PRP SAN flags or HSR DAN-H marker. Rename follows netdev name changes by changing the debugfs directory name. Termination removes the per-device subtree, and module exit removes the root. State is debugfs dentries stored in `hsr_priv`.

## Dependencies and Integration
Depends on debugfs, seq_file show helpers, HSR node database structures, RCU list traversal, and self-node detection from `hsr_framereg.c`. It is compiled only when `CONFIG_DEBUG_FS` is enabled.

## Risks and Test Signals
Risks include raw jiffies output being hard to interpret, stale RCU entries during concurrent removal, debugfs creation failures being nonfatal, and rename failure leaving stale directory names. Test signals include debugfs root creation/removal, per-device file creation, node table output for HSR and PRP modes, self-node suppression, and rename on `NETDEV_CHANGENAME`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_device.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_device.c

## Purpose
Implements virtual HSR/PRP net_device behavior: carrier and operstate propagation, MTU and feature handling, transmit entry point, supervision frame generation, VLAN/multicast propagation, protocol operation selection, and device finalization.

## APIs, Types, and Functions
Exports or defines `hsr_check_carrier_and_operstate()`, `hsr_get_max_mtu()`, `hsr_del_ports()`, `hsr_dev_setup()`, `is_hsr_master()`, `hsr_get_port_ndev()`, `hsr_get_port_type()`, and `hsr_dev_finalize()`. Key internal functions include `hsr_dev_xmit()`, `send_hsr_supervision_frame()`, `send_prp_supervision_frame()`, `hsr_announce()`, `hsr_proxy_announce()`, VLAN add/kill handlers, and protocol op tables `hsr_ops` and `prp_ops`.

## Control Flow, State, and Persistence
Carrier checks turn the master carrier on if any non-master port is administratively and operationally up, set master operstate, and arm or delete supervision timers. TX from the virtual master resets skb MAC metadata, locks `seqnr_lock`, and calls `hsr_forward_skb()`. Supervision timers allocate control skbs, fill HSR or PRP supervision tags and payloads, increment normal or supervision sequence counters, optionally add RedBox TLVs, pad to Ethernet minimum, and forward. Finalization initializes lists, locks, self node, sequence counters, timers, multicast address, protocol ops, master/slave/interlink ports, offload flags, PRP slave MAC alignment, RedBox state, debugfs, and prune timers. Persistent runtime state lives in `struct hsr_priv`: ports, node databases, sequence counters, timers, protocol version, RedBox metadata, and offload flags.

## Dependencies and Integration
Depends on net_device operations, HSR slave management, frame registry, forwarding, netlink notifications, timers, RCU port traversal, VLAN helpers, debugfs helpers, and hardware offload feature bits. It integrates with `hsr_netlink.c` for device creation and `hsr_main.c` for netdev event handling.

## Risks and Test Signals
Risks include timer lifetime during port/device teardown, MTU bounds across heterogeneous slaves, supervision skb construction for VLAN/PRP/RedBox variants, offload feature assumptions, PRP MAC mutation of slave B, and partial finalization unwind. Test signals include master open/close warnings, carrier changes from slaves, MTU rejection, TX forwarding, supervision and proxy supervision frames, VLAN propagation unwind, debugfs creation, RedBox interlink setup, and finalization failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_device.h -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_device.h

## Purpose
Declares the HSR/PRP virtual device setup, finalization, port cleanup, carrier/operstate, and MTU helper APIs.

## APIs, Types, and Functions
Declares `hsr_del_ports()`, `hsr_dev_setup()`, `hsr_dev_finalize()`, `hsr_check_carrier_and_operstate()`, and `hsr_get_max_mtu()`.

## Control Flow, State, and Persistence
No executable logic is present. The declarations expose device lifecycle operations to the netlink creation path, slave teardown path, and event notification path.

## Dependencies and Integration
Depends on `linux/netdevice.h` and `hsr_main.h` for `struct hsr_priv`, port types, and protocol constants. Implemented in `hsr_device.c` and consumed by `hsr_main.c`, `hsr_netlink.c`, and other HSR peers.

## Risks and Test Signals
Risks are header/API drift between implementation and callers, especially around `hsr_dev_finalize()` arguments for optional interlink/RedBox and extack reporting. Test signals are clean builds across HSR netlink creation, slave unregister, and notifier code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_forward.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_forward.c

## Purpose
Implements HSR/PRP frame classification, tag/trailer creation and removal, duplicate-aware forwarding, RedBox forwarding policies, and local delivery.

## APIs, Types, and Functions
Exports `hsr_forward_skb()`, `hsr_create_tagged_frame()`, `prp_create_tagged_frame()`, `hsr_get_untagged_frame()`, `prp_get_untagged_frame()`, `hsr_drop_frame()`, `prp_drop_frame()`, `hsr_fill_frame_info()`, and `prp_fill_frame_info()`. Key helpers include `is_supervision_frame()`, `is_proxy_supervision_frame()`, `create_stripped_skb_hsr()`, `prp_fill_rct()`, `hsr_fill_tag()`, `hsr_deliver_master()`, `hsr_xmit()`, `hsr_forward_do()`, `check_local_dest()`, `handle_std_frame()`, and `fill_frame_info()`.

## Control Flow, State, and Persistence
`hsr_forward_skb()` fills a transient `hsr_frame_info`, registers ingress time, forwards to eligible ports, updates master/interlink TX stats, and frees all held skb variants. Classification detects supervision frames, proxy supervision, node source, VLAN encapsulation, HSR tags, PRP trailers, standard frames, local destination, and SAN origin. Forwarding iterates all ports except the receive port, skips inappropriate local/nonlocal destinations, respects hardware duplicate generation, registers outgoing duplicates, handles supervision frames locally, applies protocol-specific drop rules, creates tagged frames for slaves and untagged frames for master/interlink, then either injects locally via `netif_rx()` or transmits with `dev_queue_xmit()`. State mutations occur in skb clones, port/device stats, sequence numbers for standard master/interlink frames, and node duplicate records via `hsr_framereg.c`.

## Dependencies and Integration
Depends on HSR header layouts, PRP RCT helpers, VLAN parsing, skb cloning/copying, hardware offload feature flags, node database helpers, address substitution helpers, and protocol ops installed by `hsr_device.c`.

## Risks and Test Signals
Risks include malformed skb header lengths, checksum offset adjustments when adding/removing HSR tags, PRP trailer size validation, forwarding loops if duplicate registration fails open, RedBox drop policy mistakes, and interactions with hardware HSR tag/duplicate offloads. Test signals include supervision frame validation, HSR v0/v1 tag handling, PRP RCT creation/removal, VLAN frames, local unicast/multicast delivery, duplicate discard, SAN frames, RedBox proxy rules, offloaded forwarding, and malformed frame drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_forward.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_forward.h -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_forward.h

## Purpose
Declares the HSR/PRP forwarding and frame-conversion interface used by the device protocol ops.

## APIs, Types, and Functions
Declares `hsr_forward_skb()`, PRP/HSR tagged frame creation, untagged frame extraction, protocol-specific drop decisions, and protocol-specific frame-info fill functions.

## Control Flow, State, and Persistence
No runtime logic is present. The header forms the contract between `hsr_device.c` protocol operation tables and `hsr_forward.c` implementations.

## Dependencies and Integration
Depends on `linux/netdevice.h`, `hsr_main.h`, and `struct hsr_frame_info` from `hsr_framereg.h`. Consumers are mainly `hsr_device.c` and implementation-local peers.

## Risks and Test Signals
Risks include signature drift between protocol ops and declarations or incorrect assumptions about skb ownership. Test signals are successful build and exercise of HSR and PRP protocol ops through `hsr_forward_skb()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_forward.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.c

## Purpose
Maintains HSR/PRP node databases, self-node recognition, proxy node state, duplicate-discard sequence tracking, supervision-frame node merging, address substitution, node pruning, and node data export.

## APIs, Types, and Functions
Implements `hsr_addr_is_redbox()`, `hsr_addr_is_self()`, `hsr_is_node_in_db()`, `hsr_create_self_node()`, `hsr_del_self_node()`, `hsr_del_nodes()`, `prp_handle_san_frame()`, `hsr_get_node()`, `prp_update_san_info()`, `hsr_get_seq_block()`, `hsr_handle_sup_frame()`, `hsr_addr_subst_source()`, `hsr_addr_subst_dest()`, `hsr_register_frame_in()`, `hsr_register_frame_out()`, `prp_register_frame_out()`, `hsr_prune_nodes()`, `hsr_prune_proxy_nodes()`, `hsr_get_next_node()`, and `hsr_get_node_data()`.

## Control Flow, State, and Persistence
Nodes are looked up by MAC A or B in RCU lists and created on first valid traffic. Each node records MAC A/B, AddrB port, ingress timestamps per port, stale flags, SAN flags, removed state, an XArray of sequence blocks, and a fixed backing buffer of sparse sequence bitmaps. Duplicate discard maps sequence numbers into 128-entry blocks, expires old blocks, reuses a bounded ring of blocks, and sets bits per outgoing port or PRP master path; failure to allocate or validate errs toward accepting frames. Supervision handling can merge a node first seen by MAC B into the real MAC A node, copy newer timestamps, OR sequence bitmaps, set AddrB port, and remove the duplicate node with RCU freeing. Prune timers detect ring errors from slave timing skew, emit netlink ring/nodedown events, remove old node/proxy entries, and restart themselves. State persists in `hsr_priv->self_node`, `node_db`, `proxy_node_db`, and each `hsr_node` until pruned or device teardown.

## Dependencies and Integration
Depends on HSR/PRP header parsing helpers, RCU lists, spinlocks, XArray, timers, netlink notification helpers, skb MAC headers, and protocol callbacks from `hsr_device.c`. KUnit visibility exposes sequence block lookup and PRP registration behavior.

## Risks and Test Signals
Risks include RCU/list removal races, bounded sequence block reuse accepting duplicates, sequence port count mismatch, jiffies wrap/stale handling, supervision skb pull/push correctness, node merge races, and ring-error false positives. Test signals include self-node replacement/removal, node creation from HSR/PRP/SAN traffic, duplicate discard across block boundaries and expiry, PRP master duplicate discard, supervision merge with RedBox TLV, address substitution, prune nodedown/ringerror events, proxy pruning, and node data export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.h -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.h

## Purpose
Defines HSR/PRP frame metadata and node registry structures plus the public frame-registry API used by forwarding, device, debugfs, and netlink code.

## APIs, Types, and Functions
Defines `struct hsr_frame_info`, `struct hsr_seq_block`, and `struct hsr_node`, sequence block constants and index/bit macros, inline `hsr_seq_block_size()`, and declarations for node deletion, lookup, supervision handling, address substitution, frame in/out registration, pruning timers, self-node creation, node iteration/data export, PRP SAN handling, database membership, and KUnit-only `hsr_get_seq_block()`.

## Control Flow, State, and Persistence
The header has no executable flow except the inline size helper, which warns if `seq_port_cnt` is zero and computes the flexible bitmap allocation size. It documents persistent node state: MAC identity, AddrB port, per-port ingress times/staleness, SAN markers, removal marker, duplicate-detection XArray, fixed sequence block backing buffer, next block cursor, and RCU head.

## Dependencies and Integration
Depends on `hsr_main.h` for protocol and port definitions. Used by `hsr_forward.c`, `hsr_framereg.c`, `hsr_device.c`, `hsr_debugfs.c`, and netlink code that reports node state.

## Risks and Test Signals
Risks include the pseudo-flexible `seq_nrs` layout depending on `struct_size_t()`, mismatched `seq_port_cnt`, ABI-like expectations between frame info producers and consumers, and enum indexes used directly for arrays. Test signals include build-time structure use, KUnit duplicate-discard tests, node-table debugfs reads, and netlink node data queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_main.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_main.c

## Purpose
Provides HSR/PRP module initialization, netdevice event handling, port lookup, and protocol version export.

## APIs, Types, and Functions
Defines notifier `hsr_nb`, module init/exit functions `hsr_init()` and `hsr_exit()`, helper `hsr_slave_empty()`, notifier callback `hsr_netdev_notify()`, exported `hsr_get_version()`, and `hsr_port_get_hsr()`.

## Control Flow, State, and Persistence
The netdevice notifier maps events to the affected HSR port or master. UP/DOWN/CHANGE events recompute carrier, operstate, and supervision timers. CHANGENAME renames debugfs for master devices. CHANGEADDR on a slave updates master and, for PRP, slave B addresses, then recreates the self node so looped self frames are recognized. CHANGEMTU on slaves clamps the master MTU to the smallest slave MTU minus tag length. UNREGISTER removes non-master ports and deletes the master device if no slaves remain. PRE_TYPE_CHANGE rejects changing slave Ethernet type. Module init verifies HSR tag size, registers the notifier, and initializes HSR netlink; exit tears down netlink, debugfs root, and notifier. Persistent module state is the registered notifier and netlink family; per-device state is managed in `hsr_priv`.

## Dependencies and Integration
Depends on rtnetlink notifier infrastructure, HSR device/slave/netlink/frame registry APIs, debugfs rename/remove helpers, and net_device lifetimes. It exports version and master-detection utilities for other kernel users.

## Risks and Test Signals
Risks include notifier ordering during unregister, self-node update failure after slave MAC changes, PRP MAC synchronization side effects, automatic master removal when slaves disappear, MTU updates bypassing normal change paths, and PRE_TYPE_CHANGE blocking legitimate transitions. Test signals include module load/unload, slave carrier changes, slave MAC change in HSR and PRP modes, slave MTU change, slave unregister removing the master when empty, debugfs rename, type-change rejection, and `hsr_get_version()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_main.c -->

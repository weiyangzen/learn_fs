# sources/distributed-fs/ceph-client/net/mac80211/trace.h

## Purpose
This header declares the main mac80211 tracepoint system. It instruments driver callbacks, driver return values, driver-called mac80211 APIs, queue stop/wake internals, multi-link operation changes, channel context management, power-save/TWT/NAN/TDLS operations, and other high-value control paths.

## Important APIs, types, and functions
- Common field macros such as `LOCAL_ENTRY`, `STA_ENTRY`, `VIF_ENTRY`, `CHANDEF_ENTRY`, `CHANCTX_ENTRY`, `KEY_ENTRY`, and `AMPDU_ACTION_ENTRY` centralize trace record layout and print formatting.
- Event classes such as `local_only_evt`, `local_sdata_addr_evt`, `local_u32_evt`, `local_sdata_evt`, `sta_event`, `chanswitch_evt`, `release_evt`, `mgd_prepare_complete_tx_evt`, `local_chanctx`, `local_sdata_chanctx`, and `sta_flag_evt` reduce duplication across related events.
- Driver callback tracepoints include lifecycle/configuration (`drv_start`, `drv_stop`, `drv_config`, `drv_add_interface`, `drv_change_interface`, `drv_remove_interface`), keying (`drv_set_key`, `drv_update_tkip_key`, `drv_get_key_seq`, `drv_set_rekey_data`), scanning, station operations, AMPDU, channel switching, chanctx assignment/switching, AP/IBSS/NAN/PMSR/TDLS/TWT, netdev offload, traffic-control, and MLO/EML/TTLM operations.
- API tracepoints include `api_start_tx_ba_session`, BA callbacks, restart/beacon/connection loss, CQM notifications, scan completion, channel switch completion, GTK rekey notification, EOSP/buffered-station operations, radar detection, SMPS, and OMI bandwidth preparation/finalization.
- Internal queue tracepoints `wake_queue` and `stop_queue` record queue, reason, and refcount.

## Control flow
This header follows the Linux tracepoint pattern: guarded declarations are included normally by users, while `trace.c` defines `CREATE_TRACE_POINTS` and includes the header once to instantiate tracepoints. Call sites invoke generated functions such as `trace_drv_config()` and `trace_api_scan_completed()`. Most driver callback wrappers in `driver-ops.h` trace before invoking a driver op and then trace a typed return event. Other direct call sites in `mlme.c`, `scan.c`, `sta_info.c`, `ht.c`, `he.c`, `main.c`, `offchannel.c`, `util.c`, and aggregation code emit API or internal events.

## State and persistence
The header defines trace record schemas, not mac80211 state. At runtime each enabled event snapshots selected fields from live objects into trace buffers: wiphy names, vif names/types, station addresses, chandefs, key metadata, changed bitmasks, link IDs, queue reasons, and selected payload arrays. Dynamic arrays are used for variable-length data such as SSIDs, ARP address lists, and vif channel-context switch arrays. Trace records persist according to kernel tracing buffer configuration, not in mac80211 objects.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>`, `<net/mac80211.h>`, `ieee80211_i.h`, and many cfg80211/mac80211 internal types referenced in trace prototypes. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` block is required by the kernel trace generator. The trace names form a user-visible ABI for tracing scripts under systems that consume ftrace/perf events, so renames and field layout changes can affect observability tooling.

## Risks and edge cases
Trace macros dereference many pointers supplied by call sites; call sites must ensure objects remain valid for the duration of trace evaluation. Some events snapshot sensitive material-adjacent metadata such as key indices, replay counters, rekey material arrays, BSSIDs, and SSIDs, so tracing configuration matters in production. Dynamic array lengths depend on live fields and must remain bounded; for example ARP addresses are capped to `IEEE80211_BSS_ARP_ADDR_LIST_LEN`. The `drv_switch_vif_chanctx` helper structs are packed and manually populated, so changes to `struct ieee80211_vif_chanctx_switch` require matching trace updates.

## Test signals
Primary signals are build-time tracepoint generation and runtime availability of `/sys/kernel/tracing/events/mac80211/*` events. Functional signals are trace consistency around driver op wrappers: a driver operation should produce an entry event and an appropriate return event. BPF/ftrace scripts that decode event fields are useful regression detectors for field names and formats.

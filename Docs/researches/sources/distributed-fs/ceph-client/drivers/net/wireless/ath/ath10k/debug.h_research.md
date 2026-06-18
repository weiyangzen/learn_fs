# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debug.h

## Purpose

`debug.h` declares ath10k logging, debug masks, packet-log metadata, debugfs APIs, station debugfs hooks, stats helpers, and compile-time stubs for builds without debugfs or verbose debugging. It is the public debug interface consumed by core, bus, WMI, HTT, RX/TX, and mac80211 integration code.

## Important APIs and Types

`enum ath10k_debug_mask` defines bitmask categories for PCI, WMI, HTC, HTT, MAC, boot, dumps, management, data, BMI, regulatory, testmode, bus-specific logging, QMI, station logging, and `ATH10K_DBG_ANY`. The global `ath10k_debug_mask` is declared here and defined as a module parameter in `core.c`.

`enum ath10k_pktlog_filter` defines firmware packet log event filters for RX, TX, rate-control find/update, debug print, peer stats, and any. `enum ath10k_dbg_aggr_mode`, `enum ath_pktlog_type`, and packed `struct ath10k_pktlog_hdr` support debug aggregation and packet-log payload interpretation. `ATH10K_FW_STATS_BUF_SIZE`, `ATH10K_TX_POWER_MAX_VAL`, and `ATH10K_TX_POWER_MIN_VAL` define shared debug limits.

Always-available declarations include `ath10k_info()`, `ath10k_err()`, `ath10k_warn()`, hardware/firmware/board/boot print helpers, and `ath10k_print_driver_info()`. With `CONFIG_ATH10K_DEBUGFS`, the header declares debug lifecycle, firmware/TPC stats processing, dbglog handling, ethtool stats hooks, inline accessors for dbglog mask/level and extended TX stats, and the DFS stat increment macro. Without debugfs, equivalent stubs either return success/default values or free passed TPC allocations.

With `CONFIG_MAC80211_DEBUGFS`, station debugfs and RX TID stats update functions are declared; otherwise no-op stubs are used. With `CONFIG_ATH10K_DEBUG`, verbose debug and dump functions are declared; otherwise they compile away.

## Control Flow and Integration

The `ath10k_dbg()` macro avoids calling `__ath10k_dbg()` unless the mask is enabled or the tracepoint is active. This keeps hot paths cheap while preserving tracing support. Debugfs lifecycle functions are called from `core.c` during object creation, firmware start/stop, registration, unregistration, and destroy. Stats process functions are called from WMI event handlers; station TID stats hooks are called from RX/HTT paths.

## State and Persistence

The header owns no storage except declarations, but it exposes access to global `ath10k_debug_mask` and inline reads of `struct ath10k_debug` fields. Debug mask and coredump/debug parameters are runtime module state; debugfs settings persist only in memory until device removal.

## Dependencies and Integration Points

`debug.h` includes `trace.h` and Linux types and relies on `struct ath10k`, mac80211 types, skb, ethtool stats, and HTT RX indication types via surrounding includes. It is included widely because the lightweight logging macros are used throughout ath10k.

## Risks

Debug mask values are effectively user-facing through module parameters and trace expectations; changing them can break operational debugging. Stub behavior must match caller assumptions when debugfs or debug logging is disabled. The `ath10k_dbg()` macro references tracepoint availability, so trace header changes can affect compilation. Packed packet-log headers and filter bit values must stay aligned with firmware/userspace tooling.

## Test Signals

Build matrix coverage is the main signal: `CONFIG_ATH10K_DEBUGFS`, `CONFIG_MAC80211_DEBUGFS`, and `CONFIG_ATH10K_DEBUG` enabled and disabled. Runtime signals include debug-mask logging only when enabled, tracepoints still receiving debug messages when active, no-op stubs not changing behavior in production builds, and successful ethtool/debugfs integration when debugfs is enabled.

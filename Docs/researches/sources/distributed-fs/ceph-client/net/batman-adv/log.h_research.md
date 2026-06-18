<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/log.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/log.h research

Purpose: defines batman-adv debug log levels and logging macros that route messages to the debug trace backend and kernel log.

Important APIs and types: `enum batadv_dbg_level` defines bit flags for BATMAN, ROUTES, TT, BLA, DAT, MCAST, TP_METER, and ALL. Debug builds declare setup/cleanup and `batadv_debug_log()`, and implement `_batadv_dbg()` as a log-level and optional `net_ratelimit()` gate. Non-debug builds provide no-op setup/cleanup and no-op `_batadv_dbg()`. `batadv_dbg()`, `batadv_dbg_ratelimited()`, `batadv_info()`, and `batadv_err()` are the main call sites.

Control flow and state behavior: `_batadv_dbg()` reads `bat_priv->log_level` atomically and calls `batadv_debug_log()` only if the requested type bit is enabled. `batadv_info()` and `batadv_err()` always write to kernel log with mesh interface name and also send the message to debug logging under `BATADV_DBG_ALL`.

Dependencies and integration: includes `main.h`, atomic, bitops, compiler, and printk. Used across packet, gateway, BLA, DAT, hard-interface, and routing modules for diagnostics.

Risks: `batadv_info()` and `batadv_err()` evaluate `netdev_priv(_netdev)` and require a valid mesh netdev. Debug macros compile away in non-debug builds, so side effects inside arguments must be avoided. `BATADV_DBG_ALL` is fixed to 255 and must cover defined bits.

Test signals: debug and non-debug builds, log level sysfs/netlink controls, ratelimited flood behavior, info/error kernel log prefixing, and no side effects from disabled debug statements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/log.h -->

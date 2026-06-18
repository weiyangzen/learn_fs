<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/main.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/main.h research

Purpose: central batman-adv header defining driver identity, protocol constants, timing values, feature limits, common enums, global declarations, and widely used inline helpers/macros.

Important APIs and types: defines source version, driver metadata, TQ/throughput constants, TTL, purge and TT/DAT/BLA/fragmentation timeouts, aggregation limits, queue lengths, `enum batadv_mesh_state`, `enum batadv_uev_action`, `enum batadv_uev_type`, gateway threshold, fragment limits, DAT candidate markers, and debug `pr_fmt`. It declares global hardif list/generation, event workqueue, mesh lifecycle, receive functions, counter helpers, VLAN/AP isolation and uevent helpers. Inline helpers include `batadv_print_vid()`, `batadv_compare_eth()`, `batadv_has_timed_out()`, sequence-number comparison macros, and per-cpu counter updates.

Control flow and state behavior: constants in this header shape behavior across modules: BLA periodic/timeout windows, DAT entry lifetime, fragment buffer limits, OGM/TT work periods, gateway election threshold, and queue sizes. The sequence macros implement wraparound comparisons using two's-complement assumptions. `BATADV_SKB_CB()` reserves skb control-buffer layout for batman-adv private metadata.

Dependencies and integration: includes many kernel networking headers, batman packet UAPI, `types.h`, and recursively includes `main.h` due to existing code structure. It is included by almost every batman-adv C file. Constants are consumed by BLA, DAT, fragmentation, hard-interface MTU calculations, gateway selection, routing, translation table, multicast, and logging.

Risks: changing constants has broad behavioral impact and can silently alter network convergence, memory pressure, or packet compatibility. `BATADV_MAX_MTU` depends on `batadv_max_header_len()` and must stay consistent with packet structure build checks in `main.c`. Sequence macros rely on operands of same type and intentionally enforce that through pointer comparison. `batadv_add_counter()` uses per-cpu storage and assumes `bat_priv->bat_counters` has been allocated.

Test signals: compile-time structure size checks, builds across 32/64-bit, sequence wraparound unit tests, timeout behavior using jiffies wrap simulation, MTU calculations with fragmentation, per-cpu counter access under traffic, and feature combinations for BLA/DAT/MCAST/debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/main.h -->

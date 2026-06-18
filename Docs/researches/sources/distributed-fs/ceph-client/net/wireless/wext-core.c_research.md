# sources/distributed-fs/ceph-client/net/wireless/wext-core.c

Purpose: implements the Wireless Extensions core: standard ioctl metadata, rtnetlink wireless event emission, handler lookup, userspace copy wrappers, compat ioctl translation, and stream helpers used by scan/range formatters.

Important APIs/functions: exported `wireless_send_event()`, `wireless_nlevent_flush()`, `get_wireless_stats()`, `wext_handle_ioctl()`, compat `compat_wext_handle_ioctl()`, and `iwe_stream_add_event/point/value()` are the main public surfaces. Internal dispatch pivots through `standard_ioctl[]`, `standard_event[]`, `get_handler()`, `ioctl_standard_iw_point()`, `ioctl_standard_call()`, `wireless_process_ioctl()`, and `wext_ioctl_dispatch()`.

Control flow: event senders validate the command against standard ioctl/event descriptions, size variable payloads, package `IFLA_WIRELESS` into an `RTM_NEWLINK` skb, add a 32-bit compat skb as `frag_list` when needed, enqueue on `net->wext_nlevents`, and schedule work to flush via rtnetlink. Ioctls copy an `iwreq`, check CAP_NET_ADMIN for setters and key reads, resolve the netdev under RTNL, handle stats/private special cases, find cfg80211 or legacy handlers, marshal fixed or point payloads, call handlers, optionally call commit, send events for mutating commands, and copy GET results back.

State and persistence: state is per-net pending event queues plus transient ioctl buffers. Driver/cfg80211 state is reached through handler callbacks. Stats reads may clear `IW_QUAL_*_UPDATED`. WEXT is deliberately disabled for MLO or `WIPHY_FLAG_DISABLE_WEXT` devices, and cfg80211 users receive a one-time deprecation warning.

Dependencies and integration: integrates netdevice notifier ordering, pernet lifecycle, rtnetlink, cfg80211 WEXT compatibility, legacy `iw_handler_def`, Linux capabilities, usercopy, and compat ABI layouts. Stream helpers are consumed by drivers/cfg80211 when composing Wireless Extension result buffers.

Risks and test signals: variable-length `iw_point` paths carry the most risk: ESSID NUL compatibility, NOMAX allocation, encode-ext key length checks, restricted event payload suppression, and 32/64-bit layout differences. Tests should cover invalid token counts, SET/GET copy faults, CAP_NET_ADMIN denial, cfg80211 disabled/MLO rejection, event queue flushing across netdevice state changes, compat event consumers, and scan/stats/range commands.

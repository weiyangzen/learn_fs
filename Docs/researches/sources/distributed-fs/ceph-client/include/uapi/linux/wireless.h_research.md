<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wireless.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wireless.h

Purpose: defines legacy Wireless Extensions version 22: ioctl numbers, event IDs, wireless statistics, request payloads, scan/auth/encoding structures, capability constants, and event stream layout.

Important APIs and types: `SIOCSIW*`/`SIOCGIW*` ioctls configure name, NWID, frequency, mode, sensitivity, range, stats, spy, AP, scan, ESSID, rates, RTS, fragmentation, TX power, retry, encoding, power, WPA IEs, MLME, auth, encode-ext, and PMKSA. `IWEV*` events report drops, quality, custom data, registration, WPA IEs, MIC failures, association IEs, and PMKID candidates. Core structs include `iw_param`, `iw_point`, `iw_freq`, `iw_quality`, `iw_statistics`, `iwreq`, `iw_range`, `iw_priv_args`, and `iw_event`.

Control flow, state, and persistence: userspace issues ioctl requests through netdevs and receives rtnetlink wireless events; drivers translate them to device configuration and stats. Runtime state is wireless driver/device state, not this header.

Dependencies and integration points: integrates legacy wireless tools, net/core wireless handlers, rtnetlink `IFLA_WIRELESS`, and older 802.11 drivers predating cfg80211/nl80211.

Risks and test signals: high-risk areas are 32/64-bit pointer layout, event packing without leaking kernel memory, private ioctl argument encoding, variable-length `iw_point` buffers, and obsolete WPA fields. Test `iwconfig`/wireless-tools compatibility, scan event parsing, private ioctls, mixed-arch compat, and stats/range reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wireless.h -->

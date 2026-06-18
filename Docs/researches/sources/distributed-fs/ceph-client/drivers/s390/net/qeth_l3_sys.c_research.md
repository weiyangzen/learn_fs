# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3_sys.c

Purpose: exposes L3-specific sysfs controls for routing mode, HiperSockets sniffer mode, HSUID, IP address takeover prefixes, VIPA addresses, and RXIP takeover addresses.

Important APIs and functions: `qeth_l3_attr_groups` publishes base L3, `ipa_takeover`, `vipa`, and `rxip` groups. Route handlers call `qeth_l3_setrouting_v4()` and `qeth_l3_setrouting_v6()`. IPATO handlers parse `addr/mask` with `qeth_l3_parse_ipatoe()` and call add/delete/update helpers. VIPA/RXIP handlers parse addresses and call `qeth_l3_modify_rxip_vipa()`. HSUID calls `qeth_configure_cq()` and `qeth_l3_modify_hsuid()`.

Control flow: route stores parse symbolic router/connector values, update cached route type under `conf_mutex`, and issue hardware routing updates if reachable, rolling back on failure. Sniffer and HSUID require IQD and down state. IPATO enable requires down state, while invert and prefix updates take `ip_lock` and recompute takeover flags. VIPA/RXIP stores directly modify the L3 address table through main-code helpers.

State and persistence: writes update runtime `card->options.route4/route6`, `card->options.sniffer`, `card->options.hsuid`, `card->ipato`, and address tables. Offline settings remain in memory until device removal. HSUID is converted to EBCDIC for storage and copied to `dev->perm_addr`.

Dependencies and integration: depends on sysfs, qeth L3 main exports, Linux address parsers, EBCDIC conversion, CQ configuration, and qeth card locks. User-visible route strings reflect broadcast echo capability with a `+` suffix.

Risks: `qeth_l3_parse_ipatoe()` temporarily writes a NUL into the sysfs buffer at the slash; callers must pass mutable buffers from sysfs. VIPA accepts multicast unless main/hardware rejects it, while RXIP explicitly rejects multicast. Some IPATO changes can happen while online and only affect cached takeover flags for future hardware operations.

Test signals: route value parsing and rollback, unsupported route modes on IQD vs OSA, sniffer enable when hardware advertises `CHSC_AC2_SNIFFER_AVAILABLE`, HSUID add/delete and CQ transitions, IPATO prefix add/delete/show including duplicate and invalid masks, VIPA/RXIP IPv4/IPv6 add/delete and multicast rejection for RXIP.

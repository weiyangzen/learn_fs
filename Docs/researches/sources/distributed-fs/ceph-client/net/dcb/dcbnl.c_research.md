# sources/distributed-fs/ceph-client/net/dcb/dcbnl.c

## Purpose

`dcbnl.c` implements the Data Center Bridging rtnetlink interface and the kernel-side DCB application and rewrite tables. It supports legacy CEE DCBX commands, IEEE 802.1Qaz/Qau/Qbb attributes, PFC, ETS/priority groups, BCN, DCBX mode, feature config, application trust, and helper APIs that drivers and upper layers use to query or mutate DCB app mappings.

## Important APIs, Types, and Functions

The file defines netlink policy tables for top-level DCB attributes and nested PFC, PG, TC, capability, NUMTCS, BCN, APP, IEEE, and feature-config attributes. Main request handlers include `dcbnl_getstate()`, `dcbnl_setstate()`, `dcbnl_getpfccfg()`, `dcbnl_setpfccfg()`, `dcbnl_getcap()`, `dcbnl_getnumtcs()`, `dcbnl_setnumtcs()`, `dcbnl_getapp()`, `dcbnl_setapp()`, priority-group handlers, BCN handlers, `dcbnl_ieee_get()`, `dcbnl_ieee_set()`, `dcbnl_ieee_del()`, `dcbnl_getdcbx()`, `dcbnl_setdcbx()`, feature handlers, and `dcbnl_cee_get()`. Exported data APIs include `dcb_getapp()`, `dcb_setapp()`, `dcb_ieee_getapp_mask()`, `dcb_ieee_setapp()`, `dcb_ieee_delapp()`, `dcb_getrewr()`, `dcb_setrewr()`, `dcb_delrewr()`, DSCP/PCP mapping helpers, and default-priority lookup.

## Control Flow

`dcb_doit()` is the rtnetlink entry point for `RTM_GETDCB` and `RTM_SETDCB`. It checks capabilities for set operations, parses attributes, finds the target device by `DCB_ATTR_IFNAME`, validates `dev->dcbnl_ops`, allocates a reply, and dispatches through `reply_funcs[dcb->cmd]`. Most handlers parse a nested attribute set, call optional driver callbacks from `struct dcbnl_rtnl_ops`, and encode a reply or status byte. IEEE set/delete paths can also fall back to the file's software APP and rewrite tables when driver-specific callbacks are absent. Notification helpers build IEEE or CEE snapshots and multicast them on `RTNLGRP_DCB`.

## State and Persistence Behavior

The persistent state owned here is `dcb_app_list`, `dcb_rewr_list`, and `dcb_lock`. Entries are keyed by netdevice ifindex plus selector/protocol/priority depending on APP versus rewrite semantics. CEE `dcb_setapp()` replaces an existing selector/protocol mapping or deletes it when priority is zero. IEEE `dcb_ieee_setapp()` permits multiple priorities for the same selector/protocol. Rewrite entries require selector/priority/protocol uniqueness. Device unregister triggers `dcbnl_flush_dev()`, which clears APP entries for the ifindex; rewrite entries are not flushed in this function. Successful APP mutations broadcast `DCB_APP_EVENT` through `dcbevent`.

## Dependencies and Integration Points

The file integrates with rtnetlink, generic netlink attribute helpers, netdevice lookup/notifiers, `struct dcbnl_rtnl_ops` supplied by drivers, and `dcbevent.c`. It exports helper APIs used by classifiers, VLAN/DSCP logic, and drivers that need app-priority maps. Initialization registers netdevice and rtnetlink handlers with `device_initcall()`.

## Risks

Netlink handlers have many optional driver callbacks; missing callback checks must remain complete to avoid NULL calls. Several setters perform multiple driver operations without rollback, matching the file comment that partial success is not reconciled. Attribute validation is especially important for app selector/type matching and app trust duplicate detection. Global APP/rewrite tables are ifindex based, so stale entries on unregister or ifindex reuse are a risk, particularly for rewrite entries. Message construction has many nested attributes and must cancel nests on `-EMSGSIZE` to avoid malformed replies.

## Test Signals

Exercise all DCB commands through rtnetlink with supported and unsupported driver callbacks, malformed nested attributes, non-admin set attempts, IEEE APP add/delete, CEE priority-zero delete, duplicate APP and rewrite entries, app trust selector validation, DCBX mode changes, device unregister cleanup, and multicast notification contents. Lockdep and fault-injection tests around `kmalloc_obj()` and skb size failures are useful.

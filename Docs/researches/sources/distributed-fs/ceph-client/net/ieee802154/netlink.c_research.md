## sources/distributed-fs/ceph-client/net/ieee802154/netlink.c

Purpose: legacy generic-netlink family implementation for IEEE 802.15.4 management. It provides helpers for constructing replies/events and registers a large operation table implemented mostly by `nl-phy.c` and `nl-mac.c`.

Important APIs/types/functions: `ieee802154_nl_create()` creates an event skb with an atomic sequence number protected by `ieee802154_seq_lock`. `ieee802154_nl_mcast()` ends the genl message and multicasts to a legacy group. `ieee802154_nl_new_reply()` and `ieee802154_nl_reply()` build and finalize replies. The `ieee802154_ops` table registers PHY/interface commands, MLME commands, MAC parameter setting, and LLSEC key/device/devkey/seclevel commands. `nl802154_family` is the legacy family named by `IEEE802154_NL_NAME`.

Control flow and state: init registers the family; exit unregisters it. Event creation increments a global sequence under spinlock with IRQ save/restore. Each reply helper expects the caller to have put attributes before finalization.

Dependencies and integration points: uses `ieee802154_policy` from `nl_policy.c`, group names from UAPI, and command handlers from `ieee802154.h`. Core module init calls `ieee802154_nl_init()` before modern `nl802154_init()`.

Risks: legacy ops use `GENL_DONT_VALIDATE` style through macros only indirectly; policy coverage exists but many handlers still perform manual checks. `ieee802154_nl_mcast()` extracts the genl header from the skb; callers must pass an skb created by the matching helper. Global sequence state is process-wide, not per-net.

Test signals: family registration, command enumeration, multicast delivery for start/beacon/coord events, reply generation under attribute-fill failures, and legacy userspace compatibility.

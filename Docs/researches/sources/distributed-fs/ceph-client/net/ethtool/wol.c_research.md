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

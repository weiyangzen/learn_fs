# sources/distributed-fs/ceph-client/net/ethtool/linkinfo.c

## Purpose
This file implements generic netlink `LINKINFO_GET` and `LINKINFO_SET` handling for physical link metadata: port type, PHY address, MDI/MDI-X state, MDI-X control, and transceiver type.

## Important APIs, Types, And Functions
`struct linkinfo_req_info` embeds `ethnl_req_info`. `struct linkinfo_reply_data` stores `struct ethtool_link_ksettings` and a pointer to its base `struct ethtool_link_settings`. `ethnl_linkinfo_get_policy`, `ethnl_linkinfo_set_policy`, and `ethnl_linkinfo_request_ops` are the exported integration objects. The main callbacks are `linkinfo_prepare_data()`, `linkinfo_reply_size()`, `linkinfo_fill_reply()`, `ethnl_set_linkinfo_validate()`, and `ethnl_set_linkinfo()`.

## Control Flow
GET calls `ethnl_ops_begin()`, retrieves link ksettings through `__ethtool_get_link_ksettings()`, completes driver ops, sizes five `u8` attributes, and emits them. SET validates the driver has both `get_link_ksettings` and `set_link_ksettings`, fetches current settings, updates only supplied attributes via `ethnl_update_u8()`, returns no-op when unchanged, otherwise calls the driver's `set_link_ksettings()`.

## State And Persistence
The file stores no persistent state. SET mutates driver-maintained link settings through the ethtool ops callback. The generic set wrapper in `netlink.c` emits `ETHTOOL_MSG_LINKINFO_NTF` when the callback reports a change.

## Dependencies And Integration Points
It depends on the shared netlink request framework in `netlink.c`/`netlink.h`, common ethtool ksettings helpers in `ioctl.c`, and driver `ethtool_ops`. It shares the same `ethtool_link_ksettings` object with `linkmodes.c`, splitting metadata from advertised modes and speed/duplex fields for netlink ABI purposes.

## Risks And Edge Cases
Unsupported drivers return `-EOPNOTSUPP`. The setter does not locally validate enumerated port or MDI-X values, relying on netlink policy type checks and the driver. Because it rewrites the whole ksettings structure after changing a few base fields, drivers must tolerate unchanged link mode fields being passed back.

## Test Signals
Tests should cover GET on devices with and without `get_link_ksettings`, no-op SET, SET failure propagation, and notification emission. Good integration checks compare ioctl `GLINKSETTINGS`/`GSET` output with netlink `LINKINFO_GET`.

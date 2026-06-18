## sources/distributed-fs/ceph-client/net/ieee802154/nl_policy.c

Purpose: legacy IEEE 802.15.4 generic-netlink attribute policy table.

Important APIs/types/functions: defines `const struct nla_policy ieee802154_policy[IEEE802154_ATTR_MAX + 1]`. It assigns types and lengths for device/PHY names, indices, status, short/hardware addresses, PAN IDs, channel/page, coordinator/source/destination addresses, capability/reason/scan fields, ED/channel-page lists, MAC params, and low-level security attributes. `NLA_HW_ADDR` is defined as `NLA_U64`.

Control flow and state: no runtime control flow beyond generic-netlink validation. The table is referenced by the legacy `nl802154_family` in `netlink.c` and constrains messages before per-command parsing.

Dependencies and integration points: uses `linux/nl802154.h` legacy UAPI constants and netlink policy types. Works with `nl-mac.c` and `nl-phy.c`, which still perform required-attribute and semantic validation.

Risks: policy type/length mismatches can reject valid legacy userspace or admit malformed data that command handlers do not expect. Hardware address as U64 differs from raw byte-array handling in some handlers, so endian conversion helpers must stay consistent.

Test signals: malformed netlink fuzzing for each attr type/length, LLSEC fixed-length key and command arrays, channel-page/ED list lengths, and compatibility with legacy userspace tools.

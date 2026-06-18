# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mac802154_hwsim.h

## Purpose
`mac802154_hwsim.h` defines the user/kernel generic-netlink ABI for the mac802154 hwsim radio simulator. It is consumed by `mac802154_hwsim.c` and by userspace tools that manage simulated radios and edges.

## Important APIs, types, and functions
The header exports three enum families: `MAC802154_HWSIM_CMD_*` for radio/edge commands, `MAC802154_HWSIM_ATTR_*` for top-level radio attributes, and `MAC802154_HWSIM_EDGE_ATTR_*` for nested edge attributes. Command semantics include get/new/delete radio and get/set/new/delete edge. Attributes identify radio IDs, nested edge descriptions, edge endpoint IDs, and edge LQI.

## Control flow
There is no executable control flow in the header. At runtime, `mac802154_hwsim.c` maps these constants into generic-netlink policy tables and operation dispatch. Requests use `MAC802154_HWSIM_ATTR_RADIO_ID` plus optional nested `MAC802154_HWSIM_ATTR_RADIO_EDGE`; dumps and replies return nested `MAC802154_HWSIM_ATTR_RADIO_EDGES` entries.

## State and persistence
The header stores no state. It defines stable numeric ABI values, so changes are persistent in the compatibility sense: reordering or renaming constants can break userspace.

## Dependencies and integration points
It is a kernel-private header in the driver folder but effectively describes a netlink ABI shared with userspace. It is directly included by the hwsim implementation and indirectly tied to generic-netlink policy validation.

## Risks and test signals
The visible risk is ABI typo/constant drift: `MAC802154_HWSIM_CMD_MAX` uses `__MAC802154_HWSIM_MAX`, which does not match the declared `__MAC802154_HWSIM_CMD_MAX`. If compiled as-is in a strict path using that macro, it would fail or reference an undefined symbol. Tests should include driver compilation with warnings enabled, netlink command enumeration checks, userspace tool compatibility, and nested attribute encode/decode round trips for radio and edge state.

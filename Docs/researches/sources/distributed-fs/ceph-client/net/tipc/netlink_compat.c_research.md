# sources/distributed-fs/ceph-client/net/tipc/netlink_compat.c

## Purpose
`netlink_compat.c` implements the legacy `TIPC_GENL_NAME` TLV-based configuration ABI on top of the modern nested generic-netlink handlers. It allocates legacy TLV replies, translates legacy request structures into modern attributes for mutating commands, runs modern dump handlers and formats their nested attributes back into legacy TLV or text output, and registers/unregisters a separate compatibility generic-netlink family.

## Important APIs, Types, And Functions
Key structures are `struct tipc_nl_compat_msg`, `struct tipc_nl_compat_cmd_dump`, and `struct tipc_nl_compat_cmd_doit`. Core helpers include `tipc_skb_tailroom()`, `tipc_add_tlv()`, `tipc_tlv_init()`, `tipc_tlv_sprintf()`, `tipc_tlv_alloc()`, `tipc_get_err_tlv()`, `tipc_nl_compat_dumpit()`, `__tipc_nl_compat_dumpit()`, `tipc_nl_compat_doit()`, and `__tipc_nl_compat_doit()`. Command-specific translation/formatting covers bearer names/enable/disable, link stats and properties, media/bearer/link property set, name-table display, socket/port display, media names, node list, net id/address get/set, and show-stats. The exported lifecycle functions are `tipc_netlink_compat_start()` and `tipc_netlink_compat_stop()`.

## Control Flow
`tipc_nl_compat_recv()` parses the legacy command header, checks `CAP_NET_ADMIN` for mutating command ranges, validates the incoming TLV when present, dispatches through `tipc_nl_compat_handle()`, maps common errors to legacy error TLVs, prepends a generic-netlink header copied from the request, and unicasts the reply. Dump commands allocate a TLV reply, optionally write a text header, build a synthetic modern dump request, call the modern dump handler repeatedly with a fake `netlink_callback`, parse each emitted modern netlink message, and call a formatter to append TLV/text output. Doit commands allocate an attribute buffer, call a transcoder under RTNL to build modern nested attributes from the legacy TLV, parse attributes into `genl_info`, call the modern handler, and return an empty success TLV.

## State And Persistence
Compatibility state is transient per request in `tipc_nl_compat_msg`. Persistent global state is the `tipc_genl_compat_family` with one `TIPC_GENL_CMD` operation. Reply size is capped by the legacy `ULTRA_STRING_MAX_LEN`/`TIPC_SKB_MAX` behavior, and truncation is represented by appending a textual `<truncated>` marker when the legacy string buffer is full.

## Dependencies And Integration Points
The file depends on modern netlink policies and handlers from bearer, media, link, node, net, name table, and socket code. It uses legacy definitions from `<linux/tipc_config.h>`, string termination helpers, generic netlink dump helpers, and RTNL serialization for translated mutating operations. It is registered separately from `tipc_genl_family` but translates through that family's id, maxattr, and policy.

## Risks And Edge Cases
This is an ABI-preservation layer, so behavior must match old `tipc-config` expectations even when modern netlink semantics differ. String TLVs are manually length-checked and must be NUL-terminated before conversion. `tipc_tlv_sprintf()` writes directly into skb tailroom and relies on the legacy cap. Dump callbacks reuse attribute buffers and fake callback state; stale cursor or parse errors can truncate or interrupt output. Some formatting, such as link TX profile percentages, divides by modern stat counters and depends on handlers providing nonzero expected attributes.

## Test Signals
Legacy `tipc-config` command coverage, CAP_NET_ADMIN denial tests, malformed TLV type/length/string tests, bearer enable/disable translation, link property set/reset stats, name-table depth filters, port publication display, net id/address get/set, large dump truncation behavior, namespace-specific requests, modern/legacy parity tests, and registration/unregistration failure tests validate this file.

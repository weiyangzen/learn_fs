# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/pedit.h

Purpose: Declares pedit header shadow structures and the shared pedit parse helper.

Important types: `struct pedit_headers` mirrors editable Ethernet, VLAN, IPv4, IPv6, TCP, and UDP header fields. `struct pedit_headers_action` stores value and mask shadows plus a pedit count.

Control flow and state: Higher-level parsers pass an array of `pedit_headers_action` for SET/ADD commands; this header defines the storage that later mod-header construction consumes.

Dependencies and integration: Includes `en_tc.h`; used by pedit and VLAN mangle/rewrite parsers.

Risks and tests: Struct layout must match offsets used by parsers. Tests should ensure VLAN rewrite and pedit share mask/value semantics and do not overlap fields incorrectly.

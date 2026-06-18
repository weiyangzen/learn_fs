# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bridge_vlan_dump.sh

Purpose: Verifies bridge VLAN dump range grouping only combines consecutive VLANs whose per-VLAN options are identical.

Important APIs/types/functions: Uses `bridge vlan add/set/show`, `bridge mdb add/del`, bridge VLAN filtering with multicast snooping, `neigh_suppress`, `mcast_max_groups`, `mcast_n_groups`, `mcast_snooping`, kselftest `lib.sh`, and deferred cleanup.

Control flow: Setup creates a namespace, bridge `br0` with VLAN/multicast snooping enabled, and a dummy port. Each test adds VLANs 10 and 11, configures differing option values, checks `bridge -d vlan show` does not contain range `10-11` while individual entries exist, then makes option values match and checks the range appears.

State and persistence behavior: Creates bridge, dummy device, VLAN entries, MDB entries, and global bridge VLAN settings in a temporary namespace. Deferred cleanup removes added entries and namespace.

Dependencies and integration points: Requires iproute2 bridge support for per-VLAN neighbor suppression and multicast attributes, bridge VLAN filtering, and root.

Risks: Output parsing with grep regexes depends on bridge command formatting. It verifies only two adjacent VLANs and specific fields, not all possible VLAN dump attributes.

Test signals: Four `log_test` cases passing show range grouping respects `neigh_suppress`, `mcast_max_groups`, `mcast_n_groups`, and inherited multicast-enabled state.

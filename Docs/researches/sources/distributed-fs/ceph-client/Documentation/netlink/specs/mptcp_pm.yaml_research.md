# sources/distributed-fs/ceph-client/Documentation/netlink/specs/mptcp_pm.yaml

Purpose: describes the legacy Generic Netlink path manager API for Multipath TCP endpoint, limit, flag, announce, remove, and subflow operations.

Important APIs/types/functions: the `event-type` enum documents MPTCP event categories. Attribute sets include `address`, `subflow-attribute`, `endpoint`, `attr`, and `event-attr`. Address attributes carry family, id, IPv4/IPv6 address, port, flags, and ifindex. `attr` wraps local/remote addresses plus receive-addrs/subflows limits, token, and local id. `event-attr` describes event payloads with token, ids, source/destination addresses and ports, backup/error flags, timeout, ifindex, reset metadata, and server-side indicator.

Control flow: administrative endpoint operations are `add-addr`, `del-addr`, and `flush-addrs`. `get-addr` supports targeted lookup and dump. `set-limits`/`get-limits` manage global or namespace path-manager limits. `set-flags` changes endpoint flags. Per-connection operations use tokens: `announce`, `remove`, `subflow-create`, and `subflow-destroy`. Most commands disable strict validation for legacy compatibility and use `uns-admin-perm` for writes.

State and persistence: the API mutates MPTCP path manager state: configured endpoints, address ids, flags, limits, and live connection subflow choices. This is kernel/network-namespace state, not YAML state, and typically persists only while the namespace and MPTCP sockets exist.

Dependencies and integration points: integrates with MPTCP kernel path manager logic, namespace-scoped networking, and userspace tools such as `ip mptcp`. The token fields connect management commands to established MPTCP connections.

Risks: non-strict validation plus nested address structures can allow ambiguous messages. Address byte order varies: IPv4 and event ports are big-endian in several places, while endpoint `port` lacks an explicit byte-order marker. Token-scoped operations can fail if the connection disappears between discovery and action. Event attributes exist in the schema but no multicast groups are declared here.

Test signals: endpoint add/get/delete/flush tests, limit set/get tests, per-token announce/remove/subflow actions against live sockets, IPv4/IPv6 exact length and endian checks, namespace isolation, and stale token/id failure paths.

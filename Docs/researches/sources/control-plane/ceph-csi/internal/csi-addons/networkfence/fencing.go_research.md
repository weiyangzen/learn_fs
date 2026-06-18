# sources/control-plane/ceph-csi/internal/csi-addons/networkfence/fencing.go

Purpose: shared implementation of CSI-addons network fencing for CephFS and RBD. It converts CSI-addons CIDR requests into Ceph OSD blocklist changes, evicts matching CephFS clients, reports the local client CIDR for fencing, and optionally auto-unfences recently blocklisted clients.

Important APIs/types/functions: `NetworkFence` holds CIDRs, monitors, and credentials. Public functions include `NewNetworkFence()`, `AddClientEviction()`, `AddNetworkFence()`, `RemoveNetworkFence()`, `GetCIDR()`, `GetFenceClients()`, `autoUnfenceClientOnMatch()`, `containsMatchingBlockListEntry()`, and `matchEntry()`. Helpers include `listActiveClients()`, `evictCephFSClient()`, `getIPRange()`, `incIP()`, `activeClient.fetchIP()`, and `activeClient.fetchID()`.

Control flow: construction validates CIDR list, resolves `clusterID` to monitors, and stores credentials. `AddClientEviction()` lists active MDS clients via `ceph tell mds.0 client ls`, parses client IP/ID, evicts clients inside requested CIDRs, then calls `AddNetworkFence()`. Add/remove blocklist operations first try range-capable Ceph commands; on "invalid command" they fall back to expanding CIDRs into individual IP entries. `GetFenceClients()` connects to the cluster with user credentials, obtains FSID and client address, converts it to a single-host CIDR, and, if enabled, removes a matching short-lived blocklist entry after cooldown. Auto-unfence queries OSD blocklist through go-ceph and matches Ceph's `:0/32` or bracketed IPv6 `:0/128` formats.

State and persistence: durable backend state is Ceph OSD blocklist entries and CephFS MDS client eviction. The package reads cluster identity, client addresses, OSD blocklist contents, and active MDS client JSON. Cooldown decisions are time-based using `util.AutoBlocklistTime` and a fixed five-minute period.

Dependencies and integration points: used by both CephFS and RBD CSI-addons fence controllers. It depends on Ceph command execution for MDS client operations, common Ceph blocklist utility functions, go-ceph OSD admin APIs, common client-IP parsing/CIDR conversion, and gRPC status codes for `GetFenceClients()`.

Risks: expanding large CIDRs can be expensive and dangerous if range commands are unsupported. Fallback detection depends on matching "invalid command" in error text. The active client list always targets MDS rank 0. Auto-unfence timing is subtle: entries just created within cooldown return an error, while older short-lived entries are removed. Address parsing must handle IPv4, IPv6, and Ceph messenger prefixes. Blocklist removal for individual IPs uses nonce `"0"` and assumes Ceph matching semantics.

Test signals: tests cover CIDR expansion, client IP/ID parsing, blocklist match/cooldown behavior, and IPv4/IPv6 match suffix parsing. They do not mock Ceph CLI, OSD admin calls, or end-to-end blocklist add/remove.
